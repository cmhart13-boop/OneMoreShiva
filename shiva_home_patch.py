"""Targeted home-screen cleanup for the production Shiva app."""
from __future__ import annotations

import streamlit as st
import shiva_home_v2 as _home

_ORIGINAL_RENDER_HOME = _home.render_home_v2
_HERO_MARKER = "Win the decision in front of you."
_WAR_ROOM_MARKUP = '<div class="home-v2-section">Your War Room</div>'
_WAR_ROOM_TIGHT = '<div class="home-v2-section" style="margin-top:4px">Your War Room</div>'
_EDGE_OLD_TYPE = '.home-edge small{font-size:14px;font-weight:950;letter-spacing:.55px;color:var(--sv-gold2);text-transform:uppercase}.home-edge b{display:block;font-size:23px;color:#fff;margin:8px 0 6px;line-height:1.12}'
_EDGE_NEW_TYPE = '.home-edge small{display:block;font-size:27px;font-weight:950;letter-spacing:-.45px;color:var(--sv-gold2);text-transform:uppercase;line-height:1.05;margin:0 0 8px}.home-edge b{display:block;font-size:18px;font-weight:850;color:#fff;margin:0 0 7px;line-height:1.18}'
_EDGE_OLD_COPY = '<small>Raise the floor</small><b>Repeatable 15+ scoring</b>'
_EDGE_NEW_COPY = '<small>Raise the floor</small><b>Consistent 15+ scoring</b>'


def _render_home_without_hero(*args, **kwargs):
    original_markdown = st.markdown

    def filtered_markdown(body, *m_args, **m_kwargs):
        if isinstance(body, str) and _HERO_MARKER in body:
            return None
        if isinstance(body, str) and _WAR_ROOM_MARKUP in body:
            body = body.replace(_WAR_ROOM_MARKUP, _WAR_ROOM_TIGHT, 1)
        if isinstance(body, str) and _EDGE_OLD_TYPE in body:
            body = body.replace(_EDGE_OLD_TYPE, _EDGE_NEW_TYPE, 1)
        if isinstance(body, str) and _EDGE_OLD_COPY in body:
            body = body.replace(_EDGE_OLD_COPY, _EDGE_NEW_COPY, 1)
        return original_markdown(body, *m_args, **m_kwargs)

    st.markdown = filtered_markdown
    try:
        return _ORIGINAL_RENDER_HOME(*args, **kwargs)
    finally:
        st.markdown = original_markdown


_home.render_home_v2 = _render_home_without_hero
