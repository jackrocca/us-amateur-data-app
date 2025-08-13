## USGA U.S. Amateur (2025) — Project Overview

This repository contains tooling and data products for the 2025 U.S. Amateur Championship at The Olympic Club. It includes scrapers, data engineering scripts, production-ready tables, and a Streamlit dashboard for analysis.

### Source
- Official scoring page: [USGA U.S. Amateur Scoring](https://championships.usga.org/usamateur/2025/scoring.html)

---

## PROD Data Tables
All final data products live in `out/` and are designed for fast analytics and visualization.

### 1) `USAM_2025_SCORES_PROD.csv`
One row per player. Columns:
- `POS` — Final leaderboard position after stroke play (e.g., `1`, `T12`)
- `CTRY` — Country
- `PLAYER` — Player name
- `TO_PAR` — Total relative-to-par (e.g., `-8`, `E`, `+2`)
- `ROUND_1_COURSE` — `Lake` or `Ocean` (inferred as opposite of R2 course)
- `ROUND_1_SCORE` — Round 1 strokes (int)
- `ROUND_2_COURSE` — `Lake` or `Ocean` (parsed from `THRU`)
- `ROUND_2_START` — `Front` or `Back` (parsed from `THRU` asterisk)
- `ROUND_2_SCORE` — Round 2 strokes (int)
- `TOTAL` — Total strokes after 2 rounds

Build script: `build_prod_scores.py`

### 2) `PER_HOLE_SCORES_PROD.csv`
Two rows per player (one per round). Columns:
- `PLAYER`, `ROUND` — Round number (1 or 2)
- `COURSE` — `Lake` or `Ocean`
- `HOLE_1` … `HOLE_9`, `OUT`, `HOLE_10` … `HOLE_18`, `IN`, `TOTAL` — Hole-by-hole strokes and sums
- `POS` — Player position recalculated at the conclusion of that round

Build script: `build_prod_per_hole.py`

### 3) `COURSE_PARS_PROD.csv`
Hole metadata for each course (long format). Columns: `COURSE`, `HOLE`, `PAR`, `YARDS`.

### 4) `ENHANCED_DATA_PROD.csv`
Analytic, feature-rich table joining player totals with per-hole scoring and course pars. Selected columns:
- Identity: `PLAYER`, `POS`, `POS_RANK`, `IS_TIED`, `CTRY`, `TO_PAR`
- Cut features: `MADE_CUT` (top 64), `CUT_MARGIN`
- Round summaries: `ROUND_1_COURSE`, `ROUND_1_SCORE`, `ROUND_1_TO_PAR`, `ROUND_2_COURSE`, `ROUND_2_START`, `ROUND_2_SCORE`, `ROUND_2_TO_PAR`, `TOTAL_SCORE`, `COURSE_SEQUENCE`
- Per-hole: `R1_HOLE_1`…`R1_HOLE_18`, `R1_OUT`, `R1_IN`, and same for R2
- Distributions: `R1_EAGLES`, `R1_BIRDIES`, `R1_PARS`, `R1_BOGEYS`, `R1_DOUBLES_PLUS` and same for R2 (computed vs official pars)
- Performance: `BEST_NINE_SCORE`, `BEST_NINE_LABEL`, `ROUND_DIFFERENTIAL`, `IMPROVED_R2`, `SCORING_AVERAGE`, `CONSISTENCY_SCORE`
- Course-specific: `LAKE_SCORE`, `OCEAN_SCORE`, `COURSE_DIFFERENTIAL`
- Rankings: `R1_RANK`, `R2_RANK`, `RANK_CHANGE`, `PERCENTILE`
- Data quality: `HAS_COMPLETE_HOLES`, `MISSING_HOLES_COUNT`

Build script: `build_enhanced_prod.py`

---

## Developer Data (for context)
- `out/usam_2025_scores.csv` — Raw leaderboard export (dev)
- `per_hole_scores.csv` — Intermediate per-hole rows (dev)

---

## Streamlit App
Interactive dashboard for analysis of stroke play and (future) match play rounds.

### Pages
- Stroke Play (implemented)
- Round of 64 (placeholder)
- Round of 32 (placeholder)
- Round of 16 (placeholder)
- Quarterfinals (placeholder)
- Semifinals (placeholder)
- Finals (placeholder)

### Stroke Play Page (data-driven from PROD tables only)
- Overview metrics: field size, made cut count, leader score, cut line, average scores
- Course analysis: average scores by course, distribution plots, course sequence impact, hardest/easiest holes
- Player analysis: field vs made cut vs missed cut, improvement rates, consistency leaders, close misses
- Advanced analytics: interactive filters, round differential distribution, Lake vs Ocean performance, best nine analysis

### Run Locally
1) Create/activate venv and install requirements:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_streamlit.txt
```
2) Generate PROD tables (if not present):
```
python build_prod_scores.py
python build_prod_per_hole.py
python build_enhanced_prod.py
```
3) Launch the dashboard (multi-page):
```
streamlit run app.py
```

---

## Notes
- PROD tables are idempotent and can be rebuilt at any time using the scripts above.
- All analytics in the app derive strictly from PROD data sources.

---

## Assets

Optional header logo support is available. Place one of the following files in `assets/`:

- `assets/olympic-club-logo.svg`
- `assets/olympic-club-logo.png`
- `assets/olympic-club-logo.jpg`

If present, the logo will render inline next to the main header. If the file is missing, the app falls back to the text header without errors.
