---
name: update-docs
description: Save session progress to the ledger, refresh any project docs the work drifted from, and write the handoff for the next session. Use at the end of a working session, when a milestone lands, when the context nears the smart-zone edge, or when the user asks to wrap up or update the docs - on a docs, training or planning repo, where nothing else holds the state. On a repo with code, where the tracker and the git history already hold it, use handoff instead.
---

# Update Docs

Run this when a milestone lands, or before the context leaves the smart zone.

## When to run it

Two triggers:

- **The context is about to leave the smart zone** - the stretch of the window where the model
  is still sharp. Around **40%** used is the house habit; a habit, not a measurement, so pick
  your own.
- **A milestone landed** - a feature done, a decision settled, a phase closed. Save the session
  while the context that produced it is still rich.

On the context trigger:

1. Pause current work
2. Tell the user the context is filling and that you are saving session state
3. Run this skill
4. Tell the user to clear the session and say where they left off - `start` fires on it

## Part 1: Update Ledger

1. Read `docs/ledger.md` (create it if missing)
2. Extract from conversation history:
   - Goal of this session
   - Progress made
   - Blockers
   - Next steps
   - Key learnings
   - Files modified
   - Artifacts created

3. Add new session entry at TOP of "📅 RECENT SESSIONS":

```markdown
### Session: YYYY-MM-DD

**Current Goal:** [What we worked on]

**Progress Made:**
- [Accomplishment 1]
- [Accomplishment 2]

**Active Issues/Blockers:**
- [Or "None"]

**Next Steps:**
- [ ] [Priority action 1]
- [ ] [Priority action 2]

**Key Learnings:**
- [Insights, or "None"]

**Files Modified:**
- [Files changed, or "None"]

**Artifacts Created:**
- [Docs/configs/workflows, or "None"]
```

4. If more than 5 sessions in Recent Sessions: move oldest to "📦 ARCHIVE" with a 1-2 sentence summary
5. Update "Last Updated" date
6. Do not rewrite the "🔑 KEY DETAILS" section as part of the routine update. Correct it only when a standing fact it states has changed, and name the correction in the output

## Part 1b: The project docs, only where the work drifted

The ledger records **what happened**. The project docs record **how the project works**.
When the work moved past what is written down, the docs are actively misleading the next
reader, human or agent.

**Ledger always; project docs only on real drift.** Do not sweep all of `docs/` - a sweep
produces a diff touching files unrelated to the work, which makes review harder and trains
people to skim doc changes.

1. **Find the drift.** Compare what the work actually did against the relevant docs. List
   each specific mismatch; do not vaguely "review the docs".
2. **Classify each mismatch by where it belongs:**

   | Mismatch | Goes to |
   |---|---|
   | An architectural or convention change | `CLAUDE.md`, `AGENTS.md`; if it is a durable decision, the ADR row below |
   | A system-design change, in a repo that already keeps `docs/architecture.md` | That file (never create it) |
   | New or sharpened domain terms | `GLOSSARY.md` at the repo root, or the older `CONTEXT.md` where the repo has one - create `GLOSSARY.md` if neither exists |
   | A decision that is hard to reverse, surprising without context, and a real trade-off - all three | An ADR under `docs/adr/` |

3. **On an ADR, check first.** List the existing ADRs in `docs/adr/` and read their titles.
   If the decision is already captured, skip. If you are unsure whether it matches an
   existing one, ask. Only create a new ADR when none covers it, using the next sequential
   number.
4. **Update minimally.** Edit the smallest set of docs that removes the drift, matching the
   existing house style. Docs are a liability when they lie - and also when they sprawl, so
   fix the drift rather than gold-plating around it.

**Do not invent a doc to hold something that already has a home.** Conventions belong in
`CLAUDE.md`, not a second spec file beside it; the repo itself is the index, so do not maintain
one; and a changelog is worth keeping only where releases are actually versioned. Where a project
already keeps such a file, update it - the rule is against creating them unasked, not against
honouring what is there.

| Mistake | Fix |
|---|---|
| Rewriting docs wholesale | Edit only what drifted; a big diff is hard to trust. |
| Forcing a project-doc edit every session | Ledger always; project docs only on real drift. |
| Recording a durable decision in prose | If it has rationale and real alternatives, it is an ADR. |
| Inventing docs that never existed | Update what is there; propose new docs rather than sprawling unasked. |

## Part 2: Create Handoff Doc

Create or update `docs/handoff.md` so the next session can pick up immediately.

```markdown
# Session Handoff - YYYY-MM-DD

## Current State
- ✅ Completed: [What's done]
- ⚠️ In Progress: [Partially done]
- ⏳ Blocked: [Waiting on something]
- 🔄 Next Up: [Tackle next]

## Active Problems
[Issues/bugs with description, what was tried, current hypothesis]

## Critical Context
[Key decisions, constraints, important discoveries]

## Next Session Action Plan
1. First: [Immediate next step]
2. Then: [Follow-up]
3. Stretch: [If time permits]

## Key Files
[Files with important changes to review]
```

## Output

Tell the user:
- Session date saved
- Sessions in Recent Sessions (and if any archived)
- Any project docs updated, and what drifted
- Handoff doc location

## Related skills

- **start** - the read-side counterpart; loads these docs at the start of a session, which is what makes keeping them honest worth the effort.
- **handoff** - the same job on a repo with code. It writes one note to the OS temporary directory instead, because there the tracker and the git history already hold the state and a doc beside them goes stale.
- **grill-me** - when a decision needs interrogating before it is written to an ADR.
