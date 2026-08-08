# OneMoreShiva

Shiva is a mobile-first fantasy-football draft workspace built for a fast ESPN/DraftSharks-style workflow while remaining an original product.

## Live product layer

- Stateful 10-team snake mock draft engine
- CPU picks that advance automatically to the user's next selection
- Real 2026 ranking/ADP board loaded from `cmhart13-boop/Draft-Coach/current_rankings.csv`
- Search and position filtering across the current player pool
- Queue synchronized automatically with drafted players
- Color-coded draft board that collapses to a vertical mobile layout instead of requiring horizontal scrolling
- Auto-built roster view with FLEX and bench assignment
- Clickable player profiles from Home, Rankings, and Mock Draft
- Real historical weekly player data from the 2014–2025 master dataset
- Season selector on every matched player profile
- Actual week-by-week ESPN full-PPR scores and position-specific box-score stats
- Career season history with games, PPR totals, PPG, 15+ point weeks, and 20+ point weeks
- Ask Shiva integration grounded in the same rankings and weekly player data
- Direct stat/PPG questions calculated locally from the database before an AI answer is generated
- Responsive two-row mobile navigation with no horizontal navigation requirement

## Data sources

The app reads the following existing files from the `Draft-Coach` repository without modifying that repository:

- `current_rankings.csv` — current 2026 player rankings, position ranks, ADP, team and bye data
- `player_weekly_master_2014_2025.csv.gz` — historical regular-season weekly player statistics
- `player_birth_dates.csv` — player birth-date data used for age context

Historical fantasy scoring is calculated as ESPN full 1-point PPR: 1 point per reception, 0.1 per rushing/receiving yard, 0.04 per passing yard, 6 per rushing/receiving TD, 4 per passing TD, -2 per interception, -2 per lost fumble, and 2 per two-point conversion.

## Streamlit Cloud

Deploy this repository with `app.py` as the entry point. The rankings and player-profile database work independently of OpenAI.

To enable full Ask Shiva recommendations, add this to Streamlit Secrets:

```toml
OPENAI_API_KEY = "your-key-here"
```

Without an API key, direct supported historical stat questions can still be answered from the connected database.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
