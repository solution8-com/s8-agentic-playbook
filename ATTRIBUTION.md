# Attribution

> A lot of this is Matt Pocock's work. Here is exactly which parts.

The S8 Agentic Playbook is a **curated** collection. A lot of it is Matt Pocock's
work, vendored under MIT with small or no changes. Some of the skills are
Solution8's own. We are grateful to the original authors, and we would rather
say plainly what we took than imply we wrote it. This collection is itself
MIT-licensed (see [LICENSE](LICENSE)).

Skills marked **verbatim** below are byte-identical to upstream. The one
set-wide exception: Matt ships Codex sidecar YAMLs in some skills' `agents/`
directories, which we do not adopt and strip on vendoring.

We are pinned to `mattpocock/skills` v1.2.3, commit `8b78b53`, 2026-08-13, MIT. `orchestrate`, `pr`, `retro` and `writing-for-agents` come from v1.3.1+, commit `4588b32`, 2026-10-05. We do not
track it continuously, and refresh deliberately instead. What changed in each tweaked skill is
recorded internally rather than here.

## Sources

- **`mattpocock/skills`** - Matt Pocock (MIT, (c) 2026).
  <https://github.com/mattpocock/skills>

## Per-skill provenance

| Skill | Origin |
|---|---|
| `onboarding` | Solution8 original |
| `setup-repo` | Solution8 original |
| `grill-me` | mattpocock/skills (`grill-me` + `grilling`), merged into one file |
| `to-spec` | mattpocock/skills (`to-spec`), tweaked |
| `to-issues` | mattpocock/skills (`to-tickets`), renamed and tweaked |
| `pickup-issue` | Solution8 original |
| `implement` | mattpocock/skills (`implement`), rewritten around a build subagent, his build steps kept inside the procedure |
| `orchestrate` | Built on mattpocock/skills (`implement-spec`, v1.3): the integration branch and the frontier. The phases, the briefs and the run log are Solution8's own |
| `wayfinder` | mattpocock/skills (`wayfinder`), tweaked |
| `prototype` | mattpocock/skills (`prototype`), verbatim |
| `research` | mattpocock/skills (`research`), verbatim |
| `improve-codebase-architecture` | mattpocock/skills (`improve-codebase-architecture`), tweaked |
| `diagnosing-bugs` | mattpocock/skills (`diagnosing-bugs`), tweaked |
| `wait-what` | mattpocock/skills (`wait-what`), tweaked |
| `verify-feature` | Solution8 original |
| `review-suite` | Solution8 original. The `standards` pass takes its smell baseline from the Standards axis of mattpocock/skills (`code-review`) |
| `suggest` | Solution8 original |
| `wizard` | mattpocock/skills (`wizard`), verbatim |
| `to-questionnaire` | mattpocock/skills (`to-questionnaire`), verbatim |
| `handoff` | mattpocock/skills (`handoff`), tweaked |
| `tdd` | mattpocock/skills (`tdd`), tweaked |
| `pr` | mattpocock/skills (`pr`, v1.3), tweaked. Its Summary visuals come from Dex Horthy's `show-me` (humanlayer/skills, MIT), see `skills/pr/CREDITS.md` |
| `retro` | mattpocock/skills (`retro`, v1.3), tweaked |
| `writing-for-agents` | mattpocock/skills (`writing-for-agents`, v1.3), verbatim |
| `start` | Solution8 original |
| `update-docs` | Solution8 original |

A line-level audit (2026-08-07) traced every vendored or reshaped line in the
collection back to one of the two libraries above; everything else is
Solution8's own text. The 2026-08-14 rescope replaced most reshaped forks with
verbatim upstream copies, which narrows what we claim as ours.

## Upstream licenses

Both source libraries are MIT-licensed. Their notices are reproduced below as
required.

### mattpocock/skills

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

