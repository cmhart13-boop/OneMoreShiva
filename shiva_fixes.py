"""Mobile presentation fixes for Shiva work pages.

Presentation only: preserve Home content and all app behavior/data contracts.
"""
from __future__ import annotations

import html
import streamlit as st
import shiva_draft_guide as _guide

POLISH_CSS = r'''
<style id="shiva-mobile-fixes-20260903">
:root{--sv-bg:#081016;--sv-panel:#101820;--sv-line:#25313a;--sv-text:#f7f7f5;--sv-muted:#aab3b9;--sv-gold2:#f0d88f}
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#081016!important;background-color:#081016!important;color-scheme:dark!important}

/* Bottom navigation must be physically anchored to the phone viewport. */
.st-key-bottom_nav_shell{
  position:fixed!important;
  left:0!important;right:0!important;bottom:0!important;
  z-index:2147483000!important;
  margin:0!important;
  padding:7px 10px calc(7px + env(safe-area-inset-bottom))!important;
  min-height:0!important;height:auto!important;
  background:#081016!important;
  border-top:1px solid #26323b!important;
  box-shadow:0 -10px 24px rgba(0,0,0,.18)!important;
}
.st-key-bottom_nav_shell [data-testid="stHorizontalBlock"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:7px!important;margin:0!important}
.st-key-bottom_nav_shell [data-testid="stColumn"],.st-key-bottom_nav_shell [data-testid="column"]{min-width:0!important;width:auto!important}
.st-key-bottom_nav_shell .stButton>button{height:50px!important;min-height:50px!important;padding:6px 4px!important;border-radius:12px!important;font-size:14px!important;line-height:1!important;overflow:visible!important}
[data-testid="stMainBlockContainer"],.main .block-container,.block-container{padding-bottom:calc(82px + env(safe-area-inset-bottom))!important}
.st-key-action_row{display:none!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important;overflow:hidden!important}

/* Home nav trophy: transparent and contained; never a black tile. */
.st-key-primary_nav_Home .stButton>button{position:relative!important;padding-top:25px!important;padding-bottom:4px!important}
.st-key-primary_nav_Home .stButton>button::before{display:block!important;content:""!important;position:absolute!important;top:3px!important;left:50%!important;transform:translateX(-50%)!important;width:19px!important;height:19px!important;background:transparent!important;border:0!important;box-shadow:none!important;background-position:center!important;background-size:contain!important;background-repeat:no-repeat!important;mix-blend-mode:screen!important}
.brand-badge,.brand-badge .shiva-trophy-mark,.shiva-trophy-mark{background:transparent!important;background-color:transparent!important;border:0!important;outline:0!important;box-shadow:none!important;border-radius:0!important}
.brand-badge .shiva-trophy-mark,.shiva-startup-splash .shiva-trophy-mark{mix-blend-mode:screen!important;filter:none!important}

/* Interior page spacing/readability. */
[data-testid="stMain"], [data-testid="stMainBlockContainer"], .main .block-container, section.main>div.block-container, .block-container{padding-top:0!important;margin-top:0!important}
.app-top{margin-top:0!important;padding-top:0!important;padding-bottom:6px!important}
.screen-head{margin-top:0!important}
.screen-head h1{font-size:31px!important;line-height:1.07!important;color:var(--sv-text)!important;letter-spacing:-.7px!important}
.screen-head p{font-size:15.5px!important;line-height:1.4!important;color:var(--sv-muted)!important}

/* Guide cards: force actual card layout even if surrounding Streamlit styles change. */
.guide-toc{display:grid!important;grid-template-columns:1fr 1fr!important;gap:10px!important;margin:8px 0 18px!important}
.guide-toc>a{display:block!important;text-decoration:none!important;color:inherit!important}
.guide-section-card{display:block!important;height:100%!important;background:#101820!important;border:1px solid #2b3741!important;border-radius:16px!important;padding:15px!important;box-shadow:none!important}
.guide-section-card b{display:block!important;font-size:16px!important;line-height:1.2!important;color:#fff!important}
.guide-section-card span{display:block!important;font-size:13px!important;line-height:1.4!important;color:#aab3b9!important;margin-top:5px!important}
.guide-section-card em{display:block!important;font-style:normal!important;font-size:12px!important;font-weight:900!important;color:#f0d88f!important;margin-top:10px!important}
.guide-back{font-size:13px!important;color:#f0d88f!important}
.guide-subhead{font-size:22px!important;line-height:1.12!important;color:#fff!important}
.rank-row,.strategy-box,.rounds,.article-card,.article-body,.player-feature{background:#101820!important;border:1px solid #25313a!important;border-radius:16px!important;box-shadow:none!important}
.article-card p,.article-body p,.rounds{font-size:14px!important;line-height:1.5!important;color:#aab3b9!important}

/* Coach pills: selected state only, no radio dot. */
div[role="radiogroup"]{display:flex!important;flex-wrap:wrap!important;gap:7px!important}
div[role="radiogroup"] label[data-baseweb="radio"]{position:relative!important;display:flex!important;align-items:center!important;justify-content:center!important;min-height:42px!important;padding:7px 11px!important;margin:0!important;border:1px solid #30404b!important;border-radius:12px!important;background:#0d161d!important;color:#aeb8bf!important;box-shadow:none!important}
div[role="radiogroup"] label[data-baseweb="radio"]>div:first-child,div[role="radiogroup"] label[data-baseweb="radio"] svg,div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::before,div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::after{display:none!important;width:0!important;height:0!important;opacity:0!important;border:0!important;content:none!important}
div[role="radiogroup"] label[data-baseweb="radio"] input{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important}
div[role="radiogroup"] label[data-baseweb="radio"] p{margin:0!important;font-size:14px!important;font-weight:900!important;color:inherit!important;line-height:1.15!important}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked){border-color:rgba(240,216,143,.72)!important;background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;color:#fff!important}

/* Draft start CTA stays normal-sized. */
.st-key-start_mock_draft .stButton>button{height:48px!important;min-height:48px!important;padding:7px 12px!important;border-radius:12px!important;font-size:15px!important;font-weight:900!important;box-shadow:none!important}

[data-stale="true"],.stale{opacity:1!important;filter:none!important}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{transition:none!important;animation:none!important}

@media(max-width:560px){
  .guide-toc{grid-template-columns:1fr 1fr!important;gap:8px!important}
  .guide-section-card{padding:13px!important}
  .guide-section-card b{font-size:15px!important}.guide-section-card span{font-size:12px!important}
  .screen-head h1{font-size:29px!important}.screen-head p{font-size:15px!important}
  .st-key-bottom_nav_shell{padding-left:8px!important;padding-right:8px!important}
}
</style>
'''

# Streamlit's Markdown HTML path is the reliable global-style path for the rendered app.
st.markdown(POLISH_CSS, unsafe_allow_html=True)

# Keep the Guide home concise and card-based.
def _clean_guide_home():
    cards=[]
    for title,slug,desc in _guide.GUIDE_SECTIONS:
        cards.append(
            f'<a href="{_guide._guide_href(slug)}" target="_self"><div class="guide-section-card">'
            f'<b>{html.escape(title)}</b><span>{html.escape(desc)}</span><em>Open section →</em></div></a>'
        )
    st.markdown('<div class="guide-toc">'+''.join(cards)+'</div>',unsafe_allow_html=True)

_guide._render_home = _clean_guide_home
