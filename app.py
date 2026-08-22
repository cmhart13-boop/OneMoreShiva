"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- app_runtime.py owns the validated transformation/render pipeline.
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

# Keep Community Cloud chrome out of the app UI.
st.set_option("client.toolbarMode", "minimal")

import shiva_home_patch  # noqa: E402,F401 - applies the targeted home-screen cleanup after page config

# Hide Streamlit's hosted-app controls/viewer badge without affecting Shiva navigation.
st.html("""
<style>
#MainMenu,
footer,
header[data-testid="stHeader"],
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
[data-testid="stViewerBadge"],
[data-testid="stAppViewerBadge"],
[data-testid*="ViewerBadge"],
[data-testid="stAppCreatorAvatar"],
[data-testid="stAppCreatorAvatarContainer"],
.stAppDeployButton,
.stAppToolbar,
.css-1jc7ptx,
.e1ewe7hr3,
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
.viewerBadge_link__1S137,
.viewerBadge_text__1JaDK,
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="viewer-badge"],
[class*="stDeployButton"],
[class*="stStatusWidget"],
button[title="Manage app"],
button[aria-label="Manage app"],
a[aria-label="Manage app"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"],
div:has(> a[href*="streamlit.io/cloud"]),
div:has(> a[href*="share.streamlit.io"]),
iframe[title*="badge" i],
iframe[title*="manage" i] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    max-width: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
}
</style>
""")

# Community Cloud can remount branded controls after initial render and may change
# their class/test-id names. Shiva intentionally has no floating control in the
# lower-right corner, so enforce that product invariant as a final guardrail.
components.html(
    """
    <script>
    (() => {
      const win = window.parent;
      const doc = win.document;

      const hide = (el) => {
        if (!el || !el.style) return;
        el.style.setProperty('display', 'none', 'important');
        el.style.setProperty('visibility', 'hidden', 'important');
        el.style.setProperty('opacity', '0', 'important');
        el.style.setProperty('pointer-events', 'none', 'important');
        el.style.setProperty('width', '0', 'important');
        el.style.setProperty('height', '0', 'important');
        el.style.setProperty('min-width', '0', 'important');
        el.style.setProperty('min-height', '0', 'important');
        el.style.setProperty('max-width', '0', 'important');
        el.style.setProperty('max-height', '0', 'important');
        el.style.setProperty('overflow', 'hidden', 'important');
      };

      const isShivaNav = (el) => Boolean(
        el.closest && (
          el.closest('.st-key-bottom_nav_shell') ||
          el.closest('.bottom-nav') ||
          el.closest('[class*="bottom_nav_shell"]')
        )
      );

      const sweep = () => {
        const directSelectors = [
          '#MainMenu',
          'footer',
          'header[data-testid="stHeader"]',
          '[data-testid="stStatusWidget"]',
          '[data-testid="stDecoration"]',
          '[data-testid="stToolbar"]',
          '[data-testid="stToolbarActions"]',
          '[data-testid="stDeployButton"]',
          '[data-testid="stAppDeployButton"]',
          '[data-testid="stViewerBadge"]',
          '[data-testid="stAppViewerBadge"]',
          '[data-testid*="ViewerBadge"]',
          '[data-testid*="viewerBadge"]',
          '[data-testid*="ManageApp"]',
          '[class*="viewerBadge"]',
          '[class*="ViewerBadge"]',
          '[class*="viewer-badge"]',
          '[class*="stDeployButton"]',
          '[class*="stStatusWidget"]',
          'button[title="Manage app"]',
          'button[aria-label="Manage app"]',
          'a[aria-label="Manage app"]',
          'iframe[title*="badge" i]',
          'iframe[title*="manage" i]'
        ];
        directSelectors.forEach((selector) => {
          doc.querySelectorAll(selector).forEach(hide);
        });

        doc.querySelectorAll('a[href*="streamlit.io"], a[href*="share.streamlit.io"], a[href*="streamlit.app"]').forEach((link) => {
          let node = link;
          for (let i = 0; i < 6 && node.parentElement; i += 1) {
            const parent = node.parentElement;
            const style = win.getComputedStyle(parent);
            node = parent;
            if (style.position === 'fixed') break;
          }
          hide(node);
          hide(link);
        });

        // Hard kill-switch: no small/high-z fixed widget is permitted in Shiva's
        // lower-right quadrant. This catches future Streamlit badge markup changes.
        doc.body.querySelectorAll('*').forEach((el) => {
          if (isShivaNav(el)) return;
          const style = win.getComputedStyle(el);
          if (style.position !== 'fixed') return;
          const rect = el.getBoundingClientRect();
          if (!rect.width || !rect.height) return;
          const z = Number.parseInt(style.zIndex || '0', 10);
          const inRight = rect.right >= win.innerWidth - 8 && rect.left >= win.innerWidth * 0.58;
          const inBottom = rect.bottom >= win.innerHeight - 8 && rect.top >= win.innerHeight * 0.55;
          const widgetSized = rect.width <= 420 && rect.height <= 420;
          const elevated = Number.isFinite(z) ? z >= 500 : true;
          if (inRight && inBottom && widgetSized && elevated) hide(el);
        });
      };

      sweep();
      const observer = new MutationObserver(sweep);
      observer.observe(doc.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'data-testid', 'aria-label', 'title']
      });
      win.setInterval(sweep, 250);
      win.addEventListener('resize', sweep, { passive: true });
      win.addEventListener('pageshow', sweep, { passive: true });
      doc.addEventListener('visibilitychange', sweep, { passive: true });
    })();
    </script>
    """,
    height=0,
    width=0,
)

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
