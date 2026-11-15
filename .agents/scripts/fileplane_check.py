#!/usr/bin/env python3
"""orion-lint check 19: file-plane pointers and drift. Flags only; changes nothing.

    fileplane_check.py VAULT [--fence REL_PATH ...] [--stale-days 7]

Fenced paths are never opened: every path in the Fences table of the vault's AGENTS.md, plus
any given with --fence. With no Fences table to read, it refuses.

Part A, pointers (this vault): every backticked ~/ or /home/ path in every page.
  STALE             a page points at a moved path; the ledger knows where it went (fix: repoint.py —
                    every page, ledgers and archive included, path only)
  LIVE-MISSING      a live page points at nothing, and the ledger doesn't know (candidates by name)
  KEPT-MISSING      same, inside a ledger or capture (archive, decisions, inbox, log, folds) — the
                    archive backlog, reported under its own heading
  OUTSIDE           a missing path outside the registered file plane (code repos, dotfiles), or a
                    pointer written `<machine>:~/path` for another machine — context, not a finding

Part B, drift (this machine's file plane, from registry/endpoints.md):
  MISNAMED          a folder in a working root that breaks the naming rule
  LOOSE             a file sitting directly in a working root
  UNKNOWN-ID        a folder name carrying a prefix the ID registry doesn't have
  STALE-INTAKE      an item in an inbox or landing strip older than --stale-days
  DUP-INTAKE        an intake file byte-identical to a file already in a working root
  UNREGISTERED-BOX  an inbox/outbox-shaped folder that isn't in the endpoint registry
  ROOT-MISSING      the work or archive root is registered but absent: every pointer into it dies

Part C, IDs (this vault):
  COUNTER-LOW       a hub id: above its Area hub's workstream_counter:
  UNKNOWN-PREFIX    a hub id: whose prefix no Area hub declares as id_prefix:
"""
import argparse
import hashlib
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fplib  # noqa: E402

WS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-([A-Z][A-Z0-9]*)-(\d+) \S.*$")
AREA_RE = re.compile(r"^([A-Z][A-Z0-9]*) \S.*$")
ID_RE = re.compile(r"^id:\s*([A-Z][A-Z0-9]*)-(\d+)\s*$", re.M)


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            if not fn.startswith("."):
                yield os.path.join(dirpath, fn)


def name_index(dirs):
    idx = {}
    for root in dirs:
        r = fplib.expand(root)
        if not os.path.isdir(r):
            continue
        for dirpath, dirnames, filenames in os.walk(r):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for n in dirnames + filenames:
                idx.setdefault(n, []).append(fplib.tilde(os.path.join(dirpath, n)))
    return idx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault")
    ap.add_argument("--fence", action="append", default=[],
                    help="another path to fence, beyond the Fences table in VAULT/AGENTS.md")
    ap.add_argument("--stale-days", type=int, default=7)
    a = ap.parse_args()
    fplib.use_vault(a.vault)
    if not os.path.isfile(fplib.ENDPOINTS):
        print(f"## File plane — check 19 ({fplib.tilde(os.path.abspath(a.vault))})")
        print("skipped: no registry/ — the file plane is not in use")
        return

    fences = fplib.vault_fences(a.vault, a.fence)
    pairs = fplib.load_ledger()
    eps = [e for e in fplib.endpoints() if os.path.isdir(fplib.expand(e["path"]))]
    rts = fplib.roots()
    work, archive = rts.get("work"), rts.get("archive")
    reg = fplib.id_registry(a.vault, fences)
    out = {}

    def add(code, line):
        out.setdefault(code, []).append(line)

    # ---- Part A: pointers ----
    search_dirs = [loc for name, loc in rts.items() if name != "code"] + [e["path"] for e in eps]
    names = None
    scope = fplib.scope_prefixes()
    total = ok = 0
    for rel, path in fplib.vault_md_files(a.vault, fences):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        kept = fplib.is_protected(rel)
        for mach, mpath in fplib.OTHER_MACHINE_RE.findall(text):
            add("OUTSIDE", f"{rel}: `{mach}:{mpath}` (another machine)")
        for raw, canon in sorted(set(fplib.pointers(text))):
            total += 1
            if os.path.lexists(fplib.expand(canon)):
                ok += 1
                continue
            target = fplib.resolve(canon, pairs)
            if target and os.path.lexists(fplib.expand(target)):
                add("STALE", f"{rel}: `{canon}` -> `{target}`")
                continue
            if not fplib.in_scope(canon, scope):
                add("OUTSIDE", f"{rel}: `{canon}`")
                continue
            if names is None:
                names = name_index(search_dirs)
            cands = names.get(os.path.basename(canon), [])
            hint = (" — candidates: " + "; ".join(f"`{c}`" for c in cands[:3])
                    + (f" (+{len(cands) - 3} more)" if len(cands) > 3 else "")) if cands else " — no candidate by name"
            add("KEPT-MISSING" if kept else "LIVE-MISSING", f"{rel}: `{canon}`{hint}")

    # ---- Part B: drift ----
    for label, root in (("work", work), ("archive", archive)):
        if not root:
            continue
        if not os.path.isdir(fplib.expand(root)):
            add("ROOT-MISSING", f"[{label}] `{root}` is registered but not on this disk")
            continue
        for n in sorted(os.listdir(fplib.expand(root))):
            if n.startswith("."):
                continue
            p = os.path.join(fplib.expand(root), n)
            if label == "work" and n == "_archive":
                continue
            if not os.path.isdir(p):
                add("LOOSE", f"`{fplib.tilde(p)}`")
                continue
            m = WS_RE.match(n) or AREA_RE.match(n)
            if not m:
                add("MISNAMED", f"`{fplib.tilde(p)}`")
            elif m.group(1) not in reg:
                add("UNKNOWN-ID", f"`{fplib.tilde(p)}` — prefix {m.group(1)}")

    now, ep_paths = time.time(), {e["path"] for e in eps}
    intake = [e for e in eps if e["direction"] in ("in", "landing")]
    size_idx = None
    for e in intake:
        base = fplib.expand(e["path"])
        for n in sorted(os.listdir(base)):
            p = os.path.join(base, n)
            if n.startswith(".") or n == "processed" or fplib.tilde(p) in ep_paths:
                continue
            age = (now - os.path.getmtime(p)) / 86400
            if age > a.stale_days:
                add("STALE-INTAKE", f"[{e['name']}] `{fplib.tilde(p)}` — {int(age)}d")
            files = [p] if os.path.isfile(p) else list(walk_files(p))
            for fp in files:
                if size_idx is None:
                    size_idx = {}
                    for root in (work, archive):
                        if root and os.path.isdir(fplib.expand(root)):
                            for wf in walk_files(fplib.expand(root)):
                                try:
                                    size_idx.setdefault(os.path.getsize(wf), []).append(wf)
                                except OSError:
                                    pass
                try:
                    same = size_idx.get(os.path.getsize(fp), [])
                except OSError:
                    continue
                if same and os.path.getsize(fp) > 0:
                    h = sha1(fp)
                    match = next((w for w in same if sha1(w) == h), None)
                    if match:
                        add("DUP-INTAKE", f"[{e['name']}] `{fplib.tilde(fp)}` = `{fplib.tilde(match)}`")

    box_re = re.compile(r"(^|[\s_-])(in|out)box($|[\s_-])", re.I)
    parents = {"~"} | {fplib.tilde(os.path.dirname(fplib.expand(p))) for p in ep_paths}
    for parent in sorted(parents):
        pp = fplib.expand(parent)
        if not os.path.isdir(pp):
            continue
        for n in sorted(os.listdir(pp)):
            p = os.path.join(pp, n)
            if n.startswith(".") or not os.path.isdir(p) or not box_re.search(n):
                continue
            if fplib.tilde(p) not in ep_paths:
                add("UNREGISTERED-BOX", f"`{fplib.tilde(p)}`")

    # ---- Part C: IDs ----
    for rel, path in fplib.vault_md_files(a.vault, fences):
        if not rel.endswith("_hub.md"):
            continue
        with open(path, encoding="utf-8") as f:
            head = f.read(4000)
        for pre, num in ID_RE.findall(head):
            if pre not in reg:
                add("UNKNOWN-PREFIX", f"{rel}: id {pre}-{num}")
            elif reg[pre] is not None and int(num) > reg[pre]:
                add("COUNTER-LOW", f"{rel}: id {pre}-{num} > {pre} workstream_counter {reg[pre]}")

    # ---- report ----
    print(f"## File plane — check 19 ({fplib.tilde(os.path.abspath(a.vault))})")
    print(f"Pointers: {total} found · {ok} resolve · moves ledger: {len(pairs)} rows · "
          f"fences skipped: {', '.join(fences) or 'none'}")
    order = ["ROOT-MISSING", "STALE", "LIVE-MISSING", "KEPT-MISSING", "MISNAMED", "LOOSE", "UNKNOWN-ID",
             "STALE-INTAKE", "DUP-INTAKE", "UNREGISTERED-BOX", "COUNTER-LOW", "UNKNOWN-PREFIX", "OUTSIDE"]
    for code in order:
        items = out.get(code, [])
        print(f"\n{code}: {len(items)}")
        for line in items:
            print(f"- {line}")


if __name__ == "__main__":
    main()
