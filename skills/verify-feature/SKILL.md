---
name: verify-feature
description: Live runtime verification of a diff - drive the real app through UI flows, hit the endpoints, inspect the database, and prove behavioral side effects, compiled into one self-contained HTML evidence report with screenshots. Use whenever the user wants a feature verified, tested end-to-end, or proven working ("verify this", "make sure it works", "test the new UI", "can we merge this?" evidence), wants an adversarial walk of the matrices, wants screenshots of new UI in a skimmable report, or says "show me what it looks like" as a feature wraps up.
---

# Verify Feature

A verification run drives browsers, restarts stacks and reads logs. That is hundreds of tool
results this session never needs. **Dispatch the run to a subagent, then audit its receipt.** The
procedure lives in [`references/procedure.md`](references/procedure.md), for the subagent to read.

**Already a subagent?** Read `references/procedure.md` and run the verification yourself.

This skill is strictly runtime verification. Pair with `/code-review` for static analysis, and do
not fold a review pass in here. It measures and reports by default. It only touches code when the
user asks for fix mode, and the ordinary building still belongs to `implement`.

## 1. Brief

The agent cannot read this conversation, so the brief is the run. Every answer below is one cheap
command, or already in context:

- **Repo root** and **current branch**.
- **Target and trunk.** The argument works like `/code-review`'s: a commit, a range, a branch, or
  an issue number. With no argument the target is the branch's diff against its merge base with
  the trunk, or this session's own edits when the tree is dirty. Say which, and say what named
  the trunk, so a wrong guess is visible instead of silent.
- **Depth.** Default, or adversarial when the user asked for it ("adversarial", "walk the
  matrices", "try to break it"), or when the diff covers a whole feature rather than a patch. An
  adversarial run costs hours rather than minutes, so the dial belongs to the user. Say which you
  chose.
- **Fix mode.** Off, unless the user asked to fix until green. Then name the branch to commit on.
- **Report path**: `.claude/reports/<YYYY-MM-DD>-verify-<slug>.html`.

Dispatch one `general-purpose` agent, because the run needs the Playwright MCP tools, Bash and
file writes. Its prompt carries:

1. Read `<absolute path to this skill>/references/procedure.md` first, and follow it.
2. The resolved facts above.
3. **Intent**, what the diff is for, in your words. The agent reads the diff; the conversation
   that produced it is yours alone.
4. **Known-accepted deferrals** ruled on in this session, so the agent marks them `accepted`
   rather than failing them.
5. The project memory directory, for the `verify-recipe`, `verify-invariants` and
   `verify-contracts` memories.
6. Any scope the user set: surfaces to skip, fixtures to use, an environment already running.

## 2. Audit the receipt

The receipt claims a verdict per category, plus the fails, the blocked and accepted checks, State
left behind, any commits, and any memory written. Audit it against evidence outside the agent's
own words. **Done when every receipt claim is either confirmed or named as unverified in your
report.**

- `git status --short` shows a clean tree. Unexpected dirt means the cleanup ledger leaked.
- The report file exists, at a plausible size.
- All four categories are present. A missing category is a silent skip, which the procedure forbids.
- Spot-check one `pass` against its evidence block. A verdict with nothing behind it is a finding.
- After a fix-mode run: `git log --oneline <trunk>..HEAD` matches what it says it fixed,
  `git diff --stat <trunk>..HEAD` stayed inside the feature boundary, and the repo's own verify
  gate exits 0 when you re-run it yourself.

The report embeds base64 screenshots, so reading it costs more context than the run you
dispatched. Leave it on disk for the human and audit from the receipt. Correct the agent with
`SendMessage` rather than re-running. Its context is intact, so a correction is cheaper than a
second run.

## 3. Report

Verdict first: the report path, one line per category, every fail and blocked check, State left
behind, and anything your audit contradicted. After a fix-mode run, say which checks read
`fail -> fixed -> pass` rather than passing first time.

## Related skills

- **implement** - runs this for you when the diff touched UI, an endpoint or the database.
- **review-suite** - the static counterpart, for quality sweeps rather than runtime proof.
- **orchestrate** - runs this once per issue on the integration branch, after every builder has merged.
