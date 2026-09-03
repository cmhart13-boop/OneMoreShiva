"""Final app-wide UI contract for One More Shiva.

This module owns the visual contract that must stay consistent across Home, Draft,
Guide, and Coach: readable mobile typography, dotless native selectors, pill-style
selected states, Guide scale, and primary draft CTA treatment.
"""
from __future__ import annotations

import streamlit as st

_ORIGINAL_HTML = st.html

# This stylesheet is intentionally appended after each page's legacy CSS in the first
# app_header st.html call. It is the final design-system layer, not a page-by-page patch,
# so shared navigation/typography remain consistent even where older page modules have
# narrower mobile overrides.
_UI_CONTRACT_CSS = r'''
<style id="shiva-ui-contract-v4">
/* --------------------------------------------------------------------------
   Native selector contract: no radio dot anywhere. Selected state = pill only.
   -------------------------------------------------------------------------- */
div[role="radiogroup"]{
    display:flex!important;
    flex-wrap:wrap!important;
    gap:8px!important;
    align-items:stretch!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]{
    position:relative!important;
    display:inline-flex!important;
    align-items:center!important;
    justify-content:center!important;
    min-height:42px!important;
    min-width:0!important;
    margin:0!important;
    padding:7px 12px!important;
    border:1px solid #30404b!important;
    border-radius:12px!important;
    background:#0d161d!important;
    color:#aeb8bf!important;
    cursor:pointer!important;
    -webkit-tap-highlight-color:transparent!important;
    box-sizing:border-box!important;
    box-shadow:none!important;
}
/* Hide every native BaseWeb radio indicator, including SVG/circle implementations. */
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child,
div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stRadio"] svg,
div[role="radiogroup"] label[data-baseweb="radio"] svg,
div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::before,
div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::after{
    position:absolute!important;
    width:0!important;
    height:0!important;
    min-width:0!important;
    min-height:0!important;
    margin:0!important;
    padding:0!important;
    border:0!important;
    opacity:0!important;
    overflow:hidden!important;
    pointer-events:none!important;
    display:none!important;
    content:none!important;
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
    font-size:15px!important;
    font-weight:900!important;
    letter-spacing:.1px!important;
    line-height:1.15!important;
    text-align:center!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input[type="radio"]:checked){
    border-color:rgba(240,216,143,.72)!important;
    background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;
    color:#fff!important;
    box-shadow:0 0 0 1px rgba(213,177,92,.12),0 0 18px rgba(213,177,92,.10)!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]:focus-within{
    outline:1px solid rgba(240,216,143,.72)!important;
    outline-offset:1px!important;
}

/* Coach sub-navigation uses the same compact pill language as Home filters. */
.product-tabs div[role="radiogroup"]{
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:8px!important;
    margin:8px 0 16px!important;
}
.product-tabs div[role="radiogroup"] label[data-baseweb="radio"]{
    min-height:44px!important;
    padding:7px 8px!important;
    border-radius:12px!important;
    background:#0d161d!important;
    border-color:#30404b!important;
}
.product-tabs div[role="radiogroup"] label[data-baseweb="radio"]:has(input[type="radio"]:checked){
    border-color:rgba(240,216,143,.72)!important;
    background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;
}
.product-tabs div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p{
    font-size:14px!important;
    font-weight:900!important;
    line-height:1.15!important;
    white-space:normal!important;
}

/* --------------------------------------------------------------------------
   Shared mobile typography: readable hierarchy across all four main pages.
   -------------------------------------------------------------------------- */
.screen-head h1{font-size:34px!important;line-height:1.06!important;letter-spacing:-.8px!important}
.screen-head p{font-size:17px!important;line-height:1.48!important;color:#aebbc4!important;margin-top:6px!important}
.stMarkdown p,.stMarkdown li{font-size:16px!important;line-height:1.52!important}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,.stCaption,.stCaption p{font-size:15px!important;line-height:1.48!important}
.stButton>button{font-size:16px!important;font-weight:900!important}
.stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stNumberInput label{font-size:15px!important;line-height:1.3!important}
.home-v2-section,.edge-title{font-size:27px!important;line-height:1.1!important}
.home-v2-sub,.edge-sub{font-size:16px!important;line-height:1.48!important}
.home-edge-preview small{font-size:19px!important;line-height:1.08!important}
.home-edge-preview b,.edge-preview-name{font-size:16px!important;line-height:1.25!important}
.edge-preview-meta,.edge-panel-kicker,.edge-rank-meta,.edge-method{font-size:14px!important;line-height:1.42!important}
.edge-panel-title{font-size:27px!important;line-height:1.08!important}
.edge-panel-copy,.home-edge p{font-size:16px!important;line-height:1.5!important}
.edge-rank-name{font-size:18px!important}.edge-rank-stat b{font-size:22px!important}.edge-rank-stat span{font-size:13px!important}
.product-hero{padding:22px 19px!important;border-radius:18px!important;margin:7px 0 16px!important}
.product-hero>span,.edge-card>span,.call-card>span,.watch-item>span{font-size:13px!important;line-height:1.2!important}
.product-hero h2{font-size:31px!important;line-height:1.05!important;margin:7px 0 9px!important}
.product-hero p{font-size:16px!important;line-height:1.5!important;color:#bcc5cb!important}
.edge-card,.call-card,.watch-item{padding:17px!important}.edge-card b{font-size:20px!important}.edge-card p,.call-card p,.watch-item p,.why-box{font-size:15px!important;line-height:1.5!important}
.call-card b{font-size:21px!important}.metric span,.table-note{font-size:13px!important}.metric b{font-size:22px!important}

/* --------------------------------------------------------------------------
   2026 Shiva Draft Guide: larger cards + larger internal content, not text only.
   -------------------------------------------------------------------------- */
.guide-toc{gap:12px!important;margin:6px 0 19px!important}
.guide-section-card{padding:17px!important;border-radius:17px!important;min-height:126px!important}
.guide-section-card b{font-size:18px!important;line-height:1.22!important}
.guide-section-card span{font-size:14px!important;line-height:1.42!important;margin-top:6px!important}
.guide-section-card em{font-size:13px!important;margin-top:12px!important}
.guide-back{font-size:14px!important;margin-bottom:14px!important}
.guide-subhead{font-size:25px!important;line-height:1.12!important;margin:12px 0 11px!important}
.rank-row{grid-template-columns:36px 40px minmax(0,1fr)!important;gap:9px!important;padding:13px 13px!important;margin-bottom:8px!important;min-height:68px!important;border-radius:14px!important}
.rank-n{font-size:15px!important}.rank-name{font-size:18px!important;line-height:1.25!important}.pos-chip{font-size:10px!important;padding:5px 3px!important;border-radius:6px!important}
.guide-player-link span{font-size:13px!important}
.strategy-grid{gap:12px!important;margin:10px 0 16px!important}
.strategy-box{padding:17px!important;border-radius:17px!important;min-height:112px!important}
.strategy-box span{font-size:13px!important}.strategy-box b{font-size:18px!important;line-height:1.3!important;margin-top:5px!important}
.article-card,.player-card-link,.guide-card{border-radius:17px!important}
.article-card,.guide-card{padding:17px!important}
.article-card b,.guide-card b{font-size:18px!important;line-height:1.3!important}
.article-card p,.guide-card p{font-size:15px!important;line-height:1.5!important}

/* Draft room hierarchy and primary mock-draft CTA. */
.draft-start-intro{padding:20px!important;border-radius:18px!important;margin:10px 0 16px!important}
.draft-start-intro b{font-size:28px!important;line-height:1.08!important}.draft-start-intro span{font-size:16px!important;line-height:1.5!important}
.st-key-start_mock_draft .stButton>button{
    min-height:58px!important;
    padding:11px 18px!important;
    font-size:19px!important;
    line-height:1.15!important;
    font-weight:950!important;
    color:#fff!important;
    letter-spacing:.1px!important;
}
.draft-status span,.draft-chip span{font-size:14px!important}.draft-status b,.draft-chip b{font-size:23px!important}.on-clock{font-size:18px!important}
.player-name,.slot-player,.board-name{font-size:17px!important;line-height:1.3!important}.player-meta,.slot-meta,.board-meta,.board-pick,.data-cell span{font-size:13px!important;line-height:1.35!important}

@media(max-width:560px){
    .screen-head h1{font-size:32px!important}.screen-head p{font-size:16.5px!important}
    .stMarkdown p,.stMarkdown li{font-size:16px!important}
    div[role="radiogroup"] label[data-baseweb="radio"]{min-height:40px!important;padding:6px 10px!important}
    div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"]{font-size:14px!important}
    .product-tabs div[role="radiogroup"]{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important}
    .product-tabs div[role="radiogroup"] label[data-baseweb="radio"]{min-height:43px!important}
    .product-tabs div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p{font-size:14px!important}
    .home-v2-section,.edge-title{font-size:25px!important}.home-v2-sub,.edge-sub{font-size:15.5px!important}
    .product-hero h2{font-size:29px!important}.product-hero p{font-size:15.5px!important}.product-hero>span{font-size:12.5px!important}
    .guide-toc{grid-template-columns:1fr!important}
    .guide-section-card{min-height:0!important;padding:16px!important}.guide-section-card b{font-size:18px!important}.guide-section-card span{font-size:14px!important}
    .guide-subhead{font-size:24px!important}.rank-row{min-height:66px!important}.rank-name{font-size:17.5px!important}
    .strategy-grid{grid-template-columns:1fr!important}.strategy-box{min-height:0!important}
    .draft-start-intro b{font-size:26px!important}.st-key-start_mock_draft .stButton>button{min-height:58px!important;font-size:19px!important}
}
</style>
'''

_ui_css_injected = False


def _html_with_ui_contract(body, *args, **kwargs):
    global _ui_css_injected
    if not _ui_css_injected and isinstance(body, str):
        # Append so this shared design-system contract is the final cascade layer.
        body = body + _UI_CONTRACT_CSS
        _ui_css_injected = True
    return _ORIGINAL_HTML(body, *args, **kwargs)


st.html = _html_with_ui_contract

# Coach extension: preserve the existing Coach product and add Draft Grade as one
# additional roster-aware view. Patching the module attribute here means app_core's
# later `from shiva_product import render_full_product` receives the extended version
# without changing Home, Draft, Guide, navigation, or startup behavior.
import shiva_product as _shiva_product
from shiva_product_plus import render_full_product as _render_full_product_plus
_shiva_product.render_full_product = _render_full_product_plus
