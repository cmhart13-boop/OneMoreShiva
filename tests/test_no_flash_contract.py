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


def test_bootstrap_emits_no_layout_before_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "st.markdown(" not in source
    assert "st.empty(" not in source
    assert "components.html(" not in source
    assert "st.container(" not in source
    assert "zero Streamlit layout elements" in source


def test_runtime_removes_legacy_preheader_slots():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert 'code.replace("st.markdown(CSS, unsafe_allow_html=True)\\ninject_coach_css()\\n", "")' in source
    assert '_badge_start = code.find("# Streamlit Community Cloud hosted-badge suppressor.")' in source
    assert 'code.find("# Startup splash: initial app launch only.")' in source
    assert 'code = code[:_start] + code[_end:]' in source
    assert 'code = code[:_badge_start] + code[_badge_end:]' in source


def test_header_carries_shell_css_and_splash_in_one_element():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert 'style id="shiva-shell-contract"' in source
    assert '[data-testid="stMainBlockContainer"]' in source
    assert 'padding-top:0!important' in source
    assert 'st.markdown(CSS +' in source
    assert 'shiva-startup-splash' in source
    assert 'animation:shivaSplashGone' in source
    # No actual pre-header placeholder call may exist. Mentions in comments are fine.
    assert '_splash_slot = st.empty()' not in source


def test_home_navigation_callback_does_not_force_second_rerun():
    source = _function_source(ROOT / "app_runtime.py", "_smooth_home_go")
    assert "st.rerun" not in source
    assert 'st.query_params["page"]' in source


def test_bottom_navigation_runtime_patch_is_callback_based():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "on_click=_nav_to" in source
    assert "_home_v2.go = _smooth_home_go" in source


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
