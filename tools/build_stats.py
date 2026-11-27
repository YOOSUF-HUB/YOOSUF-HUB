"""Fetch live GitHub stats and render assets/{dark,light}/stats.svg in the README card style.

Run locally:  GITHUB_TOKEN=$(gh auth token) python3 tools/build_stats.py
In CI the workflow passes GITHUB_TOKEN (or the optional STATS_TOKEN secret).
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

from build_assets import (C, CAP, OUT, PAD, THEMES, W, card, hline, label, measure, rect, svg, t,
                          use_theme, vline)

USER = os.environ.get("STATS_USER", "YOOSUF-HUB")
# Notebook bytes are mostly saved outputs, and markup inflates web repos; leave them out of the bar.
EXCLUDE_LANGS = {"Jupyter Notebook", "HTML", "CSS", "SCSS"}
TOP_LANGS = 6

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
    pullRequests { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "readme-stats-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def summarise(u):
    repos = u["repositories"]
    langs = {}
    for node in repos["nodes"]:
        for e in node["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in EXCLUDE_LANGS:
                langs[name] = langs.get(name, 0) + e["size"]
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: -kv[1])
    top = [(n, b / total) for n, b in ranked[:TOP_LANGS]]
    rest = 1 - sum(p for _, p in top)
    if rest > 0.005:
        top.append(("other", rest))
    cc = u["contributionsCollection"]
    return {
        "numbers": [
            ("Contributions", cc["contributionCalendar"]["totalContributions"], "past year"),
            ("Commits", cc["totalCommitContributions"], "past year"),
            ("Pull requests", u["pullRequests"]["totalCount"], "all time"),
            ("Stars", sum(n["stargazerCount"] for n in repos["nodes"]), f"across {repos['totalCount']} repos"),
        ],
        "langs": top,
    }


def shades():
    """Grey ramp for the language bar, brightest first, in the active theme."""
    dark = C["text"] == "#FFFFFF"
    return (["#FFFFFF", "#C8C8C8", "#9A9A9A", "#737373", "#555555", "#3D3D3D", "#2A2A2A"] if dark else
            ["#0A0A0A", "#3A3A3A", "#5E5E5E", "#808080", "#A3A3A3", "#C4C4C4", "#DEDEDE"])


def render(s, updated):
    H = 284
    ramp = shades()
    b = [card(W, H)]
    b.append(f'<circle class="pu" cx="{PAD + 3}" cy="34.5" r="3" fill="{C["text"]}"/>')
    b.append(label(PAD + 14, 38, "GitHub stats · live", "soft"))
    b.append(label(W - PAD, 38, f"Updated {updated}", "sec", anchor="end"))
    b.append(hline(56, 1, W - 1))
    cw = W / 4
    for i, (name, value, sub) in enumerate(s["numbers"]):
        x = i * cw
        if i:
            b.append(vline(round(x), 57, 164))
        b.append(label(x + PAD, 82, f"{i + 1:02d}  {name}", "sec", weight=500))
        b.append(t(x + PAD - 2, 128, f"{value:,}", 38, "text", 300, ls=-.02))
        b.append(t(x + PAD, 148, sub, 11, "ter"))
    b.append(hline(164, 1, W - 1))
    b.append(label(PAD, 194, "Languages", "soft"))
    b.append(t(W - PAD, 194, "by code size, public repos", 11, "ter", anchor="end"))
    x, bw = float(PAD), W - 2 * PAD
    b.append(rect(PAD, 210, bw, 8, "track", rx=2))
    for i, (name, share) in enumerate(s["langs"]):
        w = bw * share
        b.append(f'<rect x="{x:.1f}" y="210" width="{max(w - 2, 1):.1f}" height="8" rx="1.5" fill="{ramp[min(i, 6)]}"/>')
        x += w
    lx = PAD
    for i, (name, share) in enumerate(s["langs"]):
        pct = f"{share * 100:.1f}%"
        b.append(rect(lx, 242, 8, 8, ramp[min(i, 6)], "strong" if i == 6 or name == "other" else None, 2))
        b.append(t(lx + 14, 250, name, 11.5, "soft" if i == 0 else "sec", 500 if i == 0 else 400))
        nx = lx + 14 + measure(name, 11.5, 500 if i == 0 else 400) + 6
        b.append(t(nx, 250, pct, 11.5, "ter", mono=False))
        lx = nx + measure(pct, 11.5) + 22
    title = ("GitHub stats for " + USER + ": " +
             ", ".join(f"{v:,} {l.lower()} ({sub})" for l, v, sub in s["numbers"]) +
             ". Top languages: " + ", ".join(f"{n} {p*100:.0f}%" for n, p in s["langs"]))
    return svg(W, H, title, "".join(b))


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Set GITHUB_TOKEN (locally: GITHUB_TOKEN=$(gh auth token) python3 tools/build_stats.py)")
    stats = summarise(fetch(token))
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for theme in THEMES:
        use_theme(theme)
        (OUT / theme).mkdir(parents=True, exist_ok=True)
        (OUT / theme / "stats.svg").write_text(render(stats, updated))
    print("wrote stats.svg:", stats)


if __name__ == "__main__":
    main()
