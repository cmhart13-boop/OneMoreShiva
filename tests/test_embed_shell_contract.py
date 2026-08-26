from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_uses_supported_embed_shell_without_css_widget_chasing():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert source.count("st.set_page_config(") == 1
    assert "components.html(" in source
    assert "searchParams.set('embed', 'true')" in source
    assert "hide_loading_screen" in source
    assert "dark_theme" in source
    assert "location.replace" in source
    assert "MutationObserver" not in source
    assert "viewerBadge" not in source
    assert "Hosted with Streamlit" not in source


def test_runtime_still_owns_application_rendering():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "runtime.replace(" not in source
    assert "exec(compile(runtime" in source
    assert "_shiva_compile" in source
