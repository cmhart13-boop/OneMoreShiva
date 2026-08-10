from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# 1) Anchor Shiva Blast to the app content's literal top-right corner.
old="const frame=window.frameElement;\n      let playing=false;\n      const closedFrame=()=>{try{if(!frame)return;frame.style.position='absolute';frame.style.top='0';frame.style.right='0';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='122px';frame.style.height='36px';frame.style.zIndex='20';frame.style.border='0';frame.style.background='transparent';frame.style.boxShadow='none';frame.style.margin='0';}catch(e){}};\n      const openFrame=()=>{try{if(!frame)return;frame.style.position='relative';frame.style.top='auto';frame.style.right='auto';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='100%';frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';frame.style.zIndex='10';frame.style.border='0';frame.style.background='transparent';frame.style.margin='2px 0 8px';}catch(e){}};"
new="const frame=window.frameElement;\n      const host=frame ? (frame.closest('[data-testid=\\\"stElementContainer\\\"]') || frame.parentElement) : null;\n      let playing=false;\n      const closedFrame=()=>{try{if(host){host.style.position='absolute';host.style.top='0';host.style.right='0';host.style.left='auto';host.style.width='122px';host.style.zIndex='200';host.style.margin='0';host.style.padding='0';}if(frame){frame.style.position='relative';frame.style.top='0';frame.style.right='0';frame.style.left='auto';frame.style.width='122px';frame.style.height='36px';frame.style.border='0';frame.style.background='transparent';frame.style.margin='0';}}catch(e){}};\n      const openFrame=()=>{try{if(host){host.style.position='relative';host.style.top='auto';host.style.right='auto';host.style.left='auto';host.style.width='100%';host.style.zIndex='10';host.style.margin='0';}if(frame){frame.style.position='relative';frame.style.top='auto';frame.style.right='auto';frame.style.left='auto';frame.style.width='100%';frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';frame.style.zIndex='10';frame.style.border='0';frame.style.background='transparent';frame.style.margin='2px 0 8px';}}catch(e){}};"
if old not in s:
    raise SystemExit('Expected current Shiva Blast frame block not found; refusing broad edit')
s=s.replace(old,new,1)

# 2) Hide Streamlit's floating Manage app/deploy widget and establish the positioning context.
marker="mobile_css = r'''"
css='''\n.block-container{position:relative!important}\n.data-status{display:none!important}\n[data-testid="stAppDeployButton"],[data-testid="stToolbar"],[data-testid="stStatusWidget"],.stAppDeployButton,[aria-label="Manage app"],[title="Manage app"]{display:none!important;visibility:hidden!important;pointer-events:none!important}\n'''
if '[aria-label="Manage app"]' not in s:
    s=s.replace(marker,marker+css,1)

# 3) ESPN Fantasy News: remove the bad fantasy-keyword filter, take exactly four
# top ESPN feed stories, preserve ESPN links, and keep ESPN-provided thumbnails.
s=s.replace('https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100','https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=12',1)
s=s.replace('            hay=(headline+" "+description+" "+str(web)).casefold()\n            if "/fantasy/football/" not in hay and "fantasy football" not in hay:continue\n','',1)
s=s.replace('            articles.append((headline,web,img,description))\n        if not articles:','            articles.append((headline,web,img,description))\n            if len(articles)==4:break\n        if len(articles)<4:',1)
s=s.replace('            st.caption("Fantasy news is refreshing from ESPN.");return','            st.caption("Fantasy News is temporarily unavailable from ESPN.");return',1)

p.write_text(s,encoding='utf-8')

blast=s[s.index('def _home_shiva_blast():'):s.index('\ndef _home_nfl_news():',s.index('def _home_shiva_blast():'))]
news=s[s.index('def _home_nfl_news():'):s.index('\ndef home():',s.index('def _home_nfl_news():'))]
assert "host.style.top='0';host.style.right='0'" in blast
assert '🧠 SHIVA BLAST' not in blast and '⚡ SHIVA BLAST' not in blast
assert '[aria-label="Manage app"]' in s and '[data-testid="stAppDeployButton"]' in s
assert 'limit=12' in news and 'if len(articles)==4:break' in news
assert 'fantasy football" not in hay' not in news
assert 'target="_blank"' in news and 'candidate.get("url")' in news
print('THREE REQUESTED FIXES APPLIED')
