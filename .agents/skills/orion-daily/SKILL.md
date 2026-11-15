---
name: orion-daily
description: "Close today's daily note in an Orion vault's 0. Inbox/ and write tomorrow's — or write a weekly sweep. The daily note: Focus, a short 'Since the last note', one section per workstream that owes something (where it stands · yours · waiting on · a Notes line), Loose, the open-questions manifest, People with what each person is tied to, Standing. Carries every unanswered question with a plain-language count ('asked 3 times since Jan 5') and forces a do-it-or-drop-it choice at the third ask. Hard cap 150 lines; never reproduces hot.md's tables. The weekly sweep lists every Area, workstream, thread and person (and pipeline item and vendor, where the vault keeps them) with one line each and room to write. Does not ingest — run orion-ingest first, orion-cascade after. During an open hold it never auto-generates, renders no ages, and freezes ask counts. Triggers on: daily note, tomorrow's note, close the day, generate tomorrow's note, orion-daily, weekly sweep, sweep note."
---

# orion-daily — the daily note and the weekly sweep

`hot.md` says what's true. **The daily note is the one surface that asks the owner questions: what only they can answer, and what is quietly drifting.** It is also where the vault surfaces things the owner would not see unless prompted to look.

**Two notes, one skill.**

| | Daily note | Weekly sweep |
|---|---|---|
| **Job** | What's owed today and what's drifting | Everything tracked, one line each, room to write under all of it |
| **Length** | 150 lines, hard | No cap — one line per item |
| **When** | Close of day, or on resuming work | Weekly, or when the owner says `weekly sweep` |
| **File** | `0. Inbox/YYYY-MM-DD daily.md` | `0. Inbox/YYYY-MM-DD weekly-sweep.md` |
| **Tag** | `daily-note` | `weekly-sweep` |
| **Skeleton** | `6. Templates/daily-note.md` | `6. Templates/weekly-sweep.md` |

**Why two.** The full view — every Area, workstream and person, with space to annotate — is genuinely useful, but bloating the daily note to hold it destroys the daily note. So the full view is its own note, on its own cadence.

**This skill does not ingest.** If a note has answers or notes in it, run `orion-ingest` first — that files them. This skill reads what ingest left behind and builds the next note.

⛔ **Fenced paths** (`AGENTS.md`, *Fences*) **are named, never read.** Name a fenced Area; never summarise its contents.

---

## When this runs — and why it is not on a clock

**The daily note is a working surface, not a capture.** The owner writes into it across the whole day. Filing and retiring therefore have different correct moments, and conflating them archives a note while it is still in use.

| Event | What runs |
|---|---|
| **An answer or note lands, any time of day** | `orion-ingest` — files it, marks it `✓ filed MM-DD`, **leaves the note in place.** Safe to repeat |
| **Close of day** — the note has stopped being useful | `orion-ingest`, then **`orion-daily`**, then `orion-cascade`. One motion |
| **Work resumes after a hold or a gap** | The same three, in the same order. **However many days it has been** |
| **The owner says `weekly sweep`** | `orion-daily` in sweep mode → *Weekly sweep* below |
| **A hold is open** | **Nothing auto-generates.** See below |

⚠ **Never generate a new note while the current one still has unfiled text.** Check every `>` line: a question with text after it, or a `> Notes:` with text after it, and no `✓ filed` marker. If any exist, **stop and say so** — running ingest first is one step, and generating a successor around unfiled text loses it.

### Holds

⚠ **During an open hold** (`wiki/meta/holds.md`), **this skill does not generate a note on its own.** A note produced every morning of a hold is the manufactured urgency holds exist to prevent.

**Run manually during a hold and it still works**, with three changes:

1. **No ages render anywhere**, per the hold rule in `AGENTS.md`.
2. ⚠ **Ask counts do not increment.** The count is *workable asks*, not calendar days. A long hold would otherwise push every carried item past three asks and manufacture a wall of forced choices out of a period when the owner was not working.
3. **Say at the top** that a hold is open and nothing here is late.

**On resumption, one note spans the whole gap.** It says how long the hold ran, carries everything forward with its pre-hold counts intact, and renders ages from the hold's end.

---

## Paths and frontmatter

- **Daily notes:** `0. Inbox/YYYY-MM-DD daily.md` · **sweeps:** `0. Inbox/YYYY-MM-DD weekly-sweep.md` · **retired notes:** `0. Inbox/processed/YYYY-MM/`
- **Reads:** every live `*_hub.md` · `3. Resources/People/` · `3. Resources/Threads/` · `3. Resources/Pipeline/` and `3. Resources/Vendors/` *if the vault keeps them* · `4. Decisions/` · `wiki/meta/open-questions.md` · `wiki/meta/holds.md` · `wiki/hot.md` · `wiki/log.md` (for *Since the last note*)
- **Frontmatter:** `date:` · `tags: [inbox, daily-note]` (or `[inbox, weekly-sweep]`). First line after it: `RE: <Weekday> <Month D YYYY> — [[<prior note>]]`.

⚠ **If the owner keeps their own daily-capture template** (for an editor's daily-notes feature, say), **it is a different file — never write this skeleton over it.** A capture born from the wrong template carries the `daily-note` tag, and ingest will then refuse to archive an ordinary capture as though it were a daily note.

---

## Plain language — the rule behind every format choice

**A label the owner has to decode is a defect in the label** (`AGENTS.md`, *Naming conventions*). So:

| Instead of | Write |
|---|---|
| `×4 since 01-05` | `asked 4 times since Jan 5` |
| `19d` | `19 days` |
| `follow_up_by 2026-01-11` | `34 days overdue (Jan 11)` |
| a spent `follow_up_by` (on or before `last_contact`) | `Feb 17 (from last contact)` · or `no date since contact` for `organic` |
| `done_when` in prose | `done-when` — the field name only inside backticks, when it matters |

**Machine markers stay exactly as they are:** `✓ filed MM-DD` (ingest writes and reads it) and IDs.

---

## Daily note

### 1. Read the week

**The last 7 days of daily notes**, current one first, plus the most recent weekly sweep. Older notes are context for *how long* something has been carried — not content to restate.

### 2. Extract every `>` line from the current note

| State | Meaning | Action |
|---|---|---|
| **Question answered and `✓ filed`** | Text after the question, marker present | Ingest filed it. **Don't carry** |
| **Notes line with text and `✓ filed`** | `> Notes: …`, marker present | Filed. **Nothing to carry** |
| **Text after a question or `Notes:`, no marker** | Ingest has not run | ⛔ **Stop.** Don't generate a note |
| **Blank question** | Question with nothing after it | **Carry it.** Add one to its count |
| **Deferred** | Answered "not now", "upcoming", or a date | **Carry with the date given.** Not a blank |
| **Empty `> Notes:`** | Nothing written | **Ignore.** Never carried, never counted |

⚠ **A blank is data, not a failure, and never gets a nag tone.** The owner chose not to answer, or the day didn't allow it.

### 3. Count every carry-over — this is the drift metric

**Every carried item says how many notes have asked it and since when:** `asked 3 times since Jan 5`.

An item carried once is a task that didn't fit the day. An item carried four times **is not a task** — it is a decision the owner hasn't made, or something they don't actually want to do.

⚠ **Three asks promotes it.** At the third ask an item stops being carried as a task and is re-rendered as a **forced choice: do it, or drop it.** No third option; "carry it again" is not one. **A thing that survives three asks without action is a decision nobody has made.**

### 4. Gather state

- **Sends and waits** — `next:` on live Project hubs (and `3. Resources/Pipeline/`, if the vault keeps one). Same ageing and hold rules as `hot.md`. ⚠ **`next:` may be a YAML list — read every entry.**
- **Workstreams** — ⚠ **an `open` workstream gets a section only when something is owed on it today, the owner acted on it, or something external moved it.** Listing every open workstream daily is the nag list `open` exists to prevent. The weekly sweep is where every workstream appears.
- **People** — relationship tier ("armed": the only tier that can flag): overdue, due today, due in the next seven days — **and for each, what they are tied to**: the workstream, send, wait or pipeline item their follow-up exists for. **Read it from their page and the hubs that name them; never infer it.**
- **Open decisions** — `4. Decisions/` where `status: open`.
- **Open questions** — `wiki/meta/open-questions.md`, the full register.
- **Since the last note** — `wiki/log.md` entries dated after the previous note, plus anything ingest filed from it.
- ⚠ **Holds** — `wiki/meta/holds.md`. **If a hold is open: render no ages at all**, and say so at the top.
- **Calendar and mail — optional.** If you use the `thoth` agent (or the owner's mail and calendar connector directly), ask for: tomorrow's events, clashes, and mail that needs the owner — a question, decision, deadline or reply owed — with sender and age. **Read-only: no drafts, no RSVPs.** **Events and mail go inside the workstream they belong to**, under `## Loose` if none; a busy day ahead belongs in Focus. Noise is never listed. If the dispatch fails, say so in one line and write the note without it.

### 5. Surface something — the part most worth reading

**One to three things dug out of the vault that sit on no tracked list** — not an open item, not in `hot.md`, not in `open-questions.md`. Things like: two separate blocked items that are actually one conversation · a person best placed to answer a question nobody has asked them · a claim asserted somewhere and never verified · a date that just became load-bearing somewhere else · a follow-up flag pointing at work that has closed.

**A surfaced finding lives inside the workstream it concerns**, or under `## Loose` if it spans several. ⚠ **If nothing qualifies, don't manufacture one.** Padding teaches the owner to skim the one part worth reading.

### 6. Write the note

**The note is organised by workstream, not by category.** A `##` heading is a unit of work the owner opens, finishes, and collapses — **a whole task with nothing about it living anywhere else.** ⚠ Category headings (*Carried · Surfaced · Deadlines*) scatter each workstream across several sections and collapse the checkbox count; don't use them.

**Section order:**

1. **`## Focus`** — what today is about. **Three lines, hard.** No lists.
2. **`## Since the last note`** — **up to five bullets** on what changed between notes: closes, moves, answers filed, anything the owner would otherwise have to reconstruct. **Omit when nothing changed**; after a gap or a big session, this is the orientation.
3. **One `##` per workstream that owes something today** — shape below. The owner's own work first, then work waiting on other people, then work with no clock.
4. **`## Loose`** — real items belonging to no single workstream, one `###` each. **Omit when empty; never pad it.**
5. **`## Open questions — N live`** — the full manifest. Fixed shape. Every note.
6. **`## People`** — the readout with context. Fixed shape. Every note.
7. **`## Standing`** — holds, dropped items, structural facts, and the offer of a weekly sweep when one is due. **Three lines maximum.**

⚠ **Sections 5 and 6 never vary in shape**, and never drop out.

### The workstream section — same shape, every time

```markdown
## WEB-3 · Pricing Page — revised quote owed, and the launch-date call

**Where it stands:** one or two plain sentences — what's true now, not its history. → [[<hub path>|hub]]

**Yours:**
- [ ] Send Sam Example the revised quote — 6 days, asked twice since Jan 5
- [ ] **Set the launch date, or drop it as the done-when gate** — asked 3 times since Jan 2

**Waiting on:** Alex Rivera — copy review, 3 days · or `nobody`

A surfaced finding, if this workstream has one, in plain prose.

> **Set the date, or drop it as the gate —**

> Notes:
```

- **Heading: `## <ID> · <Name> — <what is actually owed>`.** All three. The ID never travels alone, and **the clause after the dash is what makes the heading a task rather than a label.**
- **`Where it stands`** is always present and always short. **It is the line that lets the owner act without opening the hub.** The hub link sits at its end.
- **`Yours`** holds every checkbox. ⚠ **Checkboxes are the interface, and the count is the test** — a note with three is a report; a note with a dozen is a working surface.
- **`Waiting on`** is always present. `nobody` is an answer. **A person blocking the work is named here**, not saved for `## People`.
- **At most one question block**, and only if it passes the three tests below.
- ⚠ **Every workstream section and every `## Loose` subsection ends with `> Notes:`** — room to write under anything. **It asks nothing**, so it is exempt from the three tests; ingest files whatever the owner writes there to that section's hub and marks it filed. **Open questions, People and Standing get no Notes line.**
- ⚠ **`practice` workstreams** (if the vault uses that status) **get a section on the same terms and never an age.**

### `## Open questions — N live` — the manifest

**Every live question, numbered, in `open-questions.md` order, with a `- [ ]` box only where the owner can close it.** Closed ones collapse to one line (`1–8, 11. Closed.`). **Parked questions are listed and never re-argued** — one line, the word *parked*, and stop.

```markdown
## Open questions — 1 live

- [ ] 9. **Is the vendor shortlist still the right three?** — one clause of current context
- 1–8, 10–11. Closed.
```

### `## People` — the readout, with what each person is tied to

A bare list of dates makes the owner look up why each person matters. So every line carries its reason.

```markdown
## People

**10 armed · 2 overdue · 0 defects · 49 pages**

**Overdue**
- Sam Example — 31 days (Jan 14) — tied to WEB-3 Pricing Page, which closed Feb 13
- Alex Rivera — 2 days (Feb 12) — copy review; waiting 6 days on a reply

**Due in the next 7 days**
- Jordan Lee — Feb 20 — HOME-1 Kitchen Refit; the quote window closes the same day
```

- **The counts line first.** Then **Overdue**, oldest first; then **Due today** if any; then **Due in the next 7 days**.
- **Every name gets what it is tied to**, read from the pages — never inferred.
- ⚠ **Age the live due date, not a spent one.** A `follow_up_by` on or before `last_contact` is spent: cadenced pages render `last_contact` + the interval, *(from last contact)*; `organic` renders **no date since contact**, never overdue → `6. Templates/_contracts.md`, *Spent follow-ups*. **A date the vault can compute is never a question for the owner.**
- ⚠ **Say plainly when a follow-up points at work that has closed, been archived, or that the owner removed the person from.** That is the most useful thing this section can say. If several flags do, one sentence — sorting them out is a people session's job, not a question here.
- **Never omitted.** *"Nobody is due"* is a real answer.

### Where a finding goes when it has no workstream

**Into `## Loose`, and only if it is genuinely homeless.** ⚠ **`## Loose` is not a second Surfaced section.** If it is longer than the workstream sections above it, the sorting is wrong.

### The three tests for a question block

**Every question the owner should answer gets a block** — that is the input channel ingest reads. ⚠ **That does not mean every section needs a question.** A finding is allowed to be just a finding. If the next move is yours, take it.

| All three must pass | |
|---|---|
| **Is it the owner's to decide?** | If the session can act, act. |
| **Does anything change based on the answer?** | If both answers lead to the same next action, there is no question. |
| **Is the premise still live?** | ⚠ **A question inherited from someone the owner has dropped dies with the engagement.** |

**The failure these prevent:** finding something real, treating "produce a question block" as the obligatory next step, and manufacturing a decision to hang on it — usually **a work item of the vault's own, dressed as a question for the owner.**

**The tell: a question block with no question in it — a bare `> **—**`.** If you cannot write the question, there isn't one. Delete the block, keep the finding. **A `> Notes:` line is not a question block and is never subject to this.**

### 7. Format — headings are the interface

**The owner reads the note in a markdown editor and collapses it.** Every section and subsection gets a real `##` / `###` heading.

| Use | For |
|---|---|
| **Bold** | The decision point in an item, and the three labels — `Where it stands` · `Yours` · `Waiting on` |
| ⚠ / ⛔ | **At most two or three in the whole note** |
| Plain prose | Everything else |

⚠ **Bolding everything is the same as bolding nothing.** A note with emphasis on most sentences reads as uniformly urgent, which is indistinguishable from uniformly ignorable.

### 8. Hard cap — 150 lines

**An unbounded state file becomes a log, and a log nobody finishes reading protects nothing.**

**Cut first, in order:** context the owner already knows · prose around a question that the question states by itself · `## Since the last note` down to three bullets · surfaced findings beyond the strongest two.

⚠ **Don't reproduce `hot.md`'s tables** — the sends table, the pipeline list, the workstream count. **Naming a send inside its own workstream's `Waiting on` or `Yours` line is context for that job, not restatement.**

### 9. Retire the old note — this skill is the only thing that may

Move the closed note to `0. Inbox/processed/YYYY-MM/`, **and only once the successor file exists on disk.** ⚠ `orion-ingest` never archives a daily note or a sweep. **A note is retired because it has been replaced, never because it has been read.**

**Refuse to retire when:** any question or Notes line has text but no `✓ filed` marker · the successor was not written · a hold is open and no successor was generated. **In each case leave the note in `0. Inbox/` and say which condition tripped.**

---

## Weekly sweep

**Triggered by `weekly sweep` or `sweep note`**, or offered in the daily note's `## Standing` when seven days have passed since the last one. **Never auto-generated.**

**Optional counsel and calendar.** If you use the `sia` agent, ask it what matters this week: up to three items, ranked, each with its reason and source. They head `## Since the last sweep` as `This week:` lines, attributed `[sia]` — counsel, not fact; the owner's ticks and Notes lines decide. If you use the `thoth` agent, ask it for the week's calendar too, as in daily step 4.

### What it covers — everything, one line each

```markdown
## How to use this
Tick a box when you've looked at it. Write under anything that changed — a Notes line is enough. Ingest files it.

## Since the last sweep
Up to five bullets.

## Areas
### Website — the public site and everything shipped on it → [[hub]]
- [ ] **WEB-3 · Pricing Page** — open · one line: where it stands
> Notes:
- [ ] **WEB-4 · Blog Migration** — paused · one line
> Notes:

## Pipeline          (only if the vault keeps one)
- [ ] **Sam Example — consulting retainer** — warm · amount · owner · waiting 8 days on a signature
> Notes:

## Threads
- [ ] **hiring-plan** — open · one line
> Notes:

## People
### Armed — 10
- [ ] **Alex Rivera** — 34 days overdue · WEB-3: copy review
### Released — follow-ups whose work closed
- [ ] **Jordan Lee** — Jan 20 · was for HOME-1 Kitchen Refit, closed Feb 2
> Notes:
### Contacts — Website
- [ ] **Sam Example** — freelance designer
> Notes:

## Vendors           (only if the vault keeps them)
None filed. / one line each

## Open questions — N live
Same manifest as the daily note.
```

- **Every live Area**, each with **every workstream** under it — `open`, `paused` (and `practice`, if used) alike, status named. Fenced Areas are named with no contents.
- **Every thread.** Where the vault keeps them: **every live pipeline item**, whoever owns it, and **every vendor.**
- **Every person page**: armed tier individually, with what they are tied to; contacts grouped by the Area they are tied to, one line each (`Unplaced` for people tied to nothing live).
- **`### Released — follow-ups whose work closed`** under People: every armed person named on a `Released:` line in `wiki/log.md` since the last sweep (written by `orion-close` and `orion-archive`), plus any armed person whose follow-up points only at closed or archived work. **Listed there instead of under Armed**, with what the follow-up was for and when that work ended. **Tier and date stay untouched** — keep, re-peg or re-tier is the owner's call, written on the Notes line.
- **A Notes line under every workstream, pipeline item and thread**, and one per contact group. **No question blocks** unless something genuinely passes the three tests.
- **A checkbox means "reviewed"**, not a task. A ticked box with no note means nothing changed.
- **No cap.** One line per item is the discipline instead.
- **Ages, spent follow-ups and hold rules are the same as the daily note's.**

### Retiring a sweep

**A sweep is a working surface for however long the review takes.** It retires to `0. Inbox/processed/YYYY-MM/` **when the next sweep is generated, or when the owner says it is done** — and in both cases **only once every Notes line with text carries `✓ filed`.** Ingest never archives it.

---

## Rules (binding)

- **Plain language.** `asked 3 times since Jan 5`, `19 days`, `34 days overdue (Jan 11)`. Only `✓ filed` and IDs stay machine-shaped.
- **Blank is data.** Carry it, count it, never nag.
- **Three asks forces a choice — do it or drop it.** "Carry again" is not an option.
- **Every workstream section: `Where it stands` · `Yours` · `Waiting on` · `> Notes:`.** Same shape, every time.
- **`## Since the last note`: up to five bullets**, omitted when nothing changed.
- **People lines say what each person is tied to**, and say plainly when that work has closed.
- **Don't reproduce `hot.md`'s tables.** A send inside its own workstream is context.
- **An open hold suppresses every age**, freezes ask counts, and the note says so at the top.
- **Surfaced findings are real or absent.** Never padded.
- **150 lines, hard**, for the daily note. The weekly sweep has no cap and one line per item.
- **Every section and subsection gets a heading.** Emphasis is scarce: at most two or three ⚠ / ⛔.
- **This skill does not ingest and does not cascade.** Run `orion-ingest` before, `orion-cascade` after.
- **Only this skill retires a daily note or a sweep**, and only after its successor exists — or, for a sweep, the owner says it's done.
- ⚠ **Never generate a successor around unfiled text.** A question or Notes line with text and no `✓ filed` means ingest has not run — stop.
- ⛔ **Fenced paths are named, never read.**
