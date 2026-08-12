from pathlib import Path
import ast

root=Path(__file__).resolve().parents[1]
p=root/'app_core.py'
s=p.read_text(encoding='utf-8')

s=s.replace('    st.markdown("#### Latest ESPN Fantasy Football")','    st.markdown(\'<div class="home-fantasy-news-title">Fantasy News</div>\',unsafe_allow_html=True)',1)
s=s.replace('<div class="quick-title">Ask Shiva</div><div class="quick-sub">Draft and player intelligence</div>','<div class="quick-title">Shiva Lab</div><div class="quick-sub">Compare players and inspect the evidence</div>',1)
s=s.replace('href="{page_href("Shiva")}"','href="{page_href("Analytics")}"',1)

p.write_text(s,encoding='utf-8')
ast.parse(s)
assert 'Latest ESPN Fantasy Football' not in s
assert 'home-fantasy-news-title' in s
assert 'Shiva Lab' in s
assert 'Draft-Coach' not in s
print('FINAL SHIVA PRODUCT CLEANUP PASSED')
