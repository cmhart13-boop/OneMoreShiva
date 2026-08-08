from pathlib import Path

source = Path(__file__).with_name("app_core.py").read_text(encoding="utf-8")
nav_css = r'''
/* Draft room primary navigation — scoped to the four live draft destinations. */
.st-key-draft_view{margin:2px 0 13px!important}
.st-key-draft_view div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:8px!important;width:100%!important}
.st-key-draft_view div[role="radiogroup"] label{position:relative!important;min-height:84px!important;border-radius:14px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:12px 4px 10px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:5px!important;margin:0!important;box-shadow:0 4px 14px rgba(0,0,0,.10)!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important;box-shadow:0 6px 18px rgba(213,22,54,.22)!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:14px;right:14px;bottom:7px;height:2px;border-radius:2px;background:#fff}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:12px!important;font-weight:950!important;white-space:nowrap!important;color:#aab8c4!important;line-height:1!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
.st-key-draft_view div[role="radiogroup"] label:nth-child(1) [data-testid="stMarkdownContainer"] p::before{content:"👥";display:block;font-size:22px;line-height:1.15;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(2) [data-testid="stMarkdownContainer"] p::before{content:"▦";display:block;font-size:25px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(3) [data-testid="stMarkdownContainer"] p::before{content:"☷";display:block;font-size:25px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(4) [data-testid="stMarkdownContainer"] p::before{content:"🛡";display:block;font-size:21px;line-height:1.15;margin-bottom:7px}
@media(max-width:430px){.st-key-draft_view div[role="radiogroup"]{gap:6px!important}.st-key-draft_view div[role="radiogroup"] label{min-height:80px!important;padding-left:2px!important;padding-right:2px!important}.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important}}
'''
source=source.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)","\n"+nav_css+"\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)",1)
old='''def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    is_user_pick=pick_team(n,st.session_state.team_count)==st.session_state.user_slot
    if is_user_pick:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)
    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
'''
new='''def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    # Primary draft navigation belongs directly under the Draft Room heading.
    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    is_user_pick=pick_team(n,st.session_state.team_count)==st.session_state.user_slot
    if is_user_pick:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)
'''
if old not in source: raise RuntimeError("Draft room source changed; refusing unsafe layout patch.")
source=source.replace(old,new,1)
exec(compile(source,str(Path(__file__).with_name("app_core.py")),"exec"),globals(),globals())
