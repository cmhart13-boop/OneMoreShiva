from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Put the Shiva Blast component in the permanent header area rather than inside Home content.
old_header="new_header = '''def app_header():\\n    live=rankings_status==\"CONNECTED\"\\n    st.markdown(f'<div class=\"app-top\"><div class=\"brand-wrap\"><div class=\"brand-badge\">🏆</div><div><div class=\"brand-title\">SHIVA COMMAND CENTER</div><div class=\"brand-sub\">Fantasy Football Intelligence</div></div></div><div class=\"data-status\">● {\"DATA LIVE\" if live else \"DATA FALLBACK\"}</div></div>',unsafe_allow_html=True)\\n'''"
new_header="new_header = '''def app_header():\\n    live=rankings_status==\"CONNECTED\"\\n    st.markdown(f'<div class=\"app-top\"><div class=\"brand-wrap\"><div class=\"brand-badge\">🏆</div><div><div class=\"brand-title\">SHIVA COMMAND CENTER</div><div class=\"brand-sub\">Fantasy Football Intelligence</div></div></div><div class=\"data-status\">● {\"DATA LIVE\" if live else \"DATA FALLBACK\"}</div></div>',unsafe_allow_html=True)\\n    _home_shiva_blast()\\n'''"
if old_header not in s:
    raise SystemExit('header anchor not found')
s=s.replace(old_header,new_header,1)

# Remove the old Home-content invocation so there is only one Shiva Blast control.
s=s.replace('    _home_shiva_blast()\n    st.markdown(\'<div class="quick-grid">\'', '    st.markdown(\'<div class="quick-grid">\'', 1)

# Make the component a small docked control next to the header data-status badge.
s=s.replace("#shivaBlast{position:fixed;top:0;right:0;width:122px;height:40px", "#shivaBlast{position:fixed;top:8px;right:112px;width:94px;height:30px", 1)
s=s.replace("font-size:12px;letter-spacing:.2px", "font-size:9px;letter-spacing:.1px", 1)
s=s.replace("#shivaBlast.playing{top:14px;right:14px;width:112px", "#shivaBlast.playing{top:8px;right:112px;width:94px", 1)
s=s.replace("f.style.top='58px';f.style.right='12px';f.style.left='auto';f.style.bottom='auto';f.style.width='122px';f.style.height='40px'", "f.style.top='8px';f.style.right='112px';f.style.left='auto';f.style.bottom='auto';f.style.width='94px';f.style.height='30px'", 1)

p.write_text(s,encoding='utf-8')
