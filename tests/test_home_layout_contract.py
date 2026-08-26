from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "shiva_home_v2.py"


def _source() -> str:
    return HOME.read_text(encoding="utf-8")


def _function_source(name: str) -> str:
    source = _source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function {name!r} not found")


def test_home_source_compiles():
    compile(_source(), "shiva_home_v2.py", "exec")


def test_decision_controls_are_compact_four_button_action_row():
    source = _source()
    render = _function_source("render_home_v2")

    assert 'with st.container(key="action_row"):' in render
    assert 'c1,c2,c3,c4=st.columns(4,gap="small")' in render
    assert "Make Your Move" not in render
    assert "one tap away" not in render

    expected = (
        ('key="home_go_draft"', 'on_click=go', 'args=("Draft",)'),
        ('key="home_go_coach"', 'on_click=go', 'args=("Coach",)'),
        ('key="home_go_guide"', 'on_click=go', 'args=("Guide",)'),
        ('key="home_go_players"', 'on_click=go', 'args=("Players",)'),
    )
    for key, callback, args in expected:
        assert key in render
        assert callback in render
        assert args in render

    assert '.st-key-action_row [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important' in source
    assert '.st-key-action_row [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:25%!important}' in source


def test_edge_previews_share_one_row_and_expand_below_it():
    source = _source()
    render = _function_source("render_home_v2")

    preview_row = render.index('with st.container(key="edge_preview_row"):')
    floor_card = render.index('with st.container(key="edge_floor_card"):', preview_row)
    floor_button = render.index('key="edge_floor_open"', floor_card)
    ceiling_card = render.index('with st.container(key="edge_ceiling_card"):', floor_button)
    ceiling_button = render.index('key="edge_ceiling_open"', ceiling_card)
    expand = render.index('if edge_mode in {"floor","ceiling"}:', ceiling_button)
    fragment = render.index('_render_edge_fragment(edge_pool,edge_mode)', expand)

    assert preview_row < floor_card < floor_button < ceiling_card < ceiling_button < expand < fragment
    assert 'on_click=_toggle_edge,args=("floor",)' in render
    assert 'on_click=_toggle_edge,args=("ceiling",)' in render
    assert 'e1,e2=st.columns(2)' not in render
    assert 'Close Shiva Edge rankings' not in render

    assert '.st-key-edge_preview_row [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important' in source
    assert '.st-key-edge_preview_row [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:50%!important' in source


def test_edge_toggle_is_authoritative_and_clears_stale_query_state():
    toggle = _function_source("_toggle_edge")
    assert 'st.session_state.get("shiva_edge_mode")==mode' in toggle
    assert 'st.session_state.pop("shiva_edge_mode",None)' in toggle
    assert 'st.session_state["shiva_edge_mode"]=mode' in toggle
    assert 'del st.query_params["edge_mode"]' in toggle
    assert "st.rerun" not in toggle


def test_edge_position_filters_are_four_callback_buttons_in_one_non_wrapping_row():
    source = _source()
    fragment = _function_source("_render_edge_fragment")

    assert 'cols=st.columns(4,gap="small")' in fragment
    assert 'for col,pos in zip(cols,("QB","RB","WR","TE")):' in fragment
    assert 'on_click=_set_edge_pos' in fragment
    assert 'args=(pos,)' in fragment
    assert 'type="primary" if current==pos else "secondary"' in fragment
    assert "st.rerun" not in fragment

    assert '.st-key-edge_panel_fragment [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important' in source
    assert '.st-key-edge_panel_fragment [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:25%!important}' in source


def test_top_ten_is_position_scoped_and_keeps_verified_data_rules():
    rows = _function_source("_edge_rows")
    assert 'pool["pos"].astype(str).eq(position)' in rows
    assert '.head(10)' in rows
    assert 'sort_values([stat,"ppg"],ascending=False)' in rows
    assert 'No estimate substituted for this position.' in rows
    assert 'minimum 8 games with verified weekly results' in rows
