---
name: implement
description: "Implement a piece of work based on a spec or set of tickets. Use when work arrives from /pickup-issue, or when the user asks to implement or build something already specced in a ticket."
---

# Implement

A build runs tests, typechecks and reads their output over and over. That is hundreds of tool
results this session never needs. **Dispatch the build to a subagent, then audit its receipt.**
The build procedure lives in [`references/procedure.md`](references/procedure.md), for the
subagent to read.

**Already a subagent?** Read `references/procedure.md` and build it yourself.

Three steps stay here, because the subagent cannot do them: the test mode, the review, and the
audit.

## 1. Resolve the test mode

The playbook builds test-first. Some organisations do not, so state the mode and the signal it
came from in one line, before the build starts, while a wrong call still costs nothing to correct.

First match wins:

1. `--tests` or `--no-tests` on the invocation.
2. A rule the repo or its org states about itself, in `AGENTS.md`, `CLAUDE.md` or `.claude/rules/`.
3. Nothing matched. Ask which mode applies, in one line.

**Read the mode from those signals alone.** The repo's own test files carry no signal in either
direction. A test-first repo can be one commit old with no tests written yet, and a repo that gave
up on testing carries orphaned test files that nobody maintains and that never pass. Counting
files gets both cases backwards.

Tests off does not mean no gate. It means typechecking and the live verification become the gate,
and the build procedure says so.

## 2. Brief

The subagent cannot read this conversation, so the brief is the plan. Dispatch one
`general-purpose` agent. It dispatches the verification leg to a subagent of its own, so it needs
the `Agent` tool. Its prompt carries:

1. Read `<absolute path to this skill>/references/procedure.md` first, and follow it.
2. **The plan in full**, written out rather than referenced: the ticket, the spec, or what this
   conversation agreed. Include the decisions already settled and the alternatives already
   rejected, so the subagent builds them rather than reopening them.
3. What `pickup-issue` confirmed and contradicted against the live tree, with the `file:line`
   for each.
4. The test mode, and the signal it came from.
5. Repo root, current branch, the worktree path where the work lives, and the trunk.
6. The gate command, when this session already knows it.
7. Known-accepted deferrals, so the verification leg marks them `accepted` rather than failing them.
8. The project memory directory.
9. Any scope the user set: files to leave alone, surfaces to skip.

## 3. Relay the review

The subagent commits, reports the SHA and the seams it tested, and stops.

Run `/code-review low` and name the target explicitly: the branch or worktree path where the
work lives. Review subagents inherit the session's working directory, not the builder's
worktree, so an untargeted review can pass without ever seeing the diff. A review that saw no
diff is not a review.

Do not run a deep review here. An agent reviewing code it just wrote is biased toward its own
solution, so the deep pass belongs in a fresh session against a fixed point.

Relay the findings with `SendMessage`. The subagent's context is intact, so it fixes them in
place, re-runs the gate, runs the verification, and returns its receipt.

## 4. Audit the receipt

Audit it against evidence outside the subagent's own words. **Done when every receipt claim is
either confirmed or named as unverified in your report.**

- `git log --oneline <trunk>..HEAD` matches the commits it claims.
- `git diff --stat <trunk>..HEAD` stayed inside the plan's boundary. A file well outside it is a
  finding for the user.
- `git status --short` shows a clean tree.
- Re-run the gate yourself and confirm exit 0.
- Tests on: the new tests exist and cover the seams the subagent named before it started.
- Where the diff touched UI, an endpoint or the database, the `verify-feature` report exists at
  the path the receipt names. Do not read the report, it embeds screenshots. Audit from the receipt.

Correct the subagent with `SendMessage` rather than starting a second run. The verifier is the
build subagent's own subagent, so a correction to the verification goes through the build
subagent, never to the verifier directly.

## 5. Report

The branch first, then the commits, the gate command and its exit code, what the review fixed,
and the `verify-feature` report path where there is one. Then anything your audit contradicted,
and anything the subagent left out.

Then stop: hand the branch to the user to review and merge. Do not merge it yourself unless the
user has said to for this work. An issue labelled `ready-for-agent` counts as that permission.
