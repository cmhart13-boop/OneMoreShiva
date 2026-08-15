"""One More Shiva production entrypoint.

One execution path: app.py -> app_core.py.
Small production-safe patches below enforce the approved readability and draft-start UX
without changing fantasy logic or data behavior.
"""
from pathlib import Path
import base64
import io
import re

from PIL import Image

core = Path(__file__).with_name("app_core.py")
code = core.read_text(encoding="utf-8")

# Draft room must not silently begin at the historical default slot. The user chooses a slot,
# then explicitly starts the mock draft. Existing snake simulation logic remains unchanged.
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

# Convert the embedded Shiva trophy JPEG to a true transparent PNG at runtime.
# This removes the baked-in black square everywhere the trophy is used: header + bottom Shiva IQ icon.
_trophy_match = re.search(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', code)
_trophy_data_uri = None
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
                r, g, b, a = _pixels[x, y]
                dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
                if dist <= 22:
                    alpha = 0
                elif dist < 58:
                    alpha = int(255 * (dist - 22) / 36)
                else:
                    alpha = 255
                _pixels[x, y] = (r, g, b, alpha)
        bbox = _img.getbbox()
        if bbox:
            _img = _img.crop(bbox)
        _out = io.BytesIO()
        _img.save(_out, format="PNG", optimize=True)
        _png_b64 = base64.b64encode(_out.getvalue()).decode("ascii")
        _old_uri = f'data:image/jpeg;base64,{_trophy_match.group(1)}'
        _trophy_data_uri = f'data:image/png;base64,{_png_b64}'
        code = code.replace(_old_uri, _trophy_data_uri)
    except Exception:
        _trophy_data_uri = None

# Replace the old championship-belt photo splash with a clean, stable trophy splash.
if _trophy_data_uri:
    _old_splash_html = '''        _splash_path = Path(__file__).with_name("1FB42328-2FEA-43AE-9BAC-D6BE96E58C93.jpeg")
        _splash_b64 = _splash_b64mod.b64encode(_splash_path.read_bytes()).decode("ascii")
        _splash_slot = st.empty()
        _splash_html = f"<style>.shiva-startup-splash{{position:fixed;inset:0;width:100vw;height:100dvh;z-index:2147483647;background:#081016;display:flex;align-items:center;justify-content:center;overflow:hidden}}.shiva-startup-splash img{{display:block;width:100%;height:100%;object-fit:cover;object-position:center center}}</style><div class='shiva-startup-splash'><img src='data:image/jpeg;base64,{_splash_b64}' alt='Shiva'></div>"
        _splash_slot.markdown(_splash_html, unsafe_allow_html=True)
        _splash_time.sleep(1.15)
        _splash_slot.empty()
'''
    _new_splash_html = f'''        _splash_slot = st.empty()
        _splash_html = """<style>
        html,body,#root,[data-testid=\"stApp\"],[data-testid=\"stAppViewContainer\"],.stApp{{background:#071019!important;color-scheme:dark!important}}
        .shiva-startup-splash{{position:fixed;inset:0;width:100vw;height:100dvh;z-index:2147483647;background:#071019;display:flex;align-items:center;justify-content:center;overflow:hidden;pointer-events:none}}
        .shiva-startup-splash img{{display:block;width:min(34vw,150px);height:auto;object-fit:contain;opacity:1;transform:none!important;animation:none!important;transition:none!important;filter:drop-shadow(0 10px 28px rgba(0,0,0,.42));will-change:auto}}
        </style><div class='shiva-startup-splash'><img src='{_trophy_data_uri}' alt='The Shiva trophy'></div>"""
        _splash_slot.markdown(_splash_html, unsafe_allow_html=True)
        _splash_time.sleep(2.50)
        _splash_slot.empty()
'''
    code = code.replace(_old_splash_html, _new_splash_html)

# Global readability floor + Streamlit chrome cleanup. This intentionally changes presentation,
# not fantasy calculations, datasets, navigation destinations, or feature logic.
readability_patch = r'''<style>
/* Approved readability audit */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stStatusWidget"],
[data-testid="stDecoration"], [data-testid="stDeployButton"], .stAppDeployButton,
button[title="Manage app"], a[aria-label="Manage app"] {display:none!important;visibility:hidden!important}
.screen-head h1{font-size:34px!important;line-height:1.08!important}.screen-head p{font-size:17px!important;line-height:1.45!important;color:#aebbc4!important}
.brand-sub{font-size:15px!important}.stButton>button{font-size:16px!important}.stSelectbox label,.stTextInput label,.stTextArea label{font-size:16px!important}
div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:14px!important}
.hero-kicker,.section-kicker,.eyebrow,.card-kicker{font-size:14px!important}.hero-title,.section-title{font-size:28px!important}.hero-copy,.section-copy,.card-copy{font-size:16px!important;line-height:1.5!important}
.draft-status span,.draft-chip span{font-size:13px!important}.draft-status b,.draft-chip b{font-size:22px!important}.on-clock{font-size:18px!important}
.player-name{font-size:17px!important}.player-meta,.data-cell span,.board-meta,.board-pick,.slot-meta{font-size:13px!important}.data-cell b,.slot-player{font-size:16px!important}
.draft-start-intro{background:linear-gradient(145deg,#14212d,#0d171f);border:1px solid #2b4151;border-radius:16px;padding:18px;margin:8px 0 14px}.draft-start-intro b{display:block;font-size:27px;color:#fff;margin-bottom:6px}.draft-start-intro span{display:block;font-size:16px;line-height:1.45;color:#b9c5cd}
.brand-badge,.brand-badge .shiva-trophy-mark{background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important}
.brand-badge .shiva-trophy-mark{mix-blend-mode:normal!important}
.st-key-primary_nav_Home .stButton>button::before{mix-blend-mode:normal!important}
.stCaptionContainer,[data-testid="stCaptionContainer"]{font-size:14px!important}
@media(max-width:520px){.screen-head h1{font-size:31px!important}.screen-head p{font-size:16px!important}.stButton>button{font-size:16px!important}.player-name{font-size:17px!important}.draft-start-intro b{font-size:25px!important}}
</style>'''
code = code.replace('app_header();qp=st.query_params', f'st.markdown({readability_patch!r},unsafe_allow_html=True);app_header();qp=st.query_params')

exec(compile(code, str(core), "exec"), globals(), globals())
