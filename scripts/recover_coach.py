from __future__ import annotations
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
live=ROOT/'shiva_live.py'
prod=ROOT/'shiva_product.py'

s=live.read_text(encoding='utf-8')
ctx=r'''def team_game_context(team_abbr: str) -> dict | None:
    try:
        data=current_scoreboard()
        needle=str(team_abbr or "").upper().strip()
        if not needle:return None
        for ev in data.get("events",[]):
            comp=(ev.get("competitions") or [{}])[0]
            competitors=comp.get("competitors",[]) or []
            found=None
            for c in competitors:
                t=c.get("team",{}) or {}
                labels={str(t.get("abbreviation") or "").upper(),str(t.get("shortDisplayName") or "").upper(),str(t.get("displayName") or "").upper()}
                if needle in labels:
                    found=c;break
            if found is None:continue
            other=next((c for c in competitors if c is not found),{})
            ot=(other.get("team",{}) or {})
            dt=datetime.fromisoformat(str(ev.get("date")).replace("Z","+00:00"))
            return {
                "day":dt.strftime("%A"),"datetime":dt,
                "opponent":str(ot.get("abbreviation") or ot.get("shortDisplayName") or ot.get("displayName") or ""),
                "home_away":str(found.get("homeAway") or ""),
                "event":str(ev.get("name") or ev.get("shortName") or ""),
            }
    except Exception:
        pass
    return None


def team_game_day(team_abbr: str) -> tuple[str|None, datetime|None]:
    ctx=team_game_context(team_abbr)
    return (ctx.get("day"),ctx.get("datetime")) if ctx else (None,None)
'''
s,n=re.subn(r'def team_game_day\(team_abbr: str\).*?\n\ndef espn_news',ctx+'\n\ndef espn_news',s,count=1,flags=re.S)
if n!=1:raise SystemExit(f'team_game_day replacements={n}')
live.write_text(s,encoding='utf-8')

p=prod.read_text(encoding='utf-8')
p=p.replace('player_news, team_game_day','player_news, team_game_context, team_game_day',1)

helper=r'''def _live_context_block(e: dict) -> str:
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


'''
needle='def render_start_sit(players,load_weekly,weekly_for_player,espn_ppr):'
if helper.strip() not in p:
    p=p.replace(needle,helper+needle,1)

old='''    for e in (ea,eb):
        st.markdown(f"<div class='metric-grid'><div class='metric'><b>{html.escape(e['name'])}</b><span>Player</span></div><div class='metric'><b>{_num(e.get('floor'))}</b><span>Floor</span></div><div class='metric'><b>{_num(e.get('ceiling'))}</b><span>Ceiling</span></div><div class='metric'><b>{_num(e.get('rate15'),0,'%')}</b><span>15+ Weeks</span></div></div>",unsafe_allow_html=True)
    with st.expander("Why this call?"):
'''
new='''    for e in (ea,eb):
        st.markdown(f"<div class='metric-grid'><div class='metric'><b>{html.escape(e['name'])}</b><span>Player</span></div><div class='metric'><b>{_num(e.get('floor'))}</b><span>Floor</span></div><div class='metric'><b>{_num(e.get('ceiling'))}</b><span>Ceiling</span></div><div class='metric'><b>{_num(e.get('rate15'),0,'%')}</b><span>15+ Weeks</span></div></div>",unsafe_allow_html=True)
    st.markdown("<div class='table-note'>Live schedule and news are shown separately from the recommendation so current context is visible without pretending it is a verified weekly projection.</div>",unsafe_allow_html=True)
    st.markdown("<div class='edge-grid'>"+_live_context_block(ea)+_live_context_block(eb)+"</div>",unsafe_allow_html=True)
    with st.expander("Why this call?"):
'''
if old not in p:raise SystemExit('Start/Sit evidence block not found')
p=p.replace(old,new,1)

trade_old='''    all_names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    mine=[n for n in _roster_names() if n in set(all_names)] or all_names
    give=st.multiselect("You give",mine,max_selections=3,key="trade_give")
    receive=st.multiselect("You receive",all_names,max_selections=3,key="trade_get")
'''
trade_new='''    all_names=players["name"].dropna().astype(str).drop_duplicates().tolist()
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
'''
if trade_old not in p:raise SystemExit('Trade selector block not found')
p=p.replace(trade_old,trade_new,1)

watch_old='''            mask=(df.get("headline",pd.Series(dtype=str)).astype(str)+" "+df.get("description",pd.Series(dtype=str)).astype(str)).str.contains(str(who).split()[-1],case=False,regex=False)
            show=df.loc[mask].sort_values("captured_at",ascending=False).head(12)
'''
watch_new='''            text=(df.get("headline",pd.Series(dtype=str)).astype(str)+" "+df.get("description",pd.Series(dtype=str)).astype(str))
            mask=text.str.contains(str(who),case=False,regex=False)
            if not mask.any():
                last=str(who).split()[-1]
                same_last=players["name"].dropna().astype(str).map(lambda x:str(x).split()[-1].casefold()==last.casefold()).sum()
                if same_last==1:mask=text.str.contains(last,case=False,regex=False)
            show=df.loc[mask].sort_values("captured_at",ascending=False).head(12)
'''
if watch_old not in p:raise SystemExit('Watch history block not found')
p=p.replace(watch_old,watch_new,1)

prod.write_text(p,encoding='utf-8')
print('COACH RECOVERY PATCH APPLIED')
