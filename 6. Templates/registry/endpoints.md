# Endpoints — every inbox and outbox, and the working roots

**Optional.** To turn the file plane on, copy `6. Templates/registry/` to `registry/` at the vault root and edit the rows to match your disk. Without a `registry/` folder, the skills skip the file plane. `orion-ingest` (endpoint mode), `orion-deliver` and `orion-lint` check 19 read it through the scripts in `.agents/scripts/`. **Adding a service is adding a row.**

## Rules the scripts rely on

- **Location** is one backticked path, `~`-relative.
- **Direction** is `in`, `out`, or `landing` (an inbox with no `processed/`: it ends every ingest empty).
- **Processed** is the box's own `processed/YYYY-MM/`, or `—` for a landing strip.
- **A box keeps one shape:** `<box>/` holds only what hasn't been looked at (in) or finished things that haven't gone (out); `<box>/processed/YYYY-MM/` holds what has. Never a workspace.
- ⛔ **Nothing goes in an outbox unless the owner says to put it there.**
- A path on another machine is written `<machine>:~/path` and is never checked on this one. Rows whose location doesn't exist on this machine are skipped.

## Endpoints

| Endpoint | Location | Service | Direction | Use when | Who else can see it | Processed |
|---|---|---|---|---|---|---|
| `os-in` | `~/Inbox` | local disk | in | A file arrived: a download, a USB stick, an export | no one | `processed/YYYY-MM/` |
| `os-out` | `~/Outbox` | local disk | out | A finished deliverable is leaving by hand | no one until handed off | `processed/YYYY-MM/` |
| `dl` | `~/Downloads` | browser | landing | Browser downloads | — | — |

## Roots

One folder per workstream under `work`, named `YYYY-MM-DD-<ID> <Workstream Name>/`, dated the day its first material arrived. Closed workstreams move to `archive`.

| Root | Location | Holds |
|---|---|---|
| `work` | `~/Documents` | Live workstream folders |
| `archive` | `~/Documents/_archive` | Closed workstream folders |
