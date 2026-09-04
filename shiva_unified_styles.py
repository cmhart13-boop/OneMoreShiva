"""Shared visual shell for the four primary Shiva pages.

Home remains the visual source of truth. This module only normalizes layout, spacing,
typography, cards, and controls; it does not change navigation, splash behavior, data,
or feature logic.
"""
import streamlit as st


UNIFIED_CSS = r'''
<style>
:root{
  --shiva-shell-max:1080px;
  --shiva-page-bg:#081016;
  --shiva-card-bg:linear-gradient(145deg,#121b23,#0d141a);
  --shiva-card-line:rgba(216,179,91,.18);
  --shiva-card-radius:15px;
  --shiva-card-pad:15px;
  --shiva-text:#f7f8f9;
  --shiva-muted:#aeb8bf;
  --shiva-gold:#d8b35b;
}

/* One centered shell for Home, Draft, Guide, and Coach. */
.block-container{
  width:100%!important;
  max-width:var(--shiva-shell-max)!important;
  margin-left:auto!important;
  margin-right:auto!important;
  padding-left:.75rem!important;
  padding-right:.75rem!important;
}

/* Shared page-title scale, matching the Home dashboard hierarchy. */
.screen-head{margin:8px 0 13px!important}
.screen-head h1{
  font-size:31px!important;
  line-height:1.04!important;
  letter-spacing:-.8px!important;
  color:var(--shiva-text)!important;
  margin:0!important;
}
.screen-head p{
  font-size:15px!important;
  line-height:1.45!important;
  color:var(--shiva-muted)!important;
  margin:6px 0 0!important;
}

/* GUIDE — inherit Home card geometry and typography instead of a separate page system. */
.guide-toc{gap:9px!important;margin:6px 0 15px!important}
.guide-section-card,.rank-row,.strategy-box,.rounds,.article-card,.article-body,.player-feature{
  box-sizing:border-box!important;
  background:var(--shiva-card-bg)!important;
  border:1px solid var(--shiva-card-line)!important;
  border-radius:var(--shiva-card-radius)!important;
  box-shadow:none!important;
}
.guide-section-card,.strategy-box,.article-card,.player-feature{padding:var(--shiva-card-pad)!important}
.rank-row{padding:11px 12px!important;min-height:64px!important;margin-bottom:7px!important}
.rounds,.article-body{padding:var(--shiva-card-pad)!important}
.guide-section-card b,.strategy-box b,.article-card b,.player-feature b,.rank-name{
  color:var(--shiva-text)!important;
  font-size:17px!important;
  line-height:1.3!important;
}
.guide-section-card span,.article-card p,.rounds,.article-body p{
  color:var(--shiva-muted)!important;
  font-size:14px!important;
  line-height:1.45!important;
}
.guide-section-card em,.guide-player-link span,.article-card span,.player-feature span,.guide-back{
  color:var(--shiva-gold)!important;
}
.guide-subhead{
  font-size:25px!important;
  line-height:1.08!important;
  letter-spacing:-.5px!important;
  color:var(--shiva-text)!important;
  margin:13px 0 9px!important;
}
.article-body h3{
  font-size:25px!important;
  line-height:1.08!important;
  letter-spacing:-.5px!important;
  margin:0 0 8px!important;
  color:var(--shiva-text)!important;
}
.st-key-guide_rank_filters .stButton>button{
  min-height:50px!important;
  border-radius:13px!important;
  font-size:13px!important;
  background:#101820!important;
  border:1px solid #2b3945!important;
  color:#b9c3ca!important;
  box-shadow:none!important;
}
.st-key-guide_rank_filters .stButton>button[kind="primary"]{
  background:#202a33!important;
  border-color:#d0ad59!important;
  color:#fff!important;
  box-shadow:inset 0 -3px 0 #d0ad59!important;
}

/* COACH — remove its competing visual system and use Home's card rhythm. */
.product-hero,.edge-card,.call-card,.watch-item,.metric,.why-box,.compare-card,.package-card,.lineup-card{
  box-sizing:border-box!important;
  border-radius:var(--shiva-card-radius)!important;
}
.product-hero,.edge-card,.watch-item,.compare-card,.package-card,.lineup-card{
  background:var(--shiva-card-bg)!important;
  border:1px solid var(--shiva-card-line)!important;
  box-shadow:none!important;
}
.product-hero{
  padding:var(--shiva-card-pad)!important;
  margin:6px 0 13px!important;
}
.product-hero>span,.edge-card>span,.call-card>span,.watch-item>span{
  font-size:10px!important;
  letter-spacing:.75px!important;
  color:var(--shiva-gold)!important;
}
.product-hero h2{
  font-size:25px!important;
  line-height:1.06!important;
  letter-spacing:-.55px!important;
  margin:5px 0 6px!important;
  color:var(--shiva-text)!important;
}
.product-hero p,.edge-card p,.call-card p,.watch-item p{
  font-size:14px!important;
  line-height:1.45!important;
  color:var(--shiva-muted)!important;
}
.edge-grid{gap:9px!important;margin:8px 0 12px!important}
.edge-card{padding:var(--shiva-card-pad)!important;min-height:0!important}
.edge-card b{font-size:17px!important;line-height:1.28!important;margin:4px 0 5px!important;color:var(--shiva-text)!important}
.call-card{
  padding:var(--shiva-card-pad)!important;
  margin:9px 0 12px!important;
  border:1px solid rgba(216,179,91,.30)!important;
  background:linear-gradient(145deg,#181913,#10120f)!important;
}
.call-card b{font-size:18px!important;line-height:1.25!important;color:var(--shiva-text)!important}
.metric-grid{gap:8px!important;margin:8px 0 12px!important}
.metric{
  background:var(--shiva-card-bg)!important;
  border:1px solid var(--shiva-card-line)!important;
  padding:12px!important;
  text-align:left!important;
}
.metric b{font-size:20px!important;color:var(--shiva-text)!important}
.metric span{font-size:10px!important;line-height:1.3!important;color:var(--shiva-muted)!important}
.watch-item{padding:var(--shiva-card-pad)!important;margin:7px 0!important}
.watch-item b{font-size:16px!important;line-height:1.3!important;color:var(--shiva-text)!important}
.st-key-coach_tab_pills{margin:5px 0 13px!important}
.st-key-coach_tab_pills .stButton>button{
  min-height:50px!important;
  border-radius:13px!important;
  font-size:13px!important;
  background:#101820!important;
  border:1px solid #2b3945!important;
  color:#b9c3ca!important;
  box-shadow:none!important;
}
.st-key-coach_tab_pills .stButton>button[kind="primary"]{
  background:#202a33!important;
  border-color:#d0ad59!important;
  color:#fff!important;
  box-shadow:inset 0 -3px 0 #d0ad59!important;
}

@media(max-width:560px){
  .block-container{padding-left:.7rem!important;padding-right:.7rem!important}
  .screen-head h1{font-size:29px!important}
  .screen-head p{font-size:14.5px!important}
  .guide-toc,.strategy-grid,.player-feature-grid{grid-template-columns:1fr!important}
  .guide-subhead,.article-body h3,.product-hero h2{font-size:23px!important}
  .edge-grid{grid-template-columns:1fr!important}
  .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .st-key-guide_rank_filters [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}
  .st-key-guide_rank_filters [data-testid="stColumn"]{min-width:120px!important;flex:1 1 120px!important;width:auto!important}
  .st-key-coach_tab_pills .stButton>button,.st-key-guide_rank_filters .stButton>button{font-size:12px!important;min-height:48px!important}
}
</style>
'''


def inject_unified_styles() -> None:
    st.markdown(UNIFIED_CSS, unsafe_allow_html=True)
