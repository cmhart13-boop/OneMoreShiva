from pathlib import Path
import ast
import base64
import io

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def _literal_assignment(path: Path, name: str):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Literal assignment {name!r} not found in {path.name}")


def test_host_bootstrap_is_scoped_and_runtime_is_unchanged():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "from streamlit.components.v1 import html as _bootstrap_html" in source
    assert "_bootstrap_html(_host_bootstrap_markup(splash_data_uri()), height=0, width=0, scrolling=False)" in source
    assert 'st.session_state["_shiva_startup_splash_seen"] = True' in source
    assert "exec(compile(runtime" in source
    assert "st.markdown(" not in source
    assert "st.html(" not in source
    assert "st.empty(" not in source


def test_bootstrap_uses_footer_free_dark_embed_mode_and_collapses_its_wrapper():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "url.searchParams.set('embed', 'true')" in source
    assert "url.searchParams.append('embed_options', 'dark_theme')" in source
    assert "url.searchParams.append('embed_options', 'hide_loading_screen')" in source
    assert "topWindow.location.replace(url.toString())" in source
    assert "doc.documentElement.style.setProperty('background-color', dark, 'important')" in source
    assert "wrapper.style.setProperty('display', 'none', 'important')" in source
    assert "height=0, width=0" in source


def test_splash_contract_is_two_point_five_seconds_and_uses_prepared_asset():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert _literal_assignment(ROOT / "app.py", "SPLASH_SECONDS") == 2.5
    assert "shiva-startup-splash-v2" in source
    assert "width:min(52vw,225px)" in source
    assert "filter:none" in source
    assert "transform:none" in source
    assert "setTimeout(() => splash.remove(), 2500)" in source


def test_high_resolution_trophy_pipeline_emits_rgba_png():
    import sys
    sys.path.insert(0, str(ROOT))
    from shiva_splash import MIN_RENDER_WIDTH, splash_data_uri

    uri = splash_data_uri()
    assert uri.startswith("data:image/png;base64,")
    raw = base64.b64decode(uri.split(",", 1)[1])
    with Image.open(io.BytesIO(raw)) as image:
        assert image.format == "PNG"
        assert image.mode == "RGBA"
        assert image.width >= MIN_RENDER_WIDTH
        assert image.getbbox() is not None


def test_approved_artwork_only():
    source = (ROOT / "shiva_splash.py").read_text(encoding="utf-8")
    assert "1FB42328-2FEA-43AE-9BAC-D6BE96E58C93.jpeg" in source
    assert "FDBBC710-B60A-4DA4-9582-F52D6210DB18.png" not in source
    assert "ImageChops.difference" in source
    assert "Image.Resampling.LANCZOS" in source
