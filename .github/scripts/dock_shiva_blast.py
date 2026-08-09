from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Treat blast as normal in-app navigation so the startup splash does not replay.
s=s.replace('(\"page\",\"player\",\"draft\",\"queue_add\")','(\"page\",\"player\",\"draft\",\"queue_add\",\"blast\")',1)

# Add compact header action styling once.
css_anchor='.work-note b{color:#fff}\n'
css_add='''.work-note b{color:#fff}\n.app-actions{display:flex;align-items:center;gap:6px;flex:0 0 auto}.shiva-blast-head{display:inline-flex;align-items:center;justify-content:center;height:28px;padding:0 8px;border-radius:999px;border:1px solid rgba(255,74,102,.55);background:linear-gradient(135deg,#c81936,#7e0c22);color:#fff!important;text-decoration:none!important;font-size:9px;font-weight:950;letter-spacing:.25px;white-space:nowrap}.shiva-blast-head:active{transform:scale(.96)}\n'''
if '.shiva-blast-head{' not in s and css_anchor in s:
    s=s.replace(css_anchor,css_add,1)

old_header="new_header = '''def app_header():\\n    live=rankings_status==\"CONNECTED\"\\n    st.markdown(f'<div class=\"app-top\"><div class=\"brand-wrap\"><div class=\"brand-badge\">🏆</div><div><div class=\"brand-title\">SHIVA COMMAND CENTER</div><div class=\"brand-sub\">Fantasy Football Intelligence</div></div></div><div class=\"data-status\">● {\"DATA LIVE\" if live else \"DATA FALLBACK\"}</div></div>',unsafe_allow_html=True)\\n'''"
old_header_with_call="new_header = '''def app_header():\\n    live=rankings_status==\"CONNECTED\"\\n    st.markdown(f'<div class=\"app-top\"><div class=\"brand-wrap\"><div class=\"brand-badge\">🏆</div><div><div class=\"brand-title\">SHIVA COMMAND CENTER</div><div class=\"brand-sub\">Fantasy Football Intelligence</div></div></div><div class=\"data-status\">● {\"DATA LIVE\" if live else \"DATA FALLBACK\"}</div></div>',unsafe_allow_html=True)\\n    _home_shiva_blast()\\n'''"
new_header="new_header = '''def app_header():\\n    live=rankings_status==\"CONNECTED\"\\n    blast=\'<a class=\"shiva-blast-head\" href=\"?page=Home&blast=1\" target=\"_self\">⚡ BLAST</a>\' if str(st.query_params.get(\"page\") or \"Home\")==\"Home\" else \"\"\\n    st.markdown(f'<div class=\"app-top\"><div class=\"brand-wrap\"><div class=\"brand-badge\">🏆</div><div><div class=\"brand-title\">SHIVA COMMAND CENTER</div><div class=\"brand-sub\">Fantasy Football Intelligence</div></div></div><div class=\"app-actions\">{blast}<div class=\"data-status\">● {\"DATA LIVE\" if live else \"DATA FALLBACK\"}</div></div></div>',unsafe_allow_html=True)\\n'''"
if old_header_with_call in s:
    s=s.replace(old_header_with_call,new_header,1)
elif old_header in s:
    s=s.replace(old_header,new_header,1)
else:
    raise SystemExit('Current header transform not found; refusing unsafe patch')

# Replace the always-floating trigger with a video overlay that exists only after the docked button is tapped.
start=s.index("new_home = r'''def _home_shiva_blast():")
fn_start=s.index('def _home_shiva_blast():',start)
fn_end=s.index('\\ndef _home_nfl_news():',fn_start)
new_fn=r'''def _home_shiva_blast():
    if str(st.query_params.get("blast") or "")!="1":return
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;height:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      #stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(2,7,12,.68);backdrop-filter:blur(5px);padding:58px 16px 20px;box-sizing:border-box}
      #blastVideo{display:block;width:auto;max-width:min(92vw,430px);height:auto;max-height:78vh;object-fit:contain;border-radius:16px;background:#000;box-shadow:0 18px 55px rgba(0,0,0,.62)}
      #closeBlast{position:fixed;top:14px;right:14px;height:32px;padding:0 10px;border-radius:999px;border:1px solid rgba(255,112,130,.55);background:#7e0c22;color:#fff!important;text-decoration:none!important;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:950}
    </style>
    <div id="stage"><a id="closeBlast" href="?page=Home" target="_parent">✕ CLOSE</a><video id="blastVideo" playsinline autoplay preload="auto"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    <script>
      try{const f=window.frameElement;if(f){f.style.position='fixed';f.style.inset='0';f.style.width='100vw';f.style.height='100dvh';f.style.zIndex='2147483000';f.style.border='0';f.style.background='transparent';}}catch(e){}
      const v=document.getElementById('blastVideo');v.muted=false;const p=v.play();if(p&&p.catch)p.catch(()=>{v.controls=true;});
    </script>
    """,height=1,scrolling=False)
'''
s=s[:fn_start]+new_fn+s[fn_end:]

# Ensure Home renders the blast overlay handler once.
if '    _home_shiva_blast()\n    st.markdown(\'<div class="quick-grid">\'' not in s:
    s=s.replace('    st.markdown(\'<div class="quick-grid">\'', '    _home_shiva_blast()\n    st.markdown(\'<div class="quick-grid">\'', 1)

p.write_text(s,encoding='utf-8')
