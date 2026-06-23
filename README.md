# IPL XI Selector

A data-driven playing XI decision tool for IPL franchises, built using 2022–2026 IPL data.

## Setup

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Data Sources
- **Team & match data:** 2022–2026 (359 matches) — match summaries from season-level CSVs
- **Player-level data:** 2026 only (ball-by-ball) — the only season with full delivery-level granularity available

## Features
- **XI Selector** – Optimal playing XI for any team/opponent/venue, using 2026 player form + 5-year venue stats + 5-year team H2H
- **Form Analysis** – Rolling last-N-match batting and bowling trends (2026)
- **Venue Intelligence** – 5-year ground avg scores & bat-first win rates, with 2026 phase-level run rates and top performers
- **H2H Matchups** – Player-level batter vs bowler head-to-head (2026)
- **Team H2H (5yr)** – Franchise vs franchise record across all 5 seasons, with full match history
- **Workload Monitor** – 7/14/28-day bowling load with risk flags (2026)

## Known Data Limitations
- Player-level stats (form, workload, batter-bowler H2H) are 2026-only since other seasons only provided match-level summaries, not ball-by-ball data
- Venue and team-level stats benefit from the full 5-year span (2022-2026)
