"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- app.py emits zero Streamlit layout elements before runtime.
- app_runtime.py owns the single validated transformation/render pipeline.
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
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
