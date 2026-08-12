from pathlib import Path
import ast
import re

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'app_core.py'
s=p.read_text(encoding='utf-8')

imp='from shiva_coach import inject_css as inject_coach_css, render_season_hub, render_draft_moment\n'
anchor='from shiva_draft_iq import render_shiva_draft_iq\n'
if imp not in s:
    s=s.replace(anchor,anchor+imp,1)

mark='''SHIVA_MARK = r"""<svg class="shiva-trophy-mark" viewBox="0 0 70 110" aria-label="The Shiva trophy" role="img">
<defs><linearGradient id="wood" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#6f4728"/><stop offset="1" stop-color="#2e1a0f"/></linearGradient><linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f0d17b"/><stop offset="1" stop-color="#9d7625"/></linearGradient></defs>
<rect x="18" y="2" width="34" height="25" rx="2" fill="url(#gold)"/><rect x="21" y="5" width="28" height="19" rx="1.5" fill="#1b2025"/><circle cx="35" cy="12" r="4.2" fill="#b99674"/><path d="M27 22c1.8-5 5-7 8-7s6.2 2 8 7" fill="#58616a"/>
<path d="M13 30h44l-3 11H16z" fill="url(#gold)"/><rect x="20" y="33" width="30" height="5" rx="1" fill="#1d2124"/><text x="35" y="37" fill="#e6cf89" font-size="5" font-weight="800" text-anchor="middle">THE SHIVA</text>
<rect x="8" y="42" width="54" height="7" rx="1.5" fill="url(#wood)"/><rect x="14" y="49" width="5" height="35" rx="2" fill="url(#gold)"/><rect x="51" y="49" width="5" height="35" rx="2" fill="url(#gold)"/>
<circle cx="35" cy="57" r="6" fill="#777f86"/><path d="M31 55c2-6 7-8 11-4-1 5-4 8-9 10z" fill="#b4bbc0"/><path d="M29 64c3-5 9-5 12 0l-1 10H30z" fill="#8d969d"/><path d="M28 74h14l4 6H24z" fill="url(#gold)"/>
<rect x="11" y="84" width="48" height="7" rx="1.5" fill="url(#wood)"/><path d="M16 91h38l5 15H11z" fill="url(#wood)"/><rect x="19" y="95" width="32" height="7" rx="1" fill="#8b6b3c"/><text x="35" y="100" fill="#24170e" font-size="4.5" font-weight="900" text-anchor="middle">SHIVA</text></svg>"""
'''
if 'SHIVA_MARK = r"""' not in s:
    idx=s.index('RANKINGS_URL =')
    s=s[:idx]+mark+'\n'+s[idx:]
s=s.replace('<div class="brand-badge">🏆</div>','<div class="brand-badge">{SHIVA_MARK}</div>',1)

s=s.replace('PAGES = ["Home","Draft","Guide","Players","Shiva","Roster","Analytics"]','PAGES = ["Home","Draft","Guide","Players","Shiva","Roster","Analytics","Coach"]',1)
s=s.replace('"Analytics":"▥"}','"Analytics":"▥","Coach":"✦"}',1)
s=s.replace('nav_pages=["Shiva","Guide","Draft","Analytics"]','nav_pages=["Shiva","Draft","Guide","Coach"]',1)
s=s.replace("label={'Shiva':'Shiva Says','Guide':'Guide','Draft':'Draft','Analytics':'Shiva Lab'}.get(p,p)","label={'Shiva':'Home','Draft':'Draft','Guide':'Guide','Coach':'Coach'}.get(p,p)",1)

css_call='st.markdown(CSS, unsafe_allow_html=True)'
if 'inject_coach_css()' not in s:
    s=s.replace(css_call,css_call+'\ninject_coach_css()',1)

success=re.compile(r"\s*st\.markdown\(f'<div class=\"stat-strip\"><div class=\"mini-stat\"><b>\{rb_count\}</b>.*?</div></div>',unsafe_allow_html=True\)",re.S)
repl='''\n        st.markdown(f\'<div class="home-insight-grid"><div class="home-insight"><span>RELIABLE RB POOL</span><b>{rb_count}</b><p>running backs produced 8+ games of 15 PPR points in 2025.</p></div><div class="home-insight"><span>RELIABLE WR POOL</span><b>{wr_count}</b><p>wide receivers produced 8+ games of 15 PPR points in 2025.</p></div></div>\',unsafe_allow_html=True)'''
s,_=success.subn(repl,s,count=1)
fallback=re.compile(r"\s*st\.markdown\('<div class=\"stat-strip\"><div class=\"mini-stat\"><b>—</b>.*?</div></div>',unsafe_allow_html=True\)",re.S)
fallback_repl='''\n        st.markdown(\'<div class="home-insight-grid"><div class="home-insight"><span>CONSISTENCY</span><b>—</b><p>Historical consistency data is temporarily unavailable.</p></div><div class="home-insight"><span>CEILING</span><b>—</b><p>Historical ceiling data is temporarily unavailable.</p></div></div>\',unsafe_allow_html=True)'''
s,_=fallback.subn(fallback_repl,s,count=1)

s=s.replace('<div class="quick-title">My Roster</div><div class="quick-sub">Live construction by slot</div>','<div class="quick-title">Shiva Coach</div><div class="quick-sub">Compare decisions and catch roster edges</div>',1)
s=s.replace('href="{page_href("Roster")}"','href="{page_href("Coach")}"',1)

draft_anchor='    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)'
if 'render_draft_moment(st.session_state.draft_log' not in s:
    s=s.replace(draft_anchor,'    render_draft_moment(st.session_state.draft_log,n,st.session_state.team_count,st.session_state.user_slot)\n'+draft_anchor,1)

if '\ndef season_coach():\n' not in s:
    coach='''\ndef season_coach():\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")\n    render_season_hub(players,load_weekly,weekly_for_player,espn_ppr)\n\n'''
    s=s.replace('\ndef roster_screen():\n',coach+'def roster_screen():\n',1)

route='{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics}[page]();bottom_nav(page)'
s=s.replace(route,'{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics,"Coach":season_coach}[page]();bottom_nav(page)',1)
s=s.replace('    render_draft_guide()','    render_draft_guide(players,profile_href)',1)

marker="\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)"
extra=r'''
/* SHIVA EXPERIENCE COMPLETION */
.shiva-trophy-mark{display:block;width:31px;height:45px}.brand-badge{height:48px!important;width:42px!important;border-radius:10px!important;padding:2px!important;background:linear-gradient(145deg,#17191b,#090b0d)!important}.brand-wrap{align-items:center!important}.app-top{min-height:58px!important}
.home-insight-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:9px 0 13px}.home-insight{background:linear-gradient(145deg,#121a21,#0c1217);border:1px solid rgba(216,179,91,.18);border-radius:14px;padding:14px;min-height:132px}.home-insight span{display:block;font-size:10px;font-weight:950;letter-spacing:.65px;color:#d8b35b}.home-insight b{display:block;font-size:38px;line-height:1;margin:9px 0 7px;color:#fff;letter-spacing:-1.2px}.home-insight p{font-size:13px;line-height:1.38;color:#abb6be;margin:0}.quick-title{font-size:15px!important}.quick-sub{font-size:12px!important;line-height:1.35!important}.quick-card{min-height:104px!important}.bottom-nav a{font-size:10.5px!important}.draft-moment{margin:7px 0 10px!important}@media(max-width:430px){.home-insight-grid{grid-template-columns:1fr}.home-insight{min-height:112px}.home-insight b{font-size:34px}.home-insight p{font-size:13px}.quick-grid{grid-template-columns:1fr 1fr}.quick-card{min-height:102px;padding:13px!important}.brand-title{font-size:19px!important}}
'''
if '/* SHIVA EXPERIENCE COMPLETION */' not in s and marker in s:
    s=s.replace(marker,'\n'+extra+marker,1)

p.write_text(s,encoding='utf-8')
ast.parse(s)

g=ROOT/'shiva_draft_guide.py'
t=g.read_text(encoding='utf-8')
old="def _rows(items):\n    return ''.join(f'<div class=\"rank-row\"><div class=\"rank-n\">{i}</div><div class=\"pos-chip pc-{p}\">{p}</div><div class=\"rank-name\">{html.escape(n)}</div></div>' for i,(p,n) in enumerate(items,1))"
new='''def _rows(items, players=None, profile_href=None):\n    out=[]\n    for i,(p,n) in enumerate(items,1):\n        name_html=html.escape(n)\n        if players is not None and profile_href is not None:\n            m=players.loc[players["name"].astype(str).str.casefold().eq(str(n).casefold())]\n            if not m.empty:\n                href=profile_href(m.iloc[0],"Guide")\n                name_html=f'<a class="guide-player-link" href="{href}" target="_self">{name_html}<span>View →</span></a>'\n        out.append(f'<div class="rank-row"><div class="rank-n">{i}</div><div class="pos-chip pc-{p}">{p}</div><div class="rank-name">{name_html}</div></div>')\n    return ''.join(out)'''
if old in t:
    t=t.replace(old,new,1)
t=t.replace('def render_draft_guide():','def render_draft_guide(players=None, profile_href=None):',1)
t=t.replace('st.markdown(_rows(board),unsafe_allow_html=True)','st.markdown(_rows(board,players,profile_href),unsafe_allow_html=True)',1)
old_research="for a,b in NUGGETS:st.markdown(f'<div class=\"guide-card\"><b>{html.escape(a)}</b><p>{html.escape(b)}</p></div>',unsafe_allow_html=True)"
if old_research in t:
    t=t.replace(old_research,'for a,b in NUGGETS:\n            with st.expander(a):\n                st.write(b)',1)
t=t.replace('</style>','''\n.guide-player-link{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;color:#fff!important;text-decoration:none!important}.guide-player-link span{font-size:9px;color:#d8b35b;font-weight:900;white-space:nowrap}.rank-row:has(.guide-player-link){border-color:rgba(216,179,91,.20)}.rank-row:has(.guide-player-link):active{background:#17212a}.guide-card b{font-size:16px}.guide-card p{font-size:14px}\n</style>''',1)
g.write_text(t,encoding='utf-8')
ast.parse(t)

assert 'Draft-Coach' not in s
assert 'render_season_hub' in s
assert 'render_draft_moment' in s
assert 'SHIVA_MARK' in s
assert 'home-insight-grid' in s
assert 'render_draft_guide(players,profile_href)' in s
assert 'guide-player-link' in t
print('COMPLETE SHIVA EXPERIENCE BUILD PASSED')
