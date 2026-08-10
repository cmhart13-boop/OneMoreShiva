from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')
start = s.index('def _home_shiva_blast():')
end = s.index('\ndef _home_nfl_news():', start)
block = s[start:end]
block = block.replace("#shivaBlast{width:104px;height:30px;border-radius:8px;border:1px solid rgba(255,92,112,.30);background:linear-gradient(135deg,rgba(166,21,43,.62),rgba(82,10,26,.40) 64%,rgba(28,11,18,.28));", "#shivaBlast{width:122px;height:34px;border-radius:8px;border:1px solid rgba(74,156,255,.48);background:linear-gradient(135deg,rgba(37,140,255,.78),rgba(20,91,171,.62) 58%,rgba(11,48,91,.48));")
block = block.replace("#shivaBlast.playing{background:linear-gradient(135deg,rgba(143,18,38,.78),rgba(63,8,20,.56));border-color:rgba(255,112,130,.38)}", "#shivaBlast.playing{background:linear-gradient(135deg,rgba(32,125,230,.88),rgba(15,72,140,.72));border-color:rgba(104,181,255,.62)}")
block = block.replace('<div id="bar"><button id="shivaBlast">⚡ SHIVA BLAST</button></div>', '<div id="bar"><button id="shivaBlast">🧠 SHIVA BLAST</button></div>')
block = block.replace("frame.style.width='104px';frame.style.height='34px'", "frame.style.width='122px';frame.style.height='36px'")
block = block.replace("btn.textContent='⚡ SHIVA BLAST'", "btn.textContent='🧠 SHIVA BLAST'")
s = s[:start] + block + s[end:]
marker = "mobile_css = r'''"
if '.data-status{display:none!important}' not in s:
    s = s.replace(marker, marker + "\n.data-status{display:none!important}\n", 1)
p.write_text(s, encoding='utf-8')
assert '🧠 SHIVA BLAST' in block
assert 'rgba(37,140,255,.78)' in block
assert '.data-status{display:none!important}' in s
