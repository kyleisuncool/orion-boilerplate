---
name: orion-research
description: "Run a deep-dive research session into a knowledge set in an Orion vault: plan the questions from what the vault already holds, fan out research agents, verify the load-bearing sources, and write a numbered set of explanatory files — every claim tagged, every file ending in a full Sources section with accessed dates. Two depths: standard (the default) and robust (on the owner's word: 'robust', 'rigorous', 'make it robust', 'go deep and verify') — every source re-opened, archived and re-checked, plus a counter-evidence pass. Also runs a robustness pass over an existing set, and a ravens' run (what has changed in the world since a set was written). Research and verification are dispatched to the odin agent where the harness has it. Triggers on: odin, ask odin, deep dive, research [topic], knowledge set on, do a deep dive, robust deep dive, make this set robust, robustness pass, ravens, ravens' run, what's changed since, refresh this set."
---

# orion-research — deep dives into a knowledge set

**A deep dive produces source material, not a plan.** It answers what something is, how it works, what it would take, and why it matters to the work in front of the owner — with every claim traceable to where it came from. **Decisions stay the owner's.**

---

## Two depths. Standard unless the owner says robust.

| | **Standard** (default) | **Robust** (on the owner's word) |
|---|---|---|
| **Trigger** | "deep dive", "research X" | "robust", "rigorous", "make it robust", "go deep and verify", or a robustness pass on an existing set |
| **Prose** | Explanatory: what it is, how it works, why it matters here, what's uncertain. Short summary on top | Same, plus a worked example or the arithmetic wherever a number drives a conclusion |
| **Sources** | Inline footnote citations; every file ends in a `## Research notes` and an annotated `## Sources` with accessed dates; agents return every URL they read, cited or not | Same |
| **Verification** | Orion re-opens the **load-bearing** sources — the ones a finding rests on | Orion re-opens **every** cited source; dead pages get a Wayback link |
| **Archive** | Accessed date recorded | Plus a Wayback snapshot requested for each cited URL (`https://web.archive.org/save/<url>`) and the snapshot URL recorded |
| **Counter-evidence** | Conflicts noted when found | **A dedicated pass** searching for sources that disagree with each numbered finding; records what it found, or `[?]` |
| **Re-check** | — | `### ⚠ Re-check findings` in each file: where a source now says something different from the file |
| **Cost** | ~4–7 agents | Roughly double: a verifier per research agent |

**Standard is not terse.** A copyediting pass is for documents that get sent and for state prose; it **does not compress research**. A research file explains.

**If the owner doesn't say which, run standard and say in one line that robust is available.** Never ask them to choose before starting.

---

## Sequence

### 1. Read the vault first — alone, before any research

- **`AGENTS.md`** — fences, the attribution rule, naming. ⛔ **Prune every path listed under Fences from every search** — in your own commands and in every agent prompt.
- **Grep the vault for the topic and its neighbours.** Record what's already on file and in whose words — `[A, who date]`. **A word the vault uses but never defines is a finding:** say so, and don't define it for the owner.
- **Find the anchors** that make the research specific: the site, the hardware, the people, the numbers already on file. Generic research with no anchor to the work is a lesser product.

### 2. Plan the files

One file per question cluster, numbered `00`–`NN`, `00` being the index. **Every file answers a question the owner would ask**, not a heading from an encyclopedia. Include a file that maps the research back onto the vault's own work when the topic touches it.

**Placement** follows the classification test in `AGENTS.md`. A fresh deep dive is **not verified by use**, so it is **area-native** — `2. Areas/<Area>/knowledge/` — even when the subject is general. It earns `3. Resources/Research/` only later, by use. **If which Area is unclear, ask** — never settle it by placement, and never file a set outside the vault of the workstream that asked for it.

**Filenames:** `YYYY-MM-DD-<set-slug>-NN-<file-slug>.md`, dated the day written.

### 3. Fan out research agents

**One `odin` agent per file or cluster, launched in parallel.** Odin carries the method, the tags, the fence discipline and the return format in its own definition, so the prompt carries only what's specific to this dive: the mode (`research`), the file's questions, and the anchors.

**If your harness has no `odin` agent** (or it doesn't load), fall back to a general-purpose agent with the full list below in its prompt, and say so in the report. Either way, a prompt states:

- **Today's date, and "verify current status with live sources; don't rely on memory."**
- The anchors from step 1, so the agent researches *this* site, *this* hardware, *this* stack.
- **No vault access** unless the file needs it — and if it does, the fences, verbatim.
- The return format:
  - numbered findings, each ending in a tag and a URL
  - explanatory, not terse
  - conflicts between sources flagged explicitly
  - **a verbatim excerpt** (one or two sentences, quoted) for every load-bearing claim
  - **an annotation for every cited source** (format in step 6)
  - **research notes:** queries run, dead ends, pages that failed (403, 404, DNS), and how each conflict was weighed
  - `## All URLs read` — **every** page opened or seen in results, cited or not: title · publisher · page date · URL · `[V·r]`/`[V·s]`
  - the access date

**Robust:** once each research agent returns, launch one `odin` in **verify** mode per research agent: re-open every cited URL, request a Wayback snapshot, search for counter-evidence to each numbered finding, report contradictions verbatim. Hand it the run's Sources and findings, not the vault.

### 4. Verify, then write

**Orion re-opens the load-bearing sources itself** (robust: every source) before writing a claim as `[V]`. Corrections caught this way go in the file *and* in the index's "how it was verified" paragraph — they are the evidence the method works.

Every file has:

- frontmatter per the reference-note contract in `6. Templates/_contracts.md` — `type: reference`, `title`, `source:` (never blank), `updated`, `tags` (Area tag plus topic tags)
- a line linking back to the index
- the tag legend
- **What's on file** — the vault's own record on this question, attributed
- **The short version** — 3–6 numbered points, each `[I]` unless directly sourced
- explanatory sections, **cited inline**
- `## Research notes`
- `## Sources`, annotated (step 6)

**Inline citations.** Every sourced claim carries its tag **and** a footnote pointing to its Sources entry: `…wound down in November 2024 [V][^3].` The footnote text is the source's short title and the section it supports — `[^3]: Example Weekly, 2024-11-07 — §4` — and the full entry lives in Sources. **A tag with no footnote is a defect; so is a footnote with no Sources entry.** Vault captures cite as `[A, who date]` with a wikilink; an `[I]` needs no footnote.

**Callouts in the body**, right under the claim they qualify:

- `> [!note]` — background, or why this matters to the work
- `> [!warning] Conflict` — sources disagree: which, and which one the file follows and why
- `> [!question]` — something only the owner (or a named person) can answer
- `> [!quote]` — the source's own words, for a load-bearing claim

**`## Research notes`**, before Sources — the working record a later session needs to trust, extend or redo the file:

- **Method:** which agents ran, what each covered, what Orion re-opened itself
- **Queries:** the searches that produced findings, and the ones that found nothing (`[?]` claims cite these)
- **Dead ends:** pages that failed and what was used instead
- **Conflicts weighed:** each disagreement, the evidence on each side, the call made
- **Corrections:** what verification caught, and what the file said before
- **Open threads:** what wasn't researched and would change the conclusions

**The index (`00`)** has: the owner's request, verbatim · what the set is and is not · the file table · the numbered findings that change how the work is planned · the tag legend · how it was verified, and what that caught · questions only the owner (or a named person) can answer.

### 5. The tags

| Tag | Means |
|---|---|
| **[A, who date]** | Attributed to a person, from the vault's first-hand captures |
| **[V]** | Orion opened the source this session and the claim matches |
| **[V·s]** | Confirmed only from a search-result excerpt |
| **[V·r]** | A research agent reported it from the linked source; Orion did not re-open it |
| **[I]** | Inference or arithmetic; not sourced |
| **[?]** | Not found — never the same as "doesn't exist" |

**An attribution is never a needless word.** A hedge that records real uncertainty stays.

### 6. The Sources section — every file, annotated, with accessed dates

Every cited source is a numbered, **annotated** entry whose number matches the footnotes in the body:

```
## Sources

1. **Title** — Publisher · page date (or n.d.) · accessed YYYY-MM-DD [· snapshot <wayback url>] · <URL> · [V]/[V·r]/[V·s]
   - **What it is:** primary (the spec, the law, the vendor's own page, the dataset) or secondary (reporting, a blog, an aggregator, a forum post); who wrote it
   - **Why trust it, or not:** authority, independence, recency, read in full or only summarised
   - **Supports:** §N — the claim(s), and a short verbatim excerpt for any load-bearing one
   - **Caveats:** what it doesn't say, conflicts, staleness, paywall or partial read

### Also consulted
(URLs agents read that nothing in this file cites — kept so the trail is complete)

### From the vault
(wikilinks and [A, who date] captures the file draws on)

### From the set
(for synthesis files: each claim's upstream file and section)

### ⚠ Re-check findings (YYYY-MM-DD)   ← robust, or whenever found
(claim · what the source now says · URL — the claim is not silently changed)
```

**Primary beats secondary.** Prefer the spec, statute, vendor page or dataset itself; when only a secondary source was reachable, say so in its annotation. **An aggregator or a search snippet never carries a load-bearing claim alone** — it goes in as `[V·s]` with that caveat.

### 7. Robustness pass on an existing set

When the owner asks to make an existing set robust:

1. **Confirm the files are committed** — git is the rollback.
2. Split the files across `odin` agents in research mode (or the fallback), naming the files each may edit. Each agent:
   - opens every inline URL, records it in Sources **with an annotation and accessed date**, and checks it's live (Wayback link if dead)
   - adds footnote citations linking each sourced claim to its Sources entry, and a `## Research notes` section recording what the pass checked and found
   - fleshes out terse fragments into explanation (~1.5–2× length through explanation, not padding)
   - **preserves verbatim every attribution, tag, quote, figure, date and hedge**
   - adds a new fact only from a source it opened, tagged `[V]`; marks its own reasoning `[I]`
   - keeps headings, since other files link to their anchors
   - sets `updated:`
   - **reports contradictions instead of fixing them**
3. **Read every diff before reporting:** `git diff --stat`, then spot-check that tags and figures survived.

### 8. Close

- Update the Area's `knowledge/_index.md` with the set: one entry, its date, what it covers, and why it is area-native.
- Add the index to the Area hub's `## Key files`.
- Batch with the session's other edits. **Cascade once at session end**, then commit per *After every session* in `AGENTS.md`.
- **Report to the owner:** what the set covers, the findings that change plans, what verification caught, the questions only they can answer, and — on standard — one line that robust is available.
- **What the findings mean for the owner's work is not the set's job.** If the owner asks, and your harness has the `sia` agent, dispatch it with the index and the findings that change plans for counsel against their commitments. **Never fold that counsel into the research files.**

### 9. Ravens' run — what's changed since

On the owner's word ("ravens", "what's changed since", "refresh this set"), over an existing set. Odin's two ravens: **Muninn** (memory) re-checks what the set already says; **Huginn** (thought) looks for what's new.

1. Read the set's index and each file's `updated:` and `## Sources`. **Confirm the set is committed.**
2. Dispatch one `odin` in **ravens** mode per file or cluster (or the fallback, with both jobs spelled out), handing it the file's questions, its Sources and its `updated:` date.
3. **Muninn's findings** go in each file's `### ⚠ Re-check findings (YYYY-MM-DD)` — claim · what the source now says · URL. **The claim is not silently changed.** A dead source gets its snapshot link.
4. **Huginn's findings** — something new on the file's questions since its date — go in a dated section, `## New since YYYY-MM-DD`, tagged and footnoted like any claim, with Sources entries. Re-open each load-bearing one yourself before writing it `[V]`.
5. Set `updated:` on each file touched; add one line to the index: the date of the run, what changed, what didn't.
6. **Report only what changed** — re-check findings and new items that would move a plan. "Nothing changed" is a complete and good answer.

A ravens' run touches only the set it was pointed at. It never re-plans, re-files, or adds files; a gap it finds is an open thread for the owner, not a new file.

---

## Output

```
## Research — <set name> (<standard | robust | robustness pass | ravens>)

Set: 2. Areas/<Area>/knowledge/YYYY-MM-DD-<set-slug>-00-index.md (+ N files)
Agents: N odin (research) · N odin (verify) — or fallback: general-purpose
Findings that change plans: <numbered, one line each>
Verification caught: <corrections> · or nothing
Only you can answer: <questions>
Robust available: <one line, on standard>

Next: cascade at session end.
```

## Rules

- **Read the vault first, alone.** Fenced paths are pruned from every search and every agent prompt.
- **Standard by default; robust only on the owner's word.** Never ask which before starting.
- **Explain, don't compress.** Research files are not run through a style pass.
- **Every claim is tagged; every sourced claim is footnoted; every file ends in a full, annotated Sources section with accessed dates.**
- **Never drop a URL an agent read.** Uncited still goes under *Also consulted*.
- **Re-open load-bearing sources yourself** (robust: every source) before writing `[V]`.
- **Contradictions are reported, never silently fixed.**
- **A fresh set is area-native.** Ask when the Area is unclear; never settle it by placement.
- **Never define a term for the owner** that the vault records as undefined in their words. Give the public meanings, sourced, and leave theirs open.
- **Never turn research into a plan**, or a finding into a recommendation the owner didn't make.
- **Never write prose in the owner's voice for publication** — facts and themes only (`orion-publish`).
- **Never file a deep dive in an outbox**, or outside the vault of the workstream that asked for it.
