"""One More Shiva production bootstrap.

The production invariant here is intentionally simple: after page config, app.py emits
zero Streamlit layout elements. app_runtime.py prepares app_core.py so the SHIVA header
is the first rendered element on every page. This prevents invisible style/component
blocks from creating a false top gutter on mobile.
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")

# app.py owns page configuration. Remove the duplicate call embedded in app_core before
# the runtime executes it. No st.markdown/st.empty/components.html calls are allowed
# above this point or they will become real vertical layout slots before the header.
_read_core = 'code = core.read_text(encoding="utf-8")'
_runtime_patch = _read_core + "\ncode = code.replace('st.set_page_config(page_title=\"One More Shiva\", page_icon=\"🏆\", layout=\"wide\", initial_sidebar_state=\"collapsed\")', '')"
runtime = runtime.replace(_read_core, _runtime_patch, 1)

exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
