---
name: orion-clean-code
description: "How code gets written and reviewed under Orion — Robert C. Martin's Clean Code, kept to the judgment calls a linter can't make, with enforcement left to each project's own tools. Used by the ptah agent when building and the anubis agent when reviewing; also by the main session for any code change. Covers writing new code, working in an inherited codebase (match its conventions, never its defects; Boy Scout Rule on touched lines only), the tool gates to run, and the three-pass review: correctness and security, then design, then readability. Triggers on: write code, fix this, refactor, clean this up, review this code, review this diff, is this ready to merge."
---

# orion-clean-code — build it well, prove it with tools

**Who uses it:** `ptah` when building, `anubis` when reviewing, and the main session for any code change. If your harness has neither agent, the main session applies both halves — but a review is worth more from a session that didn't write the code.

**Two ideas carry everything else:**

1. **"The only way to go fast is to go well."** Code is read far more than it's written. Write for the next reader — who is as likely to be an agent as a person.
2. **Tools enforce; this file judges.** A long rule list gets treated as a guideline. So the project's linter, formatter, type checker and tests decide style and correctness; this file covers what they can't see.

---

## 1. Read before you write

- **Open the file, its callers and its tests first.** Match the naming, error handling and layout already in use.
- **Search for an existing helper, type or constant** before writing a new one. Re-implementing what exists is the most common failure of generated code.
- **Check the real signature** in source or docs before calling an API. Never invent a flag, method or package.
- **Chesterton's fence.** Code that looks pointless may be guarding something. Check `git blame` and the commit message before removing it; when still unsure, ask.

## 2. Writing — the floor, not gold-plating

| | Rule |
|---|---|
| **Names** | Say what it is or does: `discountRate`, not `d`. Specific and searchable — not `data`, `handler`, `manager`. Classes are nouns, functions verbs, one word per concept. Name magic numbers |
| **Functions** | Do one thing at one level of abstraction. Few parameters; no boolean flag arguments — write two functions. Change state *or* answer a question, not both. No hidden side effects |
| **Errors** | Raise, don't return status codes. Avoid returning or passing null. Messages carry the offending value and what was expected. **Never swallow an exception** — handle it, add context, or let it propagate |
| **Comments** | Explain *why* — a decision, a constraint, a warning — never *what*. Delete commented-out code. Leave history to the commit message |
| **Tests** | **Tests travel with the change.** A bug fix gets a test that fails without it. Fast, independent, repeatable. Never weaken or delete a failing test to go green — fix the cause, or say why the test is wrong. **Prove it with the suite, not by hand:** a check you'd run by hand (a curl, a client script, a done-when demo) becomes a test the suite runs, so every later run is free. A manual probe is only for what a test can't reach (a real host, a real phone), and is recorded as manual |
| **Config and secrets** | No hard-coded URLs, sizes or credentials. Config comes from the environment. **A secret never goes in code, a log, or a commit** |

## 3. Simplicity outranks cleverness — don't over-apply

Needless structure is itself a smell.

- **KISS** — the simplest design that passes the tests and reads clearly wins.
- **YAGNI** — build today's requirement. No hook, option or abstraction without a current caller.
- **DRY is about knowledge, not text.** Two look-alike blocks that change for different reasons aren't duplication. **Wait for the third occurrence** before extracting.
- **Convention over configuration.** The framework's standard way is the one the next reader already knows.
- **Abstract only at real seams** — I/O, external services, volatile policy. One implementation and no test that needs a fake → no interface.

## 4. Inherited code — surgery, not a rewrite

Much code work happens in codebases other people built. There:

- **Match its conventions, never its defects.** Naming case, layout and formatting are style; single-letter names, swallowed errors and status-code returns are defects, not style.
- **Boy Scout Rule on the lines you touch** — one or two safe improvements, mentioned in the report. **No drive-by rewrites** of code the task doesn't need.
- **Smallest correct change.** A reviewer should be able to hold the diff in their head. Before finishing, walk every changed line: *does the task need this line?* If not, revert it and list it as a follow-up.
- **Leave alone:** generated files, lock files, vendored code, unrelated modules.
- **Stop and ask before:** changing a public interface (signatures, exports, routes, database schema), a change whose behavior can't be verified because no tests cover it, or anything that has turned from a fix into a redesign.
- **Never describe the previous code as anyone's failure** in a commit, pull request, or anything a client may read. State what was found and what was done.

## 5. The gates — run the project's own tools

Before calling anything done, run whatever the project already has, and **say exactly what ran and what didn't.** Never claim a check passed that you didn't run.

| Stack | Typical gates (use the project's own config) |
|---|---|
| PHP / Laravel | `pint --test` · `phpstan analyse` · `phpunit` (or `php artisan test`) |
| JS / TS | `eslint` · `prettier --check` · `tsc --noEmit` · the test runner in `package.json` |
| Python | `ruff check` · `ruff format --check` · `mypy` if configured · `pytest` |
| Shell | `shellcheck` · `bash -n` |
| Any | The project's CI config is the authority on what "passing" means; run its steps locally where you can |

- **Never mute a linter, type checker or warning** to get green. Suppress narrowly, with the reason in a comment, only when there is no fix.
- **No gate, no new tooling on your own.** If a project has no linter or tests, say so and propose the smallest useful gate; adding a dependency is the owner's call.

### A check must be able to fail

**Every test, probe, smoke step or start-time check you add is shown failing on broken code before it is trusted passing on fixed code** — break the thing it guards (or run it on the code before the fix) and record the failing output beside the passing one. A gate that cannot fail is worse than none: it reports green on exactly the code it exists to catch.

The traps that produce fail-open gates:

| Trap | Why it never fails | Write instead |
|---|---|---|
| `check && echo ok` mid-script | Under `set -e`, a failure **left of `&&`** does not stop the script — it only skips the echo | `check \|\| { echo "why" >&2; exit 1; }` |
| `[ -n "$f" ] && grep -c … "$f" \|\| echo 0` | `grep -c` prints `0` **and** exits 1, so the fallback prints a second `0`; later arithmetic breaks and the line is skipped | `if …; then grep -c … \|\| true; else echo 0; fi` |
| A PHP script that boots Laravel, then throws | Laravel's exception handler catches it, prints it, and the process **exits 0** | `try { … } catch (\Throwable $e) { …; exit(<non-zero>); }`, or replace the handler; give success its own distinct code, not 0 |
| A curl status test that treats one failure code as "refused" | The same refusal gives different exit codes over http, TLS and HTTP/2 (52, 56, 92) — or a dead host looks like a refusal | Enumerate the codes for each transport, and require the success path to return what it should |
| A probe that only asserts the happy path | It passes whether the fix works or the feature is simply absent | Assert the before state (`LEAKS`, `BREAKS`, `STOPPED`) as well as the after |

A gate that passes on broken code is a **Blocker** in review (§6).

## 6. Review — three passes, in this order

A review with only one kind of finding skipped a pass.

1. **Correctness and security.** Bugs, error paths, resource leaks, concurrency. Every trust boundary: who can reach this, what they control, what it reaches — injection, authentication and authorization on every entry point, secrets, sensitive data in logs, unsafe deserialization, path traversal. Trace every flag combination end to end: a "dry run" that still sends mail is a bug. **Never let design comments crowd these out.**
2. **Design.** Section 3's simplicity rules, single responsibility, dependencies pointing at abstractions only at real seams, hidden side effects, flag arguments, long call chains reaching through objects (`a.getB().getC().do()`).
3. **Readability.** Names, magic numbers, comment quality, commented-out code, duplication.

**For each finding:** where (`file:line`), the principle or smell, why it will hurt, the fix. **End with a verdict:**

| | |
|---|---|
| **Blocker** | Wrong behavior, an exploitable hole, data loss, a secret in the repo, a test gate that passes on broken code |
| **Should-fix** | A design or test defect that makes the next change harder or riskier |
| **Nit** | Readability |

**The reviewer reports; it never fixes.** Findings go back to the builder (`ptah`, or whoever wrote the change). **An approval you don't believe is a defect you co-signed.**

## 7. The report

```
Scope: files and functions touched
Changed: one line per change — what and why
Boy Scout: the small cleanups made on touched lines, if any
Gates: each tool run, and its result · tools not available
Decisions: any design choice or rule deviation, in a sentence, so the owner can overrule it
Follow-ups: cleanups or risks seen and deliberately left alone
```

---

## Sources

Every rule above traces to these.

1. **Robert C. Martin, *Clean Code*** (2008) — names, functions, errors, comments, tests, the Boy Scout Rule.
2. **chadgrant/skills — `uncle-bob-clean-code`, `clean-code-review`** — <https://github.com/chadgrant/skills> — the three review passes, simplicity table, "don't over-apply", security lens, verdict levels. Primary model for §§2, 3, 6.
3. **patbaumgartner/clean-code-skill — `references/ai-assisted-coding.md`** — <https://github.com/patbaumgartner/clean-code-skill> — failure modes of generated code, the working agreement. Source for §§1, 4, 5.
4. **iliaal/ai-skills — `simplifying-code`, `php-laravel`** — <https://github.com/iliaal/ai-skills> — Chesterton's fence, pre-submit scope audit, stop conditions, Laravel gates.
5. **ertugrul-dmr/clean-code-skills · mdadul/agent-skills · btseee/clean-code-skills** — read for coverage; they agree with the above and add per-language rule lists left out here on purpose (see *Why short*).
6. **alexrusin, "How Uncle Bob Uses AI Coding Agents"** (2026-08-20) — <https://blog.alexrusin.com/uncle-bob-ai-coding-agents/> — *"He trimmed the prompt to the bare minimum and moved enforcement into tools that run afterward."*
7. **Fabio Akita, "Clean Code for AI Agents"** (2026-04-20) — <https://akitaonrails.com/en/2026/04/20/clean-code-for-ai-agents/> — why small units, distinctive names and why-comments matter more for agents.

**Why short.** The source packs run to dozens of rules and framework guides. Their own authors' advice is that a short opinionated file plus real tools beats a long one. Language detail lives in each project's linter config, not here.
