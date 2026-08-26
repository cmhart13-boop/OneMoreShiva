"""App-wide native selector styling for the production Shiva app."""
from __future__ import annotations

import streamlit as st

_ORIGINAL_HTML = st.html

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


# app_runtime's canonical first paint calls st.html. Wrapping that native call
# keeps the selector contract in the same first paint without adding a layout
# element or changing any page renderer.
st.html = _html_with_dotless_controls
