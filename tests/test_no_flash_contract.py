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


def _literal_assignment(path: Path, name: str):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Literal assignment {name!r} not found in {path.name}")


def test_bootstrap_keeps_zero_layout_elements_before_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "st.markdown(" not in source
    assert "st.html(" not in source
    assert "st.empty(" not in source
    assert "st.container(" not in source
    assert "components.html(" not in source
    assert "zero Streamlit layout elements" in source


def test_runtime_removes_all_legacy_preheader_slots():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert 'code.find("# Startup splash: initial app launch only.")' in source
    assert 'code.replace("st.markdown(CSS, unsafe_allow_html=True)\\ninject_coach_css()\\n", "")' in source
    assert '_badge_start = code.find("# Streamlit Community Cloud hosted-badge suppressor.")' in source
    assert 'code = code[:_start] + code[_end:]' in source
    assert 'code = code[:_badge_start] + code[_badge_end:]' in source


def test_shell_uses_native_html_not_markdown_for_first_paint():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "st.html(_html)" in source
    header_patch = source[source.index("_new_header ="):source.index("code = code.replace(_old_header, _new_header)")]
    assert "st.markdown(" not in header_patch
    assert "_splash_slot = st.empty()" not in source


def test_shell_css_is_valid_and_preserves_zero_top_gutter():
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert css.startswith('<style id="shiva-shell-contract">')
    assert css.endswith("</style>")
    assert '[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}' in css
    assert '[data-testid="stMainBlockContainer"]' in css
    assert "padding-top:0!important" in css
    assert "*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}" in css


def test_splash_uses_original_shiva_trophy_not_brain_asset():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "_trophy_match = re.search" in source
    assert '_splash = f\'<div class="shiva-startup-splash">{{SHIVA_MARK}}</div>\'' in source
    assert "FDBBC710-B60A-4DA4-9582-F52D6210DB18.png" not in source
    assert "shiva-splash-trophy" not in source
    assert "width:min(52vw,225px)!important" in source
    assert ".shiva-startup-splash .shiva-trophy-mark" in source
    assert "animation:none!important" in source
    assert "transform:none!important" in source
    assert "transition:none!important" in source


def test_original_typography_contract_remains_in_app_core():
    source = (ROOT / "app_core.py").read_text(encoding="utf-8")
    expected = 'font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    assert expected in source
    bootstrap = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "SHIVA_FONT_LOCK" not in bootstrap
    assert "st.markdown =" not in bootstrap


def test_splash_duration_stays_2_point_5_seconds():
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert "animation:shivaSplashGone 0s linear 2.5s forwards" in css


def test_home_navigation_callback_does_not_force_second_rerun():
    source = _function_source(ROOT / "app_runtime.py", "_smooth_home_go")
    assert "st.rerun" not in source
    assert 'st.query_params["page"]' in source


def test_bottom_navigation_runtime_patch_is_callback_based():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "on_click=_nav_to" in source
    assert "_home_v2.go = _smooth_home_go" in source


def test_shiva_edge_position_filter_is_fragment_local_and_persistent():
    source = (ROOT / "shiva_home_v2.py").read_text(encoding="utf-8")
    fragment = _function_source(ROOT / "shiva_home_v2.py", "_render_edge_fragment")
    setter = _function_source(ROOT / "shiva_home_v2.py", "_set_edge_pos")
    assert "@st.fragment" in source
    assert 'st.session_state["shiva_edge_pos"]' in setter
    assert "on_click=_set_edge_pos" in fragment
    assert "st.rerun" not in fragment
    assert "checked' if pos=='QB'" not in source
