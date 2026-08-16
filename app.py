"""One More Shiva production bootstrap.

Production invariants:
- app.py emits zero layout elements before runtime.
- CSS/style payloads never pass through Streamlit's Markdown parser.
- app_runtime.py still owns the first visible SHIVA header/splash render.
- The original Shiva typography stack is injected with every CSS-bearing shell render.
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="One More Shiva",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Original Shiva typography contract from app_core. Keep this at the bootstrap boundary
# so shell/rendering changes cannot silently swap the app to Streamlit/browser defaults.
SHIVA_FONT_LOCK = '''<style id="shiva-font-lock">
html,body,#root,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],
button,input,textarea,select,[role="button"],[role="tab"],[role="radio"],
[data-testid="stMarkdownContainer"],[data-testid="stText"],[data-testid="stCaptionContainer"]{
  font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;
}
</style>'''

# Permanent rendering contract: unsafe HTML that contains CSS must never go through
# Markdown. Markdown can legally fall back to visible text when HTML is malformed or
# parsed differently on a client. st.html renders the HTML/CSS payload directly.
_original_markdown = st.markdown

def _shiva_safe_markdown(body, *args, **kwargs):
    if (
        isinstance(body, str)
        and kwargs.get("unsafe_allow_html", False)
        and "<style" in body.lower()
    ):
        return st.html(SHIVA_FONT_LOCK + body)
    return _original_markdown(body, *args, **kwargs)

st.markdown = _shiva_safe_markdown

runtime_path = Path(__file__).with_name("app_runtime.py")
runtime = runtime_path.read_text(encoding="utf-8")

# app.py owns page configuration. Remove the duplicate call embedded in app_core before
# the runtime executes it. This transformation creates no Streamlit layout element.
_read_core = 'code = core.read_text(encoding="utf-8")'
_runtime_patch = _read_core + "\ncode = code.replace('st.set_page_config(page_title=\"One More Shiva\", page_icon=\"🏆\", layout=\"wide\", initial_sidebar_state=\"collapsed\")', '')"
runtime = runtime.replace(_read_core, _runtime_patch, 1)

exec(compile(runtime, str(runtime_path), "exec"), globals(), globals())
