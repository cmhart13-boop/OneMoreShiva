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

st.set_option("client.toolbarMode", "minimal")

import shiva_home_patch  # noqa: E402,F401

# Streamlit Community Cloud's "Hosted with Streamlit / Created by" badge lives
# in Cloud chrome rather than normal app markup. The supported way to strip that
# chrome is Streamlit embed mode. Inject the redirect into the parent document so
# every normal app visit transparently upgrades itself to ?embed=true while
# preserving any existing query parameters and hash state.
components.html(
    """
    <script>
    (() => {
      const doc = window.parent.document;
      const script = doc.createElement('script');
      script.textContent = `
        (() => {
          try {
            const url = new URL(window.location.href);
            if (!url.searchParams.has('embed')) {
              url.searchParams.set('embed', 'true');
              window.location.replace(url.toString());
            }
          } catch (_) {}
        })();
      `;
      doc.documentElement.appendChild(script);
      script.remove();
    })();
    </script>
    """,
    height=0,
    width=0,
)

# Also suppress Streamlit's in-app chrome when rendered outside Community Cloud
# (local/dev/self-hosted). This does not touch Shiva navigation or content.
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
[data-testid*="viewerBadge"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
</style>
""")

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
