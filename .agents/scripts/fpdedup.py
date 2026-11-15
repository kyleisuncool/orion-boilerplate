#!/usr/bin/env python3
"""Delete a byte-identical duplicate and point the moves ledger at the copy that stays.

    fpdedup.py --batch PLAN.tsv [--dry-run]      # one "DROP<TAB>KEEP" per line
    fpdedup.py DROP KEEP [--dry-run]

Only from a list the owner has approved. Re-verifies sha1 at the moment of deletion and refuses
on any mismatch, a missing KEEP, a directory pair whose trees differ, or an open editor lock.
Each deletion appends a ledger row DROP -> KEEP (reason: dedup), so any vault page that named
the dropped copy is repointed to the kept one by repoint.py.
"""
import argparse
import hashlib
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fplib  # noqa: E402


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree(p):
    """Every entry under p — files by hash, folders and symlinks by kind — so rmtree loses nothing unseen."""
    out = {}
    for dp, dns, fns in os.walk(p):
        for dn in dns:
            dpath = os.path.join(dp, dn)
            out[os.path.relpath(dpath, p) + "/"] = "link:" + os.readlink(dpath) if os.path.islink(dpath) else "dir"
        for fn in fns:
            fp = os.path.join(dp, fn)
            out[os.path.relpath(fp, p)] = "link:" + os.readlink(fp) if os.path.islink(fp) else sha1(fp)
    return out


def dedup(drop, keep, dry):
    d, k = fplib.expand(drop), fplib.expand(keep)
    if not os.path.lexists(d):
        return f"SKIP missing: {fplib.tilde(drop)}"
    if not os.path.lexists(k):
        return f"SKIP keep copy missing: {fplib.tilde(keep)}"
    if fplib.locked(d):
        return f"SKIP open in an editor (.~lock): {fplib.tilde(drop)}"
    if os.path.islink(d) or os.path.islink(k):
        return f"SKIP a symlink is involved — resolve it by hand: {fplib.tilde(drop)}"
    rd, rk = os.path.realpath(d), os.path.realpath(k)
    if os.path.samefile(d, k) or rd == rk:
        return f"SKIP DROP and KEEP are the same file: {fplib.tilde(drop)}"
    if rk.startswith(rd + os.sep) or rd.startswith(rk + os.sep):
        return f"SKIP one path is inside the other: {fplib.tilde(drop)}"
    if os.path.isdir(d) != os.path.isdir(k):
        return f"SKIP file/folder mismatch: {fplib.tilde(drop)}"
    same = tree(d) == tree(k) if os.path.isdir(d) else sha1(d) == sha1(k)
    if not same:
        return f"SKIP NOT IDENTICAL: {fplib.tilde(drop)}"
    if dry:
        return f"WOULD DELETE {fplib.tilde(drop)}  (kept: {fplib.tilde(keep)})"
    shutil.rmtree(d) if os.path.isdir(d) else os.remove(d)
    fplib.append_ledger(d, k, "dedup", "byte-identical; deleted on the owner's approval")
    return f"DELETED {fplib.tilde(drop)}  (kept: {fplib.tilde(keep)})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("drop", nargs="?")
    ap.add_argument("keep", nargs="?")
    ap.add_argument("--batch")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    fplib.require_registry()
    jobs = []
    if a.batch:
        with open(a.batch, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 2 or not parts[0] or not parts[1]:
                    ap.error(f"{a.batch} line {n}: needs DROP<TAB>KEEP — nothing was run")
                jobs.append((parts[0], parts[1]))
    elif a.drop and a.keep:
        jobs = [(a.drop, a.keep)]
    else:
        ap.error("give DROP KEEP, or --batch PLAN.tsv")
    skipped = 0
    for drop, keep in jobs:
        msg = dedup(drop, keep, a.dry_run)
        skipped += msg.startswith("SKIP")
        print(msg)
    print(f"-- {len(jobs)} job(s), {skipped} skipped{' (dry run, nothing deleted)' if a.dry_run else ''}")
    sys.exit(1 if skipped else 0)


if __name__ == "__main__":
    main()
