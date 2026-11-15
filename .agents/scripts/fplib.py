"""Shared helpers for the file-plane protocol scripts (fpmove, repoint, fileplane_check).

Everything machine-specific (paths, endpoints, roots) lives in the vault's registry/ folder
(endpoints.md, file-moves.md), never here. The registry is found from $ORION_REGISTRY, else
from the nearest folder at or above the current directory that holds registry/endpoints.md.
Scripts that take a VAULT argument call use_vault() so that vault's registry/ wins.
"""
import os
import re
import datetime

HOME = os.path.expanduser("~")


def _find_registry(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, "registry", "endpoints.md")):
            return os.path.join(d, "registry")
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.join(os.path.abspath(start), "registry")
        d = parent


def use_registry(path):
    global REGISTRY, LEDGER, ENDPOINTS
    REGISTRY = path
    LEDGER = os.environ.get("FP_LEDGER") or os.path.join(REGISTRY, "file-moves.md")  # override for tests
    ENDPOINTS = os.path.join(REGISTRY, "endpoints.md")


def require_registry():
    """Exit with a plain message when there is no registry to write to."""
    if not os.path.isfile(ENDPOINTS):
        raise SystemExit(f"no registry at {REGISTRY} — the file plane is not set up. "
                         "Copy 6. Templates/registry/ to registry/ in the vault, or set $ORION_REGISTRY.")


def use_vault(vault):
    """Point the registry at VAULT/registry, unless $ORION_REGISTRY says otherwise."""
    if not os.environ.get("ORION_REGISTRY"):
        use_registry(os.path.join(os.path.abspath(vault), "registry"))


use_registry(os.environ.get("ORION_REGISTRY") or _find_registry(os.getcwd()))

# Vault paths that are ledgers or verbatim captures: never edited, old paths there
# resolve through the moves ledger instead. Generic to every Orion vault.
PROTECTED = ("4. Decisions/", "5. Archive/", "0. Inbox/", "wiki/log.md", "wiki/folds/",
             "wiki/meta/lint-report-")

# A pointer is a backticked absolute or ~-relative path. A path on another machine is written
# `<machine>:~/path` (e.g. `laptop:~/Desktop/Inbox`) and is never checked on this one.
POINTER_RE = re.compile(r"`((?:~|/home/[^/`\s]+|/Users/[^/`\s]+)/[^`\n]+)`")
OTHER_MACHINE_RE = re.compile(r"`([a-z][a-z0-9-]*):(~/[^`\n]+)`")
PLACEHOLDER_RE = re.compile(r"<|>|YYYY|MM-DD|\*|…|\{|\}|\.\.\.|\||\[")


def tilde(path):
    """Absolute or ~ path -> canonical ~-relative form, no trailing slash."""
    p = os.path.expanduser(path)
    if not p.startswith("/"):
        return path.rstrip("/")
    m = re.match(r"^/(?:home|Users)/[^/]+(/.*)?$", p)
    if m and p.startswith(HOME):
        p = "~" + p[len(HOME):]
    elif m:
        p = "~" + (m.group(1) or "")
    return p.rstrip("/") or "~"


def expand(path):
    return os.path.expanduser(path)


def table_rows(md_path, first_header):
    """Yield dicts for every markdown table whose header row's first cell == first_header."""
    rows, header = [], None
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                header = None
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                if cells and cells[0] == first_header:
                    header = cells
                else:
                    header = False
                continue
            if header is False or set("".join(cells)) <= set("-: "):
                continue
            rows.append(dict(zip(header, cells)))
    return rows


def unbacktick(cell):
    m = re.search(r"`([^`]+)`", cell or "")
    return m.group(1) if m else (cell or "").strip()


def load_ledger():
    """List of (old, new) ~-relative pairs, in ledger order."""
    pairs = []
    for r in table_rows(LEDGER, "Date"):
        old, new = unbacktick(r.get("Old path")), unbacktick(r.get("New path"))
        if old and new:
            pairs.append((tilde(old), tilde(new)))
    return pairs


def resolve(path, pairs):
    """Follow the ledger: longest old-path prefix wins, chained. Returns new path or None."""
    p, seen, moved = tilde(path), set(), False
    while p not in seen:
        seen.add(p)
        best = None
        for old, new in pairs:
            if p == old or p.startswith(old + "/"):
                if best is None or len(old) > len(best[0]):
                    best = (old, new)
        if not best:
            break
        p = best[1] + p[len(best[0]):]
        moved = True
    return p if moved else None


def append_ledger(old, new, reason, note=""):
    today = datetime.date.today().isoformat()
    note = " ".join(note.replace("|", "/").split())
    cells = []
    for p in (old, new):
        p = tilde(os.path.abspath(expand(p)))  # absolute, so the row means the same from any folder
        if any(c in p for c in "|`\n\r"):
            raise SystemExit(f"refusing to record a path containing | ` or a newline: {p!r}")
        cells.append(p)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(f"| {today} | `{cells[0]}` | `{cells[1]}` | {reason} | {note} |\n")


def endpoints():
    out = []
    for r in table_rows(ENDPOINTS, "Endpoint"):
        loc = unbacktick(r.get("Location"))
        out.append({"name": unbacktick(r.get("Endpoint")), "path": tilde(loc),
                    "direction": r.get("Direction", "").strip(), "processed": r.get("Processed", "")})
    return out


def roots():
    return {unbacktick(r.get("Root")): tilde(unbacktick(r.get("Location")))
            for r in table_rows(ENDPOINTS, "Root")}


def scope_prefixes():
    """The file plane check 19 is responsible for: every endpoint and every root except code."""
    pre = {e["path"] for e in endpoints()}
    pre |= {loc for name, loc in roots().items() if name != "code"}
    return sorted(pre)


def in_scope(path, prefixes):
    p = tilde(path)
    return any(p == q or p.startswith(q + "/") for q in prefixes)


def id_registry(vault, fences=()):
    """prefix -> counter (int or None), read from every Area hub's id_prefix: and workstream_counter:."""
    out = {}
    for rel, path in vault_md_files(vault, fences):
        if not rel.endswith("_hub.md"):
            continue
        with open(path, encoding="utf-8") as f:
            head = f.read(4000)
        pre = re.search(r"^id_prefix:\s*([A-Z][A-Z0-9]*)\s*$", head, re.M)
        if not pre:
            continue
        c = re.search(r"^workstream_counter:\s*(\d+)\s*$", head, re.M)
        out[pre.group(1)] = int(c.group(1)) if c else None
    return out


def is_protected(rel):
    return rel.startswith(PROTECTED)


def vault_md_files(vault, fences=()):
    """Yield (relpath, abspath) for every .md in a vault, skipping .git, .obsidian and fences."""
    fences = tuple(f.rstrip("/") + "/" for f in fences)
    for dirpath, dirnames, filenames in os.walk(vault):
        rel_dir = os.path.relpath(dirpath, vault)
        rel_dir = "" if rel_dir == "." else rel_dir + "/"
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and not (rel_dir + d + "/").startswith(fences)]
        for fn in filenames:
            if fn.endswith(".md") and not os.path.islink(os.path.join(dirpath, fn)):
                rel = rel_dir + fn
                if not rel.startswith(fences):
                    yield rel, os.path.join(dirpath, fn)


def pointers(text):
    """Yield (raw, canonical) for every real file-plane pointer in text."""
    for m in POINTER_RE.finditer(text):
        raw = m.group(1)
        if PLACEHOLDER_RE.search(raw):
            continue
        yield raw, tilde(raw)


def locked(abspath):
    """True if LibreOffice (or similar) has the file, or anything inside the folder, open."""
    if os.path.isdir(abspath):
        for dirpath, _, filenames in os.walk(abspath):
            if any(fn.startswith(".~lock.") for fn in filenames):
                return True
        return False
    d, b = os.path.split(abspath)
    return os.path.exists(os.path.join(d, f".~lock.{b}#"))
