"""Fetch live GitHub stats and render assets/stats.svg in the README card style.

Run locally:  GITHUB_TOKEN=$(gh auth token) python3 tools/build_stats.py
In CI the workflow passes GITHUB_TOKEN (or the optional STATS_TOKEN secret).
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

from build_assets import (ACCENT, BAR, LINE, MUTED, OFF, OUT, hline, svg, t, vline)

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
            ("CONTRIBUTIONS", cc["contributionCalendar"]["totalContributions"], "past year"),
            ("COMMITS", cc["totalCommitContributions"], "past year"),
            ("PULL REQUESTS", u["pullRequests"]["totalCount"], "all time"),
            ("STARS", sum(n["stargazerCount"] for n in repos["nodes"]), f"across {repos['totalCount']} repos"),
        ],
        "langs": top,
    }


SHADES = [ACCENT, "#3D7FCC", "#2E6299", "#244C75", "#1C3A59", "#162E45", "#2A3640"]


def render(s, updated):
    W, H = 880, 222
    b = [f'<rect width="{W}" height="28" fill="{BAR}"/>', hline(27, 0, W)]
    b.append(f'<circle class="pu" cx="17" cy="14" r="3.5" fill="{ACCENT}"/>')
    b.append(t(28, 19, "github.stats", 12, "p w"))
    b.append(t(W - 12, 19, f"live · updated {updated}", 12, "m", "end"))
    cw = W / 4
    for i, (label, value, sub) in enumerate(s["numbers"]):
        x = int(i * cw)
        if i:
            b.append(vline(x, 28, 116))
        b.append(t(x + 16, 52, label, 10, "m"))
        b.append(t(x + 16, 90, f"{value:,}", 30, "a s" if i == 0 else "p s",
                   extra=' style="font-weight:300;letter-spacing:-1px"'))
        b.append(t(x + 16, 106, sub, 10, "m"))
    b.append(hline(116, 0, W))
    b.append(t(16, 142, "LANGUAGES", 10, "m"))
    b.append(t(W - 16, 142, "by code size, public repos", 10, "m", "end"))
    x, bw = 16.0, W - 32
    b.append(f'<rect x="16" y="152" width="{bw}" height="10" fill="{OFF}"/>')
    for i, (name, share) in enumerate(s["langs"]):
        w = bw * share
        b.append(f'<rect x="{x:.1f}" y="152" width="{max(w - 2, 1):.1f}" height="10" fill="{SHADES[min(i, 6)]}"/>')
        x += w
    lx = 16
    for i, (name, share) in enumerate(s["langs"]):
        label = f"{name} {share*100:.1f}%"
        b.append(f'<rect x="{lx}" y="184" width="8" height="8" fill="{SHADES[min(i, 6)]}"/>')
        b.append(t(lx + 14, 192, label, 11, "p" if i == 0 else ""))
        lx += 14 + int(len(label) * 7.2) + 20
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
    OUT.mkdir(exist_ok=True)
    (OUT / "stats.svg").write_text(render(stats, updated))
    print("wrote stats.svg:", stats)


if __name__ == "__main__":
    main()
