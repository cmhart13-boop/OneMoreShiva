# One More Shiva

One More Shiva is a mobile-first fantasy-football decision system built for ESPN-style full-PPR play.

## Product idea

Shiva is not trying to replace a league host. It is the intelligence layer that helps a fantasy manager make better decisions faster.

The product is organized around:

- **Shiva Says** — the decision-first home experience
- **The Shiva Edge** — floor, ceiling, consistency and roster-context thinking
- **Draft Room** — rankings, snake-draft board, queue and roster construction
- **Shiva Lab** — player comparison and historical evidence
- **Shiva Blast** — fantasy news surfaced inside the Shiva experience
- **Player profiles** — season and week-level ESPN full-PPR history

## Production architecture

There is one production execution path:

```text
app.py
  -> app_core.py
      -> current_rankings.csv
      -> player_weekly_master_2014_2025.csv.gz
```

`app.py` is the Streamlit entrypoint. `app_core.py` owns the product UI and application logic.

The production app no longer executes a legacy app file, no longer relies on a runtime compile patch, and no longer reads the two primary datasets from the Draft-Coach repository.

## Local data

- `current_rankings.csv` — current ranking / ADP board used by the app
- `player_weekly_master_2014_2025.csv.gz` — historical weekly player dataset

Transferred data is not considered independently verified merely because it exists in this repository. Fantasy data should follow the project's normal validation workflow before new claims are treated as verified.

## Streamlit

Deploy with:

```text
app.py
```

To enable OpenAI-backed Ask Shiva analysis, configure `OPENAI_API_KEY` in Streamlit Secrets. Historical calculations supported directly by the local datasets do not require an OpenAI key.

## Product principle

**Raise the floor. Keep the ceiling.**

Every screen should reduce decision friction rather than simply display more information.
