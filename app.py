# Production entrypoint. Load the narrow mobile UI patch, then execute the preserved app.
import sitecustomize  # noqa: F401
from pathlib import Path

_legacy = Path(__file__).with_name("app_legacy.py")
_code = _legacy.read_text(encoding="utf-8")
exec(compile(_code, str(_legacy), "exec"), globals(), globals())
