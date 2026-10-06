---
name: orchestrate
description: Build a whole spec, or a set of issues, with parallel builder agents on one integration branch, then verify, review and hand over one pull request. Use when the user says "orchestrate", "build these issues", "implement this spec" or "run the spec", or names several issues to build together. For one issue, use implement.
---

# Orchestrate

You are the **orchestrator**. You never write feature code, except where the tool cannot start agents (see Build). You plan, grill, start **builders**, review and merge their work onto one **integration branch**, run the checks at the end, and hand the user one pull request.

The run has two phases. The labels on the issues to build decide where a run starts. For a spec, those are its child issues, not the spec issue itself:

| Label on the issues | What you do |
|---|---|
| Any issue is `needs-info` | Phase 1: grill the user on those issues, then hand over to a fresh session |
| Every issue is `ready-for-agent` | Phase 2: build, verify, review, open the pull request |

The input is a spec or a set of issue numbers (`orchestrate 41-48`, `orchestrate 41 43 47`, `orchestrate #40` for a spec issue). The tracker is whatever `.claude/tracker.md` names, or GitHub issues through `gh`.

## Start

1. **A spec with no issues yet:** run the `to-issues` skill on it. Its approval step is the one stop for the split: show the breakdown and wait for the user's OK before you publish.
2. **A spec that already has issues:** collect them, from its sub-issues or from the issues that name it as their parent.
3. **A set of loose issues:** use them as they are. Where they declare no blocking edges, the plan in phase 2 works out the order from the paths they touch.
4. **Read every issue:** body, comments, labels, blockers.
5. **Look for a run in progress:** a pull request from an `integrate/` branch whose body, or a comment, holds the run log for these issues (see "The run log"). If one exists, read it and continue from the state it records. For each issue the log shows as `building` or `failed`, start a new builder in `../<repo>-issue-<N>` and tell it to check out its existing branch instead of creating one.
6. Go to phase 1 if any issue is `needs-info`. Otherwise go to phase 2.

## Phase 1: grill

For each `needs-info` issue, in dependency order (blockers first):

1. Read the issue and the code it touches. List the decisions that are still open.
2. Grill the user with the `grill-me` discipline: one question at a time, each with your recommendation. When a choice is visual, show it with a mockup page from the `prototype` skill.
3. Make technical calls yourself. Ask the user about what a user of the product will see, and about scope.
4. When the issue has no open decision left, post one comment on it, headed `Orchestrate grill`, that lists each decision and its answer. Then change its label to `ready-for-agent`.

When every issue is `ready-for-agent`, stop. Tell the user to start a fresh session and paste the same line they typed, for example `/s8-playbook:orchestrate #40` or `/s8-playbook:orchestrate 41-48`. Phase 2 needs a clean context, and the issues now hold every answer.

## Phase 2: build

### 1. Plan

1. For each issue, guess the paths it will touch: read the issue, then look at the code. A guess is enough.
2. Make a rough plan in **waves**. An issue can start when its blockers are merged and no running issue touches the same paths.
3. Resolve the test mode once for the whole run, the way `implement` step 1 does, and state it with the signal it came from.
4. Ask the user how many builders to run at the same time. Suggest 3. Suggest 2 when each builder must run a dev server and a browser, because the machine can run short of memory.
5. Show the plan with the question:

   ```
   Plan (3 builders, tests on: AGENTS.md says test-first)
     Wave 1: #41 (lib/plan/*)   #43 (components/today/*)   #45 (app/admin/*)
     Wave 2: #42 (needs #41)    #44 (shares components/today/* with #43)
     Wave 3: #46 (needs #42, #44)
     Then: verify-feature, review-suite, fixes, pull request
   ```

   Wait for the answer. Do not start a builder before the user says yes.

### 2. Set up

1. Create the integration branch from the trunk: `integrate/<short-slug>`. Add an empty commit (`git commit --allow-empty -m "Start orchestrate run"`) and push it.
2. Open a **draft** pull request from the integration branch to the trunk. Put one `Closes #N` line per issue and the run log in its body. CI now runs on every merge you push.
3. Give each issue its own worktree beside the repo (`../<repo>-issue-<N>`) and its own dev server port, when its builder starts. Copy the untracked files the app needs to run, such as `.env.local`. The worktree stays until the hand-over, because the builder fixes its issue there later.

### 3. Build

Start one builder per issue on the **frontier**: the issues whose blockers are merged and whose paths no running builder holds. Start each builder as a background agent with the builder brief below. Never run more builders than the user chose. Count only builders that are building or fixing. A builder that reported done and waits does not take a slot. Where the tool cannot start agents, build the issues one after another yourself with the same brief.

You are each builder's parent in the sense of the `implement` skill. When a builder commits and pauses, run `/code-review low` against its branch, named explicitly, with `origin/integrate/<slug>` as the base, and relay the findings with `SendMessage`. The builder fixes them in place and sends its receipt.

When a builder asks a question:
- A technical question: answer it.
- A question about what a user will see: pause that issue, ask the user one question with two options and your recommendation, with a mockup when the choice is visual. Keep the other builders running.

When a builder sends its receipt:
1. Audit it the way `implement` step 4 does, with `origin/integrate/<slug>` in place of the trunk and without the `verify-feature` check: commits, diff boundary, clean tree, gate exit 0, tests for the named seams.
2. Merge its branch into the integration branch, one merge at a time: `git merge --no-ff`, run the gates, push. On a conflict, send the builder back to merge the integration branch into its branch and resolve it.
3. Update the run log.
4. Do not stop the builder. Its fixes come back to it later. Tell it to stop its dev server and browser.
5. Start the next issues the frontier allows.

### 4. Verify

When every issue is merged:

1. Start one `verify-feature` run per issue, each as a fresh agent that reads the `verify-feature` skill's `references/procedure.md`. Give each one its own worktree at the current integration commit and its own port. Its target is that issue's acceptance criteria against the combined code. Fix mode is off. Its report path is `.claude/reports/<YYYY-MM-DD>-verify-<slug>-<N>.html`. Run as many at the same time as the user chose builders.
2. Then start one more for the flows that cross issues: the places where two or more issues meet.
3. Audit each receipt the way `verify-feature` step 2 does. Do not read the reports. They embed screenshots.
4. Send each failure to the builder that built the issue. Send a cross-issue failure to the builder that owns the failing path, or to a fixer with the fixer brief. The builder merges the integration branch into its branch in its own worktree, fixes, and reports. Merge it as before.
5. Run only the failed checks again, with a fresh verifier in a worktree at the new integration commit. Stop after 2 rounds and record what is still failing.

### 5. Review

1. Run the `review-suite` skill yourself on the integration branch against the trunk. It starts its own review agents, so a builder cannot run it for you.
2. Send the `blocker` and `high` findings to one fresh fixer agent with the fixer brief below. Merge its branch.
3. List the `medium` and `low` findings in the final report. The `review-suite` report can turn any of them into issues.

### 6. Hand over

1. Post the run log as a comment on the pull request, headed `orchestrate run log`.
2. Write the pull request body with the `pr` skill. Keep the `Closes #N` lines.
3. Mark the pull request ready for review.
4. Write the final report to `.claude/reports/<YYYY-MM-DD>-orchestrate-<slug>.html`, one self-contained file with the plugin's `assets/report.css` inlined into a `<style>` block. It holds what was built, the verification results with a link to each `verify-feature` report, what still fails, the `review-suite` findings left, and every decision the builders made on their own.
5. Stop the builders. Remove every worktree the run made.
6. Give the user the pull request link and the report path. Tell them the two ways on: read the pull request and merge it themselves, or tell you to merge it. **Never merge into the trunk until the user says so in this session.** A `ready-for-agent` label does not count here, because the user granted it per issue, not for the whole set.

## The builder brief

Keep it short. Point to sources, do not paste them.

```
You are a builder in an orchestrate run.
Issue: #<N>. Integration branch: integrate/<slug>.
Worktree: <path>. Dev server port: <port>. Test mode: <on|off>, from <signal>.

1. In the worktree, create branch issue/<N>-<slug> from origin/integrate/<slug>.
2. Read docs/handoff.md if it exists, and the repo's CLAUDE.md or AGENTS.md.
3. Run the pickup-issue skill on #<N>, but skip its worktree step: the worktree and the
   branch above are already yours. If it finds an open decision, ask the orchestrator.
   Do not run grill-me.
4. Read the implement skill's references/procedure.md and follow it. The orchestrator is
   your parent: it runs code-review low after you commit and pause, and relays the findings.
   Skip step 4 (verify the running app). It runs later on the integration branch.
5. Other builders work in these paths right now: <paths>. Do not edit them.
   If you must, ask the orchestrator first.
6. Ask the orchestrator, not the user, when you are unsure.
7. Commit as you go. Before you send your receipt: git fetch, merge origin/integrate/<slug>
   into your branch, run the gate, push your branch.
8. Send the receipt from implement's procedure, plus: the paths you touched and every
   decision you made on your own.
```

## The fixer brief

For the review findings at the end. Same shape, no issue:

```
You are the fixer in an orchestrate run.
Integration branch: integrate/<slug>. Worktree: <path>. Dev server port: <port>.
Findings to fix: <the blocker and high findings, with file and line>.

1. In the worktree, create branch fix/<slug>-review from origin/integrate/<slug>.
2. Fix each finding. Ask the orchestrator when a fix would change behaviour a user sees.
3. Run the gate, commit and pause. The orchestrator runs code-review low against your branch,
   with origin/integrate/<slug> as the base, and relays the findings. Fix them.
4. Push your branch, and report: branch, last commit, what you fixed, what you left and why.
```

## The run log

Keep this table in the draft pull request body from the start, and update it on every change. It moves to a comment at the hand-over. It is how a new session picks up an interrupted run.

```
<!-- orchestrate run log -->
Builders: 3. Test mode: on. Integration branch: integrate/<slug>.

| Issue | Blocked by | Paths | State | Branch |
|---|---|---|---|---|
| #41 | - | lib/plan/* | merged | issue/41-plan-asof |
| #42 | #41 | lib/plan/* | building | issue/42-plan-chips |
| #43 | - | components/today/* | verified | issue/43-today-head |
```

States: `waiting`, `building`, `merged`, `verified`, `failed`, `fixed`.

## Rules

- Commit before you stop a builder. Stopping an agent can lose uncommitted work.
- Review a diff by its branch or pull request number. A review of a stale local trunk reports other builders' work as new.
- Stop a dev server by its port, never by its name. Before you trust a browser check, confirm the server on that port runs from the right worktree.
- When the trunk moves during a long run, merge it into the integration branch before the verification step.
- Run one git operation at a time on the integration branch. You own it. Builders never push to it.
