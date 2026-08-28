"""One More Shiva production Streamlit application.

Vercel's ASGI entrypoint owns the browser's first paint and launch splash. This module
owns only the Streamlit application runtime, so there is no redirect, second document
load, or duplicate splash during startup.
"""
from pathlib import Path
import builtins
import linecache

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.set_option("client.toolbarMode", "minimal")
st.session_state["_shiva_startup_splash_seen"] = True

import shiva_controls  # noqa: E402,F401


def _shiva_compile(source, filename, mode, *args, **kwargs):
    if isinstance(source, str) and str(filename).endswith("app_core.py"):
        virtual = "<shiva_transformed_app_core>"
        linecache.cache[virtual] = (len(source), None, source.splitlines(keepends=True), virtual)
        return builtins.compile(source, virtual, mode, *args, **kwargs)
    return builtins.compile(source, filename, mode, *args, **kwargs)


compile = _shiva_compile
runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())

# Final shared mobile UI contract. This is intentionally centralized so Home, Draft,
# Guide, Coach and shared controls use one consistent scale and selected-state system.
st.html(
    """
    <style id="shiva-six-item-ui-contract">
    :root{--shiva-navy:#071019;--shiva-panel:#0e1821;--shiva-panel2:#101b24;--shiva-border:#2c3a45;--shiva-gold:#d8b45d;--shiva-text:#f7f9fb;--shiva-muted:#a8b4bd}

    /* 2 — materially larger type across every primary destination */
    .screen-head h1{font-size:34px!important;line-height:1.05!important;font-weight:950!important}
    .screen-head p{font-size:18px!important;line-height:1.45!important}
    [data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{font-size:17px!important;line-height:1.5!important}
    [data-testid="stCaptionContainer"],.stCaption{font-size:15.5px!important}
    .stButton>button{font-size:16px!important;font-weight:850!important}

    /* 3 + 4 — one dotless pill-control language everywhere */
    [data-testid="stRadio"]>div{gap:8px!important;display:flex!important;flex-wrap:wrap!important}
    [data-testid="stRadio"] label{min-height:42px!important;padding:8px 12px!important;border:1px solid var(--shiva-border)!important;border-radius:12px!important;background:#0d161d!important;display:flex!important;align-items:center!important;justify-content:center!important}
    [data-testid="stRadio"] label>div:first-child,[data-testid="stRadio"] input{display:none!important;width:0!important;height:0!important;opacity:0!important}
    [data-testid="stRadio"] label p{font-size:15px!important;font-weight:900!important;color:#aeb9c2!important;line-height:1!important;margin:0!important}
    [data-testid="stRadio"] label:has(input:checked){background:#1a252e!important;border-color:var(--shiva-gold)!important;box-shadow:0 0 0 1px rgba(216,180,93,.12)!important}
    [data-testid="stRadio"] label:has(input:checked) p{color:#fff!important}
    [data-testid="stRadio"] label::before,[data-testid="stRadio"] label::after{display:none!important;content:none!important}

    /* HOME */
    .home-v2-section{font-size:26px!important;line-height:1.1!important}.home-v2-sub{font-size:16px!important;line-height:1.4!important}
    .home-v2-actions .stButton>button,.home-actions .stButton>button{font-size:15px!important;min-height:44px!important;font-weight:900!important}
    .edge-title,.home-edge-title{font-size:28px!important;line-height:1.1!important}.edge-sub,.home-edge-sub{font-size:16px!important;line-height:1.45!important}
    .edge-card b,.home-v2-card b{font-size:18px!important}.edge-card p,.home-v2-card p{font-size:15.5px!important;line-height:1.45!important}
    .edge-stat b,.home-stat b{font-size:22px!important}

    /* DRAFT + 6 — primary CTA */
    .draft-start-intro{padding:22px!important;border-radius:18px!important}.draft-start-intro b{font-size:30px!important;line-height:1.08!important}.draft-start-intro span{font-size:17px!important;line-height:1.45!important}
    .st-key-start_mock_draft .stButton>button{min-height:64px!important;padding:14px 22px!important;border-radius:16px!important;font-size:21px!important;line-height:1!important;font-weight:950!important;color:#fff!important;background:#d73a45!important;border:1px solid #ef6670!important;box-shadow:0 10px 28px rgba(215,58,69,.26)!important}
    .st-key-start_mock_draft .stButton>button p{font-size:21px!important;font-weight:950!important;color:#fff!important}
    .draft-status,.draft-label{font-size:14px!important}.draft-status b,.draft-player-name,.on-clock-name{font-size:19px!important}.draft-player-meta,.draft-meta{font-size:14px!important}.draft-data b,.draft-stat b{font-size:17px!important}

    /* 5 — scale the whole 2026 Draft Guide, not just its text */
    .guide-toc{gap:11px!important;margin-bottom:18px!important}.guide-section-card{padding:18px!important;border-radius:17px!important;min-height:118px!important}
    .guide-section-card b{font-size:20px!important;line-height:1.15!important}.guide-section-card span{font-size:15px!important;line-height:1.4!important;margin-top:7px!important}.guide-section-card em{font-size:14px!important;margin-top:11px!important}
    .guide-back{font-size:14px!important}.guide-subhead{font-size:27px!important;margin:10px 0 11px!important}
    .rank-row{grid-template-columns:38px 44px minmax(0,1fr)!important;gap:10px!important;padding:14px 13px!important;margin-bottom:8px!important;min-height:72px!important;border-radius:14px!important}
    .rank-n{font-size:15px!important}.rank-name{font-size:18px!important}.pos-chip{font-size:11px!important;padding:5px 3px!important;border-radius:7px!important}.guide-player-link span{font-size:12px!important}
    .st-key-guide_rank_filters .stButton>button{min-height:43px!important;font-size:14px!important;padding:8px 9px!important}
    .strategy-grid{gap:11px!important}.strategy-box{padding:17px!important;border-radius:16px!important}.strategy-box span{font-size:13px!important}.strategy-box b{font-size:18px!important}.rounds{font-size:16px!important;line-height:1.55!important;padding:17px!important}
    .article-grid{gap:11px!important}.article-card{padding:17px!important;border-radius:16px!important}.article-card b{font-size:19px!important}.article-card p{font-size:15.5px!important;line-height:1.48!important}.article-card span{font-size:13px!important}
    .article-body{padding:19px!important}.article-body h3{font-size:27px!important}.article-body p{font-size:17px!important}.player-feature{padding:16px!important;border-radius:15px!important}.player-feature b{font-size:18px!important}.player-feature span{font-size:13px!important}

    /* COACH — larger content + same selected pill treatment */
    .product-tabs,.coach-tabs{gap:8px!important}.product-tabs .stButton>button,.coach-tabs .stButton>button{min-height:50px!important;padding:9px 12px!important;border-radius:12px!important;font-size:15px!important;font-weight:900!important;background:#0d161d!important;border:1px solid var(--shiva-border)!important;color:#aeb9c2!important}
    .product-tabs .stButton>button[kind="primary"],.coach-tabs .stButton>button[kind="primary"]{background:#1a252e!important;border-color:var(--shiva-gold)!important;color:#fff!important}
    .product-hero,.coach-hero{padding:22px!important;border-radius:18px!important}.product-hero h2,.coach-hero h2{font-size:32px!important;line-height:1.08!important}.product-hero p,.coach-hero p{font-size:17px!important;line-height:1.5!important}
    .product-card b,.coach-card b{font-size:18px!important}.product-card p,.coach-card p{font-size:15.5px!important;line-height:1.45!important}

    /* Remove the remaining decorative connection bullet without replacing it. */
    .league-live{font-size:0!important}.league-live::after{content:"ESPN LEAGUE CONNECTED"!important;font-size:13px!important;font-weight:900!important;letter-spacing:.3px!important}

    /* Header contract — keep countdown physically separate from logo. */
    .app-top{position:relative!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;column-gap:10px!important;padding-bottom:7px!important}
    .app-top .brand-wrap{width:auto!important;min-width:0!important;overflow:hidden!important}.app-top .brand-copy{min-width:0!important}.kickoff-compact{position:static!important;align-self:center!important;justify-self:end!important;margin:0!important;max-width:100%!important}

    @media(max-width:560px){
      .screen-head h1{font-size:32px!important}.screen-head p{font-size:17px!important}[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{font-size:16.5px!important}
      [data-testid="stRadio"] label{min-height:41px!important;padding:8px 10px!important}[data-testid="stRadio"] label p{font-size:14.5px!important}
      .home-v2-section{font-size:24px!important}.home-v2-sub{font-size:15.5px!important}.home-v2-actions .stButton>button,.home-actions .stButton>button{font-size:14.5px!important}
      .guide-toc,.strategy-grid,.player-feature-grid{grid-template-columns:1fr 1fr!important}.guide-section-card{min-height:124px!important}.guide-section-card b{font-size:19px!important}.guide-section-card span{font-size:14.5px!important}.rank-name{font-size:17.5px!important}
      .product-tabs .stButton>button,.coach-tabs .stButton>button{min-height:48px!important;font-size:14.5px!important}
      .app-top{column-gap:7px!important}.app-top .brand-wrap{gap:7px!important}.app-top .brand-badge{width:46px!important;height:46px!important;flex:0 0 46px!important}.app-top .brand-title{font-size:23px!important}.app-top .brand-sub{font-size:9.5px!important;white-space:nowrap!important}.kickoff-compact{padding:5px 6px!important;gap:4px!important}.kickoff-compact span{font-size:6.5px!important}.kickoff-compact b{font-size:9px!important}
    }
    </style>
    """
)

components.html(
    r"""
    <script>
    (() => {
      let host, doc;
      try { host = window.parent; doc = host.document; } catch (_) { return; }
      const tick = () => {
        try {
          doc.querySelectorAll('[data-shiva-kickoff]').forEach((clock) => {
            const output = clock.querySelector('b');
            const target = Date.parse(clock.dataset.target || '');
            if (!output || !Number.isFinite(target)) return;
            const total = Math.max(0, Math.floor((target - Date.now()) / 1000));
            if (total === 0) { output.textContent = 'LIVE'; return; }
            const days = Math.floor(total / 86400), hours = Math.floor((total % 86400) / 3600), minutes = Math.floor((total % 3600) / 60), seconds = total % 60;
            const two = (value) => String(value).padStart(2, '0');
            output.textContent = `${two(days)}D ${two(hours)}H ${two(minutes)}M ${two(seconds)}S`;
          });
        } catch (_) {}
      };
      tick();
      const timer = host.setInterval(tick, 1000);
      window.addEventListener('beforeunload', () => host.clearInterval(timer), {once:true});
    })();
    </script>
    """,
    height=0,
    width=0,
)
