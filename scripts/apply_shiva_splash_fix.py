from pathlib import Path

p = Path('app_runtime.py')
s = p.read_text(encoding='utf-8')

start = s.index('# -----------------------------------------------------------------------------\n# ORIGINAL SHIVA TROPHY')
end = s.index('# -----------------------------------------------------------------------------\n# CANONICAL FIRST PAINT', start)
new_asset = '''# -----------------------------------------------------------------------------
# CANONICAL SHIVA LOGO — repo asset is the single source of truth
# -----------------------------------------------------------------------------
SHIVA_LOGO_FILE = Path(__file__).with_name("D7E70C85-998B-46E2-B9D8-6E02615CF194.png")
if not SHIVA_LOGO_FILE.exists():
    raise RuntimeError("Canonical Shiva logo asset is missing")
_shiva_logo_b64 = base64.b64encode(SHIVA_LOGO_FILE.read_bytes()).decode("ascii")
SHIVA_MARK_NEW = f'''<img class="shiva-trophy-mark" src="data:image/png;base64,{_shiva_logo_b64}" alt="THE SHIVA trophy">'''

# Replace the legacy embedded trophy assignment in app_core with the canonical repo asset.
_trophy_pattern = re.compile(r'SHIVA_MARK\\s*=\\s*f?"""<img class="shiva-trophy-mark" src="data:image/jpeg;base64,([A-Za-z0-9+/=]+)" alt="THE SHIVA trophy">"""')
_trophy_matches = list(_trophy_pattern.finditer(code))
if len(_trophy_matches) != 1:
    raise RuntimeError(f"Shiva trophy contract expected 1 legacy SHIVA_MARK, found {len(_trophy_matches)}")
_trophy_match = _trophy_matches[0]
_trophy_assignment = 'SHIVA_MARK = ' + repr(SHIVA_MARK_NEW)
code = code[:_trophy_match.start()] + _trophy_assignment + code[_trophy_match.end():]

'''
s = s[:start] + new_asset + s[end:]

s = s.replace('animation:shivaSplashGone 0s linear 2.5s forwards', 'animation:shivaSplashGone 0s linear 2.6s forwards')
s = s.replace('width:min(52vw,225px)!important;height:auto!important;max-height:52vh!important', 'width:min(88vw,520px)!important;height:auto!important;max-height:82vh!important')

# Hide every known Streamlit floating badge/widget/chrome variant that can overlap the app.
s = s.replace(
    '#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],[data-testid="stDeployButton"],.stAppDeployButton,button[title="Manage app"],a[aria-label="Manage app"]',
    '#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stDecoration"],[data-testid="stDeployButton"],[data-testid="stAppDeployButton"],[data-testid="stViewerBadge"],[data-testid="stAppCreatorAvatar"],.stAppDeployButton,[class*="viewerBadge"],[class*="ViewerBadge"],[class*="stDeployButton"],button[title="Manage app"],button[aria-label="Manage app"],a[aria-label="Manage app"],a[href*="streamlit.io/cloud"],a[href*="share.streamlit.io"]'
)

# Guardrails: exact requested behavior.
assert 'D7E70C85-998B-46E2-B9D8-6E02615CF194.png' in s
assert 'animation:shivaSplashGone 0s linear 2.6s forwards' in s
assert 'width:min(88vw,520px)!important' in s
assert '2.5s forwards' not in s
assert '[data-testid="stViewerBadge"]' in s
p.write_text(s, encoding='utf-8')
