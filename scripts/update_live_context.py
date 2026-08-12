from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
DATA.mkdir(exist_ok=True)
NEWS_JSON=DATA/'live_news.json'
INJURY_CSV=DATA/'injury_mentions.csv'

INJURY_TERMS=(
    'injury','injured','questionable','doubtful','out ','ruled out','hamstring','ankle','knee','shoulder','back ','concussion','groin','calf','quad','foot ','wrist','elbow','hip ','illness','limited practice','did not practice','dnp','ir ','injured reserve'
)


def get_json(url:str):
    req=Request(url,headers={'User-Agent':'Mozilla/5.0 (One More Shiva verified collector)'})
    with urlopen(req,timeout=15) as resp:return json.loads(resp.read().decode('utf-8'))


def main():
    now=datetime.now(timezone.utc).isoformat()
    news=get_json('https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100')
    articles=news.get('articles',[]) if isinstance(news,dict) else []
    compact=[]
    mentions=[]
    for a in articles:
        headline=str(a.get('headline') or '').strip();desc=str(a.get('description') or '').strip()
        links=a.get('links',{}) or {};url=(links.get('web',{}) or {}).get('href') or (links.get('mobile',{}) or {}).get('href') or ''
        published=str(a.get('published') or a.get('lastModified') or '')
        item={'captured_at':now,'published':published,'headline':headline,'description':desc,'url':url}
        compact.append(item)
        hay=(headline+' '+desc).casefold()
        if any(term in hay for term in INJURY_TERMS):mentions.append(item)
    NEWS_JSON.write_text(json.dumps({'captured_at':now,'articles':compact},indent=2),encoding='utf-8')

    existing=[];seen=set()
    if INJURY_CSV.exists():
        with INJURY_CSV.open(newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                key=(row.get('published',''),row.get('headline',''),row.get('url',''))
                if key not in seen:existing.append(row);seen.add(key)
    for row in mentions:
        key=(row['published'],row['headline'],row['url'])
        if key not in seen:existing.append(row);seen.add(key)
    existing=existing[-3000:]
    with INJURY_CSV.open('w',newline='',encoding='utf-8') as f:
        fields=['captured_at','published','headline','description','url'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(existing)
    print(f'LIVE CONTEXT PASS articles={len(compact)} injury_mentions={len(existing)}')

if __name__=='__main__':main()
