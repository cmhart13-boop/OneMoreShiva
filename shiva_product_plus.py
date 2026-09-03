from __future__ import annotations

import html
import math
import numpy as np
import pandas as pd
import streamlit as st
import shiva_product as base


def _draft_grade(players, load_weekly, weekly_for_player, espn_ppr):
    state=base._league_state(); tid=base._user_team_id()
    st.markdown("<div class='product-hero'><span>SHIVA DRAFT GRADE</span><h2>Grade your actual ESPN roster.</h2><p>Shiva evaluates the team ESPN imported into Coach instead of asking you to rebuild it by hand.</p></div>",unsafe_allow_html=True)
    if not state or tid is None:
        st.info("Connect your ESPN league under League first. Once your team is selected, your roster appears here automatically.")
        return
    roster=state.get("roster")
    if not isinstance(roster,pd.DataFrame) or roster.empty:
        st.info("ESPN connected, but no roster data was returned for this league.")
        return
    mine=roster.loc[roster["team_id"].eq(int(tid))].copy()
    if mine.empty:
        st.info("Select your ESPN team under League first.")
        return
    valid=set(players["name"].dropna().astype(str))
    scored=[]
    for r in mine.itertuples():
        name=str(r.player)
        if name not in valid: continue
        e=base._evidence(players,load_weekly,weekly_for_player,espn_ppr,name)
        rank=e.get("rank")
        value=base._value_score(e)
        scored.append({"name":name,"slot":str(getattr(r,"slot","")),"pos":str(e.get("pos","")),"rank":rank,"value":value,"floor":e.get("floor"),"ceiling":e.get("ceiling"),"rate15":e.get("rate15")})
    if not scored:
        st.info("The ESPN roster imported, but Shiva could not match its player names to the current ranking database.")
        return
    starters=[x for x in scored if x["slot"] not in {"BE","IR"}]
    core=starters if len(starters)>=6 else scored
    ranks=[float(x["rank"]) for x in core if x.get("rank") is not None and not pd.isna(x.get("rank"))]
    values=[float(x["value"]) for x in core if x.get("value") is not None and not pd.isna(x.get("value"))]
    top25=sum(1 for r in ranks if r<=25); top50=sum(1 for r in ranks if r<=50); top100=sum(1 for r in ranks if r<=100)
    avg_rank=float(np.mean(ranks)) if ranks else 140.0
    median_rank=float(np.median(ranks)) if ranks else 140.0
    value_mean=float(np.mean(values)) if values else 0.0
    pos_counts={p:sum(1 for x in scored if x["pos"]==p) for p in ("QB","RB","WR","TE")}
    balance=0
    balance += 2 if pos_counts["RB"]>=4 else -2
    balance += 2 if pos_counts["WR"]>=4 else -2
    balance += 1 if pos_counts["QB"]>=1 else -4
    balance += 1 if pos_counts["TE"]>=1 else -4
    score=72.0
    score += max(-14,min(14,(85-avg_rank)*.22))
    score += min(8,top25*1.8)
    score += min(6,top50*.75)
    score += min(4,top100*.25)
    score += max(-5,min(5,(value_mean-35)*.15))
    score += balance
    score=int(round(max(48,min(98,score))))
    letter="A+" if score>=95 else "A" if score>=90 else "A-" if score>=87 else "B+" if score>=84 else "B" if score>=80 else "B-" if score>=77 else "C+" if score>=74 else "C" if score>=70 else "C-" if score>=67 else "D"
    best=sorted(scored,key=lambda x:(999 if pd.isna(x.get("rank")) else float(x.get("rank"))))[:3]
    weak=sorted(scored,key=lambda x:(-1 if pd.isna(x.get("rank")) else float(x.get("rank"))),reverse=True)[:3]
    st.markdown(f"<div class='call-card'><span>SHIVA DRAFT GRADE</span><b>{letter} · {score}/100</b><p>This grade uses the synced ESPN roster, Shiva's current rankings, roster construction and the historical floor/ceiling evidence already inside the app. It does not invent an ESPN grade or fake weekly projection.</p></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='metric-grid'><div class='metric'><b>{top25}</b><span>Top 25</span></div><div class='metric'><b>{top50}</b><span>Top 50</span></div><div class='metric'><b>{int(round(median_rank))}</b><span>Median Rank</span></div><div class='metric'><b>{len(scored)}</b><span>Matched</span></div></div>",unsafe_allow_html=True)
    st.markdown("#### Best roster anchors")
    for x in best:
        st.markdown(f"<div class='watch-item'><span>{html.escape(x['slot'] or x['pos'])}</span><b>{html.escape(x['name'])}</b><p>Current rank {base._num(x.get('rank'),0)} · Floor {base._num(x.get('floor'))} · Ceiling {base._num(x.get('ceiling'))} · 15+ {base._num(x.get('rate15'),0,'%')}</p></div>",unsafe_allow_html=True)
    with st.expander("Where the grade can improve"):
        for x in weak:
            st.write(f"• {x['name']} — current rank {base._num(x.get('rank'),0)}")
        st.caption("This is roster-quality grading from the data Shiva currently has. If ESPN exposes reliable pick-by-pick draft slots for the connected league, that can be layered in later to grade reaches and steals by exact selection number.")


COACH_TABS = ("Home", "Start/Sit", "Draft Grade", "Waivers", "Trades", "Lineup", "Watch", "Analysts", "League")


def _set_coach_tab(tab: str) -> None:
    st.session_state["full_product_tab"] = tab


def render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col):
    base.inject_css()
    if st.session_state.get("full_product_tab") not in COACH_TABS:
        st.session_state["full_product_tab"] = "Home"
    with st.container(key="coach_tab_pills"):
        for left, right in zip(COACH_TABS[::2], COACH_TABS[1::2] + (None,)):
            c1, c2 = st.columns(2, gap="small")
            with c1:
                st.button(left, key=f"coach_tab_{left}", type="primary" if st.session_state["full_product_tab"] == left else "secondary", use_container_width=True, on_click=_set_coach_tab, args=(left,))
            if right:
                with c2:
                    st.button(right, key=f"coach_tab_{right}", type="primary" if st.session_state["full_product_tab"] == right else "secondary", use_container_width=True, on_click=_set_coach_tab, args=(right,))
    tab=st.session_state["full_product_tab"]
    if tab=="Home":base.render_dashboard(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Start/Sit":base.render_start_sit(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Draft Grade":_draft_grade(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Waivers":base.render_waivers(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Trades":base.render_trade(players,load_weekly,weekly_for_player,espn_ppr)
    elif tab=="Lineup":base.render_lineup(players)
    elif tab=="Watch":base.render_watch(players)
    elif tab=="Analysts":base.render_analysts(load_weekly,espn_ppr,weekly_name_col)
    else:base.render_league_sync()
