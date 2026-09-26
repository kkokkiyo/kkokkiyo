"""지난 1년 기여 기록을 Dot Pad 핀 모양 SVG로 그림 (라이트/다크 두 벌)"""
import json
import os
import urllib.request

USER = os.environ.get("GH_USER", "kkokkiyo")
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
THEMES = {
    "dark": {"panel": "#18181b", "frame": "#27272a", "down": "#3f3f46", "up": ["#71717a", "#a1a1aa", "#d4d4d8", "#fafafa"], "text": "#a1a1aa", "strong": "#fafafa"},
    "light": {"panel": "#f4f4f5", "frame": "#e4e4e7", "down": "#d4d4d8", "up": ["#a1a1aa", "#71717a", "#3f3f46", "#18181b"], "text": "#52525b", "strong": "#18181b"},
}
GAP, R_DOWN, R_UP = 14, 2.2, [3.4, 4.4, 5.2, 6.0]


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def render(total, weeks, theme):
    c = THEMES[theme]
    pad_x, pad_top, pad_bottom = 28, 56, 26
    width = pad_x * 2 + GAP * len(weeks)
    height = pad_top + GAP * 7 + pad_bottom
    pins = []
    for x, week in enumerate(weeks):
        days = week["contributionDays"]
        offset = 7 - len(days) if x == 0 else 0
        for i, day in enumerate(days):
            level = LEVEL[day["contributionLevel"]]
            cx = pad_x + x * GAP + GAP / 2
            cy = pad_top + (i + offset) * GAP + GAP / 2
            title = f'{day["date"]}: {day["contributionCount"]}번'
            if level == 0:
                pins.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R_DOWN}" fill="{c["down"]}"><title>{title}</title></circle>')
            else:
                delay = x * 0.025
                pins.append(
                    f'<circle class="up" style="animation-delay:{delay:.2f}s" cx="{cx:.0f}" cy="{cy:.0f}" r="{R_UP[level - 1]}" fill="{c["up"][level - 1]}"><title>{title}</title></circle>'
                )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="지난 1년 동안 {total}번 기여한 기록을 Dot Pad 핀으로 그린 그림">
<style>
  .up {{ transform-box: fill-box; transform-origin: center; animation: rise 0.6s ease-out both; }}
  @keyframes rise {{ from {{ transform: scale(0.35); opacity: 0.4; }} to {{ transform: scale(1); opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .up {{ animation: none; }} }}
  text {{ font-family: -apple-system, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif; }}
</style>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="16" fill="{c["panel"]}" stroke="{c["frame"]}" stroke-width="2"/>
<text x="{pad_x}" y="34" font-size="15" fill="{c["text"]}">지난 1년 동안 <tspan fill="{c["strong"]}" font-weight="700">{total}번</tspan> 기여했어요. 기여가 많은 날일수록 핀이 높이 올라와요.</text>
{chr(10).join(pins)}
</svg>
"""


if __name__ == "__main__":
    total, weeks = fetch()
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    for theme in THEMES:
        with open(os.path.join(out, f"dotpad-contrib-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(render(total, weeks, theme))
    print(f"total={total}, weeks={len(weeks)}")
