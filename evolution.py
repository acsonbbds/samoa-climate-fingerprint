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

for name, (path, method, unit) in configs.items():
    df = load(path)
    values = []

    for start in starts:
        s = df[df["TIME_PERIOD"].between(start, start + 9)]["OBS_VALUE"]
        values.append(metric(s, method))

    lo = min(values)
    hi = max(values)

    scores = [
        100 * (v - lo) / (hi - lo)
        for v in values
    ]

    if unit == "m":
        hover_values = [f"{v:.3f} {unit}" for v in values]
    else:
        hover_values = [f"{v:.2f} {unit}" for v in values]

    scores_rows.append(scores)
    hover_rows.append(hover_values)

fig = go.Figure(
    data=go.Heatmap(
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
    title={
        "text": (
            "<b>Samoa's Climate Fingerprint Is Intensifying</b>"
            "<br><sup>Each column represents a rolling 10-year climate window</sup>"
        ),
        "x": 0.5
    },
    xaxis_title="10-year climate window",
    yaxis_title="",
    height=520,
    margin=dict(l=150, r=80, t=100, b=120)
)

fig.add_annotation(
    text=(
        "Ocean and surface temperature: 10-year mean anomaly (°C) · "
        "Rainfall: 10-year variability (standard deviation, mm) · "
        "Sea level: 10-year mean anomaly (m)"
    ),
    x=0.5,
    y=-0.28,
    xref="paper",
    yref="paper",
    showarrow=False
)

fig.write_html("samoa_evolution.html", include_plotlyjs=True)

print("ATUALIZADO: samoa_evolution.html")
