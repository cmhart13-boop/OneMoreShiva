from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
NEWS_PATH = ROOT / "data" / "live_news.json"
KICKOFF_ISO = "2026-09-09T20:20:00-04:00"

CSS = r'''<style>
:root{--sv-bg:#081016;--sv-panel:#101820;--sv-panel2:#141e27;--sv-line:#25313a;--sv-text:#f7f7f5;--sv-muted:#aab3b9;--sv-gold:#d5b15c;--sv-gold2:#f0d88f}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#081016!important}
.home-v2{margin-top:0}.home-v2-hero{background:linear-gradient(145deg,#18222b,#0d141a);border:1px solid rgba(213,177,92,.24);border-radius:20px;padding:22px 18px 20px;margin:4px 0 14px;box-shadow:0 14px 40px rgba(0,0,0,.18)}.home-v2-kicker{font-size:14px;font-weight:900;letter-spacing:.8px;color:var(--sv-gold2);text-transform:uppercase}.home-v2-hero h1{font-size:34px;line-height:1.02;letter-spacing:-1.2px;margin:6px 0 9px;color:var(--sv-text)}.home-v2-hero p{font-size:17px;line-height:1.5;color:#c0c7cc;margin:0;max-width:760px}
.kick-card{background:transparent;border:0;border-radius:0;padding:0 2px 10px;margin:0}.kick-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:7px}.kick-label{font-size:12px;font-weight:900;letter-spacing:.7px;color:var(--sv-gold2);text-transform:uppercase}.kick-date{font-size:12px;color:var(--sv-muted)}.kick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.kick-unit{background:#0b1218;border:1px solid #25313a;border-radius:12px;padding:8px 6px;text-align:center}.kick-unit strong{display:block;font-size:28px;line-height:1;color:#fff;letter-spacing:-1px}.kick-unit span{display:block;margin-top:4px;font-size:10px;font-weight:800;color:#8f9ba3;text-transform:uppercase;letter-spacing:.5px}
.home-v2-section{font-size:22px;font-weight:950;letter-spacing:-.5px;color:#f7f7f5;margin:18px 1px 9px}.home-v2-sub{font-size:14px;color:var(--sv-muted);line-height:1.4;margin:-4px 1px 10px}
.st-key-war_room_row [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important;gap:6px!important}.st-key-war_room_row [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:25%!important}.st-key-war_room_row .stButton>button{min-width:0!important;padding-left:5px!important;padding-right:5px!important;white-space:nowrap!important}
.st-key-edge_floor_card,.st-key-edge_ceiling_card{background:#101820;border:1px solid #27333d;border-radius:16px;padding:18px!important;margin:7px 0 12px}.home-edge{background:transparent;border:0;border-radius:0;padding:0}.home-edge small{font-size:14px;font-weight:950;letter-spacing:.55px;color:var(--sv-gold2);text-transform:uppercase}.home-edge b{display:block;font-size:23px;color:#fff;margin:8px 0 6px;line-height:1.12}.home-edge p{font-size:16px;line-height:1.48;color:#b5bec4;margin:0}.leader-row{display:flex;justify-content:space-between;gap:14px;align-items:center;border-top:1px solid #222d35;padding:14px 0}.leader-row:first-of-type{border-top:0}.leader-name{font-size:17.5px;font-weight:900;color:#fff;line-height:1.2}.leader-meta{font-size:14px;color:#a1adb5;margin-top:4px}.leader-stat{font-size:22px;font-weight:950;color:var(--sv-gold2);white-space:nowrap}
.st-key-edge_panel_fragment{background:linear-gradient(145deg,#121c24,#0b1218);border:1px solid rgba(213,177,92,.30);border-radius:18px;padding:16px!important;margin:12px 0 2px}.edge-panel-kicker{font-size:11px;font-weight:950;letter-spacing:.65px;color:var(--sv-gold2);text-transform:uppercase}.edge-panel-title{font-size:24px;line-height:1.08;margin:5px 0 6px;color:#fff;font-weight:900}.edge-panel-copy{font-size:15px;line-height:1.45;color:#b9c2c8;margin:0 0 10px}.edge-rank-row{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:10px;align-items:center;border-top:1px solid #233039;padding:12px 0}.edge-rank-row:first-of-type{border-top:0}.edge-rank{font-size:15px;font-weight:950;color:#7f8e98}.edge-rank-name{font-size:17px;font-weight:900;color:#fff}.edge-rank-meta{font-size:13px;color:#9eabb3;margin-top:3px}.edge-rank-stat{text-align:right}.edge-rank-stat b{display:block;font-size:20px;color:var(--sv-gold2)}.edge-rank-stat span{display:block;font-size:10px;color:#84939d;text-transform:uppercase;font-weight:900;letter-spacing:.4px}.edge-profile{display:inline-block;margin-top:4px;font-size:11px;font-weight:900;color:var(--sv-gold2)!important;text-decoration:none!important}.edge-method{font-size:11px;color:#7f8e98;line-height:1.4;margin-top:9px}
.st-key-edge_panel_fragment [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important;gap:7px!important;margin:5px 0 7px}.st-key-edge_panel_fragment [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:25%!important}.st-key-edge_panel_fragment .stButton>button{min-height:38px!important;padding:5px 8px!important;border-radius:11px!important;font-size:12px!important;font-weight:950!important;letter-spacing:.35px!important;-webkit-tap-highlight-color:transparent!important;transition:none!important}.st-key-edge_panel_fragment .stButton>button[kind="primary"]{border-color:rgba(240,216,143,.72)!important;background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;color:#fff!important;box-shadow:0 0 0 1px rgba(213,177,92,.12),0 0 18px rgba(213,177,92,.12)!important}.st-key-edge_panel_fragment .stButton>button[kind="secondary"]{background:#0d161d!important;border-color:#30404b!important;color:#9eabb3!important}
.news-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px;margin-bottom:14px}.news-card{display:block;background:#101820;border:1px solid #27333d;border-radius:17px;overflow:hidden;color:#fff!important;text-decoration:none!important;min-height:220px}.news-thumb{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#18232c}.news-body{padding:13px}.news-meta{font-size:10px;font-weight:900;color:var(--sv-gold2);text-transform:uppercase;letter-spacing:.55px}.news-title{font-size:16px;font-weight:900;line-height:1.25;margin:5px 0 6px;color:#fff}.news-desc{font-size:12.5px;line-height:1.4;color:#aeb8bf;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.news-link{font-size:11px;font-weight:900;color:var(--sv-gold2);margin-top:9px}.news-empty{background:#101820;border:1px solid #27333d;border-radius:16px;padding:16px;color:#aeb8bf;font-size:14px}
.edge-title{font-size:28px!important;margin-top:22px!important}.edge-sub{font-size:16px!important;line-height:1.45!important;margin-top:-2px!important;margin-bottom:12px!important}
@media(max-width:520px){.home-v2-hero{padding:20px 16px}.home-v2-hero h1{font-size:31px}.home-v2-hero p{font-size:16.5px}.news-grid{grid-template-columns:1fr}.st-key-edge_floor_card,.st-key-edge_ceiling_card{padding:17px!important}.home-edge{padding:0}.leader-name{font-size:17px}.leader-meta{font-size:13.5px}.leader-stat{font-size:21px}.edge-panel-title{font-size:22px}.edge-panel-copy{font-size:14.5px}.edge-rank-name{font-size:16.5px}.edge-rank-meta{font-size:12.5px}.edge-rank-stat b{font-size:19px}.edge-title{font-size:27px!important}.edge-sub{font-size:15.5px!important}.st-key-war_room_row [data-testid="stHorizontalBlock"]{gap:4px!important}.st-key-war_room_row .stButton>button{font-size:11px!important;padding:6px 3px!important}.st-key-edge_panel_fragment [data-testid="stHorizontalBlock"]{gap:6px!important}.st-key-edge_panel_fragment .stButton>button{min-height:36px!important;font-size:11.5px!important;padding:4px!important}}
</style>'''


def go(page: str) -> None:
    st.query_params["page"] = page
    for key in ("player", "hint", "ret", "draft", "edge_mode", "edge_pos"):
        try:
            del st.query_params[key]
        except Exception:
            pass


def render_countdown() -> None:
    block=f'''<div class="kick-card"><div class="kick-top"><div class="kick-label">NFL Kickoff</div><div class="kick-date">September 9 · 8:20 PM ET</div></div><div class="kick-grid"><div class="kick-unit"><strong id="d">—</strong><span>Days</span></div><div class="kick-unit"><strong id="h">—</strong><span>Hours</span></div><div class="kick-unit"><strong id="m">—</strong><span>Min</span></div><div class="kick-unit"><strong id="s">—</strong><span>Sec</span></div></div></div><script>(function(){{const t=new Date('{KICKOFF_ISO}').getTime();function tick(){{let x=Math.max(0,t-Date.now());const d=Math.floor(x/86400000);x%=86400000;const h=Math.floor(x/3600000);x%=3600000;const m=Math.floor(x/60000);const s=Math.floor((x%60000)/1000);for(const [id,v] of [['d',d],['h',h],['m',m],['s',s]]){{const e=document.getElementById(id);if(e)e.textContent=String(v).padStart(2,'0')}}}}tick();setInterval(tick,1000)}})()</script>'''
    components.html(CSS+block,height=112,scrolling=False)


def _news() -> list[dict]:
    try:return list(json.loads(NEWS_PATH.read_text(encoding="utf-8")).get("articles") or [])
    except Exception:return []


def _edge_pool(players: pd.DataFrame, load_weekly, weekly_name_col, espn_ppr) -> pd.DataFrame:
    try:
        w=load_weekly().copy(); nc=weekly_name_col(w)
        if not nc or "season" not in w.columns or "week" not in w.columns:return pd.DataFrame()
        w["_ppr"]=espn_ppr(w)
        w=w.loc[pd.to_numeric(w["season"],errors="coerce").eq(2025)]
        w=w.loc[pd.to_numeric(w["week"],errors="coerce").between(1,18,inclusive="both") & w["_ppr"].notna()].copy()
        cols=[c for c in ["id","name","pos"] if c in players.columns]
        current=players[cols].drop_duplicates(subset=["name"]).copy(); current["_key"]=current["name"].astype(str).str.casefold(); w["_key"]=w[nc].astype(str).str.casefold()
        merge_cols=["_key","name","pos"]+(["id"] if "id" in current.columns else [])
        w=w.merge(current[merge_cols],on="_key",how="inner"); w=w.loc[w["pos"].astype(str).isin(["RB","WR","TE","QB"])]
        group_cols=["name","pos"]+(["id"] if "id" in w.columns else [])
        g=w.groupby(group_cols,as_index=False).agg(games=("_ppr","count"),ppg=("_ppr","mean"),rate15=("_ppr",lambda x:(x>=15).mean()*100),boom25=("_ppr",lambda x:(x>=25).mean()*100))
        return g.loc[g["games"]>=8].copy()
    except Exception:return pd.DataFrame()


def _edge_leaders(pool: pd.DataFrame) -> tuple[list[dict],list[dict]]:
    if pool.empty:return [],[]
    return pool.sort_values(["rate15","ppg"],ascending=False).head(3).to_dict("records"),pool.sort_values(["boom25","ppg"],ascending=False).head(3).to_dict("records")


def _leader_html(rows:list[dict],stat:str,suffix:str)->str:
    if not rows:return '<div class="leader-row"><div><div class="leader-name">Historical leader data unavailable</div><div class="leader-meta">No estimate substituted</div></div><div class="leader-stat">—</div></div>'
    return ''.join(f'<div class="leader-row"><div><div class="leader-name">{html.escape(str(r.get("name","")))}</div><div class="leader-meta">{html.escape(str(r.get("pos","")))} · {int(r.get("games",0))} games · {float(r.get("ppg",0)):.1f} PPG</div></div><div class="leader-stat">{float(r.get(stat,0)):.0f}{suffix}</div></div>' for r in rows)


def _edge_profile_href(row:dict)->str:
    pid=str(row.get("id") or "").strip(); name=str(row.get("name") or "").strip()
    return f"?page=Players&player={quote_plus(pid)}&name={quote_plus(name)}&return=Home" if pid else "?page=Players"


def _edge_rows(pool:pd.DataFrame,stat:str,stat_label:str,position:str)->str:
    ranked=pool.loc[pool["pos"].astype(str).eq(position)].sort_values([stat,"ppg"],ascending=False).head(10).to_dict("records")
    rows=[]
    if not ranked:rows.append('<div class="edge-rank-row"><div class="edge-rank">—</div><div><div class="edge-rank-name">No verified qualifying players</div><div class="edge-rank-meta">No estimate substituted for this position.</div></div><div class="edge-rank-stat"><b>—</b><span>verified</span></div></div>')
    for i,r in enumerate(ranked,1):
        href=html.escape(_edge_profile_href(r),quote=True)
        rows.append(f'<div class="edge-rank-row"><div class="edge-rank">#{i}</div><div><div class="edge-rank-name">{html.escape(str(r.get("name","")))}</div><div class="edge-rank-meta">{html.escape(str(r.get("pos","")))} · {int(r.get("games",0))} games · {float(r.get("ppg",0)):.1f} PPG</div><a class="edge-profile" href="{href}" target="_self">View player →</a></div><div class="edge-rank-stat"><b>{float(r.get(stat,0)):.0f}%</b><span>{stat_label}</span></div></div>')
    rows.append(f'<div class="edge-method">Top 10 {position} · latest completed season only · ESPN Full PPR · minimum 8 games with verified weekly results. Rookies and players without enough historical games are not estimated.</div>')
    return ''.join(rows)


def _set_edge_pos(position:str)->None:
    st.session_state["shiva_edge_pos"] = position


@st.fragment
def _render_edge_fragment(pool:pd.DataFrame,mode:str)->None:
    floor=mode=="floor"; stat="rate15" if floor else "boom25"; stat_label="15+ weeks" if floor else "25+ weeks"
    title="Safest weekly scoring profiles" if floor else "Highest week-winning upside"
    copy="If your situation calls for lowering weekly risk, start here. These players are ranked by how often they cleared 15 PPR points, with PPG as the tiebreaker." if floor else "If your situation calls for chasing upside, start here. These players are ranked by how often they cleared 25 PPR points, with PPG as the tiebreaker."
    if pool.empty:
        with st.container(key="edge_panel_fragment"):
            st.markdown('<div class="edge-panel-kicker">SHIVA SAYS</div><div class="edge-panel-title">Historical rankings unavailable</div><p class="edge-panel-copy">No estimate has been substituted.</p>',unsafe_allow_html=True)
        return
    if st.session_state.get("shiva_edge_pos") not in {"QB","RB","WR","TE"}:
        st.session_state["shiva_edge_pos"]="QB"
    with st.container(key="edge_panel_fragment"):
        st.markdown(f'<div class="edge-panel-kicker">SHIVA SAYS</div><div class="edge-panel-title">{title}</div><p class="edge-panel-copy">{copy}</p>',unsafe_allow_html=True)
        current=st.session_state["shiva_edge_pos"]
        cols=st.columns(4,gap="small")
        for col,pos in zip(cols,("QB","RB","WR","TE")):
            with col:
                st.button(pos,key=f"edge_pos_{mode}_{pos}",type="primary" if current==pos else "secondary",use_container_width=True,on_click=_set_edge_pos,args=(pos,))
        current=st.session_state["shiva_edge_pos"]
        st.markdown(_edge_rows(pool,stat,stat_label,current),unsafe_allow_html=True)


def _toggle_edge(mode:str)->None:
    if st.session_state.get("shiva_edge_mode")==mode:
        st.session_state.pop("shiva_edge_mode",None)
    else:
        st.session_state["shiva_edge_mode"]=mode


def render_home_v2(players:pd.DataFrame,load_weekly,weekly_name_col,espn_ppr)->None:
    st.markdown(CSS,unsafe_allow_html=True); render_countdown()
    st.markdown('''<div class="home-v2"><div class="home-v2-hero"><div class="home-v2-kicker">Shiva Says</div><h1>Win the decision in front of you.</h1><p>Draft smarter. Protect your weekly floor. Keep real ceiling on the roster. Shiva turns verified history, current context and league state into fast fantasy decisions.</p></div></div>''',unsafe_allow_html=True)
    st.markdown('<div class="home-v2-section">Your War Room</div><div class="home-v2-sub">The four places you should need most — one tap away.</div>',unsafe_allow_html=True)
    with st.container(key="war_room_row"):
        c1,c2,c3,c4=st.columns(4,gap="small")
        with c1:st.button("◫  Draft",use_container_width=True,key="home_go_draft",on_click=go,args=("Draft",))
        with c2:st.button("✦  Coach",use_container_width=True,key="home_go_coach",on_click=go,args=("Coach",))
        with c3:st.button("▤  Guide",use_container_width=True,key="home_go_guide",on_click=go,args=("Guide",))
        with c4:st.button("◎  Players",use_container_width=True,key="home_go_players",on_click=go,args=("Players",))

    edge_pool=_edge_pool(players,load_weekly,weekly_name_col,espn_ppr); consistency,ceiling=_edge_leaders(edge_pool)
    st.markdown('<div class="home-v2-section edge-title">The Shiva Edge</div><div class="home-v2-sub edge-sub">Historical evidence, not a mystery score.</div>',unsafe_allow_html=True)

    query_mode=str(st.query_params.get("edge_mode") or "")
    if query_mode in {"floor","ceiling"}:st.session_state["shiva_edge_mode"]=query_mode
    edge_mode=st.session_state.get("shiva_edge_mode")

    with st.container(key="edge_floor_card"):
        st.markdown('<div class="home-edge"><small>Raise the floor</small><b>Repeatable 15+ scoring</b><p>Players who most consistently cleared 15 PPR points in the latest completed season.</p>'+_leader_html(consistency,"rate15","%")+'</div>',unsafe_allow_html=True)
        st.button("Raise the Floor →",use_container_width=True,key="edge_floor_open",type="primary" if edge_mode=="floor" else "secondary",on_click=_toggle_edge,args=("floor",))
        if edge_mode=="floor":
            _render_edge_fragment(edge_pool,"floor")

    with st.container(key="edge_ceiling_card"):
        st.markdown('<div class="home-edge"><small>Keep the ceiling</small><b>Week-winning upside</b><p>Players who most often cleared 25 PPR points in the latest completed season.</p>'+_leader_html(ceiling,"boom25","%")+'</div>',unsafe_allow_html=True)
        st.button("Keep the Ceiling →",use_container_width=True,key="edge_ceiling_open",type="primary" if edge_mode=="ceiling" else "secondary",on_click=_toggle_edge,args=("ceiling",))
        if edge_mode=="ceiling":
            _render_edge_fragment(edge_pool,"ceiling")

    st.markdown('<div class="home-v2-section">Shiva Blast</div><div class="home-v2-sub">Current ESPN fantasy/NFL context with the article image and the actual story link.</div>',unsafe_allow_html=True)
    articles=[a for a in _news() if a.get("headline")][:6]
    if not articles:
        st.markdown('<div class="news-empty">Current verified news is temporarily unavailable. Shiva will keep the last verified snapshot instead of inventing headlines.</div>',unsafe_allow_html=True); return
    cards=[]
    for a in articles:
        url=html.escape(str(a.get("url") or "#"),quote=True); image=html.escape(str(a.get("image") or ""),quote=True); headline=html.escape(str(a.get("headline") or "")); desc=html.escape(str(a.get("description") or "")); published=str(a.get("published") or "")
        try:meta=datetime.fromisoformat(published.replace("Z","+00:00")).strftime("ESPN · %b %d")
        except Exception:meta="ESPN"
        thumb=f'<img class="news-thumb" src="{image}" alt="" loading="lazy">' if image else '<div class="news-thumb"></div>'
        cards.append(f'<a class="news-card" href="{url}" target="_blank" rel="noopener noreferrer">{thumb}<div class="news-body"><div class="news-meta">{meta}</div><div class="news-title">{headline}</div><p class="news-desc">{desc}</p><div class="news-link">Open story →</div></div></a>')
    st.markdown('<div class="news-grid">'+''.join(cards)+'</div>',unsafe_allow_html=True)