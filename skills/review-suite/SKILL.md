---
name: review-suite
description: Run selected review passes — over-engineering, dead-code, duplication, security, authz-coverage, docs-drift, error-handling — as parallel subagents over a diff, branch, or whole codebase, merged into one severity-coded HTML triage report with gh-issue export. Use when the user asks for any of these review types by name, wants a big feature/branch/PR/codebase swept for quality issues beyond a correctness review, or says "run the review suite".
---

# Review Suite

A series of focused review passes over one scope, each run as a read-only subagent in parallel, merged into a single triage report. Each pass lives in `passes/<name>.md` and is self-contained: a subagent needs nothing but its pass file, the scope, and the schema below.

Passes: `over-engineering` · `dead-code` · `duplication` · `security` · `authz-coverage` · `docs-drift` · `error-handling`.

## 1. Resolve the scope

One scope, resolved once, handed identically to every pass so all findings describe the same thing:

- **diff** — uncommitted work: `git diff HEAD` plus untracked files.
- **branch** — everything since trunk: `git diff <trunk>...HEAD` (three-dot, against the merge-base; trunk = the repo's default branch). A PR number resolves here too (`gh pr diff <n>`).
- **codebase** — all tracked files, optionally narrowed to a path the user named.

Infer the scope from what the user said ("this branch", "the whole repo", "PR 214"); ask once only when branch vs codebase is genuinely ambiguous. Before dispatching, prove the scope is real: the ref resolves (`git rev-parse`) and the diff or file list is non-empty. A bad ref fails here, not inside seven subagents.

Which passes: the ones the user named; "all" or an unqualified "review this" on a big target means all seven. Skip a pass whose subject matter is absent from the scope (no entry points → skip `authz-coverage`; no docs touched or claimed → skip `docs-drift`) and say so in the report header.

## 2. Dispatch the passes in parallel

One `general-purpose` subagent per selected pass, all Agent calls in a single message — they are read-only, so there are no conflicts. Each dispatch prompt carries everything the subagent will ever see:

- "Read your pass file first and follow it exactly: `<absolute path to this skill>/passes/<name>.md`."
- The scope: mode, the exact diff command or file list, and (for branch scope) the commit list.
- Repo orientation: where conventions and decisions live (`.claude/rules/`, `docs/adr/`, CLAUDE.md / AGENTS.md) — the pass file says what to do with them.
- The findings schema and severity rubric below, pasted in full.
- "Return ONLY the JSON array as your final message — it is data for the controller, not prose for a human." One pass is exempt by its own file: `authz-coverage` appends its coverage table after the array.

### Findings schema

```json
{
  "pass": "dead-code",
  "severity": "blocker | high | medium | low",
  "title": "one line",
  "location": "src/file.ts:42 (comma-separate multiple sites)",
  "evidence": "the quoted code, claim, or tool output that proves it",
  "recommendation": "the concrete fix — what to delete, extract, or add, and where",
  "effort": "S | M | L"
}
```

### Severity rubric

- **blocker** — exploitable, data-losing, or actively wrong in production behaviour right now.
- **high** — real ongoing cost: misleads every reader, hides bugs, or is a security weakness one precondition away from exploitable.
- **medium** — worth a ticket; the cost accumulates but nothing is on fire.
- **low** — polish.

## 3. Merge

Collect the arrays. Findings from two passes that describe the same underlying issue at the same location (`duplication` and `over-engineering` overlap often) collapse into one card: keep the higher severity, credit both passes. Order by severity, then by pass.

## 4. Verify the blockers and highs

Findings are candidates until they survive a skeptic. For every `blocker` and `high` finding,
dispatch one adversarial subagent - all in a single message, in parallel - briefed to **refute**
it: re-read the evidence in the repo, hunt for the reference, test, guard, or configuration that
would make the finding wrong, and return `confirmed`, `downgrade` (with the new severity), or
`drop`, with the reason. Apply the verdicts before building the report. `medium` and `low`
findings pass through unverified and the report labels them as such.

A weak finding costs more than a missing one - this gate is what lets the board be read at face
value.

## 5. Report

Write one self-contained triage board to `.claude/reports/<YYYY-MM-DD>-review-<scope-slug>.html`. Style it with the plugin's shared stylesheet, `<plugin root>/assets/report.css`, inlined into a `<style>` block so the file stays self-contained. Print the absolute path, then try to open it: `open` on macOS, `xdg-open` on Linux, `start ""` on Windows. Structure:

- **Header** — repo, scope (mode + ref or paths), date, per-pass finding counts with the
  found → confirmed tally from the verify stage, and any passes skipped with the reason. On a
  whole codebase before a launch, also the two checks this suite does not cover (see the end of
  this file).
- **One section per pass** — findings as cards: severity chip (colour carries severity), title, `file:line`, evidence in mono, recommendation. Each card gets a "file as issue" checkbox and an "afk" toggle. The `authz-coverage` section also renders its full coverage table, not just the gaps.
- **Footer** — an **Export** button that turns the checked cards into ready-to-run `gh issue create --title "…" --body "…"` commands in a copyable textarea (body = evidence + recommendation as markdown; add `--label afk` where toggled).

## 6. Offer to file issues

After presenting the report, offer to file the blocker/high findings (plus any others the user names) as GitHub issues directly — issue text is markdown, GitHub-bound. Apply the AFK test to each issue you file: clear spec, self-contained, verifiable by the repo's own check, no human decision, secret, deploy, or visual judgement needed. Label the ones that pass `afk` so an autonomous agent can pick them up.

## What this does not cover

The passes read code. They do not run the app, so a clean board leaves two checks open:

- **Rate limits.** The security pass reports a missing limit. Only requests against the running app prove that a limit works.
- **A pentest.** An app that holds customer data needs a human pentest before anyone calls it audited. A clean board does not replace one.
