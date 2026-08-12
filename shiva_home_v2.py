from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
NEWS_PATH = ROOT / "data" / "live_news.json"
KICKOFF_ISO = "2026-09-09T20:20:00-04:00"

CSS = r'''<style>
:root{--sv-bg:#081016;--sv-panel:#101820;--sv-panel2:#141e27;--sv-line:#25313a;--sv-text:#f7f7f5;--sv-muted:#aab3b9;--sv-gold:#d5b15c;--sv-gold2:#f0d88f}
.home-v2{margin-top:2px}.home-v2-hero{background:linear-gradient(145deg,#18222b,#0d141a);border:1px solid rgba(213,177,92,.24);border-radius:20px;padding:22px 18px 20px;margin:4px 0 14px;box-shadow:0 14px 40px rgba(0,0,0,.18)}.home-v2-kicker{font-size:12px;font-weight:900;letter-spacing:.9px;color:var(--sv-gold2);text-transform:uppercase}.home-v2-hero h1{font-size:34px;line-height:1.02;letter-spacing:-1.2px;margin:6px 0 9px;color:var(--sv-text)}.home-v2-hero p{font-size:16px;line-height:1.48;color:#c0c7cc;margin:0;max-width:720px}
.kick-card{background:linear-gradient(135deg,#111a22,#17232d);border:1px solid #2d3943;border-radius:18px;padding:17px 16px;margin:0 0 14px}.kick-top{display:flex;justify-content:space-between;align-items:center;gap:12px}.kick-label{font-size:12px;font-weight:900;letter-spacing:.7px;color:var(--sv-gold2);text-transform:uppercase}.kick-date{font-size:12px;color:var(--sv-muted)}.kick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}.kick-unit{background:#0b1218;border:1px solid #25313a;border-radius:13px;padding:11px 6px;text-align:center}.kick-unit strong{display:block;font-size:30px;line-height:1;color:#fff;letter-spacing:-1px}.kick-unit span{display:block;margin-top:5px;font-size:10px;font-weight:800;color:#8f9ba3;text-transform:uppercase;letter-spacing:.5px}
.home-v2-section{font-size:22px;font-weight:950;letter-spacing:-.5px;color:#f7f7f5;margin:18px 1px 9px}.home-v2-sub{font-size:14px;color:var(--sv-muted);line-height:1.4;margin:-4px 1px 10px}.home-action-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:8px 0 14px}.home-action{background:#101820;border:1px solid #28343e;border-radius:16px;padding:15px 13px;min-height:108px}.home-action span{font-size:22px}.home-action b{display:block;font-size:16px;margin:7px 0 3px;color:#fff}.home-action p{font-size:12px;line-height:1.35;color:#9ca7af;margin:0}.home-edge-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:7px 0 15px}.home-edge{background:#101820;border:1px solid #27333d;border-radius:16px;padding:15px}.home-edge small{font-size:10px;font-weight:900;letter-spacing:.6px;color:var(--sv-gold2);text-transform:uppercase}.home-edge b{display:block;font-size:19px;color:#fff;margin:6px 0 4px}.home-edge p{font-size:13px;line-height:1.42;color:#aab3b9;margin:0}.leader-row{display:flex;justify-content:space-between;gap:12px;align-items:center;border-top:1px solid #222d35;padding:10px 0}.leader-row:first-of-type{border-top:0}.leader-name{font-size:14px;font-weight:850;color:#fff}.leader-meta{font-size:11px;color:#8f9aa2;margin-top:2px}.leader-stat{font-size:17px;font-weight:950;color:var(--sv-gold2);white-space:nowrap}
.news-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px;margin-bottom:14px}.news-card{display:block;background:#101820;border:1px solid #27333d;border-radius:17px;overflow:hidden;color:#fff!important;text-decoration:none!important;min-height:220px}.news-thumb{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#18232c}.news-body{padding:13px}.news-meta{font-size:10px;font-weight:900;color:var(--sv-gold2);text-transform:uppercase;letter-spacing:.55px}.news-title{font-size:16px;font-weight:900;line-height:1.25;margin:5px 0 6px;color:#fff}.news-desc{font-size:12.5px;line-height:1.4;color:#aeb8bf;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.news-link{font-size:11px;font-weight:900;color:var(--sv-gold2);margin-top:9px}.news-empty{background:#101820;border:1px solid #27333d;border-radius:16px;padding:16px;color:#aeb8bf;font-size:14px}
@media(max-width:520px){.home-v2-hero{padding:20px 16px}.home-v2-hero h1{font-size:31px}.home-v2-hero p{font-size:15px}.kick-grid{gap:6px}.kick-unit strong{font-size:26px}.home-action-grid{grid-template-columns:1fr}.home-action{min-height:auto;padding:14px}.home-edge-grid{grid-template-columns:1fr}.news-grid{grid-template-columns:1fr}.news-card{min-height:0}.home-v2-section{font-size:21px}.news-title{font-size:17px}.news-desc{font-size:13.5px}}
</style>'''


def go(page: str) -> None:
    st.query_params["page"] = page
    for key in ("player", "hint", "ret", "draft"):
        try:
            del st.query_params[key]
        except Exception:
            pass
    st.rerun()


def render_countdown() -> None:
    html_block = f'''<div class="kick-card"><div class="kick-top"><div class="kick-label">NFL Kickoff</div><div class="kick-date">September 9 · 8:20 PM ET</div></div><div class="kick-grid"><div class="kick-unit"><strong id="d">—</strong><span>Days</span></div><div class="kick-unit"><strong id="h">—</strong><span>Hours</span></div><div class="kick-unit"><strong id="m">—</strong><span>Min</span></div><div class="kick-unit"><strong id="s">—</strong><span>Sec</span></div></div></div><script>(function(){{const target=new Date('{KICKOFF_ISO}').getTime();function tick(){{let x=Math.max(0,target-Date.now());const d=Math.floor(x/86400000);x%=86400000;const h=Math.floor(x/3600000);x%=3600000;const m=Math.floor(x/60000);const s=Math.floor((x%60000)/1000);for(const [id,v] of [['d',d],['h',h],['m',m],['s',s]]){{const e=document.getElementById(id);if(e)e.textContent=String(v).padStart(2,'0')}}}}tick();setInterval(tick,1000)}})()</script>'''
    components.html(CSS + html_block, height=172, scrolling=False)


def _news() -> list[dict]:
    try:
        data = json.loads(NEWS_PATH.read_text(encoding="utf-8"))
        return list(data.get("articles") or [])
    except Exception:
        return []


def _edge_leaders(players: pd.DataFrame, load_weekly, weekly_name_col, espn_ppr) -> tuple[list[dict], list[dict]]:
    try:
        w = load_weekly().copy()
        nc = weekly_name_col(w)
        if not nc or "season" not in w.columns or "week" not in w.columns:
            return [], []
        w["_ppr"] = espn_ppr(w)
        w = w.loc[pd.to_numeric(w["season"], errors="coerce").eq(2025)]
        w = w.loc[pd.to_numeric(w["week"], errors="coerce").between(1, 18, inclusive="both")]
        w = w.loc[w["_ppr"].notna()].copy()
        current = players[["name", "pos"]].drop_duplicates().copy()
        current["_key"] = current["name"].astype(str).str.casefold()
        w["_key"] = w[nc].astype(str).str.casefold()
        w = w.merge(current[["_key", "name", "pos"]], on="_key", how="inner")
        w = w.loc[w["pos"].astype(str).isin(["RB", "WR", "TE", "QB"])]
        g = w.groupby(["name", "pos"], as_index=False).agg(games=("_ppr", "count"), ppg=("_ppr", "mean"), rate15=("_ppr", lambda x: (x >= 15).mean()*100), boom25=("_ppr", lambda x: (x >= 25).mean()*100))
        g = g.loc[g["games"] >= 8]
        consistency = g.sort_values(["rate15", "ppg"], ascending=False).head(3).to_dict("records")
        ceiling = g.sort_values(["boom25", "ppg"], ascending=False).head(3).to_dict("records")
        return consistency, ceiling
    except Exception:
        return [], []


def _leader_html(rows: list[dict], stat: str, suffix: str) -> str:
    if not rows:
        return '<div class="leader-row"><div><div class="leader-name">Historical leader data unavailable</div><div class="leader-meta">No estimate substituted</div></div><div class="leader-stat">—</div></div>'
    out=[]
    for r in rows:
        val=float(r.get(stat,0))
        out.append(f'<div class="leader-row"><div><div class="leader-name">{html.escape(str(r.get("name","")))}</div><div class="leader-meta">{html.escape(str(r.get("pos","")))} · {int(r.get("games",0))} games · {float(r.get("ppg",0)):.1f} PPG</div></div><div class="leader-stat">{val:.0f}{suffix}</div></div>')
    return ''.join(out)


def render_home_v2(players: pd.DataFrame, load_weekly, weekly_name_col, espn_ppr) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('''<div class="home-v2"><div class="home-v2-hero"><div class="home-v2-kicker">Shiva Says</div><h1>Win the decision in front of you.</h1><p>Draft smarter. Protect your weekly floor. Keep real ceiling on the roster. Shiva turns verified history, current context and league state into fast fantasy decisions.</p></div></div>''', unsafe_allow_html=True)
    render_countdown()

    st.markdown('<div class="home-v2-section">Your War Room</div><div class="home-v2-sub">The four places you should need most — one tap away.</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button("◫  Draft", use_container_width=True, key="home_go_draft"): go("Draft")
    with c2:
        if st.button("✦  Coach", use_container_width=True, key="home_go_coach"): go("Coach")
    with c3:
        if st.button("▤  Guide", use_container_width=True, key="home_go_guide"): go("Guide")
    with c4:
        if st.button("◎  Players", use_container_width=True, key="home_go_players"): go("Players")

    consistency, ceiling = _edge_leaders(players, load_weekly, weekly_name_col, espn_ppr)
    st.markdown('<div class="home-v2-section">The Shiva Edge</div><div class="home-v2-sub">Historical evidence, not a mystery score.</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-edge-grid"><div class="home-edge"><small>Raise the floor</small><b>Repeatable 15+ scoring</b><p>Players who most consistently cleared 15 PPR points in the latest completed season.</p>'+_leader_html(consistency,"rate15","%")+'</div><div class="home-edge"><small>Keep the ceiling</small><b>Week-winning upside</b><p>Players who most often cleared 25 PPR points in the latest completed season.</p>'+_leader_html(ceiling,"boom25","%")+'</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="home-v2-section">Shiva Blast</div><div class="home-v2-sub">Current ESPN fantasy/NFL context with the article image and the actual story link.</div>', unsafe_allow_html=True)
    articles = [a for a in _news() if a.get("headline")][:6]
    if not articles:
        st.markdown('<div class="news-empty">Current verified news is temporarily unavailable. Shiva will keep the last verified snapshot instead of inventing headlines.</div>', unsafe_allow_html=True)
        return
    cards=[]
    for a in articles:
        url=html.escape(str(a.get("url") or "#"), quote=True)
        image=html.escape(str(a.get("image") or ""), quote=True)
        headline=html.escape(str(a.get("headline") or ""))
        desc=html.escape(str(a.get("description") or ""))
        published=str(a.get("published") or "")
        try:
            dt=datetime.fromisoformat(published.replace("Z","+00:00")); meta=dt.strftime("ESPN · %b %d")
        except Exception:
            meta="ESPN"
        thumb=f'<img class="news-thumb" src="{image}" alt="" loading="lazy">' if image else '<div class="news-thumb"></div>'
        cards.append(f'<a class="news-card" href="{url}" target="_blank" rel="noopener noreferrer">{thumb}<div class="news-body"><div class="news-meta">{meta}</div><div class="news-title">{headline}</div><p class="news-desc">{desc}</p><div class="news-link">Open story →</div></div></a>')
    st.markdown('<div class="news-grid">'+''.join(cards)+'</div>', unsafe_allow_html=True)
