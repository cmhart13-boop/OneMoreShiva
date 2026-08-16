"""One More Shiva launch bootstrap.

Install a permanent dark browser shell before the production runtime executes. The
shell lives in the parent document head (not the Streamlit render tree), so reruns and
page changes cannot tear it down and briefly expose a white document.
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

# First Python paint: keep every Streamlit surface dark immediately.
st.markdown(
    """
    <style>
    html, body, #root, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"], .stApp {
        background: #071019 !important;
        color-scheme: dark !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    *, *::before, *::after {
        -webkit-tap-highlight-color: transparent !important;
    }
    button, a, label, input, [role="button"], [role="tab"] {
        -webkit-tap-highlight-color: transparent !important;
    }
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewContainer"] section,
    .main, .block-container {
        background: #071019 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Permanent browser-level protection. This style node is injected into the host
# document <head>, outside Streamlit's replaceable app tree, and survives reruns.
components.html(
    """
    <script>
    (() => {
      let doc;
      try { doc = window.top.document; } catch (_) { doc = window.parent.document; }
      if (!doc) return;

      const BG = '#071019';
      doc.documentElement.style.setProperty('background', BG, 'important');
      doc.documentElement.style.setProperty('background-color', BG, 'important');
      doc.documentElement.style.setProperty('color-scheme', 'dark', 'important');
      if (doc.body) {
        doc.body.style.setProperty('background', BG, 'important');
        doc.body.style.setProperty('background-color', BG, 'important');
      }

      let meta = doc.querySelector('meta[name="theme-color"]');
      if (!meta) {
        meta = doc.createElement('meta');
        meta.setAttribute('name', 'theme-color');
        doc.head.appendChild(meta);
      }
      meta.setAttribute('content', BG);

      if (!doc.getElementById('shiva-permanent-no-flash')) {
        const style = doc.createElement('style');
        style.id = 'shiva-permanent-no-flash';
        style.textContent = `
          html, body, #root,
          [data-testid="stApp"], [data-testid="stAppViewContainer"],
          [data-testid="stMain"], [data-testid="stMainBlockContainer"], .stApp,
          [data-testid="stAppViewContainer"] > .main,
          [data-testid="stAppViewContainer"] section,
          .main, .block-container {
            background-color: ${BG} !important;
            color-scheme: dark !important;
          }
          html, body { background: ${BG} !important; overscroll-behavior-y: none !important; }
          *, *::before, *::after {
            -webkit-tap-highlight-color: transparent !important;
          }
          button, a, label, input, select, textarea,
          [role="button"], [role="tab"], [role="radio"], [role="option"] {
            -webkit-tap-highlight-color: transparent !important;
          }
          button:focus, a:focus, label:focus, [role="button"]:focus {
            outline-color: transparent !important;
          }
          [data-testid="stAppViewContainer"] {
            transition: none !important;
          }
        `;
        doc.head.appendChild(style);
      }

      // Streamlit can replace root descendants during a rerun. Reassert only the
      // background properties when that happens; never touch layout/content.
      if (!window.top.__shivaNoFlashObserver) {
        const paint = () => {
          doc.documentElement.style.setProperty('background-color', BG, 'important');
          if (doc.body) doc.body.style.setProperty('background-color', BG, 'important');
          const app = doc.querySelector('[data-testid="stAppViewContainer"]');
          if (app) app.style.setProperty('background-color', BG, 'important');
        };
        const observer = new MutationObserver(paint);
        observer.observe(doc.documentElement, { childList: true, subtree: true });
        window.top.__shivaNoFlashObserver = observer;
      }
    })();
    </script>
    """,
    height=0,
    width=0,
)

_boot_slot = None
if not st.session_state.get("_shiva_bootstrap_painted", False):
    st.session_state["_shiva_bootstrap_painted"] = True
    _boot_slot = st.empty()
    _boot_slot.markdown(
        """
        <style>
        .shiva-launch-paint {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100dvh;
            z-index: 2147483646;
            background: #071019;
            pointer-events: none;
            -webkit-tap-highlight-color: transparent;
        }
        </style>
        <div class="shiva-launch-paint" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")

# app_runtime.py preserves the previous production entrypoint byte-for-byte. Since
# page config is now deliberately the very first Streamlit command above, remove the
# later duplicate page-config call from the app_core source before that runtime executes.
_read_core = 'code = core.read_text(encoding="utf-8")'
_runtime_patch = _read_core + "\ncode = code.replace('st.set_page_config(page_title=\"One More Shiva\", page_icon=\"🏆\", layout=\"wide\", initial_sidebar_state=\"collapsed\")', '')"
runtime = runtime.replace(_read_core, _runtime_patch, 1)

exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())

if _boot_slot is not None:
    _boot_slot.empty()
