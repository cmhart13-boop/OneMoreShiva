"""One More Shiva runtime UI patch.

Keeps page changes inside the existing Streamlit session so mobile navigation does
not trigger a new browser document (and therefore does not flash white).
"""
from __future__ import annotations

import builtins

_ORIGINAL_COMPILE = builtins.compile
_APPROVED_SHIVA_ASSET = "https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/FDBBC710-B60A-4DA4-9582-F52D6210DB18.png"


def _patch_app_core(source: str) -> str:
    # Preserve all existing routes and add Analytics.
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

    # Shiva IQ is the home destination while old Home links remain valid.
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

    source = source.replace(
        'st.markdown("#### Fantasy News")',
        'st.markdown(\'<div class="home-fantasy-news-title">Fantasy News</div>\', unsafe_allow_html=True)',
        1,
    )

    # ROOT NAV FIX: the visible controls are the real Streamlit buttons. There is no
    # href, no window.location, no transparent hit layer, and no display-only nav.
    # Every tap changes only the page query param and reruns inside the same document.
    nav_start = source.find('def bottom_nav(active:str):')
    nav_end = source.find('\ndef screen_head', nav_start) if nav_start >= 0 else -1
    if nav_start >= 0 and nav_end > nav_start:
        native_nav = r'''def bottom_nav(active:str):
    nav_pages=["Shiva","Guide","Draft","Analytics"]

    def _nav_go(dest):
        for k in list(st.query_params.keys()):
            if k != "page":
                del st.query_params[k]
        st.query_params["page"] = dest
        st.rerun()

    active_key=f"nav{active.lower()}"
    st.markdown(
        f'''<style>
        .st-key-{active_key} button{{color:#f4f7f9!important;opacity:1!important}}
        </style>''',
        unsafe_allow_html=True,
    )

    with st.container(key="native_bottom_nav"):
        cols=st.columns(4,gap="small")
        for p,col in zip(nav_pages,cols):
            with col:
                st.button(
                    'Shiva IQ' if p=='Shiva' else p,
                    key=f"nav{p.lower()}",
                    on_click=_nav_go,
                    args=(p,),
                    use_container_width=True,
                )
'''
        source = source[:nav_start] + native_nav + source[nav_end:]

    # Real Analytics destination using the existing verified player data.
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

    compact_css = rf'''
/* FINAL NATIVE MOBILE NAV — NO FULL DOCUMENT NAVIGATION */
:root{{--nav-h:58px!important;background:#071019!important}}
html,body,#root,.stApp,.stAppViewContainer,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],section.main,.main,.block-container{{background:#071019!important;background-color:#071019!important;color-scheme:dark!important}}
html::before,body::before{{background:#071019!important}}
[data-testid="stAppDeployButton"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],.stAppDeployButton,[aria-label="Manage app"],[title="Manage app"],[data-testid*="manage" i],[aria-label*="Manage app" i],[title*="Manage app" i]{{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;width:0!important;height:0!important;overflow:hidden!important}}
.block-container{{padding-top:.12rem!important;padding-left:.58rem!important;padding-right:.58rem!important;padding-bottom:calc(66px + env(safe-area-inset-bottom))!important}}
.app-top{{padding:1px 1px 3px!important}}.brand-badge{{width:30px!important;height:30px!important;font-size:16px!important}}.brand-name,.brand-title{{font-size:17px!important}}.screen-head{{margin:0 0 7px!important}}.screen-head h1{{font-size:20px!important;line-height:1.08!important}}.screen-head p{{font-size:11.5px!important;line-height:1.32!important;margin-top:3px!important}}

/* The real Streamlit buttons ARE the bottom navigation. */
.st-key-native_bottom_nav{{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:100000!important;height:calc(56px + env(safe-area-inset-bottom))!important;margin:0!important;padding:4px 10px calc(4px + env(safe-area-inset-bottom))!important;box-sizing:border-box!important;background:rgba(7,13,19,.96)!important;backdrop-filter:blur(18px)!important;-webkit-backdrop-filter:blur(18px)!important;border-top:1px solid rgba(132,148,160,.18)!important;box-shadow:0 -3px 12px rgba(0,0,0,.22)!important}}
.st-key-native_bottom_nav>div,.st-key-native_bottom_nav [data-testid="stHorizontalBlock"]{{height:100%!important;margin:0!important;gap:0!important}}
.st-key-native_bottom_nav [data-testid="column"]{{height:100%!important;padding:0!important}}
.st-key-native_bottom_nav .stButton{{height:100%!important;margin:0!important}}
.st-key-native_bottom_nav .stButton>button{{width:100%!important;height:44px!important;min-height:44px!important;margin:0!important;padding:1px 0 0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:rgba(191,200,207,.60)!important;opacity:.86!important;font-size:9px!important;font-weight:760!important;line-height:1!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:1px!important}}
.st-key-native_bottom_nav .stButton>button:hover,.st-key-native_bottom_nav .stButton>button:focus,.st-key-native_bottom_nav .stButton>button:active{{background:transparent!important;border:0!important;box-shadow:none!important}}
.st-key-native_bottom_nav .stButton>button p{{margin:0!important;font-size:9px!important;line-height:1!important}}
.st-key-navshiva button::before{{content:"";display:block;width:29px;height:29px;background:url("{_APPROVED_SHIVA_ASSET}") center/contain no-repeat;flex:0 0 29px}}
.st-key-navguide button::before{{content:"▤";display:block;font-size:27px;line-height:27px;height:29px}}
.st-key-navdraft button::before{{content:"◫";display:block;font-size:27px;line-height:27px;height:29px}}
.st-key-navanalytics button::before{{content:"▥";display:block;font-size:27px;line-height:27px;height:29px}}

.st-key-home_shiva_card{{margin:1px 0 8px!important;padding:10px 10px 9px!important;border-radius:9px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 4px 12px rgba(0,0,0,.16)!important}}.st-key-home_shiva_card .home-shiva-hero{{min-height:108px!important;margin:0 0 8px!important;padding:0 0 9px!important}}.st-key-home_shiva_card .home-shiva-kicker{{font-size:9px!important;letter-spacing:.65px!important}}.st-key-home_shiva_card .home-shiva-title{{font-size:21px!important;line-height:1.04!important;letter-spacing:-.45px!important;margin:4px 0 5px!important;max-width:76%!important}}.st-key-home_shiva_card .home-shiva-copy{{font-size:11.5px!important;line-height:1.34!important;max-width:78%!important}}.home-shiva-brain{{width:86px!important;height:86px!important;right:-1px!important;top:1px!important;opacity:.60!important}}.st-key-home_shiva_card .home-ask-label{{font-size:11px!important;margin:0 0 4px!important}}.st-key-home_shiva_card .stTextArea textarea{{min-height:68px!important;height:68px!important;border-radius:7px!important;font-size:12px!important;line-height:1.35!important;padding:8px 9px!important}}.st-key-home_shiva_go .stButton>button{{min-height:40px!important;height:40px!important;border-radius:7px!important;font-size:12px!important}}
.stat-strip{{gap:5px!important;margin:6px 0 8px!important}}.mini-stat{{min-height:82px!important;padding:8px 5px!important;border-radius:7px!important}}.mini-stat b{{font-size:23px!important}}.mini-stat span{{font-size:9.5px!important;line-height:1.2!important;margin-top:6px!important}}.quick-grid{{gap:6px!important;margin:6px 0 8px!important}}.quick-card{{min-height:72px!important;padding:9px!important;border-radius:7px!important}}.quick-icon{{font-size:18.7px!important}}.quick-title{{font-size:13px!important;margin-top:2px!important}}.quick-sub{{font-size:10px!important;line-height:1.25!important;margin-top:2px!important}}.home-fantasy-news-title{{font-size:17px!important;font-weight:900!important;line-height:1.2!important;letter-spacing:-.3px!important;color:#f4f7f9!important;margin:13px 0 7px!important}}.hero-card,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell{{border-radius:7px!important}}.stButton>button,.stDownloadButton>button{{min-height:40px!important;font-size:12px!important}}
@media(max-width:430px){{.main .block-container{{padding-left:10px!important;padding-right:10px!important;padding-top:1px!important}}.screen-head h1{{font-size:20px!important}}.st-key-home_shiva_card .home-shiva-title{{font-size:20px!important}}.st-key-home_shiva_card .home-shiva-copy{{font-size:11px!important}}.home-shiva-brain{{width:82px!important;height:82px!important}}}}
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
