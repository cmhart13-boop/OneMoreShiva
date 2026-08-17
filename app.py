"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- The hosted-page bootstrap is a zero-height component and immediately removes its own wrapper.
- The bootstrap normalizes Community Cloud into dark, footer-free embed presentation.
- The approved high-resolution trophy owns the startup splash.
- app_runtime.py remains unchanged and owns the validated application runtime.
"""
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import html as _bootstrap_html

from shiva_splash import splash_data_uri

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SPLASH_SECONDS = 2.5


def _host_bootstrap_markup(trophy_uri: str) -> str:
    """Return the isolated hosted-page bootstrap used before the app runtime."""
    return f"""
    <script>
    (() => {{
      let topWindow;
      let doc;
      try {{
        topWindow = window.top;
        doc = topWindow.document;
      }} catch (_) {{
        topWindow = window.parent;
        doc = topWindow.document;
      }}

      const frame = window.frameElement;
      if (frame) {{
        let wrapper = frame;
        for (let i = 0; i < 6 && wrapper; i += 1, wrapper = wrapper.parentElement) {{
          const testId = wrapper.getAttribute && wrapper.getAttribute('data-testid');
          if (testId === 'stElementContainer' || testId === 'stIFrame') {{
            wrapper.style.setProperty('display', 'none', 'important');
            wrapper.style.setProperty('height', '0', 'important');
            wrapper.style.setProperty('min-height', '0', 'important');
            wrapper.style.setProperty('margin', '0', 'important');
            wrapper.style.setProperty('padding', '0', 'important');
          }}
        }}
      }}

      const dark = '#071019';
      doc.documentElement.style.setProperty('background-color', dark, 'important');
      if (doc.body) doc.body.style.setProperty('background-color', dark, 'important');

      const url = new URL(topWindow.location.href);
      if (url.searchParams.get('embed') !== 'true') {{
        url.searchParams.delete('embed_options');
        url.searchParams.set('embed', 'true');
        url.searchParams.append('embed_options', 'dark_theme');
        url.searchParams.append('embed_options', 'hide_loading_screen');
        topWindow.location.replace(url.toString());
        return;
      }}

      if (doc.getElementById('shiva-startup-splash-v2')) return;

      const splash = doc.createElement('div');
      splash.id = 'shiva-startup-splash-v2';
      splash.setAttribute('aria-hidden', 'true');
      splash.style.cssText = [
        'position:fixed',
        'inset:0',
        'width:100vw',
        'height:100dvh',
        'z-index:2147483647',
        'display:flex',
        'align-items:center',
        'justify-content:center',
        'overflow:hidden',
        'pointer-events:none',
        'background:{dark}'
      ].join(';');

      const trophy = doc.createElement('img');
      trophy.src = {trophy_uri!r};
      trophy.alt = 'THE SHIVA trophy';
      trophy.style.cssText = [
        'display:block',
        'width:min(52vw,225px)',
        'height:auto',
        'max-height:52vh',
        'object-fit:contain',
        'object-position:center',
        'filter:none',
        'transform:none'
      ].join(';');

      splash.appendChild(trophy);
      doc.body.appendChild(splash);
      topWindow.setTimeout(() => splash.remove(), {int(SPLASH_SECONDS * 1000)});
    }})();
    </script>
    """


# The component runs in the host page, then removes its own Streamlit wrapper. Community
# Cloud's embed presentation removes the hosted footer/chrome and loading skeleton.
_bootstrap_html(_host_bootstrap_markup(splash_data_uri()), height=0, width=0, scrolling=False)

# app_runtime.py retains its historical splash contract for safety, but the bootstrap
# above is the single startup-splash owner.
st.session_state["_shiva_startup_splash_seen"] = True

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
