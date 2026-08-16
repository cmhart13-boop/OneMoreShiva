from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def _function_source(path: Path, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function {name!r} not found in {path.name}")


def test_browser_shell_is_permanent_and_dark():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "shiva-permanent-no-flash" in source
    assert "MutationObserver" in source
    assert "theme-color" in source
    assert "#071019" in source
    assert "-webkit-tap-highlight-color: transparent" in source


def test_mobile_shell_has_no_streamlit_top_gutter():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'viewport-fit=cover' in source
    assert '[data-testid="stHeader"]' in source
    assert 'height: 0 !important' in source
    assert '[data-testid="stMainBlockContainer"]' in source
    assert 'padding-top: max(env(safe-area-inset-top), 0px) !important' in source
    assert 'margin-top: 0 !important' in source


def test_home_navigation_callback_does_not_force_second_rerun():
    source = _function_source(ROOT / "app_runtime.py", "_smooth_home_go")
    assert "st.rerun" not in source
    assert 'st.query_params["page"]' in source


def test_bottom_navigation_runtime_patch_is_callback_based():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "on_click=_nav_to" in source
    assert "_home_v2.go = _smooth_home_go" in source
    assert "no-flash interaction invariant" in source


def test_runtime_keeps_ios_tap_flash_disabled_globally():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}" in source


def test_shiva_edge_position_filter_is_fragment_local_and_persistent():
    source = (ROOT / "shiva_home_v2.py").read_text(encoding="utf-8")
    fragment = _function_source(ROOT / "shiva_home_v2.py", "_render_edge_fragment")
    setter = _function_source(ROOT / "shiva_home_v2.py", "_set_edge_pos")
    assert "@st.fragment" in source
    assert 'st.session_state["shiva_edge_pos"]' in setter
    assert "on_click=_set_edge_pos" in fragment
    assert "st.rerun" not in fragment
    assert "checked' if pos=='QB'" not in source
