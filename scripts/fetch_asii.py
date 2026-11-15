import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

SYMBOL = "ASII.JK"
URL = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range=6mo&interval=1d"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
except urllib.error.HTTPError as e:
    raise SystemExit(f"HTTP error: {e.code} {e.reason}")
except urllib.error.URLError as e:
    raise SystemExit(f"Network error: {e.reason}")

if data.get("chart", {}).get("error"):
    raise SystemExit(f"Yahoo API error: {data['chart']['error']}")

result = data["chart"]["result"][0]
timestamps = result["timestamp"]
closes = result["indicators"]["quote"][0]["close"]

points = []
for ts, c in zip(timestamps, closes):
    if c is not None and ts is not None:
        dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        points.append({"date": dt_str, "close": round(c)})

if not points:
    raise SystemExit("No closing data returned. Check the symbol or range.")

os.makedirs("data", exist_ok=True)
with open("data/asii.json", "w") as f:
    json.dump({"symbol": SYMBOL, "points": points}, f, indent=2)

print(f"Saved {len(points)} closing prices to data/asii.json")
