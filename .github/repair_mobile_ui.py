from pathlib import Path

app = Path('app.py')
core = Path('app_core.py')

app_text = app.read_text(encoding='utf-8')
core_text = core.read_text(encoding='utf-8')

# Canonical header/nav live in app_core.py. Remove the old runtime replacement blocks from app.py.
nav_start = app_text.index("old_nav = 'def bottom_nav(active:str):")
nav_end = app_text.index("# Draft view selector remains directly below the Draft Room heading.", nav_start)
app_text = app_text[:nav_start] + app_text[nav_end:]

header_start = app_text.index("# Header: preserve existing header layout and mount Shiva Blast.")
header_end = app_text.index("# Shared internal-data-first Shiva engine.", header_start)
app_text = app_text[:header_start] + app_text[header_end:]

# Replace only the Shiva Blast component implementation inside the Home source block.
blast_start = app_text.index('def _home_shiva_blast():')
blast_end = app_text.index('\ndef _home_nfl_news():', blast_start)
new_blast = r'''def _home_shiva_blast():
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color-scheme:dark}
      #wrap{width:100%;box-sizing:border-box;background:transparent}
      #bar{display:flex;justify-content:flex-end;align-items:center;height:34px}
      #shivaBlast{width:104px;height:30px;border-radius:8px;border:1px solid rgba(255,92,112,.30);background:linear-gradient(135deg,rgba(166,21,43,.62),rgba(82,10,26,.40) 64%,rgba(28,11,18,.28));color:#fff;font-weight:900;font-size:9px;letter-spacing:.12px;cursor:pointer;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 4px 12px rgba(82,8,25,.12);backdrop-filter:blur(8px)}
      #shivaBlast.playing{background:linear-gradient(135deg,rgba(143,18,38,.78),rgba(63,8,20,.56));border-color:rgba(255,112,130,.38)}
      #shivaBlast:active{transform:translateY(1px)}
      #stage{display:none;margin-top:7px;width:100%;background:transparent}
      #stage.open{display:block}
      #blastVideo{display:block;width:100%;height:auto;max-height:68vh;object-fit:contain;border-radius:12px;background:#000;box-shadow:0 12px 34px rgba(0,0,0,.42);cursor:pointer}
    </style>
    <div id="wrap">
      <div id="bar"><button id="shivaBlast">⚡ SHIVA BLAST</button></div>
      <div id="stage"><video id="blastVideo" playsinline preload="auto"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    </div>
    <script>
      const btn=document.getElementById('shivaBlast');
      const stage=document.getElementById('stage');
      const video=document.getElementById('blastVideo');
      const frame=window.frameElement;
      let playing=false;
      const closedFrame=()=>{try{if(!frame)return;frame.style.position='fixed';frame.style.top='8px';frame.style.right='8px';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='104px';frame.style.height='34px';frame.style.zIndex='2147483000';frame.style.border='0';frame.style.background='transparent';frame.style.boxShadow='none';frame.style.margin='0';}catch(e){}};
      const openFrame=()=>{try{if(!frame)return;frame.style.position='relative';frame.style.top='auto';frame.style.right='auto';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='100%';frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';frame.style.zIndex='10';frame.style.border='0';frame.style.background='transparent';frame.style.margin='2px 0 8px';}catch(e){}};
      const syncOpenHeight=()=>{if(!playing||!frame)return;try{frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';}catch(e){}};
      const closeBlast=()=>{playing=false;video.pause();video.currentTime=0;video.controls=false;stage.classList.remove('open');btn.classList.remove('playing');btn.textContent='⚡ SHIVA BLAST';closedFrame();};
      const openBlast=()=>{playing=true;stage.classList.add('open');btn.classList.add('playing');btn.textContent='✕ STOP BLAST';openFrame();video.currentTime=0;video.muted=false;requestAnimationFrame(syncOpenHeight);const p=video.play();if(p&&p.catch)p.catch(()=>{video.controls=true;syncOpenHeight();});};
      btn.addEventListener('click',()=>playing?closeBlast():openBlast());
      video.addEventListener('click',closeBlast);
      video.addEventListener('ended',()=>setTimeout(closeBlast,100));
      video.addEventListener('loadedmetadata',syncOpenHeight);
      try{new ResizeObserver(syncOpenHeight).observe(document.getElementById('wrap'));}catch(e){}
      closedFrame();
    </script>
    """,height=34,scrolling=False)

'''
app_text = app_text[:blast_start] + new_blast + app_text[blast_end+1:]

# Keep the existing design untouched; only force a dark document background during mobile navigation.
flash_css = "\n/* MOBILE NAV TRANSITION: prevent white document flash between bottom-nav pages. */\nhtml,body{background:#071019!important;color-scheme:dark!important}.stApp,.stAppViewContainer,[data-testid=\"stAppViewContainer\"]{background:#071019!important}\n"
marker = "mobile_css = r'''"
if 'MOBILE NAV TRANSITION: prevent white document flash' not in app_text:
    app_text = app_text.replace(marker, marker + flash_css, 1)

# Make header/nav direct source of truth and add a dark transition shield on bottom-nav taps.
core_fn_start = core_text.index('def app_header():')
core_fn_end = core_text.index('def screen_head', core_fn_start)
direct_header_nav = r'''def app_header():
    live=rankings_status=="CONNECTED"
    st.markdown(f'<div class="app-top"><div class="brand-wrap"><div class="brand-badge">🏆</div><div><div class="brand-title">SHIVA</div><div class="brand-sub">Fantasy Football Intelligence</div></div></div><div class="data-status">● {"DATA LIVE" if live else "DATA FALLBACK"}</div></div>',unsafe_allow_html=True)
    _home_shiva_blast()

def bottom_nav(active:str):
    parts=[]
    shield="try{var d=document;d.documentElement.style.background='#071019';d.body.style.background='#071019';var o=d.getElementById('shiva-nav-shield');if(!o){o=d.createElement('div');o.id='shiva-nav-shield';o.style.cssText='position:fixed;inset:0;background:#071019;z-index:2147483646;pointer-events:none';d.body.appendChild(o)}}catch(e){}"
    for p in PAGES:
        label='Shiva IQ' if p=='Shiva' else p
        if p=='Shiva':
            icon='<span class="nav-icon shiva-iq-navicon"><svg class="shiva-iq-mark" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="#258cff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 51c2-7 2-10-1-14-3-4-4-9-3-14 2-9 10-15 20-15 11 0 20 8 20 19 0 6-2 10-6 14-2 2-3 5-3 10"/><path d="M23 18h9l4-4m-13 11h15l5-5m-20 12h12l5 5m-17 2h10l4 5m4-27h7m-6 8h10m-9 8h8"/><circle cx="36" cy="14" r="1.6" fill="#258cff"/><circle cx="43" cy="20" r="1.6" fill="#258cff"/><circle cx="40" cy="37" r="1.6" fill="#258cff"/><circle cx="37" cy="44" r="1.6" fill="#258cff"/></g><path d="M20 27l2.4 5.1L28 34.5l-5.6 2.4L20 42l-2.4-5.1-5.6-2.4 5.6-2.4z" fill="#3b9cff"/></svg></span>'
        else:
            icon=f'<span class="nav-icon">{ICONS[p]}</span>'
        parts.append(f'<a class="{"active" if p==active else ""}" href="{page_href(p)}" target="_self" onclick="{shield}">{icon}<span>{label}</span></a>')
    st.markdown(f'<nav class="bottom-nav">{"".join(parts)}</nav>',unsafe_allow_html=True)

'''
core_text = core_text[:core_fn_start] + direct_header_nav + core_text[core_fn_end:]

if 'html,body{background:#071019!important;color-scheme:dark!important}' not in core_text:
    css_anchor = 'html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}'
    core_text = core_text.replace(css_anchor, css_anchor + 'html,body{background:#071019!important;color-scheme:dark!important}', 1)

app.write_text(app_text, encoding='utf-8')
core.write_text(core_text, encoding='utf-8')

checks = {
    'blast function present': 'def _home_shiva_blast():' in app_text,
    'blast mounted by header': '_home_shiva_blast()' in core_text[core_text.index('def app_header():'):core_text.index('def bottom_nav', core_text.index('def app_header():'))],
    'blast fixed top-right when closed': "frame.style.top='8px';frame.style.right='8px'" in app_text,
    'blast expands inline': "frame.style.position='relative'" in app_text and "#stage.open{display:block}" in app_text,
    'video tap closes blast': "video.addEventListener('click',closeBlast)" in app_text,
    'video end closes blast': "video.addEventListener('ended'" in app_text,
    'dark nav shield present': 'shiva-nav-shield' in core_text,
    'dark root background present': 'html,body{background:#071019!important;color-scheme:dark!important}' in core_text,
    'old nav runtime transformer removed': "old_nav = 'def bottom_nav(active:str):" not in app_text,
    'old header runtime transformer removed': '# Header: preserve existing header layout and mount Shiva Blast.' not in app_text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('FAILED SOURCE CHECKS: ' + ', '.join(failed))
print('SOURCE CHECKS PASSED')
for name in checks:
    print(' -', name)
