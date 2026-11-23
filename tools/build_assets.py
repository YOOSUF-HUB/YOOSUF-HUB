"""Generate the profile README SVG cards into ../assets.

Run:  python3 tools/build_assets.py
Edit the text in PROFILE / TILES / CHIPS below and re-run.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

# ── palette ──────────────────────────────────────────────────────────────
BG, BAR, LINE, PANEL = "#03080D", "#08111A", "#16232D", "#0A141C"
TEXT, DIM, MUTED = "#E6EDF2", "#8B98A4", "#52606B"
ACCENT, ACCENT_BG, OFF = "#58A6FF", "#0D1E33", "#132029"

STYLE = (
    "<style>"
    "text{font-family:'Geist Mono','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
    f"fill:{DIM};white-space:pre}}"
    f".p{{fill:{TEXT}}}.m{{fill:{MUTED}}}.a{{fill:{ACCENT}}}.w{{font-weight:600}}"
    ".s{font-family:Geist,Inter,'Segoe UI','Helvetica Neue',Arial,sans-serif}"
    "@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}.bl{animation:bl 1.1s steps(1,end) infinite}"
    "@keyframes pu{0%,100%{opacity:1}50%{opacity:.25}}.pu{animation:pu 2.4s ease-in-out infinite}"
    "@keyframes blf{0%,49%{fill-opacity:1}50%,100%{fill-opacity:0}}.blf{animation:blf 1.1s steps(1,end) infinite}"
    "@keyframes fl{0%,100%{opacity:.35}50%{opacity:1}}.fl{animation:fl 3s ease-in-out infinite}"
    "@media(prefers-reduced-motion:reduce){.bl,.blf,.pu,.fl{animation:none}}"
    "</style>"
)


def svg(w, h, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{STYLE}'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}'
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" fill="none" stroke="{LINE}"/></svg>'
    )


def t(x, y, s, size=12, cls="", anchor=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}"{c}{a} xml:space="preserve"{extra}>{escape(s)}</text>'


def code(x, y, parts, size=11):
    """One line of syntax-coloured code; parts = [(text, colour), ...] flowing as tspans."""
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">{spans}</text>'


def hline(y, x1=0, x2=880):
    return f'<line x1="{x1}" y1="{y+.5}" x2="{x2}" y2="{y+.5}" stroke="{LINE}"/>'


def vline(x, y1, y2):
    return f'<line x1="{x+.5}" y1="{y1}" x2="{x+.5}" y2="{y2}" stroke="{LINE}"/>'


# ── header ───────────────────────────────────────────────────────────────
PROFILE = {
    "first": "Yoosuf",
    "tagline": "AI engineering: LLMs, RAG and agents that ship.",
    "now": "building agentic RAG and MCP tools",
    "handle": "@YOOSUF-HUB",
    "site": "yoosufslife.vercel.app",
    "grid": [
        ("ROLE", "AI Engineer Intern"),
        ("FOCUS", "LLMs · RAG · Agents"),
        ("STUDYING", "BSc Data Science"),
        ("AT", "SLIIT"),
    ],
    "title": "Yoosuf Ahamed: AI Engineer Intern and Data Science undergraduate at SLIIT, "
             "building LLM, RAG and AI agent systems.",
}


def header():
    W, H = 880, 230
    p = PROFILE
    b = [f'<rect width="{W}" height="28" fill="{BAR}"/>', hline(27, 0, W)]
    b.append(t(12, 19, "yoosuf@hub", 12, "p w"))
    b.append(t(100, 19, "~/README.md", 12, "m"))
    b.append(f'<circle class="pu" cx="{W-196}" cy="14" r="3.5" fill="{ACCENT}"/>')
    b.append(t(W - 12, 19, p["site"] + " ↗", 12, "m", "end"))
    # left: name + tagline + key/values
    b.append(
        f'<text x="22" y="96" font-size="56" class="p s" style="font-weight:300;letter-spacing:-2px" '
        f'xml:space="preserve">{escape(p["first"])}<tspan class="blf" fill="{ACCENT}" dx="8" font-size="40">▌</tspan></text>'
    )
    b.append(t(24, 126, p["tagline"], 14, "p"))
    b.append(t(24, 170, "NOW", 11, "m") + t(104, 170, p["now"], 13, "p w"))
    b.append(t(24, 198, "HANDLE", 11, "m") + t(104, 198, p["handle"], 13, "a w"))
    # right: 2x2 grid
    gx, gw, top = 536, 172, 28
    rowh = (H - top) / 2
    b += [vline(gx, top, H), vline(gx + gw, top, H), hline(int(top + rowh), gx, W)]
    for i, (k, v) in enumerate(p["grid"]):
        x = gx + 16 + (i % 2) * gw
        y0 = top + (i // 2) * rowh
        b.append(t(x, int(y0 + 30), k, 10, "m"))
        b.append(t(x, int(y0 + 62), v, 13, "p w"))
    return svg(W, H, p["title"], "".join(b))


# ── project tiles ────────────────────────────────────────────────────────
TW, TH, ART = 440, 307, 231  # tile size, art height


def tile(n, name, right, caption, lang, title, art):
    b = [f'<rect width="{TW}" height="28" fill="{BAR}"/>', hline(27, 0, TW)]
    b.append(f'<rect x="8" y="6" width="16" height="16" fill="{ACCENT_BG}"/>')
    b.append(t(16, 18, str(n), 12, "a w", "middle"))
    b.append(t(32, 18, name, 12, "p w"))
    b.append(t(TW - 12, 18, right, 12, "m", "end"))
    b.append(
        f'<svg x="0" y="28" width="{TW}" height="{ART}" viewBox="0 0 {TW} {ART}" overflow="hidden">'
        f'<defs><pattern id="dg" width="12" height="12" patternUnits="userSpaceOnUse">'
        f'<rect width="2" height="2" fill="{LINE}"/></pattern></defs>'
        f'<rect width="{TW}" height="{ART}" fill="url(#dg)"/>{art}</svg>'
    )
    b.append(hline(259, 0, TW))
    b.append(t(16, 288, caption, 13, "p"))
    b.append(t(TW - 16, 288, lang, 12, "m", "end"))
    return svg(TW, TH, title, "".join(b))


def panel(x, y, w, h, stroke=LINE, fill=PANEL):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'


def art_idea_forge():
    # intake → score → keep → plan pipeline, with a score card
    stages = ["intake", "score", "keep", "plan"]
    a = []
    for i, s in enumerate(stages):
        x = 18 + i * 102
        on = i == 1
        a.append(panel(x, 18, 86, 30, ACCENT if on else LINE))
        a.append(t(x + 43, 37, s, 11, "a w" if on else "m", "middle"))
        if i < 3:
            a.append(t(x + 94, 37, "→", 11, "m", "middle"))
    a.append(panel(18, 62, 404, 118))
    a.append(t(30, 84, "idea: ", 11, "m") + t(72, 84, "subscription tracker for clinics", 11, "p"))
    rows = [("problem", 4), ("buyer", 3), ("timing", 3), ("feasibility", 5)]
    for i, (k, v) in enumerate(rows):
        y = 104 + i * 18
        a.append(t(30, y + 8, k, 10, "m"))
        for j in range(5):
            c = ACCENT if j < v else OFF
            a.append(f'<rect x="{130 + j*26}" y="{y}" width="22" height="9" fill="{c}"/>')
        a.append(t(268, y + 8, f"{v}/5", 10, "p"))
    a.append(t(410, 128, "3.8", 30, "a s", "end", ' style="font-weight:300"'))
    a.append(t(410, 146, "overall", 10, "m", "end"))
    a.append(t(18, 210, "a candid coach, then a tight MVP plan", 11, "m"))
    a.append(t(422, 210, "Groq", 11, "a", "end"))
    return a


def art_api_sentinel():
    a = [panel(18, 18, 236, 160)]
    lines = [
        ("POST /v1/payments", TEXT), ("  auth: none", ACCENT), ("  rate_limit: —", ACCENT),
        ("GET  /v1/users/{id}", TEXT), ("  returns: email, ssn", ACCENT), ("  errors: 500 only", DIM),
        ("DELETE /v1/users/{id}", TEXT), ("  idempotent: yes", DIM),
    ]
    for i, (s, c) in enumerate(lines):
        y = 38 + i * 18
        a.append(t(26, y, str(i + 1), 9, "m", extra=' style="opacity:.6"'))
        a.append(code(42, y, [(s, c)], 11))
        if c == ACCENT:
            a.append(f'<rect class="fl" x="244" y="{y-9}" width="4" height="11" fill="{ACCENT}" style="animation-delay:{i*.3:.1f}s"/>')
    checks = [("security", "2 high"), ("quality", "1 warn"), ("prod-ready", "no")]
    for i, (k, v) in enumerate(checks):
        y = 18 + i * 56
        a.append(panel(270, y, 152, 46, ACCENT if i == 0 else LINE))
        a.append(t(282, y + 18, k, 10, "m"))
        a.append(t(282, y + 36, v, 13, "a w" if i == 0 else "p w"))
    a.append(t(18, 210, "ask it what a senior reviewer would", 11, "m"))
    a.append(t(422, 210, "agentic RAG", 11, "a", "end"))
    return a


def art_mcp():
    a = [panel(18, 18, 404, 66)]
    a.append(code(30, 40, [("> ", MUTED), ("Generate a sprint risk report.", TEXT)]))
    a.append(code(30, 62, [("tool ", MUTED), ("generate_sprint_risk_report", ACCENT), ("()", TEXT), (" ▌", ACCENT)]))
    boxes = [("Claude", "desktop"), ("MCP server", "python"), ("SQLite", "tasks, risks")]
    for i, (k, v) in enumerate(boxes):
        x = 18 + i * 142
        on = i == 1
        a.append(panel(x, 104, 120, 54, ACCENT if on else LINE))
        a.append(t(x + 12, 126, k, 12, "a w" if on else "p w"))
        a.append(t(x + 12, 146, v, 10, "m"))
        if i < 2:
            a.append(t(x + 131, 136, "⇄", 13, "m", "middle"))
    a.append(t(18, 182, "audit_log  +1 row", 10, "m"))
    a.append(t(18, 210, "safe, predefined tools, not raw SQL", 11, "m"))
    a.append(t(422, 210, "MCP", 11, "a", "end"))
    return a


def art_brain():
    import math
    a = [panel(18, 18, 150, 160)]
    # stylised pixel "scan": an ellipse of cells with a hot region
    cx, cy, cell = 93, 98, 8
    for gy in range(-8, 9):
        for gx in range(-7, 8):
            d = (gx / 7.4) ** 2 + (gy / 8.6) ** 2
            if d > 1:
                continue
            hot = math.hypot(gx - 2.5, gy + 2) < 2.3
            shade = ["#1A2A38", "#22374A", "#2C4760"][(gx * 7 + gy * 3) % 3]
            fill = ACCENT if hot else shade
            cls = ' class="fl"' if hot else ""
            a.append(f'<rect{cls} x="{cx + gx*cell - 3}" y="{cy + gy*cell - 3}" width="{cell-1}" height="{cell-1}" fill="{fill}"/>')
    probs = [("glioma", .91), ("meningioma", .05), ("pituitary", .03), ("no tumor", .01)]
    for i, (k, v) in enumerate(probs):
        y = 30 + i * 36
        a.append(t(186, y, k, 10, "p" if i == 0 else "m"))
        a.append(t(422, y, f"{v:.2f}", 10, "a" if i == 0 else "m", "end"))
        a.append(f'<rect x="186" y="{y+7}" width="236" height="8" fill="{OFF}"/>')
        a.append(f'<rect x="186" y="{y+7}" width="{max(2, 236*v):.0f}" height="8" fill="{ACCENT if i == 0 else MUTED}"/>')
    a.append(t(186, 176, "accuracy", 10, "m") + t(422, 176, "97%", 13, "a w", "end"))
    a.append(t(18, 210, "MRI in, tumour class out", 11, "m"))
    a.append(t(422, 210, "streamlit", 11, "a", "end"))
    return a


TILES = [
    ("idea-forge", "idea-forge", "github.com/YOOSUF-HUB", "Agentic product coach for ideas", "typescript",
     "Idea Forge: agentic product coach that scores ideas and drafts MVP plans", art_idea_forge),
    ("api-sentinel", "api-sentinel-ai", "api-sentinel-ai.vercel.app", "Reviews API docs like a senior", "javascript",
     "API Sentinel AI: agentic RAG that reviews API documentation for security and production readiness", art_api_sentinel),
    ("mcp-pm", "ai-project-manager-mcp", "model context protocol", "Claude meets a real PM database", "python",
     "AI Project Manager MCP Server: connects Claude Desktop to a SQLite project database through safe tools", art_mcp),
    ("brain-tumor", "brain-tumor-cnn", "streamlit.app", "Classifies brain tumours from MRI", "tensorflow",
     "Brain Tumor Classification CNN: classifies glioma, meningioma and pituitary tumours from MRI scans", art_brain),
]


# ── link chips ───────────────────────────────────────────────────────────
def chip(label, icon, title):
    w = 48 + int(len(label) * 7.9) + 34
    b = [f'<g transform="translate(10 10)" fill="none" stroke="{DIM}" stroke-width="1.3">{icon}</g>',
         vline(36, 0, 36), t(48, 23, label, 13, "p"), t(w - 12, 23, "↗", 13, "m", "end")]
    return svg(w, 36, title, "".join(b))


GLOBE = '<circle cx="8" cy="8" r="7"/><ellipse cx="8" cy="8" rx="3" ry="7"/><line x1="1" y1="8" x2="15" y2="8"/>'
IN = ('<rect x="1" y="1" width="14" height="14" rx="2"/><line x1="4.5" y1="7" x2="4.5" y2="12"/>'
      '<circle cx="4.5" cy="4.3" r=".6" fill="#8B98A4"/><path d="M8 12V7m0 2.2c0-1.4 1-2.2 2-2.2s2 .6 2 2.2V12"/>')
CHIPS = [
    ("chip-site", "yoosufslife.vercel.app", GLOBE, "yoosufslife.vercel.app"),
    ("chip-linkedin", "linkedin/yoosuf-ahamed", IN, "Yoosuf Ahamed on LinkedIn"),
]


# ── terminal "whoami" (types itself out once, then the prompt blinks) ─────
TERMINAL = [
    ("$", "whoami"),
    ("", "yoosuf ahamed: ai engineer intern, data science @ SLIIT"),
    ("$", "cat focus.txt"),
    ("", "llms · rag · ai agents · backend systems"),
    ("$", "ls ~/learning"),
    ("", "langgraph/   model-context-protocol/   vector-databases/"),
    ("$", "echo $MOTTO"),
    ("", "real-world, production-ready ai. one repo at a time."),
]


def terminal():
    W, size, lh, top = 880, 13, 24, 58
    H = top + lh * (len(TERMINAL) + 1) + 8
    cw = size * 0.62                     # generous monospace advance
    b = [f'<rect width="{W}" height="28" fill="{BAR}"/>', hline(27, 0, W)]
    for i, c in enumerate([ACCENT, MUTED, MUTED]):
        b.append(f'<rect x="{12 + i*12}" y="10" width="8" height="8" fill="{c}"/>')
    b.append(t(56, 19, "zsh: yoosuf@hub", 12, "m"))
    b.append(t(W - 12, 19, "~", 12, "m", "end"))
    css, delay = [], 0.6
    for i, (prompt, txt) in enumerate(TERMINAL):
        y = top + i * lh
        x = 24
        if prompt:
            b.append(t(x, y, prompt, size, "a w"))
            x += 20
        b.append(t(x, y, txt, size, "p" if prompt else ""))
        width = int(len(txt) * cw) + 12
        if prompt:  # command: typed character by character
            n = len(txt)
            dur = n * 0.055
            css.append(f".c{i}{{animation:ty{i} {dur:.2f}s steps({n},end) {delay:.2f}s both}}"
                       f"@keyframes ty{i}{{to{{transform:translateX({width}px)}}}}")
        else:       # output: fades in at once
            dur = 0.18
            css.append(f".c{i}{{animation:out {dur}s linear {delay:.2f}s both}}")
        b.append(f'<rect class="cv c{i}" x="{x-1}" y="{y-size}" width="{width+2}" height="{size+6}" fill="{PANEL}"/>')
        if prompt:
            # typing cursor rides the cover's left edge, visible only while this line types
            css.append(f".k{i}{{animation:on {dur:.2f}s linear {delay:.2f}s}}")
            b.append(f'<g class="kc k{i}"><rect class="cv c{i}" x="{x-1}" y="{y-size+1}" width="8" height="{size+2}" fill="{ACCENT}"/></g>')
        delay += dur + (0.35 if prompt else 0.5)
    y = top + len(TERMINAL) * lh
    b.append(f'<g class="fin">{t(24, y, "$", size, "a w")}'
             f'<rect class="blc" x="44" y="{y-size+1}" width="8" height="{size+2}" fill="{ACCENT}"/></g>')
    css.append(f".fin{{opacity:0;animation:fin .01s linear {delay:.2f}s forwards}}@keyframes fin{{to{{opacity:1}}}}"
               ".blc{animation:bl 1.1s steps(1,end) infinite}"
               ".kc{opacity:0}@keyframes on{from,to{opacity:1}}@keyframes out{to{opacity:0}}"
               "@media(prefers-reduced-motion:reduce){.cv,.kc{display:none}.fin{opacity:1;animation:none}}")
    body = f'<rect y="28" width="{W}" height="{H-28}" fill="{PANEL}"/>' + "".join(b)
    return svg(W, H, "Terminal: whoami. Yoosuf Ahamed, AI engineer intern and data science student at SLIIT, "
               "focused on LLMs, RAG and AI agents.", f"<style>{''.join(css)}</style>{body}")


# ── agent pipeline (packets flow along the edges) ────────────────────────
PIPELINE = {
    "query": (20, 83, 120, "query", "user"),
    "plan": (180, 83, 150, "planner", "LLM · LangGraph"),
    "ret": (380, 44, 150, "retriever", "FAISS · embeddings"),
    "tool": (380, 122, 150, "tools", "MCP · APIs · SQL"),
    "syn": (580, 83, 150, "synthesizer", "grounded LLM"),
    "ans": (770, 83, 90, "answer", "+ sources"),
}


def pipeline():
    W, H, nh = 880, 230, 52
    b = [f'<rect width="{W}" height="28" fill="{BAR}"/>', hline(27, 0, W)]
    b.append(t(12, 19, "agent.pipeline", 12, "p w"))
    b.append(t(W - 12, 19, "how I build agents", 12, "m", "end"))
    b.append(f'<defs><pattern id="pg" width="12" height="12" patternUnits="userSpaceOnUse">'
             f'<rect width="2" height="2" fill="{LINE}"/></pattern>'
             f'<marker id="ah" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto">'
             f'<path d="M0 0L6 3L0 6z" fill="{MUTED}"/></marker></defs>')
    b.append(f'<rect y="28" width="{W}" height="162" fill="url(#pg)"/>')
    edges = ["M140 109H178", "M330 109H355V70H378", "M330 109H355V148H378",
             "M530 70H555V109H578", "M530 148H555V109H578", "M730 109H768"]
    for d in edges:
        b.append(f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ah)"/>')
    for d, begin in [("M140 109H355V70H555V109H770", "0s"), ("M140 109H355V148H555V109H770", "2s")]:
        b.append(f'<circle r="3.5" fill="{ACCENT}" opacity="0"><set attributeName="opacity" to="1" begin="{begin}"/>'
                 f'<animateMotion dur="4s" begin="{begin}" repeatCount="indefinite" path="{d}"/></circle>')
    for key, (x, y, w, name, sub) in PIPELINE.items():
        on = key == "plan"
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{nh}" fill="{PANEL}" stroke="{ACCENT if on else LINE}"/>')
        b.append(t(x + 12, y + 22, name, 12, "a w" if on else "p w"))
        b.append(t(x + 12, y + 40, sub, 10, "m"))
    b.append(hline(190, 0, W))
    b.append(t(16, 215, "plan → retrieve → act → answer", 13, "p"))
    b.append(t(W - 16, 215, "LangGraph · MCP · RAG", 12, "a", "end"))
    return svg(W, H, "Agent pipeline: a user query goes to an LLM planner, which retrieves context with FAISS "
               "and calls MCP tools, then a grounded LLM writes the answer with sources.", "".join(b))


# ── tech stack ───────────────────────────────────────────────────────────
STACK = [  # (row label, [(item, daily_driver), ...])
    ("LANGUAGES", [("python", 1), ("typescript", 0), ("sql", 1), ("java", 0), ("kotlin", 0)]),
    ("ML / DL", [("tensorflow", 1), ("pytorch", 0), ("scikit-learn", 1), ("pandas", 1), ("streamlit", 0)]),
    ("LLM / AGENTS", [("rag", 1), ("langgraph", 1), ("mcp", 1), ("faiss", 0), ("gemini", 0), ("groq", 0)]),
    ("BACKEND", [("fastapi", 1), ("flask", 0), ("postgres", 0), ("mongodb", 0), ("sqlite", 0)]),
    ("TOOLING", [("docker", 1), ("git", 1), ("linux", 0), ("vercel", 0), ("vscode", 0)]),
]


def stack():
    W, top, rh = 880, 28, 38
    H = top + rh * len(STACK) + 12
    b = [f'<rect width="{W}" height="28" fill="{BAR}"/>', hline(27, 0, W)]
    b.append(t(12, 19, "stack", 12, "p w"))
    b.append(f'<rect x="{W-178}" y="10" width="8" height="8" fill="{ACCENT}"/>' + t(W - 164, 19, "daily", 11, "m"))
    b.append(f'<rect x="{W-110}" y="10" width="8" height="8" fill="none" stroke="{MUTED}"/>' + t(W - 96, 19, "comfortable", 11, "m"))
    b.append(vline(150, top, H))
    for r, (label, items) in enumerate(STACK):
        y = top + 6 + r * rh
        if r:
            b.append(hline(y - 4, 0, W))
        b.append(t(16, y + 21, label, 10, "m"))
        x = 166
        for name, daily in items:
            w = int(len(name) * 7.9) + 22
            b.append(f'<rect x="{x}" y="{y+4}" width="{w}" height="24" fill="{ACCENT_BG if daily else PANEL}" '
                     f'stroke="{ACCENT if daily else LINE}"/>')
            b.append(t(x + w / 2, y + 20, name, 12, "a w" if daily else "p", "middle"))
            x += w + 8
    return svg(W, H, "Tech stack: " + "; ".join(f"{l.lower()}: {', '.join(i for i, _ in it)}" for l, it in STACK),
               "".join(b))


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header())
    for i, (slug, name, right, cap, lang, title, art) in enumerate(TILES, 1):
        (OUT / f"tile-{slug}.svg").write_text(tile(i, name, right, cap, lang, title, "".join(art())))
    (OUT / "terminal.svg").write_text(terminal())
    (OUT / "pipeline.svg").write_text(pipeline())
    (OUT / "stack.svg").write_text(stack())
    for slug, label, icon, title in CHIPS:
        (OUT / f"{slug}.svg").write_text(chip(label, icon, title))
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
