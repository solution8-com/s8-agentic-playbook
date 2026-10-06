# Standards pass

Check the scope against the repo's own written standards. The prize is a codebase that reads as if one careful person wrote it.

## Sources

1. The repo's `CODING_STANDARDS.md`. Also read `CONTRIBUTING.md` and any style section in the repo docs if they exist.
2. The smell baseline below. It applies even when the repo documents nothing.

Two rules bind the baseline:

- **The repo overrides.** A documented repo standard always wins. Where the repo endorses something the baseline would flag, drop the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation.

Skip anything a linter, formatter or type checker in the repo already enforces. Skip what another pass owns: `duplication` owns Duplicated Code across files, `over-engineering` owns Speculative Generality, and `dead-code` owns unused code. Report those here only when the repo's standards file names them.

## Smell baseline

From Fowler, *Refactoring*, chapter 3. Each reads *what it is* → *how to fix*:

- **Mysterious Name**: a function, variable or type whose name does not reveal what it does or holds. → Rename it. If no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape in more than one hunk of the change. → Extract the shared shape and call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → Move the method onto the data it envies.
- **Data Clumps**: the same few fields or parameters keep travelling together. → Bundle them into one type and pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept. → Give the concept its own small type.
- **Repeated Switches**: the same `switch` or `if` cascade on the same type recurs across the change. → Replace it with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. → Gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → Split it so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters or hooks for needs the spec does not have. → Delete it. Inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. → Hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly delegates onward. → Cut it and call the real target directly.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → Drop the inheritance and use composition.

## Verify, the false-positive gate

For each candidate:

1. Quote the standard or name the smell it breaks. No source, no finding.
2. Confirm the code in scope breaks it, not the code around it.
3. Check that no repo standard endorses the pattern.

## Severity

High: breaks a rule the repo's standards file states. Medium: a clear smell in new code that the next change will have to work around. Low: a smell in passing, cheap to leave.

## Report

Return the JSON findings array per the schema in your dispatch prompt. In `title`, name the standard or the smell ("possible Feature Envy"). In `recommendation`, give the fix from the standard or the smell line.

If the repo has no `CODING_STANDARDS.md`, say so in one finding of severity `low` only when a repeated judgement-call pattern in the scope would deserve a written rule.

An empty findings array is a valid result. A weak finding costs more than a missing one. Do not pad.
