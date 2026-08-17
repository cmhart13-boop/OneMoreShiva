from pathlib import Path
import ast
import base64
import io
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def _literal(name: str):
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def test_startup_fix_is_scoped_and_fail_safe():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    compile(source, "app.py", "exec")
    assert _literal("SPLASH_SECONDS") == 2.5
    assert "st.html(EARLY_SHELL_STYLE)" in source
    assert "background:#071019!important" in source
    assert "except Exception:\n        _splash_uri = None" in source
    assert 'if _splash_uri:' in source
    assert 'st.session_state["_shiva_startup_splash_seen"] = True' in source
    assert "location.replace" not in source
    assert "embed_options" not in source
    assert "exec(compile(runtime" in source


def test_footer_suppressor_has_no_redirect_or_state_mutation():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "stAppViewerBadge" in source
    assert "streamlit.io" in source
    assert "streamlit.app" in source
    assert "MutationObserver" in source
    assert "height=0" in source
    assert "location.replace" not in source


def test_high_resolution_trophy_prepares_retina_png():
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


def test_runtime_is_not_modified_by_startup_fix():
    runtime = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert '_splash = f\'<div class="shiva-startup-splash">{{SHIVA_MARK}}</div>\'' in runtime
