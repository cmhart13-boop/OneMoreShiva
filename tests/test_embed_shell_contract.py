from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_uses_single_document_shell_controller():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert source.count("st.set_page_config(") == 1
    assert "components.html(" in source
    assert "MutationObserver" in source
    assert "data-shiva-kickoff" in source
    assert "Hosted with Streamlit" not in source
    assert "hosted with" in source
    assert "viewerBadge" in source
    assert "location.replace" not in source
    assert "searchParams.set('embed', 'true')" not in source
    assert "__shivaShellController" in source
    assert "dispose" in source


def test_shell_controller_owns_collision_safe_header_layout():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "grid-template-columns:minmax(0,1fr) auto" in source
    assert ".kickoff-compact{position:static" in source
    assert "updateKickoff" in source
    assert "setInterval(sweep, 1000)" in source


def test_runtime_still_owns_application_rendering():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "runtime.replace(" not in source
    assert "exec(compile(runtime" in source
    assert "_shiva_compile" in source
