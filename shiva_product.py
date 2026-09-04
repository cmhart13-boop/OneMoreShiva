from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st

from shiva_live import LeagueAuth, fetch_league, fetch_player_pool, parse_free_agents, parse_league, player_news, team_game_context, team_game_day
from shiva_coach import player_evidence, compare_call


CSS = r'''<style>
.product-tabs div[role="radiogroup"]{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:7px!important;margin-bottom:10px!important}.product-tabs label{min-height:52px!important;border-radius:12px!important}.product-tabs label p{font-size:11px!important;white-space:normal!important;text-align:center!important}.product-hero{padding:17px;border:1px solid rgba(216,179,91,.25);border-radius:16px;background:linear-gradient(145deg,#171f26,#0b1116);margin:4px 0 12px}.product-hero span,.edge-card>span,.call-card>span,.watch-item>span{font-size:9px;letter-spacing:.8px;font-weight:950;color:#d8b35b}.product-hero h2{font-size:25px;line-height:1.04;margin:4px 0 6px;color:#fff}.product-hero p{font-size:13px;line-height:1.42;color:#aab5bd;margin:0}.edge-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:8px 0 12px}.edge-card{border:1px solid rgba(202,211,218,.14);background:#0f171e;border-radius:14px;padding:13px;min-height:110px}.edge-card b{display:block;color:#fff;font-size:17px;margin:4px 0}.edge-card p{font-size:12px;line-height:1.4;color:#9eabb5;margin:0}.call-card{border:1px solid rgba(216,179,91,.35);background:linear-gradient(145deg,#211f17,#11100c);border-radius:14px;padding:14px;margin:10px 0}.call-card b{display:block;font-size:19px;color:#fff;margin:4px 0}.call-card p{font-size:12.5px;line-height:1.42;color:#b8bec3;margin:0}.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:8px 0}.metric{background:#0d141a;border:1px solid rgba(202,211,218,.12);border-radius:11px;padding:9px;text-align:center}.metric b{display:block;font-size:20px;color:#fff}.metric span{font-size:8px;text-transform:uppercase;color:#8f9ca6;font-weight:900}.table-note{font-size:11px;color:#8f9ca6;line-height:1.4;margin:6px 1px 10px}.watch-item{border:1px solid rgba(202,211,218,.13);background:#0f171e;border-radius:13px;padding:12px;margin:7px 0}.watch-item b{display:block;font-size:14px;color:#fff;margin:3px 0}.watch-item p{font-size:11.5px;line-height:1.42;color:#9eabb5;margin:0}.why-box{border-left:2px solid #d8b35b;padding:8px 10px;margin:7px 0;background:#0c1217;border-radius:0 9px 9px 0;color:#b3bcc3;font-size:12px;line-height:1.45}.league-live{display:inline-block;font-size:9px;font-weight:950;letter-spacing:.7px;color:#7de0a5;border:1px solid rgba(97,208,149,.3);background:rgba(97,208,149,.08);border-radius:999px;padding:5px 8px;margin:2px 0 8px}.league-off{display:inline-block;font-size:9px;font-weight:950;letter-spacing:.7px;color:#e1bd68;border:1px solid rgba(216,179,91,.3);background:rgba(216,179,91,.08);border-radius:999px;padding:5px 8px;margin:2px 0 8px}@media(max-width:430px){.edge-grid{grid-template-columns:1fr}.metric-grid{grid-template-columns:repeat(2,1fr)}.product-tabs div[role="radiogroup"]{grid-template-columns:repeat(4,minmax(0,1fr))!important}.product-tabs label p{font-size:9.5px!important}.product-hero h2{font-size:23px}}
\n/* COACH UX V3 */\n.st-key-coach_tab_pills{margin:8px 0 15px!important}.st-key-coach_tab_pills .stButton>button{min-height:48px!important;border-radius:11px!important;background:#0d161d!important;border:1px solid #30404b!important;color:#9eabb3!important;font-size:12px!important;font-weight:950!important;letter-spacing:.35px!important;box-shadow:none!important}.st-key-coach_tab_pills .stButton>button[kind="primary"]{background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;border-color:rgba(240,216,143,.72)!important;color:#fff!important;box-shadow:0 0 0 1px rgba(213,177,92,.12),0 0 18px rgba(213,177,92,.12)!important}.product-hero{padding:21px 18px!important;border-radius:18px!important;margin:6px 0 15px!important}.product-hero>span{font-size:11px!important;letter-spacing:.8px!important}.product-hero h2{font-size:31px!important;line-height:1.04!important;margin:6px 0 8px!important}.product-hero p{font-size:15px!important;line-height:1.5!important;color:#b8c1c7!important}.edge-card{padding:16px!important;border-radius:15px!important}.edge-card b{font-size:18px!important}.edge-card p{font-size:14px!important;line-height:1.48!important}.compare-card,.package-card,.watch-card,.lineup-card{border-radius:15px!important}.compare-card b,.package-card b,.watch-card b{font-size:16px!important}.compare-card p,.package-card p,.watch-card p{font-size:13.5px!important;line-height:1.45!important}@media(max-width:560px){.product-tabs div[role="radiogroup"]{grid-template-columns:repeat(2,minmax(0,1fr))!important}.product-tabs label{min-height:60px!important}.product-tabs label p{font-size:13px!important}.product-hero h2{font-size:29px!important}.product-hero p{font-size:14.5px!important}}\n</style>'''


def inject_css():
    st.markdown(CSS,unsafe_allow_html=True)


def _num(v, digits=1, suffix=""):
    try:
        if pd.isna(v): return "—"
        return f"{float(v):.{digits}f}{suffix}"
    except Exception:
        return "—"


def _value_score(e: dict) -> float:
    vals=[]
    for key,w in (("floor",1.35),("ppg",1.0),("ceiling",.45),("recent",.35)):
        v=e.get(key)
        if v is not None and not pd.isna(v): vals.append(float(v)*w)
    r=e.get("rate15")
    if r is not None and not pd.isna(r): vals.append(float(r)*.11)
    b=e.get("bust10")
    if b is not None and not pd.isna(b): vals.append(-float(b)*.09)
    rank=e.get("rank")
    if rank is not None and not pd.isna(rank): vals.append(max(0,220-float(rank))*.08)
    return float(sum(vals))


def _evidence(players, load_weekly, weekly_for_player, espn_ppr, name: str) -> dict:
    return player_evidence(players,load_weekly,weekly_for_player,espn_ppr,name)


def _league_state() -> dict | None:
    v=st.session_state.get("shiva_league_state")
    return v if isinstance(v,dict) else None


def _user_team_id() -> int | None:
    v=st.session_state.get("shiva_user_team_id")
    try:return int(v)
    except Exception:return None


def render_league_sync():
    st.markdown("<div class='product-hero'><span>LEAGUE CONNECTION</span><h2>Bring ESPN into Shiva.</h2><p>Shiva stays the intelligence layer. ESPN remains the league platform.</p></div>",unsafe_allow_html=True)
    state=_league_state()
    if state:
        st.markdown("<div class='league-live'>● ESPN LEAGUE CONNECTED</div>",unsafe_allow_html=True)
        meta=state.get("meta",{})
        st.write(f"**{meta.get('name','ESPN League')}** · {meta.get('season','')} · scoring period {meta.get('scoring_period','—')}")
        if st.button("Disconnect league",use_container_width=True):
            for k in ("shiva_league_state","shiva_user_team_id"): st.session_state.pop(k,None)
            st.rerun()
        teams=state.get("teams")
        if isinstance(teams,pd.DataFrame) and not teams.empty:
            labels={int(r.team_id):str(r.team) for r in teams.itertuples()}
            ids=list(labels)
            current=_user_team_id()
            idx=ids.index(current) if current in ids else 0
            chosen=st.selectbox("Your team",ids,index=idx,format_func=lambda x:labels.get(int(x),str(x)),key="league_team_select")
            st.session_state["shiva_user_team_id"]=int(chosen)
        return
    st.markdown("<div class='league-off'>NOT CONNECTED</div>",unsafe_allow_html=True)
    st.caption("Public ESPN leagues usually need only league ID and season. Private leagues also require your ESPN SWID and espn_s2 cookies. They are kept only in this Streamlit session; Shiva does not write them to the repository.")
    c1,c2=st.columns(2)
    with c1: league_id=st.text_input("ESPN League ID",key="espn_league_id")
    with c2: season=st.number_input("Season",min_value=2014,max_value=2100,value=2026,step=1,key="espn_season")
    with st.expander("Private league credentials"):
        swid=st.text_input("SWID",type="password",key="espn_swid")
        espn_s2=st.text_input("espn_s2",type="password",key="espn_s2")
    if st.button("Connect ESPN league",type="primary",use_container_width=True):
        if not str(league_id).strip(): st.error("Enter the ESPN league ID.");return
        try:
            auth=LeagueAuth(str(league_id).strip(),int(season),swid,espn_s2)
            raw=fetch_league(auth)
            parsed=parse_league(raw)
            try: fa=parse_free_agents(fetch_player_pool(auth))
            except Exception: fa=pd.DataFrame()
            st.session_state["shiva_league_state"]={"meta":{k:parsed.get(k) for k in ("league_id","season","name","scoring_period","matchup_period")},"teams":parsed["teams"],"roster":parsed["roster"],"free_agents":fa,"auth":auth}
            st.rerun()
        except Exception as exc:
            st.error(f"ESPN connection failed: {exc}")


def _roster_names() -> list[str]:
    state=_league_state(); tid=_user_team_id()
    if not state or tid is None:return []
    r=state.get("roster")
    if not isinstance(r,pd.DataFrame) or r.empty:return []
    return r.loc[r["team_id"].eq(tid),"player"].dropna().astype(str).tolist()


def _free_agent_names() -> list[str]:
    state=_league_state()
    if not state:return []
    f=state.get("free_agents")
    if not isinstance(f,pd.DataFrame) or f.empty:return []
    return f["player"].dropna().astype(str).tolist()


def _live_context_block(e: dict) -> str:
    name=str(e.get("name") or "");team=str(e.get("team") or "")
    ctx=team_game_context(team)
    schedule="Current ESPN schedule context unavailable."
    if ctx:
        opp=html.escape(str(ctx.get("opponent") or "TBD"))
        side="vs" if str(ctx.get("home_away") or "").lower()=="home" else "at" if str(ctx.get("home_away") or "").lower()=="away" else "vs"
        schedule=f"{html.escape(team)} · {html.escape(str(ctx.get('day') or ''))} · {side} {opp}"
    try:hits=player_news(name,limit=2)
    except Exception:hits=[]
    news=[]
    for h in hits:
        headline=html.escape(str(h.get("headline") or ""))
        url=html.escape(str(h.get("url") or ""),quote=True)
        if headline:
            news.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{headline}</a>' if url else headline)
    news_html="<br>".join(news) if news else "No current ESPN feed item mentions this player."
    return f"<div class='watch-item'><span>CURRENT ESPN CONTEXT</span><b>{html.escape(name)}</b><p>{schedule}</p><p>{news_html}</p></div>"


def render_start_sit(players,load_weekly,weekly_for_player,espn_ppr):
    roster=[n for n in _roster_names() if n in set(players["name"].astype(str))]
    names=roster or players["name"].dropna().astype(str).drop_duplicates().tolist()
    st.markdown("<div class='product-hero'><span>SHIVA SAYS</span><h2>Start / Sit</h2><p>Make the call quickly. Open the why only when you want the evidence.</p></div>",unsafe_allow_html=True)
    if len(names)<2: st.info("Connect a league or load player data to compare starters.");return
    c1,c2=st.columns(2)
    with c1:a=st.selectbox("Player A",names,index=0,key="ss_a")
    with c2:b=st.selectbox("Player B",names,index=min(1,len(names)-1),key="ss_b")
    if a==b:st.info("Choose two different players.");return
    ea=_evidence(players,load_weekly,weekly_for_player,espn_ppr,a); eb=_evidence(players,load_weekly,weekly_for_player,espn_ppr,b)
    winner,reasons=compare_call(ea,eb)
    loser=b if winner==a else a
    st.markdown(f"<div class='call-card'><span>SHIVA SAYS</span><b>Start {html.escape(winner)}</b><p>Over {html.escape(loser)}, based on the strongest verified combination of weekly floor, ceiling, consistency and current ranking context.</p></div>",unsafe_allow_html=True)
    for e in (ea,eb):
        st.markdown(f"<div class='metric-grid'><div class='metric'><b>{html.escape(e['name'])}</b><span>Player</span></div><div class='metric'><b>{_num(e.get('floor'))}</b><span>Floor</span></div><div class='metric'><b>{_num(e.get('ceiling'))}</b><span>Ceiling</span></div><div class='metric'><b>{_num(e.get('rate15'),0,'%')}</b><span>15+ Weeks</span></div></div>",unsafe_allow_html=True)
    st.markdown("<div class='table-note'>Live schedule and news are shown separately from the recommendation so current context is visible without pretending it is a verified weekly projection.</div>",unsafe_allow_html=True)
    st.markdown("<div class='edge-grid'>"+_live_context_block(ea)+_live_context_block(eb)+"</div>",unsafe_allow_html=True)
    with st.expander("Why this call?"):
        if reasons:
            for r in reasons: st.markdown(f"- {r}")
        else: st.write("The recommendation comes from Shiva's transparent evidence score: floor first, then PPG/consistency, bust avoidance, ceiling and current rank context.")
        st.caption("This does not invent a weekly projection or confidence percentage. When verified 2026 weekly projections/opponent data are available, they can be added as a separate current-season layer.")


def render_waivers(players,load_weekly,weekly_for_player,espn_ppr):
    st.markdown("<div class='product-hero'><span>SHIVA SAYS</span><h2>Waiver Wire</h2><p>Find players who can improve your weekly floor or create actual lineup-winning upside.</p></div>",unsafe_allow_html=True)
    available=_free_agent_names()
    source="your synced ESPN free-agent pool" if available else "the current player database (connect ESPN to restrict this to players actually available in your league)"
    if not available: available=players["name"].dropna().astype(str).head(180).tolist()
    pos=st.selectbox("Position",["ALL","RB","WR","QB","TE"],key="waiver_pos")
    pmap=players.set_index("name")["pos"].astype(str).to_dict() if "pos" in players.columns else {}
    candidates=[n for n in available if n in pmap and (pos=="ALL" or pmap.get(n)==pos)]
    scored=[]
    for n in candidates[:220]:
        e=_evidence(players,load_weekly,weekly_for_player,espn_ppr,n); scored.append((n,_value_score(e),e))
    scored.sort(key=lambda x:x[1],reverse=True)
    st.caption(f"Ranked from {source}. Historical evidence and current ranking context only; no made-up ownership or projection data.")
    for i,(n,score,e) in enumerate(scored[:12],1):
        st.markdown(f"<div class='watch-item'><span>WAIVER TARGET #{i}</span><b>{html.escape(n)} · {html.escape(str(e.get('pos','')))}</b><p>Floor {_num(e.get('floor'))} · Ceiling {_num(e.get('ceiling'))} · 15+ {_num(e.get('rate15'),0,'%')} · Bust &lt;10 {_num(e.get('bust10'),0,'%')}</p></div>",unsafe_allow_html=True)
    roster=[n for n in _roster_names() if n in pmap]
    if roster and scored:
        with st.expander("Who could I drop?"):
            drops=[]
            for n in roster:
                e=_evidence(players,load_weekly,weekly_for_player,espn_ppr,n); drops.append((n,_value_score(e)))
            drops.sort(key=lambda x:x[1])
            for n,_ in drops[:5]: st.write(f"• {n}")
            st.caption("Drop candidates are evidence-ranked only. Shiva does not auto-drop a player without verified roster/availability context.")


def render_trade(players,load_weekly,weekly_for_player,espn_ppr):
    st.markdown("<div class='product-hero'><span>SHIVA SAYS</span><h2>Trade Analyzer</h2><p>Compare packages by what they do to your floor, ceiling and roster value — not by a fake single-number trade chart.</p></div>",unsafe_allow_html=True)
    all_names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    mine=[n for n in _roster_names() if n in set(all_names)] or all_names
    receive_pool=all_names
    state=_league_state();tid=_user_team_id()
    if state and tid is not None:
        teams=state.get("teams");roster=state.get("roster")
        if isinstance(teams,pd.DataFrame) and isinstance(roster,pd.DataFrame) and not teams.empty and not roster.empty:
            options=[int(x) for x in teams["team_id"].dropna().tolist() if int(x)!=tid]
            labels={int(r.team_id):str(r.team) for r in teams.itertuples()}
            if options:
                partner=st.selectbox("Trade partner",options,format_func=lambda x:labels.get(int(x),str(x)),key="trade_partner")
                receive_pool=[n for n in roster.loc[roster["team_id"].eq(int(partner)),"player"].dropna().astype(str).tolist() if n in set(all_names)]
                st.caption("Incoming-player choices are restricted to the selected ESPN roster.")
    give=st.multiselect("You give",mine,max_selections=3,key="trade_give")
    receive=st.multiselect("You receive",receive_pool,max_selections=3,key="trade_get")
    if not give or not receive:return
    def pkg(names):
        es=[_evidence(players,load_weekly,weekly_for_player,espn_ppr,n) for n in names]
        return es,sum(_value_score(e) for e in es)
    eg,sg=pkg(give); er,sr=pkg(receive)
    winner="ACCEPT" if sr>sg else "DECLINE"
    diff=abs(sr-sg)
    st.markdown(f"<div class='call-card'><span>SHIVA SAYS</span><b>{winner}</b><p>The {'incoming' if sr>sg else 'outgoing'} package has the stronger evidence-weighted profile. Difference score: {diff:.1f}. Use the Why layer before making the move.</p></div>",unsafe_allow_html=True)
    with st.expander("Why?"):
        for label,es in (("Giving",eg),("Receiving",er)):
            st.markdown(f"**{label}**")
            for e in es: st.write(f"{e['name']}: floor {_num(e.get('floor'))}, ceiling {_num(e.get('ceiling'))}, 15+ {_num(e.get('rate15'),0,'%')}, current rank {_num(e.get('rank'),0)}")
        st.caption("The analyzer intentionally does not claim future points that are not in a verified current-season projection dataset.")


def render_lineup(players):
    st.markdown("<div class='product-hero'><span>SHIVA MOMENT</span><h2>Lineup Check</h2><p>Catch the tiny roster-management mistakes that quietly cost games.</p></div>",unsafe_allow_html=True)
    state=_league_state(); tid=_user_team_id()
    if not state or tid is None:
        st.info("Connect your ESPN league to run automatic roster checks.");return
    roster=state.get("roster")
    if not isinstance(roster,pd.DataFrame) or roster.empty:return
    mine=roster.loc[roster["team_id"].eq(tid)].copy()
    flex=mine.loc[mine["slot"].eq("FLEX")]
    if flex.empty:
        st.markdown("<div class='call-card'><span>LINEUP CHECK</span><b>No FLEX player detected.</b><p>Shiva will automatically flag a Thursday FLEX trap when the synced ESPN lineup has one.</p></div>",unsafe_allow_html=True);return
    team_map=players.set_index("name")["team"].astype(str).to_dict() if "team" in players.columns else {}
    fired=False
    for r in flex.itertuples():
        team=team_map.get(str(r.player),"")
        day,_=team_game_day(team)
        if day=="Thursday":
            fired=True
            pos=str(players.loc[players["name"].eq(str(r.player)),"pos"].iloc[0]) if (players["name"].eq(str(r.player))).any() else "positional"
            st.markdown(f"<div class='call-card'><span>SHIVA MOMENT</span><b>Move {html.escape(str(r.player))} out of FLEX.</b><p>{html.escape(team)} plays Thursday. Put him in the {html.escape(pos)} slot so FLEX stays available for Sunday injury and availability changes.</p></div>",unsafe_allow_html=True)
    if not fired:
        st.markdown("<div class='call-card'><span>LINEUP CHECK</span><b>No Thursday FLEX trap detected.</b><p>Your currently synced FLEX slot does not show the specific Thursday mistake Shiva is watching for.</p></div>",unsafe_allow_html=True)
    st.markdown("<div class='edge-grid'><div class='edge-card'><span>SHIVA MOMENT</span><b>Late-game flexibility</b><p>Keep later-starting players in FLEX whenever the positional slots allow it.</p></div><div class='edge-card'><span>SHIVA MOMENT</span><b>Questionable players</b><p>Put early-game questionable players in positional slots so a late scratch does not collapse your replacement options.</p></div></div>",unsafe_allow_html=True)


def _history_path() -> Path:
    return Path(__file__).with_name("data")/"injury_mentions.csv"


def render_watch(players):
    st.markdown("<div class='product-hero'><span>PLAYER WATCH</span><h2>News + injury context</h2><p>See the current ESPN feed beside Shiva's accumulated injury/news mentions.</p></div>",unsafe_allow_html=True)
    names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    who=st.selectbox("Player",names,key="watch_name")
    try:hits=player_news(who)
    except Exception:hits=[]
    st.markdown("#### Current ESPN mentions")
    if not hits:st.info("No current ESPN feed item mentions this player.")
    for h in hits:
        link=f"<a href='{html.escape(str(h.get('url') or ''),quote=True)}' target='_blank'>Open story →</a>" if h.get("url") else ""
        st.markdown(f"<div class='watch-item'><span>ESPN</span><b>{html.escape(str(h.get('headline') or ''))}</b><p>{html.escape(str(h.get('description') or ''))}</p>{link}</div>",unsafe_allow_html=True)
    p=_history_path()
    st.markdown("#### Shiva history")
    if p.exists():
        try:
            df=pd.read_csv(p)
            text=(df.get("headline",pd.Series(dtype=str)).astype(str)+" "+df.get("description",pd.Series(dtype=str)).astype(str))
            mask=text.str.contains(str(who),case=False,regex=False)
            if not mask.any():
                last=str(who).split()[-1]
                same_last=players["name"].dropna().astype(str).map(lambda x:str(x).split()[-1].casefold()==last.casefold()).sum()
                if same_last==1:mask=text.str.contains(last,case=False,regex=False)
            show=df.loc[mask].sort_values("captured_at",ascending=False).head(12)
            if show.empty:st.caption("No stored injury/news mention for this player yet.")
            else:
                for r in show.itertuples(): st.markdown(f"<div class='watch-item'><span>{html.escape(str(getattr(r,'captured_at',''))[:10])}</span><b>{html.escape(str(getattr(r,'headline','')))}</b><p>{html.escape(str(getattr(r,'description','')))}</p></div>",unsafe_allow_html=True)
        except Exception:st.caption("Stored injury history could not be read.")
    else:st.caption("The persistent injury/news log will populate from the scheduled verified-source collector.")


def render_analysts(load_weekly,espn_ppr,weekly_name_col):
    st.markdown("<div class='product-hero'><span>ANALYZE THE ANALYSTS</span><h2>Who actually gets it right?</h2><p>Import weekly rankings snapshots. Shiva grades them against actual Full-PPR results over time.</p></div>",unsafe_allow_html=True)
    sample=pd.DataFrame([{"analyst":"Analyst Name","player":"Player Name","rank":1,"season":2025,"week":1,"position":"RB"}])
    st.download_button("Download rankings template",sample.to_csv(index=False).encode(),"shiva_analyst_rankings_template.csv","text/csv",use_container_width=True)
    up=st.file_uploader("Upload one or more rankings snapshots",type=["csv"],accept_multiple_files=True,key="analyst_files")
    if not up:return
    ranks=[]
    for f in up:
        try:ranks.append(pd.read_csv(f))
        except Exception:pass
    if not ranks:st.error("No readable ranking snapshots.");return
    r=pd.concat(ranks,ignore_index=True)
    req={"analyst","player","rank","season","week"}
    if not req.issubset(r.columns):st.error("Required columns: analyst, player, rank, season, week. Optional: position.");return
    w=load_weekly().copy(); nc=weekly_name_col(w)
    if not nc:st.error("Historical weekly player-name column unavailable.");return
    def key(v):return "".join(ch for ch in str(v).casefold() if ch.isalnum())
    w["_key"]=w[nc].astype(str).map(key);w["actual_ppr"]=espn_ppr(w)
    r["_key"]=r["player"].astype(str).map(key)
    merged=r.merge(w[["_key","season","week","actual_ppr"]],on=["_key","season","week"],how="inner")
    if merged.empty:st.info("No uploaded rows matched verified weekly results.");return
    merged["actual_rank"]=merged.groupby(["season","week"])["actual_ppr"].rank(method="min",ascending=False)
    merged["abs_error"]=(pd.to_numeric(merged["rank"],errors="coerce")-merged["actual_rank"]).abs()
    scores=merged.groupby("analyst").agg(weeks=("week","nunique"),players=("_key","count"),mean_rank_error=("abs_error","mean")).reset_index().sort_values("mean_rank_error")
    st.dataframe(scores,use_container_width=True,hide_index=True)
    st.caption("Lower mean rank error is better. The grading uses the historical weekly dataset already inside One More Shiva.")


def _league_power_board(players,load_weekly,weekly_for_player,espn_ppr) -> pd.DataFrame:
    state=_league_state()
    if not state:return pd.DataFrame()
    teams=state.get("teams");roster=state.get("roster")
    if not isinstance(teams,pd.DataFrame) or not isinstance(roster,pd.DataFrame) or teams.empty or roster.empty:return pd.DataFrame()
    valid=set(players["name"].dropna().astype(str))
    rows=[]
    for t in teams.itertuples():
        tid=int(t.team_id);mine=roster.loc[roster["team_id"].eq(tid)].copy()
        scored=[]
        for r in mine.itertuples():
            name=str(r.player)
            if name not in valid:continue
            e=_evidence(players,load_weekly,weekly_for_player,espn_ppr,name)
            scored.append((str(getattr(r,"slot","")),_value_score(e),e))
        if not scored:continue
        starters=[x for x in scored if x[0] not in {"BE","IR"}]
        chosen=starters if len(starters)>=5 else sorted(scored,key=lambda x:x[1],reverse=True)[:8]
        total=sum(x[1] for x in chosen)
        floors=[float(x[2]["floor"]) for x in chosen if x[2].get("floor") is not None and not pd.isna(x[2].get("floor"))]
        ceilings=[float(x[2]["ceiling"]) for x in chosen if x[2].get("ceiling") is not None and not pd.isna(x[2].get("ceiling"))]
        rows.append({"team_id":tid,"Team":str(t.team),"Record":f"{getattr(t,'wins','—')}-{getattr(t,'losses','—')}","Evidence Score":round(total,1),"Floor":round(float(np.mean(floors)),1) if floors else np.nan,"Ceiling":round(float(np.mean(ceilings)),1) if ceilings else np.nan})
    if not rows:return pd.DataFrame()
    out=pd.DataFrame(rows).sort_values(["Evidence Score","Ceiling"],ascending=False).reset_index(drop=True)
    out.insert(0,"Shiva Rank",range(1,len(out)+1))
    return out


def _roster_build_snapshot(players) -> dict:
    names=_roster_names()
    if not names:return {}
    x=players.loc[players["name"].astype(str).isin(names)].copy()
    counts=x["pos"].astype(str).value_counts().to_dict() if not x.empty else {}
    ranks=pd.to_numeric(x.get("overall_rank"),errors="coerce").dropna() if not x.empty else pd.Series(dtype=float)
    return {"players":len(x),"rb":int(counts.get("RB",0)),"wr":int(counts.get("WR",0)),"qb":int(counts.get("QB",0)),"te":int(counts.get("TE",0)),"median_rank":float(ranks.median()) if len(ranks) else np.nan}


def render_dashboard(players,load_weekly,weekly_for_player,espn_ppr):
    state=_league_state()
    st.markdown("<div class='product-hero'><span>SHIVA SAYS</span><h2>Your fantasy decision room.</h2><p>Draft the room. Protect your floor. Preserve your ceiling. Catch the little edges before your opponent does.</p></div>",unsafe_allow_html=True)
    if state:
        st.markdown("<div class='league-live'>● ESPN LEAGUE CONNECTED</div>",unsafe_allow_html=True)
        snap=_roster_build_snapshot(players)
        if snap:
            st.markdown(f"<div class='metric-grid'><div class='metric'><b>{snap['players']}</b><span>Rostered</span></div><div class='metric'><b>{snap['rb']}/{snap['wr']}</b><span>RB / WR</span></div><div class='metric'><b>{snap['qb']}/{snap['te']}</b><span>QB / TE</span></div><div class='metric'><b>{_num(snap.get('median_rank'),0)}</b><span>Median Rank</span></div></div>",unsafe_allow_html=True)
        board=_league_power_board(players,load_weekly,weekly_for_player,espn_ppr)
        if not board.empty:
            tid=_user_team_id();mine=board.loc[board['team_id'].eq(tid)] if tid is not None else pd.DataFrame()
            if not mine.empty:
                r=mine.iloc[0]
                st.markdown(f"<div class='call-card'><span>SHIVA POWER BOARD</span><b>#{int(r['Shiva Rank'])} · {html.escape(str(r['Team']))}</b><p>Roster evidence score {float(r['Evidence Score']):.1f}. This is Shiva's roster-strength view, not an ESPN official power ranking.</p></div>",unsafe_allow_html=True)
            st.dataframe(board.drop(columns=['team_id']),use_container_width=True,hide_index=True)
            st.caption("Power Board uses the synced ESPN rosters, current ranking context and latest completed-season floor/ceiling evidence. It does not invent weekly projections or matchup strength.")
    else:st.markdown("<div class='league-off'>CONNECT ESPN FOR ROSTER-AWARE COACHING</div>",unsafe_allow_html=True)
    st.markdown("<div class='edge-grid'><div class='edge-card'><span>LINEUP EDGE</span><b>Thursday FLEX protection</b><p>Shiva checks the synced lineup for the FLEX mistake that kills Sunday replacement flexibility.</p></div><div class='edge-card'><span>DRAFT EDGE</span><b>Read the managers between picks</b><p>Position scarcity and roster construction matter more than blindly following ADP.</p></div><div class='edge-card'><span>TEAM BUILD</span><b>Raise the floor</b><p>Repeatable 15+ point weeks keep you in every matchup.</p></div><div class='edge-card'><span>TEAM BUILD</span><b>Keep the ceiling</b><p>Use selected roster spots on players with legitimate week-winning outcomes.</p></div></div>",unsafe_allow_html=True)


def _set_product_tab(tab: str) -> None:
    st.session_state["full_product_tab"] = tab


def render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col):
    inject_css()
    tabs=("Home","Start/Sit","Waivers","Trades","Lineup","Watch","Analysts","League")
    tab=st.session_state.get("full_product_tab",tabs[0])
    if tab not in tabs:
        tab=tabs[0]
    with st.container(key="coach_tab_pills"):
        for left,right in zip(tabs[::2],tabs[1::2]):
            first,second=st.columns(2,gap="small")
            with first:
                st.button(left,key=f"coach_tab_{left}",type="primary" if tab==left else "secondary",use_container_width=True,on_click=_set_product_tab,args=(left,))
            with second:
                st.button(right,key=f"coach_tab_{right}",type="primary" if tab==right else "secondary",use_container_width=True,on_click=_set_product_tab,args=(right,))
    if tab=="Home":render_dashboard(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Start/Sit":render_start_sit(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Waivers":render_waivers(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Trades":render_trade(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Lineup":render_lineup(players)
    elif tab=="Watch":render_watch(players)
    elif tab=="Analysts":render_analysts(load_weekly,espn_ppr,weekly_name_col)
    else:render_league_sync()
