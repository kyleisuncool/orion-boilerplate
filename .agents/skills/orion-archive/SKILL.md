---
name: orion-archive
description: "Archive a whole engagement (an Area with all its Projects, or a dissolving Project whose Area stays live) into a PARA-mirrored bundle under 5. Archive/, or restore one that's resuming. Moves the folders, keeps reusable research where it is, downgrades people whose only tie was the engagement, writes a tombstone manifest, and repoints every inbound link, ledgers included. People, Vendors, Threads and Decisions never move. Fully reversible. Triggers on: archive project, archive area, archive [name], wind down [name], resume [name], restore [name], unarchive [name]."
---

# orion-archive — retire or restore a whole engagement

`orion-cascade` syncs the wiki layer and `orion-review` prunes loose ends; `orion-archive` is the one-time operation that closes out an engagement when it ends or pauses.

**Never delete.** Everything moves to `5. Archive/`; nothing is discarded. The tombstone exists so a later session can find and restore it. **Restoring is a first-class operation** — an archive isn't fully specified until reversing it is too.

**Archiving is a change, not a repair. Confirm with the owner before moving anything.**

---

## Archive or close? Check first.

| | `orion-close` | `orion-archive` (this skill) |
|---|---|---|
| **Trigger** | A workstream **finished** | An engagement **ended or paused** |
| **Unit** | One workstream | An Area and its Projects, as one bundle |
| **The Area** | **Survives and gains knowledge** | Moves into the bundle |
| **Reversible** | No | **Yes**, fully, via `resume` |
| **Shape** | `5. Archive/<Area>/<ID>/` — one folder, no manifest | PARA-mirrored bundle **with** a tombstone |

**The test: is the Area staying?** Area stays and one piece of work inside it is done → `orion-close`. Area is going away → this skill.

⚠ **Don't close every workstream inside an Area before archiving it.** Archive the bundle; the workstreams travel with it.

---

## The bundle

```
5. Archive/<Bundle Name>/
  _index.md                      ← tombstone manifest (required)
  1. Projects/<Area>/<Name>/...  ← every Project under the Area, swept wholesale
  2. Areas/<Area>/...            ← the Area folder, knowledge/ included
  3. Resources/Research/...      ← only single-owner research from the root (see below)
  <ID>/...                       ← closed workstreams already here from orion-close
```

- **Projects are subfoldered by Area, so archiving an Area sweeps `1. Projects/<Area>/` wholesale.** A hub's `area:` field is a fallback for anything filed outside that folder.
- **Area knowledge travels by construction** — it already lives in `2. Areas/<Area>/knowledge/`.
- ⚠ **`5. Archive/<Area>/` may already exist and hold closed workstreams.** That is not a collision — **merge into it.** The `<ID>/` folders already there keep their shape; the tombstone goes at the bundle root.
- **Every workstream keeps its `id:`.** IDs are never reused, including after archival.

### Naming the bundle

- **The bundle is named for the Area when the Area is archiving** — even with only one Project in it.
- ⚠ **When only a Project archives and its Area stays live, name the bundle for the dissolving Project**, and put that Project's descendants (work spun out of it) in the same bundle, so one lineage is one bundle.
  - ✅ `5. Archive/Pricing Experiments/1. Projects/Pricing Experiments/` — the `Website` Area is still live
  - ❌ `5. Archive/Website/` — names a bundle after a **live** Area and reads as though it had been archived
- The same path shape applies whether you archive a whole engagement or tuck away one stale file from a live project — the vault never runs two conventions in parallel.

### The ownership test — what stays flat

Before bundling anything outside the Area and Project folders, ask: **does this content have exactly one owning Area?**

- **Yes, one owner** → bundle it with that Area.
- **No — cross-cutting or vault-wide** → never bundle it, whatever it's called. It stays exactly where it is.

That is why `5. Archive/Threads/` and archived lint reports stay flat: a thread can span Areas, and a lint report describes the whole vault. **The rule is the test, not a list of special folders** — a new cross-cutting type stays flat automatically.

---

## What moves, what doesn't

| Category | Action |
|---|---|
| `1. Projects/<Area>/` | **Moves** into the bundle |
| `2. Areas/<Area>/`, including `knowledge/` | **Moves** into the bundle |
| Single-owner files in `3. Resources/Research/` root (classified below) | **Move** into the bundle's `3. Resources/Research/` |
| Reusable research in `3. Resources/Research/` root | **Stays**, untouched |
| Vendors (`3. Resources/Vendors/`, if the vault keeps them) | **Never move** — a vendor is a standing entity, like a person |
| People (`3. Resources/People/`) | **Never move** — downgrade, below |
| Threads | **Never bundled** — resolve or drop separately |
| Decisions (`4. Decisions/`) | **Never move, prose never edited** — dead link targets still get repointed |

### Classifying research — by content, not by tag

A file's Area tag records where it originated, not whether it's reusable. Read each candidate:

- **Area-native** (archives with the bundle): the engagement's own material — its deck, its site facts, anything obtained through that engagement's relationships (a partner's shared data, anything marked confidential or internal). It doesn't survive the relationship that produced it.
- **Reusable** (stays put): public, independent research — law, public vendor or technology research, general domain primers. Nothing about it depends on the engagement.

For a reusable file staying in the root: **strip the Area tag and any `areas:` field** (root research carries topic tags only), and add one provenance sentence near the top noting where the research originated, phrased as history, not ownership. Add a topic tag to `wiki/meta/tags.md` if none fits.

**Ambiguous → ask the owner.** Don't guess.

### People — downgrade, don't move

For every person whose **only** tracked relationship is this engagement:

- **Set `tier: contact`.** The page keeps every fact, link and its history; it stops being able to flag.
- **Remove `cadence:` and `follow_up_by:` entirely.** A contact carries neither; their presence on a contact page is a lint finding.
- **Leave the Area tag alone.** It records where the person entered the vault. Add a tag if a second Area applies — never strip one.
- Add one dated Contact History line: archived, tier changed.

**Anyone still armed whose follow-up was for the archived work** — a relationship outside the engagement, or not scoped by it alone — **is released, not changed:** one `Released:` line in the log entry (name, `follow_up_by`, what it was for), same as `orion-close`. The next weekly sweep carries them. Whether the relationship outlives the work is the owner's call.

### Decisions — untouched

No moves, no status changes, no annotations, unless the owner asks for that as a separate step. Only a dead link target inside one is repointed.

---

## Sequence

⚠ **Exclude every path listed under Fences in `AGENTS.md` from every scan, grep and move in this skill.** Links into a fence are checked for existence only. Fenced content that must move moves by path, never by content — ask before touching even one line inside it.

1. **Inventory** — every file under the Area and its Projects; root research tagged for the Area; Vendor pages introduced through the engagement; every person whose primary or only context is the engagement; threads naming it.
2. **Classify research** per the rule above. Flag anything ambiguous.
3. **Confirm with the owner** — the bundle name, what moves, what stays.
4. **Vendor pages sitting inside the Area folder** belong in `3. Resources/Vendors/` — move them there in this pass, not into the bundle.
5. **Move the Project and Area folders** into the bundle (`git mv` if the vault is a git repo, to keep history).
   - **5b. File plane (optional — only if the vault uses `registry/endpoints.md`).** Each workstream folder (default layout `~/Documents/YYYY-MM-DD-<ID> <Name>/` — a default the owner can change in `registry/endpoints.md`) and the Area's folder move to the file plane's archive (default `~/Documents/_archive/`), same name, **through the mover** — `python3 <skills-repo>/scripts/fpmove.py "<old>" "<new>" --reason archive --note "<bundle>"`, run from the vault root so it finds the vault's `registry/` (or set `$ORION_REGISTRY`), which writes the row in `registry/file-moves.md`. Never by hand. List each move in the tombstone. Then `python3 <skills-repo>/scripts/repoint.py <vault> --apply` (one `--fence` per fenced path) updates the path in every page, ledgers included, path only. File-plane pointers are backticked paths, not wikilinks — step 8's scan doesn't see them.
6. **Move single-owner research** into the bundle's `3. Resources/Research/`; **retag reusable research** in place.
7. **Write the tombstone** — format below.
8. **Repoint inbound links — everywhere, ledgers included. There is no exempt list.**
   - Scan every `[[…]]` in the vault (full-path and bare-name forms; ignore code blocks) for targets at the old paths. **A grep hit is a hypothesis** — resolve each against the real tree.
   - **In scope:** hubs, person pages, threads, `wiki/hot.md`, `wiki/log.md`, `wiki/folds/`, `4. Decisions/`, `wiki/meta/`, archived files, **and files inside the bundle itself** — files that moved together still need their cross-references repointed to the new in-bundle paths.
   - ⚠ **Only the link target changes — never a word of prose, a date, a claim or a heading.** A ledger entry keeps saying exactly what it said; the pointer just resolves again. That is what keeps this inside the append-only rule.
   - **Where the target's name changed, not just its path**, keep the original wording with a display alias: `[[new/path/Correct Name|What The Entry Originally Said]]`. (A misspelled person's name is a typo, not a claim — fix it outright.)
   - ⚠ **A "leave historical links stale" policy is a defect generator** — every archived engagement would leave the ledger pointing at paths that no longer exist.
   - **Rescan from scratch and confirm zero new dead links.** A link repointed to a second wrong path is worse than the one you started with.
9. **Downgrade and release people** per the rule above.
10. **Retire the Area tag** in `wiki/meta/tags.md` (mark it archived; pages keep it as provenance).
11. **Log** one `[vault]` entry (with `Released:` if any), and suggest `cascade` — structure changed.

---

## Tombstone — `_index.md` at the bundle root

```markdown
---
type: archive
subject: <Name> — archive bundle
date: YYYY-MM-DD
tags: [archive, <area-tag>]
---

# <Name> — archived YYYY-MM-DD

**Why:** one or two sentences — what happened, no speculation.

## In this bundle
- 1. Projects/<Area>/ — <which workstreams, by ID and name>
- 2. Areas/<Area>/ — hub and knowledge/
- 3. Resources/Research/ — <which files, and why they aren't reusable>
- File plane — <each folder moved, old → new> · or none

## Deliberately not in this bundle
- Finished external deliverables (a shipped repo, a sent deck) — linked, not duplicated
- People — <who stayed in 3. Resources/People/, downgraded to contact>
- Vendors — <who moved to 3. Resources/Vendors/, if any>
- Threads — <which, and their status>
- Decisions — untouched in 4. Decisions/

## Links
Repointed N inbound links; rescan: 0 new dead.

## If this resumes
Run `resume <Name>` — orion-archive, restore path.
```

---

## Restore — `resume <Name>`

1. **Read the tombstone first.** It lists exactly what's in the bundle. Don't reconstruct from memory.
2. **File plane (if used):** move each folder the tombstone lists back from the archive root, `fpmove.py … --reason restore`, then `repoint.py`.
3. **Move the Project and Area folders back** to their exact pre-archive paths (`git mv`).
4. **Move area-native research back into the Area's `knowledge/`**, not the `3. Resources/Research/` root — single-owner material belongs to its Area while the Area is live. This is a new path, not the pre-archive one; links follow it in step 6.
5. **Re-promote downgraded people:** restore the `cadence:` each had immediately before the archive — read it from the archive commit's diff of their page rather than guessing — and set a real `follow_up_by:`. Deviate only if something concrete about the resumed relationship changed. Add a new Contact History line; don't edit the old one.
6. **Repoint links back — everywhere, ledgers included, same method as step 8.** ⚠ A restore breaks the same links in the other direction, and the links the archive pointed into the bundle are now the stale ones. Two destinations: Project/Area content → its exact pre-archive path; research → its new `knowledge/` path. Only targets change. Rescan to zero new dead.
7. **Keep the Area's `workstream_counter:` as it was.** IDs issued before the archive stay spent.
8. **Retire the tombstone, don't delete it:** append `## Resumed YYYY-MM-DD` noting the bundle's folders were emptied. (The tombstone has no `status:` field — don't invent one.) **The bundle's permanent end state is that one file** — complete, not an unfinished cleanup.
9. Un-archive the tag in `tags.md`. Log. Cascade.

⚠ **Known limitation — ask, don't decide.** Step 3 moves the *whole* folder back, including files that were archived independently of this engagement (old superseded drafts tucked into the bundle earlier). Their reason for being archived hasn't gone away. **List them and ask the owner which stay archived**; don't silently decide.

Vendors and Decisions never need restoring — the archive never moved them.

---

## Output

```
## Archive — <Name>

Bundle: 5. Archive/<Name>/ (named for <Area | dissolving Project>)
Moved: 1. Projects/<Area>/ (N workstreams) · 2. Areas/<Area>/ · N research files
File plane: <folders moved> · or not used
Stayed: <reusable research, threads, vendors>
People downgraded: <names> · Released: <name — follow_up_by, what it was for> · or none
Links repointed: N — rescan 0 new dead
Tombstone: 5. Archive/<Name>/_index.md
Open for the owner: <ambiguous classifications, if any>

Next: run cascade.
```

## Rules

- **Never delete.** Everything is a move; always reversible.
- **Confirm before moving** — archiving is a change.
- **Bundle name:** the Area when the Area archives; **the dissolving Project when the Area stays live**, with its descendants in the same bundle.
- **The ownership test decides what's bundled.** Cross-cutting content stays flat, permanently.
- **Research is classified by content, not by tag.** Ask when ambiguous.
- **People, Vendors, Threads and Decisions never move.** People downgrade to `tier: contact` with `cadence` and `follow_up_by` removed; armed people tied to the work are released, not changed.
- **Area tags are never stripped** from pages — they are provenance.
- **Repoint every dead link the move creates, ledgers and the bundle itself included. Only the target changes. Rescan to zero before reporting done.**
- **File-plane folders move through `fpmove.py`, never by hand** — when the vault uses the file plane.
- **Fenced paths are never read or scanned.** Fenced content moves by path only.
- **A tombstone is required** for every bundle, however small.
- **Never reset a counter on restore.** IDs are never reused.
