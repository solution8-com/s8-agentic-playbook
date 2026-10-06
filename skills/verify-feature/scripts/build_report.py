"""Build a self-contained verification report HTML from a manifest.json.

Usage: python3 build_report.py <manifest.json> <output.html>

Embeds every screenshot as a base64 data URI so the output is a single file
and the source screenshots can be deleted afterward. Styling comes from the
plugin's shared assets/report.css, inlined so the report stays self-contained
and so verify-feature, review-suite and orchestrate keep matching. The
interactive layer below adds its own rules on top of that stylesheet.

The manifest carries header fields, "flows" (UI flows with screenshots) and
"sections" (non-UI results: tables, evidence blocks, notes). Flow notes and
captions are escaped plain text (backwards compatible with ui-report
manifests). Section notes, table headers/cells and notes-blocks are trusted
raw HTML so the authoring skill can mark up <code>, <span class="ok">,
<span class="warn">. The manifest is always machine-authored, never
untrusted input. Evidence-block text is escaped and rendered mono/pre-wrap.

Interactive features rendered into every report:
- Verdict strip: overall verdict + one jump-chip per flow/section.
- Collapsible sections: pass/na/notes collapse, fail/blocked stay open.
- Lightbox on screenshots: wheel zoom, drag pan, double-click 1:1, arrows.
- Copy-as-markdown button exporting the whole report for GitHub.

Optional manifest fields (all backwards compatible):
- A shot may carry "marks": [{x, y, w, h, label?}] in natural PNG pixels;
  rendered as clay callout boxes over the image (labels shown in lightbox).
- A shot may be a flip pair instead of a single image:
  {"flip": [{"path":..., "label": "Before", "marks": [...]}, ...],
   "caption": ...} renders with a segmented state toggle, also in lightbox.
- A section block {"type": "checks", "path": "results.json"} (or inline
  "results": [...]) renders a machine-authored check table from
  [{name, ok, detail}] without hand-transcription; "path" is
  manifest-relative and accepts {"results": [...]} or a bare list.
- A section "status": "auto" derives pass/fail from its checks blocks.
- Status "accepted" (on a flow/section) or "accepted": true (on a checks
  row) marks a reproduced known-accepted finding: rendered muted (ACCEPTED),
  excluded from fail tallies and from the overall verdict.
"""

import base64
import html
import json
import re
import struct
import sys
from pathlib import Path

CSS_PATH = Path(__file__).resolve().parents[3] / "assets" / "report.css"

FALLBACK_CSS = """
:root { --ivory:#101418; --slate:#e8e5df; --clay:#D97757; --oat:#2a323c;
        --oat-deep:#98a1ab; --olive:#8fb573; --gray-light:#1d242c; --gray-dark:#98a1ab; }
* { box-sizing:border-box; }
body { margin:0; background:var(--ivory); color:var(--slate);
       font-family:system-ui,-apple-system,sans-serif; line-height:1.55; }
.wrap { max-width:1120px; margin:0 auto; padding:48px 24px 96px; }
h1,h2 { font-family:ui-serif,Georgia,serif; font-weight:600; }
.eyebrow { font-family:ui-monospace,monospace; text-transform:uppercase;
           letter-spacing:.08em; font-size:.72rem; color:var(--gray-dark); }
.meta { font-family:ui-monospace,monospace; font-size:.8rem;
        color:var(--gray-dark); margin-bottom:28px; }
.flow,.summary { border:1px solid var(--oat); border-radius:14px; background:#171d24;
                 padding:24px 28px; margin-bottom:36px; }
.flow-head { display:flex; align-items:baseline; gap:14px; }
.badge { font-family:ui-monospace,monospace; font-size:.7rem; color:#10151a;
         border-radius:999px; padding:3px 12px; }
.badge.ok { background:var(--olive); } .badge.bad { background:var(--clay); }
.badge.muted { background:var(--gray-dark); } .badge.na { background:var(--oat-deep); }
.notes { margin:12px 0 4px; }
.console,.evidence { font-family:ui-monospace,monospace; font-size:.78rem;
           background:var(--gray-light); border-radius:10px; padding:10px 14px;
           margin:12px 0; white-space:pre-wrap; overflow-x:auto; color:var(--gray-dark); }
.console.errors,.evidence { border-left:3px solid var(--clay); }
.shots { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:20px; }
figure { margin:0; }
figure img { width:100%; border:1.5px solid var(--oat); border-radius:10px; display:block; }
figcaption { font-size:.85rem; color:var(--gray-dark); margin-top:8px; }
figcaption .n { font-family:ui-monospace,monospace; color:var(--clay); margin-right:6px; }
.tablewrap { overflow-x:auto; }
table.results { width:100%; border-collapse:collapse; margin:14px 0 6px; font-size:.88rem; }
table.results th { font-family:ui-monospace,monospace; text-transform:uppercase;
                   letter-spacing:.06em; font-size:.68rem; color:var(--gray-dark);
                   text-align:left; padding:8px 12px; border-bottom:1.5px solid var(--oat); }
table.results td { padding:8px 12px; border-bottom:1px solid var(--gray-light);
                   vertical-align:top; }
code { font-family:ui-monospace,monospace; font-size:.82em;
       background:var(--gray-light); border-radius:5px; padding:1px 5px; }
.ok { color:var(--olive); font-weight:600; }
.warn { color:var(--clay); font-weight:600; }
"""

STATUS = {
    "pass": ("PASS", "var(--olive)"),
    "fail": ("FAIL", "var(--clay)"),
    "blocked": ("BLOCKED", "var(--gray-dark)"),
    "na": ("N/A", "var(--oat-deep)"),
    "notes": ("NOTES", "var(--gray-dark)"),
    "accepted": ("ACCEPTED", "var(--oat-deep)"),
}

MD_ICON = {"pass": "&#x2705;", "fail": "&#x274C;", "blocked": "&#x26D4;", "na": "&mdash;", "notes": "&#x2139;&#xFE0F;", "accepted": "&#x1F7E1;"}
MD_ICON_TXT = {"pass": "✅", "fail": "❌", "blocked": "⛔", "na": "—", "notes": "ℹ️", "accepted": "🟡"}

MANIFEST_DIR = Path(".")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div class="wrap">
    <div class="eyebrow">Verification report &middot; {date}</div>
    <h1>{title}</h1>
    <div class="meta">{repo} &middot; {branch} @ {commit} &middot; {base_url}</div>
    {verdict_strip}
    <div class="summary">{summary}</div>
    {flows}
    {sections}
</div>
</body>
</html>
"""

EXTRA_CSS = """
    .acc { color: var(--oat-deep); font-weight: 600; }
    .verdict-strip {
        display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
        margin: 0 0 26px;
    }
    .verdict-overall {
        font-size: 0.78rem; padding: 5px 16px; letter-spacing: 0.1em;
    }
    .vchip {
        display: inline-flex; align-items: center; gap: 7px;
        border: 1.5px solid var(--oat); border-radius: 999px; background: var(--panel);
        padding: 4px 12px; font-family: ui-monospace, Consolas, monospace;
        font-size: 0.72rem; color: var(--slate); text-decoration: none;
        max-width: 280px; white-space: nowrap; overflow: hidden;
        text-overflow: ellipsis; transition: border-color 0.15s ease;
    }
    .vchip:hover { border-color: var(--oat-deep); }
    .vchip .dot { width: 8px; height: 8px; border-radius: 999px; flex: none; }
    .copy-md {
        margin-left: auto; border: 1.5px solid var(--oat); border-radius: 999px;
        background: var(--panel); color: var(--slate); cursor: pointer;
        font-family: ui-monospace, Consolas, monospace; font-size: 0.72rem;
        padding: 5px 14px; transition: border-color 0.15s ease;
    }
    .copy-md:hover { border-color: var(--oat-deep); }

    details.flow > summary { cursor: pointer; list-style: none; user-select: none; }
    details.flow > summary::-webkit-details-marker { display: none; }
    .chev { flex: none; color: var(--clay); font-size: 0.85rem; }
    .chev::before { content: "\\25B8"; display: inline-block; transition: transform 0.15s ease; }
    details[open] > summary .chev::before { transform: rotate(90deg); }
    details.flow > summary:hover h2 { text-decoration: underline; text-decoration-color: var(--oat-deep); text-underline-offset: 4px; }
    .flow-body { margin-top: 4px; }

    .flipbar { display: flex; margin-bottom: 8px; }
    .flip-btn, .lb-toggle {
        font-family: ui-monospace, Consolas, monospace; font-size: 0.7rem;
        letter-spacing: 0.04em; cursor: pointer; padding: 3px 12px;
        border: 1.5px solid var(--oat); background: var(--panel); color: var(--gray-dark);
    }
    .flip-btn + .flip-btn { border-left: none; }
    .flip-btn:first-child { border-radius: 999px 0 0 999px; }
    .flip-btn:last-child { border-radius: 0 999px 999px 0; }
    .flip-btn:only-child { border-radius: 999px; }
    .flip-btn.active { background: var(--slate); color: var(--ivory); border-color: var(--slate); }

    .shotwrap .state { position: relative; display: none; }
    .shotwrap .state.active { display: block; }
    .state img { cursor: zoom-in; transition: border-color 0.15s ease; }
    .state img:hover { border-color: var(--oat-deep); }
    .mark {
        position: absolute; border: 2px solid var(--clay); border-radius: 4px;
        background: rgba(217, 119, 87, 0.08); pointer-events: none;
        box-shadow: 0 0 0 1px rgba(250, 249, 245, 0.65);
    }
    .mark-label {
        position: absolute; bottom: calc(100% + 3px); left: -2px;
        font: 600 0.66rem ui-monospace, Consolas, monospace; font-style: normal;
        background: var(--clay); color: #fff; padding: 1px 7px;
        border-radius: 3px; white-space: nowrap;
    }
    .shots .mark-label { display: none; }

    .check-detail, .checks-tally {
        font-family: ui-monospace, Consolas, monospace; font-size: 0.76rem;
        color: var(--gray-dark);
    }
    .checks-tally { margin: 4px 0 0; }

    .lightbox {
        position: fixed; inset: 0; background: rgba(20, 20, 19, 0.93);
        display: none; flex-direction: column; align-items: center;
        z-index: 1000; padding: 52px 84px 20px;
    }
    .lightbox.open { display: flex; }
    .lb-stage {
        flex: 1 1 auto; min-height: 0; width: 100%; display: flex;
        align-items: center; justify-content: center; overflow: hidden;
    }
    .lb-stage.zoomed { cursor: grab; }
    .lb-stage.zoomed:active { cursor: grabbing; }
    .lb-zoom { will-change: transform; }
    .lb-shotwrap { position: relative; display: inline-block; line-height: 0; }
    .lb-shotwrap img {
        display: block; max-width: calc(100vw - 200px);
        max-height: calc(100vh - 190px); border-radius: 6px; background: var(--panel);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
    }
    .lightbox.hide-marks .mark { display: none; }
    .lb-bar { display: flex; align-items: center; gap: 14px; margin-top: 14px; }
    .lb-bar:empty { display: none; }
    .lb-flip { display: flex; }
    .lb-flip .lb-toggle + .lb-toggle { border-left: none; }
    .lb-flip .lb-toggle:first-child { border-radius: 999px 0 0 999px; }
    .lb-flip .lb-toggle:last-child { border-radius: 0 999px 999px 0; }
    .lb-flip .lb-toggle:only-child { border-radius: 999px; }
    .lb-toggle { background: rgba(250, 249, 245, 0.1); border-color: rgba(250, 249, 245, 0.3); color: var(--ivory); }
    .lb-toggle.active { background: var(--ivory); color: var(--slate); border-color: var(--ivory); }
    .lb-marks-toggle { border-radius: 999px; }
    .lb-caption {
        color: var(--ivory); font-size: 0.9rem; margin-top: 12px;
        max-width: 900px; text-align: center; min-height: 1.4em;
    }
    .lb-caption .n { font-family: ui-monospace, Consolas, monospace; color: var(--clay); margin-right: 8px; }
    .lb-btn {
        position: fixed; top: 50%; transform: translateY(-50%);
        background: rgba(250, 249, 245, 0.12); color: var(--ivory);
        border: none; font-size: 1.5rem; width: 52px; height: 52px;
        border-radius: 999px; cursor: pointer; line-height: 1; z-index: 1001;
    }
    .lb-btn:hover { background: rgba(250, 249, 245, 0.25); }
    .lb-prev { left: 20px; }
    .lb-next { right: 20px; }
    .lb-close {
        position: fixed; top: 16px; right: 20px; transform: none;
        font-size: 1.7rem; width: 44px; height: 44px;
    }
    .lb-count {
        position: fixed; top: 26px; left: 26px; color: var(--ivory);
        font-family: ui-monospace, Consolas, monospace; font-size: 0.8rem;
        letter-spacing: 0.08em; opacity: 0.7;
    }
"""

SCRIPT = """<script>
(function () {
    function openTarget(id) {
        var el = document.getElementById(id);
        if (el && el.tagName === "DETAILS") el.open = true;
    }
    [].forEach.call(document.querySelectorAll(".vchip"), function (a) {
        a.addEventListener("click", function () { openTarget(a.getAttribute("href").slice(1)); });
    });
    if (location.hash) openTarget(location.hash.slice(1));

    var mdTpl = document.getElementById("md-export");
    var copyBtn = document.querySelector(".copy-md");
    if (mdTpl && copyBtn) {
        copyBtn.addEventListener("click", function () {
            var text = mdTpl.content.textContent;
            function done(ok) {
                copyBtn.textContent = ok ? "Copied \\u2713" : "Copy failed";
                setTimeout(function () { copyBtn.textContent = "Copy as markdown"; }, 1600);
            }
            function fallback() {
                var ta = document.createElement("textarea");
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                var ok = false;
                try { ok = document.execCommand("copy"); } catch (e) {}
                ta.remove();
                return ok;
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallback()); });
            } else {
                done(fallback());
            }
        });
    }

    [].forEach.call(document.querySelectorAll("figure.shot .flip-btn"), function (btn) {
        btn.addEventListener("click", function () {
            var fig = btn.closest("figure");
            var idx = btn.getAttribute("data-state");
            [].forEach.call(fig.querySelectorAll(".flip-btn"), function (b) { b.classList.toggle("active", b === btn); });
            [].forEach.call(fig.querySelectorAll(".state"), function (s) { s.classList.toggle("active", s.getAttribute("data-state") === idx); });
        });
    });

    var figures = [].slice.call(document.querySelectorAll(".shots figure.shot"));
    if (!figures.length) return;

    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = '<div class="lb-count"></div>' +
        '<button class="lb-btn lb-prev" aria-label="Previous">&#8592;</button>' +
        '<div class="lb-stage"><div class="lb-zoom"><div class="lb-shotwrap"><img alt=""></div></div></div>' +
        '<button class="lb-btn lb-next" aria-label="Next">&#8594;</button>' +
        '<button class="lb-btn lb-close" aria-label="Close">&times;</button>' +
        '<div class="lb-bar"><div class="lb-flip"></div><button class="lb-toggle lb-marks-toggle">Marks</button></div>' +
        '<div class="lb-caption"></div>';
    document.body.appendChild(lb);
    var stage = lb.querySelector(".lb-stage"), zoomEl = lb.querySelector(".lb-zoom"),
        wrap = lb.querySelector(".lb-shotwrap"), im = wrap.querySelector("img"),
        cap = lb.querySelector(".lb-caption"), count = lb.querySelector(".lb-count"),
        flipBar = lb.querySelector(".lb-flip"), marksToggle = lb.querySelector(".lb-marks-toggle"),
        cur = 0, scale = 1, tx = 0, ty = 0, dragging = false, moved = false, sx = 0, sy = 0;

    function apply() {
        zoomEl.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
        stage.classList.toggle("zoomed", scale > 1);
    }
    function resetZoom() { scale = 1; tx = 0; ty = 0; apply(); }
    function activeState(fig) { return fig.querySelector(".state.active") || fig.querySelector(".state"); }

    function renderState(fig) {
        var st = activeState(fig);
        var src = st.querySelector("img");
        im.src = src.src;
        im.alt = src.alt;
        [].forEach.call(wrap.querySelectorAll(".mark"), function (m) { m.remove(); });
        [].forEach.call(st.querySelectorAll(".mark"), function (m) { wrap.appendChild(m.cloneNode(true)); });
        marksToggle.style.display = st.querySelector(".mark") ? "" : "none";
    }

    function show(i) {
        cur = (i + figures.length) % figures.length;
        var fig = figures[cur];
        resetZoom();
        renderState(fig);
        cap.innerHTML = "";
        var n = fig.getAttribute("data-n");
        if (n) {
            var s = document.createElement("span");
            s.className = "n";
            s.textContent = n;
            cap.appendChild(s);
        }
        cap.appendChild(document.createTextNode(im.alt));
        count.textContent = (cur + 1) + " / " + figures.length;
        flipBar.innerHTML = "";
        [].forEach.call(fig.querySelectorAll(".flip-btn"), function (b) {
            var nb = document.createElement("button");
            nb.className = "lb-toggle" + (b.classList.contains("active") ? " active" : "");
            nb.textContent = b.textContent;
            nb.addEventListener("click", function () {
                b.click();
                [].forEach.call(flipBar.querySelectorAll(".lb-toggle"), function (x) { x.classList.toggle("active", x === nb); });
                resetZoom();
                renderState(fig);
            });
            flipBar.appendChild(nb);
        });
        lb.classList.add("open");
    }
    function close() { lb.classList.remove("open"); }

    figures.forEach(function (fig, i) {
        [].forEach.call(fig.querySelectorAll(".state img"), function (el) {
            el.addEventListener("click", function () { show(i); });
        });
    });
    lb.addEventListener("click", function (e) {
        if (moved) { moved = false; return; }
        if (e.target === lb || e.target === stage) close();
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(cur - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(cur + 1); });
    marksToggle.addEventListener("click", function () { lb.classList.toggle("hide-marks"); });

    stage.addEventListener("wheel", function (e) {
        e.preventDefault();
        var rect = stage.getBoundingClientRect();
        var cx = e.clientX - rect.left - rect.width / 2, cy = e.clientY - rect.top - rect.height / 2;
        var ns = Math.min(8, Math.max(1, scale * (e.deltaY < 0 ? 1.18 : 1 / 1.18)));
        var factor = ns / scale;
        tx = cx - factor * (cx - tx);
        ty = cy - factor * (cy - ty);
        scale = ns;
        if (scale === 1) { tx = 0; ty = 0; }
        apply();
    }, { passive: false });
    stage.addEventListener("pointerdown", function (e) {
        if (scale <= 1) return;
        dragging = true;
        sx = e.clientX - tx;
        sy = e.clientY - ty;
        stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", function (e) {
        if (!dragging) return;
        tx = e.clientX - sx;
        ty = e.clientY - sy;
        moved = true;
        apply();
    });
    stage.addEventListener("pointerup", function () { dragging = false; });
    stage.addEventListener("dblclick", function (e) {
        if (scale > 1) { resetZoom(); return; }
        var rect = stage.getBoundingClientRect();
        var cx = e.clientX - rect.left - rect.width / 2, cy = e.clientY - rect.top - rect.height / 2;
        scale = Math.min(8, Math.max(2, im.naturalWidth && im.clientWidth ? im.naturalWidth / im.clientWidth : 2));
        tx = cx - scale * cx;
        ty = cy - scale * cy;
        apply();
    });

    document.addEventListener("keydown", function (e) {
        if (!lb.classList.contains("open")) return;
        if (e.key === "Escape") close();
        else if (e.key === "ArrowLeft") show(cur - 1);
        else if (e.key === "ArrowRight") show(cur + 1);
    });
})();
</script>"""

FLOW = """<details class="flow" id="{sid}"{opened}>
    <summary class="flow-head">
        <span class="chev"></span>
        <h2>{name}</h2>
        <span class="badge" style="background:{color}">{label}</span>
    </summary>
    <div class="flow-body">
    <p class="notes">{notes}</p>
    {console}
    <div class="shots">{shots}</div>
    </div>
</details>
"""

SECTION = """<details class="flow" id="{sid}"{opened}>
    <summary class="flow-head">
        <span class="chev"></span>
        <h2>{name}</h2>
        <span class="badge" style="background:{color}">{label}</span>
    </summary>
    <div class="flow-body">
    {notes}
    {blocks}
    </div>
</details>
"""


def load_css():
    try:
        return CSS_PATH.read_text(encoding="utf-8")
    except OSError:
        return FALLBACK_CSS


def embed(path):
    p = MANIFEST_DIR / path if not Path(path).is_absolute() else Path(path)
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    ext = p.suffix.lstrip(".").lower() or "png"
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{data}"


def png_size(path):
    p = MANIFEST_DIR / path if not Path(path).is_absolute() else Path(path)
    try:
        head = p.open("rb").read(24)
    except OSError:
        return None
    if head[:8] != b"\x89PNG\r\n\x1a\n" or len(head) < 24:
        return None
    return struct.unpack(">II", head[16:24])


def render_marks(marks, dims, path):
    if not marks:
        return ""
    if not dims:
        print(f"warning: marks on non-PNG or unreadable image skipped: {path}", file=sys.stderr)
        return ""
    w, h = dims
    out = []
    for m in marks:
        style = "left:{:.2f}%;top:{:.2f}%;width:{:.2f}%;height:{:.2f}%".format(
            m["x"] / w * 100, m["y"] / h * 100, m["w"] / w * 100, m["h"] / h * 100
        )
        label = (
            f'<i class="mark-label">{html.escape(m["label"])}</i>'
            if m.get("label")
            else ""
        )
        out.append(f'<span class="mark" style="{style}">{label}</span>')
    return "".join(out)


def render_figure(shot, n):
    caption = shot.get("caption", "")
    states = shot.get("flip")
    flipbar = ""
    if states is None:
        states = [{"path": shot["path"], "marks": shot.get("marks")}]
    else:
        btns = "".join(
            '<button class="flip-btn{act}" data-state="{i}">{lab}</button>'.format(
                act=" active" if i == 0 else "",
                i=i,
                lab=html.escape(st.get("label") or f"State {i + 1}"),
            )
            for i, st in enumerate(states)
        )
        flipbar = f'<div class="flipbar">{btns}</div>'
    state_html = []
    for i, st in enumerate(states):
        marks = render_marks(st.get("marks"), png_size(st["path"]), st["path"])
        state_html.append(
            '<div class="state{act}" data-state="{i}"><img src="{src}" alt="{alt}">{marks}</div>'.format(
                act=" active" if i == 0 else "",
                i=i,
                src=embed(st["path"]),
                alt=html.escape(caption),
                marks=marks,
            )
        )
    return (
        '<figure class="shot" data-n="{n:02d}">{flipbar}<div class="shotwrap">{states}</div>'
        '<figcaption><span class="n">{n:02d}</span>{cap}</figcaption></figure>'
    ).format(n=n, flipbar=flipbar, states="".join(state_html), cap=html.escape(caption))


def render_flow(flow, sid, status):
    label, color = STATUS.get(status, STATUS["blocked"])
    console = flow.get("console", "").strip()
    console_html = (
        f'<div class="console errors">{html.escape(console)}</div>' if console else ""
    )
    shots = [render_figure(s, i) for i, s in enumerate(flow.get("shots", []), 1)]
    return FLOW.format(
        sid=sid,
        opened=" open" if status in ("fail", "blocked") else "",
        name=html.escape(flow.get("name", "Flow")),
        label=label,
        color=color,
        notes=html.escape(flow.get("notes", "")),
        console=console_html,
        shots="".join(shots),
    )


def render_block(block):
    kind = block.get("type", "notes")
    if kind == "table":
        head = "".join(f"<th>{h}</th>" for h in block.get("headers", []))
        rows = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in block.get("rows", [])
        )
        head_html = f"<tr>{head}</tr>" if head else ""
        return f'<div class="tablewrap"><table class="results">{head_html}{rows}</table></div>'
    if kind == "checks":
        results = block.get("results") or []
        ok_n = sum(1 for r in results if r.get("ok"))
        acc_n = sum(1 for r in results if not r.get("ok") and r.get("accepted"))
        rows = "".join(
            '<tr><td>{badge}</td><td>{name}</td><td class="check-detail">{detail}</td></tr>'.format(
                badge='<span class="ok">PASS</span>'
                if r.get("ok")
                else '<span class="acc">ACCEPTED</span>'
                if r.get("accepted")
                else '<span class="warn">FAIL</span>',
                name=html.escape(str(r.get("name", ""))),
                detail=html.escape(str(r.get("detail", ""))),
            )
            for r in results
        )
        tally = f"{ok_n}/{len(results)} passed"
        if acc_n:
            tally += f", {acc_n} accepted"
        return (
            '<div class="tablewrap"><table class="results">'
            "<tr><th>Result</th><th>Check</th><th>Detail</th></tr>"
            f"{rows}</table></div>"
            f'<p class="checks-tally">{tally}</p>'
        )
    if kind == "evidence":
        return f'<div class="evidence">{html.escape(block.get("text", ""))}</div>'
    return f'<p class="notes">{block.get("html", "")}</p>'


def render_section(sec, sid, status):
    label, color = STATUS.get(status, STATUS["notes"])
    notes = sec.get("notes", "")
    notes_html = f'<p class="notes">{notes}</p>' if notes else ""
    blocks = "".join(render_block(b) for b in sec.get("blocks", []))
    return SECTION.format(
        sid=sid,
        opened=" open" if status in ("fail", "blocked") else "",
        name=html.escape(sec.get("name", "Section")),
        label=label,
        color=color,
        notes=notes_html,
        blocks=blocks,
    )


def effective_status(obj, default):
    s = obj.get("status", default)
    if s != "auto":
        return s
    results = [
        r
        for b in obj.get("blocks", [])
        if b.get("type") == "checks"
        for r in b.get("results") or []
    ]
    if not results:
        return "blocked"
    if any(not r.get("ok") and not r.get("accepted") for r in results):
        return "fail"
    if any(r.get("ok") for r in results):
        return "pass"
    return "accepted"


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def md_cell(s):
    return strip_tags(s).replace("|", "\\|")


def block_md(block):
    kind = block.get("type", "notes")
    if kind == "table":
        headers = [md_cell(h) for h in block.get("headers", [])]
        lines = []
        if headers:
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "---|" * len(headers))
        for row in block.get("rows", []):
            lines.append("| " + " | ".join(md_cell(c) for c in row) + " |")
        return "\n".join(lines)
    if kind == "checks":
        results = block.get("results") or []
        lines = ["| Result | Check | Detail |", "|---|---|---|"]
        for r in results:
            lines.append(
                "| {res} | {name} | {detail} |".format(
                    res="PASS" if r.get("ok") else ("ACCEPTED" if r.get("accepted") else "**FAIL**"),
                    name=md_cell(str(r.get("name", ""))),
                    detail=md_cell(str(r.get("detail", ""))),
                )
            )
        ok_n = sum(1 for r in results if r.get("ok"))
        acc_n = sum(1 for r in results if not r.get("ok") and r.get("accepted"))
        tally = f"{ok_n}/{len(results)} passed"
        if acc_n:
            tally += f", {acc_n} accepted"
        lines.append(f"\n{tally}")
        return "\n".join(lines)
    if kind == "evidence":
        return "```\n" + (block.get("text", "")) + "\n```"
    return strip_tags(block.get("html", ""))


def to_md(manifest, entries, overall):
    lines = [
        f"# {manifest.get('title', 'Verification report')}",
        "",
        "**Overall: {}** {} · {} · {} @ {} · {}".format(
            overall.upper(),
            MD_ICON_TXT.get(overall, ""),
            manifest.get("repo", ""),
            manifest.get("branch", ""),
            manifest.get("commit", ""),
            manifest.get("date", ""),
        ),
        "",
        strip_tags(manifest.get("summary", "")),
        "",
    ]
    for kind, obj, status in entries:
        icon = MD_ICON_TXT.get(status, "")
        lines.append(f"## {icon} {obj.get('name', kind)} ({status.upper()})")
        lines.append("")
        notes = obj.get("notes", "")
        if notes:
            lines.append(strip_tags(notes) if kind == "section" else notes)
            lines.append("")
        if kind == "flow":
            console = obj.get("console", "").strip()
            if console:
                lines.append("```\n" + console + "\n```")
                lines.append("")
            for i, shot in enumerate(obj.get("shots", []), 1):
                states = shot.get("flip")
                suffix = (
                    " ({})".format(" / ".join(st.get("label") or f"State {j + 1}" for j, st in enumerate(states)))
                    if states
                    else ""
                )
                lines.append(f"- screenshot {i:02d}: {shot.get('caption', '')}{suffix}")
            if obj.get("shots"):
                lines.append("")
        else:
            for b in obj.get("blocks", []):
                lines.append(block_md(b))
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def verdict_strip_html(entries, overall):
    label, color = STATUS.get(overall, STATUS["blocked"])
    chips = []
    for i, (kind, obj, status) in enumerate(entries):
        _, dot = STATUS.get(status, STATUS["notes"])
        chips.append(
            '<a class="vchip" href="#sec-{i}"><i class="dot" style="background:{dot}"></i>{name}</a>'.format(
                i=i, dot=dot, name=html.escape(obj.get("name", kind))
            )
        )
    return (
        '<div class="verdict-strip">'
        f'<span class="badge verdict-overall" style="background:{color}">{label}</span>'
        + "".join(chips)
        + '<button class="copy-md">Copy as markdown</button></div>'
    )


def main():
    global MANIFEST_DIR
    manifest_path = Path(sys.argv[1])
    MANIFEST_DIR = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out = Path(sys.argv[2])

    for sec in manifest.get("flows", []) + manifest.get("sections", []):
        for b in sec.get("blocks", []):
            if b.get("type") == "checks" and "results" not in b and "path" in b:
                data = json.loads((MANIFEST_DIR / b["path"]).read_text(encoding="utf-8"))
                b["results"] = data["results"] if isinstance(data, dict) else data

    entries = [("flow", f, effective_status(f, "blocked")) for f in manifest.get("flows", [])]
    entries += [("section", s, effective_status(s, "notes")) for s in manifest.get("sections", [])]

    real = [s for _, _, s in entries if s in ("pass", "fail", "blocked")]
    if not real:
        # Nothing was actually verified. A green PASS here would be a verdict
        # with no evidence behind it, which is the one thing the report forbids.
        overall = "na"
    else:
        overall = "fail" if "fail" in real else ("blocked" if "blocked" in real else "pass")

    flows_html = "".join(
        render_flow(obj, f"sec-{i}", status)
        for i, (kind, obj, status) in enumerate(entries)
        if kind == "flow"
    )
    sections_html = "".join(
        render_section(obj, f"sec-{i}", status)
        for i, (kind, obj, status) in enumerate(entries)
        if kind == "section"
    )

    page = PAGE.format(
        css=load_css(),
        title=html.escape(manifest.get("title", "Verification report")),
        date=html.escape(manifest.get("date", "")),
        repo=html.escape(manifest.get("repo", "")),
        branch=html.escape(manifest.get("branch", "")),
        commit=html.escape(manifest.get("commit", "")),
        base_url=html.escape(manifest.get("base_url", "")),
        verdict_strip=verdict_strip_html(entries, overall),
        summary=manifest.get("summary", ""),
        flows=flows_html,
        sections=sections_html,
    )
    page = page.replace("</style>", EXTRA_CSS + "</style>")
    md_tpl = '<template id="md-export">{}</template>'.format(html.escape(to_md(manifest, entries, overall)))
    page = page.replace("</body>", md_tpl + "\n" + SCRIPT + "\n</body>")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    print(
        f"wrote {out} ({out.stat().st_size // 1024} KB, {len(entries)} sections, overall {overall.upper()})"
    )


if __name__ == "__main__":
    main()
