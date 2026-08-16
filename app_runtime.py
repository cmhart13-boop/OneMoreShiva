"""One More Shiva production entrypoint.

This runtime patches the legacy app_core without changing fantasy data/calculations.
Critical mobile invariant: the SHIVA header is the first Streamlit layout element.
No style-only markdown, empty placeholder, or component iframe may render before it.
"""
from pathlib import Path
import base64
import io
import re

from PIL import Image
import streamlit as st
import shiva_home_v2 as _home_v2

core = Path(__file__).with_name("app_core.py")
code = core.read_text(encoding="utf-8")

# -----------------------------------------------------------------------------
# ZERO-GUTTER SHELL
# -----------------------------------------------------------------------------
_start = code.find("# Startup splash: initial app launch only.")
_end = code.find("SHIVA_MARK =", _start)
if _start >= 0 and _end > _start:
    code = code[:_start] + code[_end:]

code = code.replace("st.markdown(CSS, unsafe_allow_html=True)\ninject_coach_css()\n", "")

_badge_start = code.find("# Streamlit Community Cloud hosted-badge suppressor.")
_badge_end = code.find("\n\n\ndef stable_id", _badge_start)
if _badge_start >= 0 and _badge_end > _badge_start:
    code = code[:_badge_start] + code[_badge_end:]

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
code = code.replace(_old_bottom_nav, _new_bottom_nav)

# -----------------------------------------------------------------------------
# DRAFT START UX
# -----------------------------------------------------------------------------
code = code.replace(
    'defaults={"draft_log":[],"queue":[],"user_slot":3,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[]}',
    'defaults={"draft_log":[],"queue":[],"user_slot":1,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[],"draft_started":False}'
)
old_draft_start = '''    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
'''
new_draft_start = '''    slot_options=list(range(1,st.session_state.team_count+1))
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
code = code.replace(old_draft_start, new_draft_start)
code = code.replace(
    'if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()',
    'if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["draft_started"]=False;st.rerun()'
)

# -----------------------------------------------------------------------------
# TROPHY ASSETS
# -----------------------------------------------------------------------------
_trophy_match = re.search(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', code)
if _trophy_match:
    try:
        _raw = base64.b64decode(_trophy_match.group(1))
        _img = Image.open(io.BytesIO(_raw)).convert("RGBA")
        _pixels = _img.load()
        _w, _h = _img.size
        corners = [_pixels[0, 0][:3], _pixels[_w - 1, 0][:3], _pixels[0, _h - 1][:3], _pixels[_w - 1, _h - 1][:3]]
        bg = tuple(sum(c[i] for c in corners) / len(corners) for i in range(3))
        for y in range(_h):
            for x in range(_w):
                r, g, b, _a = _pixels[x, y]
                dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
                alpha = 0 if dist <= 22 else int(255 * (dist - 22) / 36) if dist < 58 else 255
                _pixels[x, y] = (r, g, b, alpha)
        bbox = _img.getbbox()
        if bbox:
            _img = _img.crop(bbox)
        _out = io.BytesIO()
        _img.save(_out, format="PNG", optimize=True)
        _png_b64 = base64.b64encode(_out.getvalue()).decode("ascii")
        code = code.replace(
            f'data:image/jpeg;base64,{_trophy_match.group(1)}',
            f'data:image/png;base64,{_png_b64}'
        )
    except Exception:
        pass

_splash_asset_uri = ""
_splash_source_width = 0
_splash_source_height = 0
_splash_asset_path = Path(__file__).with_name("FDBBC710-B60A-4DA4-9582-F52D6210DB18.png")
try:
    _splash_img = Image.open(_splash_asset_path).convert("RGBA")
    _splash_source_width, _splash_source_height = _splash_img.size
    _alpha_extrema = _splash_img.getchannel("A").getextrema()
    if _alpha_extrema == (255, 255):
        _sp = _splash_img.load()
        _sw, _sh = _splash_img.size
        _corners = [_sp[0, 0][:3], _sp[_sw - 1, 0][:3], _sp[0, _sh - 1][:3], _sp[_sw - 1, _sh - 1][:3]]
        _bg = tuple(sum(c[i] for c in _corners) / len(_corners) for i in range(3))
        for _y in range(_sh):
            for _x in range(_sw):
                _r, _g, _b, _a = _sp[_x, _y]
                _dist = ((_r - _bg[0]) ** 2 + (_g - _bg[1]) ** 2 + (_b - _bg[2]) ** 2) ** 0.5
                if _dist <= 16:
                    _new_a = 0
                elif _dist < 42:
                    _new_a = int(255 * (_dist - 16) / 26)
                else:
                    _new_a = 255
                _sp[_x, _y] = (_r, _g, _b, _new_a)
    _bbox = _splash_img.getbbox()
    if _bbox:
        _splash_img = _splash_img.crop(_bbox)
    _splash_source_width, _splash_source_height = _splash_img.size
    if _splash_source_width >= 675:
        _splash_out = io.BytesIO()
        _splash_img.save(_splash_out, format="PNG", optimize=True)
        _splash_asset_uri = "data:image/png;base64," + base64.b64encode(_splash_out.getvalue()).decode("ascii")
except Exception:
    _splash_asset_uri = ""

# -----------------------------------------------------------------------------
# SINGLE FIRST PAINT: CSS + optional splash + header in ONE Streamlit element.
# IMPORTANT: HTML quotes below are intentionally NOT backslash-escaped. Safari must
# receive a real <style> element, never literal CSS text.
# -----------------------------------------------------------------------------
readability_patch = r'''<style id="shiva-shell-contract">
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{background-color:#071019!important;color-scheme:dark!important}
*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}
button,a,label,input,select,textarea,[role="button"],[role="tab"],[role="radio"],[role="option"]{-webkit-tap-highlight-color:transparent!important}
#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],[data-testid="stDeployButton"],.stAppDeployButton,button[title="Manage app"],a[aria-label="Manage app"]{display:none!important;visibility:hidden!important;height:0!important;min-height:0!important}
[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}
[data-testid="stMainBlockContainer"],.main .block-container,section.main>div.block-container,.block-container{padding-top:0!important;margin-top:0!important}
.screen-head h1{font-size:34px!important;line-height:1.08!important}.screen-head p{font-size:17px!important;line-height:1.45!important;color:#aebbc4!important}
.brand-sub{font-size:15px!important}.stButton>button{font-size:16px!important}.stSelectbox label,.stTextInput label,.stTextArea label{font-size:16px!important}
div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:14px!important}
.hero-kicker,.section-kicker,.eyebrow,.card-kicker{font-size:14px!important}.hero-title,.section-title{font-size:28px!important}.hero-copy,.section-copy,.card-copy{font-size:16px!important;line-height:1.5!important}
.draft-status span,.draft-chip span{font-size:13px!important}.draft-status b,.draft-chip b{font-size:22px!important}.on-clock{font-size:18px!important}
.player-name{font-size:17px!important}.player-meta,.data-cell span,.board-meta,.board-pick,.slot-meta{font-size:13px!important}.data-cell b,.slot-player{font-size:16px!important}
.draft-start-intro{background:linear-gradient(145deg,#14212d,#0d171f);border:1px solid #2b4151;border-radius:16px;padding:18px;margin:8px 0 14px}.draft-start-intro b{display:block;font-size:27px;color:#fff;margin-bottom:6px}.draft-start-intro span{display:block;font-size:16px;line-height:1.45;color:#b9c5cd}
.brand-badge,.brand-badge .shiva-trophy-mark{background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important}.brand-badge .shiva-trophy-mark{mix-blend-mode:normal!important}
.st-key-primary_nav_Home .stButton>button::before{mix-blend-mode:normal!important}.stCaptionContainer,[data-testid="stCaptionContainer"]{font-size:14px!important}
.shiva-startup-splash{position:fixed;inset:0;width:100vw;height:100dvh;z-index:2147483647;background:#071019;display:flex;align-items:center;justify-content:center;pointer-events:none;animation:shivaSplashGone 0s linear 2.5s forwards}
.shiva-startup-splash .shiva-splash-trophy{display:block;width:min(52vw,225px)!important;height:auto!important;max-height:52vh!important;object-fit:contain!important;object-position:center!important;animation:none!important;transform:none!important;transition:none!important;filter:none!important;image-rendering:auto!important;backface-visibility:hidden!important}
@keyframes shivaSplashGone{to{opacity:0;visibility:hidden}}
@media(max-width:520px){.screen-head h1{font-size:31px!important}.screen-head p{font-size:16px!important}.stButton>button{font-size:16px!important}.player-name{font-size:17px!important}.draft-start-intro b{font-size:25px!important}}
</style>'''.replace('\\"', '"')

_old_header = '''def app_header():
    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">{SHIVA_MARK}</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div></div>',unsafe_allow_html=True)
'''
_new_header = f'''def app_header():
    _show_splash = not st.query_params.get("page") and not st.session_state.get("_shiva_startup_splash_seen", False)
    if _show_splash:
        st.session_state["_shiva_startup_splash_seen"] = True
    _splash = ''
    if _show_splash and _splash_asset_uri:
        _splash = f'<div class="shiva-startup-splash"><img class="shiva-splash-trophy" src="{{_splash_asset_uri}}" alt="The Shiva trophy" decoding="sync" fetchpriority="high"></div>'
    st.markdown(CSS + {readability_patch!r} + _splash + f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">{{SHIVA_MARK}}</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div></div>', unsafe_allow_html=True)
'''
code = code.replace(_old_header, _new_header)

code = code.replace(
    'def season_coach():\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")',
    'def season_coach():\n    inject_coach_css()\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")'
)

exec(compile(code, str(core), "exec"), globals(), globals())
