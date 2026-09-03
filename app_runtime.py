"""One More Shiva production runtime.

This module preserves the established app_core behavior while applying the production
shell/navigation contracts in one deterministic transformation pipeline.

Critical invariants:
- app.py is the only owner of st.set_page_config.
- No Streamlit layout element renders before app_header.
- Every source transformation must match exactly once; silent partial patches are forbidden.
- The splash uses the same approved SHIVA_MARK trophy as the normal app header.
- The original app_core typography remains authoritative.
- The first paint uses st.html, never Markdown, for CSS + splash + header.
"""
from pathlib import Path
import base64
import html
import io
import re
from datetime import datetime

from PIL import Image
import streamlit as st
import shiva_home_v2 as _home_v2


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    """Replace one required source contract or fail loudly before rendering."""
    matches = source.count(old)
    if matches != 1:
        raise RuntimeError(f"Shiva runtime contract {label!r} expected 1 match, found {matches}")
    return source.replace(old, new, 1)


def _remove_between_once(source: str, start_marker: str, end_marker: str, label: str) -> str:
    """Remove one required source block delimited by stable markers."""
    start = source.find(start_marker)
    if start < 0:
        raise RuntimeError(f"Shiva runtime contract {label!r} missing start marker")
    end = source.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f"Shiva runtime contract {label!r} missing end marker")
    if source.find(start_marker, start + len(start_marker)) >= 0:
        raise RuntimeError(f"Shiva runtime contract {label!r} has duplicate start markers")
    return source[:start] + source[end:]


core = Path(__file__).with_name("app_core.py")
code = core.read_text(encoding="utf-8")

# -----------------------------------------------------------------------------
# SINGLE OWNER FOR PAGE CONFIG
# -----------------------------------------------------------------------------
code = _replace_once(
    code,
    'st.set_page_config(page_title="One More Shiva", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")',
    "",
    "page-config",
)

# -----------------------------------------------------------------------------
# ZERO-GUTTER SHELL
# -----------------------------------------------------------------------------
# Remove the legacy Python-timed splash because st.empty() occupies a Streamlit layout
# slot before the real header, even after it is emptied.
code = _remove_between_once(
    code,
    "# Startup splash: initial app launch only.",
    "SHIVA_MARK =",
    "legacy-startup-splash",
)

# CSS and Coach CSS historically rendered as separate Streamlit elements before the
# header. Production CSS is now part of app_header; Coach CSS is scoped to Coach.
code = _replace_once(
    code,
    "st.markdown(CSS, unsafe_allow_html=True)\ninject_coach_css()\n",
    "",
    "preheader-css-render",
)

# Remove the hosted-badge zero-height component iframe from the pre-header stack.
code = _remove_between_once(
    code,
    "# Streamlit Community Cloud hosted-badge suppressor.",
    "\n\n\ndef stable_id",
    "hosted-badge-component",
)

# -----------------------------------------------------------------------------
# SMOOTH NAVIGATION
# -----------------------------------------------------------------------------
def _smooth_home_go(page: str) -> None:
    st.query_params["page"] = page
    for key in ("player", "hint", "ret", "draft", "edge_mode", "edge_pos"):
        try:
            del st.query_params[key]
        except Exception:
            pass


_home_v2.go = _smooth_home_go

_old_bottom_nav = '''def bottom_nav(active:str):
    active = "Home" if active == "Shiva" else active
    labels=[("Home",""),("Draft","◫"),("Guide","▤"),("Coach","✦")]
    with st.container(key="bottom_nav_shell"):
        cols=st.columns(4,gap="small")
        for i,(page_name,icon) in enumerate(labels):
            with cols[i]:
                if st.button(f"{icon}  {page_name}",key=f"primary_nav_{page_name}",type="primary" if active==page_name else "secondary",use_container_width=True):
                    st.query_params["page"]=page_name
                    for k in ("player","hint","ret","draft"):
                        try: del st.query_params[k]
                        except Exception: pass
                    st.rerun()
'''
_new_bottom_nav = '''def _nav_to(page_name:str):
    st.query_params["page"]=page_name
    for k in ("player","hint","ret","draft","edge_mode","edge_pos"):
        try: del st.query_params[k]
        except Exception: pass

def bottom_nav(active:str):
    active = "Home" if active == "Shiva" else active
    labels=[("Home",""),("Draft","◫"),("Guide","▤"),("Coach","✦")]
    with st.container(key="bottom_nav_shell"):
        cols=st.columns(4,gap="small")
        for i,(page_name,icon) in enumerate(labels):
            with cols[i]:
                st.button(
                    f"{icon}  {page_name}",
                    key=f"primary_nav_{page_name}",
                    type="primary" if active==page_name else "secondary",
                    use_container_width=True,
                    on_click=_nav_to,
                    args=(page_name,),
                )
'''
code = _replace_once(code, _old_bottom_nav, _new_bottom_nav, "bottom-navigation")

# -----------------------------------------------------------------------------
# DRAFT START UX — preserve approved behavior exactly
# -----------------------------------------------------------------------------
code = _replace_once(
    code,
    'defaults={"draft_log":[],"queue":[],"user_slot":3,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[]}',
    'defaults={"draft_log":[],"queue":[],"user_slot":1,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[],"draft_started":False}',
    "draft-defaults",
)

_old_draft_start = '''    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
'''
_new_draft_start = '''    slot_options=list(range(1,st.session_state.team_count+1))
    if not st.session_state.get("draft_started",False):
        st.markdown('<div class="draft-start-intro"><b>Start a Mock Draft</b><span>Choose where you draft, then start the room. Nothing goes on the clock until you say so.</span></div>',unsafe_allow_html=True)
        selected_slot=st.selectbox("Choose your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
        if selected_slot!=st.session_state.user_slot:
            st.session_state.user_slot=selected_slot
        if st.button("Start Mock Draft",type="primary",use_container_width=True,key="start_mock_draft"):
            st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["draft_started"]=True;sim_to_user();st.rerun()
        return
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
'''
code = _replace_once(code, _old_draft_start, _new_draft_start, "draft-start-screen")
code = _replace_once(
    code,
    'if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()',
    'if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["draft_started"]=False;st.rerun()',
    "draft-reset",
)

# -----------------------------------------------------------------------------
# CANONICAL SHIVA LOGO — repo asset is the single source of truth
# -----------------------------------------------------------------------------
SHIVA_LOGO_RELATIVE_PATH = "static/shiva-trophy.png"
SHIVA_LOGO_FILE = Path(__file__).parent / SHIVA_LOGO_RELATIVE_PATH
if not SHIVA_LOGO_FILE.exists():
    raise RuntimeError("Canonical Shiva logo asset is missing")
_shiva_logo_b64 = base64.b64encode(SHIVA_LOGO_FILE.read_bytes()).decode("ascii")
SHIVA_MARK_NEW = f'<img class="shiva-trophy-mark" src="data:image/png;base64,{_shiva_logo_b64}" alt="THE SHIVA trophy">'

# Replace the legacy embedded trophy assignment in app_core with the canonical repo asset.
_trophy_pattern = re.compile(r'SHIVA_MARK\s*=\s*f?"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,([A-Za-z0-9+/=]+)" alt="THE SHIVA trophy">"""')
_trophy_matches = list(_trophy_pattern.finditer(code))
if len(_trophy_matches) != 1:
    raise RuntimeError(f"Shiva trophy contract expected 1 legacy SHIVA_MARK, found {len(_trophy_matches)}")
_trophy_match = _trophy_matches[0]
_trophy_assignment = 'SHIVA_MARK = ' + repr(SHIVA_MARK_NEW)
code = code[:_trophy_match.start()] + _trophy_assignment + code[_trophy_match.end():]

# -----------------------------------------------------------------------------
# APPLICATION SHELL — the ASGI launch shell in app.py is the sole splash owner.
# -----------------------------------------------------------------------------
SHELL_STYLE = '''<style id="shiva-shell-contract">
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{background-color:#071019!important;color-scheme:dark!important}
*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}
button,a,label,input,select,textarea,[role="button"],[role="tab"],[role="radio"],[role="option"]{-webkit-tap-highlight-color:transparent!important}
#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],[data-testid="stDeployButton"],[data-testid="stAppDeployButton"],[data-testid="stViewerBadge"],[data-testid="stAppCreatorAvatar"],.stAppDeployButton,[class*="viewerBadge"],[class*="ViewerBadge"],[class*="stDeployButton"],button[title="Manage app"],button[aria-label="Manage app"],a[aria-label="Manage app"],a[href*="streamlit.io/cloud"],a[href*="share.streamlit.io"]{display:none!important;visibility:hidden!important;height:0!important;min-height:0!important}
[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}
[data-testid="stMainBlockContainer"],.main .block-container,section.main>div.block-container,.block-container{padding-top:0!important;margin-top:0!important}
.screen-head h1{font-size:34px!important;line-height:1.08!important}.screen-head p{font-size:17px!important;line-height:1.45!important;color:#aebbc4!important}
.brand-title{text-transform:none!important}.brand-sub{font-size:15px!important}.stButton>button{font-size:16px!important}.stSelectbox label,.stTextInput label,.stTextArea label{font-size:16px!important}
div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:14px!important}
.hero-kicker,.section-kicker,.eyebrow,.card-kicker{font-size:14px!important}.hero-title,.section-title{font-size:28px!important}.hero-copy,.section-copy,.card-copy{font-size:16px!important;line-height:1.5!important}
.draft-status span,.draft-chip span{font-size:13px!important}.draft-status b,.draft-chip b{font-size:22px!important}.on-clock{font-size:18px!important}
.player-name{font-size:17px!important}.player-meta,.data-cell span,.board-meta,.board-pick,.slot-meta{font-size:13px!important}.data-cell b,.slot-player{font-size:16px!important}
.draft-start-intro{background:linear-gradient(145deg,#14212d,#0d171f);border:1px solid #2b4151;border-radius:16px;padding:18px;margin:8px 0 14px}.draft-start-intro b{display:block;font-size:27px;color:#fff;margin-bottom:6px}.draft-start-intro span{display:block;font-size:16px;line-height:1.45;color:#b9c5cd}
.brand-badge,.brand-badge .shiva-trophy-mark{background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important}.brand-badge .shiva-trophy-mark{mix-blend-mode:screen!important}
.app-top{position:relative!important;display:block!important;padding-bottom:4px!important;border-bottom:1px solid rgba(38,52,64,.42)!important}.app-top .brand-wrap{width:100%!important;min-width:0!important}.brand-copy{min-width:0}.kickoff-compact{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:54px;margin:4px 0 0;padding:9px 12px;border:1px solid rgba(213,177,92,.32);border-radius:12px;background:linear-gradient(145deg,rgba(213,177,92,.12),rgba(213,177,92,.04));white-space:nowrap}.kickoff-compact span{font-size:11px;line-height:1;font-weight:950;letter-spacing:1px;color:#d5b15c;text-transform:uppercase}.kickoff-compact b{font-size:22px;line-height:1;font-weight:950;letter-spacing:.4px;color:#f7f7f5}
.st-key-primary_nav_Home .stButton>button::before{background-color:transparent!important;border:0!important;box-shadow:none!important;mix-blend-mode:screen!important}.stCaptionContainer,[data-testid="stCaptionContainer"]{font-size:14px!important}
@media(max-width:520px){.screen-head h1{font-size:31px!important}.screen-head p{font-size:16px!important}.stButton>button{font-size:16px!important}.player-name{font-size:17px!important}.draft-start-intro b{font-size:25px!important}.brand-wrap{gap:8px!important}.brand-badge{width:48px!important;height:48px!important;flex:0 0 48px!important}.brand-title{font-size:25px!important}.brand-sub{font-size:10.5px!important;letter-spacing:.45px!important;white-space:nowrap}.kickoff-compact{min-height:50px;padding:8px 9px;gap:7px}.kickoff-compact span{font-size:10px}.kickoff-compact b{font-size:18px}}
</style>'''

if not SHELL_STYLE.startswith('<style id="shiva-shell-contract">') or not SHELL_STYLE.endswith("</style>"):
    raise RuntimeError("Invalid Shiva shell style markup")
if '\\"' in SHELL_STYLE:
    raise RuntimeError("Escaped HTML quotes detected in Shiva shell style")

_old_header = '''def app_header():
    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">{SHIVA_MARK}</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div></div>',unsafe_allow_html=True)
'''


def _compact_kickoff_markup() -> str:
    target = datetime.fromisoformat(_home_v2.KICKOFF_ISO)
    remaining = max(0, int((target - datetime.now(target.tzinfo)).total_seconds()))
    if remaining == 0:
        value = "LIVE"
    else:
        days, remaining = divmod(remaining, 86_400)
        hours, remaining = divmod(remaining, 3_600)
        minutes, seconds = divmod(remaining, 60)
        value = f"{days:02d} DAYS · {hours:02d}:{minutes:02d}:{seconds:02d}"
    return f'<div class="kickoff-compact" data-shiva-kickoff data-target="{html.escape(_home_v2.KICKOFF_ISO, quote=True)}"><span>NFL KICKOFF</span><b>{value}</b></div>'


_new_header = f'''def app_header():
    _is_home = str(st.query_params.get("page") or "Home") in ("Home", "Shiva")
    _kickoff = _compact_kickoff_markup() if _is_home else ''
    _html = CSS + {SHELL_STYLE!r} + f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">{{SHIVA_MARK}}</div><div class="brand-copy"><div class="brand-title">Shiva</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div>{{_kickoff}}</div>'
    st.html(_html)
'''
code = _replace_once(code, _old_header, _new_header, "app-header")

# Coach CSS is intentionally scoped to Coach instead of creating a global pre-header
# layout element.
code = _replace_once(
    code,
    'def season_coach():\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")',
    'def season_coach():\n    inject_coach_css()\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")',
    "coach-css-scope",
)

# Final safety checks before executing any transformed application code.
if "st.set_page_config(" in code:
    raise RuntimeError("Duplicate Streamlit page config survived runtime transformation")
if "_splash_slot = st.empty()" in code:
    raise RuntimeError("Legacy splash layout slot survived runtime transformation")
if "components.html(" in code and "hosted-badge suppressor" in code:
    raise RuntimeError("Hosted badge component survived runtime transformation")

exec(compile(code, str(core), "exec"), globals(), globals())
