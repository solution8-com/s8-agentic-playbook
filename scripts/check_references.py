#!/usr/bin/env python3
"""Check that skill references across the repo point at skills this plugin ships.

The bug class this watches for on every refresh: a reference to a skill that does not exist.
It bites hardest on a rename, where the old name survives in prose nobody re-reads.

Two passes, because this repo references skills in two shapes:

  Pass A - slash invocations. '/grill-me' must resolve to a shipped skill or to a command that
           ships elsewhere (EXTERNAL).
  Pass B - retired names. Skills are usually written in backticks with no slash - `grill-me` -
           so a slash-only scan would miss the very rename it exists to catch. A name in RETIRED
           still appearing in backticks is a leftover. Deliberately backticks only: a retired
           name can also be an ordinary English word, and matching it in plain prose would fire
           on almost every file. The slash form needs no special handling here - a retired skill
           is not shipped, so its slash form is already unresolved under pass A.

Exit 0 when everything resolves, 1 when it does not.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".claude-plugin" / "plugin.json"

# Real slash commands that this plugin does not ship. Every entry is a check we choose not to
# make, so keep it short and justified.
EXTERNAL = {
    "plugin", "clear", "compact", "help",           # Claude Code session commands
    "context", "model", "statusline", "fast",       # Claude Code session commands
    "reload-plugins", "reload-skills",              # Claude Code plugin commands
    "code-review", "security-review",               # Claude Code review commands
    "design",                                       # ships with Claude Code; the router points at it
}

# Skills that have left this plugin. A mention of one is a leftover from a rename
# or a removal. Add a name here in the same commit that retires the skill.
RETIRED = {
    "setup-dev-repo",  # renamed to setup-repo 2026-08-25
    "guide",           # renamed to suggest 2026-08-25; note modules/guide-*.md are unrelated
    "visual-spec",     # removed 2026-10-06, nobody used it
}

# Backticked paths that are shaped exactly like a slash command. A path with a second slash is
# excluded by the pattern itself; these are not, so they are named.
NOT_COMMANDS = {"settings", "tmp", "build-tool", "s8-playbook"}  # s8-playbook: the plugin prefix in /s8-playbook:orchestrate

# Matched against the repo-relative path, not the bare filename.
#
# onboarding - its job is talking about skills the plugin does not ship but the user owns.
#              it also names skills the plugin does not ship, which is the point.
EXEMPT = {"skills/onboarding/SKILL.md"}

# A slash invocation is written one of two ways and no others: inside backticks, or alone at
# the start of a line. Matching a bare '/word' anywhere would drag in every URL path, route
# literal and directory fragment in the repo - '"/users/1"', '<slug>/issues/' - so don't.
BACKTICKED_SLASH = re.compile(r"`/([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\b(?!/)")
LINE_START_SLASH = re.compile(r"^\s*/([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\b")

# A backticked skill name, with or without a leading slash: `grill-me` or `/grill-me`.
BACKTICKED = re.compile(r"`/?([a-z][a-z0-9]*(?:-[a-z0-9]+)*)`")

SEARCHED = ["skills/*/SKILL.md", "skills/*/*.md", "modules/*.md", "*.md"]


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    shipped = {Path(p).name for p in manifest.get("skills", [])}
    known = shipped | EXTERNAL | NOT_COMMANDS

    files = []
    for pattern in SEARCHED:
        files.extend(sorted(REPO.glob(pattern)))
    files = [f for f in dict.fromkeys(files)
             if str(f.relative_to(REPO)) not in EXEMPT]

    unresolved, leftovers = {}, {}

    for path in files:
        rel = path.relative_to(REPO)
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for pattern in (BACKTICKED_SLASH, LINE_START_SLASH):
                for match in pattern.finditer(line):
                    name = match.group(1)
                    if name not in known:
                        unresolved.setdefault(name, []).append(f"{rel}:{lineno}")
            for match in BACKTICKED.finditer(line):
                name = match.group(1)
                if name in RETIRED:
                    leftovers.setdefault(name, []).append(f"{rel}:{lineno}")

    def report(title, found):
        print(f"{title} ({len(found)} name(s))")
        for name in sorted(found):
            print(f"  {name}")
            for where in found[name][:6]:
                print(f"      {where}")
            if len(found[name]) > 6:
                print(f"      ... and {len(found[name]) - 6} more")

    if unresolved or leftovers:
        print("FAIL: skill references do not resolve")
        if unresolved:
            report("  unresolved slash invocations:", unresolved)
        if leftovers:
            report("  retired skills still referenced:", leftovers)
        return 1

    print(f"OK: skill references resolve - {len(files)} files scanned, "
          f"{len(shipped)} skills shipped, {len(RETIRED)} retired names watched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
