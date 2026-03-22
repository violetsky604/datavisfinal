import pandas as pd
import json

# --- Load & Process Data ---
df = pd.read_csv("CAvideos comments removed.csv")

df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
df["trending_date"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")

dedup = df.sort_values("views", ascending=False).drop_duplicates("video_id").copy()
dedup["days_to_trend"] = (dedup["trending_date"] - dedup["publish_time"].dt.tz_localize(None)).dt.days
dedup = dedup[(dedup["days_to_trend"] >= 0) & (dedup["days_to_trend"] <= 30)]

stats = dedup.groupby("days_to_trend").agg(
    median_views=("views", "median"),
    count=("video_id", "count")
).reset_index()

records = stats.to_dict(orient="records")
with open("story3_data.json", "w") as f:
    json.dump(records, f, indent=2)

print("story3_data.json written.")

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>The Sweet Spot: When Videos Hit Their Peak</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body { font-family: Inter, sans-serif; background: white; margin: 0; padding: 20px; }
  </style>
</head>
<body>
<div id="chart"></div>
<script>
fetch("story3_data.json")
  .then(r => r.json())
  .then(data => {
    const x = data.map(d => d.days_to_trend);
    const y = data.map(d => d.median_views);
    const counts = data.map(d => d.count);

    const trace = {
      type: "scatter",
      mode: "lines",
      fill: "tozeroy",
      x: x,
      y: y,
      customdata: counts,
      line: { color: "#7C3AED", width: 3, shape: "linear" },
      fillcolor: "rgba(167, 139, 250, 0.3)",
      hovertemplate: "<b>Day %{x}</b><br>Median views: %{y:,}<br>Videos: %{customdata}<extra></extra>",
    };

    const layout = {
      title: {
        text: "<b>Patience Pays Off — But Only to a Point</b><br><sup>Median views by how many days after publishing a video hit trending in Canada (2017–2018)</sup>",
        font: { family: "Inter, sans-serif", size: 20, color: "#1e1b4b" },
        x: 0.05,
      },
      xaxis: {
        title: "Days Between Publishing and Trending",
        dtick: 1,
        gridcolor: "#f3f4f6",
        tickfont: { size: 11 },
      },
      yaxis: {
        title: "Median Views",
        tickformat: ".2s",
        gridcolor: "#f3f4f6",
        tickfont: { size: 11 },
      },
      annotations: [
        {
          x: 4,
          y: data.find(d => d.days_to_trend === 4)?.median_views || 0,
          text: "n=571 videos",
          showarrow: true, arrowhead: 2, arrowcolor: "#4C1D95",
          font: { size: 11, color: "#4C1D95", family: "Inter, sans-serif" },
          ax: -50, ay: -40,
        },
        {
          x: 5,
          y: data.find(d => d.days_to_trend === 5)?.median_views || 0,
          text: "n=148 videos",
          showarrow: true, arrowhead: 2, arrowcolor: "#4C1D95",
          font: { size: 11, color: "#4C1D95", family: "Inter, sans-serif" },
          ax: 50, ay: -40,
        },
        {
          x: 18,
          y: data.find(d => d.days_to_trend === 18)?.median_views || 0,
          text: "n=2 videos<br>Top: 17 Awesome Crafting Life Hacks<br>(MR.ROMEO, 7.3M views)",
          showarrow: true, arrowhead: 2, arrowcolor: "#7C3AED",
          font: { size: 10, color: "#7C3AED", family: "Inter, sans-serif" },
          ax: 80, ay: -60,
          align: "left",
        },
        {
          x: 22,
          y: data.find(d => d.days_to_trend === 22)?.median_views || 0,
          text: "n=1 video<br>3 Simple Tricks<br>(HawkGuruHacker, 11.7M views)",
          showarrow: true, arrowhead: 2, arrowcolor: "#7C3AED",
          font: { size: 10, color: "#7C3AED", family: "Inter, sans-serif" },
          ax: 60, ay: -60,
          align: "left",
        },
        {
          x: 27,
          y: data.find(d => d.days_to_trend === 27)?.median_views || 0,
          text: "n=1 video<br>Gunna - Sold Out Dates ft. Lil Baby<br>(Gunna, 5M views)",
          showarrow: true, arrowhead: 2, arrowcolor: "#7C3AED",
          font: { size: 10, color: "#7C3AED", family: "Inter, sans-serif" },
          ax: -80, ay: -60,
          align: "left",
        },
      ],
      plot_bgcolor: "white",
      paper_bgcolor: "white",
      height: 560,
      margin: { l: 80, r: 60, t: 110, b: 60 },
      font: { family: "Inter, sans-serif", color: "#374151" },
      hoverlabel: { bgcolor: "white", font: { size: 13 } },
    };

    Plotly.newPlot("chart", [trace], layout, { responsive: true });
  });
</script>
</body>
</html>
"""

with open("story3.html", "w", encoding="utf-8") as f:
    f.write(html)

print("story3.html written.")
