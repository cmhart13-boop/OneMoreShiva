from __future__ import annotations
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
guide=ROOT/'shiva_draft_guide.py'
app=ROOT/'app_core.py'
s=guide.read_text(encoding='utf-8')

if 'import pandas as pd' not in s:
    s=s.replace('import html\nimport streamlit as st\n','import html\nimport pandas as pd\nimport streamlit as st\n',1)

new_render=r'''def _current_board(players):
    if players is None or not isinstance(players,pd.DataFrame) or players.empty:
        return []
    x=players.copy()
    x['_rank']=pd.to_numeric(x.get('overall_rank'),errors='coerce')
    x=x.loc[x['pos'].astype(str).isin(['QB','RB','WR','TE']) & x['_rank'].notna()].sort_values(['_rank','name'])
    return [(str(r.pos),str(r.name)) for r in x.head(100).itertuples()]


def _board_gap_rows(players,limit=10):
    if players is None or not isinstance(players,pd.DataFrame) or players.empty:return []
    x=players.copy()
    x['_rank']=pd.to_numeric(x.get('overall_rank'),errors='coerce')
    x['_adp']=pd.to_numeric(x.get('draft_adp'),errors='coerce')
    x=x.loc[x['_rank'].notna() & x['_adp'].notna() & x['pos'].astype(str).isin(['QB','RB','WR','TE'])].copy()
    x['_gap']=x['_adp']-x['_rank']
    x=x.sort_values(['_gap','_rank'],ascending=[False,True]).head(limit)
    return [(str(r.name),str(r.pos),float(r._gap),float(r._rank),float(r._adp)) for r in x.itertuples()]


def _historical_rows(players,load_weekly,weekly_name_col,espn_ppr):
    if any(v is None for v in (players,load_weekly,weekly_name_col,espn_ppr)):return None,{}
    try:
        w=load_weekly().copy();nc=weekly_name_col(w)
        if not nc or 'season' not in w.columns or 'week' not in w.columns:return None,{}
        w['_ppr']=espn_ppr(w)
        season_values=pd.to_numeric(w['season'],errors='coerce').dropna()
        if season_values.empty:return None,{}
        latest=int(season_values.max())
        w=w.loc[pd.to_numeric(w['season'],errors='coerce').eq(latest) & pd.to_numeric(w['week'],errors='coerce').between(1,18,inclusive='both') & w['_ppr'].notna()].copy()
        cur=players[['name','pos']].drop_duplicates().copy();cur['_key']=cur['name'].astype(str).str.casefold()
        w['_key']=w[nc].astype(str).str.casefold();w=w.merge(cur[['_key','name','pos']],on='_key',how='inner')
        w=w.loc[w['pos'].astype(str).isin(['QB','RB','WR','TE'])]
        g=w.groupby(['name','pos'],as_index=False).agg(games=('_ppr','count'),ppg=('_ppr','mean'),rate15=('_ppr',lambda x:(x>=15).mean()*100),boom25=('_ppr',lambda x:(x>=25).mean()*100),bust10=('_ppr',lambda x:(x<10).mean()*100))
        g=g.loc[g['games']>=8].copy()
        out={}
        for pos in ('QB','RB','WR','TE'):
            z=g.loc[g['pos'].eq(pos)].sort_values(['ppg','rate15'],ascending=False).head(6)
            out[pos]=z.to_dict('records')
        return latest,out
    except Exception:
        return None,{}


def render_draft_guide(players=None, profile_href=None, load_weekly=None, weekly_name_col=None, espn_ppr=None):
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown('<div class="guide-hero"><div class="guide-kicker">Draft Intelligence</div><h2>The Shiva Draft Guide</h2><p>Full-PPR strategy, the current Shiva board, verified historical evidence and draft builds designed for fast decisions.</p></div>',unsafe_allow_html=True)
    tab=st.radio('Guide section',['Game Plan','PPR Board','Research','10 Team','12 Team'],horizontal=True,label_visibility='collapsed',key='guide_tab')
    if tab=='Game Plan':
        st.markdown('<div class="strategy-grid"><div class="strategy-box"><span>Early Rounds</span><b>Buy elite weekly ceilings</b></div><div class="strategy-box"><span>Roster Build</span><b>Protect scarce RB volume</b></div><div class="strategy-box"><span>Middle Rounds</span><b>Exploit rank vs ADP value</b></div><div class="strategy-box"><span>Late Rounds</span><b>Draft paths to upside</b></div></div>',unsafe_allow_html=True)
        st.markdown('<div class="rounds"><b>Core Full-PPR approach</b><br>Use Shiva rankings against ADP rather than drafting directly from either list. Build a strong weekly floor without giving away ceiling, preserve roster flexibility, and use later picks on players whose role can materially grow.</div>',unsafe_allow_html=True)
    elif tab=='PPR Board':
        st.caption('Current Shiva Full-PPR board · sourced from the app current-ranking dataset, not a duplicate hard-coded list.')
        selected=st.multiselect('Filter positions',['QB','RB','WR','TE'],default=['QB','RB','WR','TE'],key='guide_pos_multi',placeholder='All positions')
        board=_current_board(players)
        if selected: board=[(p,n) for p,n in board if p in selected]
        if board: st.markdown(_rows(board,players,profile_href),unsafe_allow_html=True)
        else: st.info('Current ranking data is unavailable. No substitute ranking was generated.')
    elif tab=='Research':
        st.markdown('#### Current board vs ADP')
        st.caption('Positive gap means Shiva currently ranks the player earlier than the ADP field. This section is calculated from the current ranking dataset at render time.')
        gaps=_board_gap_rows(players)
        if not gaps: st.info('Current rank/ADP comparison data is unavailable.')
        else:
            for name,pos,gap,rank,adp in gaps:
                st.markdown(f'<div class="adj-row"><span>{html.escape(name)} · {html.escape(pos)} · Rank {rank:.0f} / ADP {adp:.1f}</span><b>+{gap:.1f}</b></div>',unsafe_allow_html=True)
        season,by_pos=_historical_rows(players,load_weekly,weekly_name_col,espn_ppr)
        st.markdown('#### Verified historical Full-PPR evidence')
        if not season or not by_pos:
            st.info('Verified historical weekly evidence is unavailable. Shiva will not fill the gap with remembered statistics.')
        else:
            st.caption(f'Latest completed season in the verified weekly database: {season}. Minimum 8 games.')
            for pos in ('QB','RB','WR','TE'):
                rows=by_pos.get(pos) or []
                if not rows:continue
                st.markdown(f'**{pos}**')
                for r in rows:
                    st.markdown(f'<div class="adj-row"><span>{html.escape(str(r["name"]))} · {int(r["games"])} G · {float(r["rate15"]):.0f}% at 15+</span><b>{float(r["ppg"]):.1f} PPG</b></div>',unsafe_allow_html=True)
    elif tab=='10 Team':
        st.markdown('<div class="rounds"><b>10-Team ESPN Full PPR · Primary Build</b><br>R1–2 elite ceiling and volume · R3 best remaining difference-maker · R4–6 attack value and positional leverage · R7–10 upside starters and contingency RBs · R11–13 bench ceiling · R14 D/ST · R15 K/IR. Adjust to the room rather than forcing positions at fixed picks.</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="rounds"><b>12-Team ESPN Full PPR · Primary Build</b><br>Scarcity arrives faster. Prioritize bankable volume early, avoid reaching merely to fill a starting slot, and use the middle rounds to capture falling tiers before they disappear. Preserve late-round picks for contingent volume and breakout paths rather than low-ceiling depth.</div>',unsafe_allow_html=True)
'''

s,n=re.subn(r'def render_draft_guide\(players=None, profile_href=None\):.*\Z',new_render,s,count=1,flags=re.S)
if n!=1:raise SystemExit(f'render_draft_guide replacements={n}')
guide.write_text(s,encoding='utf-8')

ac=app.read_text(encoding='utf-8')
old='render_draft_guide(players,profile_href)'
new='render_draft_guide(players,profile_href,load_weekly,weekly_name_col,espn_ppr)'
if old not in ac:raise SystemExit('Guide callsite not found')
ac=ac.replace(old,new,1)
app.write_text(ac,encoding='utf-8')
print('GUIDE RECOVERY PATCH APPLIED')
