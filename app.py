"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration and first paint.
- The first emitted UI instruction is style-only CSS, so it cannot create a top gutter.
- Community Cloud is normalized into Streamlit's official footer-free embed presentation.
- The high-resolution trophy splash is owned here; app_runtime.py's legacy splash is suppressed.
- app_runtime.py remains the validated application transformation/render pipeline.
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SPLASH_SECONDS = 2.5

# Paint the production background before any image processing or runtime transformation.
# Streamlit routes style-only st.html content outside the main layout, so this adds no
# block, margin, or top gutter.
EARLY_SHELL_STYLE = """<style id="shiva-early-shell">
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stMain"]{
    background:#071019!important;
    background-color:#071019!important;
    color-scheme:dark!important;
}
</style>"""
st.html(EARLY_SHELL_STYLE)

# Community Cloud's documented embed presentation removes the hosted footer/chrome,
# top/bottom platform padding, and colored line. The dark-theme and hidden-loading
# options also keep the reload on the same Shiva background instead of a white skeleton.
EMBED_REDIRECT = """<script id="shiva-embed-bootstrap">
(() => {
    const url = new URL(window.location.href);
    if (url.searchParams.get("embed") === "true") return;
    url.searchParams.delete("embed_options");
    url.searchParams.set("embed", "true");
    url.searchParams.append("embed_options", "dark_theme");
    url.searchParams.append("embed_options", "hide_loading_screen");
    window.location.replace(url.toString());
})();
</script>"""
if not st.context.is_embedded:
    st.html(EMBED_REDIRECT, unsafe_allow_javascript=True)


def _bootstrap_splash_style(data_uri: str) -> str:
    """Return a style-only, fixed splash overlay that never participates in layout."""
    return f"""<style id="shiva-bootstrap-splash">
body::before{{
    content:"";
    position:fixed;
    inset:0;
    width:100vw;
    height:100dvh;
    z-index:2147483647;
    pointer-events:none;
    background-color:#071019;
    background-image:url('{data_uri}');
    background-repeat:no-repeat;
    background-position:center;
    background-size:min(52vw,225px) auto;
    animation:shivaBootstrapSplashGone 0s linear {SPLASH_SECONDS}s forwards;
}}
@keyframes shivaBootstrapSplashGone{{to{{opacity:0;visibility:hidden}}}}
</style>"""


if st.context.is_embedded and not st.session_state.get("_shiva_bootstrap_splash_seen", False):
    # Import after the immediate dark paint so Pillow work can never hold up first paint.
    from shiva_splash import splash_data_uri

    st.html(_bootstrap_splash_style(splash_data_uri()))
    st.session_state["_shiva_bootstrap_splash_seen"] = True

# app_runtime.py still contains the historical splash contract, but this bootstrap is now
# the single splash owner. Suppress the legacy path before the runtime executes.
st.session_state["_shiva_startup_splash_seen"] = True

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
