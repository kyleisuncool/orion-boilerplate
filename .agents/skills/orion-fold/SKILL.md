---
name: orion-fold
description: "Subtractive rollup of the oldest 2^k entries in an Orion vault's wiki/log.md into a fold page in wiki/folds/. Moves the child entries verbatim out of the log and leaves one pointer line, so the log stays cheap to read. Dry-run by default; add --commit to write. Run when cascade reports more than 16 unfolded entries. Triggers on: fold the log, run a fold, log rollup, roll up the log."
---

# orion-fold — subtractive log rollup

The log is append-only, so it grows forever and costs context in every session that reads it. A fold is **subtractive** — child entries **move** out of `log.md` into a fold page — and **extractive** — every claim on the fold page cites a specific child entry, with no synthesis beyond what the entries support.

**This does not break "never edit a past entry."** The entries are not edited: they move intact, headings demoted `##` → `###`, exactly as `orion-archive` moves a project. The ledger is preserved; it lives one file over, linked from where it used to be. **A fold that doesn't shrink `log.md` did nothing.**

**When:** `orion-cascade` prints `Log: N / 16` every run. Over 16 unfolded entries → a fold is due. Default `k=4` (16 entries).

---

## Paths

- **Log:** `wiki/log.md`
- **Fold output:** `wiki/folds/{FOLD-ID}.md`
- **Index:** `wiki/index.md` — the fold is linked under `## Folds`

## Entry format

```
## YYYY-MM-DD — [vault] Title of operation
- bullet details
```

An entry is everything from one line matching `^## [0-9]{4}-[0-9]{2}-[0-9]{2}` to the next. The log is newest-first, so **the oldest entries are at the bottom.** A heading containing `[folded]` is a pointer, not an entry.

## Parameters

- `k` (default 4) — batch size `2^k`.
- `--commit` — write to the vault. **Without it, dry-run: print the fold, write nothing.**
- `--force` — overwrite an existing fold with the same ID.

Fewer than `2^k` unfolded entries → report the shortfall and stop.

## Deterministic fold ID

```
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

e.g. `fold-k4-from-2026-01-02-to-2026-01-30-n16`.

**Duplicate detection (required):** before emitting anything, check whether `wiki/folds/{FOLD-ID}.md` exists. If it does, report and stop (unless `--force`).

---

## Procedure

### 1. Parse log entries

Scan `wiki/log.md` for entry headings. Take the oldest `2^k` unfolded entries — from the bottom up. Record each one's date, title and bullet content.

### 2. Build the children list

One record per entry. Do not dedupe.

```yaml
children:
  - date: "YYYY-MM-DD"
    title: "Entry title verbatim"
    summary: "One extractive sentence"
```

### 3. Compute the fold ID and check for a duplicate

Stop if the file exists and `--force` was not given.

### 4. Write the fold body — all six sections

1. **Scope** — one paragraph: period covered, dominant themes.
2. **Child entries** — table `Date | Title | Summary` (extractive, one sentence per entry).
3. **Key outcomes** — 3–7 bullets, each citing its source entry by date.
4. **Cross-entry themes** — 0–4 bullets, each naming at least two contributing entries; if none, "No cross-entry themes identified".
5. **Contradictions or corrections** — "None detected", or a list with resolution status.
6. **Child entries — verbatim** — the moved entries in full, headings demoted `##` → `###`, otherwise untouched. **This section is what makes the fold lossless and the removal from `log.md` safe.**

### 5. Self-check before emitting — every item is blocking

- **Oldest first.** ⚠ **No unfolded entry may remain below the span being folded.** Take the bottom `2^k`, then confirm every `## ` heading beneath the newest child is either a `[folded]` pointer or nothing at all. **If an unfolded entry sits below your span, you picked a middle window — stop and re-pick from the bottom.** A middle-window fold leaves a hole no later fold revisits, because every later fold also reads from the bottom and hits the hole first.
- **Every child in `children:` appears in the Child entries table and in Child entries — verbatim**, and vice versa.
- **Every entry to be removed from `log.md` was located and matched first**, on date plus normalized title. If any child cannot be resolved to a real log entry, **leave that entry in the log** and report the mismatch. **Never remove an entry you didn't positively identify.**
- **Overlap:** an entry claimed by more than one fold moves exactly once, into the **earliest-created** fold that claims it. The later fold records the count it actually holds, not the count it claimed.
- **Every numeric claim in Key outcomes is grep-verifiable** against a child entry.
- **The fold ID is deterministic** and its file does not already exist.

### 6. Emit

**Dry-run (default):** print the fold page, its ID, and what commit would do. Write nothing.

**Commit** (only after the owner confirms):

1. **Write `wiki/folds/{FOLD-ID}.md`**, including the verbatim section.
2. **Remove the folded entries from `wiki/log.md`** and leave one pointer line where the newest of them sat:
   ```
   ## {TO} — [folded] {N} entries ({FROM} to {TO}) → [[wiki/folds/{FOLD-ID}|{FOLD-ID}]]
   ```
   ⚠ **The link target is the full vault path `wiki/folds/{FOLD-ID}`.** A link containing `/` must match a real path from the vault root; a partial path like `folds/{FOLD-ID}` does not resolve.

   `{N}` is the number actually moved, which may be lower than `2^k` if the self-check left some behind. Report any shortfall.
3. **Confirm `wiki/index.md` has a `## Folds` section before relying on it.** If it is absent, add it. Then list the fold there — **a fold nothing links to is a file nobody finds.**
4. **Prepend the log entry:**
   ```
   ## {TODAY} — [vault] Log fold: k{K} rollup of {N} entries ({FROM} to {TO})
   - Location: wiki/folds/{FOLD-ID}.md
   - Range: {FROM} to {TO}
   - Children moved: {N} — log.md {BEFORE} → {AFTER} lines
   ```
   ⛔ **`{AFTER}` is `wc -l < wiki/log.md` taken *after* this entry is in the file — never a count computed before the entry is written.** Write the entry with a placeholder, run `wc -l`, fill in the number, then run `wc -l` again and confirm it still matches. **`log.md` is append-only: this entry has to be right the first time, because a wrong figure cannot be corrected by editing it later.**

### 7. Reconcile — required, and reported

After writing: `entries remaining in log.md` + `entries across all fold pages` = `entries before the fold`. **If that doesn't balance, something was lost — stop and report** rather than proceeding.

---

## Fold page frontmatter

```yaml
---
type: fold
title: "Fold k{K} — {EARLIEST-DATE} to {LATEST-DATE} — n{COUNT}"
fold_id: "fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}"
batch_exponent: {K}
entry_count: {COUNT}
entry_range:
  from: "{EARLIEST-DATE}"
  to: "{LATEST-DATE}"
created: "{TODAY}"
updated: "{TODAY}"
tags:
  - meta
  - fold
children:
  - date: "{YYYY-MM-DD}"
    title: "{log entry title verbatim}"
    summary: "{one extractive sentence}"
---
```

---

## Rules (binding)

- **Extractive only** — no invented facts, no synthesis beyond the children.
- **Dry-run by default** — write nothing until `--commit`.
- **Subtractive, and lossless** — child entries **move** into the fold page verbatim (headings demoted `##` → `###`) and are removed from `log.md`. Never edited, never deleted. A fold that doesn't shrink `log.md` did nothing.
- **Oldest first, and verified.** No unfolded entry may sit below the folded span.
- **Never remove an entry you didn't positively match.** Unresolved children stay in the log and get reported.
- **An entry moves exactly once** — the earliest-created fold wins any overlap.
- **The log entry's line count is measured after the entry is written**, and checked twice.
- **Reconcile before finishing** — remaining + moved must equal the original count.
- **Duplicate detection** — always check before writing.
