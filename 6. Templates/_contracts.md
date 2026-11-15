---
type: reference
title: "Page contracts"
tags:
  - reference
---

# Page contracts

**Read this when creating or editing a page.** The `.md` files beside this one are copy-ready skeletons; this file is the rule they implement. **When a contract changes, change its skeleton in the same edit** — a skeleton that drifts from its contract produces pages the skills can't read.

---

## Area hub — `2. Areas/<Area>/<Area>_hub.md`

```yaml
type: area
status: standing            # standing | archived
id_prefix: WEB              # short, uppercase, set once, never changed
workstream_counter: 0       # highest ID issued. Source of truth for IDs
parent:                     # nested Areas only. Never points at itself
updated: YYYY-MM-DD
tags: [hub, <area-tag>]
```

Body: `## What this is` (one sentence) · `## Workstreams` (each Project by ID, with status) · `## Open items` · `## Key files` · `## People`.

**Areas take no `next:`, no `deadline:`, and no freshness computation.** A container doesn't compete for attention.

Every Area has `2. Areas/<Area>/knowledge/_index.md` — seeded at creation, stating what belongs there.

---

## Project hub — `1. Projects/<Area>/<Name>/<ID>_hub.md`

```yaml
type: project               # never `hub`
id: WEB-1                   # from the Area's workstream_counter
area: <Area folder name>    # or the literal `none` — absent ≠ none
done_when: "one sentence, testable"
status: open                # open | paused | closed | archived
next: "verb → target — detail [since YYYY-MM-DD]"   # optional; may be a YAML list
paused_because: "one line"  # required when paused
deadline: YYYY-MM-DD        # optional — the single next delivery gate
closed: YYYY-MM-DD          # set by orion-close
threads: [slug]
updated: YYYY-MM-DD
tags: [hub, <area-tag>]
```

Body: `## What this is` · `## Tasks` (checkboxes, `(owned by: name)` when not the owner's) · `## Open items` · `## Key files` · `## Sent` (written by `orion-deliver`: date — what → who · via which outbox · staged or sent) · `## People`.

- **`done_when:` is required.** If you can't write it, it isn't a Project. If it needs the words "ongoing", "maintain" or "as needed", it's an Area.
- **`next:` — one move per entry.** Two moves go in a YAML list, never packed into one string. Grammar and verbs → `AGENTS.md`, *The `next:` field*.
- **`area: none` is legal but must be written.** Such a project has no knowledge base to receive its deliverable; `orion-close` archives it whole.

**A workstream *is* a Project.** It opens when an Area needs finite work done, and closes via `orion-close`, which returns its deliverable to the Area:

```
Area ──spawns──▶ Project (id, done_when)
  ▲                  │ on close
  └── knowledge/ ◀───┤ deliverable
                     └── process record ──▶ 5. Archive/<Area>/<ID>/
```

A workstream belongs to exactly one Area. A concern spanning several is a **thread**.

---

## Person — `3. Resources/People/<Full Name>.md`

```yaml
type: person
tier: contact               # relationship | contact
name: Full Name
pronouns:                   # ask; never infer from a name. Blank until known
role:
orgs: []
contact:
status: active              # active | dormant
cadence:                    # relationship tier ONLY: weekly | biweekly | monthly | organic
last_contact: YYYY-MM-DD
follow_up_by:               # relationship tier ONLY — a real date
updated: YYYY-MM-DD
tags: [person]
```

Body: `## Role & Relationship` · `## Background` · `## Context` · `## Open Items` · `## Contact History` (dated lines, newest first).

**Two tiers, and only one can flag:**

| Tier | Carries | Can flag? |
|---|---|---|
| `relationship` | `cadence` + `follow_up_by`, both required | **Yes** — the only pages follow-up checks read |
| `contact` | Neither — their presence is a lint finding | **Never** |

**A contact is not a neglected relationship.** It's someone the vault knows facts about. If someone doesn't warrant a real follow-up date, they're a contact.

- **`organic` cadence** means "no fixed interval — the next contact is pegged to a specific event." It still requires a real `follow_up_by`, set against that event.
- **A relationship page with no `follow_up_by` cannot flag and is invisible.** Lint reports it as a defect.
- **Spent follow-ups.** A `follow_up_by` on or before `last_contact` has been overtaken by contact. Compute the live due date instead: `weekly`/`biweekly`/`monthly` → `last_contact` + 7/14/30 days, rendered *(from last contact)*; `organic` → **no date since contact** (never overdue). **Never write the computed date back** — the stored field stays what a person set.
- **`status: dormant`** — the engagement ended; the page and every fact stay.

---

## Decision — `4. Decisions/YYYY-MM-DD-<slug>.md`

```yaml
type: decision
date: YYYY-MM-DD
topic: Short title
areas: [Area or Project]
status: open                # open | closed | reversed
updated: YYYY-MM-DD
tags: [decision]
```

Body: `## Context` · `## Decision` · `## Rationale` · `## Expected outcome` · `## Follow-up` (dated lines).

**Never edit a past decision's substance.** A reversal is a new decision file that links the old one; the old one's `status` becomes `reversed`.

---

## Thread — `3. Resources/Threads/<slug>.md`

```yaml
type: thread
title: Short title
status: open                # open | watching | resolved | dropped
domains: [Area or Project]
people: [Full Name]
opened: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [thread]
```

Body: `## What it is` · `## Why cross-cutting` · `## Current state` (replace, don't stack) · `## What's needed` · `## Update log` (append-only, newest first).

**A thread opens** when one signal shows up in two or more separate Areas or Projects. **It closes** when a decision resolves it, or it collapses to a single domain. Resolved and dropped threads move to `5. Archive/Threads/`.

---

## Reference note — `3. Resources/Research/` or `2. Areas/<Area>/knowledge/`

```yaml
type: reference
title:
source:                     # file, URL, sender, conversation — or "source unrecorded"
updated: YYYY-MM-DD
tags: [reference, <topic or area tag>]
```

**`source:` is never blank.** Placement → `AGENTS.md`, *The classification test*.

---

## Opportunity — `3. Resources/Pipeline/<who>-<vehicle-slug>.md`

**Money at a stage.** A person page models a relationship; an opportunity models a deal. **One file per opportunity, not per person** — one person can carry two deals with different fates, and a connector may carry none.

```yaml
type: opportunity
stage: pre-contact          # pre-contact | warm | verbal | committed | dead
amount: 10000               # blank when genuinely unknown
vehicle: what instrument    # a contract, a grant, an investment, a sale
for: what it funds or buys
people: [Full Name]
owner: <who drives it>      # not always the vault's owner
next: "send → Sam Example — revised terms [since YYYY-MM-DD]"
opened: YYYY-MM-DD
updated: YYYY-MM-DD
confirmed: YYYY-MM-DD       # blank = nobody has checked
tags: [opportunity]
```

| Stage | Means |
|---|---|
| `pre-contact` | Identified. No conversation yet |
| `warm` | In conversation. Nothing agreed |
| `verbal` | Said yes. Nothing papered, no funds |
| `committed` | Papered, or funds moving |
| `dead` | Won't happen. **The file stays**, so a failed deal isn't re-pitched |

Body: `## What's on the table` · `## Where it stands` (state — replace it) · `## What it's waiting on` · `## Source` · `## History` (append-only, newest first).

- **`owner:` is load-bearing.** An opportunity the vault's owner doesn't drive never produces a send for them.
- **`confirmed:` blank is an admission, not a status.** Nothing unconfirmed is reported as fact.
- **`next:` uses the project grammar.** `orion-cascade` reads it here too, so a pipeline gate lands in Outstanding sends beside project gates.

---

## Vendor — `3. Resources/Vendors/<Name>.md`

A company or service the owner buys from or works with. **A standing entity, like a person** — it doesn't archive with the project that introduced it.

```yaml
type: vendor
provides: one line
people: [Full Name]         # contacts there, if any
used_by: [WEB-3]            # projects, by ID
updated: YYYY-MM-DD
tags: [vendor]
```

Body: `## What they provide` · `## Terms` (attributed: who quoted what, when) · `## History`.

---

## Inbox notes

Daily notes and weekly sweeps carry `date:` and `tags: [inbox, daily-note]` / `[inbox, weekly-sweep]` — no `type:`. Captures carry `date:` and `tags: [inbox]`.
