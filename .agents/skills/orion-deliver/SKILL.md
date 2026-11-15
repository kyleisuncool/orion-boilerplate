---
name: orion-deliver
description: "The delivery protocol: stage a finished artifact in the right outbox for whoever it's going to, record the send on its workstream hub, and once the owner confirms it went, file the outbox folder into processed/ with a moves-ledger row. One protocol for every outbox, whatever the service — a shared-drive outbox, a local outbox for what the shared drive can't carry, a synced cloud folder. Part of the optional file-plane protocol. Runs only when the owner names the artifact and the recipient; nothing goes in an outbox on Orion's word. Triggers on: deliver, deliver this, send this to, stage this for, put this in the outbox, mark sent, it went out, orion-deliver."
---

# orion-deliver — the delivery protocol

**The out-half of the file plane**; `orion-ingest`'s endpoint mode is the in-half. **The file-plane protocol is optional.** A vault that uses it keeps **`registry/endpoints.md`** at its root — every inbox and outbox, one row each — and **`registry/file-moves.md`**, the moves ledger. The scripts live in the skills repo's `scripts/` and run against the vault's `registry/`. **The outboxes are the rows with Direction `out`.** A new service is a new row there, never a new procedure here. **No `registry/endpoints.md`, or no `out` row → say so and stop.**

⛔ **Nothing goes in an outbox unless the owner says to put it there.** This skill runs only on an instruction that names **the artifact** and **who it is for**. A finished-looking file is not an instruction. If either is missing, ask; do not stage.

⛔ **Orion stages; the owner sends.** This skill never emails, shares, uploads or messages anything to anyone. Putting a file in a synced folder is staging *because* the owner decides when it goes. If the owner asks Orion to send it through a connector, that is a separate, explicit act they approve in the moment.

**The outbox is never a workspace.** A thing is in an outbox because it is finished and leaving. The working copy stays in its workstream folder, always.

---

## A. Stage — on the owner's instruction

1. **Name the artifact and its workstream.** The final version, in its workstream folder (default layout `~/Documents/YYYY-MM-DD-<ID> <Workstream Name>/…`) or in the vault. The ID is the workstream hub's `id:`.
2. **Choose the outbox.** Read the `out` rows' **Use when** column. Typical rows: a shared-drive outbox for what the shared drive can carry; a local outbox for what leaves another way (USB, a messaging app, in person). **If the owner hasn't named the outbox and the Use-when column doesn't settle it, ask.**
3. **Create the outbox folder and copy the final in:** `<outbox>/YYYY-MM-DD-<ID> <what it is>/`, today's date.
   ```bash
   mkdir -p "<outbox>/YYYY-MM-DD-<ID> <what it is>" && cp -n "<final>" "<outbox>/YYYY-MM-DD-<ID> <what it is>/"
   ```
   **Copy, don't move** — the working copy stays home. `-n` never overwrites. A text deliverable prepared *for* the recipient (a recipient-ready version of a vault page, with vault links and internal notes removed) is written straight into that folder; the vault page stays the record.
4. **Record it on the workstream hub**, in a `## Sent` section (create it above `## Key files` if absent) — one line per delivery:
   ```markdown
   - 2026-01-05 — Revised quote → Sam Example · via `share-out` · `<outbox>/2026-01-05-WEB-3 Revised quote` · **staged, not sent**
   ```
   **Paths in backticks** — that is what lets `orion-lint` verify them. The hub's `next:` stays a `send → <recipient>` until it goes.
5. **If it leaves by email — optional.** If you use the `thoth` agent (or the owner's mail connector directly), have it write the covering email as a **draft** to the recipient: the artifact named, the recipient's name as the vault spells it, no commitment the owner hasn't given. **It never sends.** Add the draft to the hub line (`· email draft <draft id>`). **The owner sends it**, then part B.

## B. Mark sent — when the owner says it went

**Only on the owner's word that it went** ("sent it", "Sam has it", a date). **Never infer a send from the file's absence or age.**

1. **The hub line:** `**staged, not sent**` → `**sent YYYY-MM-DD**`, noting it is on the owner's word. Then retire or replace the hub's `next:` for that send.
2. **A vault text document that went out** gets `sent: YYYY-MM-DD` and `to: <recipient>` in its frontmatter. The record lives on the document and the hub — nothing separate.
3. **File the outbox folder** into its box's `processed/YYYY-MM/`, through the mover:
   ```bash
   python3 <skills-repo>/scripts/fpmove.py "<outbox>/YYYY-MM-DD-<ID> <what>" "<outbox>/processed/YYYY-MM/YYYY-MM-DD-<ID> <what>" --reason sent --note "<ID> → <recipient>"
   ```
   It appends the moves-ledger row, so the hub's staged path still resolves. Then run
   ```bash
   python3 <skills-repo>/scripts/repoint.py <vault> --apply
   ```
   with `--fence <path>` for each path listed under **Fences** in `AGENTS.md`, to update the hub line to the processed path.

---

## Output

```
## Deliver — YYYY-MM-DD

Staged: <what> → <recipient> · <endpoint> · `<outbox path>` — or none
Marked sent: <what> → <recipient>, sent YYYY-MM-DD (owner's word) · filed to `<processed path>` · ledger row written — or none
Hub updated: [[<ID>_hub]] — ## Sent line, next:
Asked: <anything the owner had to choose — which outbox, which version>
```

---

## Rules (binding)

- **Only on the owner's instruction naming the artifact and the recipient.** Nothing enters an outbox on Orion's word.
- **Stage, never send.** No email, share, upload or message on this skill's authority.
- **Copy into the outbox; the working copy stays in its workstream folder.** The outbox is never a workspace.
- **Ask which outbox when the owner hasn't said and the registry doesn't settle it.**
- **"Sent" is the owner's word, never an inference.**
- **Every move goes through `fpmove.py`**, which writes the moves ledger. A hand move leaves a pointer nothing can resolve.
- **Paths in backticks**, on the hub and in documents — or lint can't see them.
