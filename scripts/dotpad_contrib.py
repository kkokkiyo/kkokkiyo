"""지난 1년 기여 기록을 Dot Pad 핀 모양 SVG로 그림 (라이트/다크 두 벌)"""
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "kkokkiyo")
URL = f"https://github.com/users/{USER}/contributions"
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
START, END = "<!-- DOTPAD-CONTRIB:START -->", "<!-- DOTPAD-CONTRIB:END -->"
SECTION = """## 활동

<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/dotpad-contrib-light.svg">
  <img src="assets/dotpad-contrib-dark.svg" alt="지난 1년 기여 기록을 Dot Pad 핀으로 그린 그림" width="100%">
</picture>
"""
THEMES = {
    "dark": {"panel": "#18181b", "frame": "#27272a", "down": "#3f3f46", "up": ["#71717a", "#a1a1aa", "#d4d4d8", "#fafafa"], "text": "#a1a1aa", "strong": "#fafafa"},
    "light": {"panel": "#f4f4f5", "frame": "#e4e4e7", "down": "#d4d4d8", "up": ["#a1a1aa", "#71717a", "#3f3f46", "#18181b"], "text": "#52525b", "strong": "#18181b"},
}
GAP, R_DOWN, R_UP = 14, 2.2, [3.4, 4.4, 5.2, 6.0]


def fetch():
    """방문자가 보는 공개 기여 그래프 페이지를 읽음 (프로필 공개 설정을 그대로 따름)"""
    html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "dotpad-contrib"})).read().decode()
    tips = dict(re.findall(r'for="contribution-day-component-(\d+-\d+)"[^>]*>([^<]*)', html))
    cells = re.findall(r'data-date="([\d-]+)" id="contribution-day-component-(\d+)-(\d+)" data-level="(\d)"', html)
    weeks = {}
    for date, weekday, week, level in cells:
        m = re.match(r"(\d+) contributions?", tips.get(f"{weekday}-{week}", ""))
        weeks.setdefault(int(week), {})[int(weekday)] = {"date": date, "count": int(m.group(1)) if m else 0, "level": int(level)}
    ordered = [weeks[w] for w in sorted(weeks)]
    return sum(d["count"] for w in ordered for d in w.values()), ordered


def update_readme(show):
    text = open(README, encoding="utf-8").read()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    body = "\n" + SECTION + "\n" if show else "\n"
    open(README, "w", encoding="utf-8").write(before + START + body + END + after)


def render(total, weeks, theme):
    c = THEMES[theme]
    pad_x, pad_top, pad_bottom = 28, 56, 26
    width = pad_x * 2 + GAP * len(weeks)
    height = pad_top + GAP * 7 + pad_bottom
    pins = []
    for x, week in enumerate(weeks):
        for weekday, day in week.items():
            level = day["level"]
            cx = pad_x + x * GAP + GAP / 2
            cy = pad_top + weekday * GAP + GAP / 2
            title = f'{day["date"]}: {day["count"]}번'
            if level == 0:
                pins.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R_DOWN}" fill="{c["down"]}"><title>{title}</title></circle>')
            else:
                pins.append(
                    f'<circle class="up" style="animation-delay:{x * 0.025:.2f}s" cx="{cx:.0f}" cy="{cy:.0f}" r="{R_UP[level - 1]}" fill="{c["up"][level - 1]}"><title>{title}</title></circle>'
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
    update_readme(total > 0)
    print(f"total={total}, weeks={len(weeks)}, section={'shown' if total > 0 else 'hidden'}")
