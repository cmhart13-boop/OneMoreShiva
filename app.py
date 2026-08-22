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

# Keep Streamlit's normal app toolbar minimal. Community Cloud's lower-right
# "Manage app" control is separate chrome and is handled below.
st.set_option("client.toolbarMode", "minimal")

import shiva_home_patch  # noqa: E402,F401

# One durable Streamlit-chrome suppression layer.
#
# The old approach combined an embed-mode redirect with a second CSS hide. That
# could still allow Community Cloud chrome to paint before the redirect and left
# two separate mechanisms to maintain. This block instead injects the hide rules
# directly into the parent Streamlit document, handles the current Streamlit
# test IDs/classes, and keeps watching for Community Cloud controls that mount
# after the app has rendered.
#
# IMPORTANT: the One More Shiva bottom navigation is explicitly exempted from
# every JavaScript fallback below.
components.html(
    r"""
    <script>
    (() => {
      const documents = [];
      for (const win of [window.parent, window.top]) {
        try {
          if (win && win.document && !documents.includes(win.document)) {
            documents.push(win.document);
          }
        } catch (_) {}
      }

      const STREAMLIT_SELECTORS = [
        '#MainMenu',
        'footer',
        'header[data-testid="stHeader"]',
        '[data-testid="stHeader"]',
        '[data-testid="stToolbar"]',
        '[data-testid="stToolbarActions"]',
        '[data-testid="stAppToolbar"]',
        '[data-testid="stStatusWidget"]',
        '[data-testid="stDecoration"]',
        '[data-testid="stDeployButton"]',
        '[data-testid="stAppDeployButton"]',
        '[data-testid="stViewerBadge"]',
        '[data-testid="stAppViewerBadge"]',
        '[data-testid*="ViewerBadge"]',
        '[data-testid*="viewerBadge"]',
        '[data-testid="stAppCreatorAvatar"]',
        '[data-testid="stAppCreatorAvatarContainer"]',
        '.stAppDeployButton',
        '.stAppToolbar',
        '[class*="viewerBadge"]',
        '[class*="ViewerBadge"]',
        '[class*="viewer-badge"]',
        '[class*="stDeployButton"]',
        'button[title="Manage app"]',
        'button[aria-label="Manage app"]',
        'a[title="Manage app"]',
        'a[aria-label="Manage app"]'
      ];

      const STYLE_ID = 'shiva-streamlit-chrome-suppression';
      const STYLE_TEXT = `
        ${STREAMLIT_SELECTORS.join(',\n')} {
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
      `;

      const isShivaNav = (el) => {
        try {
          return Boolean(el && el.closest && el.closest('.st-key-bottom_nav_shell'));
        } catch (_) {
          return false;
        }
      };

      const hide = (el) => {
        if (!el || !el.style || isShivaNav(el)) return;
        el.style.setProperty('display', 'none', 'important');
        el.style.setProperty('visibility', 'hidden', 'important');
        el.style.setProperty('opacity', '0', 'important');
        el.style.setProperty('pointer-events', 'none', 'important');
        el.setAttribute('aria-hidden', 'true');
      };

      const streamlitSignal = (el) => {
        if (!el || isShivaNav(el)) return false;
        let haystack = '';
        try {
          const attrs = [
            el.getAttribute('data-testid'),
            el.getAttribute('class'),
            el.getAttribute('id'),
            el.getAttribute('title'),
            el.getAttribute('aria-label'),
            el.getAttribute('href'),
            el.textContent
          ];
          haystack = attrs.filter(Boolean).join(' ').toLowerCase();
          const link = el.matches && el.matches('a') ? el : el.querySelector && el.querySelector('a[href]');
          if (link) haystack += ' ' + String(link.getAttribute('href') || '').toLowerCase();
          if (el.outerHTML) haystack += ' ' + el.outerHTML.slice(0, 6000).toLowerCase();
        } catch (_) {}
        return (
          haystack.includes('streamlit') ||
          haystack.includes('manage app') ||
          haystack.includes('hosted with') ||
          haystack.includes('created by') ||
          haystack.includes('share.streamlit.io')
        );
      };

      const hideSemanticFloatingChrome = (doc) => {
        const viewportW = doc.defaultView ? doc.defaultView.innerWidth : window.innerWidth;
        const viewportH = doc.defaultView ? doc.defaultView.innerHeight : window.innerHeight;
        doc.querySelectorAll('body *').forEach((el) => {
          if (isShivaNav(el) || !streamlitSignal(el)) return;
          let style, rect;
          try {
            style = doc.defaultView.getComputedStyle(el);
            rect = el.getBoundingClientRect();
          } catch (_) {
            return;
          }
          const floating = style.position === 'fixed' || style.position === 'sticky' || style.position === 'absolute';
          const lowerRight = rect.right >= viewportW * 0.55 && rect.bottom >= viewportH * 0.55;
          const compact = rect.width <= 360 && rect.height <= 220;
          if (floating && lowerRight && compact) {
            let node = el;
            for (let i = 0; i < 4 && node.parentElement && !isShivaNav(node.parentElement); i += 1) {
              const parent = node.parentElement;
              let parentStyle, parentRect;
              try {
                parentStyle = doc.defaultView.getComputedStyle(parent);
                parentRect = parent.getBoundingClientRect();
              } catch (_) {
                break;
              }
              const parentFloating = parentStyle.position === 'fixed' || parentStyle.position === 'sticky' || parentStyle.position === 'absolute';
              const parentCompact = parentRect.width <= 420 && parentRect.height <= 260;
              if (parentFloating && parentCompact && streamlitSignal(parent)) node = parent;
              else break;
            }
            hide(node);
          }
        });
      };

      const sweep = (doc) => {
        STREAMLIT_SELECTORS.forEach((selector) => {
          try {
            doc.querySelectorAll(selector).forEach(hide);
          } catch (_) {}
        });

        // Community Cloud's lower-right control can be rendered as a link/button
        // whose generated class changes. Catch it semantically without touching
        // arbitrary Shiva UI.
        try {
          doc.querySelectorAll('a[href], button, [role="button"]').forEach((el) => {
            if (streamlitSignal(el)) hide(el);
          });
        } catch (_) {}

        hideSemanticFloatingChrome(doc);
      };

      documents.forEach((doc) => {
        try {
          if (!doc.getElementById(STYLE_ID)) {
            const style = doc.createElement('style');
            style.id = STYLE_ID;
            style.textContent = STYLE_TEXT;
            (doc.head || doc.documentElement).appendChild(style);
          }
          sweep(doc);
          const observer = new MutationObserver(() => sweep(doc));
          observer.observe(doc.documentElement, { childList: true, subtree: true, attributes: true });
          // Community Cloud occasionally mounts its control after the initial DOM
          // mutations have settled. A low-frequency sweep closes that gap.
          window.setInterval(() => sweep(doc), 1000);
        } catch (_) {}
      });
    })();
    </script>
    """,
    height=0,
    width=0,
)

# Native app-document fallback for local/self-hosted Streamlit and for the first
# render before the component observer begins. These selectors are intentionally
# limited to Streamlit chrome and do not match .st-key-bottom_nav_shell.
st.html(
    """
    <style id="shiva-streamlit-native-fallback">
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
    </style>
    """
)

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
