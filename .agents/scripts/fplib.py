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


# A ledger row is a table row with each path in backticks: | ends a cell, ` ends the pointer,
# a newline ends the row. A path holding one can't be recorded, so it must not be moved either.
LEDGER_BREAKERS = "|`\n\r"


def ledger_cell(path):
    """The form a ledger row stores: absolute, so it means the same from any folder, and ~-relative."""
    return tilde(os.path.abspath(expand(path)))


def unrecordable(*paths):
    """The paths a ledger row can't hold."""
    return [p for p in paths if any(c in ledger_cell(p) for c in LEDGER_BREAKERS)]


def unrecordable_skip(*paths):
    """A SKIP line naming the first path a ledger row can't hold, else "". Callers check this before
    touching the disk, dry run included, so a move or delete never lands without its row."""
    bad = unrecordable(*paths)
    return f"SKIP path can't be recorded in the ledger (contains | ` or a newline): {bad[0]!r}" if bad else ""


def append_ledger(old, new, reason, note=""):
    today = datetime.date.today().isoformat()
    note = " ".join(note.replace("|", "/").split())
    bad = unrecordable(old, new)
    if bad:  # callers check first; this stops a row that would corrupt the table
        raise SystemExit(f"refusing to record a path containing | ` or a newline: {ledger_cell(bad[0])!r}")
    cells = [ledger_cell(old), ledger_cell(new)]
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


FENCE_HEADER = "Fenced path"
FENCE_FORMAT = (f"Fences go in a table headed | {FENCE_HEADER} | Since | Known cost | under a ## Fences heading, "
                "one backticked path per row, relative to the vault (`2. Areas/Private/`), or a single "
                "*(none)* row. Only the owner edits that table.")
NO_FENCE = ("", "(none)")  # a blank cell, or the empty table's *(none)* row once its emphasis is stripped
HEADING_RE = re.compile(r"^(#{1,6})\s")
FENCES_HEADING_RE = re.compile(r"^#{1,6}\s+Fences\s*$")
CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")  # a \| inside [[path\|alias]] is not a column break
SPAN_RE = re.compile(r"`([^`]*)`")
EMPHASIS_RE = re.compile(r"^(\*\*|__|\*|_)(.+)\1$")
WIKILINK_RE = re.compile(r"^\[\[([^\]|\\]+)(?:\\\|[^\]]*)?\]\]$")
TRAILING_GLOB_RE = re.compile(r"(?:/\*{1,2})+/?$")


def refuse_fences(where, why):
    raise SystemExit(f"{where}: {why}. {FENCE_FORMAT} Nothing was scanned.")


def fence_cells(manual, text):
    """The Fenced-path cell of every row in the Fences section's table.

    Code blocks are skipped, and a blank line doesn't end the table, so a row the owner added
    is never silently dropped. Refuses when the section has no fences table, or more than one table."""
    level, in_code, header, separators, cells = None, False, False, 0, []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        heading = None if in_code else HEADING_RE.match(s)
        if heading:
            if level is not None and len(heading.group(1)) <= level:
                break
            if level is None and FENCES_HEADING_RE.match(s):
                level = len(heading.group(1))
            continue
        if in_code or level is None or not s.startswith("|"):
            continue
        row = [c.strip() for c in CELL_SPLIT_RE.split(s.strip("|"))]
        if set("".join(row)) <= set("-: "):
            separators += 1
        elif not header and row[0] == FENCE_HEADER:
            header = True
        elif not header:
            refuse_fences(manual, "the Fences section holds a table that isn't the fences table")
        else:
            cells.append(row[0])
    if not header:
        refuse_fences(manual, "no Fences table found")
    if separators > 1:
        refuse_fences(manual, "the Fences section holds more than one table")
    return cells


def exists_exactly(vault, rel):
    """True if rel names an entry in the vault spelled exactly so, case included. The fence matcher
    compares strings, so a near miss that a case-insensitive disk would accept must not pass."""
    d = vault
    for part in rel.split("/"):
        try:
            if part not in os.listdir(d):
                return False
        except OSError:
            return False
        d = os.path.join(d, part)
    return True


def normalise_fence(path):
    """Vault-relative form: no leading ./ or /, no trailing /** glob, no doubled or trailing slash."""
    path = re.sub(r"^(?:\./|/)+", "", path.strip())
    path = TRAILING_GLOB_RE.sub("", path)
    return os.path.normpath(path) if path else "."


def fence_path(vault, where, cell):
    """The one vault-relative path a Fences cell names. Refuses a cell that names more than one,
    carries text outside its backticks, or names no path inside the vault."""
    spans = SPAN_RE.findall(cell)
    if len(spans) > 1:
        refuse_fences(where, f"row {cell!r} names more than one path; give each its own row")
    if spans:
        if SPAN_RE.sub("", cell).strip("*_ "):
            refuse_fences(where, f"row {cell!r} has text outside its backticks")
        path = spans[0]
    else:
        path = cell.strip()
        emphasis = EMPHASIS_RE.match(path)
        if emphasis and not exists_exactly(vault, normalise_fence(path)):  # `_drafts/` stays as written
            path = emphasis.group(2)
    link = WIKILINK_RE.match(path.strip())
    if link:
        path = link.group(1)
    path = normalise_fence(path)
    if path == "." or path == ".." or path.startswith("../"):
        refuse_fences(where, f"row {cell!r} doesn't name a path inside the vault")
    if link and not exists_exactly(vault, path) and exists_exactly(vault, path + ".md"):
        path += ".md"
    if not exists_exactly(vault, path):
        refuse_fences(where, f"row {cell!r} names {path!r}, which isn't in the vault (spelling and case must match)")
    return path


def vault_fences(vault, extra=()):
    """Every fenced path, vault-relative: the Fences table in VAULT/AGENTS.md, then any extra ones given.

    Refuses when there is no table to read, or a row it can't turn into one path in the vault.
    A scan that can't see the fences would open them."""
    manual = os.path.join(vault, "AGENTS.md")
    if not os.path.isfile(manual):
        refuse_fences(manual, "no AGENTS.md")
    with open(manual, encoding="utf-8") as f:
        cells = fence_cells(manual, f.read())
    fences = []
    for where, cell in [(manual, c) for c in cells] + [("--fence", e) for e in extra]:
        if cell.strip("*_ ") in NO_FENCE:
            continue
        path = fence_path(vault, where, cell)
        if path not in fences:
            fences.append(path)
    return fences


def vault_md_files(vault, fences=()):
    """Yield (relpath, abspath) for every .md in a vault, skipping .git, .obsidian and fences.
    A fence is a folder (everything under it) or a single file."""
    fenced_files = tuple(f.rstrip("/") for f in fences)
    fences = tuple(f + "/" for f in fenced_files)
    for dirpath, dirnames, filenames in os.walk(vault):
        rel_dir = os.path.relpath(dirpath, vault)
        rel_dir = "" if rel_dir == "." else rel_dir + "/"
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and not (rel_dir + d + "/").startswith(fences)]
        for fn in filenames:
            if fn.endswith(".md") and not os.path.islink(os.path.join(dirpath, fn)):
                rel = rel_dir + fn
                if not rel.startswith(fences) and rel not in fenced_files:
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
