from __future__ import annotations

import hashlib
import os
import random
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# -----------------------------------------------------------------------------
# APP CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Shiva Fantasy Football",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# DESIGN SYSTEM
# -----------------------------------------------------------------------------
CSS = r"""
<style>
:root {
  --bg: #0b0d10;
  --panel: #12161b;
  --panel-2: #171c22;
  --line: #252b33;
  --text: #f7f8fa;
  --muted: #98a2ad;
  --red: #e31837;
  --green: #23c16b;
  --qb: #8f63e9;
  --rb: #28b8b0;
  --wr: #4d92ff;
  --te: #f08b38;
  --dst: #e7c64a;
}

html, body, [class*="css"] { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
.block-container { max-width: 1500px; padding-top: .75rem; padding-bottom: 5rem; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.shiva-shell { border: 1px solid var(--line); background: linear-gradient(180deg,#11151a,#0e1115); border-radius: 16px; overflow: hidden; }
.topbar { min-height: 68px; display:flex; align-items:center; justify-content:space-between; gap:18px; padding:12px 18px; border-bottom:1px solid var(--line); }
.brand { display:flex; align-items:center; gap:12px; }
.brand-mark { width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#f22b45,#a5081d); display:flex; align-items:center; justify-content:center; font-size:23px; box-shadow:0 8px 24px rgba(227,24,55,.25); }
.brand-title { font-size:20px; font-weight:900; letter-spacing:-.4px; }
.brand-sub { color:var(--muted); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; }
.live-pill { display:inline-flex; align-items:center; gap:7px; color:#d8dde3; font-size:12px; font-weight:800; border:1px solid var(--line); background:#151a20; padding:8px 10px; border-radius:999px; }
.live-dot { width:8px; height:8px; border-radius:99px; background:var(--green); box-shadow:0 0 0 4px rgba(35,193,107,.12); }

.hero { padding:20px 20px 10px; }
.hero h1 { margin:0; color:#fff; font-size:clamp(27px,4vw,46px); line-height:1; letter-spacing:-1.5px; }
.hero p { margin:10px 0 0; color:var(--muted); font-size:14px; }

.kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; padding:10px 20px 20px; }
.kpi { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:12px 14px; }
.kpi-label { color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:1px; font-weight:800; }
.kpi-value { color:#fff; font-size:20px; font-weight:900; margin-top:3px; }

.section-title { display:flex; justify-content:space-between; align-items:end; gap:10px; margin:6px 0 12px; }
.section-title h2 { margin:0; color:#fff; font-size:22px; letter-spacing:-.5px; }
.section-title span { color:var(--muted); font-size:12px; }

.player-row { display:grid; grid-template-columns:38px 1.6fr .5fr .55fr .55fr .55fr; align-items:center; gap:8px; min-height:58px; padding:8px 10px; margin-bottom:6px; border:1px solid var(--line); border-radius:11px; background:var(--panel); }
.rank { width:31px; height:31px; border-radius:9px; display:flex; align-items:center; justify-content:center; background:#1e242b; color:#d8dde3; font-weight:900; font-size:12px; }
.player-name { color:#fff; font-weight:900; font-size:14px; line-height:1.15; }
.player-meta { color:var(--muted); font-size:11px; margin-top:3px; }
.cell-label { color:var(--muted); font-size:9px; text-transform:uppercase; font-weight:800; letter-spacing:.6px; }
.cell-value { color:#fff; font-size:13px; font-weight:850; }

.pos { display:inline-flex; align-items:center; justify-content:center; min-width:31px; border-radius:6px; padding:4px 6px; font-weight:950; font-size:10px; color:#fff; }
.pos-QB { background:var(--qb); } .pos-RB { background:var(--rb); } .pos-WR { background:var(--wr); } .pos-TE { background:var(--te); } .pos-DST { background:var(--dst); color:#161616; }

.board-wrap { overflow-x:auto; border:1px solid var(--line); border-radius:14px; background:#0d1014; padding:9px; }
.board { display:grid; gap:6px; min-width:900px; }
.pick { min-height:68px; border-radius:9px; padding:8px; border:1px solid rgba(255,255,255,.08); display:flex; flex-direction:column; justify-content:space-between; }
.pick.empty { background:#151a20; color:#66707c; }
.pick.QB { background:rgba(143,99,233,.23); border-color:rgba(143,99,233,.45); }
.pick.RB { background:rgba(40,184,176,.21); border-color:rgba(40,184,176,.42); }
.pick.WR { background:rgba(77,146,255,.22); border-color:rgba(77,146,255,.44); }
.pick.TE { background:rgba(240,139,56,.22); border-color:rgba(240,139,56,.45); }
.pick.DST { background:rgba(231,198,74,.24); border-color:rgba(231,198,74,.46); }
.pick-no { color:#9da6af; font-size:9px; font-weight:800; }
.pick-name { color:#fff; font-size:11px; line-height:1.05; font-weight:900; }
.pick-meta { color:#aeb6bf; font-size:9px; font-weight:700; }

.roster-card { border:1px solid var(--line); border-radius:12px; background:var(--panel); overflow:hidden; margin-bottom:10px; }
.roster-head { display:flex; justify-content:space-between; padding:10px 12px; background:#171c22; border-bottom:1px solid var(--line); }
.roster-head strong { color:#fff; }
.slot { display:grid; grid-template-columns:50px 1fr auto; gap:8px; align-items:center; padding:9px 12px; border-bottom:1px solid #1d232a; }
.slot:last-child { border-bottom:0; }
.slot-name { color:#828d98; font-size:10px; font-weight:900; }
.slot-player { color:#fff; font-size:12px; font-weight:850; }
.slot-meta { color:#8f9aa5; font-size:10px; }

.profile-hero { border:1px solid var(--line); border-radius:16px; padding:18px; background:linear-gradient(145deg,#171c22,#101419); }
.profile-name { color:#fff; font-size:31px; font-weight:950; letter-spacing:-1px; }
.profile-meta { color:#aab3bd; font-size:13px; margin-top:4px; }
.profile-stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:15px; }
.profile-stat { border:1px solid var(--line); border-radius:10px; background:#101419; padding:10px; }
.profile-stat b { display:block; color:#fff; font-size:18px; }
.profile-stat small { color:#89949f; font-size:9px; font-weight:800; text-transform:uppercase; }

.ask-card { border:1px solid var(--line); border-radius:16px; background:linear-gradient(160deg,#151a20,#0d1014); padding:18px; }
.ask-title { font-size:26px; color:#fff; font-weight:950; letter-spacing:-.7px; }
.ask-sub { color:var(--muted); font-size:13px; margin:4px 0 12px; }
.answer { border-left:3px solid var(--red); background:#11161b; border-radius:0 10px 10px 0; padding:14px 16px; color:#e9edf1; line-height:1.55; }

.stButton > button { border-radius:9px !important; font-weight:850 !important; border:1px solid #2b323b !important; }
.stButton > button[kind="primary"] { background:var(--red) !important; border-color:var(--red) !important; color:#fff !important; }
.stTextInput input, .stSelectbox [data-baseweb="select"] > div { border-radius:9px !important; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:4px; background:#0d1014; border:1px solid var(--line); padding:4px; border-radius:12px; overflow-x:auto; }
[data-testid="stTabs"] button { border-radius:8px; font-weight:850; color:#9ba5af; white-space:nowrap; }
[data-testid="stTabs"] button[aria-selected="true"] { background:#20262d; color:#fff; }

@media (max-width: 820px) {
  .block-container { padding-left:.55rem; padding-right:.55rem; padding-top:.4rem; }
  .topbar { padding:10px 12px; }
  .brand-sub { display:none; }
  .hero { padding:15px 12px 7px; }
  .hero h1 { font-size:29px; }
  .kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); padding:8px 12px 14px; }
  .player-row { grid-template-columns:34px 1.5fr .48fr .48fr; min-height:55px; }
  .player-row .desktop-only { display:none; }
  .profile-stats { grid-template-columns:repeat(2,minmax(0,1fr)); }
  [data-testid="column"] { min-width:0 !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA
# -----------------------------------------------------------------------------
BASE_PLAYERS = [
    ("Bijan Robinson", "RB", "ATL", 1.4, 329.0, 5),
    ("Jahmyr Gibbs", "RB", "DET", 2.2, 321.5, 8),
    ("Ja'Marr Chase", "WR", "CIN", 2.7, 318.0, 10),
    ("Puka Nacua", "WR", "LAR", 4.5, 305.2, 8),
    ("Justin Jefferson", "WR", "MIN", 5.3, 300.4, 6),
    ("Saquon Barkley", "RB", "PHI", 6.1, 296.6, 9),
    ("CeeDee Lamb", "WR", "DAL", 7.0, 293.1, 10),
    ("De'Von Achane", "RB", "MIA", 8.6, 286.4, 12),
    ("Malik Nabers", "WR", "NYG", 9.3, 282.7, 14),
    ("Amon-Ra St. Brown", "WR", "DET", 10.2, 278.8, 8),
    ("Nico Collins", "WR", "HOU", 11.4, 274.3, 6),
    ("Ashton Jeanty", "RB", "LV", 12.5, 271.5, 8),
    ("Jonathan Taylor", "RB", "IND", 13.0, 269.0, 11),
    ("Brock Bowers", "TE", "LV", 15.6, 248.2, 8),
    ("Josh Allen", "QB", "BUF", 20.8, 372.0, 7),
    ("Lamar Jackson", "QB", "BAL", 22.1, 365.5, 7),
    ("Jalen Hurts", "QB", "PHI", 27.5, 352.1, 9),
    ("Trey McBride", "TE", "ARI", 29.4, 239.8, 8),
    ("Drake London", "WR", "ATL", 18.9, 255.0, 5),
    ("Brian Thomas Jr.", "WR", "JAX", 19.6, 251.6, 12),
    ("Chase Brown", "RB", "CIN", 23.7, 247.9, 10),
    ("Bucky Irving", "RB", "TB", 24.8, 244.8, 9),
    ("Omarion Hampton", "RB", "LAC", 26.4, 241.2, 12),
    ("Kenneth Walker III", "RB", "SEA", 31.6, 229.5, 8),
    ("Cam Skattebo", "RB", "NYG", 39.1, 215.1, 14),
    ("Patrick Mahomes", "QB", "KC", 45.0, 337.4, 10),
    ("Joe Burrow", "QB", "CIN", 47.0, 334.8, 10),
    ("Sam LaPorta", "TE", "DET", 51.0, 211.5, 8),
    ("George Kittle", "TE", "SF", 54.0, 205.4, 14),
    ("Christian Watson", "WR", "GB", 58.0, 204.2, 5),
    ("Jayden Daniels", "QB", "WAS", 62.0, 326.0, 12),
    ("James Cook", "RB", "BUF", 32.8, 225.7, 7),
    ("Kyren Williams", "RB", "LAR", 34.3, 223.0, 8),
    ("Garrett Wilson", "WR", "NYJ", 35.7, 221.9, 9),
    ("Tee Higgins", "WR", "CIN", 37.6, 219.4, 10),
    ("Ladd McConkey", "WR", "LAC", 40.0, 216.8, 12),
    ("Davante Adams", "WR", "LAR", 42.8, 211.3, 8),
    ("DJ Moore", "WR", "CHI", 49.0, 200.8, 5),
    ("Terry McLaurin", "WR", "WAS", 52.0, 198.7, 12),
    ("Alvin Kamara", "RB", "NO", 53.5, 196.9, 11),
]


def stable_id(name: str) -> str:
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:10]


@st.cache_data
def load_players() -> pd.DataFrame:
    """Load user-provided data when present, otherwise provide a deterministic starter pool."""
    csv_candidates = ["data/players.csv", "players.csv"]
    for path in csv_candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            required = {"name", "pos", "team", "adp"}
            if required.issubset(df.columns):
                if "id" not in df.columns:
                    df["id"] = df["name"].map(stable_id)
                if "projection" not in df.columns:
                    df["projection"] = np.nan
                if "bye" not in df.columns:
                    df["bye"] = np.nan
                return df

    rows = []
    for name, pos, team, adp, projection, bye in BASE_PLAYERS:
        rows.append({
            "id": stable_id(name), "name": name, "pos": pos, "team": team,
            "adp": float(adp), "projection": float(projection), "bye": bye,
        })

    # Expand to a full draftable pool while making generated rows explicit.
    positions = ["RB", "WR", "WR", "RB", "QB", "TE"]
    teams = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"]
    rng = random.Random(2026)
    start = len(rows) + 1
    for rank in range(start, 181):
        pos = positions[rank % len(positions)]
        team = teams[rank % len(teams)]
        name = f"Player Pool #{rank}"
        rows.append({
            "id": stable_id(name), "name": name, "pos": pos, "team": team,
            "adp": round(rank + rng.uniform(-2.4, 2.4), 1),
            "projection": round(max(80.0, 230 - rank * .72 + rng.uniform(-8, 8)), 1),
            "bye": 5 + (rank % 10),
        })
    return pd.DataFrame(rows).sort_values("adp").reset_index(drop=True)


players = load_players()


# -----------------------------------------------------------------------------
# STATE + DRAFT ENGINE
# -----------------------------------------------------------------------------
DEFAULT_TEAMS = 10
DEFAULT_ROUNDS = 15


def init_state() -> None:
    defaults = {
        "drafted": [],
        "queue": [],
        "draft_log": [],
        "selected_player": None,
        "draft_subview": "Players",
        "user_slot": 3,
        "team_count": DEFAULT_TEAMS,
        "rounds": DEFAULT_ROUNDS,
        "ask_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


init_state()


def pick_team(pick_no: int, team_count: int) -> int:
    round_no = (pick_no - 1) // team_count + 1
    index = (pick_no - 1) % team_count + 1
    return index if round_no % 2 == 1 else team_count - index + 1


def overall_pick_for_team(round_no: int, team_no: int, team_count: int) -> int:
    within = team_no if round_no % 2 == 1 else team_count - team_no + 1
    return (round_no - 1) * team_count + within


def drafted_ids() -> set[str]:
    return {x["id"] for x in st.session_state.draft_log}


def available_df() -> pd.DataFrame:
    return players[~players["id"].isin(drafted_ids())].copy().sort_values("adp")


def next_pick_number() -> int:
    return len(st.session_state.draft_log) + 1


def record_pick(player_id: str, team_no: int) -> None:
    if player_id in drafted_ids():
        return
    row = players.loc[players["id"] == player_id].iloc[0]
    pick_no = next_pick_number()
    st.session_state.draft_log.append({
        "pick": pick_no,
        "round": (pick_no - 1) // st.session_state.team_count + 1,
        "team": team_no,
        "id": row["id"],
        "name": row["name"],
        "pos": row["pos"],
        "nfl_team": row["team"],
        "adp": float(row["adp"]),
        "projection": float(row["projection"]) if pd.notna(row["projection"]) else np.nan,
    })
    if player_id in st.session_state.queue:
        st.session_state.queue.remove(player_id)


def cpu_pick() -> None:
    pool = available_df().head(20)
    if pool.empty:
        return
    pick_no = next_pick_number()
    team_no = pick_team(pick_no, st.session_state.team_count)
    # ADP-first but not robotic: small deterministic-ish jitter based on pick.
    rng = random.Random(9000 + pick_no)
    choice_index = min(len(pool) - 1, int(abs(rng.gauss(1.1, 1.3))))
    record_pick(pool.iloc[choice_index]["id"], team_no)


def sim_to_user_pick() -> None:
    total = st.session_state.team_count * st.session_state.rounds
    while next_pick_number() <= total and pick_team(next_pick_number(), st.session_state.team_count) != st.session_state.user_slot:
        cpu_pick()


def draft_user(player_id: str) -> None:
    total = st.session_state.team_count * st.session_state.rounds
    if next_pick_number() > total:
        return
    sim_to_user_pick()
    if pick_team(next_pick_number(), st.session_state.team_count) == st.session_state.user_slot:
        record_pick(player_id, st.session_state.user_slot)
        sim_to_user_pick()


def reset_draft() -> None:
    st.session_state.draft_log = []
    st.session_state.queue = []
    st.session_state.selected_player = None


def user_roster() -> pd.DataFrame:
    rows = [x for x in st.session_state.draft_log if x["team"] == st.session_state.user_slot]
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# HTML HELPERS
# -----------------------------------------------------------------------------
def pos_badge(pos: str) -> str:
    return f'<span class="pos pos-{pos}">{pos}</span>'


def app_header() -> None:
    pick_no = next_pick_number()
    total = st.session_state.team_count * st.session_state.rounds
    round_no = min(st.session_state.rounds, (max(1, pick_no) - 1) // st.session_state.team_count + 1)
    roster_n = len([x for x in st.session_state.draft_log if x["team"] == st.session_state.user_slot])
    st.markdown(
        f"""
        <div class="shiva-shell">
          <div class="topbar">
            <div class="brand"><div class="brand-mark">🏆</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div>
            <div class="live-pill"><span class="live-dot"></span> DRAFT ENGINE LIVE</div>
          </div>
          <div class="hero"><h1>Win the draft before it starts.</h1><p>Full-PPR draft room, board, queue, roster construction and player intelligence in one fast workspace.</p></div>
          <div class="kpi-grid">
            <div class="kpi"><div class="kpi-label">Current Pick</div><div class="kpi-value">{min(pick_no,total)} / {total}</div></div>
            <div class="kpi"><div class="kpi-label">Round</div><div class="kpi-value">{round_no}</div></div>
            <div class="kpi"><div class="kpi-label">Your Slot</div><div class="kpi-value">#{st.session_state.user_slot}</div></div>
            <div class="kpi"><div class="kpi-label">Roster</div><div class="kpi-value">{roster_n} / {st.session_state.rounds}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_profile(player_id: str) -> None:
    st.session_state.selected_player = player_id


def render_player_rows(df: pd.DataFrame, allow_draft: bool = False, queue_mode: bool = False, limit: int = 40) -> None:
    if df.empty:
        st.info("No players match this view.")
        return
    for rank, (_, row) in enumerate(df.head(limit).iterrows(), 1):
        c1, c2, c3 = st.columns([7.2, 1.15, 1.25], vertical_alignment="center")
        with c1:
            st.markdown(
                f"""
                <div class="player-row">
                  <div class="rank">{rank}</div>
                  <div><div class="player-name">{row['name']}</div><div class="player-meta">{pos_badge(str(row['pos']))}&nbsp;&nbsp; {row['team']}</div></div>
                  <div><div class="cell-label">ADP</div><div class="cell-value">{row['adp']:.1f}</div></div>
                  <div><div class="cell-label">Proj</div><div class="cell-value">{row['projection']:.0f}</div></div>
                  <div class="desktop-only"><div class="cell-label">Bye</div><div class="cell-value">{row['bye']}</div></div>
                  <div class="desktop-only"><div class="cell-label">Value</div><div class="cell-value">{row['projection'] / max(row['adp'],1):.1f}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Profile", key=f"profile_{queue_mode}_{row['id']}", use_container_width=True):
                open_profile(row["id"])
                st.session_state.draft_subview = "Profile"
                st.rerun()
        with c3:
            if allow_draft:
                if st.button("DRAFT", key=f"draft_{row['id']}", type="primary", use_container_width=True):
                    draft_user(row["id"])
                    st.rerun()
            elif queue_mode:
                if st.button("Remove", key=f"remove_{row['id']}", use_container_width=True):
                    st.session_state.queue.remove(row["id"])
                    st.rerun()
            else:
                label = "✓ Queue" if row["id"] in st.session_state.queue else "+ Queue"
                if st.button(label, key=f"queue_{row['id']}", use_container_width=True, disabled=row["id"] in st.session_state.queue):
                    st.session_state.queue.append(row["id"])
                    st.rerun()


def render_board() -> None:
    team_count = st.session_state.team_count
    rounds = st.session_state.rounds
    pick_map = {x["pick"]: x for x in st.session_state.draft_log}
    cols = " ".join(["minmax(80px, 1fr)" for _ in range(team_count)])
    html = [f'<div class="board-wrap"><div class="board" style="grid-template-columns:{cols}">']
    for round_no in range(1, rounds + 1):
        for display_team in range(1, team_count + 1):
            pick_no = overall_pick_for_team(round_no, display_team, team_count)
            pick = pick_map.get(pick_no)
            if pick:
                html.append(
                    f'<div class="pick {pick["pos"]}"><div class="pick-no">{pick_no} · TEAM {pick["team"]}</div><div class="pick-name">{pick["name"]}</div><div class="pick-meta">{pick["pos"]} · {pick["nfl_team"]}</div></div>'
                )
            else:
                html.append(f'<div class="pick empty"><div class="pick-no">{pick_no} · TEAM {pick_team(pick_no,team_count)}</div><div class="pick-name">On the clock</div><div class="pick-meta">Round {round_no}</div></div>')
    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


ROSTER_SLOTS = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "D/ST", "K", "BE", "BE", "BE", "BE", "BE", "BE"]


def assign_roster_slots(roster: pd.DataFrame) -> list[tuple[str, dict | None]]:
    if roster.empty:
        return [(slot, None) for slot in ROSTER_SLOTS]
    remaining = roster.to_dict("records")
    output = []
    for slot in ROSTER_SLOTS:
        match_idx = None
        for idx, p in enumerate(remaining):
            if slot == p["pos"] or (slot == "FLEX" and p["pos"] in {"RB", "WR", "TE"}):
                match_idx = idx
                break
        if match_idx is None and slot == "BE" and remaining:
            match_idx = 0
        output.append((slot, remaining.pop(match_idx) if match_idx is not None else None))
    return output


def render_roster() -> None:
    roster = user_roster()
    st.markdown('<div class="roster-card"><div class="roster-head"><strong>YOUR TEAM</strong><span>Projected lineup</span></div>', unsafe_allow_html=True)
    for slot, player in assign_roster_slots(roster):
        if player:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div><div class="slot-player">{player["name"]}</div><div class="slot-meta">{player["pos"]} · {player["nfl_team"]}</div></div><div class="slot-meta">Pick {player["pick"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div class="slot-player" style="color:#66707c">Empty</div><div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_profile(player_id: str | None) -> None:
    if not player_id:
        st.info("Select a player from the player list to open a profile.")
        return
    match = players[players["id"] == player_id]
    if match.empty:
        st.info("Player not found.")
        return
    p = match.iloc[0]
    value = p["projection"] / max(p["adp"], 1)
    st.markdown(
        f"""
        <div class="profile-hero">
          <div>{pos_badge(str(p['pos']))}</div>
          <div class="profile-name">{p['name']}</div>
          <div class="profile-meta">{p['team']} · Bye {p['bye']} · Full PPR</div>
          <div class="profile-stats">
            <div class="profile-stat"><b>{p['adp']:.1f}</b><small>Draft ADP</small></div>
            <div class="profile-stat"><b>{p['projection']:.1f}</b><small>Projection*</small></div>
            <div class="profile-stat"><b>{value:.1f}</b><small>Value Index</small></div>
            <div class="profile-stat"><b>{'Queued' if p['id'] in st.session_state.queue else 'Available'}</b><small>Draft Status</small></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("*Starter projections are demo values until you connect your preferred 2026 data source or upload data/players.csv.")

    seed = int(p["id"][:6], 16)
    rng = np.random.default_rng(seed)
    weeks = np.arange(1, 19)
    avg = max(6.0, min(26.0, float(p["projection"]) / 17.0))
    scores = np.maximum(0, rng.normal(avg, 4.3, len(weeks))).round(1)
    logs = pd.DataFrame({"Week": weeks, "Fantasy Points": scores})
    fig = px.line(logs, x="Week", y="Fantasy Points", markers=True, title="Sample weekly performance visualization")
    fig.update_layout(template="plotly_dark", height=330, margin=dict(l=10, r=10, t=45, b=10), paper_bgcolor="#0b0d10", plot_bgcolor="#0b0d10")
    st.plotly_chart(fig, use_container_width=True)


def ask_shiva(question: str) -> str:
    key = None
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    key = key or os.getenv("OPENAI_API_KEY")
    if not key or OpenAI is None:
        return (
            "Ask Shiva is wired for a real OpenAI connection, but this deployment does not have an OPENAI_API_KEY yet. "
            "Add the key in Streamlit Secrets and this box will answer using the live model instead of hard-coded fantasy logic."
        )

    client = OpenAI(api_key=key)
    roster = user_roster()
    roster_text = ", ".join(roster["name"].tolist()) if not roster.empty else "No players drafted yet"
    remaining = available_df().head(35)[["name", "pos", "team", "adp"]].to_dict("records")
    system = (
        "You are Shiva, an elite fantasy-football draft analyst. Default to ESPN full 1-point PPR. "
        "Be decisive, data-aware, concise, and explain the opportunity cost of the recommendation. "
        "Never invent current injuries, stats, ADP, news, or transactions. If live facts are required and not supplied, say so. "
        f"User draft slot: {st.session_state.user_slot}. User roster: {roster_text}. "
        f"Top available players from the app: {remaining}."
    )
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=[{"role": "system", "content": system}, {"role": "user", "content": question}],
        )
        return response.output_text
    except Exception as exc:
        return f"Ask Shiva could not complete this request: {exc}"


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
app_header()
st.write("")

nav_home, nav_draft, nav_rank, nav_ask = st.tabs(["🏠 Home", "🏈 Mock Draft", "📋 Rankings", "✨ Ask Shiva"])

with nav_home:
    st.markdown('<div class="section-title"><div><h2>Draft Command Center</h2><span>Everything important, without dashboard clutter.</span></div></div>', unsafe_allow_html=True)
    a, b = st.columns([1.45, 1])
    with a:
        st.markdown("#### Top Available")
        render_player_rows(available_df(), limit=8)
    with b:
        st.markdown("#### Your Roster")
        render_roster()

with nav_draft:
    settings, controls = st.columns([2.2, 1])
    with settings:
        st.markdown('<div class="section-title"><div><h2>Live Mock Draft</h2><span>Snake draft · smooth persistent state · full PPR</span></div></div>', unsafe_allow_html=True)
    with controls:
        cc1, cc2 = st.columns(2)
        with cc1:
            slot = st.selectbox("Draft slot", list(range(1, st.session_state.team_count + 1)), index=st.session_state.user_slot - 1, key="slot_widget")
            if slot != st.session_state.user_slot and not st.session_state.draft_log:
                st.session_state.user_slot = slot
        with cc2:
            if st.button("Reset draft", use_container_width=True):
                reset_draft()
                st.rerun()

    if not st.session_state.draft_log:
        sim_to_user_pick()

    sub_players, sub_board, sub_queue, sub_roster = st.tabs(["Players", "Draft Board", "Queue", "Roster"])
    with sub_players:
        f1, f2 = st.columns([2, 1])
        with f1:
            search = st.text_input("Search", placeholder="Search player or team…", key="draft_search")
        with f2:
            pos = st.selectbox("Position", ["ALL", "QB", "RB", "WR", "TE", "DST"], key="draft_pos")
        pool = available_df()
        if search:
            q = search.strip().lower()
            pool = pool[pool["name"].str.lower().str.contains(q) | pool["team"].str.lower().str.contains(q)]
        if pos != "ALL":
            pool = pool[pool["pos"] == pos]

        on_clock = pick_team(next_pick_number(), st.session_state.team_count) == st.session_state.user_slot
        if on_clock:
            st.success(f"You are on the clock at pick {next_pick_number()}.")
        render_player_rows(pool, allow_draft=on_clock, limit=45)

    with sub_board:
        render_board()

    with sub_queue:
        qdf = players[players["id"].isin(st.session_state.queue) & ~players["id"].isin(drafted_ids())].copy()
        order = {pid: i for i, pid in enumerate(st.session_state.queue)}
        if not qdf.empty:
            qdf["qorder"] = qdf["id"].map(order)
            qdf = qdf.sort_values("qorder")
        render_player_rows(qdf, queue_mode=True, limit=60)

    with sub_roster:
        r1, r2 = st.columns([1, 1.25])
        with r1:
            render_roster()
        with r2:
            roster = user_roster()
            if not roster.empty:
                fig = px.bar(roster, x="name", y="projection", color="pos", title="Roster projection mix")
                fig.update_layout(template="plotly_dark", height=390, margin=dict(l=10, r=10, t=45, b=10), paper_bgcolor="#0b0d10", plot_bgcolor="#0b0d10", xaxis_title="", yaxis_title="Projection")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Your roster will populate as you draft.")

    if st.session_state.selected_player:
        st.divider()
        st.markdown("### Player Profile")
        render_profile(st.session_state.selected_player)

with nav_rank:
    st.markdown('<div class="section-title"><div><h2>2026 Draft Rankings</h2><span>Starter board — replace with your preferred live data source.</span></div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        rq = st.text_input("Search rankings", placeholder="Player or team…")
    with c2:
        rp = st.selectbox("Filter position", ["ALL", "QB", "RB", "WR", "TE", "DST"])
    rdf = players.copy()
    if rq:
        q = rq.lower().strip()
        rdf = rdf[rdf["name"].str.lower().str.contains(q) | rdf["team"].str.lower().str.contains(q)]
    if rp != "ALL":
        rdf = rdf[rdf["pos"] == rp]
    render_player_rows(rdf, limit=60)

with nav_ask:
    st.markdown('<div class="ask-card"><div class="ask-title">Ask Shiva</div><div class="ask-sub">Draft strategy, player decisions, roster construction and scenario analysis.</div></div>', unsafe_allow_html=True)
    question = st.text_area("What do you want to know?", placeholder="I’m drafting 3rd in a 10-team full PPR league. Bijan is gone. Who should I take and why?", height=115)
    if st.button("Ask Shiva", type="primary", use_container_width=True):
        if question.strip():
            with st.spinner("Analyzing your draft context…"):
                answer = ask_shiva(question.strip())
            st.session_state.ask_history.insert(0, (question.strip(), answer))
    for q, a in st.session_state.ask_history[:5]:
        st.markdown(f"**{q}**")
        st.markdown(f'<div class="answer">{a}</div>', unsafe_allow_html=True)
        st.write("")

st.caption("Shiva Fantasy Football · Built as an original product experience inspired by the usability patterns of leading fantasy platforms. Demo projections are clearly labeled and should be replaced by a trusted live data feed before production decisions.")
