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
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Literal assignment {name!r} not found in {path.name}")


def test_vercel_first_paint_precedes_streamlit_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "class _FirstPaintASGI" in source
    assert "_inject_first_paint" in source
    assert "_HEAD_SHELL" in source
    assert "_BODY_SHELL" in source
    assert "_READY_SCRIPT" in source
    assert source.index("_streamlit_app = st.App") < source.index("app = _FirstPaintASGI")


def test_no_bootstrap_redirect_or_duplicate_runtime_splash():
    source = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert "location.replace" not in source
    assert "shiva_shell" not in source
    assert "embed_options" not in source
    assert "st.stop()" not in source
    assert 'st.session_state["_shiva_startup_splash_seen"] = True' in source


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
    runtime = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert '"legacy-startup-splash"' in runtime
    assert '"preheader-css-render"' in runtime
    assert '"hosted-badge-component"' in runtime
    assert '[data-testid="stMain"]{padding-top:0!important;margin-top:0!important}' in css
    assert '[data-testid="stMainBlockContainer"]' in css
    assert "padding-top:0!important" in css


def test_streamlit_shell_css_is_dark_before_content():
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert css.startswith('<style id="shiva-shell-contract">')
    assert css.endswith("</style>")
    assert "background-color:#071019!important" in css
    assert "st.html(_html)" in (ROOT / "app_runtime.py").read_text(encoding="utf-8")


def test_top_brand_is_title_case_shiva_without_uppercase_transform():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    css = _literal_assignment(ROOT / "app_runtime.py", "SHELL_STYLE")
    assert '<div class="brand-title">Shiva</div>' in source
    assert ".brand-title{text-transform:none!important}" in css


def test_canonical_shiva_logo_remains_single_source_of_truth():
    source = (ROOT / "app_runtime.py").read_text(encoding="utf-8")
    assert "Canonical Shiva logo asset is missing" in source
    assert "D7E70C85-998B-46E2-B9D8-6E02615CF194.png" in source
    assert 'class="shiva-trophy-mark"' in source


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


def test_runtime_source_compiles_cleanly():
    for filename in ("app.py", "streamlit_app.py", "app_runtime.py", "shiva_home_v2.py"):
        compile((ROOT / filename).read_text(encoding="utf-8"), filename, "exec")
