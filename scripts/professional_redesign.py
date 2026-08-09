from pathlib import Path
import re

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Add a final, restrained ESPN-style design pass. This intentionally overrides older rounded/bubbly experiments.
anchor='@media(max-width:430px){.stat-strip'
css=r'''
/* PROFESSIONAL FINAL DESIGN PASS — flat, restrained, Draft-Guide-led. */
:root{--pro-bg:#071018;--pro-card:#0e1821;--pro-card2:#101c26;--pro-line:rgba(95,116,132,.34);--pro-text:#f4f7f9;--pro-muted:#9aa9b5;--pro-teal:#74e3d2}
.block-container{max-width:980px!important}
.app-top{padding:4px 1px 8px!important}.brand-badge{width:34px!important;height:34px!important;border-radius:8px!important;background:linear-gradient(145deg,#152634,#0c1821)!important;border:1px solid rgba(116,227,210,.20)!important;font-size:18px!important}.brand-title{font-size:18px!important;letter-spacing:-.35px!important}.brand-sub{font-size:9px!important}.data-status{border-radius:7px!important;padding:5px 7px!important;border-color:rgba(84,144,111,.30)!important;background:#0b1b14!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.03)!important}
.screen-head{margin:1px 0 9px!important}.screen-head h1{font-size:24px!important;letter-spacing:-.6px!important}.screen-head p{font-size:13px!important;line-height:1.35!important}
.hero-card,.home-shiva-hero,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell{border-radius:9px!important;border:1px solid var(--pro-line)!important;background:linear-gradient(145deg,rgba(16,29,40,.98),rgba(10,19,27,.98))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 5px 14px rgba(0,0,0,.14)!important}
.stButton>button,.stDownloadButton>button{border-radius:8px!important;min-height:44px!important;border:1px solid rgba(93,116,133,.38)!important;background:linear-gradient(145deg,#14212c,#0d1821)!important;color:#eef3f6!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important;font-weight:850!important;font-size:13px!important}
.stButton>button[kind="primary"],.st-key-home_shiva_go .stButton>button,.st-key-shiva_page_go .stButton>button{border-radius:8px!important;background:linear-gradient(145deg,rgba(39,102,96,.72),rgba(16,48,47,.92))!important;border-color:rgba(116,227,210,.32)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 4px 12px rgba(0,0,0,.12)!important;text-shadow:none!important}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{border-radius:8px!important;border-color:rgba(91,112,128,.38)!important;background:#0c161e!important}
/* Keep only true status/filter chips pill-like; everything else stays squared and editorial. */
.pos,.board-pos{border-radius:4px!important}.quick-card{padding:14px!important}.quick-icon{font-size:23px!important}.quick-title{font-size:16px!important}.quick-sub{font-size:12px!important;line-height:1.35!important}.player-shell{padding:9px!important}.player-rank{border-radius:7px!important}.draft-inline{border-radius:7px!important}.profile-metric{border-radius:7px!important}.flip-face{border-radius:9px!important}
/* Draft and Guide navigation: compact editorial tabs, no circles, no cartoon cards. */
.st-key-draft_view div[role="radiogroup"],.st-key-guide_tab div[role="radiogroup"]{gap:5px!important}
.st-key-draft_view div[role="radiogroup"] label,.st-key-guide_tab div[role="radiogroup"] label{min-height:52px!important;border-radius:8px!important;padding:8px 5px!important;background:#0e1821!important;border:1px solid rgba(90,111,127,.36)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important}
.st-key-draft_view div[role="radiogroup"] label>div:first-child,.st-key-guide_tab div[role="radiogroup"] label>div:first-child,.st-key-draft_view input[type="radio"],.st-key-guide_tab input[type="radio"]{display:none!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked),.st-key-guide_tab div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,rgba(42,91,86,.34),rgba(14,34,35,.88))!important;border-color:rgba(116,227,210,.28)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after,.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{display:none!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p,.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;line-height:1.12!important;letter-spacing:.15px!important;text-transform:none!important}
/* Bottom navigation: clean and quiet. */
.bottom-nav{height:72px!important;background:rgba(7,14,20,.98)!important;border-top:1px solid rgba(92,111,126,.28)!important;box-shadow:0 -5px 18px rgba(0,0,0,.24)!important}.bottom-nav a{border-radius:7px!important;min-height:54px!important;font-size:9.5px!important}.bottom-nav a.active{background:rgba(35,66,67,.34)!important;color:#fff!important}.nav-icon{font-size:19px!important}
/* Custom Shiva IQ visual: side-profile silhouette with calculations streaming out. */
.shiva-iq-navicon{position:relative;width:26px;height:22px;display:block}.shiva-iq-navicon .iq-head-mini{position:absolute;left:1px;top:2px;width:15px;height:17px;border:1.5px solid rgba(210,226,235,.85);border-right-color:rgba(116,227,210,.55);border-radius:48% 44% 42% 50%;clip-path:polygon(0 0,100% 0,100% 70%,72% 70%,72% 100%,28% 100%,28% 82%,0 73%)}.shiva-iq-navicon .iq-calc-mini{position:absolute;right:-1px;top:1px;font:700 5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;color:rgba(116,227,210,.78);letter-spacing:.1px;text-align:left}
.shiva-iq-panel{position:relative;overflow:hidden;padding:17px 16px 16px;margin:4px 0 12px;min-height:150px}.shiva-iq-panel h2{font-size:24px;line-height:1.05;margin:0 0 6px;color:#fff;letter-spacing:-.6px}.shiva-iq-panel p{font-size:13px;line-height:1.45;color:#aebbc5;max-width:64%;margin:0}.shiva-iq-panel .iq-kicker{font-size:10px;color:#91dbc8;font-weight:900;letter-spacing:.8px;text-transform:uppercase;margin-bottom:5px}.iq-visual{position:absolute;right:8px;top:7px;width:132px;height:132px;opacity:.78}.iq-head{position:absolute;left:6px;top:13px;width:72px;height:92px;border:2px solid rgba(208,223,232,.48);border-right-color:rgba(116,227,210,.46);border-radius:48% 43% 40% 52%;clip-path:polygon(0 0,100% 0,100% 63%,79% 66%,77% 79%,63% 82%,62% 100%,28% 100%,28% 81%,10% 74%,0 60%);box-shadow:inset -8px 0 22px rgba(71,171,158,.05)}.iq-head:after{content:"";position:absolute;left:21px;top:27px;width:31px;height:27px;border:1px solid rgba(116,227,210,.18);border-radius:50%;box-shadow:8px 7px 0 -7px rgba(116,227,210,.34),-8px -5px 0 -7px rgba(116,227,210,.26)}.iq-formulas{position:absolute;right:0;top:4px;width:64px;font:700 7px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace;color:rgba(116,227,210,.48);white-space:pre-line;text-shadow:0 0 7px rgba(116,227,210,.08)}.iq-formulas:before{content:"";position:absolute;left:-13px;top:9px;width:13px;height:1px;background:linear-gradient(90deg,rgba(116,227,210,.28),transparent);box-shadow:0 18px 0 rgba(116,227,210,.18),0 36px 0 rgba(116,227,210,.14),0 54px 0 rgba(116,227,210,.11)}
.iq-report-shell{padding:14px;margin:8px 0 12px}.iq-report-title{font-size:17px;font-weight:900;color:#fff;margin-bottom:2px}.iq-report-copy{font-size:12px;line-height:1.4;color:#9eacb7;margin-bottom:10px}.iq-presets{font-size:10px;color:#91a2ae;margin:4px 0 8px}.iq-result-note{font-size:12px;color:#aebbc5;margin:8px 0}
@media(max-width:430px){.shiva-iq-panel p{max-width:61%}.iq-visual{right:1px;transform:scale(.92);transform-origin:top right}.st-key-guide_tab div[role="radiogroup"] label,.st-key-draft_view div[role="radiogroup"] label{min-height:50px!important;padding:7px 3px!important}}
'''
if 'PROFESSIONAL FINAL DESIGN PASS' not in s:
    if anchor in s:s=s.replace(anchor,css+'\n'+anchor,1)
    else:s=s.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)","\n"+css+"\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)",1)

# Replace bottom nav at runtime so Shiva gets a genuine custom computing-head silhouette, not an emoji.
nav_patch=r'''
old_bottom_nav='def bottom_nav(active:str):\n    links=\'\'.join(f\'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self"><span class="nav-icon">{ICONS[p]}</span><span>{p}</span></a>\' for p in PAGES);st.markdown(f\'<nav class="bottom-nav">{links}</nav>\',unsafe_allow_html=True)'
new_bottom_nav='''def bottom_nav(active:str):\n    parts=[]\n    for p in PAGES:\n        label="Shiva IQ" if p=="Shiva" else p\n        if p=="Shiva":\n            icon=\'<span class="nav-icon shiva-iq-navicon"><span class="iq-head-mini"></span><span class="iq-calc-mini">Σ\\n01\\nx²</span></span>\'\n        else:\n            icon=f\'<span class="nav-icon">{ICONS[p]}</span>\'\n        parts.append(f\'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self">{icon}<span>{label}</span></a>\')\n    st.markdown(f\'<nav class="bottom-nav">{"".join(parts)}</nav>\',unsafe_allow_html=True)\n'''
if old_bottom_nav in source:source=source.replace(old_bottom_nav,new_bottom_nav,1)
'''
# Insert nav patch immediately before the Ask Shiva engine replacement section.
marker='# Replace the simple Ask Shiva implementation'
if 'old_bottom_nav=' not in s:
    pos=s.find(marker)
    if pos!=-1:s=s[:pos]+nav_patch+'\n'+s[pos:]
    else:
        # safe insertion after mobile_css application
        pos=s.find("# Draft view selector")
        s=s[:pos]+nav_patch+'\n'+s[pos:]

# Upgrade report builder: natural-language query, presets, advanced controls, CSV + XLSX.
start=s.find("def _shiva_report_builder():")
end=s.find("\ndef _home_shiva_blast():",start)
if start!=-1 and end!=-1:
    report=r'''def _run_iq_report_from_controls(positions,season_count,metric,topn,min_games=3):
    weekly=load_weekly().copy();nc=_shiva_name_col(weekly)
    if weekly.empty or not nc:return pd.DataFrame(),[]
    weekly["_ppr"]=espn_ppr(weekly)
    seasons=sorted(pd.to_numeric(weekly["season"],errors="coerce").dropna().astype(int).unique())[-int(season_count):]
    weekly=weekly[pd.to_numeric(weekly["season"],errors="coerce").isin(seasons)].copy()
    if positions and "position" in weekly.columns:
        norm=weekly["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB","D/ST":"DST","DEF":"DST"})
        weekly=weekly[norm.isin(positions)].copy()
    out=weekly.groupby(nc)["_ppr"].agg(Games="count",Total_PPR="sum",PPR_Game="mean",Weeks_15=lambda x:int((x>=15).sum()),Best_Game="max").reset_index().rename(columns={nc:"Player"})
    out=out[out["Games"]>=int(min_games)].copy()
    col={"PPR per game":"PPR_Game","Total PPR":"Total_PPR","15+ PPR weeks":"Weeks_15","Best single game":"Best_Game"}[metric]
    out=out.sort_values([col,"Games"],ascending=[False,False]).head(int(topn)).reset_index(drop=True)
    out.index=out.index+1;out.index.name="Rank"
    out["PPR_Game"]=out["PPR_Game"].round(2);out["Total_PPR"]=out["Total_PPR"].round(1);out["Best_Game"]=out["Best_Game"].round(1)
    return out.reset_index(),seasons

def _parse_iq_report_prompt(prompt):
    q=str(prompt or "").casefold()
    top=10;m=re.search(r"top\s+(\d{1,2})",q)
    if m:top=max(1,min(50,int(m.group(1))))
    years=5;m=re.search(r"(?:last|past)\s+(\d{1,2})\s+(?:years|seasons)",q)
    if m:years=max(1,min(12,int(m.group(1))))
    positions=[]
    aliases={"QB":["quarterback","quarterbacks"," qb ","qbs"],"RB":["running back","running backs"," rb ","rbs"],"WR":["wide receiver","wide receivers"," wr ","wrs"],"TE":["tight end","tight ends"," te ","tes"]}
    padded=f" {q} "
    for p,words in aliases.items():
        if any(w in padded for w in words):positions.append(p)
    metric="PPR per game"
    if "total" in q:metric="Total PPR"
    if "15+" in q or "15 plus" in q or "consistency" in q:metric="15+ PPR weeks"
    if "best game" in q or "ceiling" in q:metric="Best single game"
    return positions or ["RB","WR","QB","TE"],years,metric,top

def _shiva_report_builder():
    st.markdown('<div class="iq-report-shell"><div class="iq-report-title">Shiva IQ Reports</div><div class="iq-report-copy">Ask the internal database for a ranked report, then export the exact result. Example: “Show me the top 5 running backs over the last 10 seasons by PPR per game.”</div></div>',unsafe_allow_html=True)
    prompt=st.text_input("Report request",placeholder="Top 5 RBs over the last 10 seasons by PPR per game",key="iq_report_prompt",label_visibility="collapsed")
    st.markdown('<div class="iq-presets">Try: top 10 WRs last 5 seasons · most 15+ point weeks among RBs · top QBs last 3 seasons by total PPR</div>',unsafe_allow_html=True)
    if st.button("RUN SHIVA IQ REPORT",type="primary",use_container_width=True,key="iq_prompt_run") and prompt.strip():
        positions,years,metric,topn=_parse_iq_report_prompt(prompt)
        out,seasons=_run_iq_report_from_controls(positions,years,metric,topn)
        st.session_state["iq_report_df"]=out;st.session_state["iq_report_scope"]=(positions,seasons,metric)
    with st.expander("Advanced report controls",expanded=False):
        positions=st.multiselect("Positions",["QB","RB","WR","TE"],default=["RB"],key="iq_report_pos")
        season_count=st.slider("Seasons",1,12,5,key="iq_report_years")
        metric=st.selectbox("Rank by",["PPR per game","Total PPR","15+ PPR weeks","Best single game"],key="iq_report_metric")
        topn=st.slider("Players",5,50,10,5,key="iq_report_topn")
        min_games=st.slider("Minimum games in sample",1,40,3,key="iq_report_min_games")
        if st.button("RUN ADVANCED REPORT",use_container_width=True,key="iq_run_report"):
            out,seasons=_run_iq_report_from_controls(positions,season_count,metric,topn,min_games)
            st.session_state["iq_report_df"]=out;st.session_state["iq_report_scope"]=(positions,seasons,metric)
    out=st.session_state.get("iq_report_df")
    if isinstance(out,pd.DataFrame) and not out.empty:
        positions,seasons,metric=st.session_state.get("iq_report_scope",([],[],"PPR per game"))
        scope=f"{', '.join(positions) if positions else 'All positions'} · {min(seasons)}–{max(seasons)} · ranked by {metric}" if seasons else metric
        st.markdown(f'<div class="iq-result-note">{html.escape(scope)} · {len(out)} players</div>',unsafe_allow_html=True)
        st.dataframe(out,use_container_width=True,hide_index=True)
        c1,c2=st.columns(2)
        with c1:st.download_button("DOWNLOAD CSV",out.to_csv(index=False).encode(),"shiva_iq_report.csv","text/csv",use_container_width=True)
        try:
            import io
            buf=io.BytesIO()
            with pd.ExcelWriter(buf,engine="openpyxl") as writer:out.to_excel(writer,index=False,sheet_name="Shiva IQ Report")
            with c2:st.download_button("DOWNLOAD EXCEL",buf.getvalue(),"shiva_iq_report.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        except Exception:
            with c2:st.caption("Excel export unavailable on this deployment.")

'''
    s=s[:start]+report+s[end:]

# Replace the dedicated Shiva page with a proper Shiva IQ workspace and the requested calculating-head visual.
shiva_start=s.find("new_shiva = r'''def shiva():")
if shiva_start!=-1:
    body_start=s.find("def shiva():",shiva_start)
    body_end=s.find("\n'''\nsource = source[:shiva_start]",body_start)
    if body_end!=-1:
        new_body=r'''def shiva():
    st.markdown('<div class="shiva-iq-panel"><div class="iq-kicker">Internal data engine</div><h2>Shiva IQ</h2><p>Ask Shiva a draft question or run a structured report across the historical Full-PPR database.</p><div class="iq-visual"><div class="iq-head"></div><div class="iq-formulas">Σ PPR\nx̄ = P/G\n15+ wk\nΔ ADP\n01 10 11\nRANK()</div></div></div>',unsafe_allow_html=True)
    st.markdown("### Ask Shiva")
    _ask_shiva_widget("shiva_page")
    _shiva_report_builder()
    history=st.session_state.get("ask_history",[])
    if history:
        with st.expander("Recent Shiva questions",expanded=False):
            for i,item in enumerate(history[:5]):
                if not isinstance(item,dict):continue
                st.markdown(f"**{html.escape(str(item.get('question','')))}**")
                parts=_shiva_answer_sections(item.get("answer",""));st.markdown(parts.get("short","") or str(item.get("answer","")))
'''
        s=s[:body_start]+new_body+s[body_end:]

# Fix home news to actually select ESPN Fantasy Football articles and render four cards in a 2x2 grid.
s=s.replace('st.markdown("#### Latest ESPN NFL")','st.markdown("#### Latest ESPN Fantasy Football")',1)
s=s.replace('if "/fantasy/football/" in txt or "fantasy football" in txt:continue','if "/fantasy/football/" not in txt and "fantasy football" not in txt:continue',1)
s=s.replace('ESPN · NFL','ESPN · Fantasy Football')

p.write_text(s,encoding='utf-8')

# Rewrite the Draft Guide render logic cleanly: no Half-PPR fallback, no undefined position variable.
g=Path('shiva_draft_guide.py')
t=g.read_text(encoding='utf-8')
start=t.find('def render_draft_guide():')
if start!=-1:
    new_render=r'''def render_draft_guide():
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown('<div class="guide-hero"><div class="guide-kicker">2026 Draft Intelligence</div><h2>The Shiva Draft Guide</h2><p>The 2026 Shiva Draft Guide to Success · ESPN Full PPR stats, strategy and draft guidance.</p></div>',unsafe_allow_html=True)
    tab=st.radio('Guide section',['Game Plan','PPR Board','Research','10 Team','12 Team'],horizontal=True,label_visibility='collapsed',key='guide_tab')
    if tab=='Game Plan':
        st.markdown('<div class="strategy-grid"><div class="strategy-box"><span>Rounds 1–2</span><b>Attack elite RB</b></div><div class="strategy-box"><span>RB Goal</span><b>3 of top ~25–30</b></div><div class="strategy-box"><span>WR Windows</span><b>Rounds 3 + 5</b></div><div class="strategy-box"><span>QB Window</span><b>Value after the elite tier</b></div></div>',unsafe_allow_html=True)
        st.markdown('<div class="rounds"><b>Core Full-PPR approach</b><br>Use Shiva rankings against ADP. Build elite weekly ceilings early, protect roster flexibility in the middle rounds, then attack contingent RB value, rookie WR upside and rushing-QB ceiling late.</div>',unsafe_allow_html=True)
        st.markdown('#### Draft Rules')
        rules=[('ADP is the price, not the ranking','The Big Board is Shiva’s independent ranking. Use ADP to decide when you need to pay.'),('Prioritize league-winning ceilings','Do not spend early picks merely to beat ADP by a few spots.'),('Keep roster construction flexible','Avoid forcing a position if the tier value says another position is clearly stronger.'),('Late-round process','Prioritize contingent RB value, rookie WR breakouts, rushing QBs and players attached to elite offenses.'),('Waivers start immediately','Post-draft and early-season waivers can be the highest-leverage roster moves of the year.')]
        for a,b in rules:st.markdown(f'<div class="guide-card"><b>{a}</b><p>{b}</p></div>',unsafe_allow_html=True)
    elif tab=='PPR Board':
        st.caption('2026 Shiva Full-PPR Big Board · independent ranking, not ADP')
        selected=st.multiselect('Filter positions',['QB','RB','WR','TE'],default=['QB','RB','WR','TE'],key='guide_pos_multi',placeholder='All positions')
        board=PPR_BIG_BOARD if not selected else [(p,n) for p,n in PPR_BIG_BOARD if p in selected]
        st.markdown(_rows(board),unsafe_allow_html=True)
    elif tab=='Research':
        st.markdown('#### Draft-Changing Signals')
        for a,b in NUGGETS:st.markdown(f'<div class="guide-card"><b>{html.escape(a)}</b><p>{html.escape(b)}</p></div>',unsafe_allow_html=True)
        st.markdown('#### 2025 Adjusted PPG')
        for pos in ('QB','RB','WR','TE'):
            st.markdown(f'**{pos}**')
            for n,v in ADJ[pos]:st.markdown(f'<div class="adj-row"><span>{html.escape(n)}</span><b>{v:.1f}</b></div>',unsafe_allow_html=True)
    elif tab=='10 Team':
        st.markdown('<div class="rounds"><b>10-Team ESPN Full PPR · Primary Build</b><br>R1 elite RB/WR · R2 elite RB/WR · R3 best remaining ceiling · R4 WR/RB value · R5 WR depth · R6 elite-falling QB/TE or BPA · R7–9 upside starters · R10–12 contingent RB + breakout WR · R13 backup ceiling · R14 D/ST · R15 K/IR.</div>',unsafe_allow_html=True)
        notes=[('Depth changes the strategy','In a 10-team league, replacement value is stronger. Chase difference-makers rather than filling positions early.'),('QB and TE patience','Unless an elite option falls, deeper waivers make it easier to wait at one-off positions.'),('Bench for upside','Use bench spots on players who can become weekly starters, not low-ceiling emergency depth.'),('RB contingency matters','High-value handcuffs and ambiguous backfields can swing a shallow league quickly.')]
        for a,b in notes:st.markdown(f'<div class="guide-card"><b>{a}</b><p>{b}</p></div>',unsafe_allow_html=True)
    elif tab=='12 Team':
        st.markdown('<div class="rounds"><b>12-Team ESPN Full PPR</b><br>R1 cornerstone RB/WR · R2 best elite tier · R3 WR/RB · R4 BPA · R5 WR · R6–8 fill value tiers · R9–12 upside and contingency · R13 deep sleeper · R14 D/ST · R15 K/IR.</div>',unsafe_allow_html=True)
        notes=[('Scarcity matters earlier','Compared with 10-team leagues, the usable waiver pool thins out faster.'),('Protect weekly starters','You can still draft for ceiling, but avoid leaving multiple starting slots dependent on waivers.'),('Know the tier cliffs','When a position is about to lose a usable starter tier, scarcity can outweigh a small ranking edge elsewhere.'),('Keep the Big Board intact','The ranking remains the same; roster size and market timing change how aggressively you act on it.')]
        for a,b in notes:st.markdown(f'<div class="guide-card"><b>{a}</b><p>{b}</p></div>',unsafe_allow_html=True)
'''
    t=t[:start]+new_render+'\n'
g.write_text(t,encoding='utf-8')
