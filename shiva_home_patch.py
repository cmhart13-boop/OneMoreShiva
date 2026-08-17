"""Targeted home-screen cleanup for the production Shiva app."""
from __future__ import annotations

import streamlit as st
import shiva_home_v2 as _home

_ORIGINAL_RENDER_HOME = _home.render_home_v2
_HERO_MARKER = "Win the decision in front of you."
_WAR_ROOM_MARKUP = '<div class="home-v2-section">Your War Room</div>'
_WAR_ROOM_TIGHT = '<div class="home-v2-section" style="margin-top:4px">Your War Room</div>'


def _render_home_without_hero(*args, **kwargs):
    original_markdown = st.markdown

    def filtered_markdown(body, *m_args, **m_kwargs):
        if isinstance(body, str) and _HERO_MARKER in body:
            return None
        if isinstance(body, str) and _WAR_ROOM_MARKUP in body:
            body = body.replace(_WAR_ROOM_MARKUP, _WAR_ROOM_TIGHT, 1)
        return original_markdown(body, *m_args, **m_kwargs)

    st.markdown = filtered_markdown
    try:
        return _ORIGINAL_RENDER_HOME(*args, **kwargs)
    finally:
        st.markdown = original_markdown


_home.render_home_v2 = _render_home_without_hero
