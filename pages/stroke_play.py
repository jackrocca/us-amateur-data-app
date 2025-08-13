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
    base_path = Path("data")
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
    # Age distribution and scoring trends
    st.subheader("Field Composition and Scoring Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution by percentile (more informative than country breakdown)
        score_percentiles = enhanced["TOTAL_SCORE"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1)
        percentile_data = {
            "Percentile": ["90th (Top 10%)", "75th (Top 25%)", "50th (Median)", "25th (Bottom 25%)", "10th (Bottom 10%)"],
            "Score": [score_percentiles[0.9], score_percentiles[0.75], score_percentiles[0.5], score_percentiles[0.25], score_percentiles[0.1]],
            "To Par": [score_percentiles[0.9] - 140, score_percentiles[0.75] - 140, score_percentiles[0.5] - 140, score_percentiles[0.25] - 140, score_percentiles[0.1] - 140]
        }
        percentile_df = pd.DataFrame(percentile_data)
        
        fig = px.bar(
            percentile_df,
            x="To Par",
            y="Percentile",
            orientation="h",
            title="Field Scoring Distribution by Percentile",
            labels={"To Par": "Strokes to Par", "Percentile": "Field Percentile"},
            color="To Par",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Course performance comparison
        ocean_better = enhanced[enhanced["COURSE_DIFFERENTIAL"] < 0]
        lake_better = enhanced[enhanced["COURSE_DIFFERENTIAL"] > 0]
        
        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Better on Ocean", 
                len(ocean_better),
                f"{len(ocean_better)/len(enhanced[enhanced['COURSE_DIFFERENTIAL'].notna()])*100:.1f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Better on Lake", 
                len(lake_better),
                f"{len(lake_better)/len(enhanced[enhanced['COURSE_DIFFERENTIAL'].notna()])*100:.1f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2c:
            # R2 Improvers vs Worseners Analysis
            st.subheader("Round 2 Performance Changes")
            
            # Calculate improvements/worsening from R1 to R2
            enhanced['R1_TO_R2_CHANGE'] = enhanced['ROUND_2_SCORE'] - enhanced['ROUND_1_SCORE']
            valid_changes = enhanced['R1_TO_R2_CHANGE'].dropna()
            
            improved_count = (valid_changes < 0).sum()  # Negative means better score
            worsened_count = (valid_changes > 0).sum()   # Positive means worse score  
            tied_count = (valid_changes == 0).sum()      # Same score
            total_count = len(valid_changes)
            
            # Create simple grouped bar chart
            change_data = pd.DataFrame({
                'Category': ['Improved', 'Tied', 'Worsened'],
                'Count': [improved_count, tied_count, worsened_count],
                'Percentage': [
                    improved_count/total_count*100,
                    tied_count/total_count*100, 
                    worsened_count/total_count*100
                ]
            })
            
            fig = px.bar(
                change_data,
                x='Category',
                y='Count',
                title='R1→R2 Performance Changes',
                color='Category',
                color_discrete_map={
                    'Improved': MADE_COLOR,
                    'Tied': NEUTRAL_COLOR, 
                    'Worsened': MISSED_COLOR
                },
                text='Count'
            )
            
            # Add percentage labels
            fig.update_traces(
                texttemplate='%{text}<br>(%{customdata:.1f}%)',
                customdata=change_data['Percentage'],
                textposition='outside'
            )
            
            fig.update_layout(
                showlegend=False,
                yaxis_title="Number of Players",
                xaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)

    # Performance-oriented tables
    st.subheader("Top Performers")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Top R2 Improvers**")
        # Calculate round 2 improvement (negative = better)
        enhanced['R2_IMPROVEMENT'] = enhanced['ROUND_1_SCORE'] - enhanced['ROUND_2_SCORE']
        r2_improvers = enhanced[enhanced['R2_IMPROVEMENT'].notna()].nlargest(10, 'R2_IMPROVEMENT')[
            ['PLAYER', 'ROUND_1_SCORE', 'ROUND_2_SCORE', 'R2_IMPROVEMENT', 'TOTAL_SCORE']
        ].copy()
        r2_improvers.columns = ['Player', 'R1 Score', 'R2 Score', 'R2 Improvement', 'Total']
        st.dataframe(r2_improvers, use_container_width=True, hide_index=True)
    
    with col_b:
        st.markdown("**Best Totals (Made Cut)**")
        made_cut_best = enhanced[enhanced['MADE_CUT']].nsmallest(10, 'TOTAL_SCORE')[
            ['PLAYER', 'POS_RANK', 'ROUND_1_SCORE', 'ROUND_2_SCORE', 'TOTAL_SCORE']
        ].copy()
        made_cut_best['TO_PAR'] = made_cut_best['TOTAL_SCORE'] - 140
        made_cut_best = made_cut_best[['PLAYER', 'POS_RANK', 'TOTAL_SCORE', 'TO_PAR']]
        made_cut_best.columns = ['Player', 'Position', 'Total Score', 'To Par']
        st.dataframe(made_cut_best, use_container_width=True, hide_index=True)

with player_tab2:
    made_cut_df = enhanced[enhanced["MADE_CUT"]]
    
    # Cut Dynamics - Histogram with cut line overlay
    st.subheader("Cut Distribution and Dynamics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of total scores colored by made cut status
        fig = go.Figure()
        
        # Add histogram for missed cut players
        missed_cut_scores = enhanced[~enhanced["MADE_CUT"]]["TOTAL_SCORE"]
        fig.add_trace(go.Histogram(
            x=missed_cut_scores,
            nbinsx=25,
            name="Missed Cut",
            marker_color=MISSED_COLOR,
            opacity=0.7,
            bingroup=1
        ))
        
        # Add histogram for made cut players
        made_cut_scores = enhanced[enhanced["MADE_CUT"]]["TOTAL_SCORE"]
        fig.add_trace(go.Histogram(
            x=made_cut_scores,
            nbinsx=25,
            name="Made Cut", 
            marker_color=MADE_COLOR,
            opacity=0.7,
            bingroup=1
        ))
        
        # Add cut line
        cut_line = enhanced[enhanced["MADE_CUT"]]["TOTAL_SCORE"].max()
        fig.add_vline(
            x=cut_line, 
            line_dash="dash", 
            line_color="black", 
            line_width=2,
            annotation_text=f"Cut Line: {cut_line}", 
            annotation_position="top"
        )
        
        fig.update_layout(
            title="Score Distribution: Cut Dynamics",
            xaxis_title="Total Score (36 holes)",
            yaxis_title="Number of Players",
            barmode="stack",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Within X shots of cut summary table
        cut_margin_analysis = []
        cut_line = enhanced[enhanced["MADE_CUT"]]["TOTAL_SCORE"].max()
        
        for margin in [1, 2, 3, 5]:
            within_range = enhanced[
                (enhanced["TOTAL_SCORE"] >= cut_line - margin) & 
                (enhanced["TOTAL_SCORE"] <= cut_line + margin)
            ]
            made_in_range = within_range["MADE_CUT"].sum()
            total_in_range = len(within_range)
            missed_in_range = total_in_range - made_in_range
            
            cut_margin_analysis.append({
                "Margin": f"±{margin}",
                "Total Players": total_in_range,
                "Made Cut": made_in_range,
                "Missed Cut": missed_in_range,
                "Cut Rate %": f"{(made_in_range/total_in_range*100):.1f}%" if total_in_range > 0 else "0%"
            })
        
        cut_margin_df = pd.DataFrame(cut_margin_analysis)
        
        st.subheader("Near-Miss Analysis")
        st.caption(f"Players within X shots of cut line ({cut_line})")
        st.dataframe(cut_margin_df, use_container_width=True, hide_index=True)
        
        # Additional context
        st.metric(
            "Tightest Miss", 
            f"+{enhanced[~enhanced['MADE_CUT']]['TOTAL_SCORE'].min() - cut_line}",
            help="Closest missed cut score relative to cut line"
        )

    # Scoring average by position (kept as valuable insight)
    st.subheader("Position vs Performance Analysis")
    fig = px.scatter(
        made_cut_df,
        x="POS_RANK",
        y="SCORING_AVERAGE", 
        title="Scoring Average by Final Position (Made Cut)",
        trendline="ols",
        hover_data=["PLAYER", "TOTAL_SCORE"],
        color_discrete_sequence=[LAKE_COLOR]
    )
    fig.update_layout(
        xaxis_title="Final Position Rank",
        yaxis_title="Scoring Average"
    )
    st.plotly_chart(fig, use_container_width=True)



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
col1, col2 = st.columns(2)

with col1:
    score_range = st.slider(
        "Total Score Range",
        min_value=int(enhanced["TOTAL_SCORE"].min()),
        max_value=int(enhanced["TOTAL_SCORE"].max()),
        value=(int(enhanced["TOTAL_SCORE"].min()), int(enhanced["TOTAL_SCORE"].max())),
    )

with col2:
    round2_start = st.selectbox("Round 2 Start", options=["All", "Front", "Back"])

# Apply filters
filtered_df = enhanced.copy()
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

# Calculate counts for legend labels
made_cut_count = filtered_df['MADE_CUT'].sum()
missed_cut_count = len(filtered_df) - made_cut_count

# Update the dataframe with count labels for legend
filtered_df_with_counts = filtered_df.copy()
filtered_df_with_counts['MADE_CUT_LABEL'] = filtered_df_with_counts['MADE_CUT'].map({
    True: f'Made Cut (n={made_cut_count})',
    False: f'Missed Cut (n={missed_cut_count})'
})

fig = px.scatter(
    filtered_df_with_counts,
    x="ROUND_1_SCORE",
    y="ROUND_2_SCORE",
    color="MADE_CUT_LABEL",
    symbol="COURSE_SEQUENCE",
    color_discrete_map={
        f'Made Cut (n={made_cut_count})': MADE_COLOR, 
        f'Missed Cut (n={missed_cut_count})': MISSED_COLOR
    },
    hover_data=["PLAYER", "POS"],
)
fig.add_shape(type="line", x0=60, y0=60, x1=85, y1=85, line=dict(color="red", dash="dash"))
fig.update_layout(legend_title_text="Cut Status")
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


