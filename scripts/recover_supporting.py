from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'shiva_product.py'
s=p.read_text(encoding='utf-8')

helper=r'''def _league_power_board(players,load_weekly,weekly_for_player,espn_ppr) -> pd.DataFrame:
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


'''
needle='def render_dashboard():'
if needle not in s:raise SystemExit('render_dashboard not found')
s=s.replace(needle,helper+'def render_dashboard(players,load_weekly,weekly_for_player,espn_ppr):',1)

old='''    if state:st.markdown("<div class='league-live'>● ESPN LEAGUE CONNECTED</div>",unsafe_allow_html=True)
    else:st.markdown("<div class='league-off'>CONNECT ESPN FOR ROSTER-AWARE COACHING</div>",unsafe_allow_html=True)
    st.markdown("<div class='edge-grid'><div class='edge-card'><span>LINEUP EDGE</span><b>Thursday FLEX protection</b><p>Shiva checks the synced lineup for the FLEX mistake that kills Sunday replacement flexibility.</p></div><div class='edge-card'><span>DRAFT EDGE</span><b>Read the managers between picks</b><p>Position scarcity and roster construction matter more than blindly following ADP.</p></div><div class='edge-card'><span>TEAM BUILD</span><b>Raise the floor</b><p>Repeatable 15+ point weeks keep you in every matchup.</p></div><div class='edge-card'><span>TEAM BUILD</span><b>Keep the ceiling</b><p>Use selected roster spots on players with legitimate week-winning outcomes.</p></div></div>",unsafe_allow_html=True)
'''
new='''    if state:
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
'''
if old not in s:raise SystemExit('dashboard body not found')
s=s.replace(old,new,1)

old_call='if tab=="Home":render_dashboard()'
new_call='if tab=="Home":render_dashboard(players,load_weekly,weekly_for_player,espn_ppr)'
if old_call not in s:raise SystemExit('dashboard call not found')
s=s.replace(old_call,new_call,1)
p.write_text(s,encoding='utf-8')
print('SUPPORTING LEAGUE INTELLIGENCE PATCH APPLIED')
