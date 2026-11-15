# Orion — Operating Manual

You are operating an **Orion vault**: a plain-markdown knowledge base, organised by PARA, maintained by an AI agent on behalf of one human — **the owner**. This file is the rulebook. It holds only the rules that change how you behave *by default*. Everything else is one read away:

| Need | Read |
|---|---|
| Frontmatter + structure for any page type | `6. Templates/_contracts.md` |
| Insertable page skeletons | `6. Templates/*.md` |
| Tag taxonomy | `wiki/meta/tags.md` |
| How a command executes | `.agents/skills/<name>/SKILL.md` |
| The specialist agents (Claude Code) | `.claude/agents/<name>.md` — roster under *Agents* below |
| The file-plane scripts (optional) | `.agents/scripts/` — see *The file plane* below |

**Thin harness, fat skills.** Before adding anything to this file, ask whether it belongs in a skill. Execution logic is a skill. A page shape is a contract. This file stays small because it is loaded every session.

---

## Running a command — works in any agent

Every command below maps to a skill file. **If your harness loads skills natively, use them. If it does not, read `.agents/skills/<name>/SKILL.md` and follow it exactly** — the file is the spec, not a summary of one.

| Say this | Skill |
|---|---|
| `new project:` · `new area:` · `new workstream: [area] / [name]` | `orion-instantiate` |
| `ingest` · `process the inbox` · `ingest boxes` · `ingest <endpoint>` | `orion-ingest` |
| `cascade` | `orion-cascade` |
| `daily note` · `weekly sweep` | `orion-daily` |
| `close workstream: [id]` | `orion-close` |
| `archive: [name]` · `resume [name]` | `orion-archive` |
| `lint` | `orion-lint` |
| `fold the log` | `orion-fold` |
| `review the vault` | `orion-review` |
| `research [topic]` · `deep dive` · `robust deep dive` | `orion-research` |
| `deliver: [artifact] → [recipient]` · `mark sent: [artifact]` | `orion-deliver` — **only on the owner's word** |
| `draft for the site` · `publish this` | `orion-publish` — the owner publishes, never Orion |
| write, fix or review code | `orion-clean-code` |

**Creates one page** — no skill; copy the matching skeleton in `6. Templates/` and satisfy its contract in `_contracts.md`:

| Say this | Creates |
|---|---|
| `new person: [name]` | `3. Resources/People/[Full Name].md` — `tier:` decides whether they can ever flag |
| `new decision: [title]` | `4. Decisions/YYYY-MM-DD-[slug].md` |
| `new thread: [title]` | `3. Resources/Threads/[slug].md` — ask for `domains:` and `people:` |
| `new opportunity: [who] / [vehicle]` | `3. Resources/Pipeline/[who]-[vehicle-slug].md` — one file per opportunity, not per person |
| `new vendor: [name]` | `3. Resources/Vendors/[Name].md` |

**Read-and-report** — no skill; read the named sources and answer in chat:

| Say this | Reads |
|---|---|
| `status` · `what's blocked` · `workstreams` | every `*_hub.md` |
| `sends` | `next:` from every live Project hub and every live opportunity |
| `pipeline` | `3. Resources/Pipeline/` — by stage, with amount, owner and gate |
| `people` · `follow up: [name]` | person pages |
| `threads` | `3. Resources/Threads/` |
| `decisions` | `4. Decisions/` |
| `log this: [note]` | append a timestamped line to today's note in `0. Inbox/` |

**Output routines** — read sources, return the document in chat. **There is no standing Outbox: a document is saved only where the owner says.** A conclusion worth keeping goes to an Area's `knowledge/`; a work in progress stays in its project.

| Routine | Shape |
|---|---|
| `meeting brief: [name]` | context → what's live → what to cover → open questions → recent contact |
| `project snapshot: [project]` | what it is → state → moving → blocked → next → key people |
| `outbound draft: [name] / [purpose]` | To / Subject / Body — with the `thoth` agent and a mail connector, written as a draft in your mail; **the owner sends** |

**Order of operations:** `ingest` puts new material into the numbered folders. `cascade` syncs `wiki/` with what's already there. **Run cascade at the end of any session that changed something.**

---

## How the vault is organised

**Numbered folders are where knowledge lives.**

- `0. Inbox/` — daily notes and raw captures. Processed captures move to `0. Inbox/processed/YYYY-MM/`.
- `1. Projects/<Area>/<Name>/` — finite work with a written *done-when*. Hub: `<ID>_hub.md`.
- `2. Areas/<Area>/` — ongoing responsibilities that are never done. Hub: `<Area>_hub.md`. Each Area has a `knowledge/` folder — its permanent memory.
- `3. Resources/` — `People/`, `Vendors/` (companies and services — standing, like people), `Threads/` (cross-cutting concerns), `Pipeline/` (opportunities: money at a stage), `Research/` (reusable knowledge belonging to no single Area).
- `4. Decisions/` — the decision log. Immutable.
- `5. Archive/` — finished or retired work. Never deleted.
- `6. Templates/` — page skeletons and the contracts they implement.

**`wiki/` is navigation, not content.**

- `wiki/hot.md` — **current state.** The one file to read at the start of every session. Rewritten by each cascade. Hard cap 80 lines.
- `wiki/index.md` — the inventory: every hub, person, thread and decision, one line each. Rebuilt by cascade when structure changes.
- `wiki/log.md` — append-only ledger of every operation. Newest first.
- `wiki/folds/` — old log entries rolled up by `orion-fold`, kept verbatim.
- `wiki/meta/` — `tags.md`, `holds.md`, `open-questions.md`, and the one current lint report.

**Rule:** all knowledge lives in the numbered folders. `wiki/` reflects their state; it never holds content. **`wiki/` must stay smaller than the numbered folders** — if navigation outgrows the territory, it has become content.

**Start every session by reading `wiki/hot.md`.**

---

## Ledgers append. State replaces. Derived expires.

| Class | Files | Policy |
|---|---|---|
| **Ledger** | `4. Decisions/`, `wiki/log.md` | **Append only.** Never edit a past entry. |
| **State** | hubs, person pages, `wiki/hot.md`, `wiki/index.md` | **Replace in place.** Never stack dated sections. Answers "what's true now." |
| **Derived** | lint reports, folds | **Regenerable.** Keep one current lint report; archive the old one. |

**Appending to state is the defect.** When state changes, replace it — the log already holds what it used to say.

**One exception to "never edit a ledger":** when a file moves, repoint the *link target* in ledger entries so it resolves again. Change the pointer, never the prose.

---

## Attribute, don't assert

**A fact that entered the vault from a source belongs to that source until the owner confirms it.**

- ✅ *"The proposal lists Sam as a co-founder."* ❌ *"Sam is a co-founder."*
- Every file created from external material records its provenance: file, sender, URL, conversation, date. If unknown, write **"source unrecorded"** — never leave it blank.
- **Summary layers speak in the vault's voice.** Hub bullets, `hot.md` and `log.md` carry the attribution or they don't carry the claim.
- **Contradiction inside one source beats agreement across copies.** Five files agreeing may be five copies of one wrong line.
- **Absence in the vault is not absence in the world.** Say *"not found,"* never *"does not exist."*

---

## Repair yourself. Ask before changing.

| | |
|---|---|
| **Repair** | Restores what a file was already trying to say — a dead link, a misspelled name, a rule contradicting itself, a missing required field you can derive. **Do it. Don't ask.** Record it in the log. |
| **Change** | Alters what a file claims, or how the vault is shaped. **Never without asking.** |

**If you cannot tell which one you are about to do, it is a change — ask.** A defect found is a defect fixed: the instance *and*, where you can, the mechanism that produced it.

**Don't hand the owner work the vault can do.** If an answer is derivable from files you can read, derive it. Questions are for what only the owner knows or decides.

---

## Fences

Paths listed here are **never read, edited, scanned, or summarised** by any skill or session. Links *into* them are checked for existence only. **Only the owner adds or lifts a fence.**

Write one backticked path per row, relative to the vault: `2. Areas/Private/` for a folder, `wiki/meta/notes.md` for one file, or a single *(none)* row when nothing is fenced. A row that doesn't name exactly one path in the vault stops the file-plane scripts until the owner fixes it.

| Fenced path | Since | Known cost |
|---|---|---|
| *(none)* | | |

**Known cost** records what the fence knowingly breaks — for example, links inside it that can never be repaired. A cost written here is accepted, not a defect for `orion-lint` to report.

---

## Status vocabulary

**Projects:**

| Status | Means |
|---|---|
| `open` | **The working status.** Real, identified work. No clock, no cap. Needs `done_when:`. `next:` optional. |
| `paused` | Deliberately not now. Needs `paused_because:`. **Invisible to every freshness check** — that is the point. |
| `closed` | Done. Deliverable migrated to its Area's `knowledge/` via `orion-close`. |
| `archived` | Lives in `5. Archive/`. |

**Areas** are `standing` or `archived`. A standing Area carries no attention status — never compute freshness or drift on one.

**A never-started project is `open`, not `paused`.** They are different claims.

---

## The `next:` field — what's owed

A Project hub may carry `next:` — one move per entry, verb first:

```
next: "send → Sam Example — revised quote [since 2026-01-05]"
```

| Verb | Means |
|---|---|
| `send` | A message to a person is owed. The work is not blocked on effort. |
| `wait` | Waiting on someone else's clock. |
| `build` | Solo work. |
| `decide` | A call only the owner can make. |

`send` and `wait` name a person. **`[since …]` is the age authority** — without it, fall back to git history, and if neither is trustworthy **render no age at all. A missing age is fine; a wrong one destroys trust in the whole table.**

---

## Holds — when life interrupts everything

A hold is involuntary and cross-cutting (illness, travel, a family event); `paused` is deliberate and per-project. Holds live in `wiki/meta/holds.md`, one line each: start, end, reason, scope. Append-only.

- **While a hold is open**, covered items render `held` — no age.
- **After it closes**, render two clocks: the lead number from the later of `[since]` and the hold's end, the true elapsed time in parentheses — `3d (since 01-05, 11d held)`.
- A hold covers an item only if the item predates the hold's start. **`[since]` is never rewritten.**
- A hold changes how ages *render*. It never means nothing is owed.

---

## A capture gap is not a defect

Days with no notes are a normal fact about a human. **Report the consequence** (stale data, false flags) **plainly, then re-read reality from the owner and move on.** Don't editorialise, don't build a mechanism to prevent it, don't carry it as an open item.

---

## The classification test

When something new arrives, in this order:

1. Can you write **"done when ___"** right now, in one sentence? → **Project**
2. Is the honest answer "it's never done," and will it hold projects? → **Area**
3. Neither, but facts and people attach to it? → **Resource or person page** — not a hub

**Reference material:** strip any single Area's context from the note. **Claim still holds → `3. Resources/Research/`** (topic tags only). **Claim needs that Area's frame → `2. Areas/<Area>/knowledge/`.**

**The vault holds knowledge, not files.** Binaries (PDFs, decks, images, spreadsheets) live outside the vault; the vault holds a markdown note of what they say, attributed, with a path to the file. Where they live is up to you, or to *The file plane* below.

---

## Naming conventions

- **Folders:** Title Case with spaces.
- **Workstream IDs:** `<PREFIX>-<N>` — a short uppercase prefix set once on the Area hub (`id_prefix:`), and a counter (`workstream_counter:`) that is the source of truth. **IDs are never reused.**
- **Hub files:** Project → `<ID>_hub.md`. Area → `<Area>_hub.md`. **The `_hub` suffix is load-bearing** — every glob matches the suffix, never the whole name.
- **People:** `Full Name.md`.
- **Dated files** — decisions, and any ledger, tracker or report filed on a hub — `YYYY-MM-DD-[slug].md`, dated at creation. Name it right on creation; renaming later breaks links.
- **Inbox captures:** `YYYY-MM-DD-HHMM [slug].md`. Daily notes: `YYYY-MM-DD daily.md`. Sweeps: `YYYY-MM-DD weekly-sweep.md`.
- **An ID never travels alone in prose.** Write `WEB-3 Pricing Page`, not bare `WEB-3`. Bare IDs are fine in frontmatter, filenames, and folders.
- **Links:** `[[wikilinks]]` without the `.md` extension. They render in Obsidian and read fine as plain text anywhere else.
- **A label the owner can't read is a defect in the label.**

---

## Vocabulary enforcement

Canonical spellings of names and terms. `orion-lint` parses this table — keep the two-column shape.

| Always use | Never use |
|---|---|
| *(add rows as corrections arise)* | |

---

## Log entries classify themselves

Every `wiki/log.md` heading carries `[build]` or `[vault]`:

```
## 2026-01-05 — [build] Pricing page shipped
## 2026-01-05 — [vault] Ingested three captures; two person pages created
```

A `[build]` entry **must** carry a `Shipped:` line naming what exists now that didn't before. **If you can't fill it, it's `[vault]`.**

---

## After every session

1. **`cascade`** — rewrites `hot.md`, appends one log entry, rebuilds `index.md` if structure changed.
2. **Commit, if the vault is a git repo.** Stage explicit paths (not `git add -A`), write a message that says *why*. Nothing auto-commits.

## Agents (Claude Code, optional)

Skills are procedures; the main session runs them. **Agents are workers with their own area, tools and rules** — called directly, or handed one step of a skill. Each one reads this file before touching the vault, and **this file wins on vault matters.** The main session stays accountable for whatever an agent returns: it reads the return, checks it, and passes it on. **A subagent's claim that it verified something is not verification.**

| Agent | Role | Called from | Never |
|---|---|---|---|
| `orionite` | Vault mechanic: cascade and lint passes | `orion-cascade`, `orion-lint` | Judgment work (ingest, review, daily) |
| `orionite-people` | The people follow-up sweep | `orion-cascade`, `orion-lint` | Anything else |
| `thoth` | Secretary: calendar and mail, triage and drafts | Directly · `orion-daily` · `orion-deliver` · `outbound draft` | Send, reply, RSVP or invite; write in the vault |
| `seshat` | Bookkeeper: ledgers, reconciliation, figures | Directly · `orion-close` when a done-when turns on money | Move money, pay or submit anything |
| `sia` | Counsellor: what matters, what's at risk, who takes what | Directly · `orion-review` · the weekly sweep | Write, send or decide anything |
| `odin` | Researcher: sourced findings | `orion-research` | Plans, or prose in the owner's voice |
| `ptah` | Builder: repos, branches, CI, servers | Directly · under `orion-clean-code` | Read a secret. Merge, push to main or change production without the owner's word |
| `anubis` | Guardian: read-only security review | After `ptah`, before the owner merges | Fix or change anything |
| `hathor` | Designer: direction, critique and audit, decision mocks, the build brief, finish review | Directly · before `ptah` builds an interface, and after, beside `anubis` | Edit a site's source, commit or merge; choose for the owner |

**Agents never commit or push the vault** — the main session does, at the end of the session. **`thoth` needs your mail and calendar connector** added to its `tools:` line: read and draft tools only, never send. `ingest` and `daily` require judgment and stay in the main session.

## The file plane (optional)

If you want Orion to manage files outside the vault, copy `6. Templates/registry/` to `registry/` and list your inboxes, outboxes and working roots in `registry/endpoints.md`. Then `ingest boxes` pulls from the inboxes, `orion-deliver` stages into the outboxes, and **every move goes through `.agents/scripts/fpmove.py`**, which records it in `registry/file-moves.md` so `repoint.py` can fix links. Where a skill writes `<skills-repo>/scripts/`, read `.agents/scripts/`. **Without a `registry/` folder, every skill skips the file plane.**

## Publishing (optional)

`orion-publish` reads this table. Leave it empty and it asks.

| Setting | Value |
|---|---|
| Site repo | *(none)* |
| Content path (a file here is published) | |
| Drafts location | |

**Nothing goes into the content path on Orion's word. Only the owner publishes.**

## Updating the skills

The skills, agents and scripts in this vault are copies from the Orion skills repo. To update them: clone it, `git pull`, then run `./vendor.sh /path/to/this/vault`. **Change a skill there, not here** — a local edit is overwritten on the next update. Vault-specific rules belong in this file.
