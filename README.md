# Orion

*A second brain management system for AI harnesses.*

A plain-markdown knowledge vault that an AI agent keeps for you. You drop notes, transcripts and documents in; the agent files them, keeps track of what's owed to whom, writes you a daily note, and keeps the whole thing linked and healthy.

It is only folders of `.md` files plus a rulebook (`AGENTS.md`) and thirteen skills (`.agents/skills/`). There's no app and no database, and you're not tied to any one agent vendor. Claude Code users also get nine specialist agents (`.claude/agents/`).

## Start

1. Copy this folder somewhere you'll keep it. Ideally `git init` it, because the agent commits after each session.
2. Point your agent at the folder (see below).
3. Say: **`new area: <something you're responsible for>`**. Then put a note in `0. Inbox/` and say **`ingest`**.
4. At the end of a session, say **`cascade`**. Then read `wiki/hot.md` whenever you want to know where things stand.

## Commands

| Say | What happens |
|---|---|
| `new area: X` / `new project: X` | Creates the hub against its contract. Projects need a "done when" sentence |
| `ingest` | Files everything in `0. Inbox/`: people, decisions, updates, reference notes |
| `cascade` | Rewrites `wiki/hot.md` (current state) and logs the session |
| `daily note` | Closes today's note and writes tomorrow's |
| `weekly sweep` | Lists everything tracked, one line each, with room to write |
| `close workstream: WEB-3` | A finished project hands its deliverable back to its Area |
| `archive: X` / `resume X` | Retires or restores a whole Area. Reversible |
| `lint` | Health check: dead links, missing fields, overdue follow-ups |
| `fold the log` | Compacts old log entries |
| `review the vault` | A deep periodic review: prune, fold orphans in, read the log for friction |
| `research [topic]` | A cited deep dive, written as a numbered knowledge set |
| `deliver: X → Sam` | Stages a finished artifact for someone and records the send. Only on your word |
| `draft for the site` | Sourced facts for a piece you write. You publish, never the agent |

The full list is in `AGENTS.md`.

## Using it with your agent

| Agent | Setup |
|---|---|
| **Claude Code** | Run `claude` in this folder. `CLAUDE.md` imports `AGENTS.md`, `.claude/skills` is a symlink to `.agents/skills`, and the agents in `.claude/agents/` load on their own |
| **Codex CLI** | Run `codex` in this folder. It reads `AGENTS.md` and discovers `.agents/skills/` |
| **pi / oh-my-pi** | Run in this folder. It reads `AGENTS.md` and discovers `.agents/skills/` |
| **Hermes Agent** | Run in this folder (`git init` first: Hermes scans project skills inside a git repo). It reads `AGENTS.md`. Trust the project skills when prompted (`hermes skills trust`) |
| **Cursor, Gemini CLI, others** | Most read `AGENTS.md`. If yours doesn't load skills, that's fine: `AGENTS.md` tells the agent to open `.agents/skills/<name>/SKILL.md` and follow it |
| **ChatGPT / chat-only tools** | Without file access the agent can't maintain the vault. Use a tool that can read and write files, or upload `AGENTS.md` and the relevant `SKILL.md` and apply the edits yourself |

**Windows:** the `.claude/skills` symlink may check out as a plain text file. If so, delete it and run `mklink /D .claude\skills ..\.agents\skills`.

## Obsidian (optional)

Open this folder as an Obsidian vault if you want graph view and clickable `[[links]]`. Nothing depends on Obsidian, and the files read fine in any editor.

## Layout

```
AGENTS.md            the rulebook: every agent reads this
CLAUDE.md            points Claude Code at AGENTS.md
.agents/skills/      the thirteen skills
.agents/scripts/     file-plane tools (optional)
.claude/agents/      nine specialist agents (Claude Code)
0. Inbox/            captures and daily notes
1. Projects/         finite work, grouped by Area
2. Areas/            ongoing responsibilities, each with a knowledge/ folder
3. Resources/        People, Vendors, Threads, Pipeline, Research
4. Decisions/        the decision log (append-only)
5. Archive/          finished work, never deleted
6. Templates/        page skeletons + _contracts.md
wiki/                hot.md (state), index.md, log.md, folds/, meta/
```

## Making it yours

- **Fences:** list paths the agent must never read in `AGENTS.md` → *Fences*.
- **Vocabulary:** add canonical spellings of names and terms to `AGENTS.md` → *Vocabulary enforcement*. Lint enforces them.
- **New page types:** add a contract to `6. Templates/_contracts.md` and a skeleton next to it, both in the same change.
- **Agents:** `thoth` (mail and calendar) needs your mail/calendar connector's read and draft tools added to its `tools:` line. Never grant it send. The roster is in `AGENTS.md` → *Agents*.
- **Files outside the vault:** copy `6. Templates/registry/` to `registry/` to turn on the file plane. See `AGENTS.md` → *The file plane*.
- Keep `AGENTS.md` small. If you're about to add procedure to it, that procedure belongs in a skill.

## Updating

The skills, agents and scripts come from **[orion-skills](https://github.com/kyleisuncool/orion-skills)**. To update a vault, clone that repo, then:

```bash
./vendor.sh /path/to/your/vault          # --check shows what changed first
```

Change skills there, not in the vault. A local edit is overwritten on the next update.

