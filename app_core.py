from __future__ import annotations

import hashlib
import html
import os
from pathlib import Path
import random
import re
from typing import Any
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from shiva_draft_guide import render_draft_guide
from shiva_draft_iq import render_shiva_draft_iq
from shiva_coach import inject_css as inject_coach_css, render_season_hub, render_draft_moment
from shiva_product import render_full_product
from shiva_home_v2 import render_home_v2

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(page_title="One More Shiva", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

# Startup splash: initial app launch only. In-app/page-query navigation never replays it.
if not st.query_params.get("page") and not st.session_state.get("_shiva_startup_splash_seen", False):
    st.session_state["_shiva_startup_splash_seen"] = True
    try:
        import base64 as _splash_b64mod
        import time as _splash_time
        _splash_path = Path(__file__).with_name("1FB42328-2FEA-43AE-9BAC-D6BE96E58C93.jpeg")
        _splash_b64 = _splash_b64mod.b64encode(_splash_path.read_bytes()).decode("ascii")
        _splash_slot = st.empty()
        _splash_html = f"<style>.shiva-startup-splash{{position:fixed;inset:0;width:100vw;height:100dvh;z-index:2147483647;background:#081016;display:flex;align-items:center;justify-content:center;overflow:hidden}}.shiva-startup-splash img{{display:block;width:100%;height:100%;object-fit:cover;object-position:center center}}</style><div class='shiva-startup-splash'><img src='data:image/jpeg;base64,{_splash_b64}' alt='Shiva'></div>"
        _splash_slot.markdown(_splash_html, unsafe_allow_html=True)
        _splash_time.sleep(1.15)
        _splash_slot.empty()
    except Exception:
        pass
SHIVA_MARK = f"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,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" alt="THE SHIVA trophy">"""

RANKINGS_URL = str(Path(__file__).with_name("current_rankings.csv"))
WEEKLY_URL = str(Path(__file__).with_name("player_weekly_master_2014_2025.csv.gz"))
DEFAULT_TEAMS = 10
DEFAULT_ROUNDS = 15
ROSTER_SLOTS = ["QB","RB","RB","WR","WR","TE","FLEX","DST","K","BE","BE","BE","BE","BE","BE"]
PAGES = ["Home","Draft","Guide","Players","Shiva","Roster","Analytics","Coach"]
ICONS = {"Home":"⌂","Draft":"◫","Guide":"▤","Players":"👥","Shiva":"","Roster":"☷","Analytics":"▥","Coach":"✦"}

CSS = r'''<style>
:root{--bg:#071018;--surface:#0e1821;--surface2:#14212d;--line:#22313f;--text:#f6f9fb;--muted:#8fa0ae;--accent:#ec1738;--lime:#d9ff38;--teal:#74e3d2;--teal-dark:#092c2a;--green:#2acb74;--qb:#7257d8;--rb:#19a89d;--wr:#347fd9;--te:#e88135;--dst:#d1b23c;--k:#687886;--nav-h:76px}
html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}html,body{background:#071019!important;color-scheme:dark!important}.stApp{background:var(--bg);color:var(--text)}.block-container{max-width:1120px;padding:0 .55rem calc(var(--nav-h) + 1.2rem)!important}#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden;height:0}
.app-top{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:0 2px 7px}.brand-wrap{display:flex;align-items:center;gap:11px}.brand-badge{width:58px;height:58px;border-radius:0;background:transparent;display:flex;align-items:center;justify-content:center;font-size:21px;overflow:visible}.brand-title{font-size:27px;font-weight:950;letter-spacing:-.7px;line-height:1}.brand-sub{font-size:12.5px;color:var(--muted);font-weight:800;letter-spacing:.75px;text-transform:uppercase;margin-top:4px}.data-status{font-size:9px;font-weight:900;color:#74e6a8;border:1px solid #24543d;background:#0b2016;padding:6px 8px;border-radius:999px;white-space:nowrap}
.screen-head{margin:2px 0 10px}.screen-head h1{font-size:24px;line-height:1.05;margin:0;color:#fff;letter-spacing:-.8px}.screen-head p{font-size:11px;color:var(--muted);margin:4px 0 0}.bottom-nav{position:fixed;left:0;right:0;bottom:0;height:var(--nav-h);z-index:9999;background:rgba(8,15,22,.97);backdrop-filter:blur(16px);border-top:1px solid #263440;display:grid;grid-template-columns:repeat(4,1fr);padding:6px 8px calc(8px + env(safe-area-inset-bottom));box-shadow:0 -8px 28px rgba(0,0,0,.35)}.bottom-nav a{color:#8495a3!important;text-decoration:none!important;text-align:center;font-size:10px;font-weight:800;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:13px;min-height:58px;gap:2px}.bottom-nav a.active{color:#fff!important;background:#172430}.nav-icon{font-size:22px;line-height:1}
.stButton>button{min-height:50px!important;border-radius:12px!important;font-weight:900!important;font-size:13px!important;border:1px solid #2b3a47!important}.stButton>button[kind="primary"]{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important}.stTextInput input,.stTextArea textarea{min-height:48px!important;border-radius:12px!important}.stSelectbox [data-baseweb="select"]>div{min-height:48px!important;border-radius:12px!important}div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:6px!important;width:100%!important}div[role="radiogroup"] label{min-height:46px;background:#0e1821;border:1px solid var(--line);border-radius:11px;padding:6px!important;justify-content:center!important;margin:0!important}div[role="radiogroup"] label:has(input:checked){background:#1d2c39;border-color:#506272}div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;font-weight:900!important;white-space:nowrap!important}
.hero-card{background:linear-gradient(135deg,#142433,#0a1118 62%);border:1px solid #243645;border-radius:18px;padding:16px;margin-bottom:10px;overflow:hidden;position:relative}.hero-card:after{content:none!important;display:none!important}.hero-kicker{color:var(--lime);font-size:10px;font-weight:950;text-transform:uppercase;letter-spacing:1px}.hero-card h2{font-size:26px;line-height:1.02;margin:5px 0;color:#fff;max-width:82%;letter-spacing:-.8px}.hero-card p{font-size:11px;color:#a6b3bd;margin:0;max-width:84%}.stat-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px 0 12px}.mini-stat{background:#0e1821;border:1px solid var(--line);border-radius:12px;padding:9px 7px;text-align:center}.mini-stat b{display:block;font-size:16px}.mini-stat b small{font-size:11px;margin-left:4px;font-weight:950}.consistency-green{color:#2acb74}.consistency-yellow{color:#ffd34d}.consistency-red{color:#ff5b69}.mini-stat span{font-size:8px;color:var(--muted);text-transform:uppercase;font-weight:850}.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0 12px}.quick-card{display:block;text-decoration:none!important;color:#fff!important;background:#111d27;border:1px solid #263745;border-radius:14px;padding:13px;min-height:82px}.quick-icon{font-size:21px}.quick-title{font-size:13px;font-weight:900;margin-top:3px}.quick-sub{font-size:9px;color:var(--muted);margin-top:2px}
.player-shell{display:grid;grid-template-columns:44px minmax(0,1fr) 48px 48px;gap:7px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:7px 9px;margin-bottom:5px;min-height:61px}.player-shell.draft-player{grid-template-columns:44px minmax(0,1fr) 45px 45px 64px}.player-rank{width:35px;height:35px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#1a2732;font-weight:950;font-size:12px;color:#dbe4ea}.player-name{display:block;color:#fff!important;text-decoration:none!important;font-size:14px;font-weight:950;line-height:1.12;padding:3px 0}.player-name:active{color:var(--lime)!important}.player-meta{font-size:9px;color:var(--muted);margin-top:2px}.data-cell{text-align:center}.data-cell span{display:block;font-size:7px;color:var(--muted);font-weight:850;text-transform:uppercase}.data-cell b{font-size:11px}.pos{display:inline-flex;align-items:center;justify-content:center;border-radius:5px;padding:2px 5px;min-width:28px;font-size:8px;font-weight:950;color:#fff}.pos-QB{background:var(--qb)}.pos-RB{background:var(--rb)}.pos-WR{background:var(--wr)}.pos-TE{background:var(--te)}.pos-DST{background:var(--dst);color:#111}.pos-K{background:var(--k)}.draft-inline{display:flex!important;align-items:center;justify-content:center;min-height:38px;padding:0 10px;border-radius:10px;background:var(--teal);border:1px solid #9af0e4;color:var(--teal-dark)!important;text-decoration:none!important;font-size:10px;font-weight:950;box-shadow:0 2px 8px rgba(116,227,210,.12)}.draft-inline:active{transform:scale(.97);background:#9af0e4}.draft-inline.disabled{opacity:.4;pointer-events:none}
.draft-status{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:5px 0 9px}.draft-chip{background:#111d27;border:1px solid var(--line);border-radius:11px;padding:8px;text-align:center}.draft-chip span{font-size:7px;color:var(--muted);font-weight:850;text-transform:uppercase;display:block}.draft-chip b{font-size:14px}.on-clock{background:linear-gradient(90deg,#801024,#c41131);border:1px solid #ef3150;border-radius:12px;padding:10px 12px;margin:6px 0 9px;font-size:12px;font-weight:900}
.board-note{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:8px 1px 7px;color:#8fa0ae;font-size:9px;font-weight:800}.board-note b{color:#d7e1e8}.board-shell{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:thin;padding:1px 1px 8px;margin:0 -1px 3px;overscroll-behavior-x:contain}.draft-board{min-width:max-content}.board-row{display:grid;grid-template-columns:repeat(var(--teams),104px);gap:5px;margin-bottom:5px}.board-cell{height:88px;border:1px solid #2a3946;border-radius:9px;background:#0c141b;padding:7px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}.board-cell.empty{background:#091016;border-color:#25313b}.board-cell.mine{box-shadow:inset 0 0 0 1px rgba(116,227,210,.34)}.board-cell.QB{background:rgba(114,87,216,.17);border-color:rgba(140,117,224,.48)}.board-cell.RB{background:rgba(25,168,157,.16);border-color:rgba(52,196,184,.48)}.board-cell.WR{background:rgba(52,127,217,.16);border-color:rgba(73,151,238,.48)}.board-cell.TE{background:rgba(232,129,53,.15);border-color:rgba(243,151,83,.48)}.board-cell.DST{background:rgba(209,178,60,.13);border-color:rgba(220,193,83,.46)}.board-cell.K{background:rgba(104,120,134,.16);border-color:rgba(135,151,164,.42)}.board-cell.clock{background:linear-gradient(145deg,#133c39,#0b2927);border-color:#74e3d2;box-shadow:0 0 0 1px rgba(116,227,210,.2),0 5px 16px rgba(0,0,0,.18)}.board-pick{font-size:9px;color:#8fa0ae;font-weight:850;letter-spacing:.2px}.board-cell.clock .board-pick{color:#a9eee5}.board-name{font-size:12px;color:#f8fbfd;font-weight:950;line-height:1.06;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.board-meta{font-size:9px;color:#9cacb7;display:flex;align-items:center;gap:4px}.board-pos{display:inline-flex;align-items:center;justify-content:center;border-radius:5px;padding:2px 5px;color:#fff;font-size:8px;font-weight:950}.board-pos.QB{background:var(--qb)}.board-pos.RB{background:var(--rb)}.board-pos.WR{background:var(--wr)}.board-pos.TE{background:var(--te)}.board-pos.DST{background:var(--dst);color:#111}.board-pos.K{background:var(--k)}.clock-title{font-size:12px;font-weight:950;color:#fff;line-height:1.05}.clock-sub{font-size:8px;color:#a9eee5;font-weight:850;text-transform:uppercase;letter-spacing:.5px}.pick-card{border:1px solid var(--line);border-radius:11px;padding:9px 10px;background:#101a23;display:grid;grid-template-columns:43px minmax(0,1fr) auto;gap:8px;align-items:center;margin-bottom:5px}.pick-num{font-size:10px;color:#92a0ab;font-weight:850}.pick-card .nm{font-size:12px;font-weight:950}.pick-card .mt{font-size:9px;color:#a0adb7}.pick-empty{opacity:.55}
.profile-hero{background:linear-gradient(140deg,#172735,#0b131a);border:1px solid #294054;border-radius:18px;padding:15px;margin-top:5px}.profile-back{font-size:11px;color:#c7d1d9!important;text-decoration:none!important;font-weight:850}.profile-name-big{font-size:27px;font-weight:980;letter-spacing:-1px;margin:8px 0 2px}.profile-sub{font-size:10px;color:var(--muted)}.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px}.profile-metric{background:#0c151d;border:1px solid #243745;border-radius:11px;padding:9px}.profile-metric b{font-size:16px;display:block}.profile-metric span{font-size:8px;color:var(--muted);text-transform:uppercase;font-weight:850}.weekly-card{display:grid;grid-template-columns:42px 48px 54px minmax(0,1fr);gap:6px;align-items:center;background:#0e1821;border:1px solid var(--line);border-radius:11px;padding:8px;margin-bottom:5px}.weekly-card .wk{font-size:11px;font-weight:950}.weekly-card .opp{font-size:10px;color:#a5b1bb}.weekly-card .pts{font-size:14px;font-weight:950;color:#54ddea}.weekly-card .detail{font-size:9px;color:#9aa8b4;text-align:right}.roster-slot{display:grid;grid-template-columns:45px minmax(0,1fr) auto;gap:8px;align-items:center;padding:10px;background:#0e1821;border:1px solid var(--line);border-radius:11px;margin-bottom:5px}.slot-tag{font-size:9px;font-weight:950;color:#81919e}.slot-player{font-size:12px;font-weight:900}.slot-meta{font-size:9px;color:var(--muted)}.shiva-box{background:linear-gradient(145deg,#151f2a,#0c1218);border:1px solid #2c3a47;border-radius:17px;padding:15px;margin-bottom:10px}.shiva-box h2{font-size:23px;margin:0}.shiva-box p{font-size:11px;color:var(--muted);margin:4px 0 0}.answer{background:#101a22;border-left:3px solid var(--accent);border-radius:0 12px 12px 0;padding:12px 13px;line-height:1.5}
@media(min-width:760px){.block-container{padding-left:1rem!important;padding-right:1rem!important}.bottom-nav{left:50%;transform:translateX(-50%);max-width:620px;border:1px solid #263440;border-bottom:0;border-radius:18px 18px 0 0}.player-shell{grid-template-columns:48px minmax(0,1fr) 70px 70px 60px}.player-shell.draft-player{grid-template-columns:48px minmax(0,1fr) 70px 70px 60px 74px}.bye-desktop{display:block!important}.profile-grid{grid-template-columns:repeat(4,1fr)}.board-row{grid-template-columns:repeat(var(--teams),112px)}.board-cell{height:92px}}
@media(max-width:759px){.bye-desktop{display:none!important}.brand-sub{display:none}.data-status{font-size:8px}.screen-head h1{font-size:22px}[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.4rem!important}[data-testid="stHorizontalBlock"]>[data-testid="column"]{min-width:145px!important;flex:1 1 145px!important}[data-testid="stDataFrame"]{font-size:10px!important}.player-shell{min-height:58px;padding:6px 8px}.player-shell.draft-player{grid-template-columns:40px minmax(0,1fr) 42px 42px 62px;gap:5px}.player-rank{width:32px;height:32px}.draft-inline{min-height:36px;padding:0 7px;font-size:10px}.board-shell{margin-left:-.55rem;margin-right:-.55rem;padding-left:.55rem;padding-right:.55rem}.board-row{grid-template-columns:repeat(var(--teams),102px)}.board-cell{height:86px;padding:6px}.board-name{font-size:11px}}

/* FINAL COMPACT ESPN-LIKE MOBILE SHELL */
:root{--nav-h:58px!important;background:#071019!important}
html,body,#root,.stApp,.stAppViewContainer,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],section.main,.main,.block-container{background:#071019!important;background-color:#071019!important;color-scheme:dark!important}
html::before,body::before{background:#071019!important}
[data-testid="stAppDeployButton"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],.stAppDeployButton,[aria-label="Manage app"],[title="Manage app"],[data-testid*="manage" i],[aria-label*="Manage app" i],[title*="Manage app" i]{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;width:0!important;height:0!important;overflow:hidden!important}
.block-container{padding-top:.12rem!important;padding-left:.58rem!important;padding-right:.58rem!important;padding-bottom:calc(66px + env(safe-area-inset-bottom))!important}
.app-top{padding:1px 1px 3px!important}.brand-badge{width:30px!important;height:30px!important;font-size:16px!important}.brand-name,.brand-title{font-size:17px!important}.screen-head{margin:0 0 7px!important}.screen-head h1{font-size:20px!important;line-height:1.08!important}.screen-head p{font-size:11.5px!important;line-height:1.32!important;margin-top:3px!important}
.st-key-navshiva,.st-key-navguide,.st-key-navdraft,.st-key-navanalytics{display:none!important}
.bottom-nav{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:99999!important;display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;box-sizing:border-box!important;height:calc(56px + env(safe-area-inset-bottom))!important;padding:4px 10px calc(4px + env(safe-area-inset-bottom))!important;background:rgba(7,13,19,.96)!important;backdrop-filter:blur(18px)!important;-webkit-backdrop-filter:blur(18px)!important;border-top:1px solid rgba(132,148,160,.18)!important;box-shadow:0 -3px 12px rgba(0,0,0,.22)!important}
.bottom-nav a{min-width:0!important;min-height:44px!important;height:44px!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:rgba(191,200,207,.56)!important;opacity:.82!important;font-size:9px!important;font-weight:760!important;line-height:1!important;letter-spacing:0!important;gap:1px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;text-decoration:none!important;pointer-events:auto!important}
.bottom-nav a.active{background:transparent!important;box-shadow:none!important;color:#f4f7f9!important;opacity:1!important}.bottom-nav .nav-icon{font-size:28px!important;line-height:28px!important;height:29px!important;display:flex!important;align-items:center!important;justify-content:center!important;color:inherit!important;filter:none!important}.bottom-nav .shiva-iq-navicon{width:31px!important;height:30px!important}.bottom-nav .shiva-iq-mark{width:31px!important;height:31px!important;filter:grayscale(1)!important;opacity:.62!important}.bottom-nav a.active .shiva-iq-mark{filter:grayscale(.15)!important;opacity:.96!important}
.st-key-home_shiva_card{margin:1px 0 8px!important;padding:10px 10px 9px!important;border-radius:9px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 4px 12px rgba(0,0,0,.16)!important}.st-key-home_shiva_card .home-shiva-hero{min-height:108px!important;margin:0 0 8px!important;padding:0 0 9px!important}.st-key-home_shiva_card .home-shiva-kicker{font-size:9px!important;letter-spacing:.65px!important}.st-key-home_shiva_card .home-shiva-title{font-size:21px!important;line-height:1.04!important;letter-spacing:-.45px!important;margin:4px 0 5px!important;max-width:76%!important}.st-key-home_shiva_card .home-shiva-copy{font-size:11.5px!important;line-height:1.34!important;max-width:78%!important}.home-shiva-brain{width:86px!important;height:86px!important;right:-1px!important;top:1px!important;opacity:.60!important}.st-key-home_shiva_card .home-ask-label{font-size:11px!important;margin:0 0 4px!important}.st-key-home_shiva_card .stTextArea textarea{min-height:68px!important;height:68px!important;border-radius:7px!important;font-size:12px!important;line-height:1.35!important;padding:8px 9px!important}.st-key-home_shiva_go .stButton>button{min-height:40px!important;height:40px!important;border-radius:7px!important;font-size:12px!important}
.stat-strip{gap:5px!important;margin:6px 0 8px!important}.mini-stat{min-height:82px!important;padding:8px 5px!important;border-radius:7px!important}.mini-stat b{font-size:23px!important}.mini-stat span{font-size:9.5px!important;line-height:1.2!important;margin-top:6px!important}.quick-grid{gap:6px!important;margin:6px 0 8px!important}.quick-card{min-height:72px!important;padding:9px!important;border-radius:7px!important}.quick-icon{font-size:18.7px!important}.quick-title{font-size:13px!important;margin-top:2px!important}.quick-sub{font-size:10px!important;line-height:1.25!important;margin-top:2px!important}.home-fantasy-news-title{font-size:17px!important;font-weight:900!important;line-height:1.2!important;letter-spacing:-.3px!important;color:#f4f7f9!important;margin:13px 0 7px!important}.hero-card,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell{border-radius:7px!important}.stButton>button,.stDownloadButton>button{min-height:40px!important;font-size:12px!important}
@media(max-width:430px){.main .block-container{padding-left:10px!important;padding-right:10px!important;padding-top:1px!important}.screen-head h1{font-size:20px!important}.st-key-home_shiva_card .home-shiva-title{font-size:20px!important}.st-key-home_shiva_card .home-shiva-copy{font-size:11px!important}.home-shiva-brain{width:82px!important;height:82px!important}}


/* ONE MORE SHIVA — PRODUCT SYSTEM */
:root{--shiva-bg:#080d12;--shiva-card:#10171e;--shiva-card-2:#151f28;--shiva-line:rgba(201,211,220,.13);--shiva-text:#f7f8f9;--shiva-muted:#9aa7b2;--shiva-gold:#d8b35b;--shiva-gold-soft:#8f7437;--shiva-green:#61d095;--shiva-red:#f06a78;--shiva-blue:#6aa7ff}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:radial-gradient(circle at 50% -12%,#17232d 0,#0b1117 34%,#080d12 66%)!important}
.block-container{max-width:980px!important;padding-left:12px!important;padding-right:12px!important}
.app-top{padding:5px 2px 9px!important;border-bottom:1px solid var(--shiva-line)!important;margin-bottom:8px!important}.brand-badge{background:linear-gradient(145deg,#2a2f34,#0d1115)!important;border:1px solid rgba(216,179,91,.38)!important;box-shadow:inset 0 0 18px rgba(216,179,91,.06)!important}.brand-badge::after{content:none!important;display:none!important}.brand-badge{font-size:0!important}.brand-title,.brand-name{color:var(--shiva-text)!important;letter-spacing:-.35px!important}.brand-sub{color:var(--shiva-gold)!important;letter-spacing:.65px!important}.data-status{background:rgba(97,208,149,.07)!important;border-color:rgba(97,208,149,.22)!important;color:#8ee3b5!important}
.screen-head h1{font-size:26px!important;letter-spacing:-.8px!important}.screen-head p{font-size:12px!important;line-height:1.42!important;color:var(--shiva-muted)!important}
.hero-card{background:linear-gradient(145deg,#18232d 0,#10171e 58%,#0c1116 100%)!important;border:1px solid rgba(216,179,91,.20)!important;border-radius:16px!important;padding:17px!important;box-shadow:0 12px 30px rgba(0,0,0,.18)!important}.hero-card:after{content:none!important;display:none!important}.hero-kicker{color:var(--shiva-gold)!important}.hero-card h2{font-size:28px!important;line-height:1.01!important;letter-spacing:-.95px!important}.hero-card p{font-size:12px!important;line-height:1.42!important;color:#aeb8c1!important}
.stat-strip{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}.mini-stat{min-height:94px!important;text-align:left!important;padding:13px!important;background:linear-gradient(145deg,#111a22,#0d141a)!important;border:1px solid var(--shiva-line)!important;border-radius:13px!important}.mini-stat b{font-size:28px!important;letter-spacing:-.8px!important}.mini-stat span{font-size:9px!important;line-height:1.35!important;color:var(--shiva-muted)!important;letter-spacing:.2px!important}
.quick-grid{gap:8px!important}.quick-card{min-height:92px!important;padding:14px!important;border-radius:14px!important;background:linear-gradient(145deg,#121b23,#0d141a)!important;border:1px solid var(--shiva-line)!important;transition:transform .12s ease,border-color .12s ease!important}.quick-card:active{transform:scale(.985)!important;border-color:rgba(216,179,91,.35)!important}.quick-icon{font-size:21px!important}.quick-title{font-size:14px!important}.quick-sub{font-size:10.5px!important;line-height:1.35!important}
.player-shell,.pick-card,.profile-hero,.weekly-card,.roster-slot,.shiva-box,.guide-card,.strategy-box,.shiva-iq-panel,.iq-report-shell{background:linear-gradient(145deg,#111a22,#0c1319)!important;border:1px solid var(--shiva-line)!important;border-radius:13px!important}.player-shell{min-height:70px!important;padding:9px 10px!important}.player-rank{background:#19242d!important;border:1px solid rgba(255,255,255,.035)!important}.draft-inline{background:linear-gradient(145deg,#d8b35b,#b38f40)!important;border-color:#e5c777!important;color:#17130b!important;box-shadow:none!important}.on-clock{background:linear-gradient(100deg,#47252b,#26161a)!important;border-color:rgba(240,106,120,.45)!important}.board-cell.clock{background:linear-gradient(145deg,#2c291b,#171711)!important;border-color:var(--shiva-gold)!important}.board-cell.mine{box-shadow:inset 0 0 0 1px rgba(216,179,91,.30)!important}
.bottom-nav{height:calc(68px + env(safe-area-inset-bottom))!important;padding:5px 12px calc(5px + env(safe-area-inset-bottom))!important;background:rgba(8,13,18,.96)!important;border-top:1px solid rgba(216,179,91,.13)!important;box-shadow:0 -8px 24px rgba(0,0,0,.30)!important}.bottom-nav a{height:54px!important;min-height:54px!important;font-size:10px!important;color:rgba(207,215,221,.60)!important}.bottom-nav a.active{color:#f8f7f4!important}.bottom-nav a.active span:last-child{color:var(--shiva-gold)!important}.bottom-nav .nav-icon{font-size:25px!important;height:28px!important}.bottom-nav .shiva-iq-mark{filter:sepia(.7) saturate(.55) hue-rotate(355deg)!important;opacity:.82!important}
.stButton>button,.stDownloadButton>button{border-radius:11px!important;border:1px solid rgba(216,179,91,.18)!important;background:#131b22!important;color:#f5f7f8!important}.stButton>button[kind="primary"]{background:linear-gradient(145deg,#d8b35b,#b38f40)!important;border-color:#ddbd70!important;color:#17130b!important}
textarea,input,[data-baseweb="select"]>div{background:#0e151b!important;border-color:rgba(216,179,91,.14)!important}
.home-fantasy-news-title{color:#f5f5f3!important;font-size:18px!important}.home-fantasy-news-title:before{content:'SHIVA BLAST';color:var(--shiva-gold);font-size:9px;letter-spacing:.8px;display:block;margin-bottom:3px}
@media(max-width:430px){.stat-strip{grid-template-columns:repeat(2,minmax(0,1fr))!important}.hero-card h2{font-size:26px!important}.bottom-nav{padding-left:8px!important;padding-right:8px!important}.bottom-nav a{font-size:9px!important}}


/* SHIVA EXPERIENCE COMPLETION */
.shiva-trophy-mark{display:block;width:31px;height:45px}.brand-badge{height:48px!important;width:42px!important;border-radius:10px!important;padding:2px!important;background:linear-gradient(145deg,#17191b,#090b0d)!important}.brand-wrap{align-items:center!important}.app-top{min-height:58px!important}
.home-insight-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:9px 0 13px}.home-insight{background:linear-gradient(145deg,#121a21,#0c1217);border:1px solid rgba(216,179,91,.18);border-radius:14px;padding:14px;min-height:132px}.home-insight span{display:block;font-size:10px;font-weight:950;letter-spacing:.65px;color:#d8b35b}.home-insight b{display:block;font-size:38px;line-height:1;margin:9px 0 7px;color:#fff;letter-spacing:-1.2px}.home-insight p{font-size:13px;line-height:1.38;color:#abb6be;margin:0}.quick-title{font-size:15px!important}.quick-sub{font-size:12px!important;line-height:1.35!important}.quick-card{min-height:104px!important}.bottom-nav a{font-size:10.5px!important}.draft-moment{margin:7px 0 10px!important}@media(max-width:430px){.home-insight-grid{grid-template-columns:1fr}.home-insight{min-height:112px}.home-insight b{font-size:34px}.home-insight p{font-size:13px}.quick-grid{grid-template-columns:1fr 1fr}.quick-card{min-height:102px;padding:13px!important}.brand-title{font-size:19px!important}}


/* FINAL SHIVA IDENTITY */
.brand-badge{background:transparent!important;border:0!important;box-shadow:none!important;width:48px!important;height:58px!important;padding:0!important;border-radius:0!important;overflow:visible!important}
.shiva-trophy-mark{width:42px!important;height:58px!important;filter:drop-shadow(0 5px 8px rgba(0,0,0,.28))}
.brand-badge::after,.hero-card::after{content:none!important;display:none!important}
.brand-wrap{gap:8px!important}.brand-title{font-size:20px!important}.brand-sub{font-size:9.5px!important}.app-top{min-height:64px!important;padding-top:4px!important}
.bottom-nav{grid-template-columns:repeat(4,1fr)!important}.bottom-nav a{font-size:10.5px!important}
@media(max-width:430px){.brand-badge{width:44px!important;height:54px!important}.shiva-trophy-mark{width:39px!important;height:54px!important}.brand-title{font-size:19px!important}}

\n/* SHIVA MOBILE UX V3 — ESPN/Draft Sharks reference pass */\nhtml,body,.stApp,[data-testid="stAppViewContainer"]{background:#081016!important}.block-container{max-width:1080px!important;padding:.55rem .75rem 7.2rem!important}.data-status{display:none!important}.app-top{min-height:66px!important;padding:7px 2px 11px!important;border-bottom:1px solid rgba(255,255,255,.07)!important;margin-bottom:10px!important}.brand-wrap{gap:10px!important}.brand-badge{width:58px!important;height:72px!important;padding:0!important;background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important}.shiva-trophy-mark{display:block!important;width:56px!important;height:70px!important}.brand-title{font-size:24px!important;line-height:1!important;letter-spacing:-.6px!important}.brand-sub{display:block!important;font-size:10.5px!important;line-height:1.2!important;margin-top:4px!important;color:#aeb6bc!important}.screen-head{margin:8px 0 14px!important}.screen-head h1{font-size:31px!important;line-height:1.02!important;letter-spacing:-1px!important}.screen-head p{font-size:15px!important;line-height:1.45!important;margin-top:7px!important;color:#aeb8bf!important}.hero-card{padding:21px 18px!important;border-radius:18px!important}.hero-kicker{font-size:11px!important}.hero-card h2{font-size:31px!important;line-height:1.04!important;max-width:100%!important}.hero-card p{font-size:15px!important;line-height:1.5!important;max-width:100%!important}.stButton>button{min-height:56px!important;border-radius:14px!important;font-size:15px!important;font-weight:850!important}.stButton>button[kind="primary"]{background:#d2ae57!important;border-color:#d2ae57!important;color:#17130a!important}.stButton>button[kind="secondary"]{background:#101820!important;border-color:#2a3640!important;color:#f3f4f4!important}.stTextInput input,.stTextArea textarea{font-size:16px!important;min-height:54px!important}.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{min-height:54px!important;font-size:15px!important}.stCaptionContainer,[data-testid="stCaptionContainer"]{font-size:13px!important;line-height:1.4!important}.player-name{font-size:16px!important}.player-meta{font-size:11px!important}.data-cell span{font-size:9px!important}.data-cell b{font-size:13px!important}.profile-name-big{font-size:34px!important}.profile-sub{font-size:13px!important}.profile-metric b{font-size:22px!important}.profile-metric span{font-size:10px!important}.bottom-nav{display:none!important}.st-key-bottom_nav_shell{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:9999!important;background:rgba(8,16,22,.98)!important;border-top:1px solid #26323b!important;padding:8px 9px calc(9px + env(safe-area-inset-bottom))!important;box-shadow:0 -12px 32px rgba(0,0,0,.35)!important;backdrop-filter:blur(18px)!important}.st-key-bottom_nav_shell [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:7px!important}.st-key-bottom_nav_shell [data-testid="column"]{min-width:0!important}.st-key-bottom_nav_shell .stButton>button{min-height:54px!important;padding:8px 4px!important;font-size:12.5px!important;border-radius:13px!important;white-space:nowrap!important}.st-key-bottom_nav_shell .stButton>button[kind="secondary"]{border-color:transparent!important;background:transparent!important;color:#98a4ac!important}.st-key-bottom_nav_shell .stButton>button[kind="primary"]{background:#1c2730!important;border:1px solid #34414b!important;color:#fff!important}.stat-strip{grid-template-columns:1fr 1fr!important;gap:10px!important}.mini-stat{min-height:118px!important;padding:15px 12px!important;border-radius:15px!important;text-align:left!important}.mini-stat b{font-size:32px!important}.mini-stat span{font-size:11px!important;line-height:1.35!important}.quick-title{font-size:16px!important}.quick-sub{font-size:12.5px!important;line-height:1.4!important}.quick-card{min-height:106px!important;border-radius:15px!important;padding:15px!important}@media(max-width:520px){.block-container{padding-left:.7rem!important;padding-right:.7rem!important}.brand-title{font-size:22px!important}.brand-sub{font-size:9.5px!important}.screen-head h1{font-size:29px!important}.screen-head p{font-size:14.5px!important}.hero-card h2{font-size:29px!important}.hero-card p{font-size:14.5px!important}.stat-strip{grid-template-columns:1fr!important}.st-key-bottom_nav_shell .stButton>button{font-size:11.5px!important}.player-shell{min-height:72px!important}}\n



/* GLOBAL SHIVA SHELL RECOVERY - protected scope */
.brand-badge .shiva-trophy-mark{display:block!important;width:58px!important;height:70px!important;object-fit:contain!important;border-radius:0!important;filter:drop-shadow(0 5px 8px rgba(0,0,0,.32))!important}
.st-key-bottom_nav_shell [data-testid="stHorizontalBlock"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;width:100%!important;gap:6px!important;flex-wrap:unset!important}
.st-key-bottom_nav_shell [data-testid="column"]{width:auto!important;min-width:0!important;flex:unset!important}
.st-key-bottom_nav_shell .stButton>button{width:100%!important;min-width:0!important}
.st-key-primary_nav_Home .stButton>button{position:relative!important;padding-top:31px!important;line-height:1!important}
.st-key-primary_nav_Home .stButton>button::before{content:""!important;position:absolute!important;top:4px!important;left:50%!important;transform:translateX(-50%)!important;width:27px!important;height:27px!important;background-image:url("data:image/jpeg;base64,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")!important;background-position:center!important;background-size:contain!important;background-repeat:no-repeat!important;border-radius:2px!important}

/* APPROVED UI POLISH PASS — typography + trophy presentation only */
.brand-badge .shiva-trophy-mark{width:58px!important;height:58px!important;object-fit:contain!important;border-radius:0!important;background:transparent!important;mix-blend-mode:screen!important;filter:contrast(1.05) saturate(.96)!important}
.st-key-primary_nav_Home button{position:relative!important;padding-top:25px!important}
.st-key-primary_nav_Home button::before{content:""!important;position:absolute!important;top:4px!important;left:50%!important;transform:translateX(-50%)!important;width:24px!important;height:24px!important;background-image:url("data:image/jpeg;base64,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")!important;background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;mix-blend-mode:screen!important;filter:contrast(1.08) saturate(.92)!important}
@media(max-width:520px){.brand-badge{width:54px!important;height:54px!important}.brand-badge .shiva-trophy-mark{width:54px!important;height:54px!important}.brand-title{font-size:26px!important}.brand-sub{font-size:12px!important}}

</style>'''
st.markdown(CSS, unsafe_allow_html=True)
inject_coach_css()

# Streamlit Community Cloud hosted-badge suppressor.
# Intentionally isolated from app CSS/layout: only fixed Streamlit-hosting links are hidden.
components.html(
    """
    <script>
    (() => {
      let doc;
      try { doc = window.top.document; } catch (_) { doc = window.parent.document; }
      const hideHostedBadge = () => {
        doc.querySelectorAll('a[href*="streamlit.io"]').forEach((link) => {
          const label = `${link.textContent || ''} ${link.getAttribute('aria-label') || ''} ${link.getAttribute('title') || ''}`.toLowerCase();
          let node = link;
          let fixedOverlay = null;
          for (let i = 0; i < 5 && node; i += 1, node = node.parentElement) {
            const style = window.getComputedStyle(node);
            if (style.position === 'fixed') { fixedOverlay = node; break; }
          }
          if (fixedOverlay && (label.includes('hosted with streamlit') || label.includes('made with streamlit') || link.href.includes('streamlit.io'))) {
            fixedOverlay.style.setProperty('display', 'none', 'important');
            fixedOverlay.style.setProperty('visibility', 'hidden', 'important');
            fixedOverlay.style.setProperty('pointer-events', 'none', 'important');
          }
        });
      };
      hideHostedBadge();
      const observer = new MutationObserver(hideHostedBadge);
      observer.observe(doc.documentElement, { childList: true, subtree: true });
      window.setTimeout(() => observer.disconnect(), 15000);
    })();
    </script>
    """,
    height=0,
    width=0,
)


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
    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">{SHIVA_MARK}</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div></div>',unsafe_allow_html=True)


def bottom_nav(active:str):
    active = "Home" if active == "Shiva" else active
    labels=[("Home",""),("Draft","◫"),("Guide","▤"),("Coach","✦")]
    with st.container(key="bottom_nav_shell"):
        cols=st.columns(4,gap="small")
        for i,(page_name,icon) in enumerate(labels):
            with cols[i]:
                if st.button(f"{icon}  {page_name}",key=f"primary_nav_{page_name}",type="primary" if active==page_name else "secondary",use_container_width=True):
                    st.query_params["page"]=page_name
                    for k in ("player","hint","ret","draft"):
                        try: del st.query_params[k]
                        except Exception: pass
                    st.rerun()

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
    system=f"You are Shiva, an elite fantasy football analyst. Default ESPN full 1-point PPR. Use supplied app data as authoritative and never invent stats. User roster: {rt}. Top available: {avail}. Historical context: {history}."
    try:return OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=[{"role":"system","content":system},{"role":"user","content":question}]).output_text
    except Exception as exc:return f"Shiva could not complete the request: {exc}"


def render_nfl_kickoff_countdown():
    components.html(
        r"""<style>
        *{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow:hidden}
        .kickoff{height:42px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;padding:5px 9px;border:1px solid rgba(116,227,210,.20);border-radius:8px;background:#0d1821;color:#f4f7f9}
        .label{font-size:9px;font-weight:900;letter-spacing:.65px;text-transform:uppercase;color:#74e3d2;white-space:nowrap}
        .time{font-size:14px;font-weight:900;letter-spacing:-.2px;white-space:nowrap;font-variant-numeric:tabular-nums}
        .sub{font-size:8px;color:#8fa0ae;font-weight:800;white-space:nowrap}
        @media(max-width:390px){.kickoff{gap:6px;padding-left:7px;padding-right:7px}.time{font-size:13px}.sub{display:none}}
        </style>
        <div class="kickoff" role="timer" aria-label="Countdown to the 2026 NFL kickoff game">
          <span class="label">NFL KICKOFF</span>
          <span class="time" id="shivaKickoffClock">--d --h --m --s</span>
          <span class="sub">SEP 9 · 8:20 PM ET</span>
        </div>
        <script>
        (function(){
          const target = new Date('2026-09-09T20:20:00-04:00').getTime();
          const el = document.getElementById('shivaKickoffClock');
          function tick(){
            const diff = Math.max(0, target - Date.now());
            const days = Math.floor(diff / 86400000);
            const hours = Math.floor((diff % 86400000) / 3600000);
            const mins = Math.floor((diff % 3600000) / 60000);
            const secs = Math.floor((diff % 60000) / 1000);
            el.textContent = days + 'd ' + String(hours).padStart(2,'0') + 'h ' + String(mins).padStart(2,'0') + 'm ' + String(secs).padStart(2,'0') + 's';
          }
          tick();
          setInterval(tick,1000);
        })();
        </script>""",
        height=46,
        scrolling=False,
    )


def home():
    render_home_v2(players,load_weekly,weekly_name_col,espn_ppr)


def draft_guide():
    screen_head("2026 Shiva Draft Guide","Full-PPR intelligence built for draft-day decisions.")
    render_draft_guide(players,profile_href,load_weekly,weekly_name_col,espn_ppr)

def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    is_user_pick=pick_team(n,st.session_state.team_count)==st.session_state.user_slot
    if is_user_pick:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    render_draft_moment(st.session_state.draft_log,n,st.session_state.team_count,st.session_state.user_slot)
    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)
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

def analytics():
    screen_head("Shiva Lab","Compare players and inspect the historical Full-PPR evidence behind the call.")
    q=st.text_input("Search analytics",placeholder="Search player or NFL team…",key="analytics_search")
    pos=st.selectbox("Position filter",["ALL","RB","WR","QB","TE","DST","K"],key="analytics_pos")
    df=players.copy()
    if q:
        q=q.casefold().strip()
        df=df.loc[df["name"].str.casefold().str.contains(q,regex=False)|df["team"].str.casefold().str.contains(q,regex=False)]
    if pos!="ALL":df=df.loc[df["pos"].eq(pos)]
    shiva_compare()
    st.markdown("### Player database")
    render_players(df,"Analytics","none",150)


def shiva_compare():
    st.markdown("### Compare players")
    st.caption("Historical evidence + current ranking context. No fabricated projection confidence.")
    names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    if len(names)<2:
        st.info("Player data is not available for comparison right now.")
        return
    c1,c2=st.columns(2)
    with c1:a=st.selectbox("Player A",names,index=0,key="compare_a")
    with c2:b=st.selectbox("Player B",names,index=min(1,len(names)-1),key="compare_b")
    if a==b:
        st.info("Choose two different players.")
        return
    rows=[]
    for nm in (a,b):
        pr=players.loc[players["name"].eq(nm)].iloc[0]
        rows.append((nm,str(pr.get("pos","")),pr.get("adp"),pr.get("rank")))
    cards=[]
    for nm,pos,adp,rank in rows:
        adp_text="—" if pd.isna(adp) else f"{float(adp):.1f}"
        rank_text="—" if pd.isna(rank) else str(int(rank))
        cards.append(f'<div class="mini-stat"><b>{html.escape(str(nm))}</b><span>{html.escape(str(pos))} · ADP {adp_text} · Rank {rank_text}</span></div>')
    st.markdown('<div class="stat-strip">'+''.join(cards)+'</div>',unsafe_allow_html=True)
    st.caption("Open either player profile for season-by-season and week-by-week Full-PPR history.")

def shiva():
    screen_head("Ask Shiva","Your draft copilot uses the same player data as the app.");st.markdown('<div class="shiva-box"><h2>✦ Shiva Intelligence</h2><p>Ask about players, weekly production, roster construction or who to draft next.</p></div>',unsafe_allow_html=True);q=st.text_area("Question",placeholder="Who should I draft here and why?",height=110)
    if st.button("Ask Shiva",type="primary",use_container_width=True) and q.strip():
        with st.spinner("Analyzing your live draft context…"):a=ask_shiva(q.strip())
        st.session_state.ask_history.insert(0,(q.strip(),a))
    for q,a in st.session_state.ask_history[:6]:st.markdown(f"**{q}**");st.markdown(f'<div class="answer">{a}</div>',unsafe_allow_html=True);st.write("")
def season_coach():
    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")
    render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)

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
page=str(qp.get("page") or "Shiva");page=page if page in PAGES else "Shiva"
{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics,"Coach":season_coach}[page]();bottom_nav(page)
