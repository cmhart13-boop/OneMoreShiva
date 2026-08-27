"""One More Shiva production bootstrap.

The browser shell is established before the application runtime is allowed to render.
That keeps startup to one visible state: Shiva splash -> Home. The Streamlit embed shell
is entered before app content renders, so Community Cloud chrome never becomes part of
the visible app surface.
"""
from pathlib import Path
import base64
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

# -----------------------------------------------------------------------------
# CANONICAL BROWSER SHELL
# -----------------------------------------------------------------------------
# Streamlit Community Cloud's creator/hosting controls live outside the application
# surface. The supported embed shell removes them cleanly. The important part is that
# we must enter that shell *before* app_runtime renders anything; redirecting after Home
# has already painted is what caused the Home -> splash -> Home replay on iOS.
_shell_ready = str(st.query_params.get("shiva_shell") or "") == "1"
if not _shell_ready:
    logo_path = Path(__file__).with_name("D7E70C85-998B-46E2-B9D8-6E02615CF194.png")
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    st.html(
        f"""
        <style>
        html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],
        [data-testid="stMain"]{{background:#071019!important;color-scheme:dark!important}}
        [data-testid="stMainBlockContainer"],.block-container{{padding:0!important;margin:0!important}}
        .shiva-shell-preflight{{position:fixed;inset:0;z-index:2147483647;background:#071019;
          display:flex;align-items:center;justify-content:center;overflow:hidden}}
        .shiva-shell-preflight img{{display:block;width:min(88vw,520px);height:auto;max-height:82vh;
          object-fit:contain;object-position:center;mix-blend-mode:screen}}
        </style>
        <div class="shiva-shell-preflight" aria-label="Shiva loading">
          <img src="data:image/png;base64,{logo_b64}" alt="THE SHIVA trophy">
        </div>
        """
    )
    components.html(
        r"""
        <script>
        (() => {
          try {
            const topWindow = window.top;
            const url = new URL(topWindow.location.href);
            url.searchParams.set('shiva_shell', '1');
            url.searchParams.set('embed', 'true');
            const currentOptions = url.searchParams.getAll('embed_options');
            if (!currentOptions.includes('hide_loading_screen')) {
              url.searchParams.append('embed_options', 'hide_loading_screen');
            }
            if (!currentOptions.includes('dark_theme')) {
              url.searchParams.append('embed_options', 'dark_theme');
            }
            topWindow.location.replace(url.toString());
          } catch (_) {}
        })();
        </script>
        """,
        height=0,
        width=0,
    )
    st.stop()

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

# The header is a two-column contract, not an overlay. This keeps the live NFL clock
# physically separate from the Shiva mark on narrow iPhone screens.
st.html(
    """
    <style id="shiva-header-layout-contract">
    .app-top{position:relative!important;display:grid!important;
      grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;
      column-gap:10px!important;padding-bottom:7px!important}
    .app-top .brand-wrap{width:auto!important;min-width:0!important;overflow:hidden!important}
    .app-top .brand-copy{min-width:0!important}
    .kickoff-compact{position:static!important;top:auto!important;right:auto!important;
      align-self:center!important;justify-self:end!important;flex:0 0 auto!important;
      margin:0!important;max-width:100%!important}
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
    </style>
    """
)

# Keep the server-rendered kickoff value alive between Streamlit reruns. This component
# has one responsibility only; unlike the removed shell controller it never hides DOM
# nodes, changes layout, or navigates the document.
components.html(
    r"""
    <script>
    (() => {
      let host, doc;
      try {
        host = window.parent;
        doc = host.document;
      } catch (_) {
        return;
      }
      const tick = () => {
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
      tick();
      const timer = host.setInterval(tick, 1000);
      window.addEventListener('beforeunload', () => host.clearInterval(timer), {once:true});
    })();
    </script>
    """,
    height=0,
    width=0,
)
