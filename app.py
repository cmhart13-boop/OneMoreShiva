"""One More Shiva production bootstrap.

This file owns only page configuration and startup presentation. The validated
app_runtime.py pipeline remains unchanged.
"""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SPLASH_SECONDS = 2.5

# Paint Shiva dark as the first app-owned UI instruction. Style-only st.html does not
# create a visible layout block or reintroduce the protected top gutter.
EARLY_SHELL_STYLE = """<style id="shiva-early-shell">
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:#071019!important;
  background-color:#071019!important;
  color-scheme:dark!important;
}
#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stStatusWidget"],[data-testid="stDecoration"],[data-testid="stDeployButton"],
.stAppDeployButton,[data-testid="stAppViewerBadge"],[data-testid="stViewerBadge"],
[data-testid="stAppCreatorBadge"],[class*="viewerBadge"],[class*="ViewerBadge"]{
  display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;
}
</style>"""
st.html(EARLY_SHELL_STYLE)


def _crisp_splash_style(data_uri: str) -> str:
    return f"""<style id="shiva-crisp-splash">
body::before{{
  content:"";position:fixed;inset:0;width:100vw;height:100dvh;z-index:2147483647;
  pointer-events:none;background-color:#071019;background-image:url('{data_uri}');
  background-repeat:no-repeat;background-position:center;background-size:min(52vw,225px) auto;
  animation:shivaCrispSplashGone 0s linear {SPLASH_SECONDS}s forwards;
}}
@keyframes shivaCrispSplashGone{{to{{opacity:0;visibility:hidden}}}}
</style>"""


# High-resolution splash is fail-safe. If asset preparation fails for any reason, do
# not claim splash ownership; the existing validated runtime splash renders instead.
_show_splash = not st.query_params.get("page") and not st.session_state.get("_shiva_startup_splash_seen", False)
if _show_splash:
    try:
        from shiva_splash import splash_data_uri
        _splash_uri = splash_data_uri()
    except Exception:
        _splash_uri = None

    if _splash_uri:
        st.html(_crisp_splash_style(_splash_uri))
        st.session_state["_shiva_startup_splash_seen"] = True

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())

# Community Cloud hosting badge suppression. No redirect, no URL mutation, no app-state
# mutation. It searches only Streamlit-hosting links/fixed overlays and self-disconnects.
components.html(
    """
    <script>
    (() => {
      let doc;
      try { doc = window.top.document; }
      catch (_) { try { doc = window.parent.document; } catch (_) { return; } }

      const hide = (node) => {
        if (!node) return;
        node.style.setProperty('display','none','important');
        node.style.setProperty('visibility','hidden','important');
        node.style.setProperty('opacity','0','important');
        node.style.setProperty('pointer-events','none','important');
      };

      const sweep = () => {
        doc.querySelectorAll('[data-testid="stAppViewerBadge"],[data-testid="stViewerBadge"],[data-testid="stAppCreatorBadge"],[class*="viewerBadge"],[class*="ViewerBadge"]').forEach(hide);
        doc.querySelectorAll('a[href*="streamlit.io"],a[href*="streamlit.app"]').forEach((link) => {
          const label = `${link.textContent || ''} ${link.getAttribute('aria-label') || ''} ${link.getAttribute('title') || ''}`.toLowerCase();
          if (!label.includes('streamlit')) return;
          let node = link;
          for (let i = 0; i < 7 && node; i += 1, node = node.parentElement) {
            const style = window.top.getComputedStyle(node);
            if (style.position === 'fixed' || style.position === 'sticky') { hide(node); break; }
          }
        });
      };

      sweep();
      const observer = new MutationObserver(sweep);
      observer.observe(doc.documentElement,{childList:true,subtree:true});
      window.setTimeout(() => observer.disconnect(),15000);
    })();
    </script>
    """,
    height=0,
    width=0,
    scrolling=False,
)
