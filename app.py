import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

datasets = [
    ("Ocean Temperature Anomaly", "data/sst.csv", "°C"),
    ("Surface Temperature Anomaly", "data/surface_temp.csv", "°C"),
    ("Rainfall Anomaly", "data/rainfall.csv", "mm"),
    ("Sea Level Anomaly", "data/sea_level.csv", "m"),
]

fig = make_subplots(
    rows=4,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.07,
    subplot_titles=[x[0] for x in datasets],
)

for row, (title, path, unit) in enumerate(datasets, start=1):
    df = pd.read_csv(path)
    df = df[df["GEO_PICT"] == "WS"].copy()

    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    # Período comum aos quatro indicadores
    df = df[df["TIME_PERIOD"].between(1993, 2023)]

    fig.add_trace(
        go.Scatter(
            x=df["TIME_PERIOD"],
            y=df["OBS_VALUE"],
            mode="lines+markers",
            name=title,
            hovertemplate=f"%{{x}}<br>%{{y:.2f}} {unit}<extra></extra>",
        ),
        row=row,
        col=1,
    )

    fig.update_yaxes(title_text=unit, row=row, col=1)

fig.update_layout(
    title={
        "text": (
            "<b>Samoa: A Climate Fingerprint in Motion</b>"
            "<br><sup>Four climate signals changing together, 1993–2023</sup>"
        ),
        "x": 0.5,
    },
    height=950,
    showlegend=False,
    hovermode="x unified",
)

fig.update_xaxes(title_text="Year", row=4, col=1)

fig.write_html(
    "samoa_climate_fingerprint.html",
    include_plotlyjs=True
)

print("CRIADO: samoa_climate_fingerprint.html")
