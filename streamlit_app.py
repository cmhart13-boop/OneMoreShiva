"""One More Shiva production Streamlit application.

Vercel owns first paint; app_runtime owns application behavior. Shared visual contracts
load before runtime so they can style the rendered app without changing its data logic.
"""
from pathlib import Path
import builtins
import linecache

import streamlit as st

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.set_option("client.toolbarMode", "minimal")
st.session_state["_shiva_startup_splash_seen"] = True

import shiva_controls  # noqa: E402,F401
import shiva_style_authority  # noqa: E402,F401
import shiva_fixes  # noqa: E402,F401


def _shiva_compile(source, filename, mode, *args, **kwargs):
    if isinstance(source, str) and str(filename).endswith("app_core.py"):
        virtual = "<shiva_transformed_app_core>"
        linecache.cache[virtual] = (len(source), None, source.splitlines(keepends=True), virtual)
        return builtins.compile(source, virtual, mode, *args, **kwargs)
    return builtins.compile(source, filename, mode, *args, **kwargs)


compile = _shiva_compile
runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
