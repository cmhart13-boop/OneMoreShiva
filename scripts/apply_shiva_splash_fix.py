from pathlib import Path

# Runtime is repaired. Align the regression contract with the canonical Shiva logo.
t = Path('tests/test_no_flash_contract.py')
s = t.read_text(encoding='utf-8')
s = s.replace('def test_splash_is_exactly_two_point_five_seconds():', 'def test_splash_is_exactly_two_point_six_seconds():')
s = s.replace('assert "animation:shivaSplashGone 0s linear 2.5s forwards" in css', 'assert "animation:shivaSplashGone 0s linear 2.6s forwards" in css')
s = s.replace('assert "FDBBC710-B60A-4DA4-9582-F52D6210DB18.png" not in source', 'assert "D7E70C85-998B-46E2-B9D8-6E02615CF194.png" in source')
s = s.replace('assert "width:min(52vw,225px)!important" in source', 'assert "width:min(88vw,520px)!important" in source')
s = s.replace('def test_trophy_asset_conversion_is_scoped_to_exact_shiva_mark_assignment():', 'def test_canonical_shiva_logo_is_scoped_to_exact_shiva_mark_assignment():')
s = s.replace('assert "expected 1 approved SHIVA_MARK" in source', 'assert "expected 1 legacy SHIVA_MARK" in source')
s = s.replace('assert "Unable to prepare approved Shiva trophy asset" in source', 'assert "Canonical Shiva logo asset is missing" in source')
s = s.replace('assert "_trophy_match.start()" in source', 'assert "SHIVA_LOGO_FILE" in source')
s = s.replace('assert "_trophy_match.end()" in source', 'assert "D7E70C85-998B-46E2-B9D8-6E02615CF194.png" in source')
t.write_text(s, encoding='utf-8')
# trigger alignment
