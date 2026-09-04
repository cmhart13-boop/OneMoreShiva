"""Vercel ASGI entrypoint for One More Shiva.

The first browser paint is owned here, before Streamlit's React bundle mounts. That
prevents iOS Safari from painting Streamlit's default light shell between the network
response and the app theme, and keeps launch to one continuous sequence:

    Shiva trophy -> Home

Internal Streamlit navigation remains untouched and does not replay the launch shell.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
import re
from typing import Any

import streamlit as st


NAVY = "#071019"
STATIC_TROPHY_URL = "/app/static/shiva-trophy.png"

# This block is deliberately injected immediately after <head>, before Streamlit's
# own styles/scripts. On iOS a late override can still allow a single light frame.
_HEAD_SHELL = f"""
<meta name="theme-color" content="{NAVY}">
<meta name="color-scheme" content="dark">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Shiva">
<link rel="manifest" href="/app/static/manifest.webmanifest">
<link rel="apple-touch-icon" href="{STATIC_TROPHY_URL}">
<link rel="apple-touch-startup-image" href="{STATIC_TROPHY_URL}">
<link rel="preload" href="{STATIC_TROPHY_URL}" as="image" fetchpriority="high">
<script>
  window.si = window.si || function () {{ (window.siq = window.siq || []).push(arguments); }};
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
<style id="shiva-first-paint">
:root,html,body,#root{{background:{NAVY}!important;background-color:{NAVY}!important;color-scheme:dark!important;min-height:100%;margin:0}}
html{{-webkit-text-size-adjust:100%;text-size-adjust:100%}}
body{{overflow-x:hidden;overscroll-behavior-y:none}}
#shiva-launch-shell{{
  position:fixed;inset:0;z-index:2147483647;background:{NAVY};
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  opacity:1;visibility:visible;pointer-events:auto;
  transition:opacity 220ms ease-out,visibility 0s linear 220ms;
}}
#shiva-launch-shell.shiva-launch-hide{{opacity:0;visibility:hidden;pointer-events:none}}
#shiva-launch-shell img{{
  display:block;width:min(88vw,520px);height:auto;max-height:82dvh;
  object-fit:contain;object-position:center;transform:none;
  background:transparent!important;border:0!important;border-radius:0!important;
  box-shadow:none!important;mix-blend-mode:lighten!important;
}}
</style>
""".strip()

_BODY_SHELL = (
    f'<div id="shiva-launch-shell" aria-label="Shiva loading">'
    f'<img src="{STATIC_TROPHY_URL}" alt="THE SHIVA trophy" fetchpriority="high" decoding="sync">'
    "</div>"
)

_READY_SCRIPT = r"""
<script id="shiva-first-paint-controller">
(() => {
  const shell = document.getElementById("shiva-launch-shell");
  const root = document.getElementById("root");
  if (!shell || !root) return;

  const started = performance.now();
  const minimumVisibleMs = 2200;
  let finished = false;

  const appReady = () =>
    Boolean(document.querySelector(".app-top")) &&
    Boolean(document.querySelector('[data-testid="stAppViewContainer"]'));

  const finish = () => {
    if (finished) return;
    finished = true;
    const wait = Math.max(0, minimumVisibleMs - (performance.now() - started));
    window.setTimeout(() => {
      shell.classList.add("shiva-launch-hide");
      window.setTimeout(() => shell.remove(), 260);
    }, wait);
  };

  const observer = new MutationObserver(() => {
    if (appReady()) {
      observer.disconnect();
      finish();
    }
  });
  observer.observe(root, {childList: true, subtree: true});

  if (appReady()) {
    observer.disconnect();
    finish();
  }

  // Never strand a user on the launch shell if a future DOM change alters the
  // readiness marker. Runtime errors remain visible after the shell clears.
  window.setTimeout(() => {
    observer.disconnect();
    finish();
  }, 7000);
})();
</script>
""".strip()


def _inject_first_paint(html: str) -> str:
    """Inject the dark launch shell at the earliest safe points in the document."""
    if 'id="shiva-first-paint"' in html:
        return html

    html = html.replace("<title>Streamlit</title>", "<title>Shiva</title>", 1)
    # Paint the document canvas in the opening tags themselves. This is parsed
    # before any linked Streamlit styles or scripts, preventing a light frame
    # while the browser builds the head.
    html = re.sub(
        r"<html(?P<attrs>[^>]*)>",
        lambda match: f'<html{match.group("attrs")} style="background:{NAVY};color-scheme:dark">',
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<head(?P<attrs>[^>]*)>",
        lambda match: f"<head{match.group('attrs')}>\n{_HEAD_SHELL}",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if "</head>" in html and 'id="shiva-first-paint"' not in html:
        html = html.replace("</head>", f"{_HEAD_SHELL}\n</head>", 1)
    html = re.sub(
        r"<body(?P<attrs>[^>]*)>",
        lambda match: f'<body{match.group("attrs")} style="background:{NAVY};margin:0;color-scheme:dark">\n{_BODY_SHELL}',
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if "</body>" in html:
        html = html.replace("</body>", f"{_READY_SCRIPT}\n</body>", 1)
    return html


class _FirstPaintASGI:
    """ASGI middleware that modifies only the initial HTML document.

    WebSockets, Streamlit health endpoints, static assets, and application traffic pass
    through unchanged.
    """

    def __init__(self, inner: Callable[..., Awaitable[Any]]) -> None:
        self._inner = inner

    async def __call__(self, scope: dict[str, Any], receive: Callable[..., Any], send: Callable[..., Any]) -> None:
        if scope.get("type") != "http" or scope.get("path") not in ("", "/"):
            await self._inner(scope, receive, send)
            return

        response_start: dict[str, Any] | None = None
        body_parts: list[bytes] = []

        async def capture(message: dict[str, Any]) -> None:
            nonlocal response_start
            message_type = message.get("type")

            if message_type == "http.response.start":
                response_start = message
                return

            if message_type != "http.response.body":
                await send(message)
                return

            body_parts.append(message.get("body", b""))
            if message.get("more_body", False):
                return

            start = response_start
            if start is None:
                raise RuntimeError("Streamlit ASGI response body arrived before response start")

            headers = list(start.get("headers", []))
            content_type = next(
                (
                    value.decode("latin-1")
                    for key, value in headers
                    if key.lower() == b"content-type"
                ),
                "",
            )
            body = b"".join(body_parts)

            if start.get("status") == 200 and "text/html" in content_type.lower():
                text = body.decode("utf-8")
                body = _inject_first_paint(text).encode("utf-8")
                headers = [
                    (key, value)
                    for key, value in headers
                    if key.lower() != b"content-length"
                ]
                headers.append((b"content-length", str(len(body)).encode("ascii")))

            await send({**start, "headers": headers})
            await send({"type": "http.response.body", "body": body, "more_body": False})

        await self._inner(scope, receive, capture)


_streamlit_app = st.App("streamlit_app.py")
app = _FirstPaintASGI(_streamlit_app)
