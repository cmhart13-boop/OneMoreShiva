from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_first_paint_shell_has_no_visible_logo_box():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'background:transparent!important' in source
    assert 'border:0!important' in source
    assert 'box-shadow:none!important' in source
    assert 'mix-blend-mode:lighten!important' in source
    assert 'transition:opacity 420ms ease-in-out' in source
    assert 'STATIC_TROPHY_URL = "/app/static/shiva-trophy.png"' in source


def test_first_paint_is_dark_and_present_before_streamlit_mounts():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'NAVY = "#071019"' in source
    assert 'id="shiva-first-paint"' in source
    assert 'id="shiva-launch-shell"' in source
    assert '<meta name="theme-color" content="{NAVY}">' in source
    assert source.index("_HEAD_SHELL") < source.index("_streamlit_app = st.App")
    assert source.index("_BODY_SHELL") < source.index("_streamlit_app = st.App")


def test_launch_shell_does_not_replay_inside_streamlit_runtime():
    source = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert 'st.session_state["_shiva_startup_splash_seen"] = True' in source
    assert "location.replace" not in source
    assert "st.stop()" not in source
