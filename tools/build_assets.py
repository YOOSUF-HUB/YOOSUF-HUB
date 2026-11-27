"""Generate the profile README SVG cards into ../assets/{dark,light}/.

Run:  python3 tools/build_assets.py
Edit the content blocks (PROFILE, TERMINAL, PROJECTS, PIPELINE, STACK, LINKS) and re-run.

Design system: "Monochrome editorial", taken from yoosufahamed.com (theme-mono.css):
every colour has r = g = b, hierarchy comes from value, weight and spacing, type is Figtree,
labels are uppercase with wide tracking, and sections are numbered "01 / NAME".
Fonts are subset and embedded (tools/fonts, SIL OFL) so GitHub renders them exactly.
"""
import base64
import json
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
FONTS = ROOT / "fonts"
METRICS = json.loads((FONTS / "metrics.json").read_text())
ICONS = json.loads((ROOT / "icons.json").read_text())
FIGTREE = base64.b64encode((FONTS / "figtree-subset.woff2").read_bytes()).decode()
MONO = base64.b64encode((FONTS / "jetbrains-mono-subset.woff2").read_bytes()).decode()

# ── tokens ───────────────────────────────────────────────────────────────
# bg      card surface            raised  inset panels / art wells
# line    hairlines, card borders strong  outlines that should read (buttons, nodes, edges)
# text    primary                 soft    body copy
# sec     secondary / captions    ter     labels, decoration (not for essential text)
# track   empty bar segments
THEMES = {
    "dark": dict(bg="#0A0A0A", raised="#111111", line="#222222", strong="#3A3A3A", track="#1C1C1C",
                 text="#FFFFFF", soft="#C8C8C8", sec="#8C8C8C", ter="#5C5C5C"),
    "light": dict(bg="#FFFFFF", raised="#F6F6F6", line="#E4E4E4", strong="#BDBDBD", track="#ECECEC",
                  text="#0A0A0A", soft="#2E2E2E", sec="#5E5E5E", ter="#9A9A9A"),
}
C = dict(THEMES["dark"])  # active palette; main() switches it per theme

W = 880          # full card width (half tiles are W / 2)
G = 0            # outer inset of full-width cards (flush, so they line up with the contribution wave)
GAP = 5          # half tiles are inset on their inner side only: 2 x GAP between them, and below each row
R = 12           # card corner radius
PAD = 24         # inner padding from the card edge
CAP = 0.16       # tracking for uppercase labels, in em

SANS = "Figtree,'Helvetica Neue',Arial,sans-serif"
MONOS = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


# ── primitives ───────────────────────────────────────────────────────────
def measure(s, size, weight=400, ls=0.0, mono=False):
    table = METRICS["mono" if mono else "sans"][str(min((300, 400, 500, 600, 700), key=lambda w: abs(w - weight)))]
    return sum(table.get(ch, 0.6) for ch in s) * size + ls * size * len(s)


def svg(w, h, title, body, mono=False, css=""):
    faces = (f"@font-face{{font-family:Figtree;font-weight:300 700;"
             f"src:url(data:font/woff2;base64,{FIGTREE}) format('woff2')}}")
    if mono:
        faces += (f"@font-face{{font-family:'JetBrains Mono';font-weight:100 800;"
                  f"src:url(data:font/woff2;base64,{MONO}) format('woff2')}}")
    style = (f"<style>{faces}text{{font-family:{SANS};white-space:pre}}.mo{{font-family:{MONOS}}}"
             "@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}.bl{animation:bl 1.1s steps(1,end) infinite}"
             "@keyframes pu{0%,100%{opacity:1}50%{opacity:.3}}.pu{animation:pu 2.4s ease-in-out infinite}"
             "@keyframes tw{0%,100%{opacity:.15}50%{opacity:.7}}.tw{animation:tw 4s ease-in-out infinite}"
             f"{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" fill="none"><title>{escape(title)}</title>{style}{body}</svg>')


def t(x, y, s, size=12, fill="text", weight=400, anchor=None, ls=0.0, mono=False, cls="", extra=""):
    """Text. fill is a palette key; ls is tracking in em. End-anchored text is nudged so tracking
    does not leave a gap after the last letter."""
    if anchor == "end" and ls:
        x += ls * size
    a = f' text-anchor="{anchor}"' if anchor else ""
    classes = " ".join(c for c in ("mo" if mono else "", cls) if c)
    c = f' class="{classes}"' if classes else ""
    w = f' font-weight="{weight}"' if weight != 400 else ""
    sp = f' letter-spacing="{ls * size:.2f}"' if ls else ""
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size}"{w}{sp} fill="{C[fill]}"{a}{c} '
            f'xml:space="preserve"{extra}>{escape(s)}</text>')


def label(x, y, s, fill="ter", size=9.5, anchor=None, weight=600):
    """Uppercase micro-label, the portfolio's caption style."""
    return t(x, y, s.upper(), size, fill, weight, anchor, CAP)


def rect(x, y, w, h, fill=None, stroke=None, rx=0, extra=""):
    f = C.get(fill, fill) if fill else "none"
    s = f' stroke="{C.get(stroke, stroke)}"' if stroke else ""
    r = f' rx="{rx}"' if rx else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r} fill="{f}"{s}{extra}/>'


def hline(y, x1, x2, color="line"):
    return f'<line x1="{x1:g}" y1="{y + .5:g}" x2="{x2:g}" y2="{y + .5:g}" stroke="{C[color]}"/>'


def vline(x, y1, y2, color="line"):
    return f'<line x1="{x + .5:g}" y1="{y1:g}" x2="{x + .5:g}" y2="{y2:g}" stroke="{C[color]}"/>'


def card(w, h, left=G, right=G, top=G, bottom=G):
    """The shared frame: hairline border, rounded corners, optional insets for the tile grid."""
    return rect(left + .5, top + .5, w - left - right - 1, h - top - bottom - 1, "bg", "line", R)


def well(x, y, w, h):
    return rect(x + .5, y + .5, w - 1, h - 1, "raised", "line", 8)


def wrap(s, width, size, weight=400):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if measure(trial, size, weight) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur] if cur else lines


def icon(name, x, y, size=16, color="soft"):
    """A 24x24 monochrome glyph from the portfolio's icon set (fill=currentColor), or a line icon."""
    inner = ICONS.get(name) or LINE_ICONS[name]
    stroke = name in LINE_ICONS
    attrs = (f'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
             if stroke else 'fill="currentColor"')
    return (f'<svg x="{x:g}" y="{y:g}" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'style="color:{C[color]}" {attrs}>{inner}</svg>')


# Line icons for things the portfolio set has no logo for (concepts, not brands).
LINE_ICONS = {
    "LangGraph": '<circle cx="5.5" cy="6" r="2.5"/><circle cx="18.5" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/>'
                 '<path d="M8 6h8M7 8.2l3.6 7.6M17 8.2l-3.6 7.6"/>',
    "RAG": '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h5M14 3l5 5v3M14 3v5h5"/>'
           '<circle cx="15.5" cy="15.5" r="3.2"/><path d="m18 18 3 3"/>',
    "MCP": '<path d="M8 3v5M16 3v5M5.5 8h13v3.5a6.5 6.5 0 0 1-13 0zM12 18v3"/>',
    "FAISS": '<circle cx="12" cy="12" r="7.5" stroke-dasharray="2 2.4"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/>'
             '<circle cx="5" cy="5" r="1" fill="currentColor"/><circle cx="19" cy="4.5" r="1" fill="currentColor"/>'
             '<circle cx="4" cy="19" r="1" fill="currentColor"/><circle cx="16" cy="9.5" r="1" fill="currentColor"/>'
             '<circle cx="9" cy="15" r="1" fill="currentColor"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    "code": '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10.5V17M8 7v.01M12 17v-6.5M12 13.2c0-1.6 1.1-2.7 2.5-2.7s2.5.9 2.5 2.7V17"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
}


# ── content ──────────────────────────────────────────────────────────────
SITE = "https://yoosufahamed.com"
SECTIONS = [  # (number, name, caption). The header's index strip lists these too.
    ("01", "Identity", "The person behind the systems."),
    ("02", "Selected work", "Five repositories, all open source."),
    ("03", "System architecture", "How I build agents."),
    ("04", "Technical toolkit", "What I reach for, by layer."),
    ("05", "GitHub activity", "Live numbers, refreshed daily."),
    ("06", "Connect", "Portfolio, code, network, inbox."),
]
NAV = ["Identity", "Work", "Architecture", "Toolkit", "Activity", "Connect"]

PROFILE = {
    "name": "YOOSUF",
    "role": "AI / ML ENGINEER",
    "facts": [("Now", "AI Engineer Intern · Guardians Solutions"),
              ("Study", "BSc (Hons) IT, Data Science · SLIIT")],
    "motto": ("Human curiosity.", "Machine intelligence."),
    "cta": "YOOSUFAHAMED.COM",
    "title": "Yoosuf Ahamed, AI / ML Engineer. Human curiosity. Machine intelligence. "
             "AI Engineer Intern at Guardians Solutions and BSc (Hons) IT, Data Science student at SLIIT. "
             "Portfolio: yoosufahamed.com",
}


# ── section label (transparent strip: "01 / IDENTITY ───── caption") ─────
def section(num, name, caption):
    H = 52
    y = 33
    b = [label(G + 2, y, num, "sec", 11, weight=500)]
    x = G + 2 + measure(num.upper(), 11, 500, CAP)
    b.append(label(x + 6, y, "/", "ter", 11, weight=500))
    x += 6 + measure("/", 11, 500, CAP) + 6
    b.append(label(x, y, name, "text", 11))
    x += measure(name.upper(), 11, 600, CAP)
    cap_w = measure(caption, 12)
    b.append(t(W - G - 2, y, caption, 12, "sec", anchor="end"))
    b.append(hline(y - 4, x + 16, W - G - 2 - cap_w - 16, "strong"))
    return svg(W, H, f"{num} / {name}: {caption}", "".join(b))


# ── header / hero ────────────────────────────────────────────────────────
def header():
    H = 340
    p = PROFILE
    b = [card(W, H)]
    # starfield: the portfolio's night sky, kept faint
    rnd = random.Random(11)
    for i in range(46):
        x, y = rnd.uniform(G + 14, W - G - 14), rnd.uniform(62, H - 20)
        r = rnd.choice((.6, .7, .8, 1.0))
        cls = ' class="tw"' if i % 6 == 0 else ""
        delay = f' style="animation-delay:{rnd.uniform(0, 4):.1f}s"' if cls else ""
        b.append(f'<circle{cls}{delay} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{C["text"]}" '
                 f'opacity="{rnd.uniform(.12, .38):.2f}"/>')
    # index strip, like the site nav: "01/ IDENTITY  02/ WORK ..."
    x = G + PAD
    for i, name in enumerate(NAV, 1):
        n = f"{i:02d}/"
        b.append(t(x, 38, n, 8, "ter", 500))
        x += measure(n, 8, 500) + 4
        b.append(t(x, 42, name.upper(), 10, "soft", 600, ls=.06))
        x += measure(name.upper(), 10, 600, .06) + 18
    b.append(t(W - G - PAD, 42, p["cta"] + "  ↗", 10, "text", 600, "end", .06))
    b.append(hline(60, G + 1, W - G - 1))
    # left: role + giant name with a blinking underscore
    b.append(t(G + PAD - 2, 120, p["role"], 30, "text", 600, ls=-.01))
    nx, limit = G + PAD - 6, 600 - 24 - 28          # stop short of the column divider
    k = measure(p["name"], 1, 500, -.04)
    size = min(140, int((limit - nx - 4) / (k + .40)))
    name_w = k * size
    b.append(t(nx, 290, p["name"], size, "text", 500, ls=-.04))
    b.append(f'<rect class="bl" x="{nx + name_w + 4:.1f}" y="{290 - size * .085:.1f}" width="{size * .40:.1f}" '
             f'height="{size * .085:.1f}" fill="{C["text"]}"/>')
    # right column: facts, motto, button
    cx = 600
    b.append(vline(cx - 24, 84, H - G - 24))
    y = 100
    for k, v in p["facts"]:
        b.append(label(cx, y, k))
        b.append(t(cx, y + 19, v, 12.5, "soft", 500))
        y += 48
    b.append(t(cx, 226, p["motto"][0], 21, "text", 500, ls=-.01))
    b.append(t(cx, 252, p["motto"][1], 21, "sec", 500, ls=-.01))
    bw = measure(p["cta"] + "  ↗", 10, 600, .08) + 32
    b.append(rect(cx + .5, 274.5, bw, 36, None, "text", 8))
    b.append(t(cx + 16, 296, p["cta"] + "  ↗", 10, "text", 600, ls=.08))
    return svg(W, H, p["title"], "".join(b))


# ── terminal intro (types itself out once, then the prompt blinks) ───────
TERMINAL = [  # (command, [output lines])
    ("whoami", ["Yoosuf Ahamed · AI engineer intern @ Guardians Solutions",
                "BSc (Hons) IT, Data Science @ SLIIT"]),
    ("cat current_focus", ["llm applications · agentic ai · rag · tool calling"]),
    ("ls building/", ["open-analyst/      conversational data analyst, in active development"]),
    ("ls exploring/", ["langgraph/   model-context-protocol/   vector-databases/"]),
]


def terminal():
    size, lh, top = 13, 25, 92
    rows = sum(1 + len(out) for _, out in TERMINAL)
    H = top + lh * rows + 30
    cw = measure("a", size, mono=True)
    b = [card(W, H)]
    for i in range(3):
        b.append(f'<circle cx="{G + PAD + 4 + i * 16}" cy="33" r="4.5" stroke="{C["strong"]}"/>')
    b.append(t(W / 2, 37, "yoosuf@hub — zsh", 11, "sec", anchor="middle", mono=True))
    b.append(t(W - G - PAD, 37, "~/identity", 11, "ter", anchor="end", mono=True))
    b.append(hline(56, G + 1, W - G - 1))
    css, delay, row = [], 0.6, 0
    x0 = G + PAD + 4
    for cmd, outs in TERMINAL:
        for j, txt in enumerate([cmd] + outs):
            y = top + row * lh
            typed = j == 0
            x = x0
            if typed:
                b.append(t(x, y, "$", size, "ter", 500, mono=True))
                x += 2 * cw
            b.append(t(x, y, txt, size, "text" if typed else ("soft" if j == 1 else "sec"), 500 if typed else 400, mono=True))
            width = len(txt) * cw + 10
            if typed:
                dur = len(txt) * 0.055
                css.append(f".c{row}{{animation:ty{row} {dur:.2f}s steps({len(txt)},end) {delay:.2f}s both}}"
                           f"@keyframes ty{row}{{to{{transform:translateX({width:.1f}px)}}}}"
                           f".k{row}{{animation:on {dur:.2f}s linear {delay:.2f}s}}")
            else:
                dur = 0.16
                css.append(f".c{row}{{animation:out {dur}s linear {delay:.2f}s both}}")
            b.append(f'<rect class="cv c{row}" x="{x - 1:.1f}" y="{y - size}" width="{width + 2:.1f}" '
                     f'height="{size + 6}" fill="{C["bg"]}"/>')
            if typed:
                b.append(f'<g class="kc k{row}"><rect class="cv c{row}" x="{x - 1:.1f}" y="{y - size + 1}" '
                         f'width="{cw:.1f}" height="{size + 3}" fill="{C["text"]}"/></g>')
            delay += dur + (0.3 if typed else 0.25)
            row += 1
        delay += 0.25
    y = top + rows * lh
    b.append(f'<g class="fin">{t(x0, y, "$", size, "ter", 500, mono=True)}'
             f'<rect class="bl" x="{x0 + 2 * cw:.1f}" y="{y - size + 1}" width="{cw:.1f}" height="{size + 3}" '
             f'fill="{C["text"]}"/></g>')
    css.append(f".fin{{opacity:0;animation:fin .01s linear {delay:.2f}s forwards}}@keyframes fin{{to{{opacity:1}}}}"
               ".kc{opacity:0}@keyframes on{from,to{opacity:1}}@keyframes out{to{opacity:0}}"
               "@media(prefers-reduced-motion:reduce){.cv,.kc{display:none}.fin{opacity:1}}")
    title = "Terminal. whoami: " + "; ".join(f"{c}: {' / '.join(o)}" for c, o in TERMINAL)
    return svg(W, H, title, "".join(b), mono=True, css="".join(css))


# ── project tiles ────────────────────────────────────────────────────────
def pill(x, y, s, h=22):
    w = measure(s, 10.5, 500, .02) + 20
    return rect(x + .5, y + .5, w, h, None, "strong", 6) + t(x + 10.5, y + 15, s, 10.5, "soft", 500, ls=.02), w


def pills(x, y, tags, max_x):
    out = []
    for s in tags:
        p, w = pill(x, y, s)
        if x + w > max_x:
            break
        out.append(p)
        x += w + 8
    return "".join(out)


def mono_line(x, y, parts, size=10.5):
    spans = "".join(f'<tspan fill="{C[c]}">{escape(s)}</tspan>' for s, c in parts)
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" class="mo" xml:space="preserve">{spans}</text>'


def bar_cells(x, y, n, on, w=20, h=7, gap=4):
    return "".join(rect(x + i * (w + gap), y, w, h, "text" if i < on else "track", rx=1.5) for i in range(n))


def art_open_analyst(w, h):
    a = [label(16, 24, "Example session")]
    a.append(rect(16.5, 36.5, 300, 30, "bg", "strong", 6))
    a.append(mono_line(28, 56, [("› ", "sec"), ("which region grew fastest last quarter?", "text")], 11))
    steps = [("load", "sales.csv", "12,480 rows"), ("group", "region, quarter", "4 × 2"),
             ("compute", "pct_change()", "exact"), ("plot", "bar chart", "done")]
    for i, (verb, arg, res) in enumerate(steps):
        y = 92 + i * 18
        a.append(mono_line(28, y, [(f"{verb:<9}", "soft"), (arg, "sec")]))
        a.append(t(316, y, res, 10.5, "ter", anchor="end", mono=True))
    a.append(vline(336, 36, 160))
    a.append(label(352, 50, "Insight"))
    a.append(t(350, 92, "+18%", 38, "text", 300, ls=-.02))
    a.append(t(352, 116, "north grew fastest,", 11.5, "soft"))
    a.append(t(352, 132, "quarter over quarter", 11.5, "sec"))
    a.append(t(352, 156, "numbers: pandas · words: LLM", 9.5, "ter"))
    a.append(hline(176, 16, w - 16))
    bars = [("north", 18), ("west", 11), ("east", 6), ("south", -3)]
    colw = (w - 32) / 4
    for i, (k, v) in enumerate(bars):
        x = 16 + i * colw
        a.append(t(x, 202, k, 11, "soft" if i == 0 else "sec", 500))
        a.append(t(x + colw - 16, 202, f"{v:+d}%", 11, "text" if i == 0 else "sec", 600 if i == 0 else 400, "end"))
        a.append(rect(x, 214, colw - 16, 6, "track", rx=1.5))
        a.append(rect(x, 214, (colw - 16) * abs(v) / 18, 6, "text" if i == 0 else ("ter" if v < 0 else "sec"), rx=1.5))
    a.append(t(16, 240, "QoQ revenue growth by region", 9.5, "ter"))
    return a


def art_idea_forge(w, h):
    a = []
    x = 14
    for i, s in enumerate(["intake", "score", "plan"]):
        sw = measure(s, 10.5, 500) + 22
        on = i == 1
        a.append(rect(x + .5, 12.5, sw, 22, "bg", "text" if on else "strong", 6))
        a.append(t(x + 11, 27, s, 10.5, "text" if on else "sec", 500))
        x += sw
        if i < 2:
            a.append(t(x + 9, 27, "→", 10.5, "ter", anchor="middle"))
            x += 18
    a.append(label(w - 14, 27, "Example scorecard", anchor="end"))
    rows = [("clarity", 4), ("feasibility", 5), ("novelty", 3), ("demand", 3)]
    for i, (k, v) in enumerate(rows):
        y = 58 + i * 21
        a.append(t(14, y + 7, k, 10.5, "sec"))
        a.append(bar_cells(96, y, 5, v))
        a.append(t(222, y + 7, f"{v}/5", 10.5, "soft", 500))
    a.append(vline(258, 50, 132))
    a.append(t(w - 14, 104, "3.8", 40, "text", 300, "end", -.02))
    a.append(label(w - 14, 124, "Overall", anchor="end"))
    return a


def art_api_sentinel(w, h):
    a = []
    lines = [("POST /v1/payments", "soft", 0), ("  auth: none", "text", 1), ("  rate_limit: —", "text", 1),
             ("GET  /v1/users/{id}", "soft", 0), ("  returns: email, ssn", "text", 1),
             ("  errors: 500 only", "sec", 0), ("DELETE /v1/users/{id}", "soft", 0)]
    for i, (s, c, flag) in enumerate(lines):
        y = 24 + i * 16.5
        a.append(t(14, y, str(i + 1), 9, "ter", mono=True))
        a.append(mono_line(30, y, [(s, c)], 10.5))
        if flag:
            a.append(f'<rect class="pu" x="226" y="{y - 8.5}" width="3" height="11" rx="1" fill="{C["text"]}" '
                     f'style="animation-delay:{i * .3:.1f}s"/>')
    a.append(vline(244, 12, h - 12))
    checks = [("Security", "2 high", 1), ("Quality", "1 warning", 0), ("Prod-ready", "no", 0)]
    for i, (k, v, hot) in enumerate(checks):
        y = 30 + i * 42
        a.append(label(258, y, k))
        a.append(t(258, y + 18, v, 13, "text" if hot else "soft", 600 if hot else 500))
    return a


def art_mcp(w, h):
    a = [mono_line(14, 26, [("› ", "sec"), ("Generate a sprint risk report.", "text")], 11)]
    a.append(mono_line(14, 45, [("tool ", "ter"), ("generate_sprint_risk_report", "soft"), ("()", "sec")], 10.5))
    boxes = [("Claude", "desktop"), ("MCP server", "python"), ("SQLite", "tasks · risks")]
    bw, gap = 104, (w - 28 - 3 * 104) / 2
    for i, (k, v) in enumerate(boxes):
        x = 14 + i * (bw + gap)
        on = i == 1
        a.append(rect(x + .5, 62.5, bw, 46, "bg", "text" if on else "strong", 8))
        a.append(t(x + 12, 82, k, 12, "text", 600))
        a.append(t(x + 12, 99, v, 10, "sec"))
        if i < 2:
            a.append(t(x + bw + gap / 2, 90, "⇄", 13, "ter", anchor="middle", mono=True))
    a.append(t(14, 130, "audit_log  +1 row", 10, "ter", mono=True))
    a.append(label(w - 14, 130, "Safe tools, not raw SQL", anchor="end"))
    return a


def art_brain(w, h):
    a = []
    cx, cy, cell = 64, 72, 6.5
    shades = ["#2A2A2A", "#333333", "#3D3D3D"] if CURRENT[0] == "dark" else ["#D6D6D6", "#CCCCCC", "#C2C2C2"]
    for gy in range(-8, 9):
        for gx in range(-7, 8):
            if (gx / 7.4) ** 2 + (gy / 8.6) ** 2 > 1:
                continue
            hot = math.hypot(gx - 2.5, gy + 2) < 2.3
            fill = C["text"] if hot else shades[(gx * 7 + gy * 3) % 3]
            cls = ' class="pu"' if hot else ""
            a.append(f'<rect{cls} x="{cx + gx * cell - 3:.1f}" y="{cy + gy * cell - 3:.1f}" '
                     f'width="{cell - 1:.1f}" height="{cell - 1:.1f}" rx="1" fill="{fill}"/>')
    x0 = 140
    a.append(label(x0, 22, "Example prediction"))
    probs = [("glioma", .91), ("meningioma", .05), ("pituitary", .03), ("no tumor", .01)]
    for i, (k, v) in enumerate(probs):
        y = 44 + i * 20
        a.append(t(x0, y, k, 10.5, "soft" if i == 0 else "sec", 500 if i == 0 else 400))
        a.append(t(w - 14, y, f"{v:.2f}", 10.5, "text" if i == 0 else "sec", 600 if i == 0 else 400, "end", mono=True))
        a.append(rect(x0 + 78, y - 6, w - 14 - 40 - x0 - 78, 5, "track", rx=1.5))
        a.append(rect(x0 + 78, y - 6, max(2, (w - 14 - 40 - x0 - 78) * v), 5, "text" if i == 0 else "ter", rx=1.5))
    a.append(hline(116, x0, w - 14))
    a.append(label(x0, 134, "Accuracy"))
    a.append(t(w - 14, 135, "97%", 14, "text", 600, "end"))
    return a


PROJECTS = [  # descriptions are the portfolio's / repos' own wording
    dict(slug="open-analyst", url="https://github.com/YOOSUF-HUB/Open-Analyst", kind="Featured",
         status="In active development", name="Open Analyst", sub="Open-source conversational data analyst",
         desc="Upload a dataset, ask a question, and get statistics, charts, and plain-language insights without code.",
         tags=["FastAPI", "React", "PostgreSQL", "LLM"], art=art_open_analyst),
    dict(slug="idea-forge", url="https://github.com/YOOSUF-HUB/idea-forge", kind="Agentic AI",
         name="Idea Forge", sub="Agentic product coach",
         desc="Scores product ideas on clarity, feasibility, novelty, and demand, then drafts a tight MVP plan.",
         tags=["Next.js", "TypeScript", "Groq", "Agent SDK"], art=art_idea_forge),
    dict(slug="api-sentinel", url="https://github.com/YOOSUF-HUB/API-Sentinel-AI-", kind="Agentic RAG",
         name="API Sentinel AI", sub="API security & documentation analysis",
         desc="Reviews API documentation like a senior technical reviewer: security, quality and production readiness.",
         tags=["LLM", "RAG", "FastAPI", "API Security"], art=art_api_sentinel),
    dict(slug="mcp-pm", url="https://github.com/YOOSUF-HUB/AI-Project-Manager-MCP-Server", kind="MCP",
         name="AI Project Manager", sub="MCP server for Claude Desktop",
         desc="An MCP server that lets Claude Desktop run project management actions through safe, predefined tools.",
         tags=["MCP", "Python", "SQLite", "Claude Desktop"], art=art_mcp),
    dict(slug="brain-tumor", url="https://github.com/YOOSUF-HUB/Brain_Tumor_Classification_CNN", kind="Deep learning",
         name="Brain Tumor Classification", sub="CNN on MRI scans",
         desc="Detects and classifies brain tumors (glioma, meningioma, pituitary) from MRI scans with 97% accuracy.",
         tags=["TensorFlow", "Keras", "Streamlit", "CNN"], art=art_brain),
]


def project_title(p):
    return f"{p['name']}: {p['sub']}. {p['desc']} Built with {', '.join(p['tags'])}."


def tile(n, p):
    TW, H = W // 2, 344 + 2 * GAP
    left = n % 2 == 0                      # 02, 04 sit on the left; 03, 05 on the right
    li, ri = (0, GAP) if left else (GAP, 0)
    x0, x1 = li + PAD - 4, TW - ri - PAD + 4
    b = [card(TW, H, li, ri, 0, 2 * GAP)]
    b.append(label(x0, 38, f"{n:02d}", "sec", weight=500))
    b.append(label(x0 + 22, 38, f"/  {p['kind']}"))
    b.append(t(x1, 39, "↗", 13, "sec", anchor="end"))
    b.append(t(x0, 72, p["name"], 21, "text", 600, ls=-.01))
    for i, line in enumerate(wrap(p["desc"], x1 - x0, 12.5)[:2]):
        b.append(t(x0, 96 + i * 18, line, 12.5, "sec"))
    aw, ah = x1 - x0, 146
    b.append(well(x0, 130, aw, ah))
    b.append(f'<g transform="translate({x0} 130)">{"".join(p["art"](aw, ah))}</g>')
    b.append(pills(x0, 292, p["tags"], x1))
    return svg(TW, H, project_title(p), "".join(b), mono=True)


def featured(p):
    H = 344 + 2 * GAP
    b = [card(W, H, bottom=2 * GAP)]
    x0 = G + PAD - 4
    b.append(label(x0, 38, "01", "sec", weight=500))
    b.append(label(x0 + 22, 38, f"/  {p['kind']}"))
    sx = W - G - PAD + 4
    b.append(label(sx, 38, p["status"], "soft", anchor="end"))
    b.append(f'<circle class="pu" cx="{sx - measure(p["status"].upper(), 9.5, 600, CAP) - 10:.1f}" cy="34.5" r="3" '
             f'fill="{C["text"]}"/>')
    b.append(t(x0, 86, p["name"], 34, "text", 600, ls=-.02))
    b.append(t(x0, 112, p["sub"], 13.5, "soft", 500))
    for i, line in enumerate(wrap(p["desc"], 290, 12.5)[:4]):
        b.append(t(x0, 146 + i * 19, line, 12.5, "sec"))
    b.append(label(x0, 212, "Approach"))
    b.append(t(x0, 232, "pandas computes the numbers; the LLM explains them.", 11.5, "soft"))
    b.append(t(x0, 262, "github.com/YOOSUF-HUB/Open-Analyst  ↗", 11, "sec", 500))
    b.append(pills(x0, 292, p["tags"], 330))
    ax, ay, aw, ah = 350, 56, W - G - PAD + 4 - 350, 258
    b.append(well(ax, ay, aw, ah))
    b.append(f'<g transform="translate({ax} {ay})">{"".join(p["art"](aw, ah))}</g>')
    return svg(W, H, project_title(p), "".join(b), mono=True)


# ── agent pipeline (packets flow along the edges) ────────────────────────
PIPELINE = {  # key: (x, y, w, name, sub, stage)
    "query": (29, 130, 120, "Query", "user", "01  Input"),
    "plan": (185, 130, 150, "Planner", "LLM · LangGraph", "02  Plan"),
    "ret": (375, 94, 160, "Retriever", "FAISS · embeddings", "03  Retrieve · act"),
    "tool": (375, 170, 160, "Tools", "MCP · APIs · SQL", None),
    "syn": (575, 130, 150, "Synthesizer", "grounded LLM", "04  Synthesize"),
    "ans": (761, 130, 90, "Answer", "+ sources", "05  Output"),
}


def pipeline():
    H, nh = 306, 52
    b = [card(W, H)]
    b.append(label(G + PAD, 38, "Agent pipeline", "soft"))
    b.append(t(W - G - PAD, 38, "plan → retrieve → act → answer", 11.5, "sec", anchor="end"))
    b.append(hline(56, G + 1, W - G - 1))
    b.append(f'<defs><marker id="ah" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="5" markerHeight="5" '
             f'orient="auto"><path d="M0 0L6 3L0 6z" fill="{C["sec"]}"/></marker></defs>')
    for key, (x, y, w, name, sub, stage) in PIPELINE.items():
        if stage:
            b.append(label(x, 82, stage))
    mid = 156
    edges = [f"M149 {mid}H183", f"M335 {mid}H355V120H373", f"M335 {mid}H355V196H373",
             f"M535 120H555V{mid}H573", f"M535 196H555V{mid}H573", f"M725 {mid}H759"]
    for d in edges:
        b.append(f'<path d="{d}" stroke="{C["strong"]}" marker-end="url(#ah)"/>')
    for d, begin in [(f"M149 {mid}H355V120H555V{mid}H761", "0s"), (f"M149 {mid}H355V196H555V{mid}H761", "2s")]:
        b.append(f'<circle r="3" fill="{C["text"]}" opacity="0"><set attributeName="opacity" to="1" begin="{begin}"/>'
                 f'<animateMotion dur="4s" begin="{begin}" repeatCount="indefinite" path="{d}"/></circle>')
    for key, (x, y, w, name, sub, stage) in PIPELINE.items():
        on = key == "plan"
        b.append(rect(x + .5, y + .5, w, nh, "raised", "text" if on else "strong", 8))
        b.append(t(x + 13, y + 23, name, 12.5, "text", 600))
        b.append(t(x + 13, y + 40, sub, 10.5, "sec"))
    b.append(hline(252, G + 1, W - G - 1))
    b.append(label(G + PAD, 282, "Built with"))
    b.append(t(G + PAD + 82, 282, "LangGraph · MCP · RAG · FAISS · FastAPI", 11.5, "soft", 500))
    b.append(f'<circle cx="{W - G - PAD - measure("DATA FLOW", 9.5, 600, CAP) - 12:.1f}" cy="278.5" r="3" fill="{C["text"]}"/>')
    b.append(label(W - G - PAD, 282, "Data flow", anchor="end"))
    return svg(W, H, "System architecture: a user query goes to an LLM planner (LangGraph), which retrieves "
               "context with FAISS embeddings and calls MCP tools, APIs and SQL; a grounded LLM synthesizer "
               "writes the answer with sources.", "".join(b))


# ── technical toolkit ────────────────────────────────────────────────────
STACK = [  # only tools listed on the portfolio or already in this README
    ("AI & Machine Learning", ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "OpenCV", "Pandas", "NumPy"]),
    ("LLM Engineering", ["LangChain", "LangGraph", "Hugging Face", "Ollama", "RAG", "MCP"]),
    ("Backend & APIs", ["Python", "FastAPI", "Flask", "Node.js", "TypeScript"]),
    ("Databases & Vector Search", ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "FAISS"]),
    ("Infrastructure & Dev Tools", ["Docker", "Git", "GitHub Actions", "AWS", "Claude Code"]),
]


def stack():
    top, step = 154, 29
    H = top + step * (max(len(i) for _, i in STACK) - 1) + 44
    total = sum(len(i) for _, i in STACK)
    b = [card(W, H)]
    b.append(label(G + PAD, 38, "Toolkit", "soft"))
    b.append(label(W - G - PAD, 38, f"{total} tools · {len(STACK)} categories", "sec", anchor="end"))
    b.append(hline(56, G + 1, W - G - 1))
    colw = (W - 2 * G) / len(STACK)
    for c, (cat, items) in enumerate(STACK):
        x = G + c * colw
        if c:
            b.append(vline(round(x), 57, H - G - 1))
        ix = x + 18
        b.append(label(ix, 82, f"{c + 1:02d}", "sec", weight=500))
        for i, line in enumerate(wrap(cat, colw - 30, 12.5, 600)[:2]):
            b.append(t(ix, 104 + i * 17, line, 12.5, "text", 600))
        for i, name in enumerate(items):
            y = top + i * step
            b.append(icon(name, ix, y - 12, 15))
            b.append(t(ix + 24, y, name, 12, "soft"))
    b.append(hline(130, G + 1, W - G - 1))
    title = "Technical toolkit. " + " ".join(f"{cat}: {', '.join(i)}." for cat, i in STACK)
    return svg(W, H, title, "".join(b))


# ── connect ──────────────────────────────────────────────────────────────
LINKS = [  # (slug, label, icon, href, title)
    ("site", "yoosufahamed.com", "globe", SITE, "Portfolio: yoosufahamed.com"),
    ("github", "github.com/YOOSUF-HUB", "code", "https://github.com/YOOSUF-HUB", "GitHub: YOOSUF-HUB"),
    ("linkedin", "in/yoosuf-ahamed", "linkedin", "https://www.linkedin.com/in/yoosuf-ahamed/", "LinkedIn: Yoosuf Ahamed"),
    ("email", "yahamed95@gmail.com", "mail", "mailto:yahamed95@gmail.com", "Email: yahamed95@gmail.com"),
]


def connect():
    H = 196
    b = [card(W, H)]
    x0 = G + PAD
    b.append(t(x0 - 2, 84, "Let's start", 38, "text", 500, ls=-.02))
    b.append(t(x0 - 2, 128, "creating together.", 38, "sec", 500, ls=-.02))
    b.append(label(x0, 168, "Portfolio · GitHub · LinkedIn · Email"))
    cx = 560
    b.append(vline(cx - 24, 40, H - G - 26))
    b.append(label(cx, 52, "Open to"))
    for i, line in enumerate(wrap("AI and ML engineering roles, research collaborations and freelance projects.",
                                  W - G - PAD - cx, 12.5)):
        b.append(t(cx, 72 + i * 18, line, 12.5, "soft"))
    b.append(label(cx, 128, "Based in"))
    b.append(t(cx, 148, "Sri Lanka, working remotely", 12.5, "soft"))
    b.append(t(cx, 166, "across time zones.", 12.5, "soft"))
    return svg(W, H, "Let's start creating together. Open to AI and ML engineering roles, research collaborations "
               "and freelance projects. Based in Sri Lanka, working remotely across time zones.", "".join(b))


def chip(text, ico, title):
    h = 40
    w = round(56 + measure(text, 12.5, 500) + 14 + measure("↗", 12.5) + 14)
    b = [rect(.5, .5, w - 1, h - 1, None, "strong", 8)]
    b.append(icon(ico, 14, 12, 16, "soft"))
    b.append(vline(42, 0, h, "strong"))
    b.append(t(56, 25, text, 12.5, "text", 500))
    b.append(t(w - 14, 25, "↗", 12.5, "sec", anchor="end"))
    return svg(w, h, title, "".join(b))


# ── build ────────────────────────────────────────────────────────────────
CURRENT = ["dark"]


def use_theme(name):
    """Point the shared palette at a theme. build_stats.py calls this too."""
    C.clear()
    C.update(THEMES[name])
    CURRENT[0] = name


def main():
    for theme in THEMES:
        use_theme(theme)
        d = OUT / theme
        d.mkdir(parents=True, exist_ok=True)
        files = {"header.svg": header(), "terminal.svg": terminal(), "pipeline.svg": pipeline(),
                 "stack.svg": stack(), "connect.svg": connect(),
                 f"tile-{PROJECTS[0]['slug']}.svg": featured(PROJECTS[0])}
        for n, p in enumerate(PROJECTS[1:], 2):
            files[f"tile-{p['slug']}.svg"] = tile(n, p)
        for num, name, cap in SECTIONS:
            files[f"section-{num}.svg"] = section(num, name, cap)
        for slug, text, ico, href, title in LINKS:
            files[f"chip-{slug}.svg"] = chip(text, ico, title)
        for name, content in files.items():
            (d / name).write_text(content)
    print("wrote", len(files), "cards x", len(THEMES), "themes")


if __name__ == "__main__":
    main()
