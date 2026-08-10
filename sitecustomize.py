"""One More Shiva runtime UI patch.

Loaded automatically by Python. It only intercepts compilation of app_core.py so the
production app can receive a final, last-in-order mobile UI patch without touching
fantasy data, draft logic, or historical calculations.
"""
from __future__ import annotations

import builtins

_ORIGINAL_COMPILE = builtins.compile


def _patch_app_core(source: str) -> str:
    # Preserve hidden legacy routes for existing in-app links, but add Analytics.
    source = source.replace(
        'PAGES = ["Home","Draft","Guide","Players","Shiva","Roster"]',
        'PAGES = ["Home","Draft","Guide","Players","Shiva","Roster","Analytics"]',
        1,
    )
    source = source.replace(
        'ICONS = {"Home":"⌂","Draft":"🏈","Guide":"📖","Players":"👥","Shiva":"🧠","Roster":"☷"}',
        'ICONS = {"Home":"⌂","Draft":"◫","Guide":"▤","Players":"👥","Shiva":"","Roster":"☷","Analytics":"▥"}',
        1,
    )

    # Bottom nav is intentionally only the four approved primary destinations.
    source = source.replace(
        '    for p in PAGES:\n',
        '    for p in ["Shiva","Guide","Draft","Analytics"]:\n',
        1,
    )

    # Shiva IQ is the home destination. Keep the old Home route valid for old links.
    source = source.replace(
        'page=str(qp.get("page") or "Home");page=page if page in PAGES else "Home"',
        'page=str(qp.get("page") or "Shiva");page=page if page in PAGES else "Shiva"',
        1,
    )
    source = source.replace(
        '{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":shiva,"Roster":roster_screen}[page]();bottom_nav(page)',
        '{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics}[page]();bottom_nav(page)',
        1,
    )

    # Real Analytics destination, reusing the verified player database and profiles.
    analytics_anchor = '\ndef shiva():\n'
    if analytics_anchor in source and '\ndef analytics():\n' not in source:
        analytics_func = r'''
def analytics():
    screen_head("Analytics","Player database and historical Full-PPR analysis.")
    q=st.text_input("Search analytics",placeholder="Search player or NFL team…",key="analytics_search")
    pos=st.selectbox("Position filter",["ALL","RB","WR","QB","TE","DST","K"],key="analytics_pos")
    df=players.copy()
    if q:
        q=q.casefold().strip()
        df=df.loc[df["name"].str.casefold().str.contains(q,regex=False)|df["team"].str.casefold().str.contains(q,regex=False)]
    if pos!="ALL":df=df.loc[df["pos"].eq(pos)]
    render_players(df,"Analytics","none",150)
'''
        source = source.replace(analytics_anchor, '\n' + analytics_func + '\ndef shiva():\n', 1)

    # This CSS is inserted at compile time, after app.py's other styling passes,
    # making it the final authority for mobile scale and bottom navigation.
    compact_css = r'''
/* FINAL COMPACT ESPN-LIKE MOBILE SHELL */
:root{--nav-h:58px!important}
.block-container{padding-top:.22rem!important;padding-left:.58rem!important;padding-right:.58rem!important;padding-bottom:calc(66px + env(safe-area-inset-bottom))!important}
.app-top{padding:2px 1px 5px!important}.brand-badge{width:30px!important;height:30px!important;font-size:16px!important}.brand-name,.brand-title{font-size:17px!important}.screen-head{margin:0 0 7px!important}.screen-head h1{font-size:20px!important;line-height:1.08!important}.screen-head p{font-size:11.5px!important;line-height:1.32!important;margin-top:3px!important}
.bottom-nav{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:99999!important;display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;box-sizing:border-box!important;height:calc(56px + env(safe-area-inset-bottom))!important;padding:4px 10px calc(4px + env(safe-area-inset-bottom))!important;background:rgba(7,13,19,.96)!important;backdrop-filter:blur(18px)!important;-webkit-backdrop-filter:blur(18px)!important;border-top:1px solid rgba(132,148,160,.18)!important;box-shadow:0 -3px 12px rgba(0,0,0,.22)!important}
.bottom-nav a{min-width:0!important;min-height:44px!important;height:44px!important;margin:0!important;padding:2px 0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:rgba(191,200,207,.56)!important;opacity:.82!important;font-size:9px!important;font-weight:760!important;line-height:1!important;letter-spacing:0!important;gap:3px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important}
.bottom-nav a.active{background:transparent!important;box-shadow:none!important;color:#f4f7f9!important;opacity:1!important}.bottom-nav .nav-icon{font-size:17px!important;line-height:17px!important;height:18px!important;display:flex!important;align-items:center!important;justify-content:center!important;color:inherit!important;filter:none!important}.bottom-nav .shiva-iq-mark{width:19px!important;height:19px!important;filter:grayscale(1)!important;opacity:.62!important}.bottom-nav a.active .shiva-iq-mark{filter:grayscale(.15)!important;opacity:.96!important}
.st-key-home_shiva_card{margin:1px 0 8px!important;padding:10px 10px 9px!important;border-radius:9px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 4px 12px rgba(0,0,0,.16)!important}.st-key-home_shiva_card .home-shiva-hero{min-height:108px!important;margin:0 0 8px!important;padding:0 0 9px!important}.st-key-home_shiva_card .home-shiva-kicker{font-size:9px!important;letter-spacing:.65px!important}.st-key-home_shiva_card .home-shiva-title{font-size:21px!important;line-height:1.04!important;letter-spacing:-.45px!important;margin:4px 0 5px!important;max-width:76%!important}.st-key-home_shiva_card .home-shiva-copy{font-size:11.5px!important;line-height:1.34!important;max-width:78%!important}.home-shiva-brain{width:86px!important;height:86px!important;right:-1px!important;top:1px!important;opacity:.60!important}.st-key-home_shiva_card .home-ask-label{font-size:11px!important;margin:0 0 4px!important}.st-key-home_shiva_card .stTextArea textarea{min-height:68px!important;height:68px!important;border-radius:7px!important;font-size:12px!important;line-height:1.35!important;padding:8px 9px!important}.st-key-home_shiva_go .stButton>button{min-height:40px!important;height:40px!important;border-radius:7px!important;font-size:12px!important}
.stat-strip{gap:5px!important;margin:6px 0 8px!important}.mini-stat{min-height:82px!important;padding:8px 5px!important;border-radius:7px!important}.mini-stat b{font-size:23px!important}.mini-stat span{font-size:9.5px!important;line-height:1.2!important;margin-top:6px!important}.quick-grid{gap:6px!important;margin:6px 0 8px!important}.quick-card{min-height:72px!important;padding:9px!important;border-radius:7px!important}.quick-icon{font-size:17px!important}.quick-title{font-size:13px!important;margin-top:2px!important}.quick-sub{font-size:10px!important;line-height:1.25!important;margin-top:2px!important}.hero-card,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell{border-radius:7px!important}.stButton>button,.stDownloadButton>button{min-height:40px!important;font-size:12px!important}
@media(max-width:430px){.main .block-container{padding-left:10px!important;padding-right:10px!important;padding-top:3px!important}.screen-head h1{font-size:20px!important}.st-key-home_shiva_card .home-shiva-title{font-size:20px!important}.st-key-home_shiva_card .home-shiva-copy{font-size:11px!important}.home-shiva-brain{width:82px!important;height:82px!important}}
'''
    css_anchor = "\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)"
    if css_anchor in source:
        source = source.replace(css_anchor, "\n" + compact_css + css_anchor, 1)
    return source


def _compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
    if isinstance(source, str) and str(filename).endswith('app_core.py'):
        source = _patch_app_core(source)
    return _ORIGINAL_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)


builtins.compile = _compile
