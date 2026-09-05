import os
import json
import urllib.request
from datetime import datetime, timedelta

USERNAME = "yogeshcodes27"
OUTPUT = "assets/contribution-graph.svg"

query = """
query($user:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$user) {
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

today = datetime.utcnow().date()
start = today - timedelta(days=364)

variables = {
    "user": USERNAME,
    "from": f"{start}T00:00:00Z",
    "to": f"{today}T23:59:59Z"
}

data = json.dumps({
    "query": query,
    "variables": variables
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={
        "Authorization": f"bearer {os.environ['GH_TOKEN']}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

days = []

for week in weeks:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if start <= date <= today:
            days.append((date, day["contributionCount"]))

days.sort()

width = 1400
height = 360
left = 70
right = 30
top = 55
bottom = 55

plot_width = width - left - right
plot_height = height - top - bottom

max_count = max((count for _, count in days), default=1)

points = []

for i, (_, count) in enumerate(days):
    x = left + (i / (len(days) - 1)) * plot_width
    y = top + plot_height - (count / max_count) * plot_height
    points.append((x, y))

line = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)

area = (
    f"{left},{top + plot_height} "
    + line
    + f" {left + plot_width},{top + plot_height}"
)

month_labels = []

last_month = None

for i, (date, _) in enumerate(days):
    if date.month != last_month:
        x = left + (i / (len(days) - 1)) * plot_width
        month_labels.append(
            f'<text x="{x:.2f}" y="{height - 20}" '
            f'fill="#8B949E" font-size="13">{date.strftime("%b")}</text>'
        )
        last_month = date.month

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}"
viewBox="0 0 {width} {height}">

<rect width="100%" height="100%" rx="12" fill="#0D1117"/>

<text x="{left}" y="28"
fill="#C9D1D9"
font-size="18"
font-family="Arial, sans-serif"
font-weight="600">
Yogesh S's Contribution Graph
</text>

<line x1="{left}" y1="{top + plot_height}"
x2="{left + plot_width}" y2="{top + plot_height}"
stroke="#30363D"/>

<line x1="{left}" y1="{top}"
x2="{left}" y2="{top + plot_height}"
stroke="#30363D"/>

<polygon points="{area}"
fill="#8B5CF6"
opacity="0.12"/>

<polyline points="{line}"
fill="none"
stroke="#8B5CF6"
stroke-width="2.5"
stroke-linejoin="round"
stroke-linecap="round"/>

{''.join(month_labels)}

<text x="18" y="{top + 5}"
fill="#8B949E"
font-size="11"
font-family="Arial, sans-serif">
{max_count}
</text>

<text x="35" y="{top + plot_height}"
fill="#8B949E"
font-size="11"
font-family="Arial, sans-serif">
0
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Generated {OUTPUT}")
print(f"Days: {len(days)}")
