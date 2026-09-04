from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "shiva_draft_guide.py"


def _source() -> str:
    return GUIDE.read_text(encoding="utf-8")


def _function_source(name: str) -> str:
    source = _source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function {name!r} not found")


def test_guide_source_compiles():
    compile(_source(), "shiva_draft_guide.py", "exec")


def test_redundant_guide_hero_is_removed_and_sections_move_up():
    source = _source()
    home = _function_source("_render_home")

    assert ".guide-hero" not in source
    assert ".guide-kicker" not in source
    assert "Joel Smyth's Draft Guide" not in home
    assert "Built like a site, not a PDF." not in home
    assert "guide-toc" in home
    assert "GUIDE_SECTIONS" in home
    assert ".guide-toc{display:grid" in source
    assert "margin:2px 0 15px" in source


def test_guide_navigation_rankings_research_and_profiles_remain_intact():
    source = _source()

    for slug in ("rankings", "strategy", "research", "luck", "player-cards"):
        assert f',"{slug}",' in source

    for function_name in (
        "_render_rankings",
        "_render_strategy",
        "_render_research",
        "_render_luck",
        "_render_player_cards",
    ):
        assert f"def {function_name}(" in source

    assert "Player profile →" in source
    assert "_player_href" in source
