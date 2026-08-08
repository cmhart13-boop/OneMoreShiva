from __future__ import annotations

import hashlib
import html
import os
import random
import re
from typing import Any
from urllib.parse import quote_plus

from shiva_ppr_2026 import DRAFT_RULES, player_payload, shiva_context

import numpy as np
import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(page_title="Shiva Fantasy Football", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

RANKINGS_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/current_rankings.csv"
WEEKLY_URL = "https://raw.githubusercontent.com/cmhart13-boop/Draft-Coach/main/player_weekly_master_2014_2025.csv.gz"
DEFAULT_TEAMS = 10
DEFAULT_ROUNDS = 15
ROSTER_SLOTS = ["QB","RB","RB","WR","WR","TE","FLEX","DST","K","BE","BE","BE","BE","BE","BE"]
PAGES = ["Home","Draft","Players","Shiva","Roster"]
ICONS = {"Home":"⌂","Draft":"🏈","Players":"👥","Shiva":"✦","Roster":"☷"}

CSS = r'''<style>
:root{--bg:#071018;--surface:#0e1821;--surface2:#14212d;--line:#22313f;--text:#f6f9fb;--muted:#8fa0ae;--accent:#ec1738;--lime:#d9ff38;--teal:#74e3d2;--teal-dark:#092c2a;--green:#2acb74;--qb:#7257d8;--rb:#19a89d;--wr:#347fd9;--te:#e88135;--dst:#d1b23c;--k:#687886;--nav-h:76px}
html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.stApp{background:var(--bg);color:var(--text)}.block-container{max-width:1120px;padding:.35rem .55rem calc(var(--nav-h) + 1.2rem)!important}#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"],[data-testid="stDecoration"],[data-testid="stHeader"],[data-testid="stMainMenu"],[data-testid="stToolbarActions"],[data-testid="stHeaderActionElements"],div[class*="viewerBadge"],div[class*="ViewerBadge"],div[class*="statusWidget"],div[class*="StatusWidget"],button[title*="Manage app"],button[aria-label*="Manage app"]{display:none!important;visibility:hidden!important;height:0!important;width:0!important;min-height:0!important;min-width:0!important;overflow:hidden!important;pointer-events:none!important}
.app-top{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:5px 2px 10px}.brand-wrap{display:flex;align-items:center;gap:9px}.brand-badge{width:39px;height:39px;border-radius:12px;background:linear-gradient(135deg,#ff3151,#9f071f);display:flex;align-items:center;justify-content:center;font-size:21px}.brand-title{font-size:19px;font-weight:950;letter-spacing:-.5px}.brand-sub{font-size:9px;color:var(--muted);font-weight:800;letter-spacing:.9px;text-transform:uppercase}.data-status{font-size:9px;font-weight:900;color:#74e6a8;border:1px solid #24543d;background:#0b2016;padding:6px 8px;border-radius:999px;white-space:nowrap}
.screen-head{margin:2px 0 10px}.screen-head h1{font-size:24px;line-height:1.05;margin:0;color:#fff;letter-spacing:-.8px}.screen-head p{font-size:11px;color:var(--muted);margin:4px 0 0}.bottom-nav{position:fixed;left:0;right:0;bottom:0;height:var(--nav-h);z-index:9999;background:rgba(8,15,22,.97);backdrop-filter:blur(16px);border-top:1px solid #263440;display:grid;grid-template-columns:repeat(5,1fr);padding:6px 8px calc(8px + env(safe-area-inset-bottom));box-shadow:0 -8px 28px rgba(0,0,0,.35)}.bottom-nav a{color:#8495a3!important;text-decoration:none!important;text-align:center;font-size:10px;font-weight:800;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:13px;min-height:58px;gap:2px}.bottom-nav a.active{color:#fff!important;background:#172430}.nav-icon{font-size:22px;line-height:1}
.stButton>button{min-height:50px!important;border-radius:12px!important;font-weight:900!important;font-size:13px!important;border:1px solid #2b3a47!important}.stButton>button[kind="primary"]{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important}.stTextInput input,.stTextArea textarea{min-height:48px!important;border-radius:12px!important}.stSelectbox [data-baseweb="select"]>div{min-height:48px!important;border-radius:12px!important}div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:6px!important;width:100%!important}div[role="radiogroup"] label{min-height:46px;background:#0e1821;border:1px solid var(--line);border-radius:11px;padding:6px!important;justify-content:center!important;margin:0!important}div[role="radiogroup"] label:has(input:checked){background:#1d2c39;border-color:#506272}div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;font-weight:900!important;white-space:nowrap!important}
.hero-card{background:linear-gradient(135deg,#142433,#0a1118 62%);border:1px solid #243645;border-radius:18px;padding:16px;margin-bottom:10px;overflow:hidden;position:relative}.hero-card:after{content:"🏆";position:absolute;right:-5px;top:2px;font-size:88px;opacity:.08;transform:rotate(10deg)}.hero-kicker{color:var(--lime);font-size:10px;font-weight:950;text-transform:uppercase;letter-spacing:1px}.hero-card h2{font-size:26px;line-height:1.02;margin:5px 0;color:#fff;max-width:82%;letter-spacing:-.8px}.hero-card p{font-size:11px;color:#a6b3bd;margin:0;max-width:84%}.stat-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px 0 12px}.mini-stat{background:#0e1821;border:1px solid var(--line);border-radius:12px;padding:9px 7px;text-align:center}.mini-stat b{display:block;font-size:16px}.mini-stat b small{font-size:11px;margin-left:4px;font-weight:950}.consistency-green{color:#2acb74}.consistency-yellow{color:#ffd34d}.consistency-red{color:#ff5b69}.mini-stat span{font-size:8px;color:var(--muted);text-transform:uppercase;font-weight:850}.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0 12px}.quick-card{display:block;text-decoration:none!important;color:#fff!important;background:#111d27;border:1px solid #263745;border-radius:14px;padding:13px;min-height:82px}.quick-icon{font-size:21px}.quick-title{font-size:13px;font-weight:900;margin-top:3px}.quick-sub{font-size:9px;color:var(--muted);margin-top:2px}
.player-shell{display:grid;grid-template-columns:44px minmax(0,1fr) 48px 48px;gap:7px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:7px 9px;margin-bottom:5px;min-height:61px}.player-shell.draft-player{grid-template-columns:44px minmax(0,1fr) 45px 45px 64px}.player-rank{width:35px;height:35px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#1a2732;font-weight:950;font-size:12px;color:#dbe4ea}.player-name{display:block;color:#fff!important;text-decoration:none!important;font-size:14px;font-weight:950;line-height:1.12;padding:3px 0}.player-name:active{color:var(--lime)!important}.player-meta{font-size:9px;color:var(--muted);margin-top:2px}.data-cell{text-align:center}.data-cell span{display:block;font-size:7px;color:var(--muted);font-weight:850;text-transform:uppercase}.data-cell b{font-size:11px}.pos{display:inline-flex;align-items:center;justify-content:center;border-radius:5px;padding:2px 5px;min-width:28px;font-size:8px;font-weight:950;color:#fff}.pos-QB{background:var(--qb)}.pos-RB{background:var(--rb)}.pos-WR{background:var(--wr)}.pos-TE{background:var(--te)}.pos-DST{background:var(--dst);color:#111}.pos-K{background:var(--k)}.draft-inline{display:flex!important;align-items:center;justify-content:center;min-height:38px;padding:0 10px;border-radius:10px;background:var(--teal);border:1px solid #9af0e4;color:var(--teal-dark)!important;text-decoration:none!important;font-size:10px;font-weight:950;box-shadow:0 2px 8px rgba(116,227,210,.12)}.draft-inline:active{transform:scale(.97);background:#9af0e4}.draft-inline.disabled{opacity:.4;pointer-events:none}
.draft-status{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:5px 0 9px}.draft-chip{background:#111d27;border:1px solid var(--line);border-radius:11px;padding:8px;text-align:center}.draft-chip span{font-size:7px;color:var(--muted);font-weight:850;text-transform:uppercase;display:block}.draft-chip b{font-size:14px}.on-clock{background:linear-gradient(90deg,#801024,#c41131);border:1px solid #ef3150;border-radius:12px;padding:10px 12px;margin:6px 0 9px;font-size:12px;font-weight:900}
.board-note{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:8px 1px 7px;color:#8fa0ae;font-size:9px;font-weight:800}.board-note b{color:#d7e1e8}.board-shell{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:thin;padding:1px 1px 8px;margin:0 -1px 3px;overscroll-behavior-x:contain}.draft-board{min-width:max-content}.board-row{display:grid;grid-template-columns:repeat(var(--teams),104px);gap:5px;margin-bottom:5px}.board-cell{height:88px;border:1px solid #2a3946;border-radius:9px;background:#0c141b;padding:7px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}.board-cell.empty{background:#091016;border-color:#25313b}.board-cell.mine{box-shadow:inset 0 0 0 1px rgba(116,227,210,.34)}.board-cell.QB{background:rgba(114,87,216,.17);border-color:rgba(140,117,224,.48)}.board-cell.RB{background:rgba(25,168,157,.16);border-color:rgba(52,196,184,.48)}.board-cell.WR{background:rgba(52,127,217,.16);border-color:rgba(73,151,238,.48)}.board-cell.TE{background:rgba(232,129,53,.15);border-color:rgba(243,151,83,.48)}.board-cell.DST{background:rgba(209,178,60,.13);border-color:rgba(220,193,83,.46)}.board-cell.K{background:rgba(104,120,134,.16);border-color:rgba(135,151,164,.42)}.board-cell.clock{background:linear-gradient(145deg,#133c39,#0b2927);border-color:#74e3d2;box-shadow:0 0 0 1px rgba(116,227,210,.2),0 5px 16px rgba(0,0,0,.18)}.board-pick{font-size:9px;color:#8fa0ae;font-weight:850;letter-spacing:.2px}.board-cell.clock .board-pick{color:#a9eee5}.board-name{font-size:12px;color:#f8fbfd;font-weight:950;line-height:1.06;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.board-meta{font-size:9px;color:#9cacb7;display:flex;align-items:center;gap:4px}.board-pos{display:inline-flex;align-items:center;justify-content:center;border-radius:5px;padding:2px 5px;color:#fff;font-size:8px;font-weight:950}.board-pos.QB{background:var(--qb)}.board-pos.RB{background:var(--rb)}.board-pos.WR{background:var(--wr)}.board-pos.TE{background:var(--te)}.board-pos.DST{background:var(--dst);color:#111}.board-pos.K{background:var(--k)}.clock-title{font-size:12px;font-weight:950;color:#fff;line-height:1.05}.clock-sub{font-size:8px;color:#a9eee5;font-weight:850;text-transform:uppercase;letter-spacing:.5px}.pick-card{border:1px solid var(--line);border-radius:11px;padding:9px 10px;background:#101a23;display:grid;grid-template-columns:43px minmax(0,1fr) auto;gap:8px;align-items:center;margin-bottom:5px}.pick-num{font-size:10px;color:#92a0ab;font-weight:850}.pick-card .nm{font-size:12px;font-weight:950}.pick-card .mt{font-size:9px;color:#a0adb7}.pick-empty{opacity:.55}
.profile-hero{background:linear-gradient(140deg,#172735,#0b131a);border:1px solid #294054;border-radius:18px;padding:15px;margin-top:5px}.profile-back{font-size:11px;color:#c7d1d9!important;text-decoration:none!important;font-weight:850}.profile-name-big{font-size:27px;font-weight:980;letter-spacing:-1px;margin:8px 0 2px}.profile-sub{font-size:10px;color:var(--muted)}.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px}.profile-metric{background:#0c151d;border:1px solid #243745;border-radius:11px;padding:9px}.profile-metric b{font-size:16px;display:block}.profile-metric span{font-size:8px;color:var(--muted);text-transform:uppercase;font-weight:850}.weekly-card{display:grid;grid-template-columns:42px 48px 54px minmax(0,1fr);gap:6px;align-items:center;background:#0e1821;border:1px solid var(--line);border-radius:11px;padding:8px;margin-bottom:5px}.weekly-card .wk{font-size:11px;font-weight:950}.weekly-card .opp{font-size:10px;color:#a5b1bb}.weekly-card .pts{font-size:14px;font-weight:950;color:#54ddea}.weekly-card .detail{font-size:9px;color:#9aa8b4;text-align:right}.roster-slot{display:grid;grid-template-columns:45px minmax(0,1fr) auto;gap:8px;align-items:center;padding:10px;background:#0e1821;border:1px solid var(--line);border-radius:11px;margin-bottom:5px}.slot-tag{font-size:9px;font-weight:950;color:#81919e}.slot-player{font-size:12px;font-weight:900}.slot-meta{font-size:9px;color:var(--muted)}.shiva-box{background:linear-gradient(145deg,#151f2a,#0c1218);border:1px solid #2c3a47;border-radius:17px;padding:15px;margin-bottom:10px}.shiva-box h2{font-size:23px;margin:0}.shiva-box p{font-size:11px;color:var(--muted);margin:4px 0 0}.answer{background:#101a22;border-left:3px solid var(--accent);border-radius:0 12px 12px 0;padding:12px 13px;line-height:1.5}
@media(min-width:760px){.block-container{padding-left:1rem!important;padding-right:1rem!important}.bottom-nav{left:50%;transform:translateX(-50%);max-width:620px;border:1px solid #263440;border-bottom:0;border-radius:18px 18px 0 0}.player-shell{grid-template-columns:48px minmax(0,1fr) 70px 70px 60px}.player-shell.draft-player{grid-template-columns:48px minmax(0,1fr) 70px 70px 60px 74px}.bye-desktop{display:block!important}.profile-grid{grid-template-columns:repeat(4,1fr)}.board-row{grid-template-columns:repeat(var(--teams),112px)}.board-cell{height:92px}}
@media(max-width:759px){.bye-desktop{display:none!important}.brand-sub{display:none}.data-status{font-size:8px}.screen-head h1{font-size:22px}[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.4rem!important}[data-testid="stHorizontalBlock"]>[data-testid="column"]{min-width:145px!important;flex:1 1 145px!important}[data-testid="stDataFrame"]{font-size:10px!important}.player-shell{min-height:58px;padding:6px 8px}.player-shell.draft-player{grid-template-columns:40px minmax(0,1fr) 42px 42px 62px;gap:5px}.player-rank{width:32px;height:32px}.draft-inline{min-height:36px;padding:0 7px;font-size:10px}.board-shell{margin-left:-.55rem;margin-right:-.55rem;padding-left:.55rem;padding-right:.55rem}.board-row{grid-template-columns:repeat(var(--teams),102px)}.board-cell{height:86px;padding:6px}.board-name{font-size:11px}}
</style>'''
st.markdown(CSS, unsafe_allow_html=True)


def stable_id(name:str)->str:return hashlib.md5(str(name).encode()).hexdigest()[:12]
def name_key(v:str)->str:return re.sub(r"[^a-z0-9]+","",str(v).casefold())
def safe_num(v:Any)->float:
    try:return float(v) if pd.notna(v) else np.nan
    except Exception:return np.nan
def fmt_num(v:Any,d:int=1)->str:
    n=safe_num(v);return f"{n:.{d}f}" if pd.notna(n) else "—"
def fmt_int(v:Any)->str:
    n=safe_num(v);return str(int(round(n))) if pd.notna(n) else "—"
def pos_badge(pos:str)->str:
    p=str(pos).upper().replace("D/ST","DST").replace("DEF","DST");return f'<span class="pos pos-{p}">{p}</span>'

@st.cache_data(ttl=1800,show_spinner=False)
def load_rankings()->tuple[pd.DataFrame,str]:
    try:
        df=pd.read_csv(RANKINGS_URL).rename(columns={"player_name":"name","position":"pos"})
        if not {"name","pos","team"}.issubset(df.columns):raise ValueError("ranking feed missing fields")
        df["name"]=df["name"].astype(str).str.strip();df["pos"]=df["pos"].astype(str).str.upper().replace({"DEF":"DST","D/ST":"DST"});df["team"]=df["team"].fillna("FA").astype(str).str.upper()
        for c in ("adp","consensus_adp","overall_rank","position_rank","bye"):df[c]=pd.to_numeric(df[c],errors="coerce") if c in df.columns else np.nan
        df["draft_adp"]=df["consensus_adp"].fillna(df["adp"]).fillna(df["overall_rank"]);df["overall_rank"]=df["overall_rank"].fillna(df["draft_adp"]);df["id"]=df["name"].map(stable_id)
        return df.drop_duplicates("id").sort_values(["overall_rank","draft_adp","name"],na_position="last").reset_index(drop=True),"CONNECTED"
    except Exception as exc:
        d=pd.DataFrame([{"name":"Jahmyr Gibbs","pos":"RB","team":"DET","draft_adp":1.0,"overall_rank":1,"position_rank":1,"bye":6},{"name":"Bijan Robinson","pos":"RB","team":"ATL","draft_adp":2.0,"overall_rank":2,"position_rank":2,"bye":11},{"name":"Ja'Marr Chase","pos":"WR","team":"CIN","draft_adp":3.2,"overall_rank":3,"position_rank":1,"bye":6},{"name":"Puka Nacua","pos":"WR","team":"LAR","draft_adp":3.8,"overall_rank":4,"position_rank":2,"bye":11}]);d["id"]=d["name"].map(stable_id);return d,f"FALLBACK: {exc}"

WEEKLY_COLUMNS={"player_id","player_display_name","player_name","name","position","recent_team","team","season","season_type","week","opponent_team","opponent","fantasy_points_ppr","fantasy_points","passing_yards","passing_tds","interceptions","rushing_yards","rushing_tds","carries","targets","receptions","receiving_yards","receiving_tds","fumbles_lost","passing_two_point_conversions","rushing_two_point_conversions","receiving_two_point_conversions"}
@st.cache_data(ttl=21600,show_spinner=False)
def load_weekly()->pd.DataFrame:
    df=pd.read_csv(WEEKLY_URL,compression="gzip",low_memory=False,usecols=lambda c:c in WEEKLY_COLUMNS)
    nonnum={"player_id","player_display_name","player_name","name","position","recent_team","team","season_type","opponent_team","opponent"}
    for c in WEEKLY_COLUMNS-nonnum:
        if c in df.columns:df[c]=pd.to_numeric(df[c],errors="coerce")
    if "season_type" in df.columns:
        m=df["season_type"].astype(str).str.upper().isin(["REG","REGULAR","REGULAR SEASON"])
        if m.any():df=df.loc[m].copy()
    if "week" in df.columns:df=df.loc[df["week"].between(1,18,inclusive="both")].copy()
    return df

def weekly_name_col(df:pd.DataFrame)->str|None:return next((c for c in ("player_display_name","player_name","name") if c in df.columns),None)
def weekly_for_player(weekly:pd.DataFrame,name:str)->pd.DataFrame:
    if weekly.empty:return pd.DataFrame()
    nc=weekly_name_col(weekly)
    if not nc:return pd.DataFrame()
    out=weekly.loc[weekly[nc].astype(str).map(name_key).eq(name_key(name))].copy()
    if out.empty:
        last=name_key(str(name).split()[-1])
        if len(last)>=5:
            mask=weekly[nc].astype(str).map(name_key).str.endswith(last);names=weekly.loc[mask,nc].dropna().astype(str).unique().tolist()
            if len(names)==1:out=weekly.loc[mask].copy()
    cols=[c for c in ("season","week") if c in out.columns];return out.sort_values(cols) if cols and not out.empty else out

def espn_ppr(frame:pd.DataFrame)->pd.Series:
    if frame.empty:return pd.Series(dtype=float)
    if "fantasy_points_ppr" in frame.columns:
        s=pd.to_numeric(frame["fantasy_points_ppr"],errors="coerce")
        if s.notna().any():return s.round(2)
    scoring={"passing_yards":.04,"passing_tds":4,"interceptions":-2,"rushing_yards":.1,"rushing_tds":6,"receptions":1,"receiving_yards":.1,"receiving_tds":6,"fumbles_lost":-2,"passing_two_point_conversions":2,"rushing_two_point_conversions":2,"receiving_two_point_conversions":2}
    total=pd.Series(0.0,index=frame.index);used=False
    for c,m in scoring.items():
        if c in frame.columns:total+=pd.to_numeric(frame[c],errors="coerce").fillna(0)*m;used=True
    return total.round(2) if used else pd.to_numeric(frame.get("fantasy_points"),errors="coerce")

players,rankings_status=load_rankings()

def init_state():
    defaults={"draft_log":[],"queue":[],"user_slot":3,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[]}
    for k,v in defaults.items():
        if k not in st.session_state:st.session_state[k]=v.copy() if isinstance(v,list) else v
init_state()
def pick_team(n:int,t:int)->int:
    r=(n-1)//t+1;w=(n-1)%t+1;return w if r%2 else t-w+1
def drafted_ids()->set[str]:return {x["id"] for x in st.session_state.draft_log}
def available_df()->pd.DataFrame:return players.loc[~players["id"].isin(drafted_ids())].copy().sort_values(["draft_adp","overall_rank"],na_position="last")
def next_pick()->int:return len(st.session_state.draft_log)+1
def record_pick(pid:str,team:int):
    if pid in drafted_ids():return
    m=players.loc[players["id"].eq(pid)]
    if m.empty:return
    r=m.iloc[0];n=next_pick();st.session_state.draft_log.append({"pick":n,"round":(n-1)//st.session_state.team_count+1,"team":team,"id":str(r["id"]),"name":str(r["name"]),"pos":str(r["pos"]),"nfl_team":str(r["team"])})
    if pid in st.session_state.queue:st.session_state.queue.remove(pid)
def cpu_pick():
    pool=available_df().head(18)
    if pool.empty:return
    n=next_pick();idx=min(len(pool)-1,max(0,int(abs(random.Random(41000+n).gauss(.9,1.15)))));record_pick(str(pool.iloc[idx]["id"]),pick_team(n,st.session_state.team_count))
def sim_to_user():
    total=st.session_state.team_count*st.session_state.rounds;guard=0
    while next_pick()<=total and pick_team(next_pick(),st.session_state.team_count)!=st.session_state.user_slot:
        before=next_pick();cpu_pick();guard+=1
        if next_pick()==before or guard>total:break
def draft_user(pid:str):
    sim_to_user()
    if pick_team(next_pick(),st.session_state.team_count)==st.session_state.user_slot:record_pick(pid,st.session_state.user_slot);sim_to_user()
def user_roster()->pd.DataFrame:return pd.DataFrame([x for x in st.session_state.draft_log if x["team"]==st.session_state.user_slot])
def page_href(page:str)->str:return f"?page={quote_plus(page)}"
def profile_href(r:pd.Series,ret:str)->str:return f"?player={quote_plus(str(r['id']))}&name={quote_plus(str(r['name']))}&return={quote_plus(ret)}"
def draft_href(pid:str)->str:return f"?page=Draft&draft={quote_plus(pid)}"

def app_header():
    live=rankings_status=="CONNECTED";st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">🏆</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div><div class="data-status">● {"DATA LIVE" if live else "DATA FALLBACK"}</div></div>',unsafe_allow_html=True)
def bottom_nav(active:str):
    links=''.join(f'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self"><span class="nav-icon">{ICONS[p]}</span><span>{p}</span></a>' for p in PAGES);st.markdown(f'<nav class="bottom-nav">{links}</nav>',unsafe_allow_html=True)
def screen_head(t:str,s:str=""):st.markdown(f'<div class="screen-head"><h1>{html.escape(t)}</h1><p>{html.escape(s)}</p></div>',unsafe_allow_html=True)
def player_card(r:pd.Series,ret:str,draft_action:bool=False):
    draft_button=f'<a class="draft-inline" href="{draft_href(str(r["id"]))}" target="_self">Draft</a>' if draft_action else ''
    shell_class='player-shell draft-player' if draft_action else 'player-shell'
    st.markdown(f'<div class="{shell_class}"><div class="player-rank">{fmt_int(r.get("overall_rank"))}</div><div><a class="player-name" href="{profile_href(r,ret)}" target="_self">{html.escape(str(r["name"]))}</a><div class="player-meta">{pos_badge(r["pos"])}&nbsp; {html.escape(str(r["team"]))}</div></div><div class="data-cell"><span>ADP</span><b>{fmt_num(r.get("draft_adp"))}</b></div><div class="data-cell"><span>POS</span><b>{html.escape(str(r["pos"]))}{fmt_int(r.get("position_rank"))}</b></div><div class="data-cell bye-desktop"><span>BYE</span><b>{fmt_int(r.get("bye"))}</b></div>{draft_button}</div>',unsafe_allow_html=True)
def render_players(df:pd.DataFrame,ret:str,action:str="none",limit:int=80):
    if df.empty:st.info("No players match this view.");return
    for _,r in df.head(limit).iterrows():
        pid=str(r["id"])
        if action=="draft":player_card(r,ret,draft_action=True)
        else:player_card(r,ret)
        if action=="remove":
            if st.button(f'Remove {r["name"]} from Queue',key=f'r_{pid}',use_container_width=True):
                if pid in st.session_state.queue:st.session_state.queue.remove(pid)
                st.rerun()

def assign_slots(roster:pd.DataFrame):
    rem=roster.to_dict("records") if not roster.empty else [];out=[]
    for slot in ROSTER_SLOTS:
        idx=None
        for i,p in enumerate(rem):
            pos=str(p["pos"]).replace("D/ST","DST")
            if slot==pos or (slot=="FLEX" and pos in {"RB","WR","TE"}):idx=i;break
        if idx is None and slot=="BE" and rem:idx=0
        out.append((slot,rem.pop(idx) if idx is not None else None))
    return out
def render_roster():
    for slot,p in assign_slots(user_roster()):
        if p:st.markdown(f'<div class="roster-slot"><div class="slot-tag">{slot}</div><div><div class="slot-player">{html.escape(str(p["name"]))}</div><div class="slot-meta">{p["pos"]} · {p["nfl_team"]}</div></div><div class="slot-meta">Pick {p["pick"]}</div></div>',unsafe_allow_html=True)
        else:st.markdown(f'<div class="roster-slot"><div class="slot-tag">{slot}</div><div class="slot-player" style="color:#637381">Empty</div><div></div></div>',unsafe_allow_html=True)
def render_draft_board():
    team_count=st.session_state.team_count;rounds=st.session_state.rounds;current=next_pick();total=team_count*rounds;pick_map={int(x["pick"]):x for x in st.session_state.draft_log}
    rows=[]
    for round_no in range(1,rounds+1):
        cells=[]
        start=(round_no-1)*team_count+1
        for pn in range(start,start+team_count):
            team=pick_team(pn,team_count);pick_label=f"{round_no}.{team}";mine=" mine" if team==st.session_state.user_slot else "";p=pick_map.get(pn)
            if p:
                pos=str(p["pos"]).upper().replace("D/ST","DST").replace("DEF","DST");name=html.escape(str(p["name"]));nfl=html.escape(str(p["nfl_team"]))
                cells.append(f'<div class="board-cell {pos}{mine}"><div class="board-pick">{pick_label}</div><div class="board-name">{name}</div><div class="board-meta">{nfl}<span class="board-pos {pos}">{pos}</span></div></div>')
            elif pn==current and current<=total:
                cells.append(f'<div class="board-cell clock{mine}"><div class="board-pick">{pick_label}</div><div><div class="clock-title">On the Clock</div><div class="clock-sub">{"Your pick" if team==st.session_state.user_slot else f"Team {team}"}</div></div><div class="board-meta">Pick {pn}</div></div>')
            else:
                cells.append(f'<div class="board-cell empty{mine}"><div class="board-pick">{pick_label}</div><div class="board-name" style="color:#44535f">—</div><div class="board-meta">Team {team}</div></div>')
        rows.append(f'<div class="board-row" style="--teams:{team_count}">{"".join(cells)}</div>')
    st.markdown(f'<div class="board-note"><span><b>Draft Board</b> · {team_count}-team snake</span><span>Swipe ↔</span></div><div class="board-shell"><div class="draft-board">{"".join(rows)}</div></div>',unsafe_allow_html=True)
def summary(f:pd.DataFrame):
    pts=espn_ppr(f).dropna();games=len(pts);weeks15=int((pts>=15).sum()) if games else 0;return {"games":games,"total":float(pts.sum()) if games else np.nan,"ppg":float(pts.mean()) if games else np.nan,"weeks15":weeks15,"rate15":round((weeks15/games)*100) if games else 0}

def render_profile(pid:str,hint:str,ret:str):
    m=players.loc[players["id"].astype(str).eq(pid)]
    if m.empty and hint:m=players.loc[players["name"].astype(str).map(name_key).eq(name_key(hint))]
    if m.empty:st.error("Player not found.");return
    p=m.iloc[0];back=ret if ret in PAGES else "Players";st.markdown(f'<a class="profile-back" href="{page_href(back)}" target="_self">← Back to {back}</a>',unsafe_allow_html=True)
    try:pf=weekly_for_player(load_weekly(),str(p["name"]))
    except Exception as exc:st.error(f"Historical data could not be loaded: {exc}");pf=pd.DataFrame()
    seasons=sorted(pd.to_numeric(pf.get("season",pd.Series(dtype=float)),errors="coerce").dropna().astype(int).unique().tolist(),reverse=True)
    st.markdown(f'<div class="profile-hero"><div>{pos_badge(p["pos"])}</div><div class="profile-name-big">{html.escape(str(p["name"]))}</div><div class="profile-sub">{p["team"]} · 2026 ADP {fmt_num(p.get("draft_adp"))} · Overall #{fmt_int(p.get("overall_rank"))}</div><div class="profile-grid"><div class="profile-metric"><b>{fmt_num(p.get("draft_adp"))}</b><span>2026 ADP</span></div><div class="profile-metric"><b>{p["pos"]}{fmt_int(p.get("position_rank"))}</b><span>Position Rank</span></div><div class="profile-metric"><b>{len(seasons)}</b><span>Seasons</span></div><div class="profile-metric"><b>{fmt_int(p.get("bye"))}</b><span>Bye Week</span></div></div></div>',unsafe_allow_html=True)
    if pf.empty:st.info("No NFL weekly history is available yet for this player.");return
    yr=st.selectbox("Season",seasons,key=f's_{pid}');sf=pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(int(yr))].copy();sm=summary(sf)
    rate15=int(sm["rate15"]);rate15_class="consistency-green" if rate15>=50 else "consistency-yellow" if rate15>=25 else "consistency-red"
    st.markdown(f'<div class="stat-strip"><div class="mini-stat"><b>{fmt_num(sm["ppg"])}</b><span>PPR PPG</span></div><div class="mini-stat"><b>{fmt_num(sm["total"])}</b><span>Total</span></div><div class="mini-stat"><b>{sm["games"]}</b><span>Games</span></div><div class="mini-stat"><b>{sm["weeks15"]}<small class="{rate15_class}">{rate15}%</small></b><span>15+ Weeks</span></div></div>',unsafe_allow_html=True)
    shiva_intel=player_payload(str(p["name"]))
    if any(v is not None for v in shiva_intel.values()):
        chips=[]
        if shiva_intel.get("rank"):chips.append(f'<span style="background:#172430;border:1px solid #344758;border-radius:999px;padding:4px 7px;font-size:9px;font-weight:900">PPR #{shiva_intel["rank"]}</span>')
        if shiva_intel.get("tag"):
            tc={"TARGET":"#2acb74","PASS":"#ffd34d","AVOID":"#ff5b69"}.get(shiva_intel["tag"],"#8fa0ae")
            chips.append(f'<span style="color:{tc};background:#101a22;border:1px solid #344758;border-radius:999px;padding:4px 7px;font-size:9px;font-weight:950">{shiva_intel["tag"]}</span>')
        if shiva_intel.get("adj_ppg") is not None:chips.append(f'<span style="background:#172430;border:1px solid #344758;border-radius:999px;padding:4px 7px;font-size:9px;font-weight:900">Adj PPG {shiva_intel["adj_ppg"]}</span>')
        if shiva_intel.get("ppr_rec_share") is not None:chips.append(f'<span style="background:#172430;border:1px solid #344758;border-radius:999px;padding:4px 7px;font-size:9px;font-weight:900">Rec Pts {shiva_intel["ppr_rec_share"]}%</span>')
        note=html.escape(shiva_intel.get("intel") or "")
        st.markdown(f'<div style="background:linear-gradient(135deg,#111d27,#0b141b);border:1px solid #2b4353;border-radius:14px;padding:11px 12px;margin:8px 0 10px"><div style="font-size:9px;color:#d9ff38;font-weight:950;letter-spacing:.8px;text-transform:uppercase;margin-bottom:7px">Shiva Draft Guide · 2026 PPR</div><div style="display:flex;gap:5px;flex-wrap:wrap">{"".join(chips)}</div>{f'<div style="font-size:11px;color:#dce5eb;line-height:1.35;margin-top:8px">{note}</div>' if note else ""}</div>',unsafe_allow_html=True)
    view=st.radio("Profile view",["Weekly","Career"],horizontal=True,label_visibility="collapsed",key=f'pv_{pid}')
    if view=="Weekly":
        sf["PPR"]=espn_ppr(sf)
        for _,r in sf.sort_values("week").iterrows():
            opp=html.escape(str(r.get("opponent_team") or r.get("opponent") or "—"));pos=str(p["pos"])
            detail=(f'{fmt_int(r.get("passing_yards"))} PY · {fmt_int(r.get("passing_tds"))} PTD · {fmt_int(r.get("rushing_yards"))} RY' if pos=="QB" else f'{fmt_int(r.get("carries"))} CAR · {fmt_int(r.get("rushing_yards"))} RY · {fmt_int(r.get("receptions"))} REC' if pos=="RB" else f'{fmt_int(r.get("targets"))} TGT · {fmt_int(r.get("receptions"))} REC · {fmt_int(r.get("receiving_yards"))} YDS')
            st.markdown(f'<div class="weekly-card"><div class="wk">WK {fmt_int(r.get("week"))}</div><div class="opp">{opp}</div><div class="pts">{fmt_num(r.get("PPR"))}</div><div class="detail">{detail}</div></div>',unsafe_allow_html=True)
    else:
        rows=[]
        for y in seasons:
            s=summary(pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(y)]);rows.append({"Season":y,"Games":s["games"],"PPR":round(s["total"],1),"PPG":round(s["ppg"],1),"15+":s["weeks15"],"15+ %":f'{int(s["rate15"])}%'})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

def ask_shiva(question:str)->str:
    qkey=name_key(question);names=[n for n in players["name"].astype(str) if name_key(n) in qkey][:4];history=[]
    shiva_draft_context=shiva_context(names)
    if names:
        try:
            w=load_weekly()
            for n in names:
                pf=weekly_for_player(w,n);yrs=sorted(pd.to_numeric(pf.get("season"),errors="coerce").dropna().astype(int).unique().tolist(),reverse=True)[:3]
                for y in yrs:
                    s=summary(pf.loc[pd.to_numeric(pf["season"],errors="coerce").eq(y)]);history.append(f'{n} {y}: {s["ppg"]:.2f} PPG, {s["total"]:.1f} total, {s["games"]} games')
        except Exception:pass
    key=None
    try:key=st.secrets.get("OPENAI_API_KEY")
    except Exception:pass
    key=key or os.getenv("OPENAI_API_KEY")
    if not key or OpenAI is None:return "Verified data:\n\n"+"\n".join(history) if history else "Add OPENAI_API_KEY in Streamlit Secrets to enable Shiva analysis."
    roster=user_roster();rt=", ".join(roster["name"].tolist()) if not roster.empty else "None";avail=available_df().head(35)[["name","pos","team","draft_adp"]].to_dict("records")
    system=f"You are Shiva, an elite fantasy football analyst. Default ESPN full 1-point PPR. Use supplied app data as authoritative and never invent stats. User roster: {rt}. Top available: {avail}. Historical context: {history}. Shiva Draft Guide 2026 full-PPR intelligence: {shiva_draft_context}. Shiva PPR strategy rules: {DRAFT_RULES}. Use this Shiva Draft Guide data as an internal draft-intelligence input, and do not treat Half-PPR or dynasty data as part of this context."
    try:return OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=[{"role":"system","content":system},{"role":"user","content":question}]).output_text
    except Exception as exc:return f"Shiva could not complete the request: {exc}"

def home():
    screen_head("Command Center","Everything important, one thumb away.");st.markdown('<div class="hero-card"><div class="hero-kicker">Draft Intelligence</div><h2>Build the team before the room knows what happened.</h2><p>Real rankings, full-PPR history, queue, draft board, roster and Shiva in one mobile workflow.</p></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="stat-strip"><div class="mini-stat"><b>{next_pick()}</b><span>Pick</span></div><div class="mini-stat"><b>#{st.session_state.user_slot}</b><span>Slot</span></div><div class="mini-stat"><b>{len(user_roster())}</b><span>Roster</span></div><div class="mini-stat"><b>{len(st.session_state.queue)}</b><span>Queue</span></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="quick-grid">'+f'<a class="quick-card" href="{page_href("Draft")}" target="_self"><div class="quick-icon">🏈</div><div class="quick-title">Draft Room</div><div class="quick-sub">Players, board, queue and roster</div></a>'+f'<a class="quick-card" href="{page_href("Shiva")}" target="_self"><div class="quick-icon">✦</div><div class="quick-title">Ask Shiva</div><div class="quick-sub">Draft and player intelligence</div></a>'+f'<a class="quick-card" href="{page_href("Players")}" target="_self"><div class="quick-icon">👥</div><div class="quick-title">Players</div><div class="quick-sub">Profiles and weekly history</div></a>'+f'<a class="quick-card" href="{page_href("Roster")}" target="_self"><div class="quick-icon">☷</div><div class="quick-title">My Roster</div><div class="quick-sub">Live construction by slot</div></a></div>',unsafe_allow_html=True)
    st.markdown("#### Top Available")
    for _,r in available_df().head(6).iterrows():player_card(r,"Home")
def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    if pick_team(n,st.session_state.team_count)==st.session_state.user_slot:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
    if view=="Players":
        q=st.text_input("Search players",placeholder="Search player or team…",key="ds");pos=st.selectbox("Position",["ALL","RB","WR","QB","TE","DST","K"],key="dp");pool=available_df()
        if q:q=q.casefold().strip();pool=pool.loc[pool["name"].str.casefold().str.contains(q,regex=False)|pool["team"].str.casefold().str.contains(q,regex=False)]
        if pos!="ALL":pool=pool.loc[pool["pos"].eq(pos)]
        render_players(pool,"Draft","draft",75)
    elif view=="Queue":
        qdf=players.loc[players["id"].isin(st.session_state.queue)&~players["id"].isin(drafted_ids())].copy();order={pid:i for i,pid in enumerate(st.session_state.queue)}
        if not qdf.empty:qdf["qorder"]=qdf["id"].map(order);qdf=qdf.sort_values("qorder")
        render_players(qdf,"Draft","remove",60)
    elif view=="Roster":render_roster()
    else:render_draft_board()
    if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
def player_db():
    screen_head("Players","Every player is a profile, not a dead row.");q=st.text_input("Search",placeholder="Search player or NFL team…",key="ps");pos=st.selectbox("Position filter",["ALL","RB","WR","QB","TE","DST","K"],key="pp");df=players.copy()
    if q:q=q.casefold().strip();df=df.loc[df["name"].str.casefold().str.contains(q,regex=False)|df["team"].str.casefold().str.contains(q,regex=False)]
    if pos!="ALL":df=df.loc[df["pos"].eq(pos)]
    render_players(df,"Players","none",150)
def shiva():
    screen_head("Ask Shiva","Your draft copilot uses the same player data as the app.");st.markdown('<div class="shiva-box"><h2>✦ Shiva Intelligence</h2><p>Ask about players, weekly production, roster construction or who to draft next.</p></div>',unsafe_allow_html=True);q=st.text_area("Question",placeholder="Who should I draft here and why?",height=110)
    if st.button("Ask Shiva",type="primary",use_container_width=True) and q.strip():
        with st.spinner("Analyzing your live draft context…"):a=ask_shiva(q.strip())
        st.session_state.ask_history.insert(0,(q.strip(),a))
    for q,a in st.session_state.ask_history[:6]:st.markdown(f"**{q}**");st.markdown(f'<div class="answer">{a}</div>',unsafe_allow_html=True);st.write("")
def roster_screen():
    screen_head("My Roster","Your live draft build, slot by slot.");r=user_roster();st.markdown(f'<div class="stat-strip"><div class="mini-stat"><b>{len(r)}</b><span>Drafted</span></div><div class="mini-stat"><b>{sum(r["pos"].eq("RB")) if not r.empty else 0}</b><span>RB</span></div><div class="mini-stat"><b>{sum(r["pos"].eq("WR")) if not r.empty else 0}</b><span>WR</span></div><div class="mini-stat"><b>{len(st.session_state.queue)}</b><span>Queue</span></div></div>',unsafe_allow_html=True);render_roster()

app_header();qp=st.query_params
# Inline draft links are handled before rendering. Clear the action immediately so a refresh cannot draft twice.
draft_param=str(qp.get("draft") or "")
if draft_param:
    draft_user(draft_param)
    st.query_params.clear();st.query_params["page"]="Draft";st.rerun()
pid=str(qp.get("player") or "");hint=str(qp.get("name") or "");ret=str(qp.get("return") or "Players")
if pid:render_profile(pid,hint,ret);bottom_nav(ret if ret in PAGES else "Players");st.stop()
page=str(qp.get("page") or "Home");page=page if page in PAGES else "Home"
{"Home":home,"Draft":draft,"Players":player_db,"Shiva":shiva,"Roster":roster_screen}[page]();bottom_nav(page)
