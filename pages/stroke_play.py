import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import base64
import datetime
import os

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
    .attribution {
        font-size: 0.9rem;
        color: #888;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 0;
    }
    .attribution a {
        color: #1f4788;
        text-decoration: none;
    }
    .attribution a:hover {
        color: #0d2647;
        text-decoration: underline;
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

# Function to save trivia results
def save_trivia_results(name, score, total, detailed_results):
    """Save trivia results to local CSV file."""
    try:
        results_file = Path("trivia_results.csv")
        
        # Create new result entry
        result_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'name': name,
            'score': score,
            'total': total,
            'percentage': round((score / total) * 100, 1),
            'detailed_results': str(detailed_results)  # Store as string for CSV
        }
        
        # Load existing results or create new DataFrame
        if results_file.exists():
            existing_df = pd.read_csv(results_file)
            new_df = pd.concat([existing_df, pd.DataFrame([result_entry])], ignore_index=True)
        else:
            new_df = pd.DataFrame([result_entry])
        
        # Save to CSV
        new_df.to_csv(results_file, index=False)
        
        return True
    except Exception as e:
        st.error(f"Failed to save results: {str(e)}")
        return False

# Trivia Modal - Must be completed before viewing the page
def show_trivia_modal():
    """Display trivia modal that must be completed before accessing the main page."""
    
    # Initialize session state for trivia
    if 'trivia_completed' not in st.session_state:
        st.session_state.trivia_completed = False
    if 'trivia_results' not in st.session_state:
        st.session_state.trivia_results = None
    if 'show_trivia_modal' not in st.session_state:
        st.session_state.show_trivia_modal = True
    
    # Trivia Questions and Correct Answers
    trivia_data = {
        "q1": {
            "question": "What was the average score on Lake Course? (Rounded to nearest whole number)",
            "answer": 75,
            "explanation": "The average score on Lake Course was 74.89, which rounds to 75."
        },
        "q2": {
            "question": "What was the average score on Ocean Course? (Rounded to nearest whole number)",
            "answer": 74,
            "explanation": "The average score on Ocean Course was 73.9, which rounds to 74."
        },
        "q3": {
            "question": "What was the hardest hole on Lake Course? (Based on average score relative to par)",
            "answer": 1,
            "explanation": "Hole 1 on Lake was the hardest, playing 0.79 strokes over par on average."
        },
        "q4": {
            "question": "What was the hardest hole on Ocean Course? (Based on average score relative to par)",
            "answer": 1,
            "explanation": "Hole 1 on Ocean was also the hardest, playing 0.66 strokes over par on average."
        },
        "q5": {
            "question": "How many holes on Lake Course were players more likely to birdie than bogey?",
            "answer": 4,
            "explanation": "4 holes on Lake (holes 7, 14, 15, and 17) had more birdies than bogeys."
        },
        "q6": {
            "question": "Did players who played Lake in Round 1 do better or worse than those who started on Ocean?",
            "answer": "Worse",
            "explanation": "Players who started on Lake averaged 149.1 vs 148.6 for those who started on Ocean (lower is better)."
        },
        "q7": {
            "question": "What was the hardest 3-hole stretch on Lake Course? (Format: X-Y, e.g., 1-3)",
            "answer": "1-3",
            "explanation": "Holes 1-3 on Lake were the hardest 3-hole stretch, playing 1.68 strokes over par."
        },
        "q8": {
            "question": "What was the easiest 3-hole stretch on Ocean Course? (Format: X-Y, e.g., 3-5)",
            "answer": "3-5",
            "explanation": "Holes 3-5 on Ocean were the easiest stretch, playing only 0.13 strokes over par."
        },
        "q9": {
            "question": "Which 9-hole stretch did players perform best on?",
            "answer": "Ocean Front",
            "explanation": "Ocean Front 9 had the lowest average score at 4.10 strokes per hole."
        },
        "q10": {
            "question": "Which player had the worst swing between rounds 1 and round 2, and by how many strokes?",
            "answer": {"player": "Connor Williams", "strokes": 16},
            "explanation": "Connor Williams R1 69 → R2 85 Yikes! A devastating +16 stroke swing from Ocean to Lake."
        }
    }
    
    # Show modal if trivia not completed
    if not st.session_state.trivia_completed:
        if st.session_state.show_trivia_modal:
            
            @st.dialog("🏆 US Amateur Championship Trivia")
            def trivia_modal():
                st.markdown("**Test your knowledge of the championship data!**")
                st.markdown("Complete this 10-question trivia to unlock the full stroke play analysis.")
                
                with st.form("trivia_form"):
                    user_answers = {}
                    
                    # Name field
                    user_answers['name'] = st.text_input(
                        "Enter your name:",
                        placeholder="Your name here...",
                        help="This will be saved with your trivia results"
                    )
                    st.markdown("---")
                    
                    # Question 1
                    user_answers['q1'] = st.number_input(
                        trivia_data['q1']['question'], 
                        min_value=60, max_value=90, value=70, step=1
                    )
                    
                    # Question 2  
                    user_answers['q2'] = st.number_input(
                        trivia_data['q2']['question'],
                        min_value=60, max_value=90, value=70, step=1
                    )
                    
                    # Question 3
                    user_answers['q3'] = st.selectbox(
                        trivia_data['q3']['question'],
                        options=list(range(1, 19))
                    )
                    
                    # Question 4
                    user_answers['q4'] = st.selectbox(
                        trivia_data['q4']['question'],
                        options=list(range(1, 19))
                    )
                    
                    # Question 5
                    user_answers['q5'] = st.number_input(
                        trivia_data['q5']['question'],
                        min_value=0, max_value=18, value=2, step=1
                    )
                    
                    # Question 6
                    user_answers['q6'] = st.selectbox(
                        trivia_data['q6']['question'],
                        options=["Better", "Worse", "Same"]
                    )
                    
                    # Question 7
                    stretch_options = [f"{i}-{i+2}" for i in range(1, 17)]
                    user_answers['q7'] = st.selectbox(
                        trivia_data['q7']['question'],
                        options=stretch_options
                    )
                    
                    # Question 8
                    user_answers['q8'] = st.selectbox(
                        trivia_data['q8']['question'],
                        options=stretch_options
                    )
                    
                    # Question 9
                    user_answers['q9'] = st.selectbox(
                        trivia_data['q9']['question'],
                        options=["Ocean Front", "Ocean Back", "Lake Front", "Lake Back"]
                    )
                    
                    # Question 10 - Two part question
                    st.markdown(trivia_data['q10']['question'])
                    col_player, col_strokes = st.columns([2, 1])
                    
                    with col_player:
                        # Top 5 worst swings based on our calculation
                        worst_swing_players = [
                            "Connor Williams", "Mesa Falleur", "Richard Teder", "Ieuan Jones", "Jager Pain"
                        ]
                        user_answers['q10_player'] = st.selectbox(
                            "Select player:",
                            options=worst_swing_players,
                            key="q10_player"
                        )
                    
                    with col_strokes:
                        user_answers['q10_strokes'] = st.number_input(
                            "Stroke difference:",
                            min_value=1, max_value=20, value=5, step=1,
                            key="q10_strokes"
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Submit Trivia", type="primary", use_container_width=True)
                    with col2:
                        skip = st.form_submit_button("Skip Trivia", use_container_width=True)
                    
                    if submitted:
                        # Validate name is provided
                        if not user_answers['name'].strip():
                            st.error("Please enter your name to submit the trivia!")
                            st.stop()
                        
                        # Calculate results
                        correct_count = 0
                        results = {}
                        
                        for q_id, q_data in trivia_data.items():
                            if q_id == 'q10':
                                # Handle two-part question
                                user_player = user_answers['q10_player']
                                user_strokes = user_answers['q10_strokes']
                                correct_player = q_data['answer']['player']
                                correct_strokes = q_data['answer']['strokes']
                                
                                player_correct = user_player == correct_player
                                strokes_correct = user_strokes == correct_strokes
                                is_correct = player_correct and strokes_correct
                                
                                if is_correct:
                                    correct_count += 1
                                
                                user_answer_display = f"{user_player} (+{user_strokes} strokes)"
                                correct_answer_display = f"{correct_player} (+{correct_strokes} strokes)"
                                
                                results[q_id] = {
                                    'question': q_data['question'],
                                    'user_answer': user_answer_display,
                                    'correct_answer': correct_answer_display,
                                    'is_correct': is_correct,
                                    'explanation': q_data['explanation']
                                }
                            else:
                                # Handle regular questions
                                user_answer = user_answers[q_id]
                                correct_answer = q_data['answer']
                                
                                is_correct = user_answer == correct_answer
                                if is_correct:
                                    correct_count += 1
                                
                                results[q_id] = {
                                    'question': q_data['question'],
                                    'user_answer': user_answer,
                                    'correct_answer': correct_answer,
                                    'is_correct': is_correct,
                                    'explanation': q_data['explanation']
                                }
                        
                        # Store results in session state
                        trivia_results = {
                            'name': user_answers['name'].strip(),
                            'score': correct_count,
                            'total': len(trivia_data),
                            'results': results
                        }
                        
                        # Save results to file
                        if save_trivia_results(
                            trivia_results['name'], 
                            trivia_results['score'], 
                            trivia_results['total'], 
                            trivia_results['results']
                        ):
                            st.success(f"Results saved for {trivia_results['name']}!")
                        
                        st.session_state.trivia_results = trivia_results
                        st.session_state.trivia_completed = True
                        st.session_state.show_trivia_modal = False
                        st.rerun()
                    
                    if skip:
                        st.session_state.trivia_completed = True
                        st.session_state.show_trivia_modal = False
                        st.session_state.trivia_results = None
                        st.rerun()
            
            trivia_modal()
        
        return False  # Don't show main content
    
    else:
        # Show results if trivia was completed
        if st.session_state.trivia_results:
            name = st.session_state.trivia_results['name']
            score = st.session_state.trivia_results['score']
            total = st.session_state.trivia_results['total']
            percentage = (score / total) * 100
            
            st.success(f"🎉 Trivia Complete, {name}! You scored {score}/{total} ({percentage:.1f}%)")
            
            with st.expander("📊 View Your Trivia Results", expanded=False):
                results = st.session_state.trivia_results['results']
                
                for q_id, result in results.items():
                    if result['is_correct']:
                        st.success(f"✅ **{result['question']}**")
                        st.write(f"Your answer: {result['user_answer']} ✓")
                    else:
                        st.error(f"❌ **{result['question']}**")
                        st.write(f"Your answer: {result['user_answer']}")
                        st.write(f"Correct answer: {result['correct_answer']}")
                    
                    st.info(f"📖 {result['explanation']}")
                    st.markdown("---")
            
            # Option to retake
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Retake Trivia", use_container_width=True):
                    st.session_state.trivia_completed = False
                    st.session_state.trivia_results = None
                    st.session_state.show_trivia_modal = True
                    st.rerun()
        else:
            # Trivia was skipped
            st.info("ℹ️ You skipped the trivia. You can take it anytime by refreshing the page.")
        
        st.markdown("---")
        return True  # Show main content

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

# Attribution line
st.markdown(
    '<p class="attribution">Built by <a href="https://github.com/jackrocca/us-amateur-data-app" target="_blank">🔗 Jack Rocca</a></p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Show trivia modal - if not completed, stop here
if not show_trivia_modal():
    st.stop()

# Basic Metrics Section
st.markdown('<h2 class="section-header">Championship Overview</h2>', unsafe_allow_html=True)

with st.container(border=True):
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
with st.container(border=True):
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

st.divider()

# Course Analysis Section
st.markdown('<h2 class="section-header">Course Analysis</h2>', unsafe_allow_html=True)

course_tab1, course_tab2, course_tab3 = st.tabs(["Overall", "Lake Course", "Ocean Course"])

with course_tab1:
    with st.container(border=True):
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
        st.caption("Relative to par 70 on both courses. Lower scores indicate better performance.")

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
        st.caption("Distribution of individual round scores. Box plots show quartiles, violin shape shows density.")

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

    with st.container(border=True):
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

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Positive values indicate holes playing above par (harder), negative values below par (easier).")

    # Scoring rates by hole (stacked)
    
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
    fig.update_layout(title = "Scoring Rates by Hole - Lake", barmode="stack", xaxis=dict(tickmode="linear", tick0=1, dtick=1))

    with st.container(border=True):
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
        margin=dict(t=40, b=40, l=40, r=40),
    )

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Positive values indicate holes playing above par (harder), negative values below par (easier).")

    # Scoring rates by hole (stacked)

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
    fig.update_layout(title = "Scoring Rates by Hole - Ocean", barmode="stack", xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)

st.divider()
# Player Analysis Section
st.markdown('<h2 class="section-header">Player Analysis</h2>', unsafe_allow_html=True)

player_tab1, player_tab2, player_tab3, player_tab4 = st.tabs(["Entire Field", "Made the Cut", "Missed the Cut", "Player Spotlight"])

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
            # R2 Improvers vs Worseners Analysis
            
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
    st.caption("Correlation between final position and scoring average among players who made the cut.")



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

with player_tab4:
    # Dynamic Player Data Viewer
    st.subheader("Player Data Viewer")
    col_slider, col_info = st.columns([3, 1])

    with col_slider:
        num_players = st.slider(
            "Number of players to display",
            min_value=10,
            max_value=len(enhanced),
            value=64,  # Top 64 by default
            step=10,
            help="Adjust to view top N players by position"
        )

    with col_info:
        st.metric("Total Players", len(enhanced))

    # Display top N players in scrollable container
    top_players = enhanced.sort_values(['POS_RANK', 'PLAYER']).head(num_players)

    # Select relevant columns for display
    display_columns = [
        'PLAYER', 'POS', 'TO_PAR', 'MADE_CUT', 'TOTAL_SCORE', 
        'ROUND_1_SCORE', 'ROUND_2_SCORE', 'CTRY', 'ROUND_1_COURSE', 
        'ROUND_2_COURSE', 'SCORING_AVERAGE'
    ]

    # Create a container with fixed height for scrolling
    with st.container(height=400):
        st.dataframe(
            top_players[display_columns], 
            use_container_width=True,
            hide_index=True,
            column_config={
                'PLAYER': 'Player',
                'POS': 'Position', 
                'TO_PAR': 'To Par',
                'MADE_CUT': st.column_config.CheckboxColumn('Made Cut'),
                'TOTAL_SCORE': 'Total Score',
                'ROUND_1_SCORE': 'R1 Score',
                'ROUND_2_SCORE': 'R2 Score', 
                'CTRY': 'Country',
                'ROUND_1_COURSE': 'R1 Course',
                'ROUND_2_COURSE': 'R2 Course',
                'SCORING_AVERAGE': 'Avg Score'
            }
        )

    st.caption(f"Displaying top {num_players} players by position. Use slider above to adjust number of players shown.")
    
    
    # Individual Player Analysis
    st.markdown("#### Individual Player Analysis")
    
    # Sort players by position (leaders first, handle ties by POS_RANK)
    player_standings = enhanced.sort_values(['POS_RANK', 'PLAYER'])[['PLAYER', 'POS']].copy()
    player_display_list = [f"{row['PLAYER']} (Pos: {row['POS']})" for _, row in player_standings.iterrows()]
    player_name_list = player_standings['PLAYER'].tolist()
    
    selected_display = st.selectbox("Select a player", player_display_list, key="player_spotlight_selector")
    # Extract actual player name from display string
    selected_player = player_name_list[player_display_list.index(selected_display)]
    p = enhanced[enhanced["PLAYER"] == selected_player].iloc[0]
    
    # Player summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Position", p['POS'])
    with col2:
        st.metric("Total Score", f"{int(p['TOTAL_SCORE'])}", f"{int(p['TOTAL_SCORE'] - 140):+d} to par")
    with col3:
        st.metric("Made Cut", "Yes" if p['MADE_CUT'] else "No")
    with col4:
        st.metric("Country", p['CTRY'])
    
    
    # Scoring breakdown
    st.markdown("#### Round Scoring Breakdown")
    r1_counts = [p["R1_EAGLES"], p["R1_BIRDIES"], p["R1_PARS"], p["R1_BOGEYS"], p["R1_DOUBLES_PLUS"]]
    r2_counts = [p["R2_EAGLES"], p["R2_BIRDIES"], p["R2_PARS"], p["R2_BOGEYS"], p["R2_DOUBLES_PLUS"]]
    labels = ["Eagles", "Birdies", "Pars", "Bogeys", "Doubles+"]
    fig = go.Figure(data=[go.Bar(name="R1", x=labels, y=r1_counts), go.Bar(name="R2", x=labels, y=r2_counts)])
    fig.update_layout(barmode="group", title="Round Scoring Breakdown")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Count of scoring outcomes by round for the selected player.")

    # Hole-by-hole line vs par for each round
    st.markdown("#### Hole-by-Hole Performance")
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
            yaxis=dict(dtick=1, tickmode="linear"),
        )
        st.plotly_chart(fig, use_container_width=True)


# Advanced Analytics Section
st.divider()
st.markdown('<h2 class="section-header">Advanced Analytics</h2>', unsafe_allow_html=True)

score_range = st.slider(
    "Total Score Range",
    min_value=int(enhanced["TOTAL_SCORE"].min()),
    max_value=int(enhanced["TOTAL_SCORE"].max()),
    value=(int(enhanced["TOTAL_SCORE"].min()), int(enhanced["TOTAL_SCORE"].max())),
    )

# Apply filters
filtered_df = enhanced.copy()
filtered_df = filtered_df[(filtered_df["TOTAL_SCORE"] >= score_range[0]) & (filtered_df["TOTAL_SCORE"] <= score_range[1])]

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
    fig.update_traces(marker_line_color="rgba(0,0,0,0.6)", marker_line_width=1)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Negative values indicate improvement in Round 2 (lower score is better).")

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
    st.caption("Diagonal line represents equal performance on both courses. Points below favor Ocean, above favor Lake.")

# R1 vs R2 scatter
st.subheader("Round 1 vs Round 2 Scores")

# Calculate counts for legend labels by course sequence and cut status
filtered_df_with_counts = filtered_df.copy()

# Create a detailed label that includes course sequence and cut status counts
def create_cut_label(row):
    cut_status = row['MADE_CUT']
    course_seq = row['COURSE_SEQUENCE']
    
    # Count for this specific combination
    count = len(filtered_df[(filtered_df['MADE_CUT'] == cut_status) & (filtered_df['COURSE_SEQUENCE'] == course_seq)])
    
    if cut_status:
        return f'Made Cut - {course_seq} (n={count})'
    else:
        return f'Missed Cut - {course_seq} (n={count})'

filtered_df_with_counts['MADE_CUT_LABEL'] = filtered_df_with_counts.apply(create_cut_label, axis=1)

# Create color mapping for all possible label combinations
unique_labels = filtered_df_with_counts['MADE_CUT_LABEL'].unique()
color_map = {}
for label in unique_labels:
    if 'Made Cut' in label:
        color_map[label] = MADE_COLOR
    else:
        color_map[label] = MISSED_COLOR

fig = px.scatter(
    filtered_df_with_counts,
    x="ROUND_1_SCORE",
    y="ROUND_2_SCORE",
    color="MADE_CUT_LABEL",
    symbol="COURSE_SEQUENCE",
    color_discrete_map=color_map,
    hover_data=["PLAYER", "POS"],
)
fig.add_shape(type="line", x0=60, y0=60, x1=85, y1=85, line=dict(color="red", dash="dash"))
fig.update_layout(legend_title_text="Cut Status")
st.plotly_chart(fig, use_container_width=True)
st.caption("45-degree line represents consistent performance between rounds. Points below line show Round 2 improvement.")

# Best nine analysis
st.subheader("Best Nine-Hole Performances")

# Convert best nine labels to course+side format
def convert_to_course_side(row):
    label = row['BEST_NINE_LABEL']
    if pd.isna(label):
        return None
    
    # Map round/side to course/side based on the course sequence
    if label == 'R1 Front':
        course = row['ROUND_1_COURSE']
        return f"{course} Front"
    elif label == 'R1 Back':
        course = row['ROUND_1_COURSE'] 
        return f"{course} Back"
    elif label == 'R2 Front':
        course = row['ROUND_2_COURSE']
        return f"{course} Front"
    elif label == 'R2 Back':
        course = row['ROUND_2_COURSE']
        return f"{course} Back"
    else:
        return label

filtered_df_nine = filtered_df.copy()
filtered_df_nine['COURSE_SIDE_LABEL'] = filtered_df_nine.apply(convert_to_course_side, axis=1)

best_nine_dist = filtered_df_nine['COURSE_SIDE_LABEL'].value_counts()

# Ensure we have exactly 4 categories in the expected order
expected_categories = ["Lake Front", "Lake Back", "Ocean Front", "Ocean Back"]
category_counts = []
for cat in expected_categories:
    count = best_nine_dist.get(cat, 0)
    category_counts.append(count)

fig = go.Figure(
    data=[go.Bar(
        x=expected_categories, 
        y=category_counts, 
        marker_color=[LAKE_COLOR, LAKE_COLOR, OCEAN_COLOR, OCEAN_COLOR],
        text=category_counts,
        textposition='auto'
    )]
)
fig.update_layout(
    title="Distribution of Best Nine-Hole Scores by Course+Side", 
    xaxis_title="Course and Side", 
    yaxis_title="Number of Players"
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Shows where players recorded their best nine-hole score during the championship.")

# Statistical summary
st.subheader("Statistical Summary")
summary_stats = filtered_df[["TOTAL_SCORE", "ROUND_1_SCORE", "ROUND_2_SCORE", "LAKE_SCORE", "OCEAN_SCORE"]].describe()
st.dataframe(summary_stats.round(2), use_container_width=True)
st.caption("Descriptive statistics for scoring across all filtered players.")



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
st.caption("Most challenging consecutive three-hole sequences based on average score vs par.")


