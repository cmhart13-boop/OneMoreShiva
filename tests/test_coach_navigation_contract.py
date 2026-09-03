from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COACH = ROOT / "shiva_product_plus.py"


def test_coach_navigation_uses_button_pills_not_radio_controls():
    source = COACH.read_text(encoding="utf-8")

    assert "COACH_TABS" in source
    assert 'key="coach_tab_pills"' in source
    assert "on_click=_set_coach_tab" in source
    assert "st.radio(" not in source
