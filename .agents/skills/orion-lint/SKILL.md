---
name: orion-lint
description: "Health-check an Orion vault: orphans, dead links, missing pages, frontmatter and workstream-contract gaps, people-tier defects, unsourced reference material, vocabulary violations, misplaced and misfiled files, stale holds, unenforced cadences, and (optionally) file-plane pointers. Attention checks skip paused and archived material; integrity checks run vault-wide, 5. Archive/ included. Writes exactly one wiki/meta/lint-report-YYYY-MM-DD.md stamped with the git commit it ran against; the previous report is archived. Flags only — never auto-fixes. Triggers on: lint, health check, audit the vault, check the vault, find orphans, find dead links, vault audit."
---

# orion-lint — vault health check

**Flags only.** Lint reports findings; the owner or the next session decides. (Repairs a report surfaces may then be made under the *Repair* rule in `AGENTS.md`.) Run every 10–15 ingests, or weekly.

---

## Delegation (optional)

**Every check here is mechanical** — glob, grep, resolve, compare. If your harness has the `orionite` agent, **dispatch the whole job to it**: the vault path, this skill, and an instruction to return only the report path and its findings summary. **It must not return** file contents, grep dumps, or its reasoning.

⚠ **The scans go inside the agent, not in the main thread.** Twenty checks across a real vault is a large number of tool calls with large outputs — exactly what dispatching keeps out of the main context. Handing an agent a pre-computed summary to format saves nothing.

**Two things stay in the main thread, and both are non-negotiable:**
- **Verify every count before it is written down.** Link resolution is easy to get wrong — a resolver that ignores check 2's own rule about code spans produces a confident, wrong number.
- **Don't accept a dispatched run's claim that it verified something.** A delegated pass can report success while shipping errors. Spot-check what it wrote.

If you have no such agent, run the checks in the main session — the procedure is the same.

---

## Scope — read this first, it determines everything else

**Every check is either an *attention* check or an *integrity* check. The test is one question:**

> **Would this finding stop being true if nobody ever worked on this file again?**

| | Answer | Scope |
|---|---|---|
| **Attention** | **Yes** — the finding is *"this needs someone's attention"*, and archived material isn't asking for any | **Skip** `paused`/`closed`/`archived` hubs and every file in their folders |
| **Integrity** | **No** — the finding is *"this is broken"*, and a broken thing stays broken whether or not anyone looks | **Run vault-wide, `5. Archive/` included** |

**Every new check classifies itself against that question before it is written.** Inheriting a blanket skip is how a lint goes blind.

**Why both halves matter.** *Attention:* a paused project is *supposed* to generate zero findings; honouring that is the biggest lever on report size, and a report full of findings about dormant material is a report nobody acts on. *Integrity:* a blanket archive skip on a dead-link check hides every link that went stale when `orion-archive` moved things — and the report reads clean. **A false flag is bad; a falsely-silenced flag is worse, because nothing reports silence.** Archive integrity findings are a fixed-size backlog, not a recurring tax — report them under their own heading so they never crowd live findings.

### Which check is which

| Attention — skip `paused`/`closed`/`archived` | Integrity — run vault-wide |
|---|---|
| 1 Orphans · 3 Missing pages · 7 Misplaced files · 8 Stale content · 9 Attention budget · 10 Misfiled reference · 12 Stale holds · 14 Standalone Areas · 16 Untouched `open` workstreams | 2 Dead wikilinks · 5 Link style · 6 Stale index entries · 11 Provenance · 13 Vocabulary · 15 Workstream contract · 17 Area knowledge misfiled · 18 Unenforced cadences · 19 File plane (optional) |

**Check 4 (frontmatter) is split by the same question.** The *contract* fields — `type`, `updated`, a Decision's `status`/`date`/`topic`, a Project's `id`/`done_when` — are integrity: a malformed file is malformed in the archive too. The *attention* fields — `next`, `paused_because`, `cadence`, `follow_up_by` — exist to make something flag, and archived material is not supposed to flag.

⚠ **Check 1 stays on the attention side deliberately.** An archived file with no inbound link is not broken — unreachable from live hubs is what *archived* means. A dangling pointer never is.

**Areas carry `status: standing` and no attention status.** Never compute freshness or drift on an Area.

**Report against a known tree.** If the vault is a git repo, record `git rev-parse --short HEAD` in the report frontmatter. If the working tree is dirty, say so at the top — a report generated mid-edit describes a state that may no longer exist.

**Every check is run mechanically** — grep and glob against actual file contents, resolving every candidate against every source file. **Never estimate from a partial read or generalise from a sample.** This matters most when the work is delegated: a model reading a handful of files will confidently generalise instead of resolving each one, and a whole report of false positives is the result.

### ⛔ Fenced paths — excluded from every check, integrity checks included

**`AGENTS.md` is the register of fences** (its *Fences* section). Read it first; if it names none, this section is a no-op. **Read the fence list from the vault being linted, never from memory or from this file.**

**Never open a file under a fenced path** — not for dead links, frontmatter, orphans or anything else. Links *into* a fenced path from outside are resolved by an existence probe on the exact target. **Report the fence as one context line, never as a finding.** Any known cost of the fence (dead links inside it, unverifiable frontmatter) is recorded beside it in `AGENTS.md`, not rediscovered each run.

⚠ **This does not contradict "run vault-wide."** An integrity check that skips archived material goes blind by accident; a fence is the owner's explicit instruction not to read a path. **Only the owner adds or lifts one.**

**A retired Area tag is not an Area tag.** `wiki/meta/tags.md` lists any retired tags; check 10 must not treat one as a match or a mismatch anywhere.

---

## Vault structure

```
0. Inbox/            — daily notes and captures
1. Projects/         — finite work, each with <ID>_hub.md
2. Areas/            — ongoing responsibilities, each with <Area>_hub.md and knowledge/
3. Resources/        — People/, Threads/, Research/ (and Vendors/, Pipeline/ if the vault uses them)
4. Decisions/        — immutable decision log
5. Archive/          — finished or retired work
6. Templates/        — skeletons and _contracts.md
wiki/                — navigation layer (hot, index, log, folds, meta)
```

**Structural invariant — check it every run:** the total word count of `wiki/` must be **less than** the total across the numbered folders. `wiki/` is navigation; if it outgrows the territory it navigates, it has become content. **Report both numbers every time.**

**Naming conventions to check against:**
- Folders: Title Case with spaces.
- Hubs: `<ID>_hub.md` for Projects, `<Area>_hub.md` for Areas. ⚠ **Match on the `_hub` suffix, never the whole filename** — a query keyed on a full name matches nothing and reports green.
- People: `Full Name.md`. Decisions: `YYYY-MM-DD-[slug].md`.

---

## Lint checks (run in order)

### 1. Orphan pages — attention

Pages with no inbound wikilink from any hub, navigation file or person page.

**Do not eyeball this.** Run it as an explicit two-pass resolution:

1. **Collect the target set.** Extract every `[[wikilink]]` target from all `*_hub.md` files (**including hubs inside `5. Archive/`** — an archived hub stopped being live, but its links still count as a source), `wiki/index.md`, `wiki/hot.md`, `3. Resources/People/*.md` and `3. Resources/Threads/*.md` (live and archived). Strip `|alias` suffixes and normalise each target to a bare path/filename (e.g. `grep -ohE '\[\[[^]|]+'`, trimming `[[`). Threads are a first-class navigation surface — a file linked only from a thread is reachable.

   **Also count backtick paths as inbound references.** A file cited as `` `3. Resources/Research/foo.md` `` is documented, just not wikilinked. Report these separately as **"referenced by path, not wikilinked"**, with a suggestion to convert.
2. **Test every candidate.** For every `.md` file in the numbered folders (excluding hubs and anything under `5. Archive/`), check whether its filename — with and without `.md`, and as its full relative path — appears anywhere in the target set.
3. **Report only genuine absences** — absent for every candidate form, not "looked unlinked" from reading a few hubs.

If a file's only inbound link lives inside an archived hub, say so and label it **a benign archival byproduct**, not a defect.

**Exempt entirely — orphaned by design.** The correct action on each is "nothing", so reporting them is noise:

| Exempt | Why nothing will ever link to it |
|---|---|
| **`4. Decisions/`** | Immutable ledger, and `orion-archive` never moves Decisions. A decision whose engagement archived is orphaned permanently, by design |
| **Root-level `3. Resources/Research/`** | The Knowledge Base: area-less, reusable, outliving any one project. Subfolders are not exempt (see check 17) |
| **`3. Resources/Vendors/`** (if the vault has it) | Cross-project standing entities that don't archive with the project that introduced them |
| **Vault-root files** | `AGENTS.md`, `CLAUDE.md`, `README.md` and siblings — operating manuals, not vault content |
| **`6. Templates/`** | Referenced by skills and by hand, never wikilinked |
| **`3. Resources/People/`** | `wiki/index.md` lists every person page (relationship tier and contacts) — no person page is an orphan in practice |

⚠ **The query blind spot is the general lesson.** If the owner has replaced any `wiki/` section with a Dataview (or similar) query, it generates links *at view time* — a text-extraction pass finds nothing and reports every target unreachable. **A file covered by a query is reachable; the check just can't prove it.** Before reporting any orphan, ask whether a generated surface already enumerates its folder.

**When a check keeps producing the same backlog, suspect the check.** If a run reports an orphan, treat the finding as suspect first and the file second.

### 2. Dead wikilinks — integrity, vault-wide

`[[wikilinks]]` whose target doesn't exist. Scan all files for `\[\[.*?\]\]`; resolve each target against the full vault path, then by bare filename anywhere in the vault.

⚠ **`5. Archive/` is both a valid link target and a valid link source.** Both halves are required:
- **As a target:** a link into the archive that resolves to a real file there **is not dead.**
- **As a source:** **files inside `5. Archive/` are scanned like every other file.** A pointer that resolves to nothing is broken whether or not anyone will open the file again.

**Scan mechanics — get these right or the count is fiction:**
- **Exclude fenced code blocks and inline code spans.** Skills and reports contain illustrative `[[old/path]]` syntax that is documentation, not a link.
- **Strip trailing backslashes and escape artifacts** (a `\|` inside a table cell) before resolving.
- **Resolve relative forms explicitly.** Links inside a PARA-mirrored archive bundle may read `../../../1. Projects/…`; they resolve from the containing file, not from the vault root.
- **Sanity-check the total against a second method before reporting it.**

**Report archive findings under their own heading**, separate from live findings.

### 3. Missing pages — attention

Entities (people, projects, places) mentioned in 3+ files without a page of their own. Name the files and suggest a page type (person / hub / resource).

### 4. Frontmatter gaps

**Exempt entirely:**

| Exempt | Why |
|---|---|
| **Vault-root files** (`AGENTS.md`, `CLAUDE.md`, `README.md`) | Operating manuals, not typed vault content |
| **`6. Templates/`** | A skeleton by definition; demanding it be filled defeats it |
| **`0. Inbox/` notes** | The convention there is `date:` + `tags:`, no `type:` (`_contracts.md`, *Inbox notes*) |

**The general rule worth carrying:** before reporting a missing field, check whether *any* file in that folder has ever carried it. **A field absent from every file in a folder is a convention, not a set of defects.**

Required, against `6. Templates/_contracts.md`:
- **Every file in the numbered folders below `0. Inbox/`:** `type`, `updated`.
- **Hubs:** `status` in the vocabulary. **`type` is `project` or `area` — `type: hub` is a defect.**
- **Project hubs:** `id`, `area` (a value or the literal `none` — absent ≠ none), `done_when` (see check 15), `paused_because` when paused. Filename is `<id>_hub.md`.
- **Area hubs:** `id_prefix`, `workstream_counter`; `parent` when nested, and **never equal to the Area's own name**.
- **People:** `tier` (`relationship` | `contact`) and `last_contact`.
  - `tier: relationship` — **also** `cadence` and `follow_up_by`. A relationship page missing `follow_up_by` **cannot flag and is therefore invisible** — report it as a defect, not a gap. Silent people behind an "all clear" dashboard is the failure this prevents.
    - **A spent `follow_up_by` — on or before `last_contact` — is not a defect and never reports as overdue.** The live date is computed (`_contracts.md`, *Spent follow-ups*). A spent `organic` page reports one attention line: **no date since contact**.
  - `tier: contact` — **must not** carry `cadence` or `follow_up_by`. Their presence is the finding; a contact that can flag defeats the tiering.
- **Decisions:** `status`, `date`, `topic`. **Threads:** `status`, `opened`.
- **Opportunities** (`3. Resources/Pipeline/`, if the vault keeps a pipeline): `stage`, `vehicle`, `for`, `owner`, `opened`.
  - **`confirmed:` blank is not a gap** — it is a deliberate admission that nobody has verified the entry. Never "fix" it by filling in a date. Report the count of unconfirmed live opportunities as one line so the number stays visible.
  - A live opportunity (`stage` not `dead`) with no `next:` is a finding.
  - An opportunity whose `people:` names someone with no page in `3. Resources/People/` is a finding — money attached to a name the vault can't identify.

### 5. Wikilink style — integrity

Links carrying a bare `.md` extension (`[[file.md]]` instead of `[[file]]`). Name the containing file.

### 6. Stale index entries — integrity

Entries in `wiki/index.md` or `wiki/hot.md` pointing at files that moved, were renamed, or no longer exist — and live hubs, people, threads or decisions that `index.md` doesn't list (cascade rebuilds it when structure changes; a gap means a rebuild was missed).

If any section of `index.md` is a query rather than a list, check the query resolves: **a query block that renders zero rows while its folder is non-empty is a finding** — it means the query is wrong (e.g. still selecting a retired `type:` value), not that the folder is empty.

### 7. Misplaced files — attention

- Content files in `wiki/` other than the navigation layer. **Never flag:** `wiki/hot.md`, `wiki/index.md`, `wiki/log.md`, `wiki/folds/*`, `wiki/meta/*`, and any other navigation file `AGENTS.md` names under `wiki/`. Those carry `type:` frontmatter by design; that alone is not a misplacement signal.
- Hubs outside `1. Projects/` or `2. Areas/`.
- Person pages outside `3. Resources/People/`. Decisions outside `4. Decisions/`.
- Binaries (PDFs, images, office files) inside the vault — **the vault holds knowledge, not files** (`AGENTS.md`, *The classification test*). The binary belongs outside the vault; the vault holds an attributed note and a path.

### 8. Stale content candidates — attention

Files that appear superseded by newer work in the same hub or Area. Flag when a file in a project folder predates its hub's `updated:` by 60+ days and has no recent inbound links.

### 9. Attention budget — attention

1. **`next:` valid.** Every entry on a Project hub uses a valid verb — `send` · `wait` · `build` · `decide` — and `send`/`wait` name a person. `next:` may be a YAML list; check every entry.

⚠ **`status: open` carries no clock and no cap — that is the point.** `open` is tracked, not committed: real, identified work with no promise attached. **It is uncapped, it can never be "stale", and it needs no `next:`.** Ageing it recreates the manufactured urgency the status exists to remove. **Report the `open` count as context, never as a finding.** Check 16 is the only thing that ever fires on one.

2. **Outstanding sends.** Report every `send` and `wait` with its age: `[since YYYY-MM-DD]` is the authority; without it, fall back to git (`git log -1 --format=%ad --date=short -S'next:' -- <hub>`); if neither is trustworthy, render no age. **A `send` older than 14 days goes at the very top of the report, above every structural finding** — it is gated on a person, it is what vaults historically lose, and it is worth more than all the structural findings combined. Apply holds as `orion-cascade` does (`AGENTS.md`, *Holds*).

### 10. Misfiled reference material — attention

`type: reference` means "reference-shaped document", not "Knowledge Base material", so a reference file inside a Project or Area folder is not misfiled by being there. **Placement is decided by whether the content survives the workstream's close** — durable material belongs in the Area's `knowledge/` (what `orion-close` migrates). That is a judgment call, **not a lint finding.**

**Flag only these two cases:**
1. **The Area tag doesn't match the containing Project/Area folder** — genuinely misfiled, unambiguous destination.
2. **No Area tag at all, while living inside `1. Projects/` or `2. Areas/`** — absence of an Area tag is the Knowledge Base signal (`wiki/meta/tags.md`), so it belongs at `3. Resources/Research/` root.

⚠ **Resolve a tag against the Area's accepted set — its own tag plus any tags `wiki/meta/tags.md` assigns to its Projects — not against the folder name.** A sub-project tag inside its parent Area is a match. Retired tags are neither match nor mismatch.

**Don't flag** a reference file whose Area tag matches its folder; that is working material, correctly filed. Report each finding with current path, inbound-link count and suggested destination.

### 11. Provenance — integrity

Mechanical checks, all cheap:

1. **Unsourced reference files.** Every `type: reference` file has a non-empty `source:` (or "source unrecorded"). Also: any `type: reference` file over ~150 lines whose body carries no attribution at all — no author, sender, URL, originating conversation or "source unrecorded". Report path and line count.
2. **Vault-voice claims tracing to an unconfirmed source.** A hub bullet, `hot.md` line or summary asserting a fact (a commitment, a figure, a relationship) whose only origin is a file failing point 1.

**Why this is a check and not a preference.** Provenance looks clean the whole way down — every downstream file honestly cites the one above it — and nobody checks the top of the chain. An unsourced document can seed hub bullets, a log line and a live memo with named commitments the owner has never heard of. **This is the failure the other checks structurally cannot catch.**

**Never auto-fixable.** The resolution is always the owner confirming or striking the source. Anything surviving two cycles goes to `wiki/meta/open-questions.md` as a forced binary: *treat as unverified, or accept as canonical.*

### 12. Stale holds — attention

Read `wiki/meta/holds.md`:
1. **An open hold with no end date, older than 30 days → finding.** Either it ended and nobody closed it, or it isn't a hold, it's the new normal.
2. **An open hold with no start date, older than 7 days → finding.** A hold may open undated and still render correctly, but an undated hold can never *close* — there's no span to subtract.

**A hold that never closes is coverage that looks like protection and provides none**, applied to the whole vault at once — its symptom is silence: no ages, no flags, nothing overdue. **A hold changes how age renders; it never discharges an obligation.** If a run finds an open hold *and* unmoved sends, report both.

### 13. Vocabulary enforcement — and the table is a suspect, not an authority — integrity

Read the **Vocabulary enforcement** table in `AGENTS.md`. For every row — canonical form, one or more banned forms — grep the vault.

⚠ **A row's scope qualifier is part of the row. Honour it or the row is unusable.** A row like `` `partner` (for the agency's work) `` only applies inside that scope; grepping an ordinary word vault-wide hits every unrelated use of it, and fires again on every future run forever. **Before grepping a banned form, ask: is it a coined or proper form, or an ordinary word?** A coined or proper form can be searched vault-wide. **An ordinary word can only be searched inside the scope its row names** (files tagged for, or living under, that Area or person). **If a row's scope can't be determined mechanically, report the row as unenforceable rather than reporting its hits.**

1. **Banned form present in vault-voice prose → finding.** Path, line, which row.
2. ⚠ **Banned form and canonical form both have zero hits → a finding about the row, not the files.** Report it as a **suspect row**: it asserts a correction nobody uses — most likely it is wrong, stale, or about someone the vault no longer references. **A table that enshrines a half-corrected spelling as canonical will validate every misspelling against a false canon and report green. The table is data to be tested, not the test.**

**Exempt — deliberate mentions,** where a file's job is to *name* the error:
- `AGENTS.md`'s own vocabulary table
- `wiki/meta/open-questions.md` and any lint or review report
- A person page's **Contact History** entries narrating a spelling correction
- Any string marked as a verbatim quote from a source — that is provenance, and it is load-bearing
- `0. Inbox/processed/` — the owner's own captures and the origin record of the error. Never rewrite what they typed

Without these exemptions the check fires forever on the files documenting the fix.

**Flags only** — ⚠ **with one exception: a misspelled person's name is a typo, not a claim,** and is repaired on sight under `AGENTS.md`, *Repair*, rather than reported. Record the repair in the log.

### 14. Standalone Areas — absolute age, not drift — attention

An Area hub with **no live (`open`) Project naming it in `area:`** is checked on **absolute age**: `updated:` more than **30 days** ago → finding.

**Why the normal checks can't see these.** Freshness on an Area is only meaningful relative to its Projects; **a projectless Area has nothing to drift against, so it never flags** — a check that structurally cannot fire. Thirty days catches a cold, projectless Area at day 30 instead of never.

**Not every hit is a defect.** **Report the age; don't prescribe a fix** — the honest outcomes are *update it*, *give it a Project*, or *archive it*, and which one is the owner's call.

⚠ **Before flagging, check `4. Decisions/` for an open decision naming the Area.** If one exists, report the age **with the decision cited**, not as a finding. Areas have no `paused` status, so there is no field in which to say "quiet on purpose" — without this exemption the check manufactures a false flag on the Area whose silence is most deliberate.

**Projectless is the normal case for an Area.** Report the count as context so a run listing six doesn't read as six defects.

**Also, on every Area hub regardless of age:** `parent:` pointing at itself → finding · `type: hub` instead of `type: area` → finding. `orion-instantiate` prevents both at creation; this catches the ones that predate it.

### 15. Workstream contract — `id:`, `done_when:`, the counter — integrity

Every Project is a workstream and carries both fields. A hub missing its contract is malformed in the archive too.

1. **A Project hub with no `id:`** — it can't be referenced, counted or closed.
2. **A Project hub with no `done_when:`** → ⚠ **the most important finding this skill produces.** "Ongoing work on X" has no done-when; **a workstream without one has never been tested against the question that decides whether it is a Project at all.**
3. **A duplicate `id:`** anywhere, `1. Projects/` and `5. Archive/` included. **Almost always caused by deriving the next ID from a scan instead of from the counter**: a closed workstream's hub has moved to `5. Archive/`, so a scan of `1. Projects/` sees a lower maximum than was issued.
4. **An issued ID above its Area's counter** — for each Area, every `<PREFIX>-N` in `1. Projects/` and `5. Archive/` must have `N ≤ workstream_counter:`. A higher one means the counter wasn't written back. **Raising the counter to the highest issued ID is a repair.**

**Area side:** an Area holding Projects but carrying no `id_prefix:` or no `workstream_counter:` → finding — the next `orion-instantiate` run has nothing to read. Two Areas sharing a prefix → finding.

⚠ **Never repair a duplicate ID by renumbering the older one.** IDs are permanent and cited from decisions, logs and archives. **The newer one is the mistake.**

### 16. `open` workstreams never touched — attention

**The one check that fires on `open`** — deliberately weak, because `open` promises nothing.

**An `open` workstream whose `updated:` equals its creation date and is more than 90 days old is a finding.** Report the age; **don't prescribe.** The honest outcomes are *work it*, *close it*, or *say plainly it isn't happening* — the owner's call.

⚠ **90 days, not 30 or 7, and the number is doing real work.** `open` exists so identified work can sit without generating urgency; a 30-day check turns it back into a nag list. What this guards against is slower: **a workstream created once, never touched, and quietly forgotten.**

**The threshold is a rule, not a date — compute it every run, never write "can't fire until <date>" anywhere.** A hardcoded date goes stale the moment a workstream is created.

**Verify it against a fixture**, since it won't fire naturally for months: plant an `open` hub with `updated:` equal to its creation date and 100 days old, confirm the check fires, remove the fixture. **A check that has never fired is not a check.**

### 17. Area knowledge filed outside its Area — integrity

`3. Resources/` holds only what belongs to no single Area; Area-native knowledge lives at `2. Areas/<Area>/knowledge/`.

1. **A subfolder under `3. Resources/Research/`** — the Area-native shape in the wrong place. It belongs in that Area's `knowledge/`.
2. **A file in root-level `3. Resources/Research/` carrying an Area tag** — the Knowledge Base is topic-tags-only by definition; an Area tag there contradicts where it is filed.

⚠ **If the owner has recorded a known exception** (an open item or decision naming the folder, with a reason), **cite it instead of reporting it.**

### 18. Unenforced cadences — check the checkers — integrity, never skipped

Skills that state a numeric cadence need something that measures it. **A cadence with no measurer is not a cadence, it is a hope.**

**18a. Log fold backlog.** Unfolded entries = `grep -c '^## ' wiki/log.md` **minus** `grep -c '\[folded\]' wiki/log.md`. ⚠ **A `[folded]` pointer is the tombstone of many entries, not one** — counting it as an entry keeps the number wrong in the reassuring direction. **Threshold 16.** Over it, report `unfolded: N / 16 — fold overdue by N`; **report the number even when under.**

**18b. Lint's own cadence.** This skill says *"every 10–15 ingests, or weekly."* Read the newest `wiki/meta/lint-report-*.md` date and report days elapsed. **A health check that can't say when it last ran isn't measuring its own health.**

**18c. Fold ordering.** `orion-fold` takes the oldest entries (bottom of the file). ⚠ **Report any unfolded entry sitting *below* a `[folded]` pointer** — an entry older than something already folded means a fold took a middle window and left a hole no later fold will revisit.

**Why this check exists.** A trigger written only inside the skill you'd open if you already knew to run it is never pulled — the log grows to many times its threshold while every run reports green. Enforcement lives in two places by design: `orion-cascade` prints the fold count every session, and this check catches it if cascade is skipped.

### 19. File plane — pointers and drift — integrity, optional

**Skip this check, with one context line, when the vault has no `registry/` folder at its root.** The file-plane protocol is optional.

When it's in use: files live outside the vault (by default one folder per workstream, `~/Documents/YYYY-MM-DD-<ID> <Workstream Name>/` — the owner can change that in `registry/endpoints.md`), and the vault holds the claim and a **backticked path**. A path that resolves to nothing is broken whether or not anyone opens the page again — check 2's rule, applied to the file plane.

**Run the script, don't re-derive it.** It is mechanical end to end; paste its output under `## File Plane`:

```bash
python3 <skills-repo>/scripts/fileplane_check.py "<vault>" --fence "<each fence AGENTS.md names>"
```

It reads the vault's `registry/endpoints.md` (inboxes, outboxes, working roots) and `registry/file-moves.md` (the moves ledger), plus the Area hubs' counters, and reports — flags only:

| Code | Finding | Fix |
|---|---|---|
| `STALE` | A page — live, ledger or archive — points at a path that moved; the ledger knows where | `repoint.py <vault> --apply`, which skips every path under **Fences** in `AGENTS.md` itself — a **repair**, do it. Only the path between the backticks changes, never the prose |
| `LIVE-MISSING` | A live page points at nothing, and the ledger doesn't know. Candidates by name are listed | Find where it went; record it with `fpmove.py --reason manual` if the owner moved it, then repoint. **A candidate is a hypothesis** — confirm before repointing |
| `KEPT-MISSING` | Same, inside a ledger, capture or `5. Archive/` | Its own heading, like check 2's archive backlog. Find it, record it in the ledger, then repoint |
| `MISNAMED` · `LOOSE` · `UNKNOWN-ID` | A working-root folder breaks the naming rule; a file sits loose in a root; a folder carries a prefix no Area declares | Rename via `fpmove.py` — a **change**, ask |
| `STALE-INTAKE` · `DUP-INTAKE` | An inbox item older than 7 days; an intake file byte-identical to one already filed | `orion-ingest` endpoint mode. **A duplicate is deleted only from a list the owner approves** |
| `UNREGISTERED-BOX` | An inbox/outbox-shaped folder `endpoints.md` doesn't list | Register it or retire it — the owner's call |
| `ROOT-MISSING` | A registered work or archive root is absent — every pointer into it dies | Restore or re-register the root before acting on any other code |
| `COUNTER-LOW` · `UNKNOWN-PREFIX` | A hub `id:` above its Area's `workstream_counter:`; a prefix no Area hub declares | Raise the counter to the highest issued; add the prefix — **repairs**. Cross-checks check 15 |

**Pointers outside the registered file plane** (code repos, dotfiles, paths on other machines) print as `OUTSIDE`: **one context count, never a finding.** This check owns the file plane, not every path a page mentions.

⚠ **A path that is only mentioned, not pointed at** — a retired location, a pattern, a path in a table about moves — **is written without backticks.** Backticks make it a pointer this check verifies and `repoint.py` rewrites.

⚠ **A pointer has no machine in it.** A path on another machine is written `<machine>:~/path` and listed under `OUTSIDE` without being checked. Rewriting an existing pointer into that form is a **repair** only when the page itself says which machine it was on; otherwise ask.

⚠ **The drift codes are machine-level.** If several vaults share one file plane, their drift lines are identical in every report — report them in each, act on them once.

⚠ **A first run on an un-migrated file plane is loud by design.** That is the backlog adopting the protocol exists to clear, not a reason to narrow the check.

---

## Report format

**Retention 1.** Before writing, move the previous `wiki/meta/lint-report-*.md` to `5. Archive/wiki-meta/`. Write `wiki/meta/lint-report-YYYY-MM-DD.md`:

```markdown
---
type: meta
title: "Lint Report YYYY-MM-DD"
created: YYYY-MM-DD
updated: YYYY-MM-DD
commit: abc1234          # git rev-parse --short HEAD — the tree this describes
tree_clean: true|false   # false ⇒ this report describes a state that may not exist
supersedes: lint-report-YYYY-MM-DD
tags: [meta, lint]
---

# Lint Report: YYYY-MM-DD

## Outstanding sends — read this before the structural findings
- [Person] — [what], [N] days. From `next:` on [[hub]].

*Anything here outranks everything below it. A structural finding costs a link; an unsent message costs a project.*

## Summary
- Scope: N open projects + N standing areas · **N paused/closed/archived hubs skipped for attention checks; integrity checks ran vault-wide**
- Fences: N (context only)
- Files scanned: N
- Issues found: N (X high · Y medium · Z low)
- `wiki/` N words vs numbered folders N words — **invariant holds / VIOLATED**

## Attention Budget
- Invalid `next:`: [[hub]]

## Orphan Pages
- [[Page Name]]: no inbound links. Suggest: link from [[Related Page]] or archive.
- Referenced by path, not wikilinked: …

## Dead Wikilinks
- [[Missing Page]] in [[Source File]]: target does not exist.

### Dead Wikilinks — inside `5. Archive/`
*Separate heading on purpose: a fixed-size historical backlog must never crowd out live findings. Report the count even when it is zero.*

## Missing Pages
- "Entity name": mentioned in [[File A]], [[File B]], [[File C]]. Suggest: person / hub page.

## Frontmatter Gaps
- [[File Name]]: missing fields: status, follow_up_by
- Unconfirmed live opportunities: N (if the vault keeps a pipeline)

## Wikilink Style Violations
## Stale Index Entries
## Misplaced Files
## Stale Content Candidates
## Misfiled Reference Material
- [[File Name]]: at path/to/file.md, N inbound links, suggest → …

## Provenance
- path (N lines): no source recorded

## Holds
- Open since YYYY-MM-DD (N days), scope `…` — within tolerance / **⚠ no end date, N days** / **⚠ no start date, N days**
- Items currently rendering `held`: N sends, N follow-ups — listed, not discharged

## Workstreams
- **N workstreams: O open · X paused.** The `open` count is context, never a finding.
- Missing `id:` / missing `done_when:` / duplicate `id:` / ID above counter — path each
- Areas holding Projects without `id_prefix:` or `workstream_counter:`
- `open` untouched since creation, 90+ days: [[hub]] — age only, no prescription

## Areas
- Standalone, 30+ days: [[hub]] (N days) [— decision cited]
- Projectless Areas: N (context)

## Area Knowledge
- Subfolders under `3. Resources/Research/`
- Root Knowledge Base files carrying an Area tag

## Vocabulary
- `banned form` → `Canonical Form`: N hits in M files — path:line each. *(Deliberate mentions excluded.)*
- ⚠ **Suspect row:** `Canonical Form` — zero hits for the canonical and every banned form. **The row is the finding.**
- Unenforceable row: … (scope can't be determined mechanically)

## Cadences
- **Log fold:** unfolded N / 16 [— ⚠ overdue by N] · folds on disk: N
- **Lint:** last ran YYYY-MM-DD (N days ago) — cadence is 10–15 ingests or weekly
- **Fold ordering:** N unfolded entries below a `[folded]` pointer [— or: none, ordering clean]

## File Plane
- check 19's output: the `Pointers:` line, then each code with its count and lines. `OUTSIDE` as one count. Counts even when zero — or "skipped: no registry/"

## Carried Findings — second cycle
- [Finding]: unchanged since lint-report-YYYY-MM-DD. **Next cycle this leaves the report** and becomes a line in `wiki/meta/open-questions.md`.
```

Omit an empty section except **Outstanding sends**, **Summary**, **Dead Wikilinks — inside `5. Archive/`**, and **Cadences**. ⚠ **The `Cadences` block prints every run, over threshold or under** — the failure it ends is silence, not a wrong number.

---

## The two-cycle rule

**A finding that survives two consecutive lints without action is not a finding — it is a decision nobody has made.**

On its second appearance, list it under *Carried Findings*. On what would be its third, **remove it from the report** and write one line to `wiki/meta/open-questions.md` as a forced binary:

```markdown
- **[Question]** — Option A / Option B. Raised YYYY-MM-DD, carried N cycles.
```

Then stop reporting it. Re-listing known-unactioned findings inflates recurrence into false urgency and buries new material.

**Corollary — the more important half: when a check keeps producing the same backlog, suspect the check.** Narrowing a wrong rule can clear a whole backlog without moving a file. **A rule nobody ever acts on is usually wrong, not ignored.**

---

## Output (to chat)

```
## Lint — YYYY-MM-DD @ <commit>

Sends > 14 days: N
Integrity: N dead links (N in archive) · N contract gaps · N provenance · N vocabulary · file plane: N / skipped
Attention: N orphans · N people defects · N misplaced · N standalone Areas
Log: N / 16 · last lint N days ago
Report: wiki/meta/lint-report-YYYY-MM-DD.md
Verified: <which counts were spot-checked, and how>
```

## Rules

- **Flags only — no auto-fix.** The narrow exceptions are repairs `AGENTS.md` already rules on (a misspelled name; a counter below an issued ID; a `STALE` pointer the ledger resolves). Safe auto-creates (stub pages for missing people, frontmatter placeholders) may be requested separately after the report is read.
- **Attention checks skip paused/closed/archived material. Integrity checks — dead links, style, index, provenance, vocabulary, contracts, cadences, file plane — run vault-wide including `5. Archive/`.** The test is whether the finding stops being true when nobody works the file again. Never compute drift on an Area.
- **Fences are excluded from everything**, integrity checks included. Read them from `AGENTS.md`.
- **Retention 1** — one lint report at a time; the previous moves to `5. Archive/wiki-meta/`.
- **Stamp the tree** — record the commit, and say plainly if the working tree was dirty.
- **Sends outrank structure.**
- **Two-cycle rule — and question the check before the files.**
- **Verify before trusting.** Full-vault link resolution is easy to get wrong by reading and generalising — a parsing bug on names with middle initials, or a delegated scan claiming every decision is an orphan when half are linked from live hubs. **A finding that wasn't produced by resolving every candidate against every source file is a hypothesis, not a fact.** Spot-check anything surprising — a large or round count, a well-known file reported broken — before it reaches the report or gets acted on.
