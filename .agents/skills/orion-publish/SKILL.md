---
name: orion-publish
description: "The rule for what may leave an Orion vault and go on the owner's site (or any public target named in AGENTS.md). The owner writes the pieces; Orion supplies the sourced fact sheets they write from and runs the rule over every piece. Nothing goes into the publish target or any outbox on Orion's word; only the owner publishes. Triggers on: publish, publish this, orion-publish, draft for the site, draft an entry, fact sheet for, push to the site."
---

# orion-publish — the rule, and what Orion hands over

**The owner writes. Orion supplies the facts.** This skill is not a pipeline. It is a rule about what may leave the vault, and a description of what Orion hands over so the owner can write.

**The publish target** — the site's repo, its content path, and where drafts live — is whatever the owner names in the **Publishing** section of `AGENTS.md`. If `AGENTS.md` names none, ask before writing anything.

---

## The one thing that must not happen

⛔ **Never write into the publish target's content path.** Assume a file there is published. A draft flag is not protection: if the repo is public, or ever becomes public, every draft in it can be read in its source. **Only the owner moves a piece into the content path.**

⛔ **Nothing goes in any outbox, shared folder or send queue on Orion's word.** Only when the owner says to put it there.

⛔ **Never push or deploy the site** unless the owner asks.

---

## What Orion hands over — a fact sheet, not prose

Prose drafted in the owner's voice tends not to be what they would write, and restyling it doesn't fix that. What they can write from is the facts. So by default Orion hands over a **fact sheet**:

- **What happened, in order.**
- **Every number, date and named artifact** — each with its source (`[A, who date]`, a file, a commit, a URL).
- **What the record does not hold** and is the owner's to supply.
- **Themes or lanes**, when asked: the angles the material supports, each with the facts behind it.

**Prose only when the owner asks for it.**

## Where things go

| What | Where |
|---|---|
| A fact sheet, a themes sheet, anything the Area knows | The `knowledge/` folder of the Area that owns publishing (as named in `AGENTS.md`), dated filename `YYYY-MM-DD-<slug>.md`, in the vault the material draws on |
| A draft of a piece, when the owner asks for one | The `drafts/` folder of the Project that owns the piece. **A work in progress stays in its project** |

Inside a `drafts/` folder, use the path the piece will have in the content path, per the site's own README — so publishing is a move, not a rewrite. The folder's `_index.md` lists what's there.

**Classifying a piece** (if the site has these kinds): something shipped or learned on a project, dated → an entry under that project. A method that held up on two or more projects, names removed → a pattern. Thinking still being worked out → an essay.

---

## The rule — run on every piece and every fact sheet, no exceptions

**Projects yes. People and money no.**

Strip or generalize:

1. **Individuals** — no names of people from `3. Resources/People/` or anywhere else in the vault. Replace with roles ("the founder", "a collaborator"). A name a project has already published itself may stay only with the owner's approval for that piece.
2. **Dollar figures** — no amounts: fees, raises, retainers, budgets, rates, valuations. Shape, not scale.
3. **Deal terms** — no tranches, equity, lease terms, investor structures, negotiation state, who has signed what.
4. **Internal reads on people** — no assessments, trust judgments, exclusion signals, or anything from a thread or person page that characterizes a person or a relationship.
5. **Live sensitive state** — nothing about an unresolved situation. If the story needs it, wait until it resolves.
6. **Anything that locates a machine or a person** — hostnames, addresses, repo locations, secrets state, open security or safety findings.

**Content fenced in `AGENTS.md` never reaches a piece** — it is never read in the first place.

### "In development" describes the work

A site may write about projects while they are still moving. Rule 5 still holds. The default reading that reconciles them — the owner may tighten it in `AGENTS.md`:

| Can be written while live | Waits until it resolves |
|---|---|
| What was built, tested, measured, abandoned | Negotiations, terms, who signed what |
| The design question being worked | Reads on people; who is in or out |
| The rule a failure produced | Open security or safety findings |

### Say whose work it is

**Never read authorship off a git author field.** Commits made with an agent can carry the owner as author while an agent wrote the code — check the `Co-Authored-By:` trailers, and check the hub for what the record actually puts in the owner's hands.

Each project page states the owner's part and where it stops. If something was built by someone else, the page says so. **How the site speaks about work an agent wrote is the owner's wording to choose.**

### When the rule bites

- **Borderline:** keep it in the draft and add a line to the `review:` block in the draft's frontmatter saying why. Never silently include, never silently drop.
- **If the rule would gut the piece** — the story *is* the sensitive part — stop and say so. Don't write a hollowed-out version.

The **Vocabulary enforcement** table in `AGENTS.md` applies.

---

## When the owner asks for a fact sheet

1. **Read the sources in full**, and the record around them: the hub, the repo's README, its known-issues file, its commit log. If a source can be opened, open it. Don't write from an earlier summary.
2. **Run the rule** over what you plan to include.
3. **Write the fact sheet** — in order, every fact sourced, gaps listed as the owner's to supply.
4. **Save it** to the publishing Area's `knowledge/`, dated.
5. **Report:** what it covers, where it is, what the rule took out or flagged.

## When the owner asks for a draft

1. **Read the sources in full**, as above.
2. **Run the rule.**
3. **Write in the site's voice** — first person, plain, specific. Dates and numbers carry the argument. No vault vocabulary (hubs, cascade, workstreams) without explanation.
4. **Put every number's source in `review:`**, and every sentence that rests on an inference. **Say in `review:` that the draft is Orion's wording until the owner edits it.**
5. **Save it to the owning Project's `drafts/` folder**, at the path it will publish to.
6. **Report:** what was drafted, where, what the rule took out or flagged, and how to preview it with the site's own command.

---

## Output

```
## Publish — <fact sheet | draft> · <piece>

Saved: <path> (never the content path)
Sources: N facts, each sourced · gaps for you: <list>
Rule: removed <what> · flagged in review: <what> · or nothing
Preview: <the site's own command> (drafts only)

Only you publish.
```

## Rules

- **The owner writes the pieces.** Orion supplies sourced fact sheets; prose only on request.
- **Never write into the publish target's content path.** Only the owner moves a piece there.
- **Never write to an outbox** unless the owner names it.
- **Never push or deploy** unless the owner asks.
- **Never edit the source vault file.** This skill reads the vault and writes only to a knowledge base or a project's `drafts/` folder.
- **Run the rule on everything** — people, money, terms, reads on people, live sensitive state, location. Borderline is flagged, never silent.
- **Authorship comes from the record, never from a git author field.**
- **A draft is Orion's wording until the owner edits it.**
