"""Targeted mobile cleanup requested 2026-09-03.

Keep this module narrow: presentation only. Do not change ESPN sync, Coach analysis,
draft logic, or data behavior.
"""
from __future__ import annotations

import streamlit as st
# Final presentation contract. These selectors intentionally override legacy page CSS.
# No radio indicators; one gold/white pill language; no trophy tile; compact bottom nav;
# consistent readable mobile type; no duplicate Home shortcut row; tighter top spacing.
POLISH_CSS = r'''
<style id="shiva-required-fixes-20260903">
:root{--sv-gold:#d8b45d;--sv-border:#30404b;--sv-bg:#071019}

/* 1 — bottom navigation is the only primary navigation. */
/* 2 — compact four-item bottom navigation; preserve iPhone safe area only. */
.st-key-bottom_nav_shell{bottom:0!important;padding:3px 7px max(3px,env(safe-area-inset-bottom))!important;min-height:0!important;height:auto!important;overflow:visible!important}
.st-key-bottom_nav_shell [data-testid="stHorizontalBlock"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:5px!important;margin:0!important}
.st-key-bottom_nav_shell .stButton>button{height:46px!important;min-height:46px!important;padding:5px 3px!important;border-radius:11px!important;font-size:13.5px!important;line-height:1!important}
.st-key-primary_nav_Home .stButton>button{padding:5px 3px!important}
.st-key-primary_nav_Home .stButton>button::before{content:none!important;display:none!important}
[data-testid="stMainBlockContainer"],.main .block-container,.block-container{padding-bottom:calc(60px + env(safe-area-inset-bottom))!important}

/* 3 — consistent readable app typography, including Coach/Trade Analyzer. */
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{font-size:16px!important;line-height:1.5!important}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,.stCaption,.stCaption p{font-size:14.5px!important;line-height:1.45!important}
.screen-head h1{font-size:32px!important;line-height:1.07!important}.screen-head p{font-size:16px!important;line-height:1.45!important}
.product-hero h2,.coach-hero h2{font-size:29px!important;line-height:1.08!important}.product-hero p,.coach-hero p{font-size:16px!important;line-height:1.48!important}
.call-card b,.watch-item b,.edge-card b,.product-card b,.coach-card b{font-size:19px!important;line-height:1.25!important}
.call-card p,.watch-item p,.edge-card p,.product-card p,.coach-card p,.why-box{font-size:15.5px!important;line-height:1.48!important}
.metric b{font-size:21px!important}.metric span,.table-note{font-size:13.5px!important}

/* 4 — Coach/Home selectors: dotless gold/white pills, never red radio dots. */
div[role="radiogroup"]{display:flex!important;flex-wrap:wrap!important;gap:7px!important}
div[role="radiogroup"] label[data-baseweb="radio"]{position:relative!important;display:flex!important;align-items:center!important;justify-content:center!important;min-height:42px!important;padding:7px 11px!important;margin:0!important;border:1px solid var(--sv-border)!important;border-radius:12px!important;background:#0d161d!important;color:#aeb8bf!important;box-shadow:none!important}
div[role="radiogroup"] label[data-baseweb="radio"]>div:first-child,div[role="radiogroup"] label[data-baseweb="radio"] svg,div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::before,div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::after{display:none!important;width:0!important;height:0!important;opacity:0!important;border:0!important;content:none!important}
div[role="radiogroup"] label[data-baseweb="radio"] input{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important}
div[role="radiogroup"] label[data-baseweb="radio"] p{margin:0!important;font-size:14.5px!important;font-weight:900!important;color:inherit!important;line-height:1.15!important}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked){border-color:rgba(240,216,143,.78)!important;background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;color:#fff!important;box-shadow:0 0 0 1px rgba(213,177,92,.12)!important}
.product-tabs div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important;margin:5px 0 13px!important}

/* 5 — remove legacy top gutters/wasted phone space. */
[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}
[data-testid="stMainBlockContainer"],.main .block-container,section.main>div.block-container,.block-container{padding-top:0!important;margin-top:0!important}
.app-top{margin-top:0!important;padding-top:0!important;padding-bottom:4px!important}
.screen-head{margin-top:0!important}

/* 7 — Start Mock Draft matches normal app controls instead of an oversized CTA. */
.st-key-start_mock_draft .stButton>button{height:50px!important;min-height:50px!important;padding:7px 12px!important;border-radius:12px!important;font-size:16px!important;font-weight:900!important;box-shadow:none!important}
.st-key-start_mock_draft .stButton>button p{font-size:16px!important;font-weight:900!important}
.draft-start-intro{padding:16px!important;border-radius:15px!important;margin:5px 0 11px!important}.draft-start-intro b{font-size:24px!important}.draft-start-intro span{font-size:15.5px!important}

/* 8 — permanent trophy rule: transparent, borderless, shadowless, no tile. */
.brand-badge,.brand-badge .shiva-trophy-mark,.shiva-trophy-mark{background:transparent!important;background-color:transparent!important;border:0!important;outline:0!important;box-shadow:none!important;border-radius:0!important}
.brand-badge .shiva-trophy-mark,.shiva-startup-splash .shiva-trophy-mark{mix-blend-mode:screen!important;filter:none!important}
.st-key-primary_nav_Home .stButton>button::before{content:none!important;display:none!important}

@media(max-width:560px){
 [data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{font-size:16px!important}
 .product-hero h2,.coach-hero h2{font-size:28px!important}.product-hero p,.coach-hero p{font-size:15.5px!important}
 .call-card p,.watch-item p,.edge-card p,.product-card p,.coach-card p{font-size:15.5px!important}
}
</style>
'''

# Inject after the existing design system on the first native HTML render.
_original_html = st.html
_injected=False
def _html(body,*args,**kwargs):
    global _injected
    if not _injected and isinstance(body,str):
        body=body+POLISH_CSS
        _injected=True
    return _original_html(body,*args,**kwargs)
st.html=_html
