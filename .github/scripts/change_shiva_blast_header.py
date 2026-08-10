from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')

# 1) Shiva Blast: replace the component itself so the CLOSED state is anchored
# to the actual top-right of the app content, not the viewport and not an offset iframe.
blast_start = s.index('def _home_shiva_blast():')
blast_end = s.index('\ndef _home_nfl_news():', blast_start)
new_blast = r'''def _home_shiva_blast():
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color-scheme:dark}
      #wrap{width:100%;box-sizing:border-box;background:transparent}
      #bar{display:flex;justify-content:flex-end;align-items:flex-start;height:34px}
      #shivaBlast{width:116px;height:32px;border-radius:7px;border:1px solid rgba(74,156,255,.46);background:linear-gradient(135deg,rgba(37,140,255,.76),rgba(20,91,171,.60) 58%,rgba(11,48,91,.46));color:#fff;font-weight:900;font-size:9px;letter-spacing:.15px;cursor:pointer;box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 3px 10px rgba(23,112,207,.14);padding:0 9px}
      #shivaBlast.playing{background:linear-gradient(135deg,rgba(32,125,230,.86),rgba(15,72,140,.70));border-color:rgba(104,181,255,.60)}
      #shivaBlast:active{transform:translateY(1px)}
      #stage{display:none;margin-top:7px;width:100%;background:transparent}
      #stage.open{display:block}
      #blastVideo{display:block;width:100%;height:auto;max-height:68vh;object-fit:contain;border-radius:12px;background:#000;box-shadow:0 12px 34px rgba(0,0,0,.42);cursor:pointer}
    </style>
    <div id="wrap">
      <div id="bar"><button id="shivaBlast" aria-label="Shiva Blast">SHIVA BLAST</button></div>
      <div id="stage"><video id="blastVideo" playsinline preload="auto"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    </div>
    <script>
      const btn=document.getElementById('shivaBlast');
      const stage=document.getElementById('stage');
      const video=document.getElementById('blastVideo');
      const frame=window.frameElement;
      const host=frame ? (frame.closest('[data-testid="stElementContainer"]') || frame.parentElement) : null;
      let playing=false;
      const closedFrame=()=>{try{
        if(host){host.style.position='absolute';host.style.top='0';host.style.right='0';host.style.left='auto';host.style.width='116px';host.style.zIndex='200';host.style.margin='0';host.style.padding='0';}
        if(frame){frame.style.position='relative';frame.style.top='0';frame.style.right='0';frame.style.left='auto';frame.style.width='116px';frame.style.height='34px';frame.style.border='0';frame.style.background='transparent';frame.style.margin='0';}
      }catch(e){}};
      const openFrame=()=>{try{
        if(host){host.style.position='relative';host.style.top='auto';host.style.right='auto';host.style.left='auto';host.style.width='100%';host.style.zIndex='10';host.style.margin='0';}
        if(frame){frame.style.position='relative';frame.style.top='auto';frame.style.right='auto';frame.style.left='auto';frame.style.width='100%';frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';frame.style.border='0';frame.style.background='transparent';frame.style.margin='2px 0 8px';}
      }catch(e){}};
      const syncOpenHeight=()=>{if(!playing||!frame)return;try{frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';}catch(e){}};
      const closeBlast=()=>{playing=false;video.pause();video.currentTime=0;video.controls=false;stage.classList.remove('open');btn.classList.remove('playing');btn.textContent='SHIVA BLAST';closedFrame();};
      const openBlast=()=>{playing=true;stage.classList.add('open');btn.classList.add('playing');btn.textContent='STOP BLAST';openFrame();video.currentTime=0;video.muted=false;requestAnimationFrame(syncOpenHeight);const p=video.play();if(p&&p.catch)p.catch(()=>{video.controls=true;syncOpenHeight();});};
      btn.addEventListener('click',()=>playing?closeBlast():openBlast());
      video.addEventListener('click',closeBlast);
      video.addEventListener('ended',()=>setTimeout(closeBlast,100));
      video.addEventListener('loadedmetadata',syncOpenHeight);
      try{new ResizeObserver(syncOpenHeight).observe(document.getElementById('wrap'));}catch(e){}
      closedFrame();
    </script>
    """,height=34,scrolling=False)
'''
s = s[:blast_start] + new_blast + s[blast_end:]

# 2) Hide Streamlit Community Cloud's floating Manage app/deploy UI and keep
# the app content as the positioning context for the header control.
marker = "mobile_css = r'''"
ui_css = """
.block-container{position:relative!important}
.data-status{display:none!important}
[data-testid=\"stAppDeployButton\"],[data-testid=\"stToolbar\"],[data-testid=\"stStatusWidget\"],.stAppDeployButton,[aria-label=\"Manage app\"],[title=\"Manage app\"]{display:none!important;visibility:hidden!important;pointer-events:none!important}
"""
if '[aria-label="Manage app"]' not in s:
    s = s.replace(marker, marker + "\n" + ui_css + "\n", 1)

# 3) Fantasy News: use ESPN's live site API, take the FIRST FOUR stories exactly,
# preserve the real ESPN article URLs, and show the article image thumbnail.
news_start = s.index('def _home_nfl_news():')
news_end = s.index('\ndef home():', news_start)
new_news = r'''def _home_nfl_news():
    st.markdown("#### Fantasy News")
    try:
        import json as _json
        from urllib.request import Request as _Request, urlopen as _urlopen

        endpoints=(
            "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=12",
            "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=12",
        )
        data=None
        for endpoint in endpoints:
            try:
                req=_Request(endpoint,headers={"User-Agent":"Mozilla/5.0 (iPhone; Shiva Fantasy Football)"})
                with _urlopen(req,timeout=10) as resp:
                    candidate=_json.loads(resp.read().decode("utf-8"))
                if candidate.get("articles"):
                    data=candidate
                    break
            except Exception:
                continue
        if not data:
            raise RuntimeError("ESPN news feed unavailable")

        articles=[]
        seen=set()
        for a in data.get("articles",[]):
            headline=str(a.get("headline") or "").strip()
            links=a.get("links",{}) or {}
            web=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            if not headline or not web or web in seen:
                continue
            seen.add(web)
            img=""
            for candidate in (a.get("images") or []):
                if isinstance(candidate,dict) and candidate.get("url"):
                    img=str(candidate.get("url"))
                    break
            description=str(a.get("description") or "").strip()
            articles.append((headline,web,img,description))
            if len(articles)==4:
                break

        if len(articles)<4:
            raise RuntimeError("ESPN returned fewer than four linked stories")

        cards=[]
        for headline,web,img,description in articles:
            h=html.escape(headline)
            u=html.escape(web,quote=True)
            d=html.escape(description)
            # ESPN normally supplies an image for these feed stories. If one is absent,
            # keep the card functional rather than dropping the article.
            media=(f'<div class="fantasy-news-img"><img src="{html.escape(img,quote=True)}" alt=""></div>' if img else '<div class="fantasy-news-img fantasy-news-img-empty"></div>')
            desc=f'<div class="fantasy-news-desc">{d}</div>' if d else ''
            cards.append(f'<a class="fantasy-news-card" href="{u}" target="_blank" rel="noopener noreferrer">{media}<div class="fantasy-news-body"><div class="fantasy-news-headline">{h}</div>{desc}<div class="fantasy-news-meta">ESPN · Fantasy Football</div></div></a>')

        css='''<style>
        .fantasy-news-list{display:flex;flex-direction:column;gap:9px;margin:7px 0 14px}
        .fantasy-news-card{display:grid;grid-template-columns:108px minmax(0,1fr);overflow:hidden;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #253644;border-radius:9px;min-height:84px}
        .fantasy-news-img{width:108px;min-height:84px;background:#172430;overflow:hidden}
        .fantasy-news-img img{display:block;width:100%;height:100%;object-fit:cover}
        .fantasy-news-img-empty{background:linear-gradient(145deg,#172430,#0e1821)}
        .fantasy-news-body{padding:9px 10px 10px;min-width:0}
        .fantasy-news-headline{font-size:13px;font-weight:950;line-height:1.27;color:#fff}
        .fantasy-news-desc{font-size:10.5px;line-height:1.32;color:#9eacb7;margin-top:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
        .fantasy-news-meta{font-size:9px;color:#8fa0ae;margin-top:7px;font-weight:850;text-transform:uppercase;letter-spacing:.15px}
        @media(max-width:430px){.fantasy-news-card{grid-template-columns:96px minmax(0,1fr);min-height:80px}.fantasy-news-img{width:96px;min-height:80px}.fantasy-news-headline{font-size:12.5px}.fantasy-news-desc{font-size:10px}}
        </style><div class="fantasy-news-list">''' + "".join(cards) + "</div>"
        st.markdown(css,unsafe_allow_html=True)
    except Exception:
        st.caption("Fantasy News is temporarily unavailable from ESPN.")
'''
s = s[:news_start] + new_news + s[news_end:]

p.write_text(s, encoding='utf-8')

# Source contracts for exactly the three requested changes.
assert '🧠 SHIVA BLAST' not in s and '⚡ SHIVA BLAST' not in s
blast=s[s.index('def _home_shiva_blast():'):s.index('\ndef _home_nfl_news():',s.index('def _home_shiva_blast():'))]
assert "host.style.top='0';host.style.right='0'" in blast
assert '>SHIVA BLAST<' in blast
assert '[aria-label="Manage app"]' in s and '[data-testid="stAppDeployButton"]' in s
news=s[s.index('def _home_nfl_news():'):s.index('\ndef home():',s.index('def _home_nfl_news():'))]
assert 'if len(articles)==4:' in news
assert 'fantasy football" not in hay' not in news
assert 'target="_blank"' in news
assert 'candidate.get("url")' in news
print('THREE REQUESTED FIXES APPLIED')
