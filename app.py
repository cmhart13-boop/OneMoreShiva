"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- app_runtime.py owns the validated transformation/render pipeline.
- hosted Community Cloud chrome is removed through Streamlit's supported embed shell.
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

# Community Cloud renders its owner/hosting controls outside the app DOM. Use the
# platform's supported embed mode as the canonical Shiva shell instead of chasing
# hosted widgets with app-level CSS. The loading screen is disabled and dark mode
# is requested before the production runtime renders.
components.html(
    r"""
    <script>
    (() => {
      try {
        const topWindow = window.top;
        const current = new URL(topWindow.location.href);
        const embedded = current.searchParams.get('embed') === 'true';
        if (!embedded) {
          current.searchParams.set('embed', 'true');
          const options = current.searchParams.getAll('embed_options');
          if (!options.includes('hide_loading_screen')) {
            current.searchParams.append('embed_options', 'hide_loading_screen');
          }
          if (!options.includes('dark_theme')) {
            current.searchParams.append('embed_options', 'dark_theme');
          }
          topWindow.location.replace(current.toString());
          return;
        }
      } catch (_) {}
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
