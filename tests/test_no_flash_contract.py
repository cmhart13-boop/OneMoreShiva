from pathlib import Path
import ast
import re

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


def test_bootstrap_is_single_owner_and_emits_no_layout_before_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert source.count("st.set_page_config(") == 1
    assert "st.markdown(" not in source
    assert "st.html(" not in source
    assert "st.empty(" not in source
    assert "components.html(" not in source
    assert "runtime.replace(" not in source
    assert "exec(compile(runtime" in source


def test_runtime_has_fail_fast_transformation_primitives():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    replace_once = _function_source(ROOT / "app_runtime.py", "_replace_once")
    remove_once = _function_source(ROOT / "app_runtime.py", "_remove_between_once")
    assert "source.count(old)" in replace_once
    assert "matches != 1" in replace_once
    assert "raise RuntimeError" in replace_once
    assert "missing start marker" in remove_once
    assert "missing end marker" in remove_once
    assert "duplicate start markers" in remove_once
    assert "code = code.replace(" not in source


def test_runtime_contracts_match_the_real_app_core_exactly_once():
    core = (ROOT / "app_core.py").read_text(encoding="utf-8")
    runtime_path = ROOT / "app_runtime.py"

    direct_contracts = {
        "page-config": 'st.set_page_config(page_title="One More Shiva", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")',
        "preheader-css": "st.markdown(CSS, unsafe_allow_html=True)\ninject_coach_css()\n",
        "draft-defaults": 'defaults={"draft_log":[],"queue":[],"user_slot":3,"team_count":DEFAULT_TEAMS,"rounds":DEFAULT_ROUNDS,"draft_view":"Players","ask_history":[]}',
        "draft-reset": 'if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()',
        "coach-css": 'def season_coach():\n    screen_head("Shiva Coach","Fast decisions, clear evidence, and the little edges people forget.")',
    }
    for label, snippet in direct_contracts.items():
        assert core.count(snippet) == 1, f"{label} contract drifted"

    for name in ("_old_bottom_nav", "_old_draft_start", "_old_header"):
        snippet = _literal_assignment(runtime_path, name)
        assert core.count(snippet) == 1, f"{name} no longer matches app_core exactly once"

    assert core.count("# Startup splash: initial app launch only.") == 1
    assert core.count("SHIVA_MARK =") == 1
    assert core.count("# Streamlit Community Cloud hosted-badge suppressor.") == 1
    assert core.count("\n\n\ndef stable_id") == 1

    trophy_pattern = re.compile(
        r'SHIVA_MARK\s*=\s*f?"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,([A-Za-z0-9+/=]+)" alt="THE SHIVA trophy">"""'
    )
    assert len(trophy_pattern.findall(core)) == 1


def test_runtime_owns_duplicate_page_config_removal():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert '"page-config"' in source
    assert 'if "st.set_page_config(" in code:' in source
    assert "Duplicate Streamlit page config survived" in source


def test_zero_top_gutter_contract_is_preserved():
    bootstrap = (ROOT / "app.py").read_text(encoding="utf-8")
    runtime = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert "st.empty(" not in bootstrap
    assert '"legacy-startup-splash"' in runtime
    assert '"preheader-css-render"' in runtime
    assert '"hosted-badge-component"' in runtime
    assert '[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}' in css
    assert '[data-testid="stMainBlockContainer"]' in css
    assert "padding-top:0!important" in css
    assert 'if "_splash_slot = st.empty()" in code:' in runtime


def test_shell_css_is_valid_and_first_paint_uses_native_html():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert css.startswith('<style id="shiva-shell-contract">')
    assert css.endswith("</style>")
    assert '\\"' not in css
    assert "*,*::before,*::after{-webkit-tap-highlight-color:transparent!important}" in css
    assert "st.html(_html)" in source
    assert "st.markdown(_html" not in source


def test_splash_uses_only_the_approved_header_trophy():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert '_splash = f\'<div class="shiva-startup-splash">{{SHIVA_MARK}}</div>\'' in source
    assert '<div class="brand-badge">{{SHIVA_MARK}}</div>' in source
    assert "FDBBC710-B60A-4DA4-9582-F52D6210DB18.png" not in source
    assert "shiva-splash-trophy" not in source
    assert "width:min(52vw,225px)!important" in source
    assert "animation:none!important" in source
    assert "transform:none!important" in source
    assert "transition:none!important" in source


def test_trophy_asset_conversion_is_scoped_to_exact_shiva_mark_assignment():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "expected 1 approved SHIVA_MARK" in source
    assert 'class="shiva-trophy-mark"' in source
    assert 'alt="THE SHIVA trophy"' in source
    assert "Unable to prepare approved Shiva trophy asset" in source
    assert "_trophy_match.start()" in source
    assert "_trophy_match.end()" in source
    assert "_trophy_assignment" in source
    assert 'f\'data:image/jpeg;base64,{_trophy_match.group(1)}\'' not in source
    assert '"approved-trophy-conversion"' not in source
    assert "data:image/png;base64," in source


def test_original_typography_remains_owned_by_app_core():
    core = (ROOT / "app_core.py").read_text(encoding="utf-8")
    runtime = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    expected = 'font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
    assert expected in core
    assert "SHIVA_FONT_LOCK" not in runtime
    assert "font-family:" not in _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")


def test_home_navigation_callback_does_not_force_second_rerun():
    source = _function_source(ROOT / "app_runtime.py", "_smooth_home_go")
    assert "st.rerun" not in source
    assert 'st.query_params["page"]' in source


def test_bottom_navigation_runtime_contract_is_callback_based():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "on_click=_nav_to" in source
    assert "_home_v2.go = _smooth_home_go" in source
    assert '"bottom-navigation"' in source


def test_shiva_edge_position_filter_is_fragment_local_and_persistent():
    source = (ROOT / "shiva_home_v2.py").read_text(encoding="utf-8")
    fragment = _function_source(ROOT / "shiva_home_v2.py", "_render_edge_fragment")
    setter = _function_source(ROOT / "shiva_home_v2.py", "_set_edge_pos")
    assert "@st.fragment" in source
    assert 'st.session_state["shiva_edge_pos"]' in setter
    assert "on_click=_set_edge_pos" in fragment
    assert "st.rerun" not in fragment
    assert "checked' if pos=='QB'" not in source


def test_runtime_source_compiles_cleanly():
    compile((ROOT / "app.py").read_text(encoding="utf-8"), "app.py", "exec")
    compile((ROOT / "app_runtime.py").read_text(encoding="utf-8"), "app_runtime.py", "exec")
    compile((ROOT / "shiva_home_v2.py").read_text(encoding="utf-8"), "shiva_home_v2.py", "exec")
