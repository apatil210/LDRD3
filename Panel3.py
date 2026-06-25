import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

st.set_page_config(
    page_title="US Manufacturing Energy 2022 Classification: Unit Operations",
    layout="wide",
)

pio.templates.default = "plotly"

SHEET_NAME = "Process-level data"
LOCAL_FILE = "DatasetJune24Part2.xlsx"

EXPECTED = {
    "naics_l2": "NAICS Level 2",
    "naics_l1": "NAICS Level 1",
    "industrial_process": "Industrial process",
    "percent_energy": "Percent Annual energy demand in 2022",
}

NAICS_COLORS = [
    "#0F4C5C",
    "#7A1F1F",
    "#5C4D7D",
    "#8A5A00",
    "#006D5B",
    "#8C2F39",
    "#355C7D",
    "#6B3E26",
    "#1D3557",
    "#7F5539",
    "#6A040F",
    "#3A5A40",
]

PROCESS_COLORS = [
    "#7A1F5C",
    "#A23B72",
    "#5B2A86",
    "#8C1C13",
    "#6C584C",
    "#2D6A4F",
    "#8D5524",
    "#3D405B",
    "#7B2CBF",
    "#9C6644",
    "#6F1D1B",
    "#386641",
]

ENERGY_SOURCE_COLORS = {
    "Annual Fuels": "#C05A00",
    "Annual Steam": "#355C9A",
    "Annual Electricity": "#1F8A4C",
}

TEMP_COLORS = {
    "<100 °C": "#2A9D8F",
    "100-200 °C": "#B9770E",
    "200-400 °C": "#C0392B",
    ">400 °C": "#5B2C6F",
}


def norm(x):
    return " ".join(str(x).replace("\n", " ").strip().split()).lower()


@st.cache_data
def load_data():
    df = pd.read_excel(LOCAL_FILE, sheet_name=SHEET_NAME, header=1, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > 0:
        first_row = " ".join([str(x) for x in df.iloc[0].fillna("").tolist()])
        if "GJ/FU" in first_row or "PJ" in first_row or "bara" in first_row:
            df = df.iloc[1:].copy()

    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    return df


def resolve_columns(df):
    resolved = {}
    missing = []

    for key, expected_name in EXPECTED.items():
        matches = [c for c in df.columns if norm(c) == norm(expected_name)]
        if matches:
            resolved[key] = matches[0]
        else:
            missing.append(expected_name)

    return resolved, missing


def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def fmt_pj(x):
    return f"{x:,.2f}"


def fmt_pct(x):
    return f"{x:.1f}%"


df = load_data()
cols, missing = resolve_columns(df)

st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #ffffff;
        color: #2f3042;
    }

    [data-testid="stAppViewContainer"],
    .main,
    .block-container {
        background: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: #ffffff !important;
    }

    .block-container {
        max-width: 1800px;
        padding-top: 3.25rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    h1, h2, h3 {
        color: #2f3042 !important;
        letter-spacing: -0.03em;
    }

    .page-title {
        font-size: 2.45rem;
        line-height: 1.16;
        font-weight: 800;
        color: #2f3042;
        margin: 0.35rem 0 1.75rem 0;
        padding-top: 0.2rem;
        overflow: visible;
        word-break: break-word;
    }

    .section-title {
        font-size: 1.25rem;
        line-height: 1.25;
        font-weight: 700;
        color: #2f3042;
        margin-bottom: 0.4rem;
    }

    .section-subtitle {
        font-size: 0.95rem;
        color: #818191;
        margin-bottom: 1rem;
        line-height: 1.4;
    }

    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 0.35rem 0 1.8rem 0;
        flex-wrap: wrap;
    }

    .metric-card {
        flex: 1 1 220px;
        background: #ffffff;
        border: 1px solid #e3e1ea;
        border-radius: 14px;
        padding: 0.95rem 1rem;
        min-width: 0;
    }

    .metric-label {
        font-size: 0.86rem;
        color: #707184;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.05rem;
        font-weight: 800;
        color: #2f3042;
    }

    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid #dcdde3 !important;
        border-radius: 10px !important;
        min-height: 44px;
        box-shadow: none !important;
    }

    div[data-baseweb="select"] input {
        color: #2f3042 !important;
    }

    .stSelectbox label {
        color: #4b4c5f !important;
        font-weight: 500 !important;
    }

    div[data-testid="stPlotlyChart"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .coverage-note {
        font-size: 0.95rem;
        color: #6f7082;
        margin-top: -0.25rem;
        margin-bottom: 1rem;
        line-height: 1.4;
    }

    @media (max-width: 1100px) {
        .page-title {
            font-size: 2.1rem;
            line-height: 1.18;
            margin-bottom: 1.35rem;
        }

        .block-container {
            padding-top: 2.5rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
    }

    @media (max-width: 640px) {
        .page-title {
            font-size: 1.8rem;
            line-height: 1.2;
            margin-bottom: 1.1rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .metric-row {
            gap: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">US Manufacturing Energy 2022 Classification: Unit Operations</div>',
    unsafe_allow_html=True,
)

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

required_min_columns = 51

if len(df.columns) < required_min_columns:
    st.error(
        "The loaded sheet does not contain enough columns after cleaning. "
        "This app requires at least Excel columns K, AU, AW, AX, and AY."
    )
    st.write("Detected columns:", len(df.columns))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_l1_col = cols["naics_l1"]
naics_l2_col = cols["naics_l2"]
industrial_process_col = cols["industrial_process"]
percent_energy_col = cols["percent_energy"]

temperature_col = df.columns[10]
total_energy_col = df.columns[46]
electricity_col = df.columns[48]
fuels_col = df.columns[49]
steam_col = df.columns[50]

naics_options = sorted(df[naics_l1_col].dropna().astype(str).drop_duplicates().tolist())
selected_naics = st.selectbox(
    "Select a NAICS Level 1 sector to generate a fact sheet",
    naics_options,
    index=0,
)

df_filtered = df[df[naics_l1_col].astype(str) == str(selected_naics)].copy()

coverage = num(df_filtered[percent_energy_col]).sum()
coverage_text = f"{coverage:.2%}" if coverage > 0 else "N/A"

total_energy = num(df_filtered[total_energy_col]).sum()
total_electricity = num(df_filtered[electricity_col]).sum()
total_fuels = num(df_filtered[fuels_col]).sum()
total_steam = num(df_filtered[steam_col]).sum()

breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

naics_donut_df = df_filtered[[naics_l2_col, total_energy_col]].copy()
naics_donut_df[total_energy_col] = pd.to_numeric(naics_donut_df[total_energy_col], errors="coerce")
naics_donut_df = (
    naics_donut_df.dropna(subset=[naics_l2_col, total_energy_col])
    .groupby(naics_l2_col, as_index=False)[total_energy_col]
    .sum()
    .rename(columns={naics_l2_col: "NAICS Level 2", total_energy_col: "Annual Energy"})
)
naics_donut_df = naics_donut_df[naics_donut_df["Annual Energy"] > 0].copy()
naics_donut_df = naics_donut_df.sort_values("Annual Energy", ascending=False)

naics_total = naics_donut_df["Annual Energy"].sum()
if naics_total > 0:
    naics_donut_df["Percent"] = (naics_donut_df["Annual Energy"] / naics_total) * 100
else:
    naics_donut_df["Percent"] = 0.0

process_df = df_filtered[[industrial_process_col, total_energy_col]].copy()
process_df[total_energy_col] = pd.to_numeric(process_df[total_energy_col], errors="coerce")
process_df = (
    process_df.dropna(subset=[industrial_process_col, total_energy_col])
    .groupby(industrial_process_col, as_index=False)[total_energy_col]
    .sum()
    .rename(columns={industrial_process_col: "Industrial process", total_energy_col: "Annual Energy"})
)
process_df = process_df[process_df["Annual Energy"] > 0].copy()
process_df = process_df.sort_values("Annual Energy", ascending=False)

temp_df = df_filtered[[temperature_col, total_energy_col]].copy()
temp_df.columns = ["Temperature", "Annual Energy"]
temp_df["Temperature"] = pd.to_numeric(temp_df["Temperature"], errors="coerce")
temp_df["Annual Energy"] = pd.to_numeric(temp_df["Annual Energy"], errors="coerce")
temp_df = temp_df.dropna(subset=["Temperature"])
temp_df = temp_df[temp_df["Annual Energy"] > 0].copy()

temp_df["Temperature Range"] = pd.cut(
    temp_df["Temperature"],
    bins=[-float("inf"), 100, 200, 400, float("inf")],
    labels=["<100 °C", "100-200 °C", "200-400 °C", ">400 °C"],
    right=False,
)

temp_donut_df = (
    temp_df.dropna(subset=["Temperature Range"])
    .groupby("Temperature Range", as_index=False)["Annual Energy"]
    .sum()
)
temp_donut_df = temp_donut_df[temp_donut_df["Annual Energy"] > 0].copy()

st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Total annual energy</div>
            <div class="metric-value">{fmt_pj(total_energy)} PJ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Annual electricity</div>
            <div class="metric-value">{fmt_pj(total_electricity)} PJ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Annual fuels</div>
            <div class="metric-value">{fmt_pj(total_fuels)} PJ</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Annual steam</div>
            <div class="metric-value">{fmt_pj(total_steam)} PJ</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.2, 1.0], gap="large")

with left_col:
    st.markdown(
        '<div class="section-title">Total Annual Energy Breakdown: NAICS Level 2</div>',
        unsafe_allow_html=True,
    )

    if not naics_donut_df.empty:
        fig_naics = px.pie(
            naics_donut_df,
            names="NAICS Level 2",
            values="Annual Energy",
            hole=0.62,
            color="NAICS Level 2",
            color_discrete_sequence=NAICS_COLORS,
        )
        fig_naics.update_traces(
            textinfo="percent+label",
            textposition="outside",
            sort=False,
            marker=dict(line=dict(color="#ffffff", width=2)),
            hovertemplate="<b>%{label}</b><br>%{percent} of selected NAICS<br>%{value:.2f} PJ<extra></extra>",
        )
        fig_naics.update_layout(
            height=520,
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(t=10, b=20, l=10, r=10),
            showlegend=False,
            font=dict(color="#2f3042", family="Inter, sans-serif", size=13),
        )
        fig_naics.add_annotation(
            x=0.5,
            y=0.5,
            text=f"<b>Total (PJ/yr)</b><br>{fmt_pj(naics_total)}",
            showarrow=False,
            font=dict(size=16, color="#2f3042"),
            xanchor="center",
            yanchor="middle",
        )
        st.plotly_chart(fig_naics, use_container_width=True)
    else:
        st.info("No NAICS Level 2 annual energy data is available for this selection.")

    st.markdown(
        '<div class="section-title" style="font-size: 1.05rem; margin-top: 1.4rem;">Total Annual Energy Breakdown: Industrial Process</div>',
        unsafe_allow_html=True,
    )

    if not process_df.empty:
        fig_process = px.pie(
            process_df,
            names="Industrial process",
            values="Annual Energy",
            hole=0.62,
            color="Industrial process",
            color_discrete_sequence=PROCESS_COLORS,
        )
        fig_process.update_traces(
            textinfo="percent+label",
            textposition="outside",
            sort=False,
            marker=dict(line=dict(color="#ffffff", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:.2f} PJ<extra></extra>",
        )
        fig_process.update_layout(
            height=420,
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(t=0, b=10, l=10, r=10),
            showlegend=False,
            font=dict(color="#2f3042", family="Inter, sans-serif", size=13),
        )
        fig_process.add_annotation(
            x=0.5,
            y=0.5,
            text=f"<b>Total (PJ/yr)</b><br>{fmt_pj(process_df['Annual Energy'].sum())}",
            showarrow=False,
            font=dict(size=15, color="#2f3042"),
            xanchor="center",
            yanchor="middle",
        )
        st.plotly_chart(fig_process, use_container_width=True)
    else:
        st.info("No industrial process annual energy data is available for this selection.")

with right_col:
    st.markdown(
        '<div class="section-title" style="font-size: 1.05rem; margin-top: 1.2rem;">Total Annual Energy Breakdown: Energy Source</div>',
        unsafe_allow_html=True,
    )

    if not breakdown_df.empty:
        fig_donut = px.pie(
            breakdown_df,
            names="Type",
            values="Value",
            hole=0.62,
            color="Type",
            color_discrete_map=ENERGY_SOURCE_COLORS,
        )
        fig_donut.update_traces(
            textinfo="percent+label",
            textposition="outside",
            sort=False,
            marker=dict(line=dict(color="#ffffff", width=2)),
        )
        fig_donut.update_layout(
            height=420,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            font=dict(color="#2f3042", family="Inter, sans-serif", size=13),
        )
        fig_donut.add_annotation(
            x=0.5,
            y=0.5,
            text=f"<b>Total (PJ/yr)</b><br>{fmt_pj(total_energy)}",
            showarrow=False,
            font=dict(size=16, color="#2f3042"),
            xanchor="center",
            yanchor="middle",
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No annual energy breakdown is available for this selection.")

    st.markdown(
        '<div class="section-title" style="font-size: 1.05rem; margin-top: 1.2rem;">Total Annual Energy Breakdown: Temperature</div>',
        unsafe_allow_html=True,
    )

    if not temp_donut_df.empty:
        fig_temp = px.pie(
            temp_donut_df,
            names="Temperature Range",
            values="Annual Energy",
            hole=0.62,
            color="Temperature Range",
            color_discrete_map=TEMP_COLORS,
        )
        fig_temp.update_traces(
            textinfo="percent+label",
            textposition="outside",
            sort=False,
            marker=dict(line=dict(color="#ffffff", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:.2f} PJ<extra></extra>",
        )
        fig_temp.update_layout(
            height=420,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            font=dict(color="#2f3042", family="Inter, sans-serif", size=13),
        )
        fig_temp.add_annotation(
            x=0.5,
            y=0.5,
            text=f"<b>Total (PJ/yr)</b><br>{fmt_pj(temp_donut_df['Annual Energy'].sum())}",
            showarrow=False,
            font=dict(size=16, color="#2f3042"),
            xanchor="center",
            yanchor="middle",
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.info("No annual energy by temperature data is available for this selection.")
