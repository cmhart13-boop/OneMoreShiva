import html
import pandas as pd
import streamlit as st

PPR_BIG_BOARD = [
("RB","Jahmyr Gibbs"),("RB","Bijan Robinson"),("WR","Ja'Marr Chase"),("WR","Puka Nacua"),("RB","Christian McCaffrey"),("WR","Amon-Ra St. Brown"),("WR","Jaxon Smith-Njigba"),("RB","Jonathan Taylor"),("RB","James Cook III"),("WR","CeeDee Lamb"),("RB","Omarion Hampton"),("RB","Ashton Jeanty"),("WR","Justin Jefferson"),("RB","Chase Brown"),("RB","Kenneth Walker III"),("RB","Saquon Barkley"),("WR","Drake London"),("RB","De'Von Achane"),("TE","Brock Bowers"),("WR","A.J. Brown"),("WR","George Pickens"),("WR","Rashee Rice"),("WR","Nico Collins"),("RB","Derrick Henry"),("TE","Trey McBride"),("RB","Jeremiyah Love"),("WR","DeVonta Smith"),("WR","Malik Nabers"),("QB","Josh Allen"),("WR","Chris Olave"),("RB","Josh Jacobs"),("WR","Tee Higgins"),("RB","Breece Hall"),("WR","Jaylen Waddle"),("WR","Zay Flowers"),("RB","Kyren Williams"),("WR","Tetairoa McMillan"),("WR","Emeka Egbuka"),("WR","Luther Burden III"),("TE","Colston Loveland"),("RB","Javonte Williams"),("WR","Garrett Wilson"),("WR","Ladd McConkey"),("WR","DJ Moore"),("RB","Cam Skattebo"),("RB","Bucky Irving"),("RB","Travis Etienne Jr."),("TE","Tyler Warren"),("WR","Terry McLaurin"),("QB","Lamar Jackson")]

POSITIONAL = {
"QB":["Josh Allen","Lamar Jackson","Drake Maye","Jayden Daniels","Joe Burrow","Jalen Hurts","Caleb Williams","Justin Herbert","Trevor Lawrence","Jaxson Dart"],
"RB":["Jahmyr Gibbs","Bijan Robinson","Christian McCaffrey","Jonathan Taylor","James Cook III","Omarion Hampton","Ashton Jeanty","Chase Brown","Kenneth Walker III","Saquon Barkley","De'Von Achane","Derrick Henry","Jeremiyah Love","Josh Jacobs","Breece Hall"],
"WR":["Ja'Marr Chase","Puka Nacua","Amon-Ra St. Brown","Jaxon Smith-Njigba","CeeDee Lamb","Justin Jefferson","Drake London","A.J. Brown","George Pickens","Rashee Rice","Nico Collins","DeVonta Smith","Malik Nabers","Chris Olave","Tee Higgins"],
"TE":["Brock Bowers","Trey McBride","Colston Loveland","Tyler Warren","Sam LaPorta","Harold Fannin Jr.","Tucker Kraft","Kyle Pitts Sr.","George Kittle","Dalton Kincaid"]}

ADJ = {
"QB":[("Josh Allen",23.2),("Matthew Stafford",20.6),("Patrick Mahomes",20.4),("Jaxson Dart",20.1),("Trevor Lawrence",19.9),("Drake Maye",19.8),("Dak Prescott",19.6),("Jacoby Brissett",18.9)],
"RB":[("Christian McCaffrey",24.8),("Jahmyr Gibbs",24.6),("Jonathan Taylor",23.8),("Bijan Robinson",22.0),("Chase Brown",21.0),("De'Von Achane",20.4),("Cam Skattebo",19.1),("Josh Jacobs",18.0)],
"WR":[("Puka Nacua",23.7),("Jaxon Smith-Njigba",20.4),("Amon-Ra St. Brown",20.3),("Ja'Marr Chase",20.1),("Drake London",19.7),("Rashee Rice",18.8),("Chris Olave",18.8),("CeeDee Lamb",16.6)],
"TE":[("Trey McBride",18.6),("Brock Bowers",16.4),("Tucker Kraft",16.2),("George Kittle",15.4),("Tyler Warren",13.1),("Dalton Kincaid",12.9),("Colston Loveland",12.9),("Travis Kelce",12.8)]}

NUGGETS = [
("Draft capital matters","Since 2015, the first 11 RBs selected top-25 in the NFL Draft all produced an RB1 fantasy season by Year 2. That puts major sophomore upside behind Ashton Jeanty and Omarion Hampton."),
("Rounds 1–2 are the RB ceiling zone","Shiva's research found only 2 of 33 early-round RBs who reached 20+ PPR PPG came from Rounds 3–4. His preferred build starts RB/RB and aims for three RBs inside roughly the top 25–30."),
("Chase Brown environment","Cincinnati QBs were the NFL's top three in checkdown rate in 2025, and Zac Taylor has produced an RB1 in six straight seasons when Chase Brown's 2024 starts are counted."),
("Josh Allen is the outlier","Allen has finished top-two at QB in fantasy points six straight seasons. Shiva also notes rushing QBs drafted in Rounds 2–5 have historically hit far more often than passing-only QBs."),
("Puka earns targets at a different level","Since 2024, Puka Nacua's targets per route sit at 36.8%; Shiva notes no other qualified player is above 30%."),
("Dalton Kincaid: routes, not efficiency","Kincaid led 2025 TEs across a huge collection of per-route efficiency measures. The unlock is simply getting him on more routes."),
("Parker Washington late value","Over Jacksonville's final four games, Washington produced 454 receiving yards despite Brian Thomas Jr. and Jakobi Meyers each running more routes."),
("Luther Burden efficiency signal","Burden ranked eighth among WRs in fantasy points per snap as a rookie; six of the seven players ahead of him were fantasy WR1s."),
("CeeDee regression candidate — upward","Shiva's 25-factor luck model rated CeeDee Lamb the unluckiest player of 2025, estimating roughly 2.7 PPG lost to bad-luck events."),
("Achane's receiving split matters","De'Von Achane has averaged 11.4 receiving PPG with Tua Tagovailoa in his career versus 3.4 in eight games without him."),
("Jaylen Warren receiving opportunity","Warren ranked top-two among RBs in targets per route, yards per route and missed tackles per reception in 2025; Pittsburgh also has 82 vacated RB targets."),
("Drake Maye game-script ceiling","Maye was QB1 over quarters 1–3 last season but QB32 in fourth quarters. A less dominant Patriots game script could preserve more late-game passing/rushing volume."),
("Jadarian Price caution","Price's college pass-blocking grade was 38.5. Shiva flags pass protection as a potential obstacle to immediate passing-down work."),
("Kenneth Walker goal-line upside","Shiva points to the possibility of stronger goal-line plus receiving usage in Walker's new environment, one of the reasons he ranks him aggressively."),
("Don't blindly follow rankings","Use rankings against ADP. If a player is ranked 62 but normally goes 85, the goal is to capture the value rather than drafting him at 62."),
]

CSS='''<style>
.guide-hero{background:linear-gradient(145deg,#162735,#0a1219);border:1px solid #294054;border-radius:9px;padding:16px;margin:4px 0 10px}.guide-kicker{font-size:9px;color:#d9ff38;font-weight:950;letter-spacing:1px;text-transform:uppercase}.guide-hero h2{font-size:25px;line-height:1.02;margin:5px 0;color:#fff}.guide-hero p{font-size:14px;color:#9cadb9;margin:0}.guide-card{background:#0e1821;border:1px solid #22313f;border-radius:9px;padding:11px;margin-bottom:7px}.guide-card b{font-size:15px;color:#fff}.guide-card p{font-size:13px;line-height:1.35;color:#a8b5bf;margin:4px 0 0}.rank-row{display:grid;grid-template-columns:31px 34px minmax(0,1fr);gap:7px;align-items:center;background:#0e1821;border:1px solid #22313f;border-radius:8px;padding:7px 9px;margin-bottom:4px}.rank-n{font-size:13px;font-weight:950;color:#8fa0ae}.rank-name{font-size:15px;font-weight:900;color:#fff}.pos-chip{border-radius:5px;text-align:center;padding:3px 2px;font-size:8px;font-weight:950;color:white}.pc-QB{background:#7257d8}.pc-RB{background:#19a89d}.pc-WR{background:#347fd9}.pc-TE{background:#e88135}.strategy-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin:7px 0 10px}.strategy-box{background:#111d27;border:1px solid #263745;border-radius:9px;padding:10px}.strategy-box span{font-size:10px;color:#8fa0ae;font-weight:900;text-transform:uppercase}.strategy-box b{display:block;font-size:15px;margin-top:2px}.adj-row{display:flex;justify-content:space-between;gap:8px;background:#0e1821;border-bottom:1px solid #22313f;padding:8px 9px;font-size:11px}.adj-row b{color:#d9ff38}.guide-note{font-size:12px;color:#8fa0ae;margin:6px 2px 10px}.rounds{font-size:13px;line-height:1.65;color:#c8d2d9;background:#0e1821;border:1px solid #22313f;border-radius:9px;padding:11px}
/* Draft Guide section navigation: same edge-to-edge card treatment as Draft Room. */
.st-key-guide_tab{display:block!important;width:100%!important;max-width:none!important;margin:2px 0 13px!important}
.st-key-guide_tab>div,.st-key-guide_tab [data-testid="stRadio"],.st-key-guide_tab [data-baseweb="radio-group"]{width:100%!important;max-width:none!important}
.st-key-guide_tab div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:6px!important;width:100%!important;max-width:none!important;align-items:stretch!important}
.st-key-guide_tab div[role="radiogroup"] label{box-sizing:border-box!important;position:relative!important;width:100%!important;min-width:0!important;max-width:none!important;min-height:50px!important;border-radius:8px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:7px 4px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;margin:0!important;box-shadow:0 4px 14px rgba(0,0,0,.10)!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,rgba(55,128,119,.34),rgba(17,43,43,.72))!important;border-color:rgba(116,227,210,.38)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 6px 18px rgba(40,130,120,.10)!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{display:none!important;content:none!important}
.st-key-guide_tab div[role="radiogroup"] label>div:first-child{display:none!important}.st-key-guide_tab input[type="radio"]{display:none!important}
.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%!important;text-align:center!important}
.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;font-weight:950!important;line-height:1.15!important;color:#aab8c4!important;text-transform:uppercase!important;text-align:center!important;margin:0!important;white-space:normal!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
@media(max-width:430px){.st-key-guide_tab div[role="radiogroup"]{gap:5px!important}.st-key-guide_tab div[role="radiogroup"] label{min-height:48px!important}.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10.5px!important}}

.guide-player-link{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;color:#fff!important;text-decoration:none!important}.guide-player-link span{font-size:9px;color:#d8b35b;font-weight:900;white-space:nowrap}.rank-row:has(.guide-player-link){border-color:rgba(216,179,91,.20)}.rank-row:has(.guide-player-link):active{background:#17212a}.guide-card b{font-size:16px}.guide-card p{font-size:14px}
\n/* GUIDE UX V3 */\n.guide-hero{border-radius:18px!important;padding:21px 17px!important;background:linear-gradient(145deg,#17212a,#0d141a)!important;border:1px solid rgba(213,177,92,.22)!important}.guide-kicker{font-size:11px!important;color:#dfc57f!important}.guide-hero h2{font-size:30px!important;line-height:1.04!important;margin:6px 0 8px!important}.guide-hero p{font-size:15px!important;line-height:1.45!important}.st-key-guide_tab div[role="radiogroup"]{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:8px!important;margin:7px 0 16px!important}.st-key-guide_tab div[role="radiogroup"] label{min-height:60px!important;border-radius:13px!important;padding:9px 7px!important;background:#101820!important;border:1px solid #2b3741!important;box-shadow:none!important}.st-key-guide_tab div[role="radiogroup"] label:has(input:checked){background:#1b252e!important;border-color:#d2ae57!important;box-shadow:inset 0 0 0 1px rgba(210,174,87,.12)!important}.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::before,.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{display:none!important;content:none!important}.st-key-guide_tab div[role="radiogroup"] p{font-size:13px!important;line-height:1.15!important;text-transform:none!important;color:#b5bec4!important}.st-key-guide_tab div[role="radiogroup"] label:has(input:checked) p{color:#f7f7f5!important}.strategy-grid{gap:10px!important}.strategy-box{border-radius:15px!important;padding:15px!important}.strategy-box span{font-size:11px!important}.strategy-box b{font-size:17px!important}.rounds{font-size:14.5px!important;line-height:1.65!important;border-radius:15px!important;padding:16px!important}.rank-row{min-height:62px!important;border-radius:12px!important;padding:10px 11px!important}.rank-name{font-size:16px!important}.guide-player-link span{font-size:11px!important}.adj-row{font-size:14px!important;padding:11px!important}@media(max-width:560px){.st-key-guide_tab div[role="radiogroup"]{grid-template-columns:repeat(2,minmax(0,1fr))!important}.st-key-guide_tab div[role="radiogroup"] label{min-height:58px!important}.st-key-guide_tab div[role="radiogroup"] label:nth-child(5){grid-column:1 / -1!important}.st-key-guide_tab div[role="radiogroup"] p{font-size:13px!important}.guide-hero h2{font-size:28px!important}.strategy-grid{grid-template-columns:1fr 1fr!important}}\n</style>'''

def _rows(items, players=None, profile_href=None):
    out=[]
    for i,(p,n) in enumerate(items,1):
        name_html=html.escape(n)
        if players is not None and profile_href is not None:
            m=players.loc[players["name"].astype(str).str.casefold().eq(str(n).casefold())]
            if not m.empty:
                href=profile_href(m.iloc[0],"Guide")
                name_html=f'<a class="guide-player-link" href="{href}" target="_self">{name_html}<span>View →</span></a>'
        out.append(f'<div class="rank-row"><div class="rank-n">{i}</div><div class="pos-chip pc-{p}">{p}</div><div class="rank-name">{name_html}</div></div>')
    return ''.join(out)

def _current_board(players):
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
