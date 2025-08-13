import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import base64

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4788;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-top: 0;
    }
    .header-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 14px;
        margin-bottom: 4px;
    }
    .header-logo {
        height: 48px;
        width: auto;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .section-header {
        color: #1f4788;
        border-bottom: 2px solid #1f4788;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .caption {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: -12px;
        margin-bottom: 12px;
        text-align: left;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Colors
LAKE_COLOR = "#3498db"
OCEAN_COLOR = "#e74c3c"
MADE_COLOR = "#2ecc71"
MISSED_COLOR = "#e74c3c"
NEUTRAL_COLOR = "#95a5a6"


# Load data
@st.cache_data
def load_data():
    base_path = Path("out")
    enhanced = pd.read_csv(base_path / "ENHANCED_DATA_PROD.csv")
    per_hole = pd.read_csv(base_path / "PER_HOLE_SCORES_PROD.csv")
    course_pars = pd.read_csv(base_path / "COURSE_PARS_PROD.csv")
    return enhanced, per_hole, course_pars


def _find_logo_path():
    assets_dir = Path("assets")
    if not assets_dir.exists():
        return None
    for ext in [".svg", ".png", ".jpg"]:
        candidate = assets_dir / f"olympic-club-logo{ext}"
        if candidate.exists():
            return candidate
    return None


def _as_data_uri(path):
    if path is None:
        return None
    try:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            mime = "image/svg+xml"
            data = path.read_text(encoding="utf-8").encode("utf-8")
        elif suffix == ".png":
            mime = "image/png"
            data = path.read_bytes()
        elif suffix in (".jpg", ".jpeg"):
            mime = "image/jpeg"
            data = path.read_bytes()
        else:
            return None
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None


# Load data
enhanced, per_hole, course_pars = load_data()

# Header with optional logo
logo_path = _find_logo_path()
logo_uri = _as_data_uri(logo_path) if logo_path else None
if logo_uri:
    header_html = (
        f'<div class="header-row">'
        f'<img class="header-logo" src="{logo_uri}" alt="Olympic Club" />'
        f'<h1 class="main-header">2025 U.S. Amateur Championship</h1>'
        f"</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">The Olympic Club, San Francisco</p>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<h1 class="main-header">2025 U.S. Amateur Championship</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">The Olympic Club, San Francisco</p>',
        unsafe_allow_html=True,
    )
st.markdown("---")

# Basic Metrics Section
st.markdown('<h2 class="section-header">Championship Overview</h2>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Players", len(enhanced), help="Total field size for stroke play")

with col2:
    made_cut = enhanced["MADE_CUT"].sum()
    st.metric(
        "Made Cut", made_cut, f"{made_cut/len(enhanced)*100:.1f}%", help="Top 64 players advance to match play"
    )

with col3:
    avg_score = enhanced["TOTAL_SCORE"].mean()
    st.metric(
        "Avg Total Score",
        f"{avg_score:.1f}",
        f"{(avg_score - 140)/140*100:+.1f}% vs par 140",
        delta_color="inverse",
    )

with col4:
    leader_score = enhanced.loc[enhanced["POS_RANK"] == 1, "TOTAL_SCORE"].iloc[0]
    st.metric("Leader Score", leader_score, f"{leader_score - 140:+d} to par", delta_color="inverse")

with col5:
    cut_line = enhanced[enhanced["MADE_CUT"]]["TOTAL_SCORE"].max()
    st.metric("Cut Line", f"+{cut_line - 140}", f"{cut_line} strokes", help="Score needed to make top 64")

# Distribution of total scores with cut/leader overlays
colA, colB = st.columns(2)
with colA:
    fig = px.histogram(
        enhanced,
        x="TOTAL_SCORE",
        nbins=25,
        title="Distribution of Total Scores (All Players)",
        color_discrete_sequence=[LAKE_COLOR],
    )
    fig.update_traces(marker_line_color="rgba(0,0,0,0.6)", marker_line_width=1)
    fig.add_vline(
        x=int(cut_line), line_dash="dash", line_color="red", annotation_text="Cut Line", annotation_position="top left"
    )
    fig.add_vline(
        x=int(leader_score), line_dash="dot", line_color="green", annotation_text="Leader", annotation_position="top right"
    )
    st.plotly_chart(fig, use_container_width=True)
with colB:
    to_par = enhanced["TOTAL_SCORE"] - 140
    fig = px.ecdf(
        to_par,
        title="Cumulative distribution of Total to‑Par (lower is better)",
    )
    fig.update_traces(line_color=NEUTRAL_COLOR)
    fig.add_vline(
        x=int(cut_line - 140), line_dash="dash", line_color="red", annotation_text="Cut (+%d)" % int(cut_line - 140)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fraction of players at or below each total to‑par after 36 holes (par 140). Lower values indicate better scoring.")

# Course Analysis Section
st.markdown('<h2 class="section-header">Course Analysis</h2>', unsafe_allow_html=True)

course_tab1, course_tab2, course_tab3 = st.tabs(["Overall", "Lake Course", "Ocean Course"])

with course_tab1:
    col1, col2 = st.columns(2)

    with col1:
        # Course difficulty comparison
        lake_avg = enhanced["LAKE_SCORE"].mean()
        ocean_avg = enhanced["OCEAN_SCORE"].mean()

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Lake Course", "Ocean Course"],
                y=[lake_avg, ocean_avg],
                text=[f"{lake_avg:.2f}", f"{ocean_avg:.2f}"],
                textposition="auto",
                marker_color=[LAKE_COLOR, OCEAN_COLOR],
            )
        )
        fig.update_layout(title="Average Score by Course", yaxis_title="Average Score", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Score distribution by course
        scores_data = []
        for _, row in enhanced.iterrows():
            if pd.notna(row["LAKE_SCORE"]):
                scores_data.append({"Course": "Lake", "Score": row["LAKE_SCORE"]})
            if pd.notna(row["OCEAN_SCORE"]):
                scores_data.append({"Course": "Ocean", "Score": row["OCEAN_SCORE"]})

        scores_df = pd.DataFrame(scores_data)
        fig = px.violin(
            scores_df,
            x="Course",
            y="Score",
            color="Course",
            box=True,
            points="all",
            title="Score Distribution by Course",
            color_discrete_map={"Lake": LAKE_COLOR, "Ocean": OCEAN_COLOR},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Per-round to-par by course (explanatory caption)
    r1 = (
        enhanced[["ROUND_1_COURSE", "ROUND_1_TO_PAR"]]
        .dropna()
        .rename(columns={"ROUND_1_COURSE": "COURSE", "ROUND_1_TO_PAR": "TO_PAR"})
    )
    r1["ROUND"] = "R1"
    r2 = (
        enhanced[["ROUND_2_COURSE", "ROUND_2_TO_PAR"]]
        .dropna()
        .rename(columns={"ROUND_2_COURSE": "COURSE", "ROUND_2_TO_PAR": "TO_PAR"})
    )
    r2["ROUND"] = "R2"
    rr = pd.concat([r1, r2], ignore_index=True)
    fig = px.bar(
        rr.groupby(["COURSE", "ROUND"]).mean(numeric_only=True).reset_index(),
        x="COURSE",
        y="TO_PAR",
        color="ROUND",
        barmode="group",
        title="Average To-Par by Course and Round",
        color_discrete_map={"R1": NEUTRAL_COLOR, "R2": LAKE_COLOR},
    )
    fig.update_layout(yaxis_title="Avg To-Par")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div class="caption">Average player score relative to official par (negative = under par). Grouped by course and round.</div>',
        unsafe_allow_html=True,
    )

with course_tab2:
    # Lake Course hole-by-hole analysis
    lake_holes = per_hole[per_hole["COURSE"] == "Lake"].copy()
    lake_pars = course_pars[course_pars["COURSE"] == "Lake"].set_index("HOLE")["PAR"].to_dict()

    # Calculate hole statistics
    hole_stats = []
    for hole in range(1, 19):
        hole_col = f"HOLE_{hole}"
        hole_scores = lake_holes[hole_col].dropna()
        if len(hole_scores) > 0:
            hole_stats.append(
                {
                    "Hole": hole,
                    "Par": lake_pars[hole],
                    "Avg Score": hole_scores.mean(),
                    "Avg vs Par": hole_scores.mean() - lake_pars[hole],
                    "Eagles": (hole_scores <= lake_pars[hole] - 2).sum(),
                    "Birdies": (hole_scores == lake_pars[hole] - 1).sum(),
                    "Pars": (hole_scores == lake_pars[hole]).sum(),
                    "Bogeys": (hole_scores == lake_pars[hole] + 1).sum(),
                    "Double+": (hole_scores >= lake_pars[hole] + 2).sum(),
                }
            )

    hole_stats_df = pd.DataFrame(hole_stats)

    # Hole difficulty chart
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=hole_stats_df["Hole"],
            y=hole_stats_df["Avg vs Par"],
            marker_color=hole_stats_df["Avg vs Par"].apply(lambda x: "#e74c3c" if x > 0 else "#2ecc71"),
            text=hole_stats_df["Avg vs Par"].round(2),
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Lake Course - Hole Difficulty (Avg Score vs Par)",
        xaxis_title="Hole",
        yaxis_title="Average vs Par",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Scoring distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hardest Holes - Lake")
        hardest = hole_stats_df.nlargest(5, "Avg vs Par")[
            ["Hole", "Par", "Avg Score", "Avg vs Par"]
        ]
        st.dataframe(hardest, use_container_width=True)

    with col2:
        st.subheader("Easiest Holes - Lake")
        easiest = hole_stats_df.nsmallest(5, "Avg vs Par")[
            ["Hole", "Par", "Avg Score", "Avg vs Par"]
        ]
        st.dataframe(easiest, use_container_width=True)

    # Scoring rates by hole (stacked)
    st.subheader("Scoring Rates by Hole - Lake")
    rates = []
    for _, r in hole_stats_df.iterrows():
        total = r["Eagles"] + r["Birdies"] + r["Pars"] + r["Bogeys"] + r["Double+"]
        if total == 0:
            continue
        rates.append(
            {
                "Hole": int(r["Hole"]),
                "Birdie or Better %": (r["Eagles"] + r["Birdies"]) / total * 100,
                "Par %": r["Pars"] / total * 100,
                "Bogey or Worse %": (r["Bogeys"] + r["Double+"]) / total * 100,
            }
        )
    rates_df = pd.DataFrame(rates).sort_values("Hole")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Birdie or Better %"], name="Birdie or Better"))
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Par %"], name="Par"))
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Bogey or Worse %"], name="Bogey or Worse"))
    fig.update_layout(barmode="stack", xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    st.plotly_chart(fig, use_container_width=True)

with course_tab3:
    # Ocean Course hole-by-hole analysis
    ocean_holes = per_hole[per_hole["COURSE"] == "Ocean"].copy()
    ocean_pars = course_pars[course_pars["COURSE"] == "Ocean"].set_index("HOLE")["PAR"].to_dict()

    # Calculate hole statistics
    hole_stats = []
    for hole in range(1, 19):
        hole_col = f"HOLE_{hole}"
        hole_scores = ocean_holes[hole_col].dropna()
        if len(hole_scores) > 0:
            hole_stats.append(
                {
                    "Hole": hole,
                    "Par": ocean_pars[hole],
                    "Avg Score": hole_scores.mean(),
                    "Avg vs Par": hole_scores.mean() - ocean_pars[hole],
                    "Eagles": (hole_scores <= ocean_pars[hole] - 2).sum(),
                    "Birdies": (hole_scores == ocean_pars[hole] - 1).sum(),
                    "Pars": (hole_scores == ocean_pars[hole]).sum(),
                    "Bogeys": (hole_scores == ocean_pars[hole] + 1).sum(),
                    "Double+": (hole_scores >= ocean_pars[hole] + 2).sum(),
                }
            )

    hole_stats_df = pd.DataFrame(hole_stats)

    # Hole difficulty chart
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=hole_stats_df["Hole"],
            y=hole_stats_df["Avg vs Par"],
            marker_color=hole_stats_df["Avg vs Par"].apply(lambda x: "#e74c3c" if x > 0 else "#2ecc71"),
            text=hole_stats_df["Avg vs Par"].round(2),
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Ocean Course - Hole Difficulty (Avg Score vs Par)",
        xaxis_title="Hole",
        yaxis_title="Average vs Par",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Scoring distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hardest Holes - Ocean")
        hardest = hole_stats_df.nlargest(5, "Avg vs Par")[
            ["Hole", "Par", "Avg Score", "Avg vs Par"]
        ]
        st.dataframe(hardest, use_container_width=True)

    with col2:
        st.subheader("Easiest Holes - Ocean")
        easiest = hole_stats_df.nsmallest(5, "Avg vs Par")[
            ["Hole", "Par", "Avg Score", "Avg vs Par"]
        ]
        st.dataframe(easiest, use_container_width=True)

    # Scoring rates by hole (stacked)
    st.subheader("Scoring Rates by Hole - Ocean")
    rates = []
    for _, r in hole_stats_df.iterrows():
        total = r["Eagles"] + r["Birdies"] + r["Pars"] + r["Bogeys"] + r["Double+"]
        if total == 0:
            continue
        rates.append(
            {
                "Hole": int(r["Hole"]),
                "Birdie or Better %": (r["Eagles"] + r["Birdies"]) / total * 100,
                "Par %": r["Pars"] / total * 100,
                "Bogey or Worse %": (r["Bogeys"] + r["Double+"]) / total * 100,
            }
        )
    rates_df = pd.DataFrame(rates).sort_values("Hole")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Birdie or Better %"], name="Birdie or Better"))
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Par %"], name="Par"))
    fig.add_trace(go.Bar(x=rates_df["Hole"], y=rates_df["Bogey or Worse %"], name="Bogey or Worse"))
    fig.update_layout(barmode="stack", xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    st.plotly_chart(fig, use_container_width=True)


# Player Analysis Section
st.markdown('<h2 class="section-header">Player Analysis</h2>', unsafe_allow_html=True)

player_tab1, player_tab2, player_tab3 = st.tabs(["Entire Field", "Made the Cut", "Missed the Cut"])

with player_tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        # Country distribution (ranked bar instead of pie)
        country_counts = enhanced["CTRY"].value_counts().head(10).sort_values()
        fig = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation="h",
            title="Top 10 Countries by Player Count",
            labels={"x": "Players", "y": "Country"},
            color_discrete_sequence=[NEUTRAL_COLOR],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Round improvement (temporary gauge retained until PR 07)
        improved = enhanced["IMPROVED_R2"].sum()
        total_with_both = enhanced["IMPROVED_R2"].notna().sum()
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=improved / total_with_both * 100,
                title={"text": "Players Who Improved in R2"},
                delta={"reference": 50},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [{"range": [0, 50], "color": "lightgray"}, {"range": [50, 100], "color": "gray"}],
                    "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 50},
                },
            )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        # Consistency leaders
        st.subheader("Most Consistent Players")
        consistent = enhanced.nsmallest(5, "CONSISTENCY_SCORE")[
            ["PLAYER", "ROUND_1_SCORE", "ROUND_2_SCORE", "CONSISTENCY_SCORE"]
        ]
        st.dataframe(consistent, use_container_width=True)

with player_tab2:
    made_cut_df = enhanced[enhanced["MADE_CUT"]]

    col1, col2 = st.columns(2)

    with col1:
        # Scoring average by position
        fig = px.scatter(
            made_cut_df,
            x="POS_RANK",
            y="SCORING_AVERAGE",
            title="Scoring Average by Position (Made Cut)",
            trendline="ols",
            hover_data=["PLAYER", "TOTAL_SCORE"],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Birdie makers
        made_cut_df = made_cut_df.assign(TOTAL_BIRDIES=made_cut_df["R1_BIRDIES"] + made_cut_df["R2_BIRDIES"])
        top_birdie_makers = made_cut_df.nlargest(10, "TOTAL_BIRDIES")[
            ["PLAYER", "POS", "TOTAL_BIRDIES", "R1_BIRDIES", "R2_BIRDIES"]
        ]
        st.subheader("Top Birdie Makers (Made Cut)")
        st.dataframe(top_birdie_makers, use_container_width=True)

    # Cut makers by starting nine
    st.subheader("Impact of Starting Nine (Round 2)")
    start_stats = made_cut_df.groupby("ROUND_2_START").agg({"PLAYER": "count", "TOTAL_SCORE": "mean", "ROUND_2_SCORE": "mean"}).round(2)
    start_stats.columns = ["Players", "Avg Total", "Avg R2 Score"]
    st.dataframe(start_stats, use_container_width=True)

with player_tab3:
    missed_cut_df = enhanced[~enhanced["MADE_CUT"]]

    col1, col2 = st.columns(2)

    with col1:
        # Where Players Struggled
        st.subheader("Where Players Struggled")
        missed_cut_df = missed_cut_df.assign(
            TOTAL_DOUBLES_PLUS=missed_cut_df["R1_DOUBLES_PLUS"] + missed_cut_df["R2_DOUBLES_PLUS"]
        )
        struggled = missed_cut_df.nlargest(10, "TOTAL_DOUBLES_PLUS")[
            ["PLAYER", "POS", "TOTAL_DOUBLES_PLUS", "TOTAL_SCORE"]
        ]
        st.dataframe(struggled, use_container_width=True)

    with col2:
        # Close misses
        st.subheader("Closest to Making Cut")
        close_misses = missed_cut_df.nsmallest(10, "CUT_MARGIN")[
            ["PLAYER", "POS", "TOTAL_SCORE", "CUT_MARGIN"]
        ].copy()
        close_misses["CUT_MARGIN"] = close_misses["CUT_MARGIN"].abs()
        close_misses.columns = ["Player", "Position", "Total Score", "Shots Missed By"]
        st.dataframe(close_misses, use_container_width=True)


# Advanced Analytics Section
st.markdown('<h2 class="section-header">Advanced Analytics</h2>', unsafe_allow_html=True)

# Interactive filters
col1, col2, col3 = st.columns(3)
with col1:
    country_filter = st.multiselect(
        "Filter by Country",
        options=["All"] + sorted(enhanced["CTRY"].unique().tolist()),
        default=["All"],
    )

with col2:
    score_range = st.slider(
        "Total Score Range",
        min_value=int(enhanced["TOTAL_SCORE"].min()),
        max_value=int(enhanced["TOTAL_SCORE"].max()),
        value=(int(enhanced["TOTAL_SCORE"].min()), int(enhanced["TOTAL_SCORE"].max())),
    )

with col3:
    round2_start = st.selectbox("Round 2 Start", options=["All", "Front", "Back"])

# Apply filters
filtered_df = enhanced.copy()
if "All" not in country_filter:
    filtered_df = filtered_df[filtered_df["CTRY"].isin(country_filter)]
filtered_df = filtered_df[(filtered_df["TOTAL_SCORE"] >= score_range[0]) & (filtered_df["TOTAL_SCORE"] <= score_range[1])]
if round2_start != "All":
    filtered_df = filtered_df[filtered_df["ROUND_2_START"] == round2_start]

# Momentum analysis
col1, col2 = st.columns(2)

with col1:
    # Round differential distribution
    fig = px.histogram(
        filtered_df,
        x="ROUND_DIFFERENTIAL",
        title="Round 2 vs Round 1 Score Differential",
        nbins=20,
        color_discrete_sequence=["#3498db"],
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="No Change")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Course differential for players who played both
    both_courses = filtered_df[filtered_df["COURSE_DIFFERENTIAL"].notna()]
    fig = px.scatter(
        both_courses,
        x="LAKE_SCORE",
        y="OCEAN_SCORE",
        title="Lake vs Ocean Performance",
        hover_data=["PLAYER", "POS"],
        trendline="ols",
    )
    fig.add_shape(type="line", x0=65, y0=65, x1=85, y1=85, line=dict(color="red", dash="dash"))
    st.plotly_chart(fig, use_container_width=True)

# R1 vs R2 scatter
st.subheader("Round 1 vs Round 2 Scores")
fig = px.scatter(
    filtered_df,
    x="ROUND_1_SCORE",
    y="ROUND_2_SCORE",
    color="MADE_CUT",
    symbol="COURSE_SEQUENCE",
    color_discrete_map={True: MADE_COLOR, False: MISSED_COLOR},
    hover_data=["PLAYER", "POS"],
)
fig.add_shape(type="line", x0=60, y0=60, x1=85, y1=85, line=dict(color="red", dash="dash"))
fig.update_layout(legend_title_text="Made Cut")
st.plotly_chart(fig, use_container_width=True)

# Best nine analysis
st.subheader("Best Nine-Hole Performances")
best_nine_dist = filtered_df["BEST_NINE_LABEL"].value_counts()
fig = go.Figure(
    data=[go.Bar(x=best_nine_dist.index, y=best_nine_dist.values, marker_color=["#2ecc71", "#3498db", "#e74c3c", "#f39c12"])]
)
fig.update_layout(title="Distribution of Best Nine-Hole Scores by Round/Side", xaxis_title="Round and Side", yaxis_title="Number of Players")
st.plotly_chart(fig, use_container_width=True)

# Statistical summary
st.subheader("Statistical Summary")
summary_stats = filtered_df[["TOTAL_SCORE", "ROUND_1_SCORE", "ROUND_2_SCORE", "LAKE_SCORE", "OCEAN_SCORE"]].describe()
st.dataframe(summary_stats.round(2), use_container_width=True)

# Player spotlight
with st.expander("Player Spotlight", expanded=False):
    player_list = sorted(enhanced["PLAYER"].unique().tolist())
    selected_player = st.selectbox("Select a player", player_list)
    p = enhanced[enhanced["PLAYER"] == selected_player].iloc[0]
    st.markdown(
        f"**{selected_player}** — POS: {p['POS']} | Total: {int(p['TOTAL_SCORE'])} ({int(p['TOTAL_SCORE'] - 140):+d})"
    )
    # Scoring breakdown
    r1_counts = [p["R1_EAGLES"], p["R1_BIRDIES"], p["R1_PARS"], p["R1_BOGEYS"], p["R1_DOUBLES_PLUS"]]
    r2_counts = [p["R2_EAGLES"], p["R2_BIRDIES"], p["R2_PARS"], p["R2_BOGEYS"], p["R2_DOUBLES_PLUS"]]
    labels = ["Eagles", "Birdies", "Pars", "Bogeys", "Doubles+"]
    fig = go.Figure(data=[go.Bar(name="R1", x=labels, y=r1_counts), go.Bar(name="R2", x=labels, y=r2_counts)])
    fig.update_layout(barmode="group", title="Round Scoring Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    # Hole-by-hole line vs par for each round
    ph = per_hole[per_hole["PLAYER"] == selected_player]
    for rnd in [1, 2]:
        row = ph[ph["ROUND"] == rnd]
        if row.empty:
            continue
        course = row["COURSE"].iloc[0]
        pars_map = course_pars[course_pars["COURSE"] == course].set_index("HOLE")["PAR"].to_dict()
        scores = [row[f"HOLE_{h}"].iloc[0] for h in range(1, 19)]
        vs_par = [scores[h - 1] - pars_map[h] if pd.notna(scores[h - 1]) else np.nan for h in range(1, 19)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, 19)), y=vs_par, mode="lines+markers"))
        fig.update_layout(
            title=f"Round {rnd} ({course}) — Hole-by-Hole vs Par",
            xaxis_title="Hole",
            yaxis_title="Strokes vs Par",
            xaxis=dict(tickmode="linear", tick0=1, dtick=1),
            yaxis=dict(dtick=1),
        )
        st.plotly_chart(fig, use_container_width=True)

# Hardest three-hole stretches
st.subheader("Hardest Three-Hole Stretches")

def hardest_stretches(course_name: str) -> pd.DataFrame:
    df = per_hole[per_hole["COURSE"] == course_name]
    pars = course_pars[course_pars["COURSE"] == course_name].set_index("HOLE")["PAR"].to_dict()
    avg_vs = []
    for hole in range(1, 19):
        hole_scores = df[f"HOLE_{hole}"].dropna()
        if len(hole_scores) == 0:
            avg = np.nan
        else:
            avg = hole_scores.mean() - pars[hole]
        avg_vs.append(avg)
    stretches = []
    for start in range(1, 17):
        window = [avg_vs[start - 1], avg_vs[start], avg_vs[start + 1]]
        if any(pd.isna(window)):
            continue
        stretches.append({"Course": course_name, "Stretch": f"{start}-{start+2}", "Avg vs Par": float(np.sum(window))})
    return pd.DataFrame(stretches).nlargest(3, "Avg vs Par")

stretches_df = pd.concat([hardest_stretches("Lake"), hardest_stretches("Ocean")])
st.dataframe(stretches_df.reset_index(drop=True), use_container_width=True)


