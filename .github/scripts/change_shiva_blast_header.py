from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')
start = s.index('def _home_shiva_blast():')
end = s.index('\ndef _home_nfl_news():', start)
block = s[start:end]

# Only two corrections: remove the brain/icon text and pin the closed control
# to the exact top-right corner of the app header area.
block = block.replace('🧠 SHIVA BLAST', 'SHIVA BLAST')
block = block.replace('⚡ SHIVA BLAST', 'SHIVA BLAST')
block = block.replace("frame.style.top='6px';frame.style.right='8px'", "frame.style.top='0';frame.style.right='0'")
block = block.replace("frame.style.top='8px';frame.style.right='8px'", "frame.style.top='0';frame.style.right='0'")

s = s[:start] + block + s[end:]
marker = "mobile_css = r'''"
if '.data-status{display:none!important}' not in s:
    s = s.replace(marker, marker + "\n.data-status{display:none!important}\n", 1)
p.write_text(s, encoding='utf-8')

assert '🧠 SHIVA BLAST' not in block
assert '⚡ SHIVA BLAST' not in block
assert '>SHIVA BLAST<' in block or "textContent='SHIVA BLAST'" in block
assert "frame.style.top='0';frame.style.right='0'" in block
assert '.data-status{display:none!important}' in s
