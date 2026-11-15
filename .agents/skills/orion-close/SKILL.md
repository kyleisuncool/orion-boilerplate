---
name: orion-close
description: "Close a finished workstream in an Orion vault and return its deliverable to the Area that spawned it. Verifies done_when is actually met, splits the output into deliverable (→ 2. Areas/<Area>/knowledge/) and process record (→ 5. Archive/<Area>/<ID>/), updates the Area hub, releases follow-ups tied to the work, and repoints inbound links. The second half of the Area→workstream→Area loop. Not reversible. Distinct from orion-archive, which retires a whole engagement and is reversible. Triggers on: close workstream, close [ID], this workstream is done, finish workstream, ship it."
---

# orion-close — return a finished workstream to its Area

**An Area spawns a workstream; when the workstream finishes, its deliverable comes home.** The Area is the memory; the workstream is the episode. If finished output archives together with its process, the Area learns nothing and the next workstream in that domain starts cold.

```
2. Areas/<Area>/                ──spawns──▶  1. Projects/<Area>/<Name>/
  knowledge/  ◀── deliverable ──────────────────┤
                                                 └── process ──▶ 5. Archive/<Area>/<ID>/
```

## Close or archive? State the difference before running either.

| | `orion-close` | `orion-archive` |
|---|---|---|
| **Trigger** | One workstream **finished** | An engagement **ended or paused** |
| **Unit** | One workstream | An Area and its Projects, as one bundle |
| **The Area** | **Stays, gains knowledge** | Moves into the bundle |
| **Reversible** | **No** — closing asserts the work is done | **Yes**, via `resume` |
| **Deliverable** | **Migrates to `knowledge/`** | Travels with the bundle |

**Is the Area staying? → close. Is it going away? → archive.** Closing a workstream inside an Area that is about to archive is wasted motion. If there's any chance the work resumes, it's `paused`, not closed.

---

## 1. Verify `done_when:` against reality

Read the hub's `done_when:` and check it against what actually exists — not against how finished the work feels.

**When `done_when:` turns on money** — reconciled, accounted for, a total, a balance — check the record against its sources: every total stated or re-derived **with tools, never by eye**, open notes counted, unassigned rows counted. **If your harness has the `seshat` agent, dispatch it for this check, read-only.** Its return is evidence for the check, not the verdict; Orion reads it and decides. Without `seshat`, do the same check in the main session.

⚠ **Not met → stop and say which part is outstanding.** Don't close it, and never rewrite `done_when:` to match what happened. **A done-when edited at close time never tested anything** — the same failure as a `follow_up_by` that gets pushed instead of answered.

| Situation | Action |
|---|---|
| The work is done and the sentence was wrong | **The owner's call.** Record the correction and *why* on the hub, then close |
| The work stopped and won't resume | Not a close — `status: paused` with a reason, or `orion-archive` |
| Scope changed underneath it | **Not a close.** The old workstream closes as superseded; a new one opens with a new ID |

## 2. Split the output — the decision this skill exists to make

| Pile | Goes to | What it is |
|---|---|---|
| **Deliverable** | `2. Areas/<Area>/knowledge/` | What the Area now knows that it didn't: conclusions, specs, finished documents, reusable findings |
| **Process record** | `5. Archive/<Area>/<ID>/` | How it got there: session notes, superseded drafts, dead ends, the hub itself |

**One question per file:** *would a session working in this Area six months from now want to read this without knowing the workstream existed?* Yes → knowledge. No → archive.

⚠ **An Area that accumulates every session note and dead end stops being a knowledge base and becomes a second archive.** That is why the split has a default test rather than a fresh judgment call each time.

⚠ **When genuinely unclear, ask.** This is the one checkpoint in this skill that stops execution. Everything else runs.

## 3. Migrate the deliverable

- Move each deliverable file into `2. Areas/<Area>/knowledge/`.
- **Keep the filename.** Renaming at close breaks every inbound link for no gain.
- **Add a provenance line** if the file doesn't carry one: *"Produced by `<ID>` — `<Name>`, closed YYYY-MM-DD."* A file that reaches the knowledge base with no origin can't be attributed later, which is the failure the attribution rule in `AGENTS.md` exists to prevent.

## 4. Move the process record

- Create `5. Archive/<Area>/<ID>/` and move the workstream folder's remaining contents into it, **including `<ID>_hub.md`** — it keeps its name in the archive.
- Set the hub's `status: closed` and add `closed: YYYY-MM-DD`.
- **This is not a PARA-mirrored bundle** — that shape belongs to `orion-archive`. A closed workstream is one folder under its Area's name. **No tombstone** — there is nothing to restore.

### 4b. Move the file-plane folder (optional — only if the vault uses `registry/endpoints.md`)

The workstream's binaries close with it. Its folder (default layout `~/Documents/YYYY-MM-DD-<ID> <Name>/` — a default the owner can change in `registry/endpoints.md`) moves to the file plane's archive (default `~/Documents/_archive/`), same name, **through the mover**. Run it from the vault root, so it finds the vault's `registry/` (or set `$ORION_REGISTRY`):

```bash
python3 <skills-repo>/scripts/fpmove.py "~/Documents/YYYY-MM-DD-<ID> <Name>" "~/Documents/_archive/YYYY-MM-DD-<ID> <Name>" --reason close --note "<ID> closed"
```

- **A deliverable binary the Area keeps using** (a finished deck, a signed contract) first moves to the Area's own folder, `--reason close` — the same deliverable/process split as step 2, applied to files.
- **No folder** (the workstream produced no binaries) → nothing to move; say so in the report.
- **Then repoint:** `python3 <skills-repo>/scripts/repoint.py <vault> --apply` (one `--fence` per path under Fences in `AGENTS.md`). It updates the path everywhere, the archived hub included — path only, never prose.
- **Never move a file-plane folder by hand.** The mover writes the row in `registry/file-moves.md`.

## 5. Update the Area hub

- Mark the workstream **closed** under `## Workstreams`, keeping its ID and one line on what it produced.
- **Link the migrated deliverable** from the Area hub or from `knowledge/_index.md`.
- ⚠ **Never decrement `workstream_counter:`.** IDs are never reused; `WEB-3` means one thing forever, including after it closes.

### 5b. Release the follow-ups it was holding

**List every armed person whose follow-up exists for this workstream — and change nothing on their page.** Candidates: `tier: relationship` pages that link the hub or name the ID, and anyone the hub's `next:` names. Keep only those whose follow-up is *for* this work, read from their page.

- **One line each** — name, `follow_up_by`, what it was for — in the close report, and as a `Released:` line in the step 7 log entry. **The next weekly sweep reads that line** and lists them.
- ⚠ **Never change `tier:`, `cadence:` or `follow_up_by:` here.** Whether the relationship outlives the work is the owner's call. A follow-up left firing on closed work is a false flag; one silently cleared is a dropped relationship.

## 6. Repoint inbound links

Scan the vault for links into the workstream folder and repoint them: deliverables to their new `knowledge/` path, everything else to the archive path. **Skip every path under Fences in `AGENTS.md`**; links into a fence are checked for existence only.

**Method — not optional:**

1. **Scan** every `.md` for `[[…]]` targets pointing into the old folder, full-path and bare-name forms, ignoring code blocks — with a resolver whose rules you can state.
2. **Resolve each hit against the real tree.** A grep hit is a hypothesis.
3. **Edit only the link target, never the prose.** Preserve display aliases exactly: `[[new/path/File|Original Text]]`. **Ledgers are included** — `4. Decisions/`, `wiki/log.md`, `wiki/folds/`, `0. Inbox/processed/` — pointer only, never a word of the entry.
4. **Rescan from scratch and report that scan's number**, not a tally of your edits.

⚠ **An alias does not rescue a path form.** `aliases:` on a page keeps `[[Name]]` resolving; it does nothing for `[[full/path/Name]]`. A repoint that relies on an alias can report complete while a full-path link stays dead.

## 7. Log it

Append one `wiki/log.md` entry. **`[build]` if the deliverable is a shipped thing** — and then it carries a `Shipped:` line naming what exists now that didn't. Otherwise `[vault]`. If you can't fill `Shipped:`, it's `[vault]`. Include `Released:` if any.

## 8. Suggest cascade

Structure changed. `orion-cascade` next. **This skill does not cascade.**

---

## Output

```
## Close — <ID> · <Name>

done_when: "<sentence>" — ✅ met / ⚠ met with correction (why)
Money check: <seshat | main session> — <what was re-derived> · or n/a

Deliverable → 2. Areas/<Area>/knowledge/
- <file> — what the Area now knows
Process → 5. Archive/<Area>/<ID>/ — N files incl. hub
File plane: <old folder> → <archive folder> · ledger row written — or no folder / not used

Area hub: <what changed>
Links repointed: N — rescan shows N dead (was N)
Released: <Name — follow_up_by, what it was for> · or none
Flagged: <anything genuinely ambiguous, and what was decided>

Next: run cascade.
```

## Rules

- **Verify `done_when:` against reality before anything moves.** Never rewrite it to fit.
- **Money-based done-whens are re-derived with tools, never by eye** — by `seshat` if available. Its return is evidence; Orion decides.
- **Split deliverable from process.** Ask only when genuinely unclear — the one checkpoint that stops execution.
- **Every migrated file carries its origin.** Keep its filename.
- **Never decrement the counter. Never reuse an ID.**
- **Release follow-ups; never change them.** The owner decides whether a relationship outlives the work.
- **File-plane folders move through `fpmove.py`, never by hand** — when the vault uses the file plane.
- **Closing isn't reversible.** If it might resume, pause it.
- **Only link targets change, ledgers included. Rescan and report the rescan.**
- **`area: none` workstreams archive whole** — there is no knowledge base to receive a deliverable. A consequence of the design, not a bug.
- **This skill does not cascade.** Run `orion-cascade` after.
