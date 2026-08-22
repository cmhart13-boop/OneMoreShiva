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

# Keep native Streamlit toolbar chrome minimal. Community Cloud's lower-right
# "Manage app" / hosted badge is separate chrome and is suppressed below.
st.set_option("client.toolbarMode", "minimal")

import shiva_home_patch  # noqa: E402,F401

# Current Streamlit chrome selectors used by this deployment. Keep this list
# specific to Streamlit-owned UI; Shiva's .st-key-bottom_nav_shell is not matched.
_STREAMLIT_CHROME_CSS = r"""
#MainMenu,
footer,
header[data-testid="stHeader"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stAppToolbar"],
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
[data-testid="stViewerBadge"],
[data-testid="stAppViewerBadge"],
[data-testid*="ViewerBadge"],
[data-testid*="viewerBadge"],
[data-testid="stAppCreatorAvatar"],
[data-testid="stAppCreatorAvatarContainer"],
.stAppDeployButton,
.stAppToolbar,
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="viewer-badge"],
[class*="stDeployButton"],
button[title="Manage app"],
button[aria-label="Manage app"],
a[title="Manage app"],
a[aria-label="Manage app"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    max-width: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
}
"""

# First-render/native-document fallback. This covers local/self-hosted Streamlit
# and standard app chrome before the Community Cloud observer starts.
st.html(f'<style id="shiva-streamlit-native-fallback">{_STREAMLIT_CHROME_CSS}</style>')

# Community Cloud can mount its lower-right control after the app DOM has loaded,
# and generated class names may change across Streamlit releases. Inject the same
# explicit selectors into the parent document, then watch for late mounts. A
# semantic fallback only removes interactive/floating elements that identify
# themselves as Streamlit, "Manage app", "Hosted with", or "Created by".
# The Shiva bottom toolbar is explicitly protected in every removal path.
components.html(
    r"""
    <script>
    (() => {
      const docs = [];
      for (const win of [window.parent, window.top]) {
        try {
          if (win && win.document && !docs.includes(win.document)) docs.push(win.document);
        } catch (_) {}
      }

      const selectors = [
        '#MainMenu', 'footer', 'header[data-testid="stHeader"]',
        '[data-testid="stHeader"]', '[data-testid="stToolbar"]',
        '[data-testid="stToolbarActions"]', '[data-testid="stAppToolbar"]',
        '[data-testid="stStatusWidget"]', '[data-testid="stDecoration"]',
        '[data-testid="stDeployButton"]', '[data-testid="stAppDeployButton"]',
        '[data-testid="stViewerBadge"]', '[data-testid="stAppViewerBadge"]',
        '[data-testid*="ViewerBadge"]', '[data-testid*="viewerBadge"]',
        '[data-testid="stAppCreatorAvatar"]',
        '[data-testid="stAppCreatorAvatarContainer"]',
        '.stAppDeployButton', '.stAppToolbar', '[class*="viewerBadge"]',
        '[class*="ViewerBadge"]', '[class*="viewer-badge"]',
        '[class*="stDeployButton"]', 'button[title="Manage app"]',
        'button[aria-label="Manage app"]', 'a[title="Manage app"]',
        'a[aria-label="Manage app"]'
      ];

      const protectedNav = (el) => {
        try { return !!(el && el.closest && el.closest('.st-key-bottom_nav_shell')); }
        catch (_) { return false; }
      };

      const hide = (el) => {
        if (!el || !el.style || protectedNav(el)) return;
        el.style.setProperty('display', 'none', 'important');
        el.style.setProperty('visibility', 'hidden', 'important');
        el.style.setProperty('opacity', '0', 'important');
        el.style.setProperty('pointer-events', 'none', 'important');
        el.setAttribute('aria-hidden', 'true');
      };

      const signal = (el) => {
        if (!el || protectedNav(el)) return false;
        try {
          const link = el.matches('a[href]') ? el : el.querySelector('a[href]');
          const parts = [
            el.getAttribute('data-testid'), el.getAttribute('class'),
            el.getAttribute('id'), el.getAttribute('title'),
            el.getAttribute('aria-label'), el.getAttribute('href'),
            el.textContent, link && link.getAttribute('href'),
            el.outerHTML && el.outerHTML.slice(0, 5000)
          ].filter(Boolean).join(' ').toLowerCase();
          return parts.includes('streamlit') || parts.includes('manage app') ||
                 parts.includes('hosted with') || parts.includes('created by') ||
                 parts.includes('share.streamlit.io');
        } catch (_) { return false; }
      };

      const sweep = (doc) => {
        for (const selector of selectors) {
          try { doc.querySelectorAll(selector).forEach(hide); } catch (_) {}
        }

        // Handle generated Community Cloud wrappers without relying on one class.
        try {
          doc.querySelectorAll('a[href], button, [role="button"]').forEach((el) => {
            if (!signal(el) || protectedNav(el)) return;
            let node = el;
            for (let i = 0; i < 4 && node.parentElement && !protectedNav(node.parentElement); i++) {
              const parent = node.parentElement;
              const style = doc.defaultView.getComputedStyle(parent);
              const rect = parent.getBoundingClientRect();
              const floating = ['fixed', 'sticky', 'absolute'].includes(style.position);
              const compact = rect.width <= 420 && rect.height <= 260;
              if (floating && compact && signal(parent)) node = parent;
              else break;
            }
            hide(node);
          });
        } catch (_) {}
      };

      for (const doc of docs) {
        try {
          const styleId = 'shiva-streamlit-parent-suppression';
          if (!doc.getElementById(styleId)) {
            const style = doc.createElement('style');
            style.id = styleId;
            style.textContent = selectors.join(',\n') +
              '{display:none!important;visibility:hidden!important;opacity:0!important;' +
              'pointer-events:none!important;width:0!important;height:0!important;' +
              'min-width:0!important;min-height:0!important;max-width:0!important;' +
              'max-height:0!important;overflow:hidden!important}';
            (doc.head || doc.documentElement).appendChild(style);
          }
          sweep(doc);
          const observer = new MutationObserver(() => sweep(doc));
          observer.observe(doc.documentElement, {childList:true, subtree:true});
          window.setInterval(() => sweep(doc), 1000);
        } catch (_) {}
      }
    })();
    </script>
    """,
    height=0,
    width=0,
)

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
