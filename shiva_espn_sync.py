from __future__ import annotations

import html
import math
from datetime import datetime
from urllib.request import Request, urlopen
from http.cookiejar import CookieJar
from urllib.request import HTTPCookieProcessor, build_opener
import json

import pandas as pd
import streamlit as st

ESPN_POS = {1:"QB",2:"RB",3:"WR",4:"TE",5:"K",16:"DST"}
LINEUP = {0:"QB",2:"RB",4:"WR",6:"TE",16:"DST",17:"K",20:"BE",21:"IR",23:"FLEX"}

CSS = """<style>
.espn-sync-hero{margin:10px 0 14px;padding:18px;border:1px solid #263746;border-radius:17px;background:linear-gradient(145deg,#101c27,#0b141c)}
.espn-sync-hero span{font-size:11px;font-weight:950;letter-spacing:.9px;color:#d5b15c}.espn-sync-hero h3{margin:5px 0 6px;font-size:25px;color:#fff}.espn-sync-hero p{margin:0;color:#aebbc4;font-size:14px;line-height:1.45}
.espn-connected{margin:10px 0;padding:14px;border:1px solid #28503d;border-radius:15px;background:#0b1c16}.espn-connected span{font-size:10px;font-weight:900;color:#72d69d;letter-spacing:.7px}.espn-connected b{display:block;color:#fff;font-size:18px;margin-top:3px}.espn-connected p{margin:4px 0 0;color:#aebbc4;font-size:13px}
.espn-roster{display:grid;grid-template-columns:1fr;gap:8px;margin:10px 0}.espn-player{display:flex;justify-content:space-between;gap:10px;padding:11px 12px;border:1px solid #22313f;border-radius:12px;background:#0d171f}.espn-player b{font-size:14px;color:#fff}.espn-player span{font-size:11px;color:#91a0ab}.espn-player em{font-style:normal;font-size:11px;color:#d5b15c;font-weight:850}
.grade-card{margin:12px 0;padding:18px;border:1px solid #2c4150;border-radius:17px;background:linear-gradient(145deg,#14212d,#0d171f)}.grade-card .letter{font-size:54px;font-weight:950;line-height:1;color:#fff}.grade-card .score{font-size:13px;color:#d5b15c;font-weight:900}.grade-card p{color:#b4c0c8;font-size:13px;line-height:1.5;margin:8px 0 0}.grade-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:12px}.grade-row div{padding:9px;border-radius:10px;background:#0b141b;border:1px solid #21303b}.grade-row b{display:block;color:#fff;font-size:16px}.grade-row span{font-size:10px;color:#8797a3}
.start-call{margin:12px 0;padding:15px;border-radius:14px;background:#102218;border:1px solid #2d6042}.start-call span{font-size:10px;color:#72d69d;font-weight:950;letter-spacing:.8px}.start-call b{display:block;font-size:20px;color:#fff;margin:4px 0}.start-call p{font-size:13px;color:#b6c2c9;margin:0;line-height:1.45}
</style>"""


def _key(v: str) -> str:
    return "".join(ch for ch in str(v).casefold() if ch.isalnum())


def _fetch_league(league_id: str, season: int, swid: str = "", espn_s2: str = "") -> dict:
    url=(f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{int(season)}/segments/0/leagues/{league_id}"
         "?view=mTeam&view=mRoster&view=mSettings&view=mDraftDetail&view=mStatus")
    headers={"User-Agent":"Mozilla/5.0 (iPhone; One More Shiva)","Accept":"application/json"}
    if swid.strip() or espn_s2.strip():
        cookies=[]
        if swid.strip(): cookies.append("SWID="+swid.strip())
        if espn_s2.strip(): cookies.append("espn_s2="+espn_s2.strip())
        headers["Cookie"]="; ".join(cookies)
    req=Request(url,headers=headers)
    with urlopen(req,timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


def _team_name(t: dict) -> str:
    return str(t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or f"Team {t.get('id','')}").strip()


def _entry_player(entry: dict) -> dict:
    pp=(entry.get("playerPoolEntry") or {})
    p=(pp.get("player") or {})
    name=str(p.get("fullName") or p.get("name") or f"Player {entry.get('playerId','')}")
    pos=ESPN_POS.get(p.get("defaultPositionId"),str(p.get("defaultPositionId") or ""))
    slot=LINEUP.get(entry.get("lineupSlotId"),str(entry.get("lineupSlotId") or ""))
    return {"id":entry.get("playerId"),"name":name,"pos":pos,"slot":slot,"acq":entry.get("acquisitionType")}


def _rank_lookup(players: pd.DataFrame) -> dict:
    if players is None or players.empty or "name" not in players.columns: return {}
    rank_col=next((c for c in ["overall_rank","rank","consensus_rank","draft_rank"] if c in players.columns),None)
    pos_col=next((c for c in ["pos","position"] if c in players.columns),None)
    out={}
    for _,r in players.iterrows():
        name=str(r.get("name", ""))
        try: rank=float(r.get(rank_col)) if rank_col else math.nan
        except Exception: rank=math.nan
        out[_key(name)]={"rank":rank,"pos":str(r.get(pos_col,"")) if pos_col else ""}
    return out


def _draft_picks(data: dict, team_id: int) -> dict[int,int]:
    picks={}
    candidates=[]
    dd=data.get("draftDetail") or {}
    for key in ("picks","drafted","draftPicks"):
        if isinstance(dd.get(key),list): candidates.extend(dd[key])
    if isinstance(data.get("draftPicks"),list): candidates.extend(data["draftPicks"])
    for p in candidates:
        if int(p.get("teamId",-1) or -1)!=int(team_id): continue
        pid=p.get("playerId")
        overall=p.get("overallPickNumber") or p.get("overallPick") or p.get("pickNumber")
        if pid is not None and overall is not None:
            try:picks[int(pid)]=int(overall)
            except Exception:pass
    return picks


def _grade(roster: list[dict], players: pd.DataFrame, data: dict, team_id: int) -> tuple[int,str,dict,str]:
    lookup=_rank_lookup(players); picks=_draft_picks(data,team_id)
    vals=[]; starters=0; top50=0; reaches=0; steals=0
    for x in roster:
        info=lookup.get(_key(x["name"]),{})
        rank=info.get("rank",math.nan)
        if x["slot"] not in ("BE","IR"): starters+=1
        if not pd.isna(rank) and rank<=50: top50+=1
        if x.get("id") in picks and not pd.isna(rank):
            delta=float(picks[x["id"]])-float(rank)
            vals.append(max(-35,min(35,delta)))
            if delta>=10:steals+=1
            if delta<=-12:reaches+=1
        elif not pd.isna(rank):
            vals.append(max(-25,min(25,85-float(rank)))/2.5)
    base=72.0
    if vals: base+=sum(vals)/max(5,len(vals))*.85
    base+=min(8,top50*1.2)
    base-=reaches*1.5
    score=int(round(max(45,min(98,base))))
    letter="A+" if score>=95 else "A" if score>=90 else "A-" if score>=87 else "B+" if score>=84 else "B" if score>=80 else "B-" if score>=77 else "C+" if score>=74 else "C" if score>=70 else "C-" if score>=67 else "D"
    detail={"top50":top50,"steals":steals,"reaches":reaches,"ranked":len(vals)}
    if picks:
        note="Grade compares your ESPN draft slots with Shiva's current player rankings, then adjusts for roster quality and major reaches/values."
    else:
        note="ESPN did not expose pick-by-pick draft slots for this league, so the grade uses the imported roster against Shiva's current rankings and roster strength."
    return score,letter,detail,note


def _evidence(players: pd.DataFrame, name: str) -> tuple[float,str]:
    if players is None or players.empty:return (999.0,"")
    row=players.loc[players["name"].astype(str).map(_key).eq(_key(name))]
    if row.empty:return (999.0,"")
    r=row.iloc[0]
    rank_col=next((c for c in ["overall_rank","rank","consensus_rank","draft_rank"] if c in players.columns),None)
    try:rank=float(r.get(rank_col)) if rank_col else 999.0
    except Exception:rank=999.0
    return rank,str(r.get("pos",r.get("position","")))


def render_espn_coach(players: pd.DataFrame) -> None:
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown("<div class='espn-sync-hero'><span>LEAGUE SYNC</span><h3>Connect your ESPN league</h3><p>Import your ESPN team and roster into Shiva, then use it for a draft grade and roster-aware start/sit decisions.</p></div>",unsafe_allow_html=True)

    data=st.session_state.get("espn_league_data")
    selected_id=st.session_state.get("espn_team_id")
    if not data:
        with st.expander("Connect ESPN League",expanded=True):
            league_id=st.text_input("ESPN League ID",placeholder="Example: 12345678",key="espn_league_id_input")
            season=st.number_input("Season",min_value=2020,max_value=2030,value=2026,step=1,key="espn_season_input")
            st.caption("Public leagues usually need only the League ID. For a private ESPN league, open Advanced and add your ESPN cookies. They stay only in this app session.")
            with st.expander("Advanced · private league"):
                swid=st.text_input("SWID",type="password",key="espn_swid_input")
                s2=st.text_input("espn_s2",type="password",key="espn_s2_input")
            if st.button("Connect ESPN",type="primary",use_container_width=True,key="espn_connect_btn"):
                if not league_id.strip(): st.error("Enter the ESPN League ID.")
                else:
                    try:
                        with st.spinner("Syncing ESPN league…"):
                            league=_fetch_league(league_id.strip(),int(season),swid,s2)
                        if not league.get("teams"): raise ValueError("ESPN returned no teams")
                        st.session_state["espn_league_data"]=league
                        st.session_state["espn_team_id"]=None
                        st.rerun()
                    except Exception as e:
                        st.error("I couldn't connect to that ESPN league. If it is private, add SWID and espn_s2 under Advanced and try again.")
        return

    settings=data.get("settings") or {}; name=str(settings.get("name") or "ESPN League")
    teams=data.get("teams") or []
    st.markdown(f"<div class='espn-connected'><span>ESPN CONNECTED</span><b>{html.escape(name)}</b><p>{len(teams)} teams · synced this session</p></div>",unsafe_allow_html=True)
    options={int(t.get("id")): _team_name(t) for t in teams if t.get("id") is not None}
    ids=list(options)
    if not ids:return
    idx=ids.index(selected_id) if selected_id in ids else 0
    team_id=st.selectbox("Your team",ids,index=idx,format_func=lambda x:options[x],key="espn_team_select")
    st.session_state["espn_team_id"]=team_id
    team=next(t for t in teams if int(t.get("id"))==int(team_id))
    entries=((team.get("roster") or {}).get("entries") or [])
    roster=[_entry_player(e) for e in entries]
    st.session_state["espn_roster"]=roster

    c1,c2=st.columns(2)
    with c1:
        if st.button("Refresh ESPN",use_container_width=True,key="espn_refresh"):
            st.session_state.pop("espn_league_data",None);st.session_state.pop("espn_team_id",None);st.rerun()
    with c2:
        if st.button("Disconnect",use_container_width=True,key="espn_disconnect"):
            for k in ["espn_league_data","espn_team_id","espn_roster"]:st.session_state.pop(k,None)
            st.rerun()

    view=st.radio("ESPN Coach",["Roster","Draft Grade","Start / Sit"],horizontal=True,label_visibility="collapsed",key="espn_coach_view")
    if view=="Roster":
        cards=[]
        for x in sorted(roster,key=lambda z:(z["slot"] in ("BE","IR"),z["slot"],z["name"])):
            cards.append(f"<div class='espn-player'><div><b>{html.escape(x['name'])}</b><br><span>{html.escape(x['pos'])}</span></div><em>{html.escape(x['slot'])}</em></div>")
        st.markdown("<div class='espn-roster'>"+"".join(cards)+"</div>",unsafe_allow_html=True)
    elif view=="Draft Grade":
        score,letter,d,note=_grade(roster,players,data,team_id)
        st.markdown(f"<div class='grade-card'><div class='letter'>{letter}</div><div class='score'>{score}/100 SHIVA DRAFT SCORE</div><p>{html.escape(note)}</p><div class='grade-row'><div><b>{d['top50']}</b><span>Top-50 players</span></div><div><b>{d['steals']}</b><span>Draft values</span></div><div><b>{d['reaches']}</b><span>Major reaches</span></div></div></div>",unsafe_allow_html=True)
    else:
        eligible=[x for x in roster if x["pos"] not in ("K","DST")]
        if len(eligible)<2:
            st.info("Your ESPN roster does not have enough skill-position players to compare yet.");return
        names=[x["name"] for x in eligible]
        a=st.selectbox("Player A",names,index=0,key="espn_ss_a")
        b=st.selectbox("Player B",names,index=min(1,len(names)-1),key="espn_ss_b")
        if a==b:st.info("Choose two different players.");return
        ra,pa=_evidence(players,a); rb,pb=_evidence(players,b)
        winner=a if ra<=rb else b; wr=min(ra,rb); loser=b if winner==a else a; lr=max(ra,rb)
        gap=lr-wr if wr<999 and lr<999 else 0
        reason=(f"Shiva currently ranks {winner} {int(gap)} spots ahead of {loser}." if gap>=1 else f"Shiva's current ranking context gives {winner} the stronger lean.")
        st.markdown(f"<div class='start-call'><span>SHIVA START/SIT</span><b>Start {html.escape(winner)}</b><p>{html.escape(reason)} Because this is tied to your imported ESPN roster, only your actual players appear in the comparison.</p></div>",unsafe_allow_html=True)
