from __future__ import annotations

import hashlib
import os
import random
import re
from typing import Any

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

RANKINGS_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/current_rankings.csv"
WEEKLY_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/player_weekly_master_2014_2025.csv.gz"
BIRTHS_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/player_birth_dates.csv"
DATA_SEASONS = tuple(range(2014, 2026))


# -----------------------------------------------------------------------------
# DESIGN SYSTEM — MOBILE FIRST
# -----------------------------------------------------------------------------
CSS = r"""
<style>
:root {
  --bg:#080b0f; --panel:#10151b; --panel2:#151b22; --line:#242c35;
  --text:#f7f9fb; --muted:#8f9ba7; --red:#e31837; --green:#21c16b;
  --qb:#7657d7; --rb:#22a99f; --wr:#3989ee; --te:#ed893d; --dst:#d7bb3f; --k:#727d89;
}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1480px;padding-top:.55rem;padding-bottom:5rem}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden}

.shiva-shell{border:1px solid var(--line);background:linear-gradient(180deg,#11161c,#0c1015);border-radius:16px;overflow:hidden}
.topbar{min-height:62px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 16px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px}.brand-mark{width:40px;height:40px;border-radius:11px;background:linear-gradient(135deg,#f52d49,#9d071c);display:flex;align-items:center;justify-content:center;font-size:21px}
.brand-title{font-size:19px;font-weight:950;letter-spacing:-.4px}.brand-sub{color:var(--muted);font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px}
.live-pill{display:inline-flex;align-items:center;gap:7px;color:#dbe1e7;font-size:10px;font-weight:900;border:1px solid var(--line);background:#151b21;padding:7px 9px;border-radius:999px}
.live-dot{width:7px;height:7px;border-radius:99px;background:var(--green);box-shadow:0 0 0 4px rgba(33,193,107,.11)}
.hero{padding:16px 18px 8px}.hero h1{margin:0;color:#fff;font-size:clamp(27px,4vw,43px);line-height:1;letter-spacing:-1.3px}.hero p{margin:8px 0 0;color:var(--muted);font-size:12px}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;padding:9px 18px 17px}.kpi{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:10px 12px}.kpi-label{color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.8px;font-weight:850}.kpi-value{color:#fff;font-size:18px;font-weight:950;margin-top:2px}

.section-title{display:flex;justify-content:space-between;align-items:end;gap:10px;margin:6px 0 10px}.section-title h2{margin:0;color:#fff;font-size:21px;letter-spacing:-.5px}.section-title span{color:var(--muted);font-size:11px}
.data-chip{display:inline-flex;align-items:center;gap:5px;border:1px solid #1e5439;background:#0d2118;color:#7ce6aa;padding:5px 8px;border-radius:999px;font-size:9px;font-weight:900}

.player-row{display:grid;grid-template-columns:36px 1.65fr .52fr .52fr .52fr;align-items:center;gap:7px;min-height:56px;padding:7px 9px;margin-bottom:5px;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
.rank{width:29px;height:29px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:#1d242c;color:#dbe0e5;font-weight:950;font-size:11px}
.player-name{color:#fff;font-weight:920;font-size:13px;line-height:1.12}.player-meta{color:var(--muted);font-size:10px;margin-top:3px}.cell-label{color:var(--muted);font-size:8px;text-transform:uppercase;font-weight:850;letter-spacing:.5px}.cell-value{color:#fff;font-size:12px;font-weight:900}
.pos{display:inline-flex;align-items:center;justify-content:center;min-width:29px;border-radius:5px;padding:3px 5px;font-weight:950;font-size:9px;color:#fff}.pos-QB{background:var(--qb)}.pos-RB{background:var(--rb)}.pos-WR{background:var(--wr)}.pos-TE{background:var(--te)}.pos-DST,.pos-D\/ST{background:var(--dst);color:#151515}.pos-K{background:var(--k)}

.board-wrap{border:1px solid var(--line);border-radius:13px;background:#0c1014;padding:8px}.board{display:grid;grid-template-columns:repeat(10,minmax(78px,1fr));gap:5px}.pick{min-height:64px;border-radius:8px;padding:7px;border:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;justify-content:space-between}.pick.empty{background:#141a20;color:#68737e}.pick.QB{background:rgba(118,87,215,.23)}.pick.RB{background:rgba(34,169,159,.22)}.pick.WR{background:rgba(57,137,238,.22)}.pick.TE{background:rgba(237,137,61,.22)}.pick.DST,.pick.D\/ST{background:rgba(215,187,63,.24)}.pick.K{background:rgba(114,125,137,.23)}.pick-no{color:#9ca7b1;font-size:8px;font-weight:850}.pick-name{color:#fff;font-size:10px;line-height:1.05;font-weight:950}.pick-meta{color:#adb6bf;font-size:8px;font-weight:750}

.roster-card{border:1px solid var(--line);border-radius:11px;background:var(--panel);overflow:hidden;margin-bottom:9px}.roster-head{display:flex;justify-content:space-between;padding:9px 11px;background:#161c23;border-bottom:1px solid var(--line)}.roster-head strong{color:#fff}.slot{display:grid;grid-template-columns:44px 1fr auto;gap:7px;align-items:center;padding:8px 11px;border-bottom:1px solid #1c232b}.slot:last-child{border-bottom:0}.slot-name{color:#7f8b96;font-size:9px;font-weight:950}.slot-player{color:#fff;font-size:11px;font-weight:880}.slot-meta{color:#8f9aa5;font-size:9px}

.profile-hero{border:1px solid var(--line);border-radius:15px;padding:15px;background:linear-gradient(145deg,#171e26,#0f141a)}.profile-name-big{color:#fff;font-size:30px;font-weight:980;letter-spacing:-1px}.profile-meta{color:#aab4be;font-size:12px;margin-top:3px}.profile-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:13px}.profile-stat{border:1px solid var(--line);border-radius:9px;background:#0d1217;padding:9px}.profile-stat b{display:block;color:#fff;font-size:17px}.profile-stat small{color:#87939e;font-size:8px;font-weight:850;text-transform:uppercase}.profile-season-card{border:1px solid var(--line);background:#10161c;border-radius:10px;padding:10px;margin-bottom:8px}.profile-season-card strong{font-size:15px;color:#fff}.profile-season-card span{color:#98a4af;font-size:10px}

.ask-card{border:1px solid var(--line);border-radius:15px;background:linear-gradient(160deg,#151b21,#0c1014);padding:16px}.ask-title{font-size:25px;color:#fff;font-weight:980;letter-spacing:-.7px}.ask-sub{color:var(--muted);font-size:12px;margin:4px 0 11px}.answer{border-left:3px solid var(--red);background:#10161b;border-radius:0 9px 9px 0;padding:12px 14px;color:#e9edf1;line-height:1.52}

.stButton>button{border-radius:8px!important;font-weight:880!important;border:1px solid #2b343e!important;min-height:38px}.stButton>button[kind="primary"]{background:var(--red)!important;border-color:var(--red)!important;color:#fff!important}.stTextInput input,.stSelectbox [data-baseweb="select"]>div{border-radius:8px!important}
div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:5px!important;width:100%!important}div[role="radiogroup"] label{background:#11171d;border:1px solid var(--line);border-radius:8px;padding:6px 7px!important;margin:0!important;justify-content:center!important;min-height:38px}div[role="radiogroup"] label:has(input:checked){background:#222a33;border-color:#485561}div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;font-weight:900!important;white-space:nowrap!important}

@media(max-width:820px){
 .block-container{padding-left:.5rem;padding-right:.5rem;padding-top:.3rem}.topbar{padding:9px 11px}.brand-sub{display:none}.hero{padding:13px 11px 6px}.hero h1{font-size:27px}.hero p{font-size:11px}.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));padding:7px 11px 13px}.kpi{padding:8px 10px}.kpi-value{font-size:16px}
 div[role="radiogroup"]{grid-template-columns:repeat(2,minmax(0,1fr))!important}.player-row{grid-template-columns:31px 1.65fr .5fr .5fr;min-height:52px;padding:6px}.player-row .desktop-only{display:none}.profile-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.profile-name-big{font-size:25px}.board{grid-template-columns:1fr!important}.pick{min-height:55px}.board-wrap{padding:6px}.section-title span{display:none}[data-testid="column"]{min-width:0!important}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA SOURCES
# -----------------------------------------------------------------------------
def stable_id(name: str) -> str:
    return hashlib.md5(str(name).encode("utf-8")).hexdigest()[:12]


def name_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def safe_num(value: Any, default: float = np.nan) -> float:
    out = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return float(out) if pd.notna(out) else default


@st.cache_data(ttl=900, show_spinner=False)
def load_rankings() -> tuple[pd.DataFrame, str]:
    try:
        raw = pd.read_csv(RANKINGS_URL)
        rename = {
            "player_name": "name",
            "position": "pos",
            "consensus_adp": "consensus_adp",
            "overall_rank": "overall_rank",
            "position_rank": "position_rank",
        }
        df = raw.rename(columns=rename).copy()
        required = {"name", "pos", "team"}
        if not required.issubset(df.columns):
            raise ValueError("Ranking feed is missing required player fields")
        df["name"] = df["name"].astype(str).str.strip()
        df["pos"] = df["pos"].astype(str).str.upper().replace({"DEF": "DST", "D/ST": "DST"})
        df["team"] = df["team"].fillna("FA").astype(str).str.upper()
        for col in ("adp", "consensus_adp", "overall_rank", "position_rank", "bye"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = np.nan
        df["draft_adp"] = df["consensus_adp"].fillna(df["adp"]).fillna(df["overall_rank"])
        df["overall_rank"] = df["overall_rank"].fillna(df["draft_adp"])
        df["id"] = df["name"].map(stable_id)
        df = df.drop_duplicates("id").sort_values(["overall_rank", "draft_adp", "name"], na_position="last").reset_index(drop=True)
        return df, "Draft-Coach current_rankings.csv"
    except Exception as exc:
        # An explicit emergency fallback keeps the app online but never masquerades as live data.
        emergency = pd.DataFrame([
            {"name":"Jahmyr Gibbs","pos":"RB","team":"DET","draft_adp":1.0,"overall_rank":1,"position_rank":1,"bye":6},
            {"name":"Bijan Robinson","pos":"RB","team":"ATL","draft_adp":2.0,"overall_rank":2,"position_rank":2,"bye":11},
            {"name":"Ja'Marr Chase","pos":"WR","team":"CIN","draft_adp":3.2,"overall_rank":3,"position_rank":1,"bye":6},
            {"name":"Puka Nacua","pos":"WR","team":"LAR","draft_adp":3.8,"overall_rank":4,"position_rank":2,"bye":11},
        ])
        emergency["id"] = emergency["name"].map(stable_id)
        return emergency, f"EMERGENCY FALLBACK — live rankings unavailable: {exc}"


@st.cache_data(ttl=3600, show_spinner=False)
def load_weekly() -> pd.DataFrame:
    df = pd.read_csv(WEEKLY_URL, compression="gzip", low_memory=False)
    for c in (
        "season", "week", "fantasy_points_ppr", "fantasy_points", "passing_yards", "passing_tds",
        "interceptions", "rushing_yards", "rushing_tds", "carries", "targets", "receptions",
        "receiving_yards", "receiving_tds", "fumbles_lost", "passing_two_point_conversions",
        "rushing_two_point_conversions", "receiving_two_point_conversions",
    ):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "season_type" in df.columns:
        reg = df["season_type"].astype(str).str.upper().isin(["REG", "REGULAR", "REGULAR SEASON"])
        if reg.any():
            df = df.loc[reg].copy()
    if "week" in df.columns:
        df = df.loc[df["week"].between(1, 18, inclusive="both") | df["week"].isna()].copy()
    return df


@st.cache_data(ttl=86400, show_spinner=False)
def load_births() -> pd.DataFrame:
    try:
        return pd.read_csv(BIRTHS_URL, low_memory=False)
    except Exception:
        return pd.DataFrame()


def weekly_name_col(df: pd.DataFrame) -> str | None:
    for col in ("player_display_name", "player_name", "name"):
        if col in df.columns:
            return col
    return None


def weekly_for_player(weekly: pd.DataFrame, player_name: str) -> pd.DataFrame:
    if weekly.empty:
        return pd.DataFrame()
    ncol = weekly_name_col(weekly)
    if not ncol:
        return pd.DataFrame()
    target = name_key(player_name)
    mask = weekly[ncol].astype(str).map(name_key).eq(target)
    out = weekly.loc[mask].copy()
    if out.empty:
        # Conservative last-name fallback only when the exact normalized name misses.
        last = re.sub(r"[^a-z0-9]+", "", str(player_name).casefold().split()[-1])
        if len(last) >= 5:
            candidates = weekly[ncol].astype(str).map(name_key)
            mask = candidates.str.endswith(last)
            names = weekly.loc[mask, ncol].dropna().astype(str).unique().tolist()
            if len(names) == 1:
                out = weekly.loc[mask].copy()
    return out.sort_values([c for c in ("season", "week") if c in out.columns]) if not out.empty else out


def espn_ppr_points(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=float)
    scoring = {
        "passing_yards": 0.04,
        "passing_tds": 4.0,
        "interceptions": -2.0,
        "rushing_yards": 0.10,
        "rushing_tds": 6.0,
        "receptions": 1.0,
        "receiving_yards": 0.10,
        "receiving_tds": 6.0,
        "fumbles_lost": -2.0,
        "passing_two_point_conversions": 2.0,
        "rushing_two_point_conversions": 2.0,
        "receiving_two_point_conversions": 2.0,
    }
    available = [c for c in scoring if c in frame.columns]
    if available:
        total = pd.Series(0.0, index=frame.index)
        for col in available:
            total = total + pd.to_numeric(frame[col], errors="coerce").fillna(0) * scoring[col]
        return total.round(2)
    if "fantasy_points_ppr" in frame.columns:
        return pd.to_numeric(frame["fantasy_points_ppr"], errors="coerce")
    if "fantasy_points" in frame.columns:
        return pd.to_numeric(frame["fantasy_points"], errors="coerce")
    return pd.Series(np.nan, index=frame.index)


players, rankings_source = load_rankings()


# -----------------------------------------------------------------------------
# STATE + DRAFT ENGINE
# -----------------------------------------------------------------------------
DEFAULT_TEAMS = 10
DEFAULT_ROUNDS = 15
ROSTER_SLOTS = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K", "BE", "BE", "BE", "BE", "BE", "BE"]


def init_state() -> None:
    defaults = {
        "draft_log": [], "queue": [], "selected_player": None, "profile_return": "Home",
        "user_slot": 3, "team_count": DEFAULT_TEAMS, "rounds": DEFAULT_ROUNDS,
        "ask_history": [], "main_page": "Home", "draft_view": "Players",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


init_state()


def pick_team(pick_no: int, team_count: int) -> int:
    round_no = (pick_no - 1) // team_count + 1
    index = (pick_no - 1) % team_count + 1
    return index if round_no % 2 else team_count - index + 1


def overall_pick_for_team(round_no: int, team_no: int, team_count: int) -> int:
    within = team_no if round_no % 2 else team_count - team_no + 1
    return (round_no - 1) * team_count + within


def drafted_ids() -> set[str]:
    return {x["id"] for x in st.session_state.draft_log}


def available_df() -> pd.DataFrame:
    return players.loc[~players["id"].isin(drafted_ids())].copy().sort_values(["draft_adp", "overall_rank"], na_position="last")


def next_pick_number() -> int:
    return len(st.session_state.draft_log) + 1


def record_pick(player_id: str, team_no: int) -> None:
    if player_id in drafted_ids():
        return
    match = players.loc[players["id"].eq(player_id)]
    if match.empty:
        return
    row = match.iloc[0]
    pick_no = next_pick_number()
    st.session_state.draft_log.append({
        "pick": pick_no,
        "round": (pick_no - 1) // st.session_state.team_count + 1,
        "team": team_no,
        "id": row["id"], "name": row["name"], "pos": row["pos"], "nfl_team": row["team"],
        "adp": safe_num(row["draft_adp"]), "overall_rank": safe_num(row["overall_rank"]),
    })
    if player_id in st.session_state.queue:
        st.session_state.queue.remove(player_id)


def cpu_pick() -> None:
    pool = available_df().head(24)
    if pool.empty:
        return
    pick_no = next_pick_number()
    team_no = pick_team(pick_no, st.session_state.team_count)
    rng = random.Random(26000 + pick_no)
    # Consensus-driven but allows believable small reaches rather than a robotic ADP copy.
    choice_index = min(len(pool) - 1, max(0, int(abs(rng.gauss(1.4, 1.7)))))
    record_pick(str(pool.iloc[choice_index]["id"]), team_no)


def sim_to_user_pick() -> None:
    total = st.session_state.team_count * st.session_state.rounds
    guard = 0
    while next_pick_number() <= total and pick_team(next_pick_number(), st.session_state.team_count) != st.session_state.user_slot:
        cpu_pick(); guard += 1
        if guard > total:
            break


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
    return pd.DataFrame([x for x in st.session_state.draft_log if x["team"] == st.session_state.user_slot])


# -----------------------------------------------------------------------------
# UI HELPERS
# -----------------------------------------------------------------------------
def fmt_num(v: Any, decimals: int = 1, fallback: str = "—") -> str:
    n = safe_num(v)
    return f"{n:.{decimals}f}" if pd.notna(n) else fallback


def fmt_int(v: Any, fallback: str = "—") -> str:
    n = safe_num(v)
    return str(int(round(n))) if pd.notna(n) else fallback


def pos_badge(pos: str) -> str:
    p = str(pos).upper().replace("D/ST", "DST")
    return f'<span class="pos pos-{p}">{p}</span>'


def app_header() -> None:
    pick_no = next_pick_number(); total = st.session_state.team_count * st.session_state.rounds
    round_no = min(st.session_state.rounds, (max(1, pick_no) - 1) // st.session_state.team_count + 1)
    roster_n = len([x for x in st.session_state.draft_log if x["team"] == st.session_state.user_slot])
    live_ok = not rankings_source.startswith("EMERGENCY")
    st.markdown(f"""
    <div class="shiva-shell">
      <div class="topbar">
        <div class="brand"><div class="brand-mark">🏆</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div>
        <div class="live-pill"><span class="live-dot"></span>{'REAL DATA CONNECTED' if live_ok else 'DATA FALLBACK'}</div>
      </div>
      <div class="hero"><h1>Win the draft before it starts.</h1><p>2026 rankings + real 2014–2025 ESPN full-PPR weekly history + live draft context.</p></div>
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">Current Pick</div><div class="kpi-value">{min(pick_no,total)} / {total}</div></div>
        <div class="kpi"><div class="kpi-label">Round</div><div class="kpi-value">{round_no}</div></div>
        <div class="kpi"><div class="kpi-label">Your Slot</div><div class="kpi-value">#{st.session_state.user_slot}</div></div>
        <div class="kpi"><div class="kpi-label">Roster</div><div class="kpi-value">{roster_n} / {st.session_state.rounds}</div></div>
      </div>
    </div>""", unsafe_allow_html=True)


def open_profile(player_id: str, return_page: str) -> None:
    st.session_state.selected_player = player_id
    st.session_state.profile_return = return_page
    st.rerun()


def render_player_rows(df: pd.DataFrame, *, allow_draft: bool = False, queue_mode: bool = False, limit: int = 50, return_page: str = "Home") -> None:
    if df.empty:
        st.info("No players match this view.")
        return
    for _, row in df.head(limit).iterrows():
        c1, c2, c3 = st.columns([7.2, 1.15, 1.25], vertical_alignment="center")
        with c1:
            st.markdown(f"""
            <div class="player-row">
              <div class="rank">{fmt_int(row.get('overall_rank'))}</div>
              <div><div class="player-name">{row['name']}</div><div class="player-meta">{pos_badge(row['pos'])}&nbsp;&nbsp;{row['team']}</div></div>
              <div><div class="cell-label">ADP</div><div class="cell-value">{fmt_num(row.get('draft_adp'))}</div></div>
              <div><div class="cell-label">Pos Rk</div><div class="cell-value">{str(row['pos'])}{fmt_int(row.get('position_rank'))}</div></div>
              <div class="desktop-only"><div class="cell-label">Bye</div><div class="cell-value">{fmt_int(row.get('bye'))}</div></div>
            </div>""", unsafe_allow_html=True)
        with c2:
            if st.button("Profile", key=f"profile_{return_page}_{queue_mode}_{row['id']}", use_container_width=True):
                open_profile(str(row["id"]), return_page)
        with c3:
            pid = str(row["id"])
            if allow_draft:
                if st.button("DRAFT", key=f"draft_{pid}", type="primary", use_container_width=True):
                    draft_user(pid); st.rerun()
            elif queue_mode:
                if st.button("Remove", key=f"remove_{pid}", use_container_width=True):
                    if pid in st.session_state.queue: st.session_state.queue.remove(pid)
                    st.rerun()
            else:
                queued = pid in st.session_state.queue
                if st.button("✓ Queue" if queued else "+ Queue", key=f"queue_{return_page}_{pid}", use_container_width=True, disabled=queued):
                    st.session_state.queue.append(pid); st.rerun()


def render_board() -> None:
    team_count = st.session_state.team_count; rounds = st.session_state.rounds
    pick_map = {x["pick"]: x for x in st.session_state.draft_log}
    html = ['<div class="board-wrap"><div class="board">']
    for round_no in range(1, rounds + 1):
        for display_team in range(1, team_count + 1):
            pick_no = overall_pick_for_team(round_no, display_team, team_count)
            pick = pick_map.get(pick_no)
            if pick:
                ppos = str(pick["pos"]).replace("D/ST", "DST")
                html.append(f'<div class="pick {ppos}"><div class="pick-no">{pick_no} · TEAM {pick["team"]}</div><div class="pick-name">{pick["name"]}</div><div class="pick-meta">{ppos} · {pick["nfl_team"]}</div></div>')
            else:
                html.append(f'<div class="pick empty"><div class="pick-no">{pick_no} · TEAM {pick_team(pick_no,team_count)}</div><div class="pick-name">Available</div><div class="pick-meta">Round {round_no}</div></div>')
    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def assign_roster_slots(roster: pd.DataFrame) -> list[tuple[str, dict | None]]:
    if roster.empty:
        return [(slot, None) for slot in ROSTER_SLOTS]
    remaining = roster.to_dict("records"); output = []
    for slot in ROSTER_SLOTS:
        idx = None
        for i, p in enumerate(remaining):
            pos = str(p["pos"]).replace("D/ST", "DST")
            if slot == pos or (slot == "FLEX" and pos in {"RB", "WR", "TE"}):
                idx = i; break
        if idx is None and slot == "BE" and remaining:
            idx = 0
        output.append((slot, remaining.pop(idx) if idx is not None else None))
    return output


def render_roster() -> None:
    roster = user_roster()
    st.markdown('<div class="roster-card"><div class="roster-head"><strong>YOUR TEAM</strong><span>Live draft roster</span></div>', unsafe_allow_html=True)
    for slot, player in assign_roster_slots(roster):
        if player:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div><div class="slot-player">{player["name"]}</div><div class="slot-meta">{player["pos"]} · {player["nfl_team"]}</div></div><div class="slot-meta">Pick {player["pick"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div class="slot-player" style="color:#66707c">Empty</div><div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# REAL PLAYER PROFILE ENGINE
# -----------------------------------------------------------------------------
def season_summary(frame: pd.DataFrame) -> dict[str, Any]:
    pts = espn_ppr_points(frame).dropna()
    return {
        "games": int(len(pts)),
        "total": float(pts.sum()) if len(pts) else np.nan,
        "ppg": float(pts.mean()) if len(pts) else np.nan,
        "median": float(pts.median()) if len(pts) else np.nan,
        "weeks15": int((pts >= 15).sum()) if len(pts) else 0,
        "weeks20": int((pts >= 20).sum()) if len(pts) else 0,
    }


def player_birth_age(player_name: str, season: int) -> str:
    births = load_births()
    if births.empty:
        return "—"
    ncol = weekly_name_col(births)
    if "name_key" in births.columns:
        mask = births["name_key"].astype(str).map(name_key).eq(name_key(player_name))
    elif ncol:
        mask = births[ncol].astype(str).map(name_key).eq(name_key(player_name))
    else:
        return "—"
    row = births.loc[mask]
    if row.empty or "birth_date" not in row.columns:
        return "—"
    dob = pd.to_datetime(row.iloc[0]["birth_date"], errors="coerce")
    if pd.isna(dob):
        return "—"
    age = int((pd.Timestamp(year=int(season), month=9, day=1) - dob).days / 365.2425)
    return str(age)


def weekly_table(frame: pd.DataFrame, pos: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    out = pd.DataFrame(index=frame.index)
    out["WK"] = pd.to_numeric(frame.get("week"), errors="coerce").astype("Int64") if "week" in frame.columns else range(1, len(frame)+1)
    for src in ("opponent_team", "opponent", "opp"):
        if src in frame.columns:
            out["OPP"] = frame[src].fillna("—").astype(str); break
    out["PPR"] = espn_ppr_points(frame).round(1)
    p = str(pos).upper()
    if p == "QB":
        cols = [("PASS YDS","passing_yards"),("PASS TD","passing_tds"),("INT","interceptions"),("RUSH YDS","rushing_yards"),("RUSH TD","rushing_tds")]
    elif p in {"WR","TE"}:
        cols = [("TGT","targets"),("REC","receptions"),("REC YDS","receiving_yards"),("REC TD","receiving_tds"),("RUSH YDS","rushing_yards")]
    else:
        cols = [("CAR","carries"),("RUSH YDS","rushing_yards"),("RUSH TD","rushing_tds"),("REC","receptions"),("REC YDS","receiving_yards"),("REC TD","receiving_tds")]
    for label, src in cols:
        if src in frame.columns:
            out[label] = pd.to_numeric(frame[src], errors="coerce").fillna(0).round(0).astype(int)
    return out.sort_values("WK").reset_index(drop=True)


def render_profile(player_id: str) -> None:
    match = players.loc[players["id"].eq(player_id)]
    if match.empty:
        st.error("Player not found in the current ranking feed."); return
    p = match.iloc[0]
    if st.button("← Back", key="profile_back"):
        st.session_state.selected_player = None; st.rerun()

    with st.spinner("Loading verified weekly player history…"):
        try:
            weekly = load_weekly()
            pf = weekly_for_player(weekly, str(p["name"]))
        except Exception as exc:
            st.error(f"Weekly data could not be loaded: {exc}")
            pf = pd.DataFrame()

    seasons = sorted(pd.to_numeric(pf.get("season", pd.Series(dtype=float)), errors="coerce").dropna().astype(int).unique().tolist(), reverse=True)
    latest = seasons[0] if seasons else 2025
    season_default = latest

    st.markdown(f"""
    <div class="profile-hero">
      <div>{pos_badge(p['pos'])}</div>
      <div class="profile-name-big">{p['name']}</div>
      <div class="profile-meta">{p['team']} · 2026 ADP {fmt_num(p.get('draft_adp'))} · Overall #{fmt_int(p.get('overall_rank'))} · Bye {fmt_int(p.get('bye'))}</div>
      <div class="profile-stats">
        <div class="profile-stat"><b>{fmt_num(p.get('draft_adp'))}</b><small>2026 Consensus ADP</small></div>
        <div class="profile-stat"><b>{p['pos']}{fmt_int(p.get('position_rank'))}</b><small>Position Rank</small></div>
        <div class="profile-stat"><b>{len(seasons)}</b><small>Seasons On File</small></div>
        <div class="profile-stat"><b>{'Queued' if p['id'] in st.session_state.queue else ('Drafted' if p['id'] in drafted_ids() else 'Available')}</b><small>Draft Status</small></div>
      </div>
    </div>""", unsafe_allow_html=True)

    if pf.empty:
        st.warning("No historical weekly record matched this player in the 2014–2025 master file. This can be normal for 2026 rookies or players without NFL regular-season data yet.")
        return

    season = st.selectbox("Season", seasons, index=seasons.index(season_default), key=f"season_{player_id}")
    view = st.radio("Profile view", ["Overview", "Weekly Stats"], horizontal=True, label_visibility="collapsed", key=f"profile_view_{player_id}")
    sf = pf.loc[pd.to_numeric(pf["season"], errors="coerce").eq(int(season))].copy()
    summary = season_summary(sf)

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("PPR PPG", fmt_num(summary["ppg"]))
    m2.metric("PPR Total", fmt_num(summary["total"]))
    m3.metric("Games", summary["games"])
    m4.metric("15+ Weeks", summary["weeks15"])
    m5.metric("20+ Weeks", summary["weeks20"])
    st.caption(f"ESPN full 1-point PPR · Age entering {season}: {player_birth_age(str(p['name']), int(season))} · Regular season only")

    if view == "Weekly Stats":
        table = weekly_table(sf, str(p["pos"]))
        chart = table[["WK","PPR"]].dropna() if {"WK","PPR"}.issubset(table.columns) else pd.DataFrame()
        if not chart.empty:
            fig = px.line(chart, x="WK", y="PPR", markers=True, title=f"{p['name']} — {season} weekly ESPN PPR")
            fig.update_layout(template="plotly_dark", height=315, margin=dict(l=8,r=8,t=42,b=8), paper_bgcolor="#080b0f", plot_bgcolor="#080b0f", xaxis=dict(dtick=1), yaxis_title="PPR Points")
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(table, use_container_width=True, hide_index=True, height=min(620, 38 + 35 * len(table)))
    else:
        career_rows = []
        for yr in seasons:
            yf = pf.loc[pd.to_numeric(pf["season"], errors="coerce").eq(int(yr))]
            s = season_summary(yf)
            career_rows.append({"Season":yr,"Games":s["games"],"PPR Total":round(s["total"],1),"PPR PPG":round(s["ppg"],1),"15+":s["weeks15"],"20+":s["weeks20"]})
        st.markdown("#### Career fantasy history")
        st.dataframe(pd.DataFrame(career_rows), use_container_width=True, hide_index=True)
        table = weekly_table(sf, str(p["pos"]))
        if not table.empty:
            st.markdown(f"#### {season} weekly consistency")
            fig = px.bar(table, x="WK", y="PPR", title=f"{p['name']} — week-by-week PPR")
            fig.add_hline(y=15, line_dash="dash", annotation_text="15 PPR")
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=8,r=8,t=42,b=8), paper_bgcolor="#080b0f", plot_bgcolor="#080b0f", xaxis=dict(dtick=1))
            st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# ASK SHIVA — GROUNDED IN THE SAME DATA
# -----------------------------------------------------------------------------
def mentioned_players(question: str, limit: int = 4) -> list[str]:
    q = name_key(question)
    q_words = re.findall(r"[a-z0-9]+", question.casefold())
    found = []
    for name in players["name"].astype(str):
        nk = name_key(name)
        last = re.sub(r"[^a-z0-9]+", "", name.casefold().split()[-1])
        if nk and nk in q:
            found.append(name)
        elif len(last) >= 5 and last in q_words:
            found.append(name)
        if len(found) >= limit:
            break
    return found


def player_history_context(player_name: str, question: str, weekly: pd.DataFrame) -> str:
    pf = weekly_for_player(weekly, player_name)
    if pf.empty:
        return f"{player_name}: no historical weekly match."
    requested = [int(x) for x in re.findall(r"20\d{2}", question) if int(x) in DATA_SEASONS]
    seasons = requested or sorted(pd.to_numeric(pf["season"], errors="coerce").dropna().astype(int).unique().tolist(), reverse=True)[:3]
    blocks = []
    for season in seasons:
        sf = pf.loc[pd.to_numeric(pf["season"], errors="coerce").eq(season)]
        s = season_summary(sf)
        weekly_pts = espn_ppr_points(sf).round(1).tolist()
        blocks.append(f"{season}: {s['games']} games, {s['total']:.1f} PPR, {s['ppg']:.2f} PPG, {s['weeks15']} weeks >=15, {s['weeks20']} weeks >=20; weekly PPR={weekly_pts}")
    return f"{player_name}: " + " | ".join(blocks)


def ask_shiva(question: str) -> str:
    names = mentioned_players(question)
    history_context = []
    if names:
        try:
            weekly = load_weekly()
            history_context = [player_history_context(n, question, weekly) for n in names]
        except Exception as exc:
            history_context = [f"Historical feed unavailable: {exc}"]

    # Deterministic local answer for direct single-player/year PPG questions, even if no API key is configured.
    years = [int(x) for x in re.findall(r"20\d{2}", question) if int(x) in DATA_SEASONS]
    if len(names) == 1 and years and any(term in question.casefold() for term in ("points per game", "ppg", "average")):
        try:
            weekly = load_weekly(); pf = weekly_for_player(weekly, names[0]); year = years[0]
            sf = pf.loc[pd.to_numeric(pf["season"], errors="coerce").eq(year)]
            s = season_summary(sf)
            if s["games"]:
                return f"{names[0]} averaged **{s['ppg']:.2f} ESPN full-PPR points per game in {year}** across {s['games']} regular-season games ({s['total']:.1f} total PPR points)."
        except Exception:
            pass

    key = None
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    key = key or os.getenv("OPENAI_API_KEY")
    if not key or OpenAI is None:
        if history_context:
            return "Verified app data:\n\n" + "\n\n".join(history_context) + "\n\nAdd OPENAI_API_KEY in Streamlit Secrets for full Shiva analysis and recommendations."
        return "Add OPENAI_API_KEY in Streamlit Secrets to enable Shiva recommendations. The rankings and player-profile data are already connected independently."

    roster = user_roster()
    roster_text = ", ".join(roster["name"].tolist()) if not roster.empty else "No players drafted yet"
    remaining = available_df().head(40)[["name","pos","team","draft_adp","overall_rank"]].to_dict("records")
    system = (
        "You are Shiva, an elite fantasy-football analyst inside a draft application. Default scoring is ESPN full 1-point PPR with 4 points per passing TD. "
        "Be decisive and concise. Treat the supplied rankings, roster, and historical stat context as authoritative app data. Never invent a stat, injury, transaction, ADP, or news item that is not supplied. "
        "For draft advice, account for positional scarcity, roster construction, ADP opportunity cost, and the players actually available. "
        f"User draft slot: {st.session_state.user_slot}. User roster: {roster_text}. Top available: {remaining}. "
        f"Historical player context: {history_context}."
    )
    try:
        client = OpenAI(api_key=key)
        response = client.responses.create(model="gpt-5-mini", input=[{"role":"system","content":system},{"role":"user","content":question}])
        return response.output_text
    except Exception as exc:
        return f"Ask Shiva could not complete the model request: {exc}"


# -----------------------------------------------------------------------------
# APPLICATION
# -----------------------------------------------------------------------------
app_header(); st.write("")

if rankings_source.startswith("EMERGENCY"):
    st.error(rankings_source)
else:
    st.markdown('<span class="data-chip">● 2026 ranking feed connected</span>', unsafe_allow_html=True)

if st.session_state.selected_player:
    render_profile(str(st.session_state.selected_player))
    st.stop()

page = st.radio("Main navigation", ["Home", "Mock Draft", "Rankings", "Ask Shiva"], horizontal=True, label_visibility="collapsed", key="main_page")
st.write("")

if page == "Home":
    st.markdown('<div class="section-title"><div><h2>Draft Command Center</h2><span>Current board + roster, without dashboard clutter.</span></div></div>', unsafe_allow_html=True)
    a,b = st.columns([1.45,1])
    with a:
        st.markdown("#### Top Available")
        render_player_rows(available_df(), limit=10, return_page="Home")
    with b:
        st.markdown("#### Your Roster")
        render_roster()

elif page == "Mock Draft":
    settings, controls = st.columns([2.3,1])
    with settings:
        st.markdown('<div class="section-title"><div><h2>Live Mock Draft</h2><span>10-team snake · real 2026 board · persistent state</span></div></div>', unsafe_allow_html=True)
    with controls:
        x1,x2 = st.columns(2)
        with x1:
            slot = st.selectbox("Draft slot", list(range(1, st.session_state.team_count+1)), index=st.session_state.user_slot-1, key="slot_widget")
            if slot != st.session_state.user_slot and not st.session_state.draft_log:
                st.session_state.user_slot = slot
        with x2:
            if st.button("Reset draft", use_container_width=True):
                reset_draft(); st.rerun()
    if not st.session_state.draft_log:
        sim_to_user_pick()

    view = st.radio("Draft navigation", ["Players", "Draft Board", "Queue", "Roster"], horizontal=True, label_visibility="collapsed", key="draft_view")
    if view == "Players":
        f1,f2 = st.columns([2,1])
        with f1: search = st.text_input("Search", placeholder="Search player or NFL team…", key="draft_search")
        with f2: pos = st.selectbox("Position", ["ALL","QB","RB","WR","TE","DST","K"], key="draft_pos")
        pool = available_df()
        if search:
            q = search.strip().casefold(); pool = pool.loc[pool["name"].str.casefold().str.contains(q, regex=False) | pool["team"].str.casefold().str.contains(q, regex=False)]
        if pos != "ALL": pool = pool.loc[pool["pos"].eq(pos)]
        on_clock = pick_team(next_pick_number(), st.session_state.team_count) == st.session_state.user_slot
        if on_clock: st.success(f"You are on the clock at pick {next_pick_number()}.")
        render_player_rows(pool, allow_draft=on_clock, limit=60, return_page="Mock Draft")
    elif view == "Draft Board":
        render_board()
    elif view == "Queue":
        qdf = players.loc[players["id"].isin(st.session_state.queue) & ~players["id"].isin(drafted_ids())].copy()
        order = {pid:i for i,pid in enumerate(st.session_state.queue)}
        if not qdf.empty: qdf["qorder"] = qdf["id"].map(order); qdf = qdf.sort_values("qorder")
        render_player_rows(qdf, queue_mode=True, limit=80, return_page="Mock Draft")
    else:
        r1,r2 = st.columns([1,1.2])
        with r1: render_roster()
        with r2:
            roster = user_roster()
            if not roster.empty:
                counts = roster["pos"].value_counts().rename_axis("Position").reset_index(name="Players")
                fig = px.bar(counts, x="Position", y="Players", title="Roster construction")
                fig.update_layout(template="plotly_dark",height=300,margin=dict(l=8,r=8,t=42,b=8),paper_bgcolor="#080b0f",plot_bgcolor="#080b0f",yaxis=dict(dtick=1))
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Your roster will populate as you draft.")

elif page == "Rankings":
    st.markdown('<div class="section-title"><div><h2>2026 Draft Rankings</h2><span>Connected directly to your current ranking database.</span></div></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1: rq = st.text_input("Search rankings", placeholder="Player or team…")
    with c2: rp = st.selectbox("Filter position", ["ALL","QB","RB","WR","TE","DST","K"])
    rdf = players.copy()
    if rq:
        q = rq.casefold().strip(); rdf = rdf.loc[rdf["name"].str.casefold().str.contains(q,regex=False) | rdf["team"].str.casefold().str.contains(q,regex=False)]
    if rp != "ALL": rdf = rdf.loc[rdf["pos"].eq(rp)]
    render_player_rows(rdf, limit=100, return_page="Rankings")

else:
    st.markdown('<div class="ask-card"><div class="ask-title">Ask Shiva</div><div class="ask-sub">Draft decisions and player-stat questions grounded in the same data powering the app.</div></div>', unsafe_allow_html=True)
    question = st.text_area("What do you want to know?", placeholder="How many PPR points per game did Christian McCaffrey average in 2025?", height=105)
    if st.button("Ask Shiva", type="primary", use_container_width=True):
        if question.strip():
            with st.spinner("Analyzing verified app data…"):
                answer = ask_shiva(question.strip())
            st.session_state.ask_history.insert(0,(question.strip(),answer))
    for q,a in st.session_state.ask_history[:6]:
        st.markdown(f"**{q}**"); st.markdown(f'<div class="answer">{a}</div>',unsafe_allow_html=True); st.write("")

st.caption("Shiva Fantasy Football · 2026 rankings from your Draft-Coach ranking feed · historical regular-season player data from your 2014–2025 weekly master database · ESPN full 1-point PPR calculations.")