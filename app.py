from __future__ import annotations

import hashlib
import html
import os
import random
import re
from typing import Any
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(page_title="Shiva Fantasy Football", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

RANKINGS_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/current_rankings.csv"
WEEKLY_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/player_weekly_master_2014_2025.csv.gz"
BIRTHS_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/player_birth_dates.csv"
DATA_SEASONS = tuple(range(2014, 2026))
DEFAULT_TEAMS = 10
DEFAULT_ROUNDS = 15
ROSTER_SLOTS = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K", "BE", "BE", "BE", "BE", "BE", "BE"]

CSS = r"""
<style>
:root{--bg:#080b0f;--panel:#10151b;--panel2:#151b22;--line:#242c35;--text:#f7f9fb;--muted:#8f9ba7;--red:#e31837;--green:#21c16b;--qb:#7657d7;--rb:#22a99f;--wr:#3989ee;--te:#ed893d;--dst:#d7bb3f;--k:#727d89}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1480px;padding-top:.45rem;padding-bottom:4rem}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden}
.shiva-shell{border:1px solid var(--line);background:linear-gradient(180deg,#11161c,#0c1015);border-radius:16px;overflow:hidden}
.topbar{min-height:60px;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 14px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:9px}.brand-mark{width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,#f52d49,#9d071c);display:flex;align-items:center;justify-content:center;font-size:20px}.brand-title{font-size:18px;font-weight:950}.brand-sub{color:var(--muted);font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.1px}
.live-pill{display:inline-flex;align-items:center;gap:6px;color:#dbe1e7;font-size:9px;font-weight:900;border:1px solid var(--line);background:#151b21;padding:6px 8px;border-radius:999px}.live-dot{width:7px;height:7px;border-radius:50%;background:var(--green)}
.hero{padding:14px 16px 7px}.hero h1{margin:0;color:#fff;font-size:clamp(26px,4vw,42px);line-height:1;letter-spacing:-1.2px}.hero p{margin:7px 0 0;color:var(--muted);font-size:12px}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;padding:8px 16px 15px}.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:9px 11px}.kpi-label{color:var(--muted);font-size:8px;text-transform:uppercase;font-weight:850}.kpi-value{color:#fff;font-size:17px;font-weight:950;margin-top:2px}
.data-chip{display:inline-flex;align-items:center;border:1px solid #1e5439;background:#0d2118;color:#7ce6aa;padding:5px 8px;border-radius:999px;font-size:9px;font-weight:900}
.section-title h2{margin:3px 0 2px;color:#fff;font-size:21px}.section-title span{color:var(--muted);font-size:11px}
.player-card{display:grid;grid-template-columns:34px minmax(0,1fr) 52px 52px 45px;align-items:center;gap:6px;min-height:57px;padding:7px 8px;margin:0 0 5px;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
.rank{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:#1d242c;color:#dbe0e5;font-weight:950;font-size:11px}.player-link{display:block;color:#fff!important;text-decoration:none!important;font-weight:920;font-size:13px;line-height:1.12;padding:3px 0}.player-link:active,.player-link:hover{color:#dfff00!important}.player-meta{color:var(--muted);font-size:9px;margin-top:3px}.cell-label{color:var(--muted);font-size:7px;text-transform:uppercase;font-weight:850}.cell-value{color:#fff;font-size:11px;font-weight:900}
.pos{display:inline-flex;align-items:center;justify-content:center;min-width:27px;border-radius:5px;padding:3px 5px;font-weight:950;font-size:8px;color:#fff}.pos-QB{background:var(--qb)}.pos-RB{background:var(--rb)}.pos-WR{background:var(--wr)}.pos-TE{background:var(--te)}.pos-DST{background:var(--dst);color:#151515}.pos-K{background:var(--k)}
.board-wrap{border:1px solid var(--line);border-radius:12px;background:#0c1014;padding:7px}.board{display:grid;grid-template-columns:repeat(10,minmax(78px,1fr));gap:5px}.pick{min-height:62px;border-radius:8px;padding:7px;border:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;justify-content:space-between}.pick.empty{background:#141a20;color:#68737e}.pick.QB{background:rgba(118,87,215,.23)}.pick.RB{background:rgba(34,169,159,.22)}.pick.WR{background:rgba(57,137,238,.22)}.pick.TE{background:rgba(237,137,61,.22)}.pick.DST{background:rgba(215,187,63,.24)}.pick.K{background:rgba(114,125,137,.23)}.pick-no{color:#9ca7b1;font-size:8px;font-weight:850}.pick-name{color:#fff;font-size:10px;line-height:1.05;font-weight:950}.pick-meta{color:#adb6bf;font-size:8px}
.roster-card{border:1px solid var(--line);border-radius:11px;background:var(--panel);overflow:hidden;margin-bottom:9px}.roster-head{display:flex;justify-content:space-between;padding:9px 11px;background:#161c23;border-bottom:1px solid var(--line)}.slot{display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:7px;align-items:center;padding:8px 10px;border-bottom:1px solid #1c232b}.slot-name{color:#7f8b96;font-size:9px;font-weight:950}.slot-player{color:#fff;font-size:11px;font-weight:880}.slot-meta{color:#8f9aa5;font-size:9px}
.profile-hero{border:1px solid var(--line);border-radius:14px;padding:14px;background:linear-gradient(145deg,#171e26,#0f141a)}.profile-name-big{color:#fff;font-size:29px;font-weight:980;letter-spacing:-1px}.profile-meta{color:#aab4be;font-size:11px;margin-top:3px}.profile-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:12px}.profile-stat{border:1px solid var(--line);border-radius:9px;background:#0d1217;padding:9px}.profile-stat b{display:block;color:#fff;font-size:16px}.profile-stat small{color:#87939e;font-size:8px;font-weight:850;text-transform:uppercase}
.ask-card{border:1px solid var(--line);border-radius:14px;background:linear-gradient(160deg,#151b21,#0c1014);padding:15px}.ask-title{font-size:24px;color:#fff;font-weight:980}.ask-sub{color:var(--muted);font-size:12px;margin:4px 0 10px}.answer{border-left:3px solid var(--red);background:#10161b;border-radius:0 9px 9px 0;padding:12px 14px;color:#e9edf1;line-height:1.5}
.stButton>button{border-radius:8px!important;font-weight:850!important;min-height:40px}.stButton>button[kind="primary"]{background:var(--red)!important;border-color:var(--red)!important;color:#fff!important}
[data-testid="stMetric"]{background:#10161c;border:1px solid var(--line);padding:7px 9px;border-radius:9px}
div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:5px!important;width:100%!important}div[role="radiogroup"] label{background:#11171d;border:1px solid var(--line);border-radius:8px;padding:6px!important;margin:0!important;justify-content:center!important;min-height:39px}div[role="radiogroup"] label:has(input:checked){background:#252d36;border-color:#52606d}div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10px!important;font-weight:900!important;white-space:nowrap!important}
@media(max-width:820px){
 .block-container{padding-left:.4rem;padding-right:.4rem;padding-top:.25rem}.topbar{padding:8px 9px}.brand-sub{display:none}.live-pill{font-size:8px;padding:5px 6px}.hero{padding:12px 10px 5px}.hero h1{font-size:26px}.hero p{font-size:10px}.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));padding:6px 10px 11px}.kpi{padding:7px 8px}.kpi-value{font-size:15px}
 .player-card{grid-template-columns:30px minmax(0,1fr) 43px 43px;gap:4px;padding:6px}.player-card .bye-cell{display:none}.player-link{font-size:12px}.player-meta{font-size:8px}.cell-value{font-size:10px}
 .profile-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.profile-name-big{font-size:24px}.profile-meta{font-size:10px}
 .board{display:flex;flex-direction:column}.pick{min-height:51px}
 div[role="radiogroup"]{grid-template-columns:repeat(2,minmax(0,1fr))!important}
 [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.35rem!important}[data-testid="stHorizontalBlock"]>[data-testid="column"]{min-width:160px!important;flex:1 1 160px!important}
 [data-testid="stDataFrame"]{font-size:10px!important}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def stable_id(name: str) -> str:
    return hashlib.md5(str(name).encode("utf-8")).hexdigest()[:12]


def name_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def safe_num(value: Any) -> float:
    try:
        return float(value) if pd.notna(value) else np.nan
    except Exception:
        return np.nan


@st.cache_data(ttl=1800, show_spinner=False)
def load_rankings() -> tuple[pd.DataFrame, str]:
    try:
        raw = pd.read_csv(RANKINGS_URL)
        df = raw.rename(columns={"player_name": "name", "position": "pos"}).copy()
        if not {"name", "pos", "team"}.issubset(df.columns):
            raise ValueError("ranking feed missing name/position/team")
        df["name"] = df["name"].astype(str).str.strip()
        df["pos"] = df["pos"].astype(str).str.upper().replace({"DEF": "DST", "D/ST": "DST"})
        df["team"] = df["team"].fillna("FA").astype(str).str.upper()
        for col in ("adp", "consensus_adp", "overall_rank", "position_rank", "bye"):
            df[col] = pd.to_numeric(df[col], errors="coerce") if col in df.columns else np.nan
        df["draft_adp"] = df["consensus_adp"].fillna(df["adp"]).fillna(df["overall_rank"])
        df["overall_rank"] = df["overall_rank"].fillna(df["draft_adp"])
        df["id"] = df["name"].map(stable_id)
        df = df.dropna(subset=["name"]).drop_duplicates("id").sort_values(["overall_rank", "draft_adp", "name"], na_position="last").reset_index(drop=True)
        return df, "Draft-Coach/current_rankings.csv"
    except Exception as exc:
        emergency = pd.DataFrame([
            {"name":"Jahmyr Gibbs","pos":"RB","team":"DET","draft_adp":1.0,"overall_rank":1,"position_rank":1,"bye":6},
            {"name":"Bijan Robinson","pos":"RB","team":"ATL","draft_adp":2.0,"overall_rank":2,"position_rank":2,"bye":11},
            {"name":"Ja'Marr Chase","pos":"WR","team":"CIN","draft_adp":3.2,"overall_rank":3,"position_rank":1,"bye":6},
            {"name":"Puka Nacua","pos":"WR","team":"LAR","draft_adp":3.8,"overall_rank":4,"position_rank":2,"bye":11},
        ])
        emergency["id"] = emergency["name"].map(stable_id)
        return emergency, f"EMERGENCY FALLBACK — {exc}"


WEEKLY_COLUMNS = {
    "player_id","player_display_name","player_name","name","position","recent_team","team","season","season_type","week","opponent_team","opponent","fantasy_points_ppr","fantasy_points",
    "passing_yards","passing_tds","interceptions","passing_attempts","completions","rushing_yards","rushing_tds","carries","targets","receptions","receiving_yards","receiving_tds","fumbles_lost",
    "passing_two_point_conversions","rushing_two_point_conversions","receiving_two_point_conversions"
}


@st.cache_data(ttl=21600, show_spinner=False)
def load_weekly() -> pd.DataFrame:
    df = pd.read_csv(WEEKLY_URL, compression="gzip", low_memory=False, usecols=lambda c: c in WEEKLY_COLUMNS)
    for c in WEEKLY_COLUMNS:
        if c in df.columns and c not in {"player_id","player_display_name","player_name","name","position","recent_team","team","season_type","opponent_team","opponent"}:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "season_type" in df.columns:
        mask = df["season_type"].astype(str).str.upper().isin(["REG", "REGULAR", "REGULAR SEASON"])
        if mask.any():
            df = df.loc[mask].copy()
    if "week" in df.columns:
        df = df.loc[df["week"].between(1, 18, inclusive="both")].copy()
    return df


@st.cache_data(ttl=86400, show_spinner=False)
def load_births() -> pd.DataFrame:
    try:
        return pd.read_csv(BIRTHS_URL, low_memory=False)
    except Exception:
        return pd.DataFrame()


def weekly_name_col(df: pd.DataFrame) -> str | None:
    return next((c for c in ("player_display_name", "player_name", "name") if c in df.columns), None)


def weekly_for_player(weekly: pd.DataFrame, player_name: str) -> pd.DataFrame:
    if weekly.empty:
        return pd.DataFrame()
    ncol = weekly_name_col(weekly)
    if not ncol:
        return pd.DataFrame()
    target = name_key(player_name)
    out = weekly.loc[weekly[ncol].astype(str).map(name_key).eq(target)].copy()
    if out.empty:
        last = name_key(str(player_name).split()[-1])
        if len(last) >= 5:
            keys = weekly[ncol].astype(str).map(name_key)
            mask = keys.str.endswith(last)
            names = weekly.loc[mask, ncol].dropna().astype(str).unique().tolist()
            if len(names) == 1:
                out = weekly.loc[mask].copy()
    return out.sort_values([c for c in ("season", "week") if c in out.columns]) if not out.empty else out


def espn_ppr_points(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=float)
    if "fantasy_points_ppr" in frame.columns:
        stored = pd.to_numeric(frame["fantasy_points_ppr"], errors="coerce")
        if stored.notna().any():
            return stored.round(2)
    scoring = {"passing_yards":.04,"passing_tds":4.,"interceptions":-2.,"rushing_yards":.1,"rushing_tds":6.,"receptions":1.,"receiving_yards":.1,"receiving_tds":6.,"fumbles_lost":-2.,"passing_two_point_conversions":2.,"rushing_two_point_conversions":2.,"receiving_two_point_conversions":2.}
    total = pd.Series(0.0, index=frame.index); found = False
    for c, m in scoring.items():
        if c in frame.columns:
            total += pd.to_numeric(frame[c], errors="coerce").fillna(0) * m; found = True
    if found:
        return total.round(2)
    return pd.to_numeric(frame.get("fantasy_points", pd.Series(np.nan, index=frame.index)), errors="coerce")


players, rankings_source = load_rankings()


def init_state() -> None:
    defaults = {"draft_log":[],"queue":[],"user_slot":3,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"ask_history":[],"main_page":"Home","draft_view":"Players"}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


init_state()


def pick_team(pick_no:int, team_count:int)->int:
    round_no=(pick_no-1)//team_count+1; within=(pick_no-1)%team_count+1
    return within if round_no%2 else team_count-within+1


def overall_pick_for_team(round_no:int, team_no:int, team_count:int)->int:
    within=team_no if round_no%2 else team_count-team_no+1
    return (round_no-1)*team_count+within


def drafted_ids()->set[str]: return {x["id"] for x in st.session_state.draft_log}
def available_df()->pd.DataFrame: return players.loc[~players["id"].isin(drafted_ids())].copy().sort_values(["draft_adp","overall_rank"],na_position="last")
def next_pick_number()->int: return len(st.session_state.draft_log)+1


def record_pick(player_id:str, team_no:int)->None:
    if player_id in drafted_ids(): return
    match=players.loc[players["id"].eq(player_id)]
    if match.empty:return
    row=match.iloc[0]; pick_no=next_pick_number()
    st.session_state.draft_log.append({"pick":pick_no,"round":(pick_no-1)//st.session_state.team_count+1,"team":team_no,"id":row["id"],"name":row["name"],"pos":row["pos"],"nfl_team":row["team"],"adp":safe_num(row["draft_adp"]),"overall_rank":safe_num(row["overall_rank"])})
    if player_id in st.session_state.queue: st.session_state.queue.remove(player_id)


def cpu_pick()->None:
    pool=available_df().head(24)
    if pool.empty:return
    pick_no=next_pick_number(); rng=random.Random(26000+pick_no); idx=min(len(pool)-1,max(0,int(abs(rng.gauss(1.4,1.7)))))
    record_pick(str(pool.iloc[idx]["id"]),pick_team(pick_no,st.session_state.team_count))


def sim_to_user_pick()->None:
    total=st.session_state.team_count*st.session_state.rounds; guard=0
    while next_pick_number()<=total and pick_team(next_pick_number(),st.session_state.team_count)!=st.session_state.user_slot:
        before=next_pick_number(); cpu_pick(); guard+=1
        if next_pick_number()==before or guard>total: break


def draft_user(player_id:str)->None:
    if next_pick_number()>st.session_state.team_count*st.session_state.rounds:return
    sim_to_user_pick()
    if pick_team(next_pick_number(),st.session_state.team_count)==st.session_state.user_slot:
        record_pick(player_id,st.session_state.user_slot); sim_to_user_pick()


def reset_draft()->None: st.session_state.draft_log=[]; st.session_state.queue=[]
def user_roster()->pd.DataFrame: return pd.DataFrame([x for x in st.session_state.draft_log if x["team"]==st.session_state.user_slot])
def fmt_num(v:Any,decimals:int=1,fallback:str="—")->str:
    n=safe_num(v); return f"{n:.{decimals}f}" if pd.notna(n) else fallback

def fmt_int(v:Any,fallback:str="—")->str:
    n=safe_num(v); return str(int(round(n))) if pd.notna(n) else fallback

def pos_badge(pos:str)->str:
    p=str(pos).upper().replace("D/ST","DST"); return f'<span class="pos pos-{p}">{html.escape(p)}</span>'

def profile_href(row:pd.Series,return_page:str)->str:
    return f"?player={quote_plus(str(row['id']))}&name={quote_plus(str(row['name']))}&return={quote_plus(return_page)}"


def app_header()->None:
    pick_no=next_pick_number(); total=st.session_state.team_count*st.session_state.rounds; round_no=min(st.session_state.rounds,(max(1,pick_no)-1)//st.session_state.team_count+1); roster_n=len(user_roster())
    live_ok=not rankings_source.startswith("EMERGENCY")
    st.markdown(f'<div class="shiva-shell"><div class="topbar"><div class="brand"><div class="brand-mark">🏆</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div><div class="live-pill"><span class="live-dot"></span>{"REAL DATA CONNECTED" if live_ok else "DATA FALLBACK"}</div></div><div class="hero"><h1>Win the draft before it starts.</h1><p>2026 rankings + verified 2014–2025 full-PPR weekly history + live draft context.</p></div><div class="kpi-grid"><div class="kpi"><div class="kpi-label">Current Pick</div><div class="kpi-value">{min(pick_no,total)} / {total}</div></div><div class="kpi"><div class="kpi-label">Round</div><div class="kpi-value">{round_no}</div></div><div class="kpi"><div class="kpi-label">Your Slot</div><div class="kpi-value">#{st.session_state.user_slot}</div></div><div class="kpi"><div class="kpi-label">Roster</div><div class="kpi-value">{roster_n} / {st.session_state.rounds}</div></div></div></div>',unsafe_allow_html=True)


def render_player_rows(df:pd.DataFrame,*,allow_draft:bool=False,queue_mode:bool=False,limit:int=50,return_page:str="Home")->None:
    if df.empty: st.info("No players match this view."); return
    for _,row in df.head(limit).iterrows():
        pid=str(row["id"]); name=html.escape(str(row["name"])); team=html.escape(str(row["team"])); href=profile_href(row,return_page)
        st.markdown(f'<div class="player-card"><div class="rank">{fmt_int(row.get("overall_rank"))}</div><div><a class="player-link" href="{href}" target="_self">{name}</a><div class="player-meta">{pos_badge(row["pos"])}&nbsp;&nbsp;{team} · tap name for profile</div></div><div><div class="cell-label">ADP</div><div class="cell-value">{fmt_num(row.get("draft_adp"))}</div></div><div><div class="cell-label">Pos</div><div class="cell-value">{html.escape(str(row["pos"]))}{fmt_int(row.get("position_rank"))}</div></div><div class="bye-cell"><div class="cell-label">Bye</div><div class="cell-value">{fmt_int(row.get("bye"))}</div></div></div>',unsafe_allow_html=True)
        if allow_draft:
            if st.button(f"Draft {row['name']}",key=f"draft_{pid}",type="primary",use_container_width=True): draft_user(pid); st.rerun()
        elif queue_mode:
            if st.button(f"Remove {row['name']} from queue",key=f"remove_{pid}",use_container_width=True):
                if pid in st.session_state.queue: st.session_state.queue.remove(pid)
                st.rerun()
        else:
            queued=pid in st.session_state.queue
            if st.button("✓ Queued" if queued else f"+ Queue {row['name']}",key=f"queue_{return_page}_{pid}",use_container_width=True,disabled=queued): st.session_state.queue.append(pid); st.rerun()


def render_board()->None:
    pick_map={x["pick"]:x for x in st.session_state.draft_log}; html_parts=['<div class="board-wrap"><div class="board">']
    for round_no in range(1,st.session_state.rounds+1):
        for display_team in range(1,st.session_state.team_count+1):
            pick_no=overall_pick_for_team(round_no,display_team,st.session_state.team_count); pick=pick_map.get(pick_no)
            if pick:
                ppos=html.escape(str(pick["pos"]).replace("D/ST","DST")); pname=html.escape(str(pick["name"])); nfl=html.escape(str(pick["nfl_team"]))
                html_parts.append(f'<div class="pick {ppos}"><div class="pick-no">{pick_no} · TEAM {pick["team"]}</div><div class="pick-name">{pname}</div><div class="pick-meta">{ppos} · {nfl}</div></div>')
            else:
                html_parts.append(f'<div class="pick empty"><div class="pick-no">{pick_no} · TEAM {pick_team(pick_no,st.session_state.team_count)}</div><div class="pick-name">Available</div><div class="pick-meta">Round {round_no}</div></div>')
    html_parts.append('</div></div>'); st.markdown(''.join(html_parts),unsafe_allow_html=True)


def assign_roster_slots(roster:pd.DataFrame)->list[tuple[str,dict|None]]:
    if roster.empty:return [(slot,None) for slot in ROSTER_SLOTS]
    remaining=roster.to_dict("records"); out=[]
    for slot in ROSTER_SLOTS:
        idx=None
        for i,p in enumerate(remaining):
            pos=str(p["pos"]).replace("D/ST","DST")
            if slot==pos or (slot=="FLEX" and pos in {"RB","WR","TE"}): idx=i; break
        if idx is None and slot=="BE" and remaining: idx=0
        out.append((slot,remaining.pop(idx) if idx is not None else None))
    return out


def render_roster()->None:
    st.markdown('<div class="roster-card"><div class="roster-head"><strong>YOUR TEAM</strong><span>Live draft roster</span></div>',unsafe_allow_html=True)
    for slot,p in assign_roster_slots(user_roster()):
        if p:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div><div class="slot-player">{html.escape(str(p["name"]))}</div><div class="slot-meta">{html.escape(str(p["pos"]))} · {html.escape(str(p["nfl_team"]))}</div></div><div class="slot-meta">Pick {p["pick"]}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="slot"><div class="slot-name">{slot}</div><div class="slot-player" style="color:#66707c">Empty</div><div></div></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)


def season_summary(frame:pd.DataFrame)->dict[str,Any]:
    pts=espn_ppr_points(frame).dropna(); return {"games":int(len(pts)),"total":float(pts.sum()) if len(pts) else np.nan,"ppg":float(pts.mean()) if len(pts) else np.nan,"median":float(pts.median()) if len(pts) else np.nan,"weeks15":int((pts>=15).sum()),"weeks20":int((pts>=20).sum())}


def player_birth_age(player_name:str,season:int)->str:
    births=load_births()
    if births.empty:return "—"
    ncol=weekly_name_col(births)
    if "name_key" in births.columns: mask=births["name_key"].astype(str).map(name_key).eq(name_key(player_name))
    elif ncol: mask=births[ncol].astype(str).map(name_key).eq(name_key(player_name))
    else:return "—"
    row=births.loc[mask]
    if row.empty:return "—"
    dob_col=next((c for c in ("birth_date","birthdate","dob") if c in row.columns),None)
    if not dob_col:return "—"
    dob=pd.to_datetime(row.iloc[0][dob_col],errors="coerce")
    if pd.isna(dob):return "—"
    return str(max(0,int((pd.Timestamp(year=int(season),month=9,day=1)-dob).days/365.2425)))


def weekly_table(frame:pd.DataFrame,pos:str)->pd.DataFrame:
    if frame.empty:return pd.DataFrame()
    f=frame.copy(); f["PPR"]=espn_ppr_points(f)
    data={"WK":pd.to_numeric(f["week"],errors="coerce").astype("Int64"),"PPR":f["PPR"].round(1)}
    opp=next((c for c in ("opponent_team","opponent") if c in f.columns),None)
    if opp:data["OPP"]=f[opp].fillna("—").astype(str)
    p=str(pos).upper().replace("D/ST","DST")
    pairs={"QB":[("PASS YDS","passing_yards"),("PASS TD","passing_tds"),("INT","interceptions"),("RUSH YDS","rushing_yards"),("RUSH TD","rushing_tds")],"WR":[("TGT","targets"),("REC","receptions"),("REC YDS","receiving_yards"),("REC TD","receiving_tds")],"TE":[("TGT","targets"),("REC","receptions"),("REC YDS","receiving_yards"),("REC TD","receiving_tds")],"RB":[("CAR","carries"),("RUSH YDS","rushing_yards"),("RUSH TD","rushing_tds"),("REC","receptions"),("REC YDS","receiving_yards"),("REC TD","receiving_tds")]}.get(p,[])
    for label,c in pairs:
        if c in f.columns:data[label]=pd.to_numeric(f[c],errors="coerce").fillna(0).round(0).astype(int)
    table=pd.DataFrame(data).loc[lambda x:pd.to_numeric(x["WK"],errors="coerce").between(1,18)].sort_values("WK")
    cols=["WK","OPP","PPR"]+[c for c in table.columns if c not in {"WK","OPP","PPR"}]
    return table[[c for c in cols if c in table.columns]]


def render_profile(player_id:str,player_name_hint:str="",return_page:str="Rankings")->None:
    match=players.loc[players["id"].astype(str).eq(str(player_id))]
    if match.empty and player_name_hint: match=players.loc[players["name"].astype(str).map(name_key).eq(name_key(player_name_hint))]
    if match.empty: st.error("That player is not in the current 2026 ranking feed."); return
    p=match.iloc[0]; back_page=return_page if return_page in {"Home","Mock Draft","Rankings","Ask Shiva"} else "Rankings"
    st.markdown(f'<a href="?page={quote_plus(back_page)}" target="_self" style="color:#fff;text-decoration:none;font-weight:900">← Back to {html.escape(back_page)}</a>',unsafe_allow_html=True)
    try:
        with st.spinner("Loading verified weekly player history…"): pf=weekly_for_player(load_weekly(),str(p["name"]))
    except Exception as exc:
        st.error(f"Weekly data could not be loaded: {exc}"); pf=pd.DataFrame()
    seasons=sorted(pd.to_numeric(pf.get("season",pd.Series(dtype=float)),errors="coerce").dropna().astype(int).unique().tolist(),reverse=True)
    status="Drafted" if p["id"] in drafted_ids() else ("Queued" if p["id"] in st.session_state.queue else "Available")
    st.markdown(f'<div class="profile-hero"><div>{pos_badge(p["pos"])}</div><div class="profile-name-big">{html.escape(str(p["name"]))}</div><div class="profile-meta">{html.escape(str(p["team"]))} · 2026 ADP {fmt_num(p.get("draft_adp"))} · Overall #{fmt_int(p.get("overall_rank"))} · Bye {fmt_int(p.get("bye"))}</div><div class="profile-stats"><div class="profile-stat"><b>{fmt_num(p.get("draft_adp"))}</b><small>2026 Consensus ADP</small></div><div class="profile-stat"><b>{html.escape(str(p["pos"]))}{fmt_int(p.get("position_rank"))}</b><small>Position Rank</small></div><div class="profile-stat"><b>{len(seasons)}</b><small>Seasons On File</small></div><div class="profile-stat"><b>{status}</b><small>Draft Status</small></div></div></div>',unsafe_allow_html=True)
    if pf.empty:
        st.info("No NFL regular-season weekly history is available for this player yet. Current 2026 ranking and draft information remain available above."); return
    season=st.selectbox("Season",seasons,index=0,key=f"season_{p['id']}")
    view=st.radio("Profile view",["Overview","Weekly Stats"],horizontal=True,label_visibility="collapsed",key=f"profile_view_{p['id']}")
    sf=pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(int(season))].copy(); summary=season_summary(sf)
    m1,m2,m3,m4=st.columns(4); m1.metric("PPR PPG",fmt_num(summary["ppg"])); m2.metric("PPR Total",fmt_num(summary["total"])); m3.metric("15+ Weeks",summary["weeks15"]); m4.metric("20+ Weeks",summary["weeks20"])
    st.caption(f"ESPN full 1-point PPR · {summary['games']} regular-season games · Age entering {season}: {player_birth_age(str(p['name']),int(season))}")
    table=weekly_table(sf,str(p["pos"]))
    if view=="Weekly Stats":
        if not table.empty:
            chart=table[["WK","PPR"]].dropna(); fig=px.line(chart,x="WK",y="PPR",markers=True,title=f"{p['name']} — {season} weekly ESPN PPR"); fig.update_layout(template="plotly_dark",height=285,margin=dict(l=5,r=5,t=38,b=5),paper_bgcolor="#080b0f",plot_bgcolor="#080b0f",xaxis=dict(dtick=1),yaxis_title="PPR"); st.plotly_chart(fig,use_container_width=True)
            st.dataframe(table,use_container_width=True,hide_index=True,height=min(580,45+34*len(table)))
    else:
        career=[]
        for yr in seasons:
            s=season_summary(pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(int(yr))]); career.append({"Season":yr,"Games":s["games"],"PPR Total":round(s["total"],1),"PPR PPG":round(s["ppg"],1),"15+":s["weeks15"],"20+":s["weeks20"]})
        st.markdown("#### Career fantasy history"); st.dataframe(pd.DataFrame(career),use_container_width=True,hide_index=True)
        if not table.empty:
            fig=px.bar(table,x="WK",y="PPR",title=f"{p['name']} — {season} weekly consistency"); fig.add_hline(y=15,line_dash="dash"); fig.update_layout(template="plotly_dark",height=275,margin=dict(l=5,r=5,t=38,b=5),paper_bgcolor="#080b0f",plot_bgcolor="#080b0f",xaxis=dict(dtick=1)); st.plotly_chart(fig,use_container_width=True)


def mentioned_players(question:str,limit:int=4)->list[str]:
    q=name_key(question); words=set(re.findall(r"[a-z0-9]+",question.casefold())); found=[]
    for name in players["name"].astype(str):
        nk=name_key(name); last=name_key(name.split()[-1])
        if (nk and nk in q) or (len(last)>=5 and last in words): found.append(name)
        if len(found)>=limit: break
    return found


def player_history_context(player_name:str,question:str,weekly:pd.DataFrame)->str:
    pf=weekly_for_player(weekly,player_name)
    if pf.empty:return f"{player_name}: no historical weekly match."
    requested=[int(x) for x in re.findall(r"20\d{2}",question) if int(x) in DATA_SEASONS]
    seasons=requested or sorted(pd.to_numeric(pf["season"],errors="coerce").dropna().astype(int).unique().tolist(),reverse=True)[:3]; blocks=[]
    for season in seasons:
        sf=pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(season)]; s=season_summary(sf); blocks.append(f"{season}: {s['games']} games, {s['total']:.1f} PPR, {s['ppg']:.2f} PPG, {s['weeks15']} weeks >=15, {s['weeks20']} weeks >=20")
    return f"{player_name}: "+" | ".join(blocks)


def ask_shiva(question:str)->str:
    names=mentioned_players(question); history=[]
    if names:
        try: weekly=load_weekly(); history=[player_history_context(n,question,weekly) for n in names]
        except Exception as exc: history=[f"Historical feed unavailable: {exc}"]
    years=[int(x) for x in re.findall(r"20\d{2}",question) if int(x) in DATA_SEASONS]
    if len(names)==1 and years and any(t in question.casefold() for t in ("points per game","ppg","average")):
        try:
            sf=weekly_for_player(load_weekly(),names[0]); sf=sf.loc[pd.to_numeric(sf["season"],errors="coerce").eq(years[0])]; s=season_summary(sf)
            if s["games"]: return f"{names[0]} averaged **{s['ppg']:.2f} ESPN full-PPR points per game in {years[0]}** across {s['games']} regular-season games ({s['total']:.1f} total PPR points)."
        except Exception: pass
    key=None
    try:key=st.secrets.get("OPENAI_API_KEY")
    except Exception:pass
    key=key or os.getenv("OPENAI_API_KEY")
    if not key or OpenAI is None:
        return ("Verified app data:\n\n"+"\n\n".join(history)+"\n\nAdd OPENAI_API_KEY in Streamlit Secrets for full Shiva analysis.") if history else "Add OPENAI_API_KEY in Streamlit Secrets to enable Shiva recommendations. Rankings and player profiles work independently."
    roster=user_roster(); roster_text=", ".join(roster["name"].tolist()) if not roster.empty else "No players drafted yet"; remaining=available_df().head(40)[["name","pos","team","draft_adp","overall_rank"]].to_dict("records")
    system="You are Shiva, an elite fantasy-football analyst. Default to ESPN full 1-point PPR and 4 points per passing TD. Treat supplied rankings, roster, and historical stats as authoritative. Never invent stats, injuries, transactions, ADP, or news. Be decisive and account for positional scarcity, roster construction, ADP opportunity cost, and actual availability. "+f"Draft slot: {st.session_state.user_slot}. Roster: {roster_text}. Top available: {remaining}. Historical context: {history}."
    try:
        response=OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=[{"role":"system","content":system},{"role":"user","content":question}]); return response.output_text
    except Exception as exc:return f"Ask Shiva could not complete the model request: {exc}"


app_header(); st.write("")
if rankings_source.startswith("EMERGENCY"): st.error(rankings_source)
else: st.markdown('<span class="data-chip">● 2026 ranking feed connected</span>',unsafe_allow_html=True)

qp=st.query_params; player_param=str(qp.get("player") or ""); name_param=str(qp.get("name") or ""); return_param=str(qp.get("return") or "Rankings")
if player_param:
    render_profile(player_param,name_param,return_param); st.stop()

pages=["Home","Mock Draft","Rankings","Ask Shiva"]; page_hint=str(qp.get("page") or "")
if page_hint in pages and st.session_state.get("main_page")!=page_hint: st.session_state.main_page=page_hint
page=st.radio("Main navigation",pages,horizontal=True,label_visibility="collapsed",key="main_page"); st.write("")

if page=="Home":
    st.markdown('<div class="section-title"><h2>Draft Command Center</h2><span>Current board + roster, without dashboard clutter.</span></div>',unsafe_allow_html=True)
    st.markdown("#### Top Available"); render_player_rows(available_df(),limit=10,return_page="Home"); st.markdown("#### Your Roster"); render_roster()
elif page=="Mock Draft":
    st.markdown('<div class="section-title"><h2>Live Mock Draft</h2><span>10-team snake · real 2026 board · persistent state</span></div>',unsafe_allow_html=True)
    slot=st.selectbox("Draft slot",list(range(1,st.session_state.team_count+1)),index=st.session_state.user_slot-1,key="slot_widget")
    if slot!=st.session_state.user_slot and not st.session_state.draft_log: st.session_state.user_slot=slot
    if st.button("Reset draft",use_container_width=True): reset_draft(); st.rerun()
    if not st.session_state.draft_log: sim_to_user_pick()
    view=st.radio("Draft navigation",["Players","Draft Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
    if view=="Players":
        search=st.text_input("Search",placeholder="Search player or NFL team…",key="draft_search"); pos=st.selectbox("Position",["ALL","QB","RB","WR","TE","DST","K"],key="draft_pos"); pool=available_df()
        if search:
            q=search.strip().casefold(); pool=pool.loc[pool["name"].str.casefold().str.contains(q,regex=False)|pool["team"].str.casefold().str.contains(q,regex=False)]
        if pos!="ALL": pool=pool.loc[pool["pos"].eq(pos)]
        on_clock=pick_team(next_pick_number(),st.session_state.team_count)==st.session_state.user_slot
        if on_clock: st.success(f"You are on the clock at pick {next_pick_number()}.")
        render_player_rows(pool,allow_draft=on_clock,limit=75,return_page="Mock Draft")
    elif view=="Draft Board": render_board()
    elif view=="Queue":
        qdf=players.loc[players["id"].isin(st.session_state.queue)&~players["id"].isin(drafted_ids())].copy(); order={pid:i for i,pid in enumerate(st.session_state.queue)}
        if not qdf.empty: qdf["qorder"]=qdf["id"].map(order); qdf=qdf.sort_values("qorder")
        render_player_rows(qdf,queue_mode=True,limit=80,return_page="Mock Draft")
    else: render_roster()
elif page=="Rankings":
    st.markdown('<div class="section-title"><h2>2026 Draft Rankings</h2><span>Connected directly to your current ranking database.</span></div>',unsafe_allow_html=True)
    rq=st.text_input("Search rankings",placeholder="Player or team…"); rp=st.selectbox("Filter position",["ALL","QB","RB","WR","TE","DST","K"]); rdf=players.copy()
    if rq:
        q=rq.casefold().strip(); rdf=rdf.loc[rdf["name"].str.casefold().str.contains(q,regex=False)|rdf["team"].str.casefold().str.contains(q,regex=False)]
    if rp!="ALL": rdf=rdf.loc[rdf["pos"].eq(rp)]
    render_player_rows(rdf,limit=150,return_page="Rankings")
else:
    st.markdown('<div class="ask-card"><div class="ask-title">Ask Shiva</div><div class="ask-sub">Draft decisions, player comparisons, historical performance and roster construction.</div></div>',unsafe_allow_html=True)
    question=st.text_area("What do you want to know?",placeholder="How many PPR points per game did Christian McCaffrey average in 2025?",height=105)
    if st.button("Ask Shiva",type="primary",use_container_width=True) and question.strip():
        with st.spinner("Analyzing verified app data…"): answer=ask_shiva(question.strip())
        st.session_state.ask_history.insert(0,(question.strip(),answer))
    for q,a in st.session_state.ask_history[:6]: st.markdown(f"**{html.escape(q)}**"); st.markdown(f'<div class="answer">{html.escape(a)}</div>',unsafe_allow_html=True); st.write("")

st.caption("Shiva Fantasy Football · mobile-first · 2026 ranking feed + verified 2014–2025 weekly player history.")