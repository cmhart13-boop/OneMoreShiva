from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_production_app_executes_home_without_runtime_exception():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=45)
    app.run()
    assert not app.exception, [str(item) for item in app.exception]
