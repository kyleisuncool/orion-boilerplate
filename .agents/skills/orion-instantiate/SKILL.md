---
name: orion-instantiate
description: "Create a Project (workstream) or Area in an Orion vault against its frontmatter contract. Runs the done-when test first, assigns the workstream ID from the Area's counter, seeds the Area's knowledge/ folder, and registers the new hub so it is never an orphan. Also converts a Project that turns out to be an Area, and dissolves a redundant parent Area. Triggers on: new project, new area, new workstream, create project, create area, instantiate, this should be an area, dissolve area."
---

# orion-instantiate — create a Project or Area

Creation is where most structural defects start: a hub with no done-when never finishes, a hub with no Area can never be measured against anything, and a hub nobody links to is an orphan from day one. This skill makes creation follow the contract in `6. Templates/_contracts.md` instead of copying a template and hoping.

---

## 1. The test — before anything else

| Question | If yes |
|---|---|
| Can you write **"this is done when ___"** in one sentence, right now? | **Project** |
| Is the honest answer **"it's never done"**? | **Area** |
| Neither, but facts and people attach to it? | **Resource or person page — not a hub.** Stop here |

⚠ **If the done-when needs "ongoing", "maintain", or "as needed", it is not a Project.** It is an Area, or a task inside one.

If the owner hasn't given a done-when and you can't derive one from what they said, ask for it. **No done-when, no Project.**

---

## 2. Creating an Area

1. Folder: `2. Areas/<Area Name>/` (Title Case, spaces).
2. Hub: `<Area Name>_hub.md` from `6. Templates/area-hub.md`:
   - `type: area`, `status: standing`
   - `id_prefix:` — short, uppercase, unambiguous, **not already used by another Area** (grep every `*_hub.md` for `id_prefix:`). Permanent once set.
   - `workstream_counter: 0`
   - `parent:` only if nested, and **never pointing at itself.**
3. **Seed `knowledge/_index.md`** — the Area's permanent memory. State in two or three lines what belongs here (durable material that needs this Area's frame to make sense) and what doesn't (reusable-anywhere material → `3. Resources/Research/`; process notes → the workstream). **This is the step that gets skipped.** Without an obvious home, knowledge scatters.
4. Pick an Area tag (lowercase-kebab) and register it in `wiki/meta/tags.md`.

## 3. Creating a Project (workstream)

1. **Pick its Area.** Default: every Project has one. If it genuinely has none, write `area: none` explicitly — absent is indistinguishable from an oversight. ⚠ An `area: none` Project has no counter to draw an ID from: use prefix `X` with the next number not used by any hub in `1. Projects/` or `5. Archive/`, and tell the owner its deliverable will archive whole on close.
2. **Assign the ID — read the counter, never scan for it.**
   1. Read `workstream_counter:` on the Area hub.
   2. Increment it and **write the new value back first.**
   3. `id: <PREFIX>-<new value>`.

   ⚠ **Scanning existing hubs for the highest ID collides.** Closed projects have moved to `5. Archive/`, so a scan of `1. Projects/` sees a lower maximum than was issued. The counter persists; the hubs don't. **IDs are never reused.**
3. Folder: `1. Projects/<Area>/<Project Name>/`. Hub: `<ID>_hub.md` from `6. Templates/project-hub.md`. **Assign the ID before creating the file — the ID is the filename.**
4. Frontmatter: `type: project` (never `hub`), `id`, `area`, `done_when` (**the sentence verbatim**, not a paraphrase), `status: open`, `updated`, `tags: [hub, <area-tag>]`. Add `next:` if a first move is known.

## 4. Register — part of creation, not after it

- [ ] **Project:** listed on its Area hub under `## Workstreams` with its ID and status
- [ ] **Project:** Area's `workstream_counter:` incremented
- [ ] **Area:** tag in `wiki/meta/tags.md`; `knowledge/_index.md` seeded
- [ ] At least one inbound link (Area hub → Project; `wiki/index.md` → Area)
- [ ] **No file-plane folder yet** (if you use the file plane). A workstream's folder is created when its first material arrives, via `orion-ingest` endpoint mode — never empty at creation
- [ ] Suggest `cascade` — structure changed

---

## Converting a Project that turns out to be an Area

A Project that fails the done-when test isn't finished — it was misfiled. **Ask the owner before converting; it is a change, not a repair.**

1. **Correct the hub first.** Converting a hub with false statements relocates them.
2. **Route everything in a table in the hub:** each task or sub-effort → done (history) · ongoing (Area open item) · has a real done-when (its own new Project with an ID) · dead (closed, reason stated).
3. Move the folder to `2. Areas/<Name>/`, rename the hub `<Name>_hub.md`, set `type: area`, `status: standing`.
4. ⚠ **Give it `id_prefix:` and `workstream_counter: 0` now.** Conversion is the one path into Area-hood that skips the creation contract; an Area without a counter can never spawn a workstream, and nothing reports it.
5. Seed `knowledge/_index.md`. Repoint inbound links (see `orion-close` step 6 for method). Log it. Cascade.

---

## Dissolving a parent Area — when the container itself is redundant

Neither conversion nor `orion-archive`: the work inside is live, only the container goes. **Ask the owner first; it is a change.**

1. **Route everything in a table at the top of the dissolving hub** — each workstream, nested Area, `knowledge/` file and open item, with its destination and the reason. **The table is also the reverse map.**
2. **IDs never change.** A workstream keeps `<OLD>-N` wherever it lands; only `area:` changes. The old Area's counter is final. Renumbering breaks every ledger, note and filename that cites the ID.
3. **Nested Areas are promoted, not re-created.** Remove `parent:`; keep `id_prefix:` and `workstream_counter:`.
4. **A workstream whose only home was the parent needs a real Area** — use the creation path. ⚠ Don't make one catch-all Area for "the parent's own work": that is the parent again, renamed.
5. **A workstream closing the same day is re-homed first, then closed**, so its deliverable lands in a live `knowledge/`.
6. **Route `knowledge/` by content**, per `orion-archive`'s ownership test.
7. **Move the hub into `5. Archive/<Parent>/`** with a tombstone per `orion-archive`, and retire the parent's tag in `wiki/meta/tags.md` (pages keep it as provenance).
8. **Fenced content moves by path, never by content** — move the folder, repoint outside links, and ask before touching even a `parent:` line inside it.
9. **Scan, move, rewrite, rescan.** Baseline dead links first; rewrite link targets only; the rescan must show zero new dead links.

---

## Output

```
## Instantiate — <ID or Area name>

Done-when: "<sentence>"            (Projects)
Created: <path>
ID: <PREFIX>-<N> — counter now <N> (Projects)
Registered: <Area hub listing · tag · knowledge/ seeded · inbound link>

Next: run cascade.
```

## Rules

- **Done-when test first.** No sentence, no Project.
- **`type:` is `project` or `area`. Never `hub`.**
- **Read the counter, write it back, then use it.** Never derive IDs by scanning. Never reuse one.
- **`area: none` is legal but written.** Absent ≠ none.
- **Every Area gets `id_prefix`, `workstream_counter` and `knowledge/`** however it came into being.
- **Register on creation.** An unregistered hub is an orphan.
