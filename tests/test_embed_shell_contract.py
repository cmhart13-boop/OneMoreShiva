from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vercel_entrypoint_wraps_streamlit_asgi_without_redirects():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert '_streamlit_app = st.App("streamlit_app.py")' in source
    assert "app = _FirstPaintASGI(_streamlit_app)" in source
    assert "location.replace" not in source
    assert "searchParams.set" not in source
    assert "embed_options" not in source


def test_first_document_paint_is_dark_and_owns_single_launch_shell():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'NAVY = "#071019"' in source
    assert 'id="shiva-first-paint"' in source
    assert 'id="shiva-launch-shell"' in source
    assert "/app/static/shiva-trophy.png" in source
    assert 'rel="preload"' in source
    assert 'name="theme-color"' in source
    assert 'minimumVisibleMs = 2200' in source
    assert "MutationObserver" in source
    assert 'document.querySelector(".app-top")' in source
    assert "7000" in source


def test_first_paint_middleware_only_modifies_root_html():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'scope.get("type") != "http"' in source
    assert 'scope.get("path") not in ("", "/")' in source
    assert '"text/html" in content_type.lower()' in source
    assert 'key.lower() != b"content-length"' in source
    assert 'headers.append((b"content-length"' in source


def test_streamlit_runtime_has_no_second_document_navigation_or_splash():
    source = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert source.count("st.set_page_config(") == 1
    assert 'st.session_state["_shiva_startup_splash_seen"] = True' in source
    assert "location.replace" not in source
    assert "shiva_shell" not in source
    assert "embed_options" not in source
    assert "st.stop()" not in source


def test_static_trophy_is_served_by_streamlit():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "enableStaticServing = true" in config
    assert (ROOT / "static" / "shiva-trophy.png").is_file()
