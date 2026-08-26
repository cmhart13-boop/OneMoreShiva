"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- app_runtime.py owns the validated transformation/render pipeline.
- The shell controller is idempotent and never navigates/reloads the app.
- Hosted Streamlit chrome and the live kickoff clock are controlled from the parent DOM.
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

# The prior bootstrap attempted to redirect the top window into Streamlit embed mode.
# On iOS that creates a second document load, which can replay startup state and produce
# the observed Home -> splash -> Home sequence. Keep one document/session instead and
# own only the parent-DOM behavior Streamlit does not expose as a native API.
components.html(
    r"""
    <script>
    (() => {
      let host;
      let doc;
      try {
        host = window.parent;
        doc = host.document;
      } catch (_) {
        return;
      }

      try {
        if (host.__shivaShellController && host.__shivaShellController.dispose) {
          host.__shivaShellController.dispose();
        }
      } catch (_) {}

      const chromeSelectors = [
        '#MainMenu', 'footer', 'header[data-testid="stHeader"]',
        '[data-testid="stHeader"]', '[data-testid="stToolbar"]',
        '[data-testid="stToolbarActions"]', '[data-testid="stAppToolbar"]',
        '[data-testid="stStatusWidget"]', '[data-testid="stDecoration"]',
        '[data-testid="stDeployButton"]', '[data-testid="stAppDeployButton"]',
        '[data-testid="stViewerBadge"]', '[data-testid="stAppViewerBadge"]',
        '[data-testid*="ViewerBadge"]', '[data-testid*="viewerBadge"]',
        '[data-testid="stAppCreatorAvatar"]', '[data-testid="stAppCreatorAvatarContainer"]',
        '.stAppDeployButton', '.stAppToolbar', '[class*="viewerBadge"]',
        '[class*="ViewerBadge"]', '[class*="viewer-badge"]', '[class*="stDeployButton"]',
        'button[title="Manage app"]', 'button[aria-label="Manage app"]',
        'a[title="Manage app"]', 'a[aria-label="Manage app"]'
      ];

      const protectedNav = (el) => {
        try { return !!(el && el.closest && el.closest('.st-key-bottom_nav_shell')); }
        catch (_) { return false; }
      };

      const hide = (el) => {
        if (!el || !el.style || protectedNav(el)) return;
        for (const [name, value] of [
          ['display','none'], ['visibility','hidden'], ['opacity','0'],
          ['pointer-events','none'], ['width','0'], ['height','0'],
          ['min-width','0'], ['min-height','0'], ['max-width','0'],
          ['max-height','0'], ['overflow','hidden']
        ]) el.style.setProperty(name, value, 'important');
        el.setAttribute('aria-hidden', 'true');
      };

      const looksLikeHostedChrome = (el) => {
        if (!el || protectedNav(el)) return false;
        try {
          const link = el.matches && el.matches('a[href]') ? el : el.querySelector && el.querySelector('a[href]');
          const signal = [
            el.getAttribute && el.getAttribute('data-testid'),
            el.getAttribute && el.getAttribute('class'),
            el.getAttribute && el.getAttribute('id'),
            el.getAttribute && el.getAttribute('title'),
            el.getAttribute && el.getAttribute('aria-label'),
            el.getAttribute && el.getAttribute('href'),
            el.textContent,
            link && link.getAttribute('href')
          ].filter(Boolean).join(' ').toLowerCase();
          return signal.includes('streamlit') || signal.includes('manage app') ||
                 signal.includes('hosted with') || signal.includes('created by') ||
                 signal.includes('share.streamlit.io');
        } catch (_) { return false; }
      };

      const updateKickoff = () => {
        try {
          doc.querySelectorAll('[data-shiva-kickoff]').forEach((clock) => {
            const output = clock.querySelector('b');
            const target = Date.parse(clock.dataset.target || '');
            if (!output || !Number.isFinite(target)) return;
            const total = Math.max(0, Math.floor((target - Date.now()) / 1000));
            if (total === 0) {
              output.textContent = 'LIVE';
              return;
            }
            const days = Math.floor(total / 86400);
            const hours = Math.floor((total % 86400) / 3600);
            const minutes = Math.floor((total % 3600) / 60);
            const seconds = total % 60;
            const two = (value) => String(value).padStart(2, '0');
            output.textContent = `${two(days)}D ${two(hours)}H ${two(minutes)}M ${two(seconds)}S`;
          });
        } catch (_) {}
      };

      const sweep = () => {
        for (const selector of chromeSelectors) {
          try { doc.querySelectorAll(selector).forEach(hide); } catch (_) {}
        }
        try {
          doc.querySelectorAll('a[href], button, [role="button"]').forEach((el) => {
            if (!looksLikeHostedChrome(el)) return;
            let node = el;
            for (let i = 0; i < 4 && node.parentElement && !protectedNav(node.parentElement); i++) {
              const parent = node.parentElement;
              const style = doc.defaultView.getComputedStyle(parent);
              const rect = parent.getBoundingClientRect();
              if (['fixed','sticky','absolute'].includes(style.position) && rect.width <= 460 && rect.height <= 280 && looksLikeHostedChrome(parent)) node = parent;
              else break;
            }
            hide(node);
          });
        } catch (_) {}
        updateKickoff();
      };

      const styleId = 'shiva-production-shell-style';
      let style = doc.getElementById(styleId);
      if (!style) {
        style = doc.createElement('style');
        style.id = styleId;
        (doc.head || doc.documentElement).appendChild(style);
      }
      style.textContent = `
        ${chromeSelectors.join(',\n')}{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;width:0!important;height:0!important;min-width:0!important;min-height:0!important;max-width:0!important;max-height:0!important;overflow:hidden!important}
        html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"]{background:#071019!important;color-scheme:dark!important}
        .app-top{position:relative!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;column-gap:10px!important;padding-bottom:7px!important}
        .app-top .brand-wrap{width:auto!important;min-width:0!important;overflow:hidden!important}
        .app-top .brand-copy{min-width:0!important}
        .kickoff-compact{position:static!important;top:auto!important;right:auto!important;align-self:center!important;justify-self:end!important;flex:0 0 auto!important;margin:0!important;max-width:100%!important}
        .shiva-startup-splash{animation:shivaSplashGone .28s ease 2.32s forwards!important;will-change:opacity!important}
        @keyframes shivaSplashGone{from{opacity:1;visibility:visible}to{opacity:0;visibility:hidden}}
        @media(max-width:520px){
          .app-top{column-gap:7px!important}
          .app-top .brand-wrap{gap:7px!important}
          .app-top .brand-badge{width:46px!important;height:46px!important;flex:0 0 46px!important}
          .app-top .brand-title{font-size:23px!important;line-height:1!important}
          .app-top .brand-sub{font-size:9.5px!important;letter-spacing:.35px!important;white-space:nowrap!important}
          .kickoff-compact{padding:5px 6px!important;gap:4px!important}
          .kickoff-compact span{font-size:6.5px!important}
          .kickoff-compact b{font-size:9px!important;letter-spacing:0!important}
        }
      `;

      sweep();
      const observer = new MutationObserver(sweep);
      observer.observe(doc.documentElement, {childList:true, subtree:true});
      const interval = host.setInterval(sweep, 1000);
      host.__shivaShellController = {
        dispose: () => {
          try { observer.disconnect(); } catch (_) {}
          try { host.clearInterval(interval); } catch (_) {}
        }
      };
    })();
    </script>
    """,
    height=0,
    width=0,
)

import shiva_controls  # noqa: E402,F401


def _shiva_compile(source, filename, mode, *args, **kwargs):
    """Keep inspect/Streamlit cache source lookups aligned with transformed app_core."""
    if isinstance(source, str) and str(filename).endswith("app_core.py"):
        virtual = "<shiva_transformed_app_core>"
        linecache.cache[virtual] = (
            len(source),
            None,
            source.splitlines(keepends=True),
            virtual,
        )
        return builtins.compile(source, virtual, mode, *args, **kwargs)
    return builtins.compile(source, filename, mode, *args, **kwargs)


compile = _shiva_compile
runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
