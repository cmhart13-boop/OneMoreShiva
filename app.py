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
[data-testid*="viewerBadge"],
[data-testid="stAppCreatorAvatar"],
[data-testid="stAppCreatorAvatarContainer"],
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="viewer-badge"],
[class*="stDeployButton"],
[class*="stStatusWidget"],
button[title="Manage app"],
button[aria-label="Manage app"],
a[aria-label="Manage app"],
a[href*="streamlit.io"],
a[href*="share.streamlit.io"],
a[href*="streamlit.app"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
</style>
""")

# Streamlit Community Cloud mounts its creator/hosting badge outside the normal
# app content and can remount it after navigation. Remove only elements that
# identify themselves as Streamlit/hosting chrome; never use geometry, z-index,
# or position heuristics so Shiva's own controls cannot be collateral damage.
components.html(
    """
    <script>
    (() => {
      const win = window.parent;
      const doc = win.document;

      const remove = (el) => {
        if (!el || !el.remove) return;
        el.remove();
      };

      const sweep = () => {
        const selectors = [
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
          '[data-testid="stAppCreatorAvatar"]',
          '[data-testid="stAppCreatorAvatarContainer"]',
          '[class*="viewerBadge"]',
          '[class*="ViewerBadge"]',
          '[class*="viewer-badge"]',
          '[class*="stDeployButton"]',
          '[class*="stStatusWidget"]',
          'button[title="Manage app"]',
          'button[aria-label="Manage app"]',
          'a[aria-label="Manage app"]'
        ];
        selectors.forEach((selector) => {
          doc.querySelectorAll(selector).forEach(remove);
        });

        doc.querySelectorAll('a').forEach((link) => {
          const href = (link.getAttribute('href') || '').toLowerCase();
          const text = (link.textContent || '').toLowerCase();
          const aria = (link.getAttribute('aria-label') || '').toLowerCase();
          const title = (link.getAttribute('title') || '').toLowerCase();
          const branded =
            href.includes('streamlit.io') ||
            href.includes('share.streamlit.io') ||
            href.includes('streamlit.app') ||
            text.includes('hosted with streamlit') ||
            text.includes('made with streamlit') ||
            text.includes('created with streamlit') ||
            aria.includes('streamlit') ||
            title.includes('streamlit');
          if (!branded) return;

          let node = link;
          for (let i = 0; i < 8 && node.parentElement; i += 1) {
            const parent = node.parentElement;
            const parentText = (parent.textContent || '').toLowerCase();
            node = parent;
            if (parentText.includes('streamlit') || win.getComputedStyle(parent).position === 'fixed') {
              continue;
            }
            break;
          }
          remove(node);
          remove(link);
        });

        // Some Community Cloud badge versions are buttons/divs rather than links.
        // Match only explicit Streamlit branding text so app content is untouched.
        doc.querySelectorAll('button, div, span').forEach((el) => {
          if (el.children.length > 4) return;
          const text = (el.textContent || '').trim().toLowerCase();
          const aria = (el.getAttribute('aria-label') || '').toLowerCase();
          const title = (el.getAttribute('title') || '').toLowerCase();
          if (
            text === 'hosted with streamlit' ||
            text === 'made with streamlit' ||
            text === 'created with streamlit' ||
            aria.includes('streamlit') ||
            title.includes('streamlit')
          ) {
            remove(el);
          }
        });
      };

      sweep();
      const observer = new MutationObserver(sweep);
      observer.observe(doc.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'data-testid', 'aria-label', 'title', 'href']
      });
      win.setInterval(sweep, 300);
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
