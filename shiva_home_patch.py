"""Targeted home-screen cleanup and app-wide control styling for the production Shiva app."""
from __future__ import annotations

import streamlit as st
import shiva_home_v2 as _home

_ORIGINAL_RENDER_HOME = _home.render_home_v2
_ORIGINAL_HTML = st.html
_HERO_MARKER = "Win the decision in front of you."
_WAR_ROOM_MARKUP = '<div class="home-v2-section">Your War Room</div>'
_WAR_ROOM_TIGHT = '<div class="home-v2-section" style="margin-top:4px">Your War Room</div>'
_EDGE_OLD_TYPE = '.home-edge small{font-size:14px;font-weight:950;letter-spacing:.55px;color:var(--sv-gold2);text-transform:uppercase}.home-edge b{display:block;font-size:23px;color:#fff;margin:8px 0 6px;line-height:1.12}'
_EDGE_NEW_TYPE = '.home-edge small{display:block;font-size:27px;font-weight:950;letter-spacing:-.45px;color:var(--sv-gold2);text-transform:uppercase;line-height:1.05;margin:0 0 8px}.home-edge b{display:block;font-size:18px;font-weight:850;color:#fff;margin:0 0 7px;line-height:1.18}'
_EDGE_OLD_COPY = '<small>Raise the floor</small><b>Repeatable 15+ scoring</b>'
_EDGE_NEW_COPY = '<small>Raise the floor</small><b>Consistent 15+ scoring</b>'

# Universal Shiva selector contract: native Streamlit radio circles/dots are never
# shown. Radio-based navigation/filter controls retain their native state and
# accessibility semantics, but visually match the clean illuminated position
# filters used by Raise the Floor / Keep the Ceiling.
_DOTLESS_CONTROL_CSS = r'''
<style id="shiva-dotless-control-contract">
div[role="radiogroup"]{
    display:flex!important;
    flex-wrap:wrap!important;
    gap:7px!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]{
    position:relative!important;
    display:inline-flex!important;
    align-items:center!important;
    justify-content:center!important;
    min-height:38px!important;
    min-width:0!important;
    margin:0!important;
    padding:5px 10px!important;
    border:1px solid #30404b!important;
    border-radius:11px!important;
    background:#0d161d!important;
    color:#9eabb3!important;
    cursor:pointer!important;
    -webkit-tap-highlight-color:transparent!important;
    transition:none!important;
    box-sizing:border-box!important;
}
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child{
    position:absolute!important;
    width:0!important;
    height:0!important;
    min-width:0!important;
    min-height:0!important;
    margin:0!important;
    padding:0!important;
    opacity:0!important;
    overflow:hidden!important;
    pointer-events:none!important;
}
div[role="radiogroup"] label[data-baseweb="radio"] input[type="radio"]{
    position:absolute!important;
    width:1px!important;
    height:1px!important;
    opacity:0!important;
    pointer-events:none!important;
}
div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child,
div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"]{
    margin:0!important;
    padding:0!important;
    color:inherit!important;
    font-size:12px!important;
    font-weight:950!important;
    letter-spacing:.25px!important;
    line-height:1.1!important;
    text-align:center!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input[type="radio"]:checked){
    border-color:rgba(240,216,143,.72)!important;
    background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;
    color:#fff!important;
    box-shadow:0 0 0 1px rgba(213,177,92,.12),0 0 18px rgba(213,177,92,.12)!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]:focus-within{
    outline:1px solid rgba(240,216,143,.72)!important;
    outline-offset:1px!important;
}
@media(max-width:520px){
    div[role="radiogroup"]{gap:6px!important}
    div[role="radiogroup"] label[data-baseweb="radio"]{min-height:36px!important;padding:4px 8px!important}
    div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child,
    div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"]{font-size:11.5px!important}
}
</style>
'''

_dotless_css_injected = False


def _html_with_dotless_controls(body, *args, **kwargs):
    global _dotless_css_injected
    if not _dotless_css_injected and isinstance(body, str):
        body = _DOTLESS_CONTROL_CSS + body
        _dotless_css_injected = True
    return _ORIGINAL_HTML(body, *args, **kwargs)


# app_runtime's canonical first paint calls st.html. Wrapping it here folds the
# universal control CSS into that same first paint instead of creating another
# pre-header Streamlit element or flash.
st.html = _html_with_dotless_controls


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
