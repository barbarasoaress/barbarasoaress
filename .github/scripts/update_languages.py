import json
import os
import urllib.request
from html import escape

USER = "barbarasoaress"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT = "assets/languages.svg"

COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Python": "#3572A5",
    "Java": "#b07219",
    "C#": "#178600",
    "C++": "#f34b7d",
    "C": "#555555",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Shell": "#89e051",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Go": "#00ADD8",
    "Rust": "#dea584",
}


def github_get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "barbarasoaress-profile-stats",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def main():
    repos = github_get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    totals = {}

    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        languages = github_get(repo["languages_url"])
        for language, amount in languages.items():
            totals[language] = totals.get(language, 0) + amount

    grand_total = sum(totals.values())
    if not grand_total:
        return

    ordered = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    top = ordered[:7]
    if len(ordered) > 7:
        top.append(("Outras", sum(value for _, value in ordered[7:])))

    width = 680
    left = 28
    usable = width - 56
    bar_y = 55
    bar_h = 18
    line_h = 27
    height = 105 + len(top) * line_h

    segments = []
    x = left
    for index, (language, amount) in enumerate(top):
        pct = amount / grand_total
        seg_w = usable * pct
        if index == len(top) - 1:
            seg_w = left + usable - x
        color = COLORS.get(language, "#8b949e")
        segments.append(
            f'<rect x="{x:.2f}" y="{bar_y}" width="{max(seg_w, 1):.2f}" height="{bar_h}" fill="{color}" />'
        )
        x += seg_w

    rows = []
    y = 102
    for language, amount in top:
        pct = amount / grand_total * 100
        color = COLORS.get(language, "#8b949e")
        rows.append(
            f'<circle cx="{left + 5}" cy="{y - 4}" r="5" fill="{color}" />'
            f'<text x="{left + 18}" y="{y}" class="lang">{escape(language)}</text>'
            f'<text x="{width - left}" y="{y}" text-anchor="end" class="pct">{pct:.1f}%</text>'
        )
        y += line_h

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .title {{ font: 600 18px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; fill: #24292f; }}
  .lang, .pct {{ font: 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; fill: #57606a; }}
  @media (prefers-color-scheme: dark) {{
    .title {{ fill: #f0f6fc; }}
    .lang, .pct {{ fill: #8b949e; }}
  }}
</style>
<text x="{left}" y="30" class="title">Linguagens mais usadas</text>
<clipPath id="bar"><rect x="{left}" y="{bar_y}" width="{usable}" height="{bar_h}" rx="9" /></clipPath>
<g clip-path="url(#bar)">{''.join(segments)}</g>
{''.join(rows)}
</svg>'''

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as file:
        file.write(svg)


if __name__ == "__main__":
    main()
