# Daily guide - watching and steering the work

The modules say *why*; this says *what to actually watch and do* while working. Dated on
purpose - written Aug 2026 against Claude Code as it is now
([*What the agent reads*](m2-what-the-agent-reads.md): rules expire).

## The context gauge

Everything the agent reads and does fills its working memory, and quality drops well before
it's full ([*The context window*](m1-the-context-window.md)). So:

- Keep the gauge visible (see *Setup guide*: the status line).
- `/context` shows what's eating the window when you're surprised.
- Our house habit: start wrapping up around 40%. That number is a habit, not a law - the module
  says so out loud - but a shared habit beats everyone improvising.

## Session hygiene

- **One task, one session.** `/clear` when you switch tasks - it wipes the conversation and
  keeps only the instructions files.
- **`/compact`** squeezes the current conversation into a summary. Use it only when you must
  continue mid-task; a fresh session with a written handoff is almost always better.
- **Ending a work session, on a repo with code:** [`handoff`](../skills/handoff/SKILL.md) compacts
  what only exists in the chat - the decisions nobody wrote down - into a note the next session
  opens with. It writes outside the repo, because the tracker and the commits already hold the
  rest. That is what makes killing a session free
  ([*The context window*](m1-the-context-window.md)).
- **Ending a work session, on a docs or planning repo:**
  [`update-docs`](../skills/update-docs/SKILL.md) instead. There is no tracker and no commit
  history carrying the decisions, so the note has to be durable: a ledger entry, a handoff in the
  repo, and any project doc the work actually drifted from.
- **Opening one:** [`start`](../skills/start/SKILL.md) reads all of them, in parallel, before it
  does anything else. A session that starts by guessing is a session that starts wrong.
- **Esc** stops the agent mid-action (Ctrl+C if Esc is ignoring you). Interrupt early - a
  wrong direction gets more expensive every minute you let it run.

## Building more than one ticket at a time

One ticket at a time is safe and slow. The set is built to go wider, and the thing that makes it
safe is not the agent, it is the **worktree** - a second full copy of the repo on its own branch.
Two sessions in one folder share a git index and corrupt each other.

1. **Ask which tickets are free.** [`to-issues`](../skills/to-issues/SKILL.md) already recorded
   what blocks what. The batch is the tickets with no blocker left that do not touch the same
   files. Two jobs on one file cannot run at the same time
   ([*Many agents on one job*](m8-many-agents-on-one-job.md)).
2. **One agent per ticket**, each running [`pickup-issue`](../skills/pickup-issue/SKILL.md) then
   [`implement`](../skills/implement/SKILL.md). `pickup-issue` makes the worktree and the branch.
   Ask the main session to start them, or open one terminal per worktree and run them yourself.
3. **The main session holds the map** and collects the branches as they come back.
4. **You review and merge.** Then the next batch.

**The reviewer is the limit, not the machine.** More agents at once sends more work to the same
person ([*Working as a team*](m7-teams.md)). Two or three is usually the honest number.

## Choosing a model

The menu changes every few months - as of Aug 2026 it runs from Fable 5 at the top through
Opus and Sonnet to Haiku 4.5. The logic outlives the menu, and it is the budget argument one level
up ([*The context window*](m1-the-context-window.md)):

- **Biggest model** where judgment concentrates: planning, review, hard debugging, anything
  you'd give your most senior person.
- **Middle** for everyday building.
- **Small and fast** for mechanical bulk work: renames, formatting, simple sweeps.
- Stuck in a loop of failed attempts? Switching *up* is usually cheaper than three more
  retries. `/model` switches mid-session.
- `/fast` is a different lever: same model, faster output, more tokens for the same work. Reach for
  it when your own waiting is the expensive part, not when the work needs more judgment.

## Red flags - signs the agent is off

Each of these means stop and steer, not "hope it works out":

| What you see | What it usually means | What to do |
|---|---|---|
| The change is far bigger than the task - a "small fix" arrives as 400 changed lines | It's doing more than asked: uninvited refactoring, scope creep | Stop. Ask for the *minimal* change ([*Deciding before building*](m3-deciding-before-building.md)) |
| "Everything works as expected", no evidence | A claim, not a check | Ask for the check that could have failed: the test run, the output ([*Verifying agent work*](m5-verifying-agent-work.md)) |
| It repeats work, forgets instructions, contradicts itself | Context rot - the session is past its best | Wrap up, write the handoff, start fresh ([*The context window*](m1-the-context-window.md)) |
| It delivered something quietly smaller than what was asked | Goal-shrinking under difficulty | Compare against the ticket, not against what got built ([*Verifying agent work*](m5-verifying-agent-work.md), Gate 3) |
| It edited the *test* until things passed | Gaming the check instead of fixing the code | Hard stop. Restore the test, reproduce the failure, then fix - [`implement`](../skills/implement/SKILL.md) is meant to report a failing check, never adjust it |
| Files far outside the task are changing | Scope drift | Stop; narrow the brief; keep it on its own branch so drift is cheap to discard ([*Working unattended*](m6-working-unattended.md)) |
| Long confident explanations, nothing actually run | Guessing, not measuring | "Run it and show me" - evidence, not theory ([*Verifying agent work*](m5-verifying-agent-work.md)) |
| A vague request came back with zero questions | It guessed your meaning and built the guess | Interview first next time - that's what [`grill-me`](../skills/grill-me/SKILL.md) is for (*Deciding before building*) |

## Finishing a change

The flow stops at the commit on purpose: the agent builds and commits on its branch, and a
*person* decides what happens next - unless the ticket carries a `ready-for-agent` label, which
lets [`implement`](../skills/implement/SKILL.md) merge on green ([*Working as a team*](m7-teams.md): you own what you hand in). From
there, two good paths:

- **Branch, then merge it yourself.** One feature branch per issue; when the work checks
  out, merge to main and delete the branch. Right when you're the only person who'd review
  it anyway - most solo and small-team work runs this way, including most of ours.
- **Branch, then a pull request.** The PR gives review a surface: a colleague reads the
  change, the checks show green on exactly what will merge, and the approval is on record.
  Right when several people share the code, or the project is big enough that "who checked
  this?" needs an answer.

[`orchestrate`](../skills/orchestrate/SKILL.md) always ends at a pull request, whatever the labels
say. Then you choose: read it and merge it yourself, or tell it to merge. Both are fine. The pull
request is there so that the choice is yours.

Pick per repo. The skills work with either - and with whatever your organisation's repo
settings enforce. Protected branches and required reviews beat any written convention
([*What the agent reads*](m2-what-the-agent-reads.md): a rule is a wish, an automatic check is a
wall). Whichever path: green only counts if the checks ran on the exact version being merged, not
the branch as it looked ten minutes ago ([*Verifying agent work*](m5-verifying-agent-work.md)).

## When to watch and when to walk away

[`to-issues`](../skills/to-issues/SKILL.md) puts one status label on every ticket it writes.
`needs-info` means a decision is still open, and it is the default, so work only runs unattended
when somebody decided everything on purpose. `ready-for-agent` means the ticket is fully decided
and an agent can build it without asking. [`orchestrate`](../skills/orchestrate/SKILL.md) grills
you on each `needs-info` ticket, flips it to `ready-for-agent`, then builds the whole set.

Working a `needs-info` ticket? Stay close and interrupt freely. Handed `ready-for-agent` work to
an agent? Let it run and judge the result at the end instead - interrupting unattended work defeats the point of
labelling it ([*Working unattended*](m6-working-unattended.md)). The label was the decision; make
it when you create the ticket, not in the moment.
