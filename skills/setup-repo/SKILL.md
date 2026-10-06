---
name: setup-repo
description: Set up a project repo - create it or adopt an existing one, then wire what the project actually needs. Use when standing up a new project, or bringing an existing one under the playbook.
---

# Setup Repo

## Overview

Gets a project ready to work in. It looks first, because the situations need different things: a
new project has to be created, an existing one has to be understood, and a project with no code in
it needs far less than one with code.

**Every project gets** a repo, a slim `CLAUDE.md`, the `afk`/`hitl` issue labels, and somewhere for
tickets to live.

**Projects with code also get** a stack, a dev environment, a commit gate and CI.

A documentation, training or planning repo has no stack and no tests, so a commit gate on it is
friction with nothing behind it. That is the whole difference. It is not a lesser setup - tickets
matter there as much as anywhere, because `wayfinder` puts decision tickets on the tracker and a
decision is not code.

## Step 0: look before you act

Establish which situation you are in before changing anything:

- `git rev-parse --is-inside-work-tree` - is this a repo at all?
- Manifests: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`,
  `*.csproj`, `pom.xml`, `Gemfile`.
- Existing tooling: a lockfile, `.pre-commit-config.yaml`, `.husky/`, workflows under
  `.github/workflows/`, a configured formatter or linter.

No manifest and no repo means **new project**. Anything already there means **existing
project**, and the job changes from building to understanding.

**Then settle whether it has code**, because that decides how much of this runs. On an existing
repo, read it off the manifests above - one present means code, and asking about something visible
on disk wastes the user's attention. On a new, empty project there is nothing to read, so ask - in
the same breath as the name and the owner, never as a separate interview.

## New project

### 1. Name it

**Ask the user what the repo should be called and which owner (account or org) it belongs
under.** Do not guess and do not derive it from a convention - naming schemes are the owner's
business, and renaming a repo later breaks every clone and remote. This is the cheapest possible
moment to be sure.

### 2. Create it

Create the repository under the correct owner, with an empty first commit so the default
branch exists. Seed only:

| Seeded | Why |
|---|---|
| Issue labels: `afk` `hitl` | `to-issues` stamps one on every slice: can a person walk away while this is built? `afk` for small, decision-free work, `hitl` where a decision is still plausible. Nothing gates on them. Type and severity are deliberately absent - GitHub gives you those and nothing here read them |
| A license | One file, and awkward to remember later |
| The default branch | Nothing else works without it |

Not seeded: a starter `.github/` directory (an empty template folder is clutter the agent
reads past every session - add it the day a real PR template exists), and not branch
protection (those rules need per-project thought, and a rule set too tight silently blocks the
agent's own pull requests).

### 3. Take the stack from the plan

**Code projects only.** A project with no code skips to `CLAUDE.md` and the tracker.

By the time this runs the stack is usually already settled - `grill-me` or `wayfinder` decided it,
or the user named it in the same breath as the repo. Read it off what you have and confirm in one
line rather than re-asking.

Ask only about what is genuinely still open, and only where the answer changes what you build. The
two that are rarely inferable are the **package manager** (`bun` vs `npm`) and
**what kind of thing this is** - CLI, library, web service - because that shapes the layout.
Everything else: take the ecosystem standard and say which one you took.

**Match the question to the person** - someone who names a stack gets answered in those terms;
someone who does not know gets a recommendation they can take without bluffing.

### 4. Scaffold

**Code projects only.**

1. `git init` if needed; a language-appropriate `.gitignore`, plus `.claude/reports/` so generated reports never get committed.
2. The minimal layout and manifest for the chosen stack.
3. Install dependencies with the project's package manager.
4. A formatter, a linter or type-checker, and a test runner - plus **one trivial passing
   test**, so the suite is green from the first commit and the gate has something to run.
5. The commit gate (below).
6. An initial commit.

## Existing project

### 1. Identify the stack

Read the manifests and lockfiles. Do not assume - a repo with a `package.json` may still be
driven by a Makefile.

### 2. Install the dependencies

With the project's own package manager, read off the lockfile. Note anything else the repo
says it needs to run: required runtime versions, env vars (`.env.example`), services
(`docker-compose.yml`, a README "Getting started"). Nothing in step 3 can run until this has.

### 3. Find the real commands, then run them

Look for what the project actually uses for format, lint, type-check, test and build:
`package.json` scripts, a `Makefile` or `Taskfile`, `pyproject.toml`, `tox.ini`, the CI
workflows.

**Then run each one and confirm it works.** This is the step that matters. Config rots: a repo
can claim `npm test` works when it has not for a year, and a command taken on trust puts
everything built on top of it on a broken foundation. A documented command is a claim, not
evidence.

### 4. Fill the gaps

If a formatter, linter or test gate is missing, propose adding it - but **match what is already
there** rather than imposing a different stack on someone else's codebase.

**A missing test runner and missing tests are two different findings.** Installing a runner is
cheap and changes no application code, so propose it: without one, the next slice that wants a
test has nowhere to put it. **On an existing codebase, never write a trivial passing test to make
the gate look armed.** An empty suite reporting green reads as coverage over real code, which is
worse than no suite. Where the runner fails on an empty suite, pass the flag that permits one.

Uncovered code is a **finding for the report**, not a job. Do not open a coverage project, and do
not write tests outside the slice someone is changing.

## The commit gate (code projects, both paths)

Skip this entirely where there is no code. There is nothing for a gate to check, and a linter
standing between someone and their own notes is friction that buys nothing.

The mechanism differs per ecosystem, the principle does not: run the fast deterministic checks
on every commit, block on failure, and auto-format so all output meets the project's style.

1. **Use the project's native mechanism** - the `pre-commit` framework, Husky with lint-staged,
   a plain git hook, whatever fits.
2. **Order the checks cheapest first**: format, then lint and type-check, then the fast test
   subset. Keep it quick; slow and end-to-end tests belong in CI.
3. **Scan for secrets on every commit.** Add `gitleaks` to the gate: the `gitleaks` hook in the
   `pre-commit` framework, or `gitleaks git --pre-commit --staged` in a plain hook. A secret
   stays in the git history after you delete it, so the gate must stop it before the commit
   exists. Whether a commit holds a secret is a yes-or-no question, so a tool answers it, not the agent.
4. **Mirror the same checks in CI.** A local gate can be walked past with `git commit
   --no-verify`, so a gate that exists only locally is a suggestion. CI is where it becomes a
   rule. Every project gets this; on a small one it is a single workflow running the same commands,
   nothing more.

   **This step is load-bearing, not hygiene.** Work merges once its checks are
   green, so CI is the last thing standing between a change and trunk. A project whose CI
   runs nothing will merge anything.

   **CI also scans the dependencies.** Run `osv-scanner` over the lockfiles. It reads every
   ecosystem, not only JavaScript. A dependency can become vulnerable with no change to your
   code, so this check belongs in CI and not in the commit gate.

   **On an existing repo, never edit a running CI workflow on your own.** Breaking one costs a
   failed release, not a failed check. Read it, say what it covers, and propose the missing steps
   as a diff the user approves. Add a new workflow only where none exists.

### Prove it blocks

**Do not report the gate as working until you have watched it work.** Make a commit that
violates a rule and confirm it is rejected. Then make a clean one and confirm it passes.
Commit a dummy key too, and confirm that `gitleaks` rejects it.

A misconfigured gate is indistinguishable from a working one right up until something broken
sails through months later. Installing it is not evidence; watching it block is.

## Seed `CLAUDE.md` (every project)

Write a slim `CLAUDE.md` at the repo root. Other skills read it as the conventions file -
`pickup-issue` sessions read it at the head of every issue, and the built-in `/code-review`
checks the diff against it - so
a repo without one leaves both of them guessing.

Do this last, because by now you know things that were only assumptions at the start. Record
what you **verified**, not what you intended:

| Include | Why |
|---|---|
| The stack, in one line | The first thing any session needs. Where there is no code, say what the repo is for instead |
| The real commands for test, lint, type-check, build | You just ran them. These are evidence, not claims. Code projects only |
| How the commit gate works and what it runs | So nobody re-derives it or works around it. Code projects only |
| Repo-specific conventions that are not guessable from the code | The only part a human has to supply |

**`CONTEXT.md` is deliberately not seeded.** Several skills read the domain glossary, but an
empty one is clutter the agent reads past every session, and the vocabulary does not exist yet on
day one. Create it the first time a term is worth recording.

**Slim pointer, not a fat template.** Every line here is re-read at the start of every session
forever, so it is the most expensive prose in the repo. Aphorisms, restated best practice and
anything the agent could learn by reading one file are pure cost. If a section would be true of
any project, leave it out.

On an **existing repo that already has one**, do not overwrite it. Propose additions for
whatever the discovery step learned that the file does not already say, the same way missing
linters are proposed rather than imposed.

## Where the tickets go

Ask once, at setup, and write the answer down. **Which tracker a team uses cannot be detected** -
it is a decision, not a fact on disk, and a repo hosted on GitHub may keep every ticket in Jira.
**Whether the tools to reach it exist can be detected**, so do that part yourself rather than
asking.

Three answers:

- **GitHub Issues** - the recommendation. Ask nothing further and write nothing: **the absence of a
  tracker note means GitHub**, everywhere in this set. The recommended path costs the user no
  configuration at all.
- **Local files** - markdown in the repo, which `to-issues` already knows how to write. No account,
  no network, and a fine place to start before a team has chosen anything.
- **Something else** - Jira, Linear, Azure DevOps. Look for a way to reach it: an MCP server for it
  among the session's tools, or a CLI on the machine. **Say what you found.** If nothing can reach
  it, that is a legitimate answer and not a failure - record `automation: none`, and the skills that
  create tickets will write the text out for a human to paste.

When the answer is anything but GitHub, write `.claude/tracker.md`:

```markdown
# Tracker

- **Where tickets live:** Jira, project ABC
- **Read a ticket:** `jira issue view <KEY>`
- **Create a ticket:** `jira issue create --project ABC --type Task`
- **Automation:** cli
```

`Automation:` is one of `cli`, `mcp`, `local` or `none`. Never invent a command you have not
confirmed exists - an unverified command is a claim, and a skill that runs one fails in a way the
user cannot diagnose.

## Report

Say what was wired, what the checks returned, and what a human still needs to handle - secrets,
deploy targets, anything requiring an account you do not have.

**Say what is not covered, and say what happens next.** Name the size of the untested code and the
paths where a mistake would be expensive: money, auth, data loss. Then answer the question that
finding creates. **Nothing needs to happen today**, and coverage is not a project: the next time
work changes one of those files, `tdd` pins the current behaviour first, and `verify-feature`
proves behaviour by driving the real app while the suite is still thin.

End by pointing at the next stage, sized to the project: on a bigger project - weeks of work,
many sessions - suggest **wayfinder**, since at that size there is fog you cannot chart yet. On
a smaller one, or when the user already knows the shape, suggest **grill-me**. Suggest, do not
launch.

## Done when

Every project:

- [ ] The repo exists under the owner the user named, with a default branch and a license
- [ ] The `afk` and `hitl` issue labels exist
- [ ] Where tickets live is settled - and written to `.claude/tracker.md` unless it is GitHub
- [ ] A slim `CLAUDE.md` records what the repo is and the conventions a session cannot guess
- [ ] The user knows what only a human can still do (secrets, deploy targets)

Projects with code, additionally:

- [ ] A fresh clone can install everything without manual fixes
- [ ] The format and lint/type-check commands were **run**, not read; the test command too, or
      the report states there is no suite and which paths that leaves unproven
- [ ] The commit gate was seen blocking a bad commit and passing a clean one
- [ ] CI runs the same checks as the gate
- [ ] The gate runs `gitleaks`, and CI runs `osv-scanner`
- [ ] `CLAUDE.md` records the stack, the verified commands and the gate

## Related skills

- **wayfinder** / **grill-me** - the planning that continues once the project runs. Often they
  already ran and settled the stack; this skill just wired it.
