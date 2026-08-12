"""One More Shiva production entrypoint.

One execution path: app.py -> app_core.py.
"""
from pathlib import Path

core = Path(__file__).with_name("app_core.py")
code = core.read_text(encoding="utf-8")
exec(compile(code, str(core), "exec"), globals(), globals())
