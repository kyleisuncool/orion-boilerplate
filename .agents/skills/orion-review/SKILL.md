---
name: orion-review
description: "Deep periodic review of an Orion vault (the 'Orionite' pass), run as an interactive working session with the owner present. Prunes superseded content, folds orphans into real homes, and reads a multi-week slice of wiki/log.md for workflow friction and direction. Writes NO report file — its only durable outputs are the changes it causes and one wiki/log.md entry. Never deletes, only archives. Triggers on: review the vault, prune the vault, orionite, run orion-review, deep vault review."
---

# orion-review — the deep vault review ("Orionite")

`orion-lint` flags structural issues mechanically; `orion-cascade` syncs the wiki layer after each session. `orion-review` is the slower periodic pass that **acts with judgment**. Run it monthly at most — and only when there is appetite to *act*, not just to look.

**Never delete.** The worst outcome for any file is a move to `5. Archive/` with a note pointing at what superseded it.

---

## This skill writes no report file

A review report goes stale within a day: the owner acts on the vault, and the report keeps recommending changes to things that have already moved. Successive reports end up reviewing each other's unacted recommendations. **A report that can't survive the day it was written is a conversation that got filed by mistake.**

**So review runs as a conversation.** Its durable outputs are exactly two: the changes it causes, and one `wiki/log.md` entry. A finding that doesn't survive the session wasn't a finding.

**Precondition:** if the last review produced findings nobody acted on, running again produces the same list. Say so and stop. Prefer an interactive pass against what's already known over a fresh inventory of it.

**The owner must be present.** If nobody is going to act in this session, don't run.

---

## Inputs

- **The vault** — the folder the session runs in. If the session spans several vaults, ask which one.
- **Hubs** — every `*_hub.md` in `1. Projects/` and `2. Areas/`.
- **Lint input** — `wiki/meta/lint-report-YYYY-MM-DD.md`, the one current report.
- **History** — `wiki/log.md` and any `wiki/folds/*` covering the window.
- **Standing questions** — `wiki/meta/open-questions.md`.

⚠ **Exclude every path listed under Fences in `AGENTS.md`** from every read, grep and scan.

---

## Sequence

### 1. Scope check — before anything else

**Read every `open` project** (and `practice`, if the vault's status vocabulary defines it), **plus every `standing` Area.** Skip every `paused` and `archived` hub entirely.

This is the biggest determinant of how large the session gets. **Paused means invisible — honor it.** If the open list outgrows a session, `paused` is the lever, not a new status.

**Areas carry no attention status.** Never compute freshness drift on an Area, and never draft an "Area-refresh proposal" — such proposals get produced every review and acted on never.

### 2. Gather lint input

Use the current lint report if it is dated within 7 days. Otherwise run `orion-lint`'s checks in memory. **Don't write a lint report from inside review.**

### 3. Classify findings, then work them with the owner, live

| Bucket | Criteria | Handling |
|---|---|---|
| **Auto-link** | Orphan clearly belongs to one hub, person or thread; the tie already exists in text, just no wikilink | Do it, mention it |
| **Auto-move** | File at the wrong PARA depth with an unambiguous destination | Do it, mention it |
| **Archive candidate** | Explicit supersession language present, no inbound links | Do it, mention it |
| **Reorg / ambiguous archive** | Anything requiring judgment | **Ask, in the session.** Don't file it for later |

There is no `--commit` gate. **The gate is that the owner is present.**

**Reference-note placement is an Auto-move lint can't supply.** Lint catches *tag* drift; a `type: reference` note whose Area tag matches its folder passes lint even when its content is domain-agnostic. That takes a content read: for each note in an Area's `knowledge/`, ask whether its claim would still hold with the Area's context stripped. If it would, **and it is verified by use** (an unsourced capture stays Area-native), move it to `3. Resources/Research/`, strip the Area tag, repoint inbound links — in the session.

Every move repoints its inbound links, ledgers included, target only, never prose — method in `orion-close` step 6.

### 4. Workflow evaluation

Read `wiki/log.md` plus any `wiki/folds/*` covering the window — since the last review's log entry, or 30 days.

Look for **repeated friction, not incidents:** the same blocker across 3+ entries, a lint category recurring unchanged, a thread collapsed to zero live domains.

**Report the `[build]` / `[vault]` ratio** for the window. It is the fastest read on whether the vault is serving the work or absorbing it — a vault mostly logging `[vault]` entries is maintaining itself.

**Cite the specific log entry or fold behind every observation.** Describe friction; don't prescribe.

### 5. Direction evaluation

Per **in-scope** project only: what shipped, what stalled, what changed scope. One short paragraph plus 2–3 concrete options. **The owner's call** — make the choice legible, don't make it.

**Optional second read:** if your harness has the `sia` agent, dispatch it with the in-scope hubs, the log window and step 4's friction findings, asking what's at risk, what's being missed, and what clashes. Bring its counsel to the owner **as Sia's**, beside your own read, where they differ. Never write it into a file — this skill writes no report. Without `sia`, give your own read alone.

**Watch every `next:` that begins `send` or `wait`.** Those are gated on a person, not on effort. Unfinished work is far more often blocked on a message than on building; **a `send` sitting for weeks is the most important signal a review can surface.**

### 6. The two-cycle rule

**A finding that has survived two consecutive reviews without action is not a finding — it is a decision nobody has made.**

Move it out of the review and into `wiki/meta/open-questions.md` as one line with a forced binary:

```markdown
- **[Question]** — Option A / Option B. Raised YYYY-MM-DD, carried N cycles.
```

Then stop reporting it. Re-litigating old findings inflates recurrence counts into false urgency.

### 7. Append to `wiki/log.md`

One entry. The only file this skill writes besides the changes themselves.

```
## YYYY-MM-DD — [vault] Orion review
- Scope: N in-scope projects (N paused hubs skipped)
- Acted: N linked · N moved · N archived
- Log ratio this window: N [build] / N [vault]
- Moved to open-questions.md: N
- Friction: [one line each, cited]
```

### 8. Suggest next step

If structure changed, suggest `cascade`.

---

## Rules

- **No report file. Ever.** Durable output is the changes plus one log entry.
- **Never delete** — archive only, with a note pointing at what superseded it.
- **Skip `paused` and `archived` hubs.** Never draft Area-refresh proposals; Areas have no attention status.
- **Fenced paths are never read or scanned.**
- **Judgment calls get asked live**, not filed as proposals for a future session that won't come.
- **Two-cycle rule** — a twice-surviving finding becomes an open question, then leaves the review.
- **Extractive analysis** — cite the log entry or fold behind every observation.
- **Direction evaluation proposes options, never a verdict.** A `sia` read is labelled as Sia's and never filed.
- **If nobody is going to act in this session, don't run.**
