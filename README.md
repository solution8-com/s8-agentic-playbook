# S8 Agentic Playbook

> Solution8's curated setup for building with coding agents.

## What this is

A working setup for building with coding agents: a set of Claude Code skills, a short list
of tools worth having, and modules that teach the thinking behind both.

It exists because the tool is the easy part. Claude Code installs in a minute. What takes months is
working out how to get reliable results from it - what to check, what to automate, where a person
still has to look, and how a whole team does that one way instead of eight. This repo is that
working-out, already done.

Most people reach for a newer model when they want better results. The model matters, but so does
everything around it: the tools it can reach, what it reads first, how its work gets checked. NVIDIA
took Claude Opus 5 from a 30% baseline to a perfect score on ARC-AGI-3, a long-horizon agent
benchmark, [without changing the model at all](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/) -
the whole gain came from the harness they built around it. That surrounding machinery is the part
you control, and it is what this repo is about.

### Where this runs

Claude Code, in a terminal. Claude Code is not the Claude chat app: it reads
your files, runs your commands and works in a loop, which is what everything here assumes. We use
the terminal version because that is where the harness is most open to you. Hooks, settings files,
skills, the CLI tools it reaches for, a worktree per agent, the status line. That is the half you
own, and this repo is almost entirely about shaping it.

### Who it is for

Technical teams, and anyone who wants to learn this properly. You need to be
comfortable with a terminal and git. You do not need any experience with agents.

### What it asks of you

Nothing. The Main Flow below is the one that makes sense most of the
time, and nobody is signed up to it. Skills are tools: reach for the ones that help and leave the rest.

## What is in it

| Part | Where | What it gives you |
|---|---|---|
| **Skills** | [`skills/`](./skills/) | 23 ready-made ways of working, installed as one plugin that keeps itself up to date |
| **Tools** | [`tools/`](./tools/README.md) | The CLIs and MCP servers worth having, with setup notes, plus a status line you can adopt as your own. None of it is required |
| **Modules** | [`modules/`](./modules/) | Nine lessons on the principles, plus two hands-on guides. Read these to understand why the skills are shaped the way they are |

We gather from a wide range of verified sources - Anthropic's own engineering writing, independent
research, and practitioners working in the open - and distil it against our own experience.
[SOURCES.md](./modules/SOURCES.md) lists the reading behind the modules and why each source is worth
trusting. Some of the skills began as [Matt Pocock's](https://github.com/mattpocock/skills) and have
been developed further; others are our own. [ATTRIBUTION.md](./ATTRIBUTION.md) says which is which,
and names the upstream version we vendored from.

## Install

### The short way

Paste this into any Claude Code session and let it do the work:

```
Install the Solution8 agentic playbook for me. It lives at
github.com/solution8-com/s8-agentic-playbook.

Add it as a plugin marketplace, install the s8-playbook plugin, then ask me to
run /reload-plugins. Once that is done, use the onboarding skill to set it up
alongside whatever Claude setup I already have.
```

Claude runs the install itself. You type one thing, `/reload-plugins`, when it asks - skills only
attach at that point, so nothing works until you do. Onboarding then looks at what you already
have and walks you through the rest.

### By hand

```
/plugin marketplace add solution8-com/s8-agentic-playbook
/plugin install s8-playbook@solution8
```

The repo is private for now, so this works once you have been given access to it. Installing ties
you to this repo - no reinstall, no version pinning.

**It keeps itself up to date.** New skills and fixes arrive without anyone running a command. To
pull one immediately, `/plugin marketplace update solution8`.

**What an update cannot do is reach a session that is already open.** Skills attach when a session
starts, so restart or run `/reload-plugins` to pick one up. And treat the reload's own summary as
decoration: it has been seen reporting "0 skills" while attaching one. Check the skill list, not
the message.

## Getting started

Once the plugin is in:

1. **Let onboarding run.** If you used the paste-block above it starts on its own. It looks at
   the setup you already have, tells you what collides with what, and shows you where to begin.
2. **Type `/suggest` when you are not sure what to reach for.** Say it however you would say it
   out loud - a whole messy sentence, not a keyword. It works out what you are doing and points
   you at the skill that fits, with one line on why - and offers to run it where one skill is
   clearly the right one.

   ```
   /suggest i wanna start building a finance tracker
   /suggest how do i use context management
   ```

   The first routes you - a new product runs for weeks, so `wayfinder` rather than `grill-me`.
   The second is not a routing question at all, and it says so: it answers from the modules
   instead, because most work needs no skill.
3. **Run `gh auth login` if you have not.** Seven skills drive GitHub directly - issues,
   branches and pull requests - so `pickup-issue`, `wayfinder`, `review-suite` and
   `verify-feature` need it to do their job. `onboarding` and `suggest` both check it for you.
4. **Read [`m0-the-agentic-loop`](./modules/m0-the-agentic-loop.md).** Ten minutes, and the rest of
   the set makes sense afterwards.
5. **Run one real piece of work through the Main Flow.** Pick something small you were going to do
   anyway. The flow pays off more on the second run than the first, because by then you have
   stopped reading it and started recognising it.
6. **Wire a project up properly when you want to.** `setup-repo` handles code and non-code repos
   alike - on a code project it sets up the stack, the commit gate and CI, then proves the gate
   blocks.

None of this has to be adopted at once. Most people stop after step 2 and come back to the rest
when they hit something that needs it.

## The skills, by group

| Group | Skills | What it's for |
|---|---|---|
| [Project setup](#project-setup) | 2 | Getting set up, and standing up a project the rest of this can work in |
| [Main Flow](#main-flow) | 5 | Idea to code that landed |
| [Shape](#shape) | 4 | Working out what to build, before there is a spec to write |
| [Utilities](#utilities) | 6 | Reached for mid-work, in whatever order the work demands |
| [Context](#context) | 3 | Opening and closing a session, so the next one starts where this one stopped |
| [Misc](#misc) | 3 | Occasional, and nobody has to use them |

## Project setup

> Getting set up, and standing up a project the rest of this can work in.

- **[`onboarding`](./skills/onboarding/SKILL.md)** - run once, right after install. Looks at the Claude setup you already have,
  says what will collide with the playbook and why, changes nothing without your say-so, and shows
  you where to start.
- **[`setup-repo`](./skills/setup-repo/SKILL.md)** - create a repo or adopt an existing one, then wire what it actually needs.
  Every project gets a `CLAUDE.md`, issue labels and somewhere for tickets. Projects with code also
  get the stack, the dev environment, a commit gate proven to block, and the same checks in CI.

## Main Flow

> The usual path to code that landed. You join it wherever your work already is.

```
grill-me  ->  to-spec  ->  to-issues  ->  pickup-issue  ->  implement
```

Nothing written down yet? Start at the left. A spec already written? Start at `to-issues`. An issue
someone else assigned you? Start at `pickup-issue` - and if its decisions were never settled,
`pickup-issue` sends you back to `grill-me` before anything gets built. Nobody picks a flow; the
work already says where you are.

- **[`grill-me`](./skills/grill-me/SKILL.md)** - a relentless interview that sharpens a plan until the open decisions are settled.
  It gets you and your coding agent on the same page about exactly what you want built, before
  anything is built.
- **[`to-spec`](./skills/to-spec/SKILL.md)** - turn the conversation into a durable spec.
- **[`to-issues`](./skills/to-issues/SKILL.md)** - break a spec into tracer-bullet vertical slices, published as GitHub issues with
  their blocking edges and an `afk` (safe to run unattended) / `hitl` (human in the loop - the
  default) label.
- **[`pickup-issue`](./skills/pickup-issue/SKILL.md)** - read one issue and its comments, brief you in plain language before it
  touches the code, check the issue's claims against the live tree, sort out the worktree, then
  work out whether the issue is settled enough to build or needs a grill first. Writes no code and
  no plan of its own.
- **[`implement`](./skills/implement/SKILL.md)** - build what was already decided. It never reopens the plan, which is what
  separates it from typing "build this" at a fresh agent.

Review has no skill of its own here, because Claude Code ships `/code-review`. Use
`/code-review low` for a small change that matters, and at the end of a work session run the full
pass over the diff in a fresh session. `review-suite` below is for a broad quality sweep.

`implement` runs `verify-feature` for you. When it commits, it looks at what the diff touched -
UI, an endpoint, the database - and proves the behaviour before it hands the branch back.
Reach for it yourself on a change that did not come through the flow.

## Shape

> For when you do not know enough yet to write a spec.

- **[`wayfinder`](./skills/wayfinder/SKILL.md)** - charts a map of the decisions a big piece of work needs, then works one per
  session. Start here on anything that runs for weeks. It takes over the research and prototyping
  itself.
- **[`prototype`](./skills/prototype/SKILL.md)** - build a throwaway to answer one design question before committing.
- **[`research`](./skills/research/SKILL.md)** - chase a question back to primary sources in a background agent, written up with
  citations.
- **[`visual-spec`](./skills/visual-spec/SKILL.md)** - render a spec as a self-contained HTML overview for a human to read.

Claude Code also ships `design`, so there is nothing for us to add there. It opens an editable
canvas you move things around on directly, and because it runs inside the repo the layout arrives
with the code it has to sit on, instead of a screenshot you then have to explain. Reach for it when
a lot is still undefined. `prototype` is the better tool once the direction is settled and you want
two or three variants built to compare.

## Utilities

> Reached for mid-work, in whatever order the work demands.

- **[`improve-codebase-architecture`](./skills/improve-codebase-architecture/SKILL.md)** - find shallow modules worth deepening. A periodic sweep,
  scoped to an area you name or to the hot spots in recent commit history; it has nothing useful to
  say about a single issue.
- **[`diagnosing-bugs`](./skills/diagnosing-bugs/SKILL.md)** - disciplined root-cause debugging, reproduce first, fix second.
- **[`wait-what`](./skills/wait-what/SKILL.md)** - re-pitch the last message in plain language when it did not land.
- **[`verify-feature`](./skills/verify-feature/SKILL.md)** - drive the real app through the diff: UI flows, endpoints, database and
  behavioral side effects, handed back as one self-contained HTML report with screenshots.
  `implement` runs it for you when the diff touched UI, an endpoint or the database. Ask for an
  adversarial run when a whole feature wraps up, and it walks the state, permission and input
  matrices instead of the happy path.
- **[`review-suite`](./skills/review-suite/SKILL.md)** - seven quality passes (dead code, duplication, security, authz, docs drift,
  error handling, over-engineering) run in parallel, merged into one triage board with issue export.
  Run it when a big feature or branch wraps up.
- **[`tdd`](./skills/tdd/SKILL.md)** - the red-green loop, and what makes a test worth keeping. `implement` calls it at
  pre-agreed seams; you can also invoke it yourself.

## Misc

> Occasional, and nobody has to use them.

- **[`suggest`](./skills/suggest/SKILL.md)** - not sure which skill fits? Routes your situation to the right one, with a line
  on why. Checks `gh auth status` first, since much of the
  flow runs through GitHub.
- **[`wizard`](./skills/wizard/SKILL.md)** - generate a script that walks a human through the steps only they can do:
  provisioning, credentials, one-off migrations. Secrets never touch the model.
- **[`to-questionnaire`](./skills/to-questionnaire/SKILL.md)** - turn the questions someone else has to answer into a fillable form.

## Context

> Opening and closing a session, so the next one starts where this one stopped.

A session is throwaway; what it learned is not. These three are how the knowledge outlives the
session - which is what makes ending a tired one cost nothing. *The context window* is the module
behind them.

- **[`start`](./skills/start/SKILL.md)** - the read side, and the one you use most. Opens a session by reading the handoff,
  the ledger and any domain glossary before doing anything else, so a fresh session picks up where
  the last one stopped. It reads all of them, in parallel, every time - nothing here is
  last-writer-wins.
- **[`update-docs`](./skills/update-docs/SKILL.md)** - the write side **on a docs, training or planning repo**, where the thinking
  is the deliverable and nothing else holds the state. There is no tracker and no git history
  carrying the decisions, so it writes durable ones: a ledger entry, `docs/handoff.md`, and only
  those project docs the work actually drifted from.
- **[`handoff`](./skills/handoff/SKILL.md)** - the write side **on a repo with code**, for when a decision gets made in one
  session and has to be picked up in another. Compacts the session into a note a fresh one can pick
  up from, written to a temp file rather than into the repo: the tracker and the git history are
  already the project's memory, and this covers only what they do not hold.

Which write side you want is decided by the repo, not by preference - a stack manifest present
means code. `suggest` reads it the same way.

## Reports

> Every report looks the same on any machine.

`verify-feature`, `review-suite`, `visual-spec` and `improve-codebase-architecture` write
self-contained HTML to `.claude/reports/`, styled with `assets/report.css`. `setup-repo` adds
that folder to `.gitignore`.

## Modules

> The teaching layer: the principles behind the skills, one lesson doc per concept.

Nine lesson docs in [`modules/`](./modules), ordered the way the agentic loop runs - context,
action, verification - then the operating topics. Each one teaches a single concept in plain words:
why it matters, and what you can do about it. These are fresh drafts and still under review.
[SOURCES.md](./modules/SOURCES.md) collects the reading behind all of them.

1. [The agentic loop](./modules/m0-the-agentic-loop.md) - what an agentic tool does, and why you are part of the loop.
2. [The context window](./modules/m1-the-context-window.md) - the agent's working memory is a budget, and sessions get worse before they get full.
3. [What the agent reads](./modules/m2-what-the-agent-reads.md) - instruction files, the codebase itself, and checks that enforce instead of hope.
4. [Deciding before building](./modules/m3-deciding-before-building.md) - shared vision beats clever wording; agree what done looks like first.
5. [Handing work off](./modules/m4-handing-work-off.md) - delegation, scouts, and briefs that stand alone.
6. [Verifying agent work](./modules/m5-verifying-agent-work.md) - the three gates between "done" and done.
7. [Working unattended](./modules/m6-working-unattended.md) - containment beats supervision; when work can safely run alone.
8. [Working as a team](./modules/m7-teams.md) - a shared setup beats everyone improvising.
9. [Many agents on one job](./modules/m8-many-agents-on-one-job.md) - rounds, lanes, and why a report has to carry its evidence.

Two hands-on guides sit alongside them, both dated on purpose because the tooling moves under
them:

- [Setup guide - your machine and your repos](./modules/guide-1-setup.md) - the commands and file
  names behind the lessons above.
- [Daily guide - watching and steering the work](./modules/guide-2-daily.md) - what to watch and what
  to do while the work is running.

## Tools

> What to install alongside the skills.

[tools/](./tools/README.md) covers the MCPs, CLIs and plugins worth having - including the three
things the skills need (`gh`, Playwright MCP, Python 3) and which MCPs are worth keeping switched
off until you need them.

| Tool | Kind | What it's for |
|---|---|---|
| [Context7](./tools/README.md#context7) | MCP | Current library documentation |
| [Playwright](./tools/README.md#playwright) | MCP | A real browser to drive |
| [Supabase](./tools/README.md#supabase) | MCP | Your database, queryable |
| [n8n](./tools/README.md#n8n) | MCP | Automations, and their failures |
| [Vercel](./tools/README.md#vercel) | MCP | Deploys, build logs, preview URLs |
| [Miro](./tools/README.md#miro) | MCP | Boards read and written in place |
| [GitHub](./tools/README.md#github-gh) | CLI | Issues, PRs and CI from the terminal |
| [Azure](./tools/README.md#azure-az) | CLI | Azure resources and deployments |
| [Postgres](./tools/README.md#postgres-psql) | CLI | Direct database queries |
| [context-mode](./tools/README.md#context-mode) | Plugin + MCP | Big output kept out of the conversation |
| [Caveman](./tools/README.md#caveman) | Plugin | Shorter replies |
| [Language servers](./tools/README.md#language-servers) | Plugin | Real types instead of grep |

## License

MIT - see [LICENSE](./LICENSE). Upstream notices are in [ATTRIBUTION.md](./ATTRIBUTION.md).
