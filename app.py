"""Vercel/ASGI launcher for One More Shiva.

The application itself lives in ``streamlit_app.py``. Streamlit 1.61 exposes
``st.App`` as an ASGI-compatible application object, which gives Vercel the
standard top-level ``app`` entry point its Python runtime expects while keeping
the existing Streamlit application code unchanged.
"""
import streamlit as st

app = st.App("streamlit_app.py")
