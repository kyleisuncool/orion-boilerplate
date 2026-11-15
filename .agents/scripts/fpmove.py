#!/usr/bin/env python3
"""Move a file or folder in the file plane and record it in the moves ledger, in one step.

    fpmove.py SRC DEST --reason {reorg,ingest,deliver,sent,close,archive,restore,manual} [--note TEXT] [--dry-run]
    fpmove.py --batch PLAN.tsv --reason reorg [--dry-run]     # one "SRC<TAB>DEST[<TAB>NOTE]" per line
    fpmove.py OLD NEW --reason manual --record-only --note "<source of the claim>"

--record-only logs a move that already happened outside the protocol (before the ledger existed,
or by hand): OLD must be gone, NEW must exist, nothing on disk changes. The note says how the
move is known — a log entry, the owner's word, or "inferred: <why>".

Never copies, never deletes, never overwrites. Refuses if DEST exists or SRC is open in an
editor (a .~lock file). Parent folders of DEST are created. Every protocol step that moves a
file uses this, so the ledger cannot fall behind the disk.
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fplib  # noqa: E402

REASONS = ("reorg", "ingest", "deliver", "sent", "close", "archive", "restore", "manual")


def record(src, dest, reason, note, dry):
    s, d = fplib.expand(src), fplib.expand(dest)
    if os.path.lexists(s):
        return f"SKIP old path still exists (not a past move): {fplib.tilde(src)}"
    if not os.path.lexists(d):
        return f"SKIP new path missing: {fplib.tilde(dest)}"
    if not note:
        return f"SKIP --record-only needs --note saying how the move is known: {fplib.tilde(src)}"
    if dry:
        return f"WOULD RECORD {fplib.tilde(src)}  ->  {fplib.tilde(dest)}"
    fplib.append_ledger(s, d, reason, note)
    return f"RECORDED {fplib.tilde(src)}  ->  {fplib.tilde(dest)}"


def move(src, dest, reason, note, dry):
    s, d = fplib.expand(src), fplib.expand(dest)
    if not os.path.lexists(s):
        return f"SKIP missing source: {fplib.tilde(src)}"
    if os.path.lexists(d):
        return f"SKIP destination exists: {fplib.tilde(dest)}"
    if fplib.locked(s):
        return f"SKIP open in an editor (.~lock): {fplib.tilde(src)}"
    if dry:
        return f"WOULD MOVE {fplib.tilde(src)}  ->  {fplib.tilde(dest)}"
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.move(s, d)
    fplib.append_ledger(s, d, reason, note)
    return f"MOVED {fplib.tilde(src)}  ->  {fplib.tilde(dest)}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?")
    ap.add_argument("dest", nargs="?")
    ap.add_argument("--batch")
    ap.add_argument("--reason", required=True, choices=REASONS)
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--record-only", action="store_true", help="log a move that already happened; change nothing on disk")
    a = ap.parse_args()
    fplib.require_registry()
    jobs = []
    if a.batch:
        with open(a.batch, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 2 or not parts[0] or not parts[1]:
                    ap.error(f"{a.batch} line {n}: needs SRC<TAB>DEST[<TAB>NOTE] — nothing was run")
                jobs.append((parts[0], parts[1], parts[2] if len(parts) > 2 else a.note))
    elif a.src and a.dest:
        jobs.append((a.src, a.dest, a.note))
    else:
        ap.error("give SRC DEST, or --batch PLAN.tsv")
    skipped = 0
    for src, dest, note in jobs:
        msg = (record if a.record_only else move)(src, dest, a.reason, note, a.dry_run)
        skipped += msg.startswith("SKIP")
        print(msg)
    print(f"-- {len(jobs)} job(s), {skipped} skipped{' (dry run, nothing moved)' if a.dry_run else ''}")
    sys.exit(1 if skipped else 0)


if __name__ == "__main__":
    main()
