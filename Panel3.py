import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Manufacturing Energy 2022 Classification: Unit Operations",
    layout="wide",
)

SHEET_NAME = "Process-level data"
LOCAL_FILE = "DatasetJune24Part2.xlsx"

EXPECTED = {
    "naics_l2": "NAICS Level 2",
    "naics_l1": "NAICS Level 1",
    "industrial_process": "Industrial process",
    "percent_energy": "Percent Annual energy demand in 2022",
    "annual_energy": "Annual energy demand in 2022",
    "annual_electricity": "Annual electricity demand in 2022",
    "annual_fuels": "Annual fuels demand in 2022",
    "annual_steam": "Annual fuels or electricity for steam or steam from CHP demand in 2022",
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
        background: #f3f3f6;
        color: #2f3042;
    }

    [data-testid="stAppViewContainer"],
    .main,
    .block-container {
        background: #f3f3f6 !important;
    }

    [data-testid="stHeader"] {
        background: #f3f3f6 !important;
    }

    .block-container {
        max-width: 1800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    h1, h2, h3 {
        color: #2f3042 !important;
        letter-spacing: -0.03em;
    }

    .page-title {
        font-size: 3.1rem;
        line-height: 1.05;
        font-weight: 800;
        color: #2f3042;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2f3042;
        margin-bottom: 0.4rem;
    }

    .section-subtitle {
        font-size: 0.95rem;
        color: #818191;
        margin-bottom: 1rem;
    }

    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 0.35rem 0 1.8rem 0;
    }

    .metric-card {
        flex: 1;
        background: #f7f6fb;
        border: 1px solid #e3e1ea;
        border-radius: 14px;
        padding: 0.95rem 1rem;
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

    .selector-label {
        font-size: 0.95rem;
        color: #4b4c5f;
        margin-bottom: 0.3rem;
        font-weight: 500;
    }

    div[data-baseweb="select"] > div {
        background: #efedf3 !important;
        border: 1px solid #efedf3 !important;
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

    .plot-caption {
        font-size: 0.92rem;
        color: #8b8b98;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .coverage-note {
        font-size: 0.95rem;
        color: #6f7082;
        margin-top: -0.25rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_l1_col = cols["naics_l1"]
naics_l2_col = cols["naics_l2"]
industrial_process_col = cols["industrial_process"]
percent_energy_col = cols["percent_energy"]
annual_energy_col = cols["annual_energy"]
annual_electricity_col = cols["annual_electricity"]
annual_fuels_col = cols["annual_fuels"]
annual_steam_col = cols["annual_steam"]

naics_options = sorted(df[naics_l1_col].dropna().astype(str).drop_duplicates().tolist())
selected_naics = st.selectbox("Select a NAICS Level 1 sector to generate a fact sheet", naics_options, index=0)

df_filtered = df[df[naics_l1_col].astype(str) == str(selected_naics)].copy()

coverage = num(df_filtered[percent_energy_col]).sum()
coverage_text = f"{coverage:.2%}" if coverage > 0 else "N/A"

total_energy = num(df_filtered[annual_energy_col]).sum()
total_electricity = num(df_filtered[annual_electricity_col]).sum()
total_fuels = num(df_filtered[annual_fuels_col]).sum()
total_steam = num(df_filtered[annual_steam_col]).sum()

breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

bar_df = df_filtered[[naics_l2_col, annual_energy_col]].copy()
bar_df[annual_energy_col] = pd.to_numeric(bar_df[annual_energy_col], errors="coerce")
bar_df = (
    bar_df.dropna(subset=[naics_l2_col, annual_energy_col])
    .groupby(naics_l2_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={naics_l2_col: "NAICS Level 2", annual_energy_col: "Annual Energy"})
)
bar_df = bar_df[bar_df["Annual Energy"] > 0].copy()
bar_df = bar_df.sort_values("Annual Energy", ascending=False)

bar_total = bar_df["Annual Energy"].sum()
if bar_total > 0:
    bar_df["Percent"] = (bar_df["Annual Energy"] / bar_total) * 100
else:
    bar_df["Percent"] = 0.0

process_df = df_filtered[[industrial_process_col, annual_energy_col]].copy()
process_df[annual_energy_col] = pd.to_numeric(process_df[annual_energy_col], errors="coerce")
process_df = (
    process_df.dropna(subset=[industrial_process_col, annual_energy_col])
    .groupby(industrial_process_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={industrial_process_col: "Industrial process", annual_energy_col: "Annual Energy"})
)
process_df = process_df[process_df["Annual Energy"] > 0].copy()
process_df = process_df.sort_values("Annual Energy", ascending=False)

st.markdown(
    '<div class="page-title">US Manufacturing Energy 2022 Classification: Unit Operations</div>',
    unsafe_allow_html=True,
)

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

left_col, right_col = st.columns([1.45, 1.0], gap="large")

with left_col:
    st.markdown('<div class="section-title">Percent Annual Energy by Unit Operation Classification</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="coverage-note">Selected sector: {selected_naics} · Total sector coverage: {coverage_text}</div>',
        unsafe_allow_html=True,
    )

    if not bar_df.empty:
        display_bar = bar_df.sort_values("Percent", ascending=True).copy()

        fig_bar = px.bar(
            display_bar,
            x="Percent",
            y="NAICS Level 2",
            orientation="h",
            text=display_bar["Percent"].map(fmt_pct),
        )
        fig_bar.update_traces(
            marker_color="#0f7c7c",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:.2f}% of selected NAICS<extra></extra>",
        )
        fig_bar.update_layout(
            height=max(520, len(display_bar) * 34),
            paper_bgcolor="#f3f3f6",
            plot_bgcolor="#f3f3f6",
            margin=dict(t=10, b=20, l=160, r=55),
            xaxis_title="",
            yaxis_title="",
            font=dict(color="#2f3042", family="Inter, sans-serif", size=14),
            showlegend=False,
        )
        fig_bar.update_xaxes(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            visible=False,
        )
        fig_bar.update_yaxes(
            showgrid=False,
            ticks="",
            categoryorder="array",
            categoryarray=display_bar["NAICS Level 2"].tolist(),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No NAICS Level 2 annual energy data is available for this selection.")

with right_col:
    st.markdown('<div class="selector-label">Select a unit operation (Level 2 classification) to generate a fact sheet</div>', unsafe_allow_html=True)

    unit_options = bar_df["NAICS Level 2"].astype(str).tolist() if not bar_df.empty else []
    selected_unit = st.selectbox(
        "Unit operation",
        unit_options if unit_options else ["No options available"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-title" style="font-size: 1.05rem; margin-top: 1.2rem;">Total Annual Energy Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Categorization by Energy Source</div>', unsafe_allow_html=True)

    if not breakdown_df.empty:
        fig_donut = px.pie(
            breakdown_df,
            names="Type",
            values="Value",
            hole=0.62,
            color="Type",
            color_discrete_map={
                "Annual Fuels": "#f58600",
                "Annual Steam": "#5b74b2",
                "Annual Electricity": "#2fb36d",
            },
        )
        fig_donut.update_traces(
            textinfo="percent+label",
            textposition="outside",
            sort=False,
            marker=dict(line=dict(color="#f3f3f6", width=2)),
        )
        fig_donut.update_layout(
            height=420,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="#f3f3f6",
            plot_bgcolor="#f3f3f6",
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

    st.markdown('<div class="section-subtitle" style="margin-top: 1rem;">Categorization by Industrial Process</div>', unsafe_allow_html=True)

    if not process_df.empty:
        top_process = process_df.head(8).copy()
        fig_process = px.bar(
            top_process.sort_values("Annual Energy", ascending=True),
            x="Annual Energy",
            y="Industrial process",
            orientation="h",
            text="Annual Energy",
        )
        fig_process.update_traces(
            marker_color="#e85d75",
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:.2f} PJ<extra></extra>",
        )
        fig_process.update_layout(
            height=320,
            paper_bgcolor="#f3f3f6",
            plot_bgcolor="#f3f3f6",
            margin=dict(t=0, b=10, l=120, r=40),
            xaxis_title="",
            yaxis_title="",
            font=dict(color="#2f3042", family="Inter, sans-serif", size=13),
            showlegend=False,
        )
        fig_process.update_xaxes(showgrid=False, showticklabels=False, visible=False)
        fig_process.update_yaxes(showgrid=False, ticks="")
        st.plotly_chart(fig_process, use_container_width=True)
    else:
        st.info("No industrial process annual energy data is available for this selection.")
