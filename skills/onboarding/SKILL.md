---
name: onboarding
description: Set the playbook up alongside a person's existing Claude setup, then show them where to start. Use immediately after the plugin is installed, when someone says they have just installed it, or when they ask how it fits with the skills, CLAUDE.md or habits they already have.
---

# Onboarding

Someone has just installed the playbook. They arrive with their own `CLAUDE.md`, their own skills
and their own way of working, and the questions in their head are not curious ones - they are
*will this break what I have?*

This skill answers those questions by **looking**, then **suggesting**, then **getting out of the
way**. It runs once. It never touches their code.

**You suggest. They decide.** Every removal or edit needs an explicit yes. That is not timidity -
the playbook advises and never mandates, and the most personal file on someone's machine is the
last place to start making exceptions.

## 1. Say what you are about to read

Before reading anything, say what you will look at and why. One short paragraph. A person who has
just handed you their machine should not have to wonder what you are doing in it.

Five things, all global. **Never their project code.**

| What | Why it matters |
|---|---|
| `~/.claude/CLAUDE.md` | Their standing instructions. Anything here outranks the playbook |
| `~/.claude/skills/` | Their own skills. A shared name means one shadows the other |
| Installed plugins | Two can do the same job twice, and one can tell the model to always prefer its own |
| `~/.claude/settings.json` | Permissions and env that change what skills can do |
| Hooks | A hook can block a command a skill depends on, and the failure looks like a bug |

**Read plugins for what they assert, not only for what they contain.** A list of skill names shows
you where two plugins overlap. It does not show you what either one will *do* about that overlap,
and that is where the conflict actually lives. So open the text a plugin injects at the start of
every session, and any skill text that claims priority over other skills. A plugin can instruct
the model to always reach for its own skills first, in words strong enough that it will.

Then check `gh auth status`. Three of the five Main Flow skills (`to-spec`, `to-issues` and
`pickup-issue`) go through GitHub, and finding that out in week one is worse than finding it out
now.

## 2. Show what you found

Report it plainly, in their terms, not as a config dump. For each thing worth mentioning give the
finding, then **a reason in one sentence a non-developer could judge**.

The five that actually come up:

- **Two skills with the same name.** Say which one wins and what the other one did. This is the
  most common one and the most confusing when it bites.
- **A hardcoded workflow in their global `CLAUDE.md`.** Two kinds, and they get different
  treatment. A **habit** - "always write tests first, then open a PR" - names no skill and no
  plugin, and cannot go stale. It is theirs: report it if it steers something, then leave it
  alone. A **hardcoded chain** - one that names specific skills or a plugin to route work
  through - goes stale the day the tools change. Recommend removing it, and **put nothing in its
  place**: the agent finds skills from their descriptions, so the chain adds nothing.
- **Another plugin covering the same ground.** Name both and let them pick.
- **A plugin that claims precedence.** Some plugins instruct the model, every session, to always
  use their own skills first - occasionally in capitals, phrased as non-negotiable. This is a
  finding in its own right, not a footnote to the overlap above. Describe what it will do rather
  than quoting it: *"when you say let's build something, this will send you to its planning skill
  instead of `grill-me`"*. Which moment it takes, and what it takes it from.
- **A hook that will block something.** Say which skill it stops and what the failure will look
  like, so they recognise it if it happens.

Where you found nothing, say so. "Nothing in your setup fights this" is a real result and a good
one to hear - and say it about precedence specifically, since silence there reads as "not
checked".

## 3. Suggest, one at a time

Each suggestion is its own yes or no. Bundling them means one reluctant yes carries four changes
nobody read.

**Only surface what they can judge, and never decide in silence.** If you cannot state the cost
and the benefit in one sentence they could weigh, do not make it a question. Take the sensible
default, then **say in one line what you took and why**.

Size is not the test. **Reversibility is.** Anything hard to undo stays a question, however small
it looks: a deletion, or a change to a file they own.

**Back the file up before the first edit** - `CLAUDE.md` to `CLAUDE.md.bak-<date>`. There is no
git in most people's `~/.claude/`, so this is the only undo there is. It is what makes saying yes
cheap.

**Where a plugin claims precedence, there are two fixes and they are not equal.** One line in
their own `CLAUDE.md` outranks anything a plugin injects and the plugin keeps updating, but the
injected text is still there and still loud. Removing the plugin ends it completely. Match the fix
to what they have asked for: someone who has said they want **one way** gets removal recommended,
with the price named in the same breath - the skills they lose that this set has no equivalent
for.

Declining is a normal outcome. Move to the next one without arguing, and never re-raise it later
in the session.

## 4. Say how to actually start

Two sentences before the flow, because they are the part nobody guesses:

- **Just use it.** There is no mode to switch on and nothing to run at the start of a session.
- **Claude will reach for a lot of these on its own now**, because the tools are there. They do
  not have to remember names to benefit.

Then, for their other projects: **`setup-repo`** brings the playbook to work they already have.

### Context, tailored to what you found

Only mention what they actually have.

- **They have `start` and `update-docs`:** keep them for documentation and planning repos, where
  nothing else holds the state. On code repos use **`handoff` then clear** instead - the decisions
  are already in the tickets and the code, so a document beside them only goes stale.
- **They do not:** when a session gets long, run **`handoff`**, then clear. That is the whole rule.

### Then the Main Flow, in plain words

> **How we usually work**
>
> Most jobs go through the same five steps. You do not have to use them - but this is the order
> that works.
>
> 1. **`grill-me`** - You have an idea, but it is still fuzzy. Claude asks you awkward questions
>    until it is sharp.
> 2. **`to-spec`** - Writes down what you just decided, so it is not only in your head.
> 3. **`to-issues`** - Chops that into small tickets, each one small enough to finish.
> 4. **`pickup-issue`** - Takes one ticket and sets up the work for it.
> 5. **`implement`** - Builds it.
>
> Then you read it and merge it. That part stays yours.
>
> **You do not have to start at step 1.** Start where your work already is:
> nothing written down goes to step 1, an existing spec to step 3, an existing ticket to step 4.
>
> **And you can skip all of it.** Most small jobs need none of this.

**Say this, never write it.** The five steps are spoken, not saved to a file. A hardcoded chain in
a `CLAUDE.md` is read every session and goes stale the day the set changes, which is the
same fault this skill recommends removing above. Writing ours in after taking theirs out swaps one
stale rule for another.

Steps 2 to 4 assume GitHub issues. If `gh auth status` came back signed out, say so here and give
them `gh auth login`. If they use a different tracker, `setup-repo` records it per project and the
skills read it.

### Where to get answers after today

This skill runs once. End by pointing at the two things that stay.

- **`suggest`** - for "I do not know what to reach for". It takes a description of the work and
  names the skill.
- **The modules, on their own disk.** They ship with the plugin, under its `modules/` directory:
  nine lessons on why the set is shaped this way, plus two guides, with `guide-2-daily.md` holding
  the everyday rules. Say they can ask Claude to read one - *"read me module 5"* - because nobody
  guesses a plugin put lessons on their machine.

## Register

Explain terms rather than avoiding them. Ten seconds on what a markdown file is lifts the people
who did not know instead of losing them, and costs the people who did know nothing at all.

Never ask what they are working on. It blocks someone who is already lost, and being lost is why
they are here. Where a prompt would help, make it an **offer** they can walk past: *"point me at a
repo you are working in and I will suggest where to start"*.

## Done when

- [ ] They know what was read, because you said so before reading it
- [ ] Every collision in their setup has been named, or you said there were none
- [ ] Any plugin asserting precedence was reported, in plain words, or you said none does
- [ ] Every change was approved individually, and every edited file was backed up first
- [ ] They know whether GitHub is set up, and how to fix it if not
- [ ] They know the five steps, that the flow is joined anywhere, and that it is all optional
- [ ] They know Claude now reaches for these on its own
- [ ] They know to run `setup-repo` on their other projects
- [ ] Any hardcoded chain got a removal recommendation, with nothing offered in its place - or
      there was none
- [ ] They know `suggest` exists, and that the modules are on their disk and readable on request
