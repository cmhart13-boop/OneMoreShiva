from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')
start=s.index('def _home_nfl_news():')
end=s.index('\ndef home():',start)

new_fn=r'''def _home_nfl_news():
    st.markdown("#### Fantasy News")
    try:
        import json as _json
        from urllib.request import Request as _Request, urlopen as _urlopen

        req=_Request(
            "https://now.core.api.espn.com/v1/sports/news?limit=30&sport=football&leagues=nfl",
            headers={"User-Agent":"Mozilla/5.0 (iPhone; Shiva Fantasy Football)"},
        )
        with _urlopen(req,timeout=12) as resp:
            data=_json.loads(resp.read().decode("utf-8"))

        articles=[]
        seen=set()
        for a in data.get("headlines") or []:
            if str(a.get("type") or "").casefold() != "story":
                continue
            headline=str(a.get("headline") or a.get("title") or "").strip()
            links=a.get("links") or {}
            web=(
                (links.get("web") or {}).get("href")
                or ((links.get("web") or {}).get("self") or {}).get("href")
                or (links.get("mobile") or {}).get("href")
            )
            img=next(
                (x.get("url") for x in (a.get("images") or []) if isinstance(x,dict) and x.get("url")),
                None,
            )
            if not headline or not web or not img or "espn.com" not in str(web) or web in seen:
                continue
            seen.add(web)
            description=str(a.get("description") or "").strip()
            articles.append((headline,web,img,description))
            if len(articles)==4:
                break

        if len(articles)<4:
            st.caption("Fantasy News is temporarily unavailable from ESPN.")
            return

        cards=[]
        for headline,web,img,description in articles:
            h=html.escape(headline)
            u=html.escape(web,quote=True)
            im=html.escape(img,quote=True)
            d=html.escape(description)
            desc=f'<div class="fantasy-news-desc">{d}</div>' if d else ''
            cards.append(
                f'<a class="fantasy-news-card" href="{u}" target="_blank" rel="noopener noreferrer">'
                f'<div class="fantasy-news-img"><img src="{im}" alt=""></div>'
                f'<div class="fantasy-news-body"><div class="fantasy-news-headline">{h}</div>{desc}'
                f'<div class="fantasy-news-meta">ESPN · Fantasy Football</div></div></a>'
            )

        css='''<style>
        .fantasy-news-list{display:flex;flex-direction:column;gap:9px;margin:7px 0 14px}
        .fantasy-news-card{display:grid;grid-template-columns:108px minmax(0,1fr);overflow:hidden;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #253644;border-radius:9px;min-height:84px}
        .fantasy-news-img{width:108px;min-height:84px;background:#172430;overflow:hidden}
        .fantasy-news-img img{display:block;width:100%;height:100%;object-fit:cover}
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

s=s[:start]+new_fn+s[end:]
p.write_text(s,encoding='utf-8')

block=s[s.index('def _home_nfl_news():'):s.index('\ndef home():',s.index('def _home_nfl_news():'))]
assert 'now.core.api.espn.com/v1/sports/news?limit=30&sport=football&leagues=nfl' in block
assert 'data.get("headlines")' in block
assert 'if len(articles)==4:' in block
assert 'target="_blank"' in block
assert 'x.get("url")' in block
assert 'site.api.espn.com/apis/site/v2/sports/football/nfl/news' not in block
print('ESPN NOW NEWS SOURCE APPLIED')
