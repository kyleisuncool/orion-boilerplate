---
name: orion-ingest
description: "Bring external material INTO an Orion vault's numbered folders — every capture sitting in 0. Inbox/ by default, or a file, transcript, document or email the owner names. Follows any explicit instructions in the source, classifies the rest (decision / reference / person / narrative update) and asks only when genuinely unclear, records provenance, creates and updates pages directly, cross-links them, marks answered lines in daily notes as filed, then archives processed captures into 0. Inbox/processed/YYYY-MM/. Optional endpoint mode runs the same protocol over every registered file-plane inbox (a shared-drive inbox, a chat app's download folder, the browser's downloads): each item is matched to a workstream ID, moved — never copied — into its workstream folder with a moves-ledger row, and given a vault record. Distinct from orion-cascade, which syncs wiki/ with what's already in the folders. Triggers on: ingest, process the inbox, ingest this, file this, process new entries, ingest mail, ingest boxes, ingest <endpoint>."
---

# orion-ingest — bring material into the vault

Ingest turns raw capture — a new inbox entry, a document the owner points at, a pasted transcript — into filed, cross-linked, attributed vault content. It gives structure and a checklist, not a rigid decision tree: **placement is a judgment call, and a fixed classification table would get real material wrong.** This skill exists to make that call well.

**Ingest before cascade.** Ingest is how new material gets into the numbered folders; `orion-cascade` then syncs `wiki/` with what's there.

⛔ **Never read a path listed under *Fences* in `AGENTS.md`.**

---

## Paths

- **Inbox root:** `0. Inbox/` — new captures land here
- **Processed archive:** `0. Inbox/processed/YYYY-MM/` — where captures go once fully worked
- **Destinations:** `1. Projects/`, `2. Areas/`, `3. Resources/` (`People/`, `Threads/`, `Research/`, and `Pipeline/` or `Vendors/` if the vault keeps them), `4. Decisions/`

---

## Execution sequence

### 1. Identify the source

- **Default:** every file at the root of `0. Inbox/` (not in `processed/`).
- **Named:** whatever the owner names — a file path, pasted text, a transcript, a URL's content.
- **Mail — optional** (`ingest mail`, `ingest that email from Sam`): if you use the `thoth` agent (or the owner's mail connector directly), have it find the messages and return their text, sender and date. **The owner names which ones are filed**; each is then a named source from step 2 on, with provenance *"email from <sender>, <date>"*. The mail agent never writes in the vault; ingest does the filing.
- **Endpoint mode — optional** (`ingest boxes` for every registered inbox and landing strip, `ingest <endpoint>` for one) → step 1b.

### 1b. Endpoint mode — the ingest protocol for file-plane inboxes

**Only if the vault uses the file-plane protocol.** The file plane is the set of folders outside the vault where binaries live; it is optional. A vault that uses it keeps two files at its root: **`registry/endpoints.md`** — every inbox and outbox, one row each, Direction `in` (has its own `processed/YYYY-MM/`) or `landing` (ends every ingest empty) — and **`registry/file-moves.md`**, the moves ledger. The scripts live in the skills repo's `scripts/` and run against the vault's `registry/`. **One protocol, whatever the service:** a new inbox is a new row in `endpoints.md`, never a new procedure here. No `registry/endpoints.md` → say the vault has no registered endpoints and stop.

**For each item at the top of the endpoint** (skip `processed/`, dotfiles, and any sub-path that is itself a registered endpoint):

1. **Match it to a workstream ID.** From the item's name, its sender, and the `id:` fields of the vault's hubs. **This matches an existing ID; it never mints one** — new workstreams go through `orion-instantiate`. **Ambiguous → ask the owner, listing the candidates** — step 4's one binding rule, applied to files. No workstream fits → the Area's own folder (`<PREFIX> <Area Name>`).
2. **Check for a duplicate.** `python3 <skills-repo>/scripts/fileplane_check.py <vault>` (it skips every path under **Fences** in `AGENTS.md` itself) lists every `DUP-INTAKE` — an intake file byte-identical to one already in a working folder. **A duplicate is not moved.** It goes on a list for the owner, and is deleted only once they approve that list — never on this skill's judgment.
3. **Move it into the workstream folder.** The default layout is `~/Documents/YYYY-MM-DD-<ID> <Workstream Name>/YYYY-MM-DD-<slug>/` — the folder date is when the workstream's first material arrived, the batch date is today; the owner can set a different root in `registry/endpoints.md`. Create the workstream folder now if this is its first material. **Always through the mover:**
   ```bash
   python3 <skills-repo>/scripts/fpmove.py "<src>" "<dest>" --reason ingest --note "<endpoint> · <ID>"
   ```
   It refuses to overwrite, refuses a file open in an editor (a lock file beside it), and appends the moves-ledger row itself. **Never `mv`, `cp` or a file manager** — a move the ledger doesn't know about leaves a pointer nothing can resolve.
4. **Write the vault record** — steps 4–7 below, unchanged: what the material says, attributed, with the new path **in backticks** (that is what lets `orion-lint` verify the pointer).
5. **The intake is now empty of that item.** For an `in` box, something the owner wants kept *as received* (a signed original, a delivery record) goes to `<box>/processed/YYYY-MM/` through the same mover with `--reason ingest`; everything else lives in its workstream folder.

⚠ **Files from others keep their original names inside the batch.** The owner's own outputs follow `Subject-vN.ext`.

### 2. Read for structure

Captures often follow an informal pattern — `## Focus`, `## Decisions`, `## Instructions`, `## Notes`, `## Content` — but not every one has all of them. **Use whatever headings are present as parsing hints, not a schema to enforce.**

### 3. Follow explicit instructions first

If the source says what to do with its content ("file this under X", "pull the testimonials into their own document", "this is old, keep it for reference", "make a person page for her"), that is not ambiguous — do it. **Don't re-derive a classification the source already gave you.**

### 4. Classify what's left

| Content | Destination |
|---|---|
| A decision was made | `4. Decisions/YYYY-MM-DD-<slug>.md`, from the decision skeleton |
| A status update on a project or area | Update that hub directly — replace state, don't stack dated sections |
| An update about a person | Their page: `Contact History` (dated line), `last_contact`, Background, Open Items |
| A new person worth knowing | `3. Resources/People/<Full Name>.md`, `tier: contact` unless the owner says to follow up |
| Reference that holds anywhere | `3. Resources/Research/` root — topic tags only, never an Area tag (or another `3. Resources/` folder if an existing pattern fits better) |
| Reference that needs one Area's frame | `2. Areas/<Area>/knowledge/` — **not** a dated file inside a project folder. `knowledge/` is the Area's permanent memory; a workstream is only the episode that produced the material |
| Something that spans two or more Areas or Projects | A thread in `3. Resources/Threads/`, or an update to an existing one |
| Finite new work | Suggest `new project:` — creation goes through `orion-instantiate` |
| **Money at a stage** — an instrument, an amount, a destination *(if the vault keeps a pipeline)* | `3. Resources/Pipeline/<who>-<vehicle>.md`. **One file per opportunity, not per person** |
| **A binary** — deck, photo, receipt, spreadsheet, PDF | **Not into the vault.** It lives outside the vault — in its workstream's file-plane folder (images under its `media/`), moved with `fpmove.py` per step 1b, if you use the file plane. The vault gets a markdown record — what it says, attributed, plus the file's path in backticks — never a copy. Narrow exception: something small and load-bearing enough to want version history on directly (a signed contract, an issued permit) |

**A binary is not reference material, even when it's the source a reference note cites.** The reference rows are for the vault's own prose distilling a source; the PDF, deck or spreadsheet itself is never what gets filed into `3. Resources/`. Binaries committed to a git-tracked vault bloat its history permanently.

**A person is not an opportunity, and an opportunity is not a person.** Someone who also has money on the table gets **both**: a person page, and an opportunity that links to it. Getting this wrong misfiles a human being as a deal, or loses a deal inside a biography.

**The reference rows are a placement call, not a guess:** apply `AGENTS.md`'s classification test — strip any single Area's context from the note; if the claim still holds, it's root `Research/`; if it needs that Area's frame, it's that Area's `knowledge/`. Root notes use topic tags from `wiki/meta/tags.md`. ⚠ **An unsourced or unverified capture stays Area-native** however domain-agnostic it reads — a source with no recorded provenance is a finding, not a reference.

**When it is genuinely unclear which row applies, ask rather than guess.** This is the one binding rule. Everything else in this skill executes directly — this is the single checkpoint, because classification, not file-writing, is where judgment lives.

### 5. Record provenance — before writing anything

**Every file this skill creates records where its content came from**: source file, sender, conversation, URL, date — whatever is actually known. If unknown, write **"source unrecorded"** — never leave it blank. This is the cheapest check in the vault, and its absence produces the worst failures in it: a document nobody can trace, whose claims get copied downstream as fact.

**Attribute, don't assert.** A claim that came from a source rather than from the owner stays attributed to that source until the owner confirms it:

- ✅ *"The vendor's quote lists delivery in six weeks."*
- ❌ *"Delivery is in six weeks."*

The attribution is the seam a later session can find. Without it, every downstream file honestly cites the one above it and the chain looks clean all the way down.

- **Never write an unconfirmed claim into a summary layer.** Hub bullets, `hot.md` and `log.md` speak in the vault's voice; a claim that reaches them unattributed has laundered itself. Summaries carry the attribution or they don't carry the claim.
- **Contradiction inside one source outranks agreement across copies.** Five files agreeing may be five copies of one wrong line.

### 6. Create and write

**Create files and edit hub and person pages directly** — no commit gate, no dry run. Ingest is generative, not pruning; the checkpoint that matters is classification (step 4), not execution.

If a name in the source matches the *Never use* column of the **Vocabulary enforcement** table in `AGENTS.md`, write the canonical form. Keep the source's spelling only when quoting it verbatim.

### 7. Cross-link

**Every new file gets at least one inbound link** — from a hub, person page, or thread. A new file with no inbound link is an orphan this skill created, and exactly what `orion-lint` exists to catch.

### 8. Archive the source — except daily notes and sweeps

Move each processed capture to `0. Inbox/processed/YYYY-MM/` (create the month folder if needed). **Never delete** — the capture is the record of what came in and when, and past captures are never rewritten, even when terminology or structure changes later.

⚠ **Never archive a file tagged `daily-note` or `weekly-sweep`.** File its answers and Notes lines, and leave it exactly where it is. **Only `orion-daily` retires either.**

**Why: archival is a function of succession, not of ingestion.** A capture is finished the instant it is written, so filing it and retiring it happen together. A daily note is not a capture — it is a working surface the owner writes into all day, and archiving it mid-day removes it while it's in use. It retires when its *replacement exists*. That also makes ingest **safe to run repeatedly against the same live note**: an answer written at 09:00 can be filed at 09:05.

#### Marking what has been filed

**For every `>` block whose answer you file, append ` ✓ filed MM-DD` to the end of that block.**

- **Skip any block already carrying `✓ filed`.** That makes repeat runs idempotent.
- **A blank question gets no marker** — there is nothing to file, and it is not a failure.
- ⚠ **`> Notes:` lines are not questions.** Every workstream section of a daily note, and every item of a weekly sweep, ends in one. **Text after `Notes:` is the owner's free annotation:** classify it with the table in step 4 — usually a narrative update to that section's hub, person or pipeline page — file it, then append ` ✓ filed MM-DD`. **An empty `> Notes:` is not a blank answer**; ignore it. In a sweep, a ticked `- [x]` with no note means *reviewed, nothing changed* — nothing to file.

⚠ **The marker answers the question the owner otherwise can't ask: which of the things I wrote down actually landed in the vault?** Without it, an answer typed into a note and an answer filed into a hub look identical. `orion-daily` reads the markers to decide what carries, and refuses to retire a note with unfiled text.

### 9. Suggest cascade

Hub and person state just changed. Tell the owner to run `cascade` next.

---

## Output

```
## Ingest — YYYY-MM-DD

Source: <capture name(s), document, or emails>

Created:
- <path> — one line

Updated:
- [[Page]] — what changed

Filed in notes: N lines marked ✓
Archived: N captures → 0. Inbox/processed/YYYY-MM/

Moved (endpoint mode): `<old>` → `<new>` · <ID> · ledger row written — or none
Duplicates held for your approval: `<intake path>` = `<existing path>` — or none

Asked / flagged: <any classification question, and the answer>

Next: run cascade.
```

---

## Rules (binding)

- **Explicit instructions in the source win** over the classification table.
- **File creation and hub/person edits happen directly** — no commit gate.
- **Classification ambiguity is the one thing that stops execution** — ask rather than guess.
- **Every created file records its provenance.** Unknown → "source unrecorded".
- **Attribute, don't assert.** An unconfirmed claim never reaches a hub bullet, `hot.md` or `log.md` unattributed.
- **Cross-link on creation** — no new file lands without an inbound link.
- **Archive, never delete.** Every processed capture stays in `0. Inbox/processed/YYYY-MM/`.
- ⚠ **Never archive a `daily-note` or `weekly-sweep`.** File its answers and Notes lines, mark them `✓ filed MM-DD`, leave the file in place. Only `orion-daily` retires either.
- **File-plane moves go through `fpmove.py`, always.** It writes the moves-ledger row; a hand move leaves a pointer nothing can resolve. **A byte-identical intake duplicate is deleted only from a list the owner has approved.**
- **Endpoint mode matches IDs; it never mints them.**
