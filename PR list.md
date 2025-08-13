[ ] = Open
[x] = Closed

## PR 01 — Convert to true multi‑page Streamlit app (programmatic navigation) [x]

- Rationale: Replace the single‑file selectbox with Streamlit's multi‑page framework for a clean, scalable navigation experience.
- Changes:
  - Create `app.py` that defines navigation via `st.navigation` and `st.Page` (or fallback to `pages/` directory if needed).
  - Move current stroke‑play page into `pages/stroke_play.py` (or programmatic page) and leave placeholders for match‑play rounds.
  - Remove the sidebar selectbox.
- Acceptance criteria:
  - Running `streamlit run app.py` loads a nav with at least: Stroke Play, Round of 64, Round of 32, Round of 16, Quarterfinals, Semifinals, Finals.
  - Deep links and browser back/forward work.

## PR 02 — Header logo support (SVG/JPEG/PNG) next to title [x]

- Rationale: Display Olympic Club branding in the header.
- Changes:
  - Add `assets/olympic-club-logo.(svg|png|jpg)` support; detect and render if present; fallback to text if missing.
  - Document expected path in `README.md`.
- Acceptance criteria:
  - If an image exists at `assets/olympic-club-logo.svg` (or .png/.jpg), it displays inline with the main header; otherwise, no errors and header renders as today.

## PR 03 — Overview: histogram polish and clearer ECDF title [x]

- Rationale: Improve readability of overall scoring distributions.
- Changes:
  - Add bar borders to the `TOTAL_SCORE` histogram (e.g., `marker_line_color` and `marker_line_width`).
  - Retitle ECDF to “Cumulative distribution of Total to‑Par (lower is better)” and add a short caption.
- Acceptance criteria:
  - Histogram bars have visible outlines; ECDF title/caption clearly communicate interpretation; cut/leader overlays remain.

## PR 04 — Course Analysis: clarify “Avg to‑Par by Course and Round” and add caption [x]

- Rationale: Chart is correct but needs explanation.
- Changes:
  - Add subtitle/annotation explaining calculation: average of player round scores relative to official par, split by course and round.
- Acceptance criteria:
  - Users understand what “to‑Par” means and how the aggregation is computed.

## PR 05 — Course Analysis: remove overall hole difficulty heatmap [x]

- Rationale: Redundant with Lake/Ocean tabs and adds visual repetition.
- Changes:
  - Remove the “Hole Difficulty Heatmap (Avg vs Par)” from the Overall tab.
- Acceptance criteria:
  - Overall tab shows the course averages and distributions without the heatmap; Lake/Ocean tabs retain hole‑level detail.

## PR 06 — Player Analysis: replace country pie with deemphasized bar or move to expander [ ]

- Rationale: US Amateur is predominantly Americans; the chart is low‑signal.
- Changes:
  - Either move the country composition into an expander or keep a compact horizontal bar at the bottom of the tab.
- Acceptance criteria:
  - Player Analysis focuses on performance; country chart is available but deemphasized.

## PR 07 — Player Analysis: replace gauge with simple, robust “R2 improvers vs worseners” chart [ ]

- Rationale: Current gauge/HTML is buggy and overkill.
- Changes:
  - Compute counts of players who improved, tied, or worsened from R1→R2.
  - Display as a small grouped bar or three KPI metrics; add percentage labels.
- Acceptance criteria:
  - No custom HTML/gauge; chart renders consistently and communicates counts/percents.

## PR 08 — Player Analysis: replace “Most Consistent Players” with higher‑value tables [ ]

- Rationale: Consistency can highlight two bad rounds; we want performance.
- Changes:
  - Replace with two tables: (a) Top R2 improvers (sorted by `-ROUND_DIFFERENTIAL`), (b) Best totals among made‑cut (sorted by `TOTAL_SCORE`).
- Acceptance criteria:
  - New tables render; columns include player, scores, and deltas; content is clearly performance‑oriented.

## PR 09 — Made‑the‑Cut tab: rework visuals to focus on cut dynamics [ ]

- Rationale: Current content feels thin.
- Changes:
  - Add histogram/density of `TOTAL_SCORE` colored by `MADE_CUT` with cut line overlay.
  - Add “within X shots of cut” summary table for context (e.g., ±2 shots).
  - Keep or replace “scoring average by position” if still valuable; remove “Top birdie makers”.
- Acceptance criteria:
  - Visuals directly communicate cut distribution and near‑misses; fewer low‑signal tables.

## PR 10 — Remove “Impact of Starting Nine (Round 2)” section [ ]

- Rationale: Chart is confusing/low value.
- Changes:
  - Remove the section and any dependencies.
- Acceptance criteria:
  - Player Analysis renders without that section; no references/errors.

## PR 11 — Filters: remove country filter; keep score range and Round‑2 start

- Rationale: Country adds little for US Amateur; R2 start may remain as a filter.
- Changes:
  - Remove the country multiselect; update filtering logic accordingly; keep score range and Round‑2 start select.
- Acceptance criteria:
  - Filters work without country; page performance unaffected.

## PR 12 — R1 vs R2 scatter: show legend counts for made‑cut groups [ ]

- Rationale: Quick quantification of cohort sizes.
- Changes:
  - Update legend labels (or annotations) to include counts for `MADE_CUT=True/False`.
  - Ensure 45° reference line remains.
- Acceptance criteria:
  - Legend or chart text clearly shows counts of made/missed cut.

## PR 13 — Best nine‑hole performance: show by course+side (Lake F/B, Ocean F/B)

- Rationale: “By round” is harder to digest; course+side is more intuitive.
- Changes:
  - Recompute labeling to bucket best‑nine into: Lake Front, Lake Back, Ocean Front, Ocean Back.
  - Update bar to use these four categories with counts.
- Acceptance criteria:
  - Chart shows exactly four categories; totals match players with valid nine‑hole data.

## PR 14 — Player Spotlight improvements [ ]

- Rationale: Better UX and clarity.
- Changes:
  - Sort player selector by position (leaders first; handle ties by `POS_RANK`).
  - For hole‑by‑hole vs par plots, set y‑axis ticks to integers only (`dtick=1`) and clamp domain if needed.
- Acceptance criteria:
  - Selector starts at the leader; vs‑par charts have integer y‑ticks only.

## PR 15 — Titles/captions polish across charts [ ]

- Rationale: Improve clarity and reduce ambiguity.
- Changes:
  - Add concise captions where needed (e.g., “lower is better”, “relative to par 70 on both courses”).
  - Ensure all color legends use consistent palette and wording.
- Acceptance criteria:
  - Charts have clear, concise titles and optional captions; color usage consistent across the app.

