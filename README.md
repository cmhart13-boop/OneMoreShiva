# OneMoreShiva

Shiva is a mobile-first fantasy-football draft workspace built for a fast, ESPN-style draft-room experience while remaining an original product.

## Current product layer

- Stateful 10-team snake mock draft engine
- CPU picks that advance automatically to the user's next selection
- Draftable player pool with search and position filtering
- Queue that stays synchronized with drafted players
- Live color-coded draft board
- Auto-built roster view with FLEX/bench assignment
- Clickable player profiles and weekly visualization
- Rankings workspace
- Ask Shiva integration using the OpenAI Responses API when `OPENAI_API_KEY` is configured
- Responsive dark UI optimized for desktop and mobile
- Optional `data/players.csv` override for production player data

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

Deploy this repository with `app.py` as the entry point. To enable Ask Shiva, add this to Streamlit Secrets:

```toml
OPENAI_API_KEY = "your-key-here"
```

## Player data contract

For production data, add `data/players.csv` with these columns:

```text
name,pos,team,adp,projection,bye
```

An `id` column is optional; Shiva will generate stable IDs automatically.

The bundled starter projections are deliberately labeled as demo data. Replace them with a trusted current data feed before using projections for real draft decisions.
