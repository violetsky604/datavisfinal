import pandas as pd
import json

# --- Load & Process Data ---
df = pd.read_csv("CAvideos comments removed.csv")

# Parse trending_date (format: YY.DD.MM)
df["trending_date"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")
df["week"] = df["trending_date"].dt.to_period("W").apply(lambda r: str(r.start_time.date()))

# Aggregate views per channel per week
weekly = df.groupby(["week", "channel_title"])["views"].sum().reset_index()

# Find top 10 channels by total views across all weeks
top_channels = (
    weekly.groupby("channel_title")["views"].sum()
    .nlargest(10)
    .index.tolist()
)

weekly_top = weekly[weekly["channel_title"].isin(top_channels)].copy()

# Rank channels within each week by views
weekly_top["rank"] = weekly_top.groupby("week")["views"].rank(ascending=False, method="first").astype(int)

# Get all weeks
weeks_all = sorted(weekly_top["week"].unique().tolist())

# Build series
series = []
for ch in top_channels:
    cdata = weekly_top[weekly_top["channel_title"] == ch].sort_values("week")
    week_rank = {row["week"]: row["rank"] for _, row in cdata.iterrows()}
    week_views = {row["week"]: int(row["views"]) for _, row in cdata.iterrows()}
    ranks = [week_rank.get(w) for w in weeks_all]
    views = [week_views.get(w, 0) for w in weeks_all]
    series.append({
        "channel": ch,
        "weeks": weeks_all,
        "ranks": ranks,
        "views": views,
    })

output = {"weeks": weeks_all, "series": series}
with open("story3_data.json", "w") as f:
    json.dump(output, f, indent=2)

print("story3_data.json written.")

# --- Write HTML ---
html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Who Ruled Canadian YouTube in 2017?</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body { font-family: Inter, sans-serif; background: white; margin: 0; padding: 20px; }
    #controls { margin-bottom: 12px; display: flex; gap: 8px; align-items: center; }
    button {
      padding: 6px 14px; font-size: 12px; font-family: Inter, sans-serif;
      border-radius: 4px; cursor: pointer;
      background: #F5F3FF; border: 1px solid #7C3AED; color: #374151;
    }
    button.active { background: #7C3AED; color: white; }
  </style>
</head>
<body>

<div id="controls">
  <span style="font-size:12px;color:#374151;line-height:2">Labels:</span>
  <button class="active" onclick="toggleLabels(this)">On</button>
</div>

<div id="chart"></div>

<script>
let showLabels = true;

fetch("story3_data.json")
  .then(r => r.json())
  .then(data => { window._chartData = data; renderChart(); });

function renderChart() {
  const data = window._chartData;
  const colors = [
    "#5B21B6","#7C3AED","#A78BFA","#2563EB",
    "#60A5FA","#059669","#34D399","#D97706",
    "#F59E0B","#EF4444"
  ];

  const traces = data.series.map((s, i) => ({
    type: "scatter",
    mode: showLabels ? "lines+markers+text" : "lines+markers",
    name: s.channel,
    x: s.weeks,
    y: s.ranks,
    text: showLabels ? s.ranks.map(r => r != null ? String(r) : "") : [],
    textposition: "top center",
    textfont: { size: 9 },
    connectgaps: false,
    customdata: s.views.map(v => v.toLocaleString()),
    hovertemplate: "<b>" + s.channel + "</b><br>Week: %{x}<br>Rank: %{y}<br>Views: %{customdata}<extra></extra>",
    line: { width: 2.5, color: colors[i % colors.length] },
    marker: { size: 7, color: colors[i % colors.length] },
  }));

  const layout = {
    title: {
      text: "<b>Who Ruled Canadian YouTube in 2017?</b><br><sup>Top 10 channels ranked weekly by total views — rank 1 = most viewed</sup>",
      font: { family: "Inter, sans-serif", size: 20, color: "#1e1b4b" },
      x: 0.05,
    },
    xaxis: {
      title: "Week",
      tickangle: -45,
      tickfont: { size: 10 },
      gridcolor: "#f3f4f6",
    },
    yaxis: {
      title: "Rank",
      autorange: "reversed",
      dtick: 1,
      tickfont: { size: 11 },
      gridcolor: "#f3f4f6",
    },
    legend: { font: { size: 10 }, x: 1.01, y: 1 },
    plot_bgcolor: "white",
    paper_bgcolor: "white",
    height: 600,
    margin: { l: 60, r: 260, t: 100, b: 80 },
    font: { family: "Inter, sans-serif", color: "#374151" },
    hoverlabel: { bgcolor: "white", font: { size: 13 } },
  };

  Plotly.react("chart", traces, layout, { responsive: true });
}

function toggleLabels(btn) {
  showLabels = !showLabels;
  btn.classList.toggle("active");
  btn.textContent = showLabels ? "On" : "Off";
  renderChart();
}
</script>
</body>
</html>
"""

with open("story3.html", "w", encoding="utf-8") as f:
    f.write(html)

print("story3.html written.")

