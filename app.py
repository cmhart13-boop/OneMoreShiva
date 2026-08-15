"""One More Shiva launch bootstrap.

Paint the app's dark launch surface before the heavier production runtime imports and
runtime patches execute. This prevents the bright white frame seen on cold mobile
launches while preserving the existing app behavior in app_runtime.py.
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_boot_slot = None
if not st.session_state.get("_shiva_bootstrap_painted", False):
    st.session_state["_shiva_bootstrap_painted"] = True
    _boot_slot = st.empty()
    _boot_slot.markdown(
        """
        <style>
        html, body, #root, [data-testid="stApp"], [data-testid="stAppViewContainer"],
        [data-testid="stMain"], [data-testid="stMainBlockContainer"], .stApp {
            background: #071019 !important;
            color-scheme: dark !important;
        }
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stAppViewContainer"] section,
        .main, .block-container {
            background: #071019 !important;
        }
        .shiva-launch-paint {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100dvh;
            z-index: 2147483646;
            background: #071019;
            pointer-events: none;
        }
        </style>
        <div class="shiva-launch-paint" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")

# app_runtime.py preserves the previous production entrypoint byte-for-byte. Since
# page config is now deliberately the very first Streamlit command above, remove the
# later duplicate page-config call from the app_core source before that runtime executes.
_read_core = 'code = core.read_text(encoding="utf-8")'
_runtime_patch = _read_core + "\ncode = code.replace('st.set_page_config(page_title=\"One More Shiva\", page_icon=\"🏆\", layout=\"wide\", initial_sidebar_state=\"collapsed\")', '')"
runtime = runtime.replace(_read_core, _runtime_patch, 1)

exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())

if _boot_slot is not None:
    _boot_slot.empty()
