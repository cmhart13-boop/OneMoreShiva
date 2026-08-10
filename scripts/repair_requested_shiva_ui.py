from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')

# Repair corrupted bottom-nav transform without changing page layout.
start = s.find('old_nav =')
end = s.find('# Draft view selector remains directly below the Draft Room heading.', start)
if start != -1 and end != -1:
    old_nav_value = '''def bottom_nav(active:str):
    links=''.join(f'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self"><span class="nav-icon">{ICONS[p]}</span><span>{p}</span></a>' for p in PAGES);st.markdown(f'<nav class="bottom-nav">{links}</nav>',unsafe_allow_html=True)'''
    new_nav_value = '''def bottom_nav(active:str):
    parts=[]
    for p in PAGES:
        label='Shiva IQ' if p=='Shiva' else p
        if p=='Shiva':
            icon='<span class="nav-icon shiva-iq-navicon"><svg class="shiva-iq-mark" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="#258cff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 51c2-7 2-10-1-14-3-4-4-9-3-14 2-9 10-15 20-15 11 0 20 8 20 19 0 6-2 10-6 14-2 2-3 5-3 10"/><path d="M23 18h9l4-4m-13 11h15l5-5m-20 12h12l5 5m-17 2h10l4 5m4-27h7m-6 8h10m-9 8h8"/><circle cx="36" cy="14" r="1.6" fill="#258cff"/><circle cx="43" cy="20" r="1.6" fill="#258cff"/><circle cx="40" cy="37" r="1.6" fill="#258cff"/><circle cx="37" cy="44" r="1.6" fill="#258cff"/></g><path d="M20 27l2.4 5.1L28 34.5l-5.6 2.4L20 42l-2.4-5.1-5.6-2.4 5.6-2.4z" fill="#3b9cff"/></svg></span>'
        else:
            icon=f'<span class="nav-icon">{ICONS[p]}</span>'
        parts.append(f'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self">{icon}<span>{label}</span></a>')
    st.markdown(f'<nav class="bottom-nav">{"".join(parts)}</nav>',unsafe_allow_html=True)
'''
    nav_block = 'old_nav = ' + repr(old_nav_value) + '\nnew_nav = ' + repr(new_nav_value) + '\nif old_nav in source:\n    source=source.replace(old_nav,new_nav,1)\n\n'
    s = s[:start] + nav_block + s[end:]

# Repair corrupted header transform from earlier failed pass.
ht_start = s.find('# Header: move Command Center into the permanent Shiva branding row.')
if ht_start == -1:
    ht_start = s.find('# Header: preserve existing header layout and ensure Shiva Blast is mounted there.')
ht_end = s.find('# Shared internal-data-first Shiva engine.', ht_start)
if ht_start != -1 and ht_end != -1:
    header_value = '''def app_header():
    live=rankings_status=="CONNECTED"
    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">🏆</div><div><div class="brand-title"></div><div class="brand-sub">Fantasy Football Intelligence</div></div></div><div class="data-status">● {"DATA LIVE" if live else "DATA FALLBACK"}</div></div>',unsafe_allow_html=True)
    _home_shiva_blast()
'''
    header_transform = (
        '# Header: preserve existing header layout and mount Shiva Blast.\n'
        "header_start = source.index('def app_header():')\n"
        "header_end = source.index('\\ndef bottom_nav', header_start)\n"
        'new_header = ' + repr(header_value) + '\n'
        'source = source[:header_start] + new_header + source[header_end:]\n\n'
    )
    s = s[:ht_start] + header_transform + s[ht_end:]

# Replace the Shiva Blast implementation only. No other layout/card changes here.
blast_start = s.find('def _home_shiva_blast():')
blast_end = s.find('\ndef _home_nfl_news():', blast_start)
if blast_start != -1 and blast_end != -1:
    blast = '''def _home_shiva_blast():
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;height:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      #stage{position:fixed;inset:0;display:none;align-items:center;justify-content:center;background:rgba(2,7,12,.62);backdrop-filter:blur(4px);padding:58px 16px 20px;box-sizing:border-box}
      #stage.open{display:flex}
      #blastVideo{display:block;width:auto;max-width:min(92vw,430px);height:auto;max-height:78vh;object-fit:contain;border-radius:14px;background:#000;box-shadow:0 18px 55px rgba(0,0,0,.62)}
      #shivaBlast{position:fixed;top:8px;right:112px;width:94px;height:30px;border-radius:8px;border:1px solid rgba(255,92,112,.34);background:linear-gradient(135deg,rgba(174,22,45,.70),rgba(91,10,28,.46) 62%,rgba(31,12,20,.34));color:#fff;font-weight:900;font-size:9px;letter-spacing:.1px;cursor:pointer;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 4px 12px rgba(82,8,25,.15);backdrop-filter:blur(8px);z-index:5}
      #shivaBlast.playing{background:linear-gradient(135deg,rgba(145,19,39,.82),rgba(67,8,21,.62));border-color:rgba(255,112,130,.42)}
      #shivaBlast:active{transform:translateY(1px)}
    </style>
    <div id="stage"><video id="blastVideo" playsinline preload="auto"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    <button id="shivaBlast">⚡ SHIVA BLAST</button>
    <script>
      const btn=document.getElementById('shivaBlast');
      const stage=document.getElementById('stage');
      const video=document.getElementById('blastVideo');
      let playing=false;
      const frame=()=>window.frameElement;
      const floatFrame=()=>{try{const f=frame();if(!f)return;f.style.position='fixed';f.style.top='8px';f.style.right='112px';f.style.left='auto';f.style.bottom='auto';f.style.width='94px';f.style.height='30px';f.style.zIndex='2147483000';f.style.border='0';f.style.background='transparent';f.style.boxShadow='none';}catch(e){}};
      const overlayFrame=()=>{try{const f=frame();if(!f)return;f.style.position='fixed';f.style.inset='0';f.style.width='100vw';f.style.height='100dvh';f.style.zIndex='2147483000';f.style.border='0';f.style.background='transparent';}catch(e){}};
      const closeBlast=()=>{playing=false;video.pause();video.currentTime=0;stage.classList.remove('open');btn.classList.remove('playing');btn.textContent='⚡ SHIVA BLAST';floatFrame();};
      const openBlast=()=>{playing=true;overlayFrame();stage.classList.add('open');btn.classList.add('playing');btn.textContent='✕ STOP BLAST';video.currentTime=0;video.muted=false;const playPromise=video.play();if(playPromise&&playPromise.catch)playPromise.catch(()=>{video.controls=true;video.play().catch(()=>{});});};
      btn.addEventListener('click',()=>playing?closeBlast():openBlast());
      video.addEventListener('click',closeBlast);
      video.addEventListener('ended',()=>setTimeout(closeBlast,160));
      floatFrame();
    </script>
    """,height=1,scrolling=False)

'''
    s = s[:blast_start] + blast + s[blast_end:]

p.write_text(s, encoding='utf-8')
