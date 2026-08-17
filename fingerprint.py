import pandas as pd
import plotly.graph_objects as go

configs = {
    "Ocean heat": ("data/sst.csv", "mean"),
    "Surface heat": ("data/surface_temp.csv", "mean"),
    "Rainfall volatility": ("data/rainfall.csv", "std"),
    "Sea level": ("data/sea_level.csv", "mean"),
}

def load_samoa(path):
    df = pd.read_csv(path)
    df = df[df["GEO_PICT"] == "WS"].copy()

    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

    return df[df["TIME_PERIOD"].between(1993, 2023)]

def metric(series, method):
    if method == "std":
        return series.std()
    return series.mean()

old_raw = {}
new_raw = {}
old_score = {}
new_score = {}

for name, (path, method) in configs.items():
    df = load_samoa(path)

    # Todas as janelas possíveis de 10 anos
    window_values = []

    for start in range(1993, 2015):
        end = start + 9
        s = df[df["TIME_PERIOD"].between(start, end)]["OBS_VALUE"]

        if len(s) == 10:
            window_values.append(metric(s, method))

    lo = min(window_values)
    hi = max(window_values)

    old = metric(
        df[df["TIME_PERIOD"].between(1993, 2002)]["OBS_VALUE"],
        method
    )

    new = metric(
        df[df["TIME_PERIOD"].between(2014, 2023)]["OBS_VALUE"],
        method
    )

    old_raw[name] = old
    new_raw[name] = new

    old_score[name] = 100 * (old - lo) / (hi - lo)
    new_score[name] = 100 * (new - lo) / (hi - lo)

categories = list(configs.keys())

old_values = [old_score[x] for x in categories]
new_values = [new_score[x] for x in categories]

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=old_values + [old_values[0]],
    theta=categories + [categories[0]],
    fill="toself",
    name="1993–2002"
))

fig.add_trace(go.Scatterpolar(
    r=new_values + [new_values[0]],
    theta=categories + [categories[0]],
    fill="toself",
    name="2014–2023"
))

fig.update_layout(
    title={
        "text": (
            "<b>Samoa: A Climate Fingerprint in Motion</b>"
            "<br><sup>How Samoa's climate profile shifted across three decades</sup>"
        ),
        "x": 0.5,
    },
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            ticksuffix="%"
        )
    ),
    height=750
)

fig.add_annotation(
    text="Scores show each 10-year period's position within Samoa's observed 1993–2023 range.",
    x=0.5,
    y=-0.08,
    xref="paper",
    yref="paper",
    showarrow=False
)

fig.write_html("samoa_fingerprint.html", include_plotlyjs=True)

print("CRIADO: samoa_fingerprint.html")
print()

for name in categories:
    print(
        name,
        "|",
        f"1993-2002: {old_score[name]:.1f}",
        "|",
        f"2014-2023: {new_score[name]:.1f}"
    )
