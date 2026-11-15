#!/usr/bin/env python3
"""Repoint stale file-plane pointers in a vault, using the moves ledger.

    repoint.py VAULT [--fence REL_PATH ...] [--live-only] [--apply]

Dry run by default: prints every replacement it would make. --apply writes them.
Every page is in scope, ledgers, captures and 5. Archive/ included: only the path between
the backticks changes, never a word of prose (the vault's link rule,
applied to file-plane paths). --live-only skips 4. Decisions/, 5. Archive/, 0. Inbox/,
wiki/log.md, wiki/folds/ and lint reports. Fenced paths are never opened: every path in the
Fences table of the vault's AGENTS.md, plus any given with --fence. With no Fences table to
read, or a row that doesn't name one path in the vault, it refuses. A pointer is repointed
only when the old path is gone and the ledger's new path exists.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fplib  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault")
    ap.add_argument("--fence", action="append", default=[],
                    help="another path to fence, beyond the Fences table in VAULT/AGENTS.md")
    ap.add_argument("--live-only", action="store_true", help="skip ledgers, captures and 5. Archive/")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    fplib.use_vault(a.vault)
    fplib.require_registry()
    fences = fplib.vault_fences(a.vault, a.fence)
    pairs = fplib.load_ledger()
    changed_files = changes = 0
    for rel, path in fplib.vault_md_files(a.vault, fences):
        if fplib.is_protected(rel) and a.live_only:
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        new_text = text
        for raw, canon in set(fplib.pointers(text)):
            if os.path.lexists(fplib.expand(canon)):
                continue
            target = fplib.resolve(canon, pairs)
            if not target or not os.path.lexists(fplib.expand(target)):
                continue
            new_text = new_text.replace(f"`{raw}`", f"`{target}`")
            changes += 1
            print(f"{rel}: `{fplib.tilde(raw)}` -> `{target}`")
        if new_text != text:
            changed_files += 1
            if a.apply:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_text)
    mode = "applied" if a.apply else "dry run, nothing written"
    print(f"-- {changes} pointer(s) in {changed_files} file(s) ({mode})")


if __name__ == "__main__":
    main()
