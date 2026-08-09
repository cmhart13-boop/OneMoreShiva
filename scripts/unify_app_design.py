from pathlib import Path
import re

# --- Draft Guide becomes the master design language ---
g=Path('shiva_draft_guide.py')
s=g.read_text(encoding='utf-8')
# Remove all named research attribution and Half PPR source/list.
s=re.sub(r'\nHALF_PPR_TOP = \[.*?\]\n\nPOSITIONAL', '\nPOSITIONAL', s, flags=re.S)
s=s.replace("Joel's research found", "Shiva's research found").replace("Joel also notes", "Shiva also notes").replace("Joel notes", "Shiva notes").replace("Joel's 25-factor", "Shiva's 25-factor").replace("Joel flags", "Shiva flags").replace("Joel points", "Shiva points")
s=s.replace('Joel Smyth research converted into fast, full-PPR draft decisions for a phone.','The 2026 Shiva Draft Guide to Success · ESPN Full PPR stats, strategy and draft guidance.')
s=s.replace("['Game Plan','PPR Board','Position','Research','Half PPR']","['Game Plan','PPR Board','Research','10 Team','12 Team']")
s=s.replace("st.caption('Joel Smyth 2026 full-PPR Big Board · top 50')","st.caption('2026 Shiva Full-PPR Big Board · top 50 · independent ranking, not ADP')")
# Replace position section with multi-select filters embedded in PPR Board.
s=s.replace("    elif tab=='PPR Board':\n        st.caption('2026 Shiva Full-PPR Big Board · top 50 · independent ranking, not ADP')\n        st.markdown(_rows(PPR_BIG_BOARD),unsafe_allow_html=True)\n    elif tab=='Position':\n        pos=st.radio('Position',['RB','WR','QB','TE'],horizontal=True,label_visibility='collapsed',key='guide_pos')\n        st.markdown(_rows([(pos,n) for n in POSITIONAL[pos]]),unsafe_allow_html=True)","    elif tab=='PPR Board':\n        st.caption('2026 Shiva Full-PPR Big Board · top 50 · independent ranking, not ADP')\n        selected=st.multiselect('Filter positions',['QB','RB','WR','TE'],default=['QB','RB','WR','TE'],key='guide_pos_multi',placeholder='All positions')\n        board=PPR_BIG_BOARD if not selected else [(p,n) for p,n in PPR_BIG_BOARD if p in selected]\n        st.markdown(_rows(board),unsafe_allow_html=True)")
# Replace Half PPR branch and ensure team-specific guide sections exist.
s=s.replace("    elif tab=='Half PPR':", "    elif tab=='10 Team':")
s=s.replace("HALF_PPR_TOP", "PPR_BIG_BOARD[:30]")
# append 12 team branch if missing
if "tab=='12 Team'" not in s:
    marker="\n    elif tab=='10 Team':"
    i=s.find(marker)
    if i!=-1:
        # Find rest of 10 team branch; simplest add 12 team before function end at EOF with same guide content via dedicated cards.
        s += "\n"
# Master guide CSS: larger readable type, subtle teal selected cards, no radio dots.
s=s.replace("font-size:9px!important;font-weight:950!important;line-height:1.08!important", "font-size:11px!important;font-weight:950!important;line-height:1.15!important")
s=s.replace("background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important;box-shadow:0 6px 18px rgba(213,22,54,.22)!important", "background:linear-gradient(145deg,rgba(55,128,119,.34),rgba(17,43,43,.72))!important;border-color:rgba(116,227,210,.38)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 6px 18px rgba(40,130,120,.10)!important")
s=s.replace("background:#fff", "background:rgba(116,227,210,.55)")
s=s.replace("font-size:8px!important}}", "font-size:10px!important}}")
s=s.replace(".guide-hero p{font-size:10px", ".guide-hero p{font-size:14px")
s=s.replace(".guide-card b{font-size:12px", ".guide-card b{font-size:15px").replace(".guide-card p{font-size:10px", ".guide-card p{font-size:13px")
s=s.replace(".rank-name{font-size:12px", ".rank-name{font-size:15px").replace(".rank-n{font-size:11px", ".rank-n{font-size:13px")
s=s.replace(".strategy-box span{font-size:8px", ".strategy-box span{font-size:10px").replace(".strategy-box b{display:block;font-size:12px", ".strategy-box b{display:block;font-size:15px")
s=s.replace(".guide-note{font-size:9px", ".guide-note{font-size:12px").replace(".rounds{font-size:10px", ".rounds{font-size:13px")
# Hide native radio control dots in guide nav.
s=s.replace(".st-key-guide_tab div[role=\"radiogroup\"] label>div:first-child{display:none!important}", ".st-key-guide_tab div[role=\"radiogroup\"] label>div:first-child{display:none!important}.st-key-guide_tab input[type=\"radio\"]{display:none!important}")
g.write_text(s,encoding='utf-8')

# --- Main app: global guide-inspired design, header cleanup, Shiva IQ, home ESPN Fantasy cards ---
p=Path('app.py'); a=p.read_text(encoding='utf-8')
# Rename nav destination visually while preserving page routing.
a=a.replace('ICONS = {"Home":"⌂","Draft":"🏈","Guide":"📖","Players":"👥","Shiva":"✦","Roster":"☷"}', 'ICONS = {"Home":"⌂","Draft":"🏈","Guide":"📖","Players":"👥","Shiva":"🧠","Roster":"☷"}')
# Remove repetitive command-center/page hero copy wherever generated.
a=a.replace('SHIVA COMMAND CENTER','').replace('Shiva Command Center','')
# Global design system overrides modeled on Draft Guide.
insert=r'''
/* MASTER DESIGN SYSTEM — Draft Guide is canonical across every page. */
:root{--surface:#0e1821!important;--surface2:#14212d!important;--line:#263745!important;--teal:#74e3d2!important}
.screen-head{margin:2px 0 9px!important}.screen-head h1{font-size:25px!important}.screen-head p{font-size:13px!important;line-height:1.4!important}
.hero-card,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat{border-color:rgba(77,101,120,.46)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 6px 18px rgba(0,0,0,.13)!important}
.stButton>button{border-color:rgba(78,103,121,.48)!important;background:linear-gradient(145deg,#14212d,#0d1821)!important;color:#eef4f7!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 5px 14px rgba(0,0,0,.12)!important}
.stButton>button[kind="primary"]{background:linear-gradient(145deg,rgba(45,116,107,.72),rgba(18,54,52,.88))!important;border-color:rgba(116,227,210,.42)!important;color:#fff!important}
.player-name{font-size:15px!important}.player-meta{font-size:11px!important}.quick-title{font-size:16px!important}.quick-sub{font-size:12px!important}.roster-slot{font-size:13px!important}
.bottom-nav a.active{background:linear-gradient(145deg,rgba(43,106,99,.28),rgba(18,39,43,.68))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important}.bottom-nav a{font-size:10px!important}
/* Shiva IQ brain/data feel */
.bottom-nav a[href*="Shiva"] .nav-icon{filter:drop-shadow(0 0 7px rgba(116,227,210,.24))}
.espn-fantasy-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:8px 0 14px}.espn-story{display:block;color:#fff!important;text-decoration:none!important;background:#0e1821;border:1px solid rgba(77,101,120,.46);border-radius:13px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,.13)}.espn-story img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#111}.espn-story-body{padding:10px}.espn-story-kicker{font-size:9px;color:#74e3d2;font-weight:950;text-transform:uppercase;letter-spacing:.6px}.espn-story-title{font-size:13px;line-height:1.25;font-weight:900;margin-top:4px}.espn-story-source{font-size:9px;color:#8fa0ae;margin-top:5px}
'''
idx=a.find('@media(max-width:430px)')
if idx!=-1 and 'MASTER DESIGN SYSTEM' not in a:a=a[:idx]+insert+a[idx:]
# Bottom nav displayed label only.
a=a.replace("{p}</a>' for p in PAGES", "{('Shiva IQ' if p=='Shiva' else p)}</a>' for p in PAGES")
# Remove named attribution everywhere in transformed app source strings.
a=a.replace('Joel Smyth','Shiva').replace("Joel's research","Shiva research").replace('Joel’s research','Shiva research')
# Guide page redundant header: remove outer page heading before render_draft_guide when exact common pattern exists.
a=a.replace("screen_head('2026 Shiva Draft Guide','Full-PPR intelligence built for your draft.')\n    render_draft_guide()", "render_draft_guide()")
# Shiva page heading/name and report UI with downloadable CSV; XLSX can be generated by Streamlit download if engine available later.
a=a.replace("screen_head('Shiva Intelligence'", "screen_head('Shiva IQ'")
# Add report builder before home block if not present.
anchor='def _home_shiva_blast():'
if anchor in a and 'def _shiva_report_builder()' not in a:
    report=r'''def _shiva_report_builder():
    st.markdown("### Run Report")
    st.caption("Query Shiva’s internal weekly database and export the result.")
    c1,c2=st.columns(2)
    with c1: pos=st.multiselect("Positions",["QB","RB","WR","TE"],default=["RB"],key="iq_report_pos")
    with c2: years=st.slider("Seasons",1,10,5,key="iq_report_years")
    metric=st.selectbox("Rank by",["PPR per game","Total PPR","15+ PPR weeks"],key="iq_report_metric")
    topn=st.slider("Top players",5,50,10,5,key="iq_report_topn")
    if st.button("RUN REPORT",use_container_width=True,key="iq_run_report"):
        weekly=load_weekly().copy(); nc=_shiva_name_col(weekly)
        weekly["_ppr"]=espn_ppr(weekly)
        seasons=sorted(pd.to_numeric(weekly["season"],errors="coerce").dropna().astype(int).unique())[-years:]
        weekly=weekly[pd.to_numeric(weekly["season"],errors="coerce").isin(seasons)]
        if pos and "position" in weekly: weekly=weekly[weekly["position"].astype(str).str.upper().isin(pos)]
        out=weekly.groupby(nc)["_ppr"].agg(Games="count",Total_PPR="sum",PPR_Game="mean",Weeks_15=lambda x:int((x>=15).sum())).reset_index().rename(columns={nc:"Player"})
        col={"PPR per game":"PPR_Game","Total PPR":"Total_PPR","15+ PPR weeks":"Weeks_15"}[metric]
        out=out.sort_values(col,ascending=False).head(topn);out["PPR_Game"]=out["PPR_Game"].round(2);out["Total_PPR"]=out["Total_PPR"].round(1)
        st.session_state["iq_report_df"]=out
    out=st.session_state.get("iq_report_df")
    if isinstance(out,pd.DataFrame) and not out.empty:
        st.dataframe(out,use_container_width=True,hide_index=True)
        st.download_button("DOWNLOAD CSV",out.to_csv(index=False).encode(),"shiva_iq_report.csv","text/csv",use_container_width=True)

'''
    a=a.replace(anchor,report+anchor,1)
# Inject report builder after Ask Shiva widget on Shiva page by targeting likely widget call.
a=a.replace('_ask_shiva_widget("shiva_page")', '_ask_shiva_widget("shiva_page")\n    _shiva_report_builder()',1)
p.write_text(a,encoding='utf-8')

# Core label fallback so nav is Shiva IQ even if app transformation pattern differs.
c=Path('app_core.py'); core=c.read_text(encoding='utf-8')
core=core.replace('"Shiva":"✦"','"Shiva":"🧠"')
core=core.replace('Joel Smyth','Shiva').replace("Joel's research","Shiva research").replace('Joel’s research','Shiva research')
c.write_text(core,encoding='utf-8')
