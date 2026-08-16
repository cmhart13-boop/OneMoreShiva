from pathlib import Path
import ast
import struct

ROOT = Path(__file__).resolve().parents[1]


def _function_source(path: Path, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function {name!r} not found in {path.name}")


def _literal_assignment(path: Path, name: str):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Literal assignment {name!r} not found in {path.name}")


def _png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()[:24]
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    assert raw[12:16] == b"IHDR", f"{path.name} has no PNG IHDR"
    return struct.unpack(">II", raw[16:24])


def test_bootstrap_emits_no_layout_before_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "st.empty(" not in source
    assert "components.html(" not in source
    assert "st.container(" not in source
    assert "st.html(" in source  # used only inside the deferred renderer wrapper


def test_bootstrap_routes_style_html_away_from_markdown_parser():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    wrapper = _function_source(ROOT / "app.py", "_shiva_safe_markdown")
    assert "_original_markdown = st.markdown" in source
    assert '"<style" in body.lower()' in wrapper
    assert 'kwargs.get("unsafe_allow_html", False)' in wrapper
    assert "return st.html(body)" in wrapper
    assert "return _original_markdown(body, *args, **kwargs)" in wrapper
    assert "st.markdown = _shiva_safe_markdown" in source


def test_runtime_removes_legacy_preheader_slots():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert 'code.replace("st.markdown(CSS, unsafe_allow_html=True)\\ninject_coach_css()\\n", "")' in source
    assert '_badge_start = code.find("# Streamlit Community Cloud hosted-badge suppressor.")' in source
    assert 'code.find("# Startup splash: initial app launch only.")' in source
    assert 'code = code[:_start] + code[_end:]' in source
    assert 'code = code[:_badge_start] + code[_badge_end:]' in source


def test_shell_css_is_canonical_valid_html():
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert css.startswith('<style id="shiva-shell-contract">')
    assert css.endswith("</style>")
    assert '\\"' not in css
    assert "<style" in css and "</style>" in css
    assert "*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}" in css
    assert '[data-testid="stMainBlockContainer"]' in css
    assert "padding-top:0!important" in css


def test_runtime_shell_is_forced_through_bootstrap_html_guard():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "{SHELL_STYLE!r}" in source
    assert "st.markdown(_base_css +" in source
    # The bootstrap replaces st.markdown with the native-HTML routing wrapper before
    # app_runtime executes, so this CSS-bearing call never reaches Markdown parsing.
    bootstrap = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "st.markdown = _shiva_safe_markdown" in bootstrap


def test_header_carries_shell_css_and_splash_in_one_element():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "{SHELL_STYLE!r}" in source
    assert "shiva-startup-splash" in source
    assert "animation:shivaSplashGone" in source
    assert "_splash_slot = st.empty()" not in source


def test_retina_splash_uses_real_high_resolution_png():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    asset = ROOT / "FDBBC710-B60A-4DA4-9582-F52D6210DB18.png"
    width, height = _png_dimensions(asset)
    assert width >= 675
    assert height > 0
    assert '_splash_asset_path = Path(__file__).with_name("FDBBC710-B60A-4DA4-9582-F52D6210DB18.png")' in source
    assert '_splash_img = Image.open(_splash_asset_path).convert("RGBA")' in source
    assert "if _splash_source_width >= 675:" in source
    assert "data:image/png;base64," in source
    assert 'class="shiva-splash-trophy"' in source
    assert "width:min(52vw,225px)!important" in source
    assert "filter:none!important" in source
    assert "transform:none!important" in source
    assert "transition:none!important" in source


def test_header_and_nav_asset_remain_separate_from_splash_asset():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "_trophy_match = re.search" in source
    assert '_splash_asset_path = Path(__file__).with_name(' in source
    assert '<div class="brand-badge">{SHIVA_MARK}</div>' in source
    assert 'class="shiva-splash-trophy"' in source


def test_home_navigation_callback_does_not_force_second_rerun():
    source = _function_source(ROOT / "app_runtime.py", "_smooth_home_go")
    assert "st.rerun" not in source
    assert 'st.query_params["page"]' in source


def test_bottom_navigation_runtime_patch_is_callback_based():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "on_click=_nav_to" in source
    assert "_home_v2.go = _smooth_home_go" in source


def test_runtime_keeps_ios_tap_flash_disabled_globally():
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert "*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}" in css


def test_shiva_edge_position_filter_is_fragment_local_and_persistent():
    source = (ROOT / "shiva_home_v2.py").read_text(encoding="utf-8")
    fragment = _function_source(ROOT / "shiva_home_v2.py", "_render_edge_fragment")
    setter = _function_source(ROOT / "shiva_home_v2.py", "_set_edge_pos")
    assert "@st.fragment" in source
    assert 'st.session_state["shiva_edge_pos"]' in setter
    assert "on_click=_set_edge_pos" in fragment
    assert "st.rerun" not in fragment
    assert "checked' if pos=='QB'" not in source
