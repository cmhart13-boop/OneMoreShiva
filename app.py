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

# Hide Streamlit's hosted-app controls/widget without affecting the Shiva UI.
st.html("""
<style>
#MainMenu,
footer,
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
[data-testid="stViewerBadge"],
[data-testid="stAppCreatorAvatar"],
.stAppDeployButton,
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="stDeployButton"],
button[title="Manage app"],
button[aria-label="Manage app"],
a[aria-label="Manage app"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}
</style>
""")

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")
exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
