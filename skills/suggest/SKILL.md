---
name: suggest
description: Point someone at the skill that fits what they are doing. Use when they are unsure what to reach for ("what do I use for...", "is there a skill for this"), or describe a piece of work without naming a skill.
---

# Suggest

Work out what someone is doing and name the skill that fits, with one line on why. Suggest, never
push - the Main Flow is what we usually do, not a process anyone must follow, and most work needs
no skill at all.

Orientation is not this skill's job. Someone new to the playbook wants `onboarding`, which runs
once and sets them up against what they already have. Someone opening a session on a project that
already exists wants `start`, which runs every time.

## Preflight

Run `gh auth status` once, quietly. Much of the flow (issues, branches, PRs) runs through
the `gh` CLI; if it is not authenticated, say so and point at `gh auth login` before routing
anywhere that needs it.

## Route

For build work, work out **where their work already is - never ask**. The Main Flow is one chain,
joined at whichever point matches what exists:

```
grill-me  ->  to-spec  ->  to-issues  ->  pickup-issue  ->  implement
```

Nothing written down means the whole chain. A spec already written starts at `to-issues`. A named
issue, a URL, or "pick up #12" starts at `pickup-issue` - and if its decisions were never settled,
`pickup-issue` hands back to `grill-me` before anything gets built. The signal is in what they
said, so read it and route.

Then match the situation to the skill, with one line on why:

| Situation | Skill |
|---|---|
| A new product, a client engagement, anything running for weeks | `wayfinder` |
| One piece of work - an automation, a script, a small tool, a fix | `grill-me` |
| "Would this design even feel right?" | `prototype` - also a `wayfinder` ticket type |
| A screen or layout with a lot still undefined | `design` - Claude Code ships it, not us |
| A question needing sources, not opinions | `research` - also a `wayfinder` ticket type |
| Decisions settled, nothing written down | `to-spec` |
| A spec that needs to become tickets | `to-issues` |
| A ticket ready to build | `pickup-issue` (hands to `grill-me` or `implement`) |
| A whole spec, or several tickets, to build together | `orchestrate` |
| A pull request body to write | `pr` |
| Something broken, failing, or slow | `diagnosing-bugs` |
| "Prove this feature actually works" | `verify-feature` |
| A branch or codebase to sweep for quality | `review-suite` |
| A repo to stand up, with or without code | `setup-repo` |
| Steps only a human can do (credentials, dashboards) | `wizard` |
| Opening a session on a project that already exists | `start` |
| Session ending, on a repo with code | `handoff` |
| Session ending, on a docs, training or planning repo | `update-docs` |
| "What should the agent's setup learn from this session?" | `retro` - typed only, so tell the user to run `/retro` |
| Writing or editing a skill, a `CLAUDE.md` or a doc agents read | `writing-for-agents` |

**The first two rows split on size, not uncertainty.** Every new project feels uncertain, so
uncertainty routes everything to `grill-me` and nothing to `wayfinder` - which is backwards. Ask
instead how long the work runs. `wayfinder` also **subsumes** the research and the prototyping:
its ticket types *are* `research`, `prototype`, `grilling` and `task`, so walking the map is how
those happen, in the order the fog demands. They stay invocable on their own outside a map.
`wayfinder` is the default for anything non-trivial, never a requirement.

**The last two rows split on repo type**, read the way `setup-repo` reads it: a stack manifest
present means code. Do not ask about something visible.

If nothing fits, say so plainly - most work needs no skill at all.

## Handing over

Where **one skill is unambiguously right**, do not stop at naming it - offer to run it, and invoke
it if they say yes. Naming a skill and leaving someone to type it is friction with no upside.

Where **two skills genuinely compete**, or you are naming a fork for them to pick, name them and
stop. Offering there would be choosing for them, which is the one thing this skill must not do.

## When they are asking how something works

Some questions are not routing questions. "How do I use X", "what is the smart zone", "how does
context management work" want an explanation, not a skill - and the modules are where the playbook
answers them. Answer the question from the modules and name the module by its title, not its
filename; the numbers move.

Context management is the one that comes up most, so it is worth knowing outright:

- **On a repo with code:** `/clear` between tasks, `handoff` when decisions need to survive the
  session, `/compact` almost never - only when you must continue mid-task, because a fresh session
  with a written handoff is almost always better.
- **On a docs, training or planning repo:** `start` to open the session, `update-docs` to close it.

## The two questions that come after the build

Neither is a step in the flow, and saying so is part of the job:

- **Review.** `implement` already runs `/code-review low` over its own diff. A full `/code-review`
  in a fresh session is worth it at the end of a work session, and `review-suite` is for sweeping
  a whole branch or codebase. `/security-review` is the built-in security check over the same
  diff. Advise it when the change touches login, permissions or user data.
- **`verify-feature`.** `implement` now runs it itself whenever the diff touched
  UI, an endpoint or the database - so on work that came through the flow it is already done, and
  advising it again is noise. Advise it for a change that did **not** come through `implement`,
  or when a human has to trust a result the tests do not already carry: client-facing work, a
  change nobody is going to read the diff of.
