"""One More Shiva production entrypoint.

Global shell recovery preprocessor:
- preserves app_core.py as the product baseline
- replaces only Shiva identity + primary bottom navigation at runtime
"""
from pathlib import Path
import re

SHIVA_LOGO_B64 = "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"

core = Path(__file__).with_name("app_core.py")
code = core.read_text(encoding="utf-8")

mark = 'SHIVA_MARK = f"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,{SHIVA_LOGO_B64}" alt="The Shiva trophy">"""'

code, n_mark = re.subn(
    r'SHIVA_MARK\s*=\s*r?""".*?</svg>"""',
    mark,
    code,
    count=1,
    flags=re.S,
)
if n_mark != 1:
    raise RuntimeError(f"Global shell recovery expected one Shiva mark, found {n_mark}")

new_nav = r"""def bottom_nav(active:str):
    active = "Home" if active == "Shiva" else active
    items = [("Home", None), ("Draft", "◫"), ("Guide", "▤"), ("Coach", "✦")]
    links = []
    for page_name, icon in items:
        active_class = "active" if active == page_name else ""
        if page_name == "Home":
            icon_html = f'<span class="nav-icon shiva-home-navicon">{SHIVA_MARK}</span>'
        else:
            icon_html = f'<span class="nav-icon">{icon}</span>'
        links.append(
            f'<a class="{active_class}" href="{page_href(page_name)}" target="_self">'
            f'{icon_html}<span>{page_name}</span></a>'
        )
    st.markdown(
        f'<nav class="bottom-nav" aria-label="Primary navigation">{"".join(links)}</nav>',
        unsafe_allow_html=True,
    )
"""

code, n_nav = re.subn(
    r'def bottom_nav\(active:str\):.*?\n\ndef screen_head',
    new_nav + "\ndef screen_head",
    code,
    count=1,
    flags=re.S,
)
if n_nav != 1:
    raise RuntimeError(f"Global shell recovery expected one bottom nav, found {n_nav}")

code = code.replace(".bottom-nav{display:none!important}", ".bottom-nav{display:grid!important}", 1)

shell_css = r"""
/* GLOBAL SHIVA SHELL RECOVERY - protected scope */
.brand-badge .shiva-trophy-mark{display:block!important;width:58px!important;height:70px!important;object-fit:contain!important;border-radius:0!important;filter:drop-shadow(0 5px 8px rgba(0,0,0,.32))!important}
.bottom-nav{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important}
.bottom-nav a{display:flex!important;min-width:0!important}
.bottom-nav .shiva-home-navicon{width:34px!important;height:34px!important;overflow:hidden!important}
.bottom-nav .shiva-home-navicon .shiva-trophy-mark{width:34px!important;height:34px!important;object-fit:contain!important;filter:none!important}
"""
code = code.replace("\n</style>\'\'\'", "\n" + shell_css + "\n</style>\'\'\'", 1)

exec(compile(code, str(core), "exec"), globals(), globals())
