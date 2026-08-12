from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
core_path = ROOT / "app_core.py"
code = core_path.read_text(encoding="utf-8")

mark = '''SHIVA_MARK = f"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,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" alt="The Shiva trophy">"""'''
code, n1 = re.subn(r'SHIVA_MARK\s*=\s*r?""".*?</svg>"""', mark, code, count=1, flags=re.S)
if n1 != 1:
    raise SystemExit(f"SHIVA_MARK replacements={n1}")

new_nav = r'''def bottom_nav(active:str):
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
'''
code, n2 = re.subn(r'def bottom_nav\(active:str\):.*?\n\ndef screen_head', new_nav + "\ndef screen_head", code, count=1, flags=re.S)
if n2 != 1:
    raise SystemExit(f"bottom_nav replacements={n2}")

code = code.replace(".bottom-nav{display:none!important}", ".bottom-nav{display:grid!important}", 1)

extra = r'''
/* GLOBAL SHIVA SHELL RECOVERY - protected scope */
.brand-badge .shiva-trophy-mark{display:block!important;width:58px!important;height:70px!important;object-fit:contain!important;border-radius:0!important;filter:drop-shadow(0 5px 8px rgba(0,0,0,.32))!important}
.bottom-nav{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important}
.bottom-nav a{display:flex!important;min-width:0!important}
.bottom-nav .shiva-home-navicon{width:34px!important;height:34px!important;overflow:hidden!important}
.bottom-nav .shiva-home-navicon .shiva-trophy-mark{width:34px!important;height:34px!important;object-fit:contain!important;filter:none!important}
'''
needle = "\n</style>" + "'''"
if needle not in code:
    raise SystemExit("CSS terminator not found")
code = code.replace(needle, "\n" + extra + needle, 1)

core_path.write_text(code, encoding="utf-8")
print("GLOBAL SHELL PATCH APPLIED")
