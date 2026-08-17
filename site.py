import pandas as pd
import plotly.graph_objects as go

configs = {
    "Ocean heat": ("data/sst.csv", "mean", "°C"),
    "Surface heat": ("data/surface_temp.csv", "mean", "°C"),
    "Rainfall volatility": ("data/rainfall.csv", "std", "mm"),
    "Sea level": ("data/sea_level.csv", "mean", "m"),
}

def load(path):
    df = pd.read_csv(path)
    df = df[df["GEO_PICT"] == "WS"].copy()
    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df[df["TIME_PERIOD"].between(1993, 2023)]

def metric(series, method):
    return series.std() if method == "std" else series.mean()

starts = list(range(1993, 2015))
labels = [f"{s}–{s+9}" for s in starts]

scores_rows = []
hover_rows = []
stats = {}

for name, (path, method, unit) in configs.items():
    df = load(path)

    values = []
    for start in starts:
        s = df[df["TIME_PERIOD"].between(start, start + 9)]["OBS_VALUE"]
        values.append(metric(s, method))

    lo = min(values)
    hi = max(values)

    scores = [100 * (v - lo) / (hi - lo) for v in values]

    if unit == "m":
        hover = [f"{v:.3f} {unit}" for v in values]
    else:
        hover = [f"{v:.2f} {unit}" for v in values]

    scores_rows.append(scores)
    hover_rows.append(hover)

    old = values[0]
    new = values[-1]
    stats[name] = (old, new)

fig = go.Figure(
    go.Heatmap(
        z=scores_rows,
        x=labels,
        y=list(configs.keys()),
        customdata=hover_rows,
        zmin=0,
        zmax=100,
        colorscale="YlOrRd",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x}<br>"
            "Observed value: <b>%{customdata}</b><br>"
            "Relative intensity: %{z:.0f}/100"
            "<extra></extra>"
        ),
        colorbar=dict(title="Relative<br>intensity")
    )
)

fig.update_layout(
    template="plotly_white",
    height=520,
    margin=dict(l=130, r=60, t=30, b=110),
    xaxis_title="Rolling 10-year climate window",
    yaxis_title="",
    font=dict(family="Arial, sans-serif")
)

chart = fig.to_html(
    full_html=False,
    include_plotlyjs=True,
    config={"displayModeBar": False, "responsive": True}
)

ocean_change = stats["Ocean heat"][1] - stats["Ocean heat"][0]
surface_change = stats["Surface heat"][1] - stats["Surface heat"][0]
sea_change_cm = (stats["Sea level"][1] - stats["Sea level"][0]) * 100
rain_change = (
    (stats["Rainfall volatility"][1] / stats["Rainfall volatility"][0] - 1) * 100
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Samoa: A Climate Fingerprint in Motion</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #07111f;
    color: #f4f7fb;
}}

.page {{
    max-width: 1250px;
    margin: auto;
    padding: 70px 28px;
}}

.eyebrow {{
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 12px;
    color: #8da5bf;
    margin-bottom: 18px;
}}

h1 {{
    font-size: clamp(42px, 7vw, 82px);
    line-height: 0.98;
    max-width: 950px;
    margin: 0;
}}

.lead {{
    font-size: 21px;
    line-height: 1.55;
    color: #b9c8d8;
    max-width: 780px;
    margin: 28px 0 45px;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 55px;
}}

.card {{
    background: #101d2d;
    border: 1px solid #203247;
    border-radius: 14px;
    padding: 22px;
}}

.value {{
    font-size: 34px;
    font-weight: bold;
    margin-bottom: 7px;
}}

.label {{
    color: #9fb0c2;
    font-size: 14px;
    line-height: 1.35;
}}

.section {{
    background: #ffffff;
    color: #172235;
    border-radius: 18px;
    padding: 28px;
}}

.section h2 {{
    font-size: 30px;
    margin: 0 0 8px;
}}

.section p {{
    color: #5b6675;
    margin-top: 0;
}}

.note {{
    color: #8795a5;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 20px;
}}

footer {{
    margin-top: 38px;
    color: #77899d;
    font-size: 13px;
    line-height: 1.6;
}}

@media (max-width: 800px) {{
    .cards {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 500px) {{
    .cards {{
        grid-template-columns: 1fr;
    }}
}}
</style>
</head>

<body>
<div class="page">

<div class="eyebrow">Pacific Dataviz Challenge 2026 · Climate Change</div>

<h1>Samoa's climate fingerprint is changing.</h1>

<p class="lead">
From 1993 to 2023, four climate signals tell the same broad story:
warmer ocean water, warmer surface temperatures, a higher sea level,
and increasingly volatile rainfall.
</p>

<div class="cards">

<div class="card">
<div class="value">+{ocean_change:.2f}°C</div>
<div class="label">change in 10-year mean ocean temperature anomaly</div>
</div>

<div class="card">
<div class="value">+{surface_change:.2f}°C</div>
<div class="label">change in 10-year mean surface temperature anomaly</div>
</div>

<div class="card">
<div class="value">+{sea_change_cm:.1f} cm</div>
<div class="label">change in 10-year mean sea-level anomaly</div>
</div>

<div class="card">
<div class="value">+{rain_change:.0f}%</div>
<div class="label">change in 10-year rainfall variability</div>
</div>

</div>

<div class="section">

<h2>A fingerprint in motion</h2>

<p>
Each column below is a rolling 10-year window. Darker cells indicate
where that climate signal sits closer to the highest 10-year value
observed in Samoa during 1993–2023.
</p>

{chart}

<div class="note">
Temperature and sea level use 10-year mean anomalies.
Rainfall volatility is measured using the standard deviation of annual
precipitation anomalies within each 10-year window.
Hover over any cell to see the observed value.
</div>

</div>

<footer>
Data: Pacific Data Hub · Pacific Community (SPC).<br>
Indicators: Sea Surface Temperature anomalies, Surface Temperature
anomalies, Precipitation anomalies and Sea Level Anomalies.
</footer>

</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("CRIADO: index.html")
