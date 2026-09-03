"""Targeted presentation cleanup requested 2026-09-03.

Presentation only. Do not change ESPN sync, Coach analysis, draft logic, Home content,
logo assets, or splash behavior.
"""
from __future__ import annotations

import html
import streamlit as st
import shiva_draft_guide as _guide

POLISH_CSS = r'''
<style id="shiva-required-fixes-20260903">
:root{
  --sv-bg:#081016;
  --sv-panel:#101820;
  --sv-panel2:#141e27;
  --sv-line:#25313a;
  --sv-text:#f7f7f5;
  --sv-muted:#aab3b9;
  --sv-gold:#d5b15c;
  --sv-gold2:#f0d88f;
}

/* --------------------------------------------------------------------------
   NAVIGATION — compact, fully visible, no gray stale-state flash.
   -------------------------------------------------------------------------- */
.st-key-action_row{display:none!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important;overflow:hidden!important}
.st-key-bottom_nav_shell{
  bottom:0!important;
  padding:2px 7px max(2px,env(safe-area-inset-bottom))!important;
  min-height:0!important;
  height:auto!important;
  overflow:visible!important;
}
.st-key-bottom_nav_shell [data-testid="stHorizontalBlock"]{
  display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:5px!important;
  margin:0!important;
}
.st-key-bottom_nav_shell [data-testid="stColumn"],
.st-key-bottom_nav_shell [data-testid="column"]{min-width:0!important;width:auto!important}
.st-key-bottom_nav_shell .stButton>button{
  height:46px!important;
  min-height:46px!important;
  padding:4px 3px!important;
  border-radius:11px!important;
  font-size:13px!important;
  line-height:1!important;
  overflow:visible!important;
}
[data-testid="stMainBlockContainer"],.main .block-container,.block-container{
  padding-bottom:calc(55px + env(safe-area-inset-bottom))!important;
}
.st-key-primary_nav_Home .stButton>button{
  position:relative!important;
  padding-top:23px!important;
  padding-bottom:4px!important;
}
.st-key-primary_nav_Home .stButton>button::before{
  display:block!important;
  content:""!important;
  position:absolute!important;
  top:3px!important;
  left:50%!important;
  transform:translateX(-50%)!important;
  width:18px!important;
  height:18px!important;
  background-color:transparent!important;
  border:0!important;
  border-radius:0!important;
  box-shadow:none!important;
  mix-blend-mode:screen!important;
  filter:none!important;
  background-position:center!important;
  background-size:contain!important;
  background-repeat:no-repeat!important;
}

/* Streamlit marks the previous tree stale during reruns. Keep the old frame visually
   stable until the new page replaces it instead of dimming/graying the whole app. */
[data-stale="true"],
[data-testid="stAppViewContainer"] [data-stale="true"],
.stale{opacity:1!important;filter:none!important}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  transition:none!important;
  animation:none!important;
}

/* --------------------------------------------------------------------------
   SHARED NON-HOME VISUAL LANGUAGE — copied from the approved Home treatment.
   -------------------------------------------------------------------------- */
.screen-head h1{font-size:31px!important;line-height:1.07!important;color:var(--sv-text)!important;letter-spacing:-.7px!important}
.screen-head p{font-size:15.5px!important;line-height:1.4!important;color:var(--sv-muted)!important}

/* Native controls: same dark panel + gold selected state used on Home. */
div[role="radiogroup"]{display:flex!important;flex-wrap:wrap!important;gap:7px!important}
div[role="radiogroup"] label[data-baseweb="radio"]{
  position:relative!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  min-height:42px!important;
  padding:7px 11px!important;
  margin:0!important;
  border:1px solid #30404b!important;
  border-radius:12px!important;
  background:#0d161d!important;
  color:#aeb8bf!important;
  box-shadow:none!important;
}
div[role="radiogroup"] label[data-baseweb="radio"]>div:first-child,
div[role="radiogroup"] label[data-baseweb="radio"] svg,
div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::before,
div[role="radiogroup"] label[data-baseweb="radio"] [role="radio"]::after{
  display:none!important;width:0!important;height:0!important;opacity:0!important;border:0!important;content:none!important
}
div[role="radiogroup"] label[data-baseweb="radio"] input{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important}
div[role="radiogroup"] label[data-baseweb="radio"] p{margin:0!important;font-size:14px!important;font-weight:900!important;color:inherit!important;line-height:1.15!important}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked){
  border-color:rgba(240,216,143,.72)!important;
  background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;
  color:#fff!important;
  box-shadow:0 0 0 1px rgba(213,177,92,.12)!important;
}

/* --------------------------------------------------------------------------
   GUIDE — readable, Home-sized typography and Home-style cards.
   -------------------------------------------------------------------------- */
.guide-toc{gap:10px!important;margin:4px 0 15px!important}
.guide-section-card,
.article-card,
.player-feature,
.strategy-box,
.rank-row,
.article-body,
.rounds{
  background:var(--sv-panel)!important;
  border:1px solid var(--sv-line)!important;
  border-radius:16px!important;
  box-shadow:none!important;
}
.guide-section-card{padding:15px!important}
.guide-section-card b{font-size:16px!important;line-height:1.2!important;color:var(--sv-text)!important}
.guide-section-card span{font-size:13px!important;line-height:1.4!important;color:var(--sv-muted)!important;margin-top:5px!important}
.guide-section-card em{font-size:12px!important;color:var(--sv-gold2)!important;margin-top:10px!important}
.guide-back{font-size:13px!important;color:var(--sv-gold2)!important;margin-bottom:12px!important}
.guide-subhead{font-size:22px!important;line-height:1.12!important;color:var(--sv-text)!important;margin:9px 0 10px!important}
.rank-row{min-height:58px!important;padding:10px 11px!important;margin-bottom:6px!important}
.rank-n{font-size:13px!important}.rank-name{font-size:16px!important;line-height:1.2!important}
.strategy-box{padding:14px!important}.strategy-box span{font-size:11px!important}.strategy-box b{font-size:16px!important;line-height:1.25!important}
.rounds{font-size:15px!important;line-height:1.55!important;padding:15px!important;color:#c8d2d9!important}
.article-card{padding:14px!important}.article-card b{font-size:16px!important;line-height:1.25!important}.article-card p{font-size:14px!important;line-height:1.5!important;color:var(--sv-muted)!important}.article-card span{font-size:11.5px!important;color:var(--sv-gold2)!important}
.article-body{padding:16px!important}.article-body h3{font-size:24px!important}.article-body p{font-size:15px!important;line-height:1.55!important}
.player-feature{padding:14px!important}.player-feature b{font-size:15.5px!important}.player-feature span{font-size:11.5px!important;color:var(--sv-gold2)!important}
.st-key-guide_rank_filters .stButton>button{
  min-height:39px!important;
  border-radius:11px!important;
  font-size:12px!important;
  font-weight:950!important;
  background:#0d161d!important;
  border-color:#30404b!important;
  color:#9eabb3!important;
}
.st-key-guide_rank_filters .stButton>button[kind="primary"]{
  border-color:rgba(240,216,143,.72)!important;
  background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;
  color:#fff!important;
  box-shadow:0 0 0 1px rgba(213,177,92,.12)!important;
}

/* --------------------------------------------------------------------------
   COACH — same scale, colors, card shape, pills, and spacing as Home.
   -------------------------------------------------------------------------- */
.coach-phase{font-size:11px!important;color:var(--sv-gold2)!important;margin:6px 1px 8px!important}
.coach-hero{
  background:linear-gradient(145deg,#111b23,#0d151b)!important;
  border:1px solid rgba(213,177,92,.30)!important;
  border-radius:17px!important;
  padding:16px!important;
  margin-bottom:13px!important;
}
.coach-hero>span,.shiva-says-call>span,.draft-moment>span,.moment>span,.lineup-alert>span{font-size:11px!important;color:var(--sv-gold2)!important}
.coach-hero h2{font-size:25px!important;line-height:1.08!important;color:var(--sv-text)!important;margin:5px 0 6px!important}
.coach-hero p{font-size:15px!important;line-height:1.45!important;color:var(--sv-muted)!important}
.coach-section-title{font-size:22px!important;line-height:1.12!important;color:var(--sv-text)!important;margin:15px 0 9px!important}
.coach-player-card,.moment,.watch-card{
  background:var(--sv-panel)!important;
  border:1px solid var(--sv-line)!important;
  border-radius:16px!important;
  padding:14px!important;
}
.coach-player-top b,.moment b,.watch-card b{font-size:16px!important;line-height:1.25!important}
.coach-player-top span{font-size:12px!important;color:var(--sv-muted)!important}.coach-rank{font-size:13px!important;color:var(--sv-gold2)!important}
.coach-metrics div{background:#0d151b!important;border:1px solid #222f38!important;border-radius:10px!important;padding:9px!important}
.coach-metrics strong{font-size:19px!important}.coach-metrics span{font-size:10px!important}
.shiva-says-call,.draft-moment,.lineup-alert{
  background:linear-gradient(145deg,rgba(213,177,92,.12),rgba(213,177,92,.04))!important;
  border:1px solid rgba(213,177,92,.30)!important;
  border-radius:16px!important;
  padding:14px!important;
}
.shiva-says-call b,.draft-moment b,.lineup-alert b{font-size:18px!important}.shiva-says-call p,.draft-moment p,.lineup-alert p,.moment p,.watch-card p{font-size:14px!important;line-height:1.48!important;color:var(--sv-muted)!important}
.watch-card a{font-size:12px!important;color:var(--sv-gold2)!important}
.st-key-coach_view div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:6px!important;overflow:visible!important}
.st-key-coach_view div[role="radiogroup"] label{min-width:0!important;min-height:42px!important;padding:6px 5px!important}
.st-key-coach_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11.5px!important}

/* --------------------------------------------------------------------------
   DRAFT — align density, type, surfaces, and CTA proportions to Home.
   -------------------------------------------------------------------------- */
.draft-start-intro{
  background:linear-gradient(145deg,#111b23,#0d151b)!important;
  border:1px solid var(--sv-line)!important;
  border-radius:17px!important;
  padding:16px!important;
  margin:7px 0 12px!important;
}
.draft-start-intro b{font-size:23px!important;line-height:1.08!important;color:var(--sv-text)!important}
.draft-start-intro span{font-size:15px!important;line-height:1.45!important;color:var(--sv-muted)!important}
.st-key-start_mock_draft .stButton>button{
  height:48px!important;
  min-height:48px!important;
  padding:7px 12px!important;
  border-radius:12px!important;
  font-size:15px!important;
  font-weight:900!important;
  box-shadow:none!important;
}
.draft-status,.draft-chip,.player-row,.board-row,.draft-moment{border-color:var(--sv-line)!important}
.player-name{font-size:16px!important}.player-meta,.board-meta,.board-pick,.slot-meta{font-size:12.5px!important}.data-cell b,.slot-player{font-size:15.5px!important}

/* Top-spacing cleanup across interior pages. */
[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}
[data-testid="stMainBlockContainer"],.main .block-container,section.main>div.block-container,.block-container{padding-top:0!important;margin-top:0!important}
.app-top{margin-top:0!important;padding-top:0!important;padding-bottom:4px!important}.screen-head{margin-top:0!important}

/* Trophy treatment is preserved and forced transparent; never create a black tile. */
.brand-badge,.brand-badge .shiva-trophy-mark,.shiva-trophy-mark{
  background:transparent!important;background-color:transparent!important;border:0!important;outline:0!important;box-shadow:none!important;border-radius:0!important
}
.brand-badge .shiva-trophy-mark,.shiva-startup-splash .shiva-trophy-mark{mix-blend-mode:screen!important;filter:none!important}

@media(max-width:560px){
  .screen-head h1{font-size:29px!important}.screen-head p{font-size:15px!important}
  .guide-section-card b{font-size:16px!important}.guide-section-card span{font-size:13px!important}
  .article-card p,.shiva-says-call p,.draft-moment p,.lineup-alert p,.moment p,.watch-card p{font-size:14px!important}
  .coach-hero h2{font-size:24px!important}.coach-hero p{font-size:14.5px!important}
  .st-key-coach_view div[role="radiogroup"]{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:4px!important}
  .st-key-coach_view div[role="radiogroup"] label{min-width:0!important;padding:5px 2px!important}
  .st-key-coach_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10.5px!important}
}
</style>
'''

_original_html = st.html
_injected = False


def _html(body,*args,**kwargs):
    global _injected
    if not _injected and isinstance(body,str):
        body = body + POLISH_CSS
        _injected = True
    return _original_html(body,*args,**kwargs)


st.html = _html


# Guide home: preserve the existing content and links, render only the useful section cards.
def _clean_guide_home():
    cards=[]
    for title,slug,desc in _guide.GUIDE_SECTIONS:
        cards.append(
            f'<a href="{_guide._guide_href(slug)}" target="_self"><div class="guide-section-card">'
            f'<b>{html.escape(title)}</b><span>{html.escape(desc)}</span><em>Open section →</em></div></a>'
        )
    st.markdown('<div class="guide-toc">'+''.join(cards)+'</div>',unsafe_allow_html=True)


_guide._render_home = _clean_guide_home
