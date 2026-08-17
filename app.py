"""One More Shiva production bootstrap.

Production invariants:
- app.py owns Streamlit page configuration.
- app_runtime.py owns the validated transformation/render pipeline.
"""
from pathlib import Path

import streamlit as st

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
[data-testid="stAppCreatorAvatar"],
[data-testid="stAppCreatorAvatarContainer"],
.stAppDeployButton,
.stAppToolbar,
.css-1jc7ptx,
.e1ewe7hr3,
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
.viewerBadge_link__1S137,
.viewerBadge_text__1JaDK,
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="viewer-badge"],
[class*="stDeployButton"],
[class*="stStatusWidget"],
button[title="Manage app"],
button[aria-label="Manage app"],
a[aria-label="Manage app"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"],
div:has(> a[href*="streamlit.io/cloud"]),
div:has(> a[href*="share.streamlit.io"]),
iframe[title*="badge" i],
iframe[title*="manage" i] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    max-width: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
}
</style>
""")

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
