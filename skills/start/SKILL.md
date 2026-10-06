---
name: start
description: Pick up an existing project cold by reading its state docs before doing anything else. Use at the beginning of a working session, when the user says "start", "continue", "where were we", or "pick up where we left off", or whenever you are dropped into a repo with no context from a previous session.
---

# Start - Continue Session

Continue working from where you left off by reading project state first, then acting.

This runs at the top of **every** session. It is not orientation: someone new to the playbook,
setting it up for the first time, wants `onboarding`, which runs once and never again.

## Instructions

1. **Read project context (read all in parallel):**
   - `docs/handoff.md` - current state, active work, immediate context. The primary one.
   - **A handoff in the OS temporary directory** - `$TMPDIR/handoff-<repo-or-project>-*.md`. On a
     repo with code, `handoff` writes there rather than into the workspace, so this is where the
     last session's note lives. Take the most recent one for this project. It may well be the only
     handoff there is.
   - `docs/ledger.md` - session history, key details, milestones. Read it even when a handoff exists.
   - `GLOSSARY.md` - the domain glossary, if the project keeps one. Many projects will not have one; that is fine. Older repos call it `CONTEXT.md`.
   - `docs/adr/` - architecture decision records. If the directory exists, count the files. Under 10, read them all. 10 or more, read just the title line of each and open only the bodies whose titles look relevant to the task at hand.
   - If none of these exist, say so plainly and carry on with the task.

2. **For third-party libraries and frameworks:** look the documentation up rather than
   working from memory, which may be out of date. If the project has a docs-lookup MCP
   configured (Context7 or similar), use it; otherwise fetch the official docs.

3. **For complex decision-making:** architectural calls, weighing approaches, or reasoning
   through trade-offs are worth slowing down for. Where the shape is genuinely unsettled,
   `grill-me` is the skill for it rather than deciding alone.

4. **Then proceed:**
   - If the user named a task, work on that.
   - If not, summarise the current state and ask what to work on.

## Usage

```
start                     # read state, then ask what to work on
start fix the auth bug    # read state, then work on that task
```

## Related skills

- **handoff** - the write side on a repo with code. It writes to the OS temporary directory, which
  is the second thing this skill reads.
- **update-docs** - the write side on a docs, training or planning repo. It writes `docs/handoff.md`
  and the ledger, which are the first and third things this skill reads.
- **onboarding** - runs once, when the playbook is first installed. This skill runs every session.
