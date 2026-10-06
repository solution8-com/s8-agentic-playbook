# Setup guide - your machine and your repos

The modules say *why*. This says *how*, with the actual commands and file names. It is dated on
purpose - tools change, and this page changes with them ([*What the agent reads*](m2-what-the-agent-reads.md):
rules expire, and a stale one still looks like discipline).
Written Aug 2026 against Claude Code as it is now.

## The whole flow in one picture

```
idea ->  grill-me  ->  to-spec  ->  to-issues  ->  pickup-issue  ->  implement  ->  YOU review & merge
         (interview)   (write it   (tickets       (read ticket,     (build, test,     (unless the ticket
                        down)       + labels)      set up space)     verify, commit)    is ready-for-agent)
```

For a set of tickets, [`orchestrate`](../skills/orchestrate/SKILL.md) runs the pickup-issue and
implement steps for every ticket, in parallel, and ends at one pull request for you.

A suggestion, not a fixed sequence - skip what doesn't fit the task. Every step is a skill in the
`s8-playbook` plugin; install commands live in the plugin's README. Where the work touched a UI, an
endpoint or the database, [`implement`](../skills/implement/SKILL.md) runs
[`verify-feature`](../skills/verify-feature/SKILL.md) before it commits, and tells you where the
report landed.

## Your instructions files

Claude reads these automatically, and reads **all** of them - they stack, rather than one replacing
another:

1. `~/.claude/CLAUDE.md` - **global**: how *you* work, everywhere. Applies to every project.
2. The project's `CLAUDE.md` - what's true of *this* project: how to run it, what's unusual.
3. `CLAUDE.local.md` - personal overrides for one machine; not committed.

Global says how you work, the project file says what the project is, and neither repeats what the
code already shows ([*What the agent reads*](m2-what-the-agent-reads.md)). Keep each to one screen -
every line is read every session, and a stale line costs every session. Start nearly empty and grow
it from real corrections; [`setup-repo`](../skills/setup-repo/SKILL.md) seeds a lean one.

## What a well-set-up repo looks like

- `CLAUDE.md` - one screen, see *Your instructions files* above. `setup-repo` seeds it.
- `docs/` - only what the repo genuinely needs. **On a repo with code**, session state lives in
  the tracker and the git history, and [`handoff`](../skills/handoff/SKILL.md) writes the leftovers
  to a temp file rather than into the repo. **On a docs, training or planning repo** nothing else
  carries that state, so [`update-docs`](../skills/update-docs/SKILL.md) writes it here on purpose -
  a ledger, a handoff, and the project docs the work actually drifted from.
  [`start`](../skills/start/SKILL.md) reads all of them, in parallel, before it does anything else.
- `GLOSSARY.md` - a glossary, only if the project has real domain vocabulary.
- `.claude/` - settings, and `reports/` where [`verify-feature`](../skills/verify-feature/SKILL.md)
  and [`review-suite`](../skills/review-suite/SKILL.md) write their reports.
- **On a repo with code:** one command that runs the tests. The check step is only as good as what
  you give it to check against ([*The agentic loop*](m0-the-agentic-loop.md)). A repo with no code
  has nothing for a gate to check, and `setup-repo` skips it rather than inventing one.

## The status line - your context gauge

The context gauge is the one instrument you should always see
([*The context window*](m1-the-context-window.md): sessions get worse before they get full). Show at
least the **model** and **context usage**. Something like this is enough:

```
Opus 5 | myproject:main | ctx 138k/1.0M 13%
```

The raw pair matters more than the percentage. `138k/1.0M` tells you which model's window you are
spending, and those differ by a factor of five between models.

This repo ships an example you can use as it is: [`tools/statusline.sh`](../tools/statusline.sh).
Hand the file to Claude and ask it to wire it up. Its zones are the ones in the module. Config
lands in `~/.claude/settings.json` under `statusLine`.

## Hooks

A hook is a small program that runs automatically on every action
([*What the agent reads*](m2-what-the-agent-reads.md): a written rule is a wish, an automatic check
is a wall). Config: `settings.json`, under `"hooks"`.

- **Before an action** (`PreToolUse`): your script gets the action; exit code 2 *blocks* it
  and the reason is shown to the agent. Use for: dangerous commands, secrets, the live
  system.
- **After an edit** (`PostToolUse`): run the formatter, so style enforces itself and leaves
  your instructions file entirely.

There are a dozen or so other events - session start and end, prompt submit, file and config
changes - but start with one blocking hook for the single action that would hurt most, not a rule
system.

## The pipeline - same checks, twice

- The **commit gate** runs the checks locally before a change is saved; **CI** runs the same
  checks on the server for every branch and merge. `setup-repo` wires both and proves
  the gate actually blocks.
- Keep the two identical. A check that exists only in CI gets discovered late; one that
  exists only locally proves nothing to your team.
- Green counts on the exact version being merged - see *Daily guide*, "Finishing a change".

## Permissions - the everyday posture

Cycle modes with Shift+Tab. The sane default day
([*Working unattended*](m6-working-unattended.md)):

- **Accept edits** inside containment - the agent edits and runs freely *on its own branch*.
- **Auto** when you want it to get on with the work and pick its own way through the small
  decisions. The everyday mode once you trust the containment around it.
- **Plan mode** when you want it to look and think before touching anything.
- **Ask-everything** only while you're new and still reading the prompts.
- **Bypass everything** only in a sandbox you could delete without a thought.

## Worktrees - a room per agent

Think of one workshop with several benches. Everyone draws from the same stock of materials, but
each person works at their own bench, so nobody knocks over somebody else's half-finished piece.
A worktree is the bench.

Two sessions working in one checkout corrupt each other - they share one working state, and the
failures are ugly. A worktree gives each session its own folder and its own branch. The shared
stock is everything it does not separate: the same database, the same ports, the same running
services. Two ways to get one ([*Working unattended*](m6-working-unattended.md)):

- `claude --worktree` (or `-w`) starts the session in a fresh worktree with its own branch.
- In the flow, [`pickup-issue`](../skills/pickup-issue/SKILL.md) sets one up per issue - you don't
  have to think about it.

## Tools

MCPs, CLIs and plugins - what we actually recommend, how to install each, and how to review one
before it runs - live in `tools/README.md` in the plugin repo. One rule worth carrying here:
connect only what the day's work needs, because every connected tool eats context
([*The context window*](m1-the-context-window.md)).
