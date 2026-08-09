from pathlib import Path

source = Path(__file__).with_name("app_core.py").read_text(encoding="utf-8")

# OneMoreShiva is the production source of truth.
source = source.replace('\"user_slot\":3', '\"user_slot\":1', 1)

# Splash is launch-only. Normal query-param navigation never replays it.
source = source.replace(
    'if not st.session_state.get("_shiva_startup_splash_seen", False):',
    'if not any(k in st.query_params for k in ("page","player","draft","queue_add")) and not st.session_state.get("_shiva_startup_splash_seen", False):',
    1,
)
source = source.replace('_splash_time.sleep(2.3)', '_splash_time.sleep(2.0)', 1)

# Shared phone-first visual overrides. These are deliberately additive so existing app behavior stays intact.
mobile_css = r'''
/* Draft Room top navigation: four equal full-width cards. */
.st-key-draft_view{display:block!important;width:100%!important;max-width:none!important;margin:2px 0 13px!important}
.st-key-draft_view>div,.st-key-draft_view [data-testid="stRadio"],.st-key-draft_view [data-baseweb="radio-group"]{width:100%!important;max-width:none!important}
.st-key-draft_view div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:7px!important;width:100%!important;max-width:none!important;align-items:stretch!important}
.st-key-draft_view div[role="radiogroup"] label{box-sizing:border-box!important;position:relative!important;width:100%!important;min-width:0!important;max-width:none!important;min-height:84px!important;border-radius:14px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:12px 3px 10px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;margin:0!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:14px;right:14px;bottom:7px;height:2px;border-radius:2px;background:#fff}
.st-key-draft_view div[role="radiogroup"] label>div:first-child{display:none!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%!important;text-align:center!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:13px!important;font-weight:950!important;white-space:nowrap!important;color:#aab8c4!important;line-height:1!important;text-transform:uppercase!important;text-align:center!important;margin:0!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
.st-key-draft_view div[role="radiogroup"] label:nth-child(1) [data-testid="stMarkdownContainer"] p::before{content:"👥";display:block;font-size:24px;line-height:1.15;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(2) [data-testid="stMarkdownContainer"] p::before{content:"▦";display:block;font-size:27px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(3) [data-testid="stMarkdownContainer"] p::before{content:"☷";display:block;font-size:27px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(4) [data-testid="stMarkdownContainer"] p::before{content:"🛡";display:block;font-size:23px;line-height:1.15;margin-bottom:7px}
.player-shell.draft-player{grid-template-columns:44px minmax(0,1fr) 45px 45px 64px!important}
.queue-inline{display:none!important}

/* Global mobile readability. */
.screen-head p{font-size:13px!important;line-height:1.4!important}
.hero-kicker{font-size:12px!important}.hero-card p{font-size:14px!important;line-height:1.45!important}.hero-card h2{font-size:28px!important}
.mini-stat{padding:15px 10px!important;min-height:132px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;overflow:hidden!important;position:relative!important}.mini-stat b{font-size:32px!important;line-height:1!important;color:#fff!important;font-weight:980!important;text-shadow:0 2px 8px rgba(0,0,0,.25)!important}.mini-stat span{font-size:13px!important;line-height:1.28!important;letter-spacing:0!important;text-transform:none!important;margin-top:11px!important;color:#eef4f7!important;font-weight:800!important}
.quick-card{min-height:112px!important;padding:17px!important}.quick-icon{font-size:29px!important}.quick-title{font-size:18px!important;line-height:1.18!important;margin-top:5px!important}.quick-sub{font-size:13px!important;line-height:1.4!important;margin-top:4px!important;color:#c3ced6!important}
.player-name{font-size:16px!important}.player-meta{font-size:11px!important}.data-cell span{font-size:9px!important}.data-cell b{font-size:13px!important}.draft-inline{font-size:12px!important}
.draft-chip{padding:10px!important}.draft-chip span{font-size:10px!important}.draft-chip b{font-size:18px!important}.on-clock{font-size:14px!important;line-height:1.25!important;padding:12px 13px!important}
.profile-sub{font-size:12px!important;line-height:1.4!important}.profile-metric{padding:11px!important}.profile-metric b{font-size:20px!important}.profile-metric span{font-size:10px!important;line-height:1.2!important}
.weekly-card .wk{font-size:13px!important}.weekly-card .opp{font-size:12px!important}.weekly-card .pts{font-size:17px!important}.weekly-card .detail{font-size:11px!important;line-height:1.25!important}
.roster-slot{padding:12px!important}.slot-tag{font-size:11px!important}.slot-player{font-size:14px!important}.slot-meta{font-size:11px!important}.shiva-box p{font-size:13px!important;line-height:1.4!important}.answer{font-size:14px!important;line-height:1.5!important}.stButton>button{font-size:14px!important}.bottom-nav a{font-size:11px!important}
.shiva-iq-title{font-size:16px!important}.shiva-iq-live{font-size:10px!important}.shiva-iq-copy{font-size:12px!important;line-height:1.4!important}.iq-label{font-size:9px!important}.iq-name{font-size:15px!important}.iq-meta{font-size:10px!important}.iq-reason{font-size:11px!important;line-height:1.35!important}.iq-draft{font-size:11px!important}.iq-locked{font-size:11px!important}

/* Home Ask Shiva + descriptive stat cards. */
.home-shiva-hero{background:linear-gradient(140deg,#182b3b,#0a1219 68%);border:1px solid #365167;border-radius:19px;padding:17px 16px 15px;margin:3px 0 8px;position:relative;overflow:hidden}.home-shiva-hero:after{content:"✦";position:absolute;right:12px;top:-12px;font-size:94px;color:#ec1738;opacity:.10}.home-shiva-kicker{font-size:11px;font-weight:950;color:#d9ff38;letter-spacing:1px;text-transform:uppercase}.home-shiva-title{font-size:27px;font-weight:980;color:#fff;letter-spacing:-.8px;line-height:1.05;margin-top:5px}.home-shiva-copy{font-size:14px;color:#b6c2cb;line-height:1.4;margin-top:6px;max-width:90%}.home-ask-label{font-size:12px;font-weight:900;color:#c6d2da;margin:2px 0 3px}.work-note{font-size:12px;color:#aebdc7;line-height:1.45}.work-note b{color:#fff}
.metric-rb{background:linear-gradient(135deg,rgba(240,161,94,.46) 0%,rgba(118,67,34,.28) 42%,#0e1821 100%)!important;border-color:rgba(240,161,94,.48)!important}.metric-wr{background:linear-gradient(135deg,rgba(93,164,242,.46) 0%,rgba(37,82,137,.28) 42%,#0e1821 100%)!important;border-color:rgba(93,164,242,.48)!important}.metric-ppg{background:linear-gradient(135deg,rgba(82,214,139,.43) 0%,rgba(31,102,67,.27) 42%,#0e1821 100%)!important;border-color:rgba(82,214,139,.46)!important}.metric-weeks{background:linear-gradient(135deg,rgba(229,195,75,.44) 0%,rgba(111,88,25,.27) 42%,#0e1821 100%)!important;border-color:rgba(229,195,75,.46)!important}.metric-rb b,.metric-rb span,.metric-wr b,.metric-wr span,.metric-ppg b,.metric-ppg span,.metric-weeks b,.metric-weeks span{color:#fff!important}
.quick-card.q-draft{border-color:#3b78a7!important;background:linear-gradient(135deg,rgba(59,120,167,.34) 0%,rgba(26,56,78,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(59,120,167,.15)}.quick-card.q-guide{border-color:#9a5ac9!important;background:linear-gradient(135deg,rgba(154,90,201,.34) 0%,rgba(70,40,91,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(154,90,201,.15)}.quick-card.q-players{border-color:#2c9b82!important;background:linear-gradient(135deg,rgba(44,155,130,.33) 0%,rgba(20,72,61,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(44,155,130,.15)}.quick-card.q-roster{border-color:#b8873d!important;background:linear-gradient(135deg,rgba(184,135,61,.34) 0%,rgba(82,58,26,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(184,135,61,.15)}
@media(max-width:430px){.stat-strip{gap:7px!important}.mini-stat{min-height:136px!important;padding:13px 7px!important}.mini-stat b{font-size:31px!important}.mini-stat span{font-size:12px!important;line-height:1.28!important}.quick-card{min-height:112px!important;padding:15px!important}.quick-icon{font-size:28px!important}.quick-title{font-size:17px!important}.quick-sub{font-size:12.5px!important}.st-key-draft_view div[role="radiogroup"]{gap:6px!important}.st-key-draft_view div[role="radiogroup"] label{min-height:84px!important;padding-left:2px!important;padding-right:2px!important}.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:12px!important}.player-shell.draft-player{grid-template-columns:36px minmax(0,1fr) 37px 37px 58px!important;padding-left:6px!important;padding-right:6px!important}}
'''
source = source.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)", "\n" + mobile_css + "\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)", 1)

# Draft view selector remains directly below the Draft Room heading.
draft_start = source.index('def draft():')
draft_end = source.index('\ndef player_db():', draft_start)
draft_block = source[draft_start:draft_end]
old_line = '    screen_head("Draft Room","Live snake draft built for a phone.")\n    slot_options=list(range(1,st.session_state.team_count+1))'
new_line = '    screen_head("Draft Room","Live snake draft built for a phone.")\n    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")\n    slot_options=list(range(1,st.session_state.team_count+1))'
if old_line in draft_block:
    draft_block = draft_block.replace(old_line, new_line, 1)
    draft_block = draft_block.replace('    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")\n', '', 1) if draft_block.count('view=st.radio("Draft view"') > 1 else draft_block
source = source[:draft_start] + draft_block + source[draft_end:]

# Keep draft actions recoverable with Undo + Reset.
source = source.replace(
    '    if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()\ndef player_db():',
    '''    ctrl1,ctrl2=st.columns(2)\n    with ctrl1:\n        if st.button("↶ Undo Last Pick",use_container_width=True,disabled=not bool(st.session_state.draft_log)):\n            last_user_idx=next((i for i in range(len(st.session_state.draft_log)-1,-1,-1) if st.session_state.draft_log[i]["team"]==st.session_state.user_slot),None)\n            if last_user_idx is not None:st.session_state.draft_log=st.session_state.draft_log[:last_user_idx]\n            else:st.session_state.draft_log=st.session_state.draft_log[:-1]\n            st.session_state["shiva_iq_recs"]=[];st.rerun()\n    with ctrl2:\n        if st.button("↻ Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["shiva_iq_recs"]=[];st.rerun()\ndef player_db():''',
    1,
)

# Header: move Command Center into the permanent Shiva branding row.
header_start = source.index('def app_header():')
header_end = source.index('\ndef bottom_nav', header_start)
new_header = '''def app_header():\n    live=rankings_status=="CONNECTED"\n    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">🏆</div><div><div class="brand-title">SHIVA COMMAND CENTER</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div><div class="data-status">● {"DATA LIVE" if live else "DATA FALLBACK"}</div></div>',unsafe_allow_html=True)\n'''
source = source[:header_start] + new_header + source[header_end:]

# Shared internal-data-first Shiva engine.
ask_start = source.index('def ask_shiva(question:str)->str:')
ask_end = source.index('\ndef home():', ask_start)
new_ask = r'''def _shiva_parse_top_n(question:str)->int:
    m=re.search(r"\btop\s+(\d{1,2})\b",question.casefold())
    return max(1,min(25,int(m.group(1)))) if m else 5

def _shiva_position(question:str)->str|None:
    q=question.casefold()
    aliases={"RB":["running back","running backs"," rb ","rbs"],"WR":["wide receiver","wide receivers"," wr ","wrs"],"QB":["quarterback","quarterbacks"," qb ","qbs"],"TE":["tight end","tight ends"," te ","tes"]}
    padded=f" {q} "
    for pos,words in aliases.items():
        if any(w in padded for w in words):return pos
    return None

def _shiva_years(question:str,weekly:pd.DataFrame)->list[int]:
    available=sorted(pd.to_numeric(weekly.get("season",pd.Series(dtype=float)),errors="coerce").dropna().astype(int).unique().tolist())
    if not available:return []
    explicit=sorted({int(y) for y in re.findall(r"\b20\d{2}\b",question) if int(y) in available})
    if len(explicit)>=2:
        lo,hi=min(explicit),max(explicit);return [y for y in available if lo<=y<=hi]
    if len(explicit)==1:return explicit
    q=question.casefold();m=re.search(r"last\s+(\d{1,2})\s+(?:years|seasons)",q)
    n=max(1,min(12,int(m.group(1)))) if m else 5
    return available[-n:]

def _shiva_name_col(weekly:pd.DataFrame)->str|None:
    return next((c for c in ("player_display_name","player_name","name") if c in weekly.columns),None)

def _shiva_internal_result(question:str)->dict:
    result={"answer":"","method":"","data_used":"","seasons":"","table":pd.DataFrame(),"internal":False}
    q=question.casefold().strip()
    try:weekly=load_weekly().copy()
    except Exception as exc:
        result["method"]=f"Internal weekly database could not be loaded: {exc}";return result
    nc=_shiva_name_col(weekly)
    if weekly.empty or not nc:return result
    weekly["_ppr"]=espn_ppr(weekly)
    years=_shiva_years(question,weekly)
    if years:weekly=weekly.loc[pd.to_numeric(weekly["season"],errors="coerce").isin(years)].copy()
    pos=_shiva_position(question)
    poscol="position" if "position" in weekly.columns else None
    if pos and poscol:
        weekly=weekly.loc[weekly[poscol].astype(str).str.upper().replace({"HB":"RB","FB":"RB","D/ST":"DST","DEF":"DST"}).eq(pos)].copy()
    names=[]
    for n in players["name"].astype(str).tolist():
        if name_key(n) and name_key(n) in name_key(question):names.append(n)
    metric="ppg"
    if "total" in q and ("point" in q or "ppr" in q):metric="total"
    if "15+" in q or "15 plus" in q or "15-point" in q or "15 point" in q:metric="weeks15"
    if any(x in q for x in ("average","per game","ppg")):metric="ppg"

    if names:
        rows=[]
        for name in names[:6]:
            pf=weekly.loc[weekly[nc].astype(str).map(name_key).eq(name_key(name))].copy()
            if pf.empty:continue
            pts=pf["_ppr"].dropna();rows.append({"Player":name,"Games":len(pts),"Total PPR":round(float(pts.sum()),1),"PPR/Game":round(float(pts.mean()),2) if len(pts) else None,"15+ PPR Weeks":int((pts>=15).sum())})
        if rows:
            df=pd.DataFrame(rows);result.update(internal=True,table=df,seasons=", ".join(map(str,years)) if years else "all available seasons",data_used="Internal weekly player history and ESPN full-PPR scoring")
            result["method"]="For each named player, Shiva filtered the internal weekly game log to the selected seasons, calculated PPR points for each game, then summarized games, total PPR, PPR per game, and 15+ point weeks."
            result["answer"]="Here’s the internal-data comparison:\n\n"+"\n".join(f"**{r['Player']}** — {r['PPR/Game']:.2f} PPR/game, {r['Total PPR']:.1f} total PPR, {r['15+ PPR Weeks']} weeks of 15+ points across {r['Games']} games." for r in rows)
            return result

    ranking_words=("top","best","highest","leaders","most")
    if any(w in q for w in ranking_words) and (pos or "player" in q or "ppr" in q or "point" in q):
        grouped=weekly.groupby(nc,dropna=True)["_ppr"].agg(Games="count",Total_PPR="sum",PPR_Game="mean",Weeks_15=lambda x:int((x>=15).sum())).reset_index().rename(columns={nc:"Player"})
        grouped=grouped.loc[grouped["Games"]>=3].copy()
        n=_shiva_parse_top_n(question)
        sortcol={"ppg":"PPR_Game","total":"Total_PPR","weeks15":"Weeks_15"}[metric]
        top=grouped.sort_values([sortcol,"Games"],ascending=[False,False]).head(n).copy()
        top["Total PPR"]=top["Total_PPR"].round(1);top["PPR/Game"]=top["PPR_Game"].round(2);top["15+ PPR Weeks"]=top["Weeks_15"].astype(int)
        table=top[["Player","Games","Total PPR","PPR/Game","15+ PPR Weeks"]].reset_index(drop=True);table.index=table.index+1
        metric_label={"ppg":"PPR per game","total":"total PPR points","weeks15":"15+ PPR-point weeks"}[metric]
        lines=[]
        for rank,(_,r) in enumerate(table.iterrows(),1):lines.append(f"**{rank}. {r['Player']}** — {r['PPR/Game']:.2f} PPR/game, {r['Total PPR']:.1f} total, {int(r['15+ PPR Weeks'])} weeks of 15+ points.")
        result.update(internal=True,table=table,seasons=", ".join(map(str,years)) if years else "all available seasons",data_used=f"Internal weekly game log{f' filtered to {pos}' if pos else ''} with ESPN full-PPR scoring",method=f"Shiva filtered the internal weekly database to {', '.join(map(str,years)) if years else 'the available seasons'}{f' and {pos}s' if pos else ''}, calculated PPR for each player-game, grouped by player, then ranked the results by {metric_label}. Players needed at least three games in the filtered sample.",answer=f"Using the app’s internal data, the top {len(table)}{f' {pos}s' if pos else ' players'} by {metric_label} are:\n\n"+"\n".join(lines))
        return result

    if any(x in q for x in ("who should i draft","who do i draft","draft next","best available","my roster")):
        avail=available_df().head(12).copy();rost=user_roster();cols=[c for c in ("name","pos","team","draft_adp","overall_rank") if c in avail.columns]
        table=avail[cols].rename(columns={"name":"Player","pos":"Pos","team":"Team","draft_adp":"ADP","overall_rank":"Rank"}).copy()
        roster_text=", ".join(f"{r['name']} ({r['pos']})" for _,r in rost.iterrows()) if not rost.empty else "No players drafted yet"
        first=table.iloc[0] if not table.empty else None
        answer=(f"Based on the live internal draft board, **{first['Player']} ({first['Pos']})** is the best available market-value option right now. " if first is not None else "The internal available-player pool is empty. ")+f"Your current roster: {roster_text}."
        result.update(internal=True,table=table,seasons="Current 2026 draft state",data_used="Live available-player pool, rankings/ADP, and your current drafted roster",method="Shiva read the app’s live roster and available-player pool first, then ordered the current options by the app’s draft market/ranking data before any AI explanation.",answer=answer)
        return result
    return result

def ask_shiva_full(question:str)->dict:
    internal=_shiva_internal_result(question)
    answer=internal.get("answer","")
    key=None
    try:key=st.secrets.get("OPENAI_API_KEY")
    except Exception:pass
    key=key or os.getenv("OPENAI_API_KEY")
    if key and OpenAI is not None:
        roster=user_roster();rt=", ".join(roster["name"].tolist()) if not roster.empty else "None"
        evidence=internal.get("table",pd.DataFrame())
        evidence_text=evidence.to_string(index=False) if isinstance(evidence,pd.DataFrame) and not evidence.empty else "No structured internal table was generated."
        system="You are Shiva, an elite fantasy-football analyst. ESPN full 1-point PPR is the default. INTERNAL APP DATA IS AUTHORITATIVE. Never alter, invent, or contradict supplied numbers. If internal evidence answers the question, explain it clearly and concisely. If it does not, say what is uncertain."
        prompt=f"Question: {question}\nCurrent roster: {rt}\nInternal answer: {answer or 'No deterministic internal answer'}\nInternal evidence:\n{evidence_text}\nMethod: {internal.get('method','')}\nGive the user a concise useful answer."
        try:
            ai=OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=[{"role":"system","content":system},{"role":"user","content":prompt}]).output_text
            if ai:answer=ai
        except Exception:
            if not answer:answer="Shiva’s AI explanation is temporarily unavailable, but the app’s internal data engine is still online. Try a statistical, player-history, ranking, or live-draft question."
    if not answer:
        answer="I can answer directly from Shiva’s internal database for player history, PPR scoring, multi-season leaders, rankings, ADP, and your live draft state. Try something like: “Top 5 RBs by PPR per game over the last 5 seasons.”"
        internal["method"]="No matching deterministic internal query pattern was found, so no statistic was fabricated."
        internal["data_used"]="No internal result generated"
        internal["seasons"]="—"
    internal["answer"]=answer
    return internal

def ask_shiva(question:str)->str:
    return ask_shiva_full(question).get("answer","")

def _render_shiva_work(item:dict,key:str):
    with st.expander("* See Shiva's work",expanded=False):
        st.markdown(f'<div class="work-note"><b>Data used:</b> {html.escape(str(item.get("data_used") or "Internal app data"))}<br><b>Seasons / scope:</b> {html.escape(str(item.get("seasons") or "—"))}<br><b>How Shiva calculated it:</b> {html.escape(str(item.get("method") or "No calculation details available."))}</div>',unsafe_allow_html=True)
        table=item.get("table")
        if isinstance(table,pd.DataFrame) and not table.empty:st.dataframe(table,use_container_width=True)

def _ask_shiva_widget(prefix:str):
    q=st.text_area("Ask Shiva",placeholder="Ask about players, PPR history, rankings, your roster, or who to draft…",height=92,key=f"{prefix}_q",label_visibility="collapsed")
    if st.button("✦ GET SHIVA'S ANSWER",type="primary",use_container_width=True,key=f"{prefix}_go") and q.strip():
        with st.spinner("Reading Shiva's internal data…"):
            result=ask_shiva_full(q.strip())
        st.session_state[f"{prefix}_result"]={"question":q.strip(),**result}
        hist=st.session_state.get("ask_history",[])
        hist.insert(0,st.session_state[f"{prefix}_result"]);st.session_state["ask_history"]=hist[:12]
    item=st.session_state.get(f"{prefix}_result")
    if item:
        st.markdown(f'<div class="answer">{html.escape(str(item.get("answer",""))).replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
        _render_shiva_work(item,prefix)
'''
source = source[:ask_start] + new_ask + source[ask_end:]

# Home: Shiva first, then descriptive stats, Blast, shortcuts, and four NFL stories.
home_start = source.index('def home():')
home_end = source.index('\ndef draft_guide():', home_start)
new_home = r'''def _home_shiva_blast():
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;height:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      #stage{position:fixed;inset:0;display:none;align-items:center;justify-content:center;background:rgba(2,7,12,.62);backdrop-filter:blur(4px);padding:58px 16px 20px;box-sizing:border-box}
      #stage.open{display:flex}
      #blastVideo{display:block;width:auto;max-width:min(92vw,430px);height:auto;max-height:78vh;object-fit:contain;border-radius:16px;background:#000;box-shadow:0 18px 55px rgba(0,0,0,.62)}
      #shivaBlast{position:fixed;top:0;right:0;width:122px;height:40px;border-radius:12px;border:1px solid rgba(255,92,112,.48);background:linear-gradient(135deg,rgba(202,24,53,.78),rgba(112,10,31,.58) 58%,rgba(42,11,21,.44));color:#fff;font-weight:900;font-size:12px;letter-spacing:.2px;cursor:pointer;box-shadow:0 6px 18px rgba(111,9,30,.22);backdrop-filter:blur(7px);z-index:5}
      #shivaBlast.playing{top:14px;right:14px;width:112px;background:linear-gradient(135deg,rgba(160,20,43,.86),rgba(76,8,22,.72));border-color:rgba(255,112,130,.55)}
      #shivaBlast:active{transform:scale(.97)}
    </style>
    <div id="stage"><video id="blastVideo" playsinline preload="metadata"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    <button id="shivaBlast">⚡ SHIVA BLAST</button>
    <script>
      const btn=document.getElementById('shivaBlast');
      const stage=document.getElementById('stage');
      const video=document.getElementById('blastVideo');
      let playing=false;
      const frame=()=>window.frameElement;
      const floatFrame=()=>{try{const f=frame();if(!f)return;f.style.position='fixed';f.style.top='58px';f.style.right='12px';f.style.left='auto';f.style.bottom='auto';f.style.width='122px';f.style.height='40px';f.style.zIndex='2147483000';f.style.border='0';f.style.background='transparent';f.style.boxShadow='none';}catch(e){}};
      const overlayFrame=()=>{try{const f=frame();if(!f)return;f.style.position='fixed';f.style.inset='0';f.style.width='100vw';f.style.height='100dvh';f.style.zIndex='2147483000';f.style.border='0';f.style.background='transparent';}catch(e){}};
      const closeBlast=()=>{playing=false;video.pause();video.currentTime=0;stage.classList.remove('open');btn.classList.remove('playing');btn.textContent='⚡ SHIVA BLAST';floatFrame();};
      const openBlast=()=>{playing=true;overlayFrame();stage.classList.add('open');btn.classList.add('playing');btn.textContent='✕ STOP BLAST';video.currentTime=0;video.muted=false;const p=video.play();if(p&&p.catch)p.catch(()=>{video.controls=true;});};
      btn.addEventListener('click',()=>playing?closeBlast():openBlast());
      video.addEventListener('click',closeBlast);
      video.addEventListener('ended',()=>setTimeout(closeBlast,160));
      floatFrame();
    </script>
    """,height=1,scrolling=False)

def _home_nfl_news():
    st.markdown("#### Latest ESPN NFL")
    try:
        import json as _json
        from urllib.request import Request as _Request,urlopen as _urlopen
        req=_Request("https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=30",headers={"User-Agent":"Mozilla/5.0 (iPhone; Shiva Fantasy Football)"})
        with _urlopen(req,timeout=8) as resp:data=_json.loads(resp.read().decode("utf-8"))
        articles=[]
        for a in data.get("articles",[]):
            links=a.get("links",{}) or {};web=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            imgs=a.get("images") or [];img=imgs[0].get("url") if imgs and isinstance(imgs[0],dict) else ""
            headline=str(a.get("headline") or "").strip()
            if not headline or not web or not img:continue
            txt=(headline+" "+str(a.get("description") or "")+" "+web).casefold()
            if "/fantasy/football/" in txt or "fantasy football" in txt:continue
            articles.append((headline,web,img))
            if len(articles)==4:break
        cards=[]
        for headline,web,img in articles:
            h=html.escape(headline);u=html.escape(web,quote=True);im=html.escape(img,quote=True)
            cards.append(f'<a class="espn-news-card" href="{u}" target="_blank" rel="noopener noreferrer"><div class="espn-news-img"><img src="{im}" alt=""></div><div class="espn-news-body"><div class="espn-news-headline">{h}</div><div class="espn-news-meta">ESPN · NFL</div></div></a>')
        if cards:
            news_css_html = "<style>.espn-news-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:7px 0 14px}.espn-news-card{display:block;overflow:hidden;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #253644;border-radius:14px;box-shadow:0 5px 16px rgba(0,0,0,.16)}.espn-news-img{width:100%;aspect-ratio:16/9;background:#172430;overflow:hidden}.espn-news-img img{display:block;width:100%;height:100%;object-fit:cover}.espn-news-body{padding:9px 10px 10px}.espn-news-headline{font-size:13px;font-weight:950;line-height:1.28;color:#fff;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;min-height:48px}.espn-news-meta{font-size:10px;color:#8fa0ae;margin-top:7px;font-weight:850;text-transform:uppercase}</style><div class=\"espn-news-grid\">" + "".join(cards) + "</div>"
            st.markdown(news_css_html,unsafe_allow_html=True)
        else:st.caption("NFL headlines are refreshing.")
    except Exception:st.caption("NFL headlines are refreshing.")

def home():
    st.markdown('<div class="home-shiva-hero"><div class="home-shiva-kicker">Your fantasy football copilot</div><div class="home-shiva-title">Shiva Draft Intelligence</div><div class="home-shiva-copy">Ask Shiva for help building your championship team. Player history, PPR scoring, rankings and your live draft data are checked inside the app first.</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="home-ask-label">Ask Shiva anything</div>',unsafe_allow_html=True)
    _ask_shiva_widget("home_shiva")
    try:
        w=load_weekly();sw=w.loc[pd.to_numeric(w.get("season"),errors="coerce").eq(2025)].copy();nc=weekly_name_col(sw);sw["_ppr"]=espn_ppr(sw)
        g=sw.groupby(nc,dropna=True)["_ppr"].agg(ppg="mean",weeks15=lambda x:int((x>=15).sum())) if nc else pd.DataFrame();top_ppg=float(g["ppg"].max()) if not g.empty else 0;top15=int(g["weeks15"].max()) if not g.empty else 0;rb_count=wr_count=0
        if nc and "position" in sw.columns:
            sw["_pos"]=sw["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB"});gp=sw.groupby([nc,"_pos"],dropna=True)["_ppr"].agg(weeks15=lambda x:int((x>=15).sum())).reset_index();rb_count=int(((gp["_pos"]=="RB")&(gp["weeks15"]>=8)).sum());wr_count=int(((gp["_pos"]=="WR")&(gp["weeks15"]>=8)).sum())
        st.markdown(f'<div class="stat-strip"><div class="mini-stat metric-rb"><b>{rb_count}</b><span>Running backs with 8+ weeks of 15+ PPR points</span></div><div class="mini-stat metric-wr"><b>{wr_count}</b><span>Wide receivers with 8+ weeks of 15+ PPR points</span></div><div class="mini-stat metric-ppg"><b>{top_ppg:.1f}</b><span>Highest average PPR points per game in 2025</span></div><div class="mini-stat metric-weeks"><b>{top15}</b><span>Most weeks of 15+ PPR points by one player in 2025</span></div></div>',unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="stat-strip"><div class="mini-stat metric-rb"><b>—</b><span>Running backs with 8+ weeks of 15+ PPR points</span></div><div class="mini-stat metric-wr"><b>—</b><span>Wide receivers with 8+ weeks of 15+ PPR points</span></div><div class="mini-stat metric-ppg"><b>—</b><span>Highest average PPR points per game in 2025</span></div><div class="mini-stat metric-weeks"><b>—</b><span>Most weeks of 15+ PPR points by one player in 2025</span></div></div>',unsafe_allow_html=True)
    _home_shiva_blast()
    st.markdown('<div class="quick-grid">'+f'<a class="quick-card q-draft" href="{page_href("Draft")}" target="_self"><div class="quick-icon">🏈</div><div class="quick-title">Draft Room</div><div class="quick-sub">Players, board, queue and roster</div></a>'+f'<a class="quick-card q-guide" href="{page_href("Guide")}" target="_self"><div class="quick-icon">📖</div><div class="quick-title">2026 Shiva Draft Guide</div><div class="quick-sub">Draft-day strategy and rankings</div></a>'+f'<a class="quick-card q-players" href="{page_href("Players")}" target="_self"><div class="quick-icon">👥</div><div class="quick-title">Players</div><div class="quick-sub">Profiles and weekly history</div></a>'+f'<a class="quick-card q-roster" href="{page_href("Roster")}" target="_self"><div class="quick-icon">☷</div><div class="quick-title">My Roster</div><div class="quick-sub">Your live construction by slot</div></a></div>',unsafe_allow_html=True)
    _home_nfl_news()
'''
source = source[:home_start] + new_home + source[home_end:]

# Dedicated Shiva page reuses the exact same engine and evidence UI as Home.
shiva_start = source.index('def shiva():')
shiva_end = source.index('\ndef roster_screen():', shiva_start)
new_shiva = r'''def shiva():
    screen_head("Ask Shiva","Internal app data first. AI explanation second.")
    st.markdown('<div class="shiva-box"><h2>✦ Shiva Intelligence</h2><p>Ask about player history, multi-season PPR leaders, rankings, your roster, or who to draft next.</p></div>',unsafe_allow_html=True)
    _ask_shiva_widget("shiva_page")
    history=st.session_state.get("ask_history",[])
    if history:
        st.markdown("#### Recent Shiva Questions")
        for i,item in enumerate(history[:5]):
            if not isinstance(item,dict):continue
            st.markdown(f"**{html.escape(str(item.get('question','')))}**")
            st.markdown(f'<div class="answer">{html.escape(str(item.get("answer",""))).replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
            _render_shiva_work(item,f"hist_{i}")
'''
source = source[:shiva_start] + new_shiva + source[shiva_end:]

exec(compile(source, str(Path(__file__).with_name("app_core.py")), "exec"), globals(), globals())
