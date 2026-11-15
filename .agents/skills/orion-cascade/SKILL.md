---
name: orion-cascade
description: "Sync an Orion vault's wiki/ navigation layer from the numbered PARA folders. Rewrites wiki/hot.md (current state: outstanding sends, workstreams, the owner's own next moves, pipeline, people due for follow-up), appends one wiki/log.md entry, rebuilds wiki/index.md when the structure changed, and reports how many log entries are waiting to be folded. Run once at the end of every session that changed something. Triggers on: cascade, run cascade, sync the wiki, update the wiki, sync wiki."
---

# orion-cascade — sync the wiki layer

Cascade reads the numbered folders (the source of truth) and syncs `wiki/` to reflect current state.

**Distinction from ingest:** `orion-ingest` brings external material *into* the numbered folders. Cascade syncs `wiki/` *with* what's already there. Separate operations.

⛔ **Skip every path listed under *Fences* in `AGENTS.md`.** Never open a file there; links into one are checked by existence only.

---

## One command, no flags — once per session

The owner says `cascade`. That is the whole interface — **no flags, no modes, nothing to remember.**

- **Always:** rewrite `wiki/hot.md`, append one entry to `wiki/log.md`.
- **When you detect the structure changed** — a hub added, removed, renamed, or its `status`/`parent`/`area` changed since the last cascade — also rebuild `wiki/index.md`. That is your call to make by looking, not the owner's to make by remembering a flag. When in doubt, rebuild it; it's cheap.

**Run once per working session, not once per milestone inside it.** Cascade is the highest-frequency operation in the vault, so its cost compounds harder than anything else. A session that ships three checkpoints on one piece of work (an Area created, then a pipeline finished, then a schema designed) gets one cascade at the end, not three. A session that pauses and resumes hours or days later, or moves to a genuinely separate piece of work, is a new session; ordinary back-and-forth on the same thread is not.

**There is no overview file.** Current state → `hot.md`, history → `log.md`, inventory → `index.md`. If you want a "status across everything" file, that is `hot.md`.

---

## Delegation (optional)

**Cascade is mechanical: glob files, parse frontmatter, compare dates, rewrite two files.** If your harness has the `orionite` and `orionite-people` agents, dispatch to them:

- **`orionite`** — everything except the People sweep: hub reads, pipeline reads, threads, the unfiled-decision scan, the writes, the log append and count.
- **`orionite-people`** — the People armed-tier sweep (step 2) only. It is narrower and carries a mandatory re-verification pass, because this is the step where names get substituted or dropped.

**Give each agent the whole job for its part — the scans as well as the writes.** Dispatching only the writes fails the ask: if the main thread runs the investigation and hands an agent a summary to type up, the expensive half already happened. **What each gets:** the vault path, this skill, and an instruction to return only its **Output** block. **What neither returns:** file contents, grep dumps, or reasoning.

⚠ **If you run these agents on a cheaper model, keep the People sweep off the smallest tier.** Small record count, high name similarity and zero tolerance for substitution is exactly where a small model reports success while wrong.

⛔ **Order and git:**
1. **Dispatch `orionite-people` first**, then `orionite` with the People block pasted into its prompt. (`orionite` can't dispatch agents itself; without the block it stops.)
2. **Neither agent commits or pushes, and the dispatch prompt never asks them to.**
3. **The main thread reads `git diff` on `hot.md` and `log.md` line by line before committing.** Every removed line needs a reason: resolved, or evicted with a pointer. A removal with no reason gets restored.
4. **Commit; push only on the owner's word.**

**What stays in the main thread, and is not optional:** reading both reports, merging them, the People spot-check (step 2), and any judgment an agent flags — a claim that needs attributing, a `⚠` worth carrying, a count that looks wrong. ⚠ **Verify any number before it reaches `log.md`.** A dispatched run can report success while shipping errors.

`orionite-people` is not cascade-specific — `orion-lint`'s people checks compute the same sweep.

`orion-ingest`, `orion-review` and `orion-daily` are **not** delegated: they classify ambiguous content, ask the owner questions, and make judgment calls.

No agents? Run every step in the main session; the procedure and the verification are the same.

---

## Vault paths

The vault is the folder the session runs in (or the one a dispatch names — if several vaults exist and the dispatch names none, stop and ask).

- **Numbered folders:** `0. Inbox/` … `4. Decisions/` · **Wiki layer:** `wiki/hot.md`, `wiki/index.md`, `wiki/log.md`, `wiki/meta/holds.md`
- **People:** `3. Resources/People/` · **Threads:** `3. Resources/Threads/` · **Pipeline:** `3. Resources/Pipeline/` (if the vault keeps one)
- **Hubs:** `*_hub.md` — ⚠ **live hubs are `<ID>_hub.md` or `<Area>_hub.md`. Glob the suffix, never the whole name.**

---

## Execution sequence

### 1. Read hubs

Glob `1. Projects/**/*_hub.md` and `2. Areas/**/*_hub.md`.

**Skip any Project with `status: paused`, `closed` or `archived`** for attention purposes — count them, don't read them further. Paused is a deliberate exclusion, not an oversight: a paused project generates no flags, no staleness, no findings. That exclusion is the entire point of the status.

**Areas carry `status: standing` and no attention status at all.** List them; never compute freshness or drift on one. A container doesn't compete for attention.

For each `open` Project: `id`, name, `next:` (**may be a YAML list — read every entry**), `deadline:`, open items, blockers.

### 1b. Read the pipeline — if the vault keeps one

Glob `3. Resources/Pipeline/*.md`. **Skip `stage: dead`** — a dead opportunity is kept so it isn't re-pitched, not so it generates flags.

For each live opportunity: `stage`, `amount`, `for`, `owner`, `next`, `confirmed`.

**Opportunity `next:` fields feed the sends block exactly like Project hubs do.** People tiers model upkeep (`relationship`) and facts (`contact`); neither models a deal. Re-tiering someone to `contact` silently takes a live deal's gate dark unless the opportunity carries it.

**Two filters, both binding:**
- **`owner:` is not always the owner of the vault.** An opportunity owned by someone else never renders as an owner-facing send.
- **`confirmed:` blank means nobody has checked.** Render it, but mark it unconfirmed — never state it as fact.

### 2. Read people — the step that needs its own verification

Glob `3. Resources/People/*.md`, **filter to `tier: relationship` only.** `tier: contact` pages carry no `cadence` and no `follow_up_by` by design and must never be flagged — a contact is not a neglected relationship.

For each, compute the **live due date**:
- `follow_up_by` after `last_contact` (or no `last_contact`) → `follow_up_by`.
- `follow_up_by` on or before `last_contact` is **spent** → `weekly`/`biweekly`/`monthly`: `last_contact` + 7/14/30 days, rendered *(from last contact)*; `organic`: **no date since contact** — its own line, never Overdue.
- No `follow_up_by` at all → **defect.** A relationship page with no date cannot flag and is invisible — the shape of a dashboard reading "all clear" over a roster of silent people.

Bucket: **Overdue** · **Due within 7 days** · **No date since contact** · **Defects**. **Never write a computed date back to the page** (`_contracts.md`, *Spent follow-ups*).

⚠ **Every rule here is mechanical, and it is still the step that breaks:** a `contact` substituted for a similarly named `relationship` person, a real overdue person dropped, a date miscomputed — each while reporting success.

**If delegated:** `orionite` takes `orionite-people`'s block and drops it into `hot.md`/`log.md` **verbatim**. It must not recompute or "sanity-check" the block against its own read of People — that reintroduces the substitution risk the split removes.

⚠ **Transcription is the same failure surface as computation.** A correct list can still be retyped wrong on its way into `hot.md` — a name silently missing. **Diff the People block in `hot.md` against the block the sweep returned, name by name, every run.**

⚠ **Main verifies the assembled result — cheap, not a redo.** After the files are written: confirm every name in `hot.md`'s Overdue/Due-soon lines is genuinely `tier: relationship` in its own file (one combined grep across `3. Resources/People/`), and that the armed count matches. **Not optional, no clean-run shorthand.** A subagent cannot perform this step and must never report on it.

### 3. Check for unfiled decisions

⛔ **Do not scan for a section named exactly `## Decisions`.** Hubs write `## Key decisions`, `## Decisions made <date>`, `## Open questions — resolved`. **A check whose selector matches nothing reports success forever** — that, not a missed bullet, is the failure to watch for.

**Match the heading by pattern, in live Projects and Areas. Two tiers, because precision matters more than volume:**

```bash
# Tier 1 — sections that say they hold decisions
grep -rn "^#\{2,3\} .*[Dd]ecision" "1. Projects" "2. Areas" --include="*_hub.md"

# Tier 2 — sections that hold settled calls under another name
grep -rn "^#\{2,3\} .*\([Rr]esolved\|[Aa]ccepted\|[Oo]wner's call\|[Oo]pen question\)" \
  "1. Projects" "2. Areas" --include="*_hub.md"
```

(Add any phrasing your own hubs use for settled calls to the Tier 2 pattern.)

**In each section found, scan bullets.** A bullet that isn't a `[[wikilink]]` into `4. Decisions/` is **unfiled**. Report: `Unfiled decision in [hub] § [heading]: [text]`.

**Tier 2 is a candidate, not a finding.** `## Accepted limitations` may be an engineering note rather than a strategic decision; the difference is judgment. Hand it to the main thread with the heading named — don't file it and don't silently drop it.

**Known false-positive shapes — not findings:**
- **A `- [ ]` checkbox list** under a decision heading is work awaiting a call, not a ledger of calls made.
- **A dated narrative section that already links its decision.**
- **A bullet stating a folder convention** (*"`4. Decisions/` — immutable; never edit past entries"*).

⚠ **A prose bullet describing a superseded decision still counts** — superseded is not filed; the ledger is immutable precisely so a reversal stays readable. ⚠ **A severed link and an unfiled decision look identical in a hub.** Before calling one unfiled, check whether the decision file exists under another path (a moved file leaves the hub's link dead).

⚠ **Report the selector's yield, not just its findings** — how many sections each tier matched. **If Tier 1 matches zero sections across the whole vault, that is a defect in the check, not a clean vault** — say so in those words rather than printing "none".

### 4. Read threads

Glob `3. Resources/Threads/*.md`: `status`, one-line state. **A thread whose `domains:` no longer name any live hub has collapsed** — flag it against the thread lifecycle (close or drop), don't just report it stale.

### 5. Read holds

Read `wiki/meta/holds.md` **before rendering any age.** Rules in step 6 and `AGENTS.md`, *Holds*.

### 6. Rewrite `wiki/hot.md`

**Rewrite, never append.** `hot.md` is state; appending to state is the defect that turns a status file into a second log. If a section is superseded, replace it — `log.md` already holds the history.

⛔ **Earlier sessions' entries carry forward word for word.** An entry leaves only when (a) it's resolved, and the resolution is named in this run's log entry, or (b) it's evicted at the cap, moved to `log.md` or `wiki/meta/open-questions.md` with a pointer left behind. **Never compress, merge or rewrite an earlier entry, never generalise one project's state to others, and never replace earlier sessions' entries with this session's news.** List every removed line in the Output under `Removed from hot.md:`.

Hard cap **80 lines.** Sections, in this order:

```markdown
## Hold                 ← ONLY when one is open in wiki/meta/holds.md. Above everything
## Outstanding sends    ← every `send` and `wait`, from live hubs AND live opportunities, with age
## Workstreams          ← "N open: WEB-1, WEB-3, OPS-2 · N paused: HOME-1" — one line, never a block each
## Now                  ← every `build`/`decide` next: — the owner's own moves. Oldest [since] first, no ages
## Pipeline             ← live opportunities by stage; unconfirmed marked (omit if the vault has no pipeline)
## People               ← "N armed", then overdue / due soon / no date since contact / defects by name
## Threads              ← open threads, one line each (omit if none)
## [session-specific]   ← what changed, warnings, corrections worth carrying
## Standing state       ← carried forward, pruned each run
```

**`## Hold`** appears only when a hold is open: two or three lines — period, reason, scope, what's held. It costs budget deliberately: without it at the top, every age below reads as an accusation. When the hold closes, the section goes; the closed entry lives in `holds.md`.

**The cap is enforced by eviction, not compression.** At 80 lines, don't shrink prose and don't raise the cap — find what no longer belongs. Blank lines that make the file readable aren't to be stripped to fit; if it only fits that way, something needs to leave.

⚠ **A `⚠` warning is the one class that doesn't clear itself.** Sends clear by sending, projects by shipping, but a warning retires only when the owner acts. Warnings arrive faster than one person clears them, so **they are what puts this file at cap.**

**The two-cycle exit:**

> A `⚠` item that has appeared in **two consecutive cascades** without resolving is not news. It moves to `wiki/meta/open-questions.md` as a forced binary, and `hot.md` keeps **one pointer line stating the consequence, not the reasoning.**

```markdown
⚠ Vendor quote unverified — don't cite its dates → open question #4
```

`hot.md` is the only file loaded every session, so the pointer is load-bearing. **Never evict a warning without leaving one.** A silently dropped warning is the failure this whole layer exists to prevent.

#### The sends block — the point of the file

Parse `next:` from each live Project hub **and each live opportunity**. Verb-first: `send` · `wait` · `build` · `decide`; `send` and `wait` name a person. **Render every `send` and `wait`** — messages nobody has sent are the single most common thing a vault loses track of.

**Ageing.** Read the `[since YYYY-MM-DD]` suffix; that is the authority. Fall back to git (`git log -1 --format=%ad --date=short -S'next:' -- <file>`) **only** when there's no suffix — git dates a commit, which may be a restructure rather than a decision. **If neither is trustworthy, render no age. A missing age is fine; a wrong age destroys trust in the whole table.** Never invent one.

⛔ **Compute every day count with `date` in a shell — never in your head, and never by adding to the number already in `hot.md`.** This covers send ages, a hold's lead number, and People overdue counts. Mental date arithmetic fails by a day and looks exactly like a correct run.

```bash
# days from SINCE to today — Linux (GNU date)
echo $(( ( $(date -d "$(date +%Y-%m-%d)" +%s) - $(date -d 2026-01-05 +%s) ) / 86400 ))
# macOS (BSD date)
echo $(( ( $(date -j -f %Y-%m-%d "$(date +%Y-%m-%d)" +%s) - $(date -j -f %Y-%m-%d 2026-01-05 +%s) ) / 86400 ))
```

**Run it once per distinct date and paste the result.** Today's date comes from `date +%Y-%m-%d`, not from the conversation or the last `hot.md` heading.

#### Then apply holds

**Coverage first: a hold covers an item only if the item's `[since]` predates the hold's start.** Scope says which *kinds* of item; this says which *instances*. An obligation created **during** a hold is not held — creating it proves the owner was working on that thing.

- **Hold has no start date** → **it cannot be applied.** Render real ages and say so in `## Hold`. Don't default to holding everything, and don't default to holding nothing.
- **Hold is open and covers the item** → render **`held`**, no number. Don't compute, don't estimate.
- **The most recent covering hold has closed** → **two clocks, render both.** The **lead** number counts from the **later of** `[since]` and that hold's end — workable urgency, how long the owner has actually had to move it. The **parenthetical** carries accountability: `[since]` and the held span. `3d (since 01-05, 11d held)`. ⚠ **`0d (since 01-05, 11d held)` on the day a hold closes is correct** — no opportunity yet, the full span still owed.
- **No hold covers the item** → unchanged: `[since]` → git → nothing.

**A falsely-silenced flag is worse than a false one**, because nothing reports silence. Never widen a hold to cover something the owner demonstrably acted on.

**Never rewrite `[since]` to account for a hold.** The hold changes what's *reported*, not what's on file; re-baselining would make "we were interrupted" indistinguishable from "this was always fresh".

**Honour the scope exactly.** A hold scoped `sends+people` covers the sends block, pipeline `next:` and `follow_up_by` — **not** `build` or `decide` items. Building can continue while sends stop; holding the build items would be false the other way.

#### `## Now` — the owner's own moves

The sends block carries everything gated on another person; **`## Now` carries everything gated on the owner.** Parse every `build` and `decide` entry from each live Project's `next:`. One line each: ID, name, the move. **Order oldest first by `[since]`; entries with no `[since]` go last. Render no ages** — the order carries the signal.

⚠ **A `send →` or `wait →` naming the owner is a mis-verbed `build`; a `build →` whose move is a message is a mis-verbed `send`.** Fixing the hub's verb is a repair — do it, then render in the right block.

#### Workstreams

**Use the ID everywhere, and never alone in prose** — `WEB-3 Pricing Page` in session notes; the `## Workstreams` line itself may list bare IDs.

| Status | Renders as |
|---|---|
| `open` | ⚠ **A count and a list of IDs on one line. Never a block per workstream** |
| `paused` | A count and IDs only |

`open` is uncapped, so a block each would blow the 80-line cap the moment it grows. **Six open workstreams is one line; twenty is still one line.** **Never age an `open` workstream** — it carries no clock by design.

**Vault voice.** Everything in `hot.md` is the vault speaking. **A claim sourced from a document rather than from the owner stays attributed, or stays out.**

**Preserve verbatim across runs unless the underlying fact changed:** standing warnings (fenced paths, places the owner said to stay out of), recorded corrections, and standing lessons.

### 7. Rebuild `wiki/index.md` — only when the structure changed

Plain markdown, one line per page, **navigation only — never prose:**

```markdown
## Areas
- [[2. Areas/Website/Website_hub|Website]] — standing · prefix WEB · 3 issued
## Projects
### Open
- [[1. Projects/Website/Pricing Page/WEB-3_hub|WEB-3 Pricing Page]] — done when: "…"
### Paused
## Threads
## People
### Relationship tier
- [[3. Resources/People/Sam Example|Sam Example]] — monthly · due 2026-02-01
### Contacts
## Decisions
- [[4. Decisions/2026-01-05-pricing-model|2026-01-05 Pricing model]] — open
## Folds
```

Only touch it when the *shape* changes — a hub added, removed, renamed or re-statused; a new person, thread or decision. **Never add narrative prose** — "prior cascade" paragraphs in an index are duplicates of `log.md`.

*(If the vault is opened in Obsidian with Dataview, the owner may replace sections with queries; they then self-maintain. Keep the headings, and check a query that renders zero rows over a non-empty folder — it's wrong, not empty.)*

### 8. Append to `wiki/log.md`

`log.md` is a **ledger**: never edit a past entry. New entry **at the top**, below the header. Every heading is classified `[build]` or `[vault]`:

```
## YYYY-MM-DD — [build] Pricing page shipped
## YYYY-MM-DD — [vault] Cascade: two workstreams opened, one person armed
```

A `[build]` entry **must** carry a `Shipped:` line naming what exists now that didn't before. **If you can't fill it, it's `[vault]`.** No judgment call. (Without the split, maintenance and delivery look identical and a maintenance-heavy workload stays invisible.)

Body:

```
- Projects: N open, N paused
- People: N overdue, N due soon — armed tier only
- [overdue people by name + date]
- [unfiled decisions]
- [notable state changes; anything removed from hot.md and why]
```

**Never state an unconfirmed claim in the vault's voice** here either — an unsourced table restated as "active investors (5)" in the log stands as fact until someone notices.

### 9. Count unfolded log entries — every run

After appending:

```bash
grep -c '^## ' wiki/log.md        # all entry headings
grep -c '\[folded\]' wiki/log.md  # fold pointers — not entries
```

**Unfolded = headings − `[folded]` pointers.** ⚠ **A `[folded]` pointer is the tombstone of many entries, not one** — counting it as one keeps the number wrong in the reassuring direction.

**Threshold 16.** Over it, `orion-fold` is due: report both numbers — `unfolded: 23 / 16 — fold overdue by 7`. **Under it, still print the count.** A check that only speaks when it's angry teaches nobody what normal looks like, and a fold trigger that lives only inside the fold skill is never pulled.

⚠ **Don't run the fold from cascade.** `orion-fold` is dry-run by default and commits only on the owner's word; cascade's job is to make the number impossible to miss.

---

## `cascade: [change]` variant

Everything above, plus propagate the named change: update hub frontmatter on a status change, re-check dependents when a blocker resolves, update a person page when contact happens.

---

## Output

```
## Cascade — YYYY-MM-DD

Sends outstanding
- <Person> — <what> (<age>)

Workstreams: N open (<IDs>) · N paused (<IDs>)

People (armed: N) — computed by the sweep, spot-checked by main
Overdue: <Name> (due YYYY-MM-DD)
Due this week: <Name> (due YYYY-MM-DD[, from last contact])
No date since contact: <Name> (organic, last contact YYYY-MM-DD)
Defects: <Name> — relationship tier, no follow_up_by

Main verification: <N> name(s) in the People lines checked against `tier:` in their own files — pass / <what didn't match>

Unfiled decisions: Tier 1 matched N sections, Tier 2 N — then findings, or "none" *with* the yield
Threads: <collapsed or notable>

Removed from hot.md: every removed line with its reason (resolved → where · evicted → pointer), or "none"

Log: unfolded N / 16 [— ⚠ fold overdue by N]
Wiki updated: hot.md · log.md [· index.md]
```

⚠ **The `Log`, `Main verification` and `Removed from hot.md` lines print every run, with no clean-run shorthand.** The first exists because silence let the log grow unchecked; the second because a merge step can drop a name even after the computation is right; the third because a rewrite can silently discard live state.

---

## Rules (binding)

- **`hot.md` and `index.md` are state — rewrite, never append. `log.md` is a ledger — new entries at the top, never edit a past one.**
- **Once per session, not once per milestone.**
- **Earlier `hot.md` entries carry forward verbatim** until resolved or evicted with a pointer; every removal is listed.
- **Skip paused/closed/archived Projects. Areas have no attention status; never compute drift on one.**
- **Only `tier: relationship` people can flag.** Spent follow-ups compute a live date; the stored one is never rewritten.
- **Sends come from hubs and the pipeline.** Skip `stage: dead`; never render a send for an opportunity the owner doesn't own.
- **Never state an unconfirmed claim in the vault's voice.** `hot.md` and `log.md` are the vault speaking; a document's claim stays attributed or stays out.
- **Never render an age you can't source, and compute every age with `date`.** Lead number: later of `[since]` and the last covering hold's end → git → nothing; when a hold moved it, append `(since MM-DD, Nd held)`. While a hold is open, covered items render `held`. `[since]` is never rewritten.
- **Verify every rendered name and count in the main thread before it's written or committed.** A delegated claim of verification is not verification.
- **Agents never commit or push. Push only on the owner's word.**
- **One command, no flags.** Whether `index.md` needs rebuilding is your judgment, never the owner's.
