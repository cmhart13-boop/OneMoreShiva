from pathlib import Path

source = Path(__file__).with_name("app_core.py").read_text(encoding="utf-8")

# OneMoreShiva is the single source of truth and production app moving forward.
# Preserve Draft Coach's final user-facing default: start mock drafts at Pick 1.
source=source.replace('"user_slot":3','"user_slot":1',1)

nav_css = r'''
/* Draft room primary navigation — scoped to the four live draft destinations. */
.st-key-draft_view{margin:2px 0 13px!important}
.st-key-draft_view div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:8px!important;width:100%!important}
.st-key-draft_view div[role="radiogroup"] label{position:relative!important;min-height:84px!important;border-radius:14px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:12px 4px 10px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:5px!important;margin:0!important;box-shadow:0 4px 14px rgba(0,0,0,.10)!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important;box-shadow:0 6px 18px rgba(213,22,54,.22)!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:14px;right:14px;bottom:7px;height:2px;border-radius:2px;background:#fff}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:12px!important;font-weight:950!important;white-space:nowrap!important;color:#aab8c4!important;line-height:1!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
.st-key-draft_view div[role="radiogroup"] label:nth-child(1) [data-testid="stMarkdownContainer"] p::before{content:"👥";display:block;font-size:22px;line-height:1.15;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(2) [data-testid="stMarkdownContainer"] p::before{content:"▦";display:block;font-size:25px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(3) [data-testid="stMarkdownContainer"] p::before{content:"☷";display:block;font-size:25px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(4) [data-testid="stMarkdownContainer"] p::before{content:"🛡";display:block;font-size:21px;line-height:1.15;margin-bottom:7px}
.player-shell.draft-player{grid-template-columns:44px minmax(0,1fr) 43px 43px 44px 58px!important}
.queue-inline{display:flex!important;align-items:center;justify-content:center;min-height:38px;border-radius:10px;background:#172430;border:1px solid #405363;color:#d9ff38!important;text-decoration:none!important;font-size:18px;font-weight:950}
@media(max-width:430px){.st-key-draft_view div[role="radiogroup"]{gap:6px!important}.st-key-draft_view div[role="radiogroup"] label{min-height:80px!important;padding-left:2px!important;padding-right:2px!important}.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important}.player-shell.draft-player{grid-template-columns:36px minmax(0,1fr) 37px 37px 40px 52px!important;padding-left:6px!important;padding-right:6px!important}}
'''
source=source.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)","\n"+nav_css+"\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)",1)

old='''def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    is_user_pick=pick_team(n,st.session_state.team_count)==st.session_state.user_slot
    if is_user_pick:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)
    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
'''
new='''def draft():
    screen_head("Draft Room","Live snake draft built for a phone.")
    # Primary draft navigation belongs directly under the Draft Room heading.
    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")
    slot_options=list(range(1,st.session_state.team_count+1))
    selected_slot=st.selectbox("Select your draft position",slot_options,index=slot_options.index(st.session_state.user_slot),format_func=lambda x:f"Pick #{x}",key="draft_slot_selector")
    if selected_slot!=st.session_state.user_slot:
        st.session_state.user_slot=selected_slot;st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()
    if not st.session_state.draft_log:sim_to_user()
    n=next_pick();rnd=(n-1)//st.session_state.team_count+1;st.markdown(f'<div class="draft-status"><div class="draft-chip"><span>Pick</span><b>{n}</b></div><div class="draft-chip"><span>Round</span><b>{rnd}</b></div><div class="draft-chip"><span>Your Slot</span><b>#{st.session_state.user_slot}</b></div></div>',unsafe_allow_html=True)
    is_user_pick=pick_team(n,st.session_state.team_count)==st.session_state.user_slot
    if is_user_pick:st.markdown(f'<div class="on-clock">🔥 YOU ARE ON THE CLOCK · PICK {n}</div>',unsafe_allow_html=True)
    render_shiva_draft_iq(available_df(),user_roster(),n,rnd,is_user_pick,draft_href)
'''
if old not in source: raise RuntimeError("Draft room source changed; refusing unsafe layout patch.")
source=source.replace(old,new,1)

old_news='''    st.markdown("#### Latest ESPN Fantasy Football")
    try:
        import json as _json
        from urllib.request import Request as _Request, urlopen as _urlopen
        req=_Request("https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=50",headers={"User-Agent":"Mozilla/5.0"})
        with _urlopen(req,timeout=8) as resp:data=_json.loads(resp.read().decode("utf-8"))
        articles=[]
        for a in data.get("articles",[]):
            text=(str(a.get("headline",""))+" "+str(a.get("description",""))).casefold()
            links=a.get("links",{}) or {};web=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            if not web:continue
            if "fantasy" not in text and "/fantasy/football/" not in web:continue
            imgs=a.get("images") or [];img=imgs[0].get("url") if imgs and isinstance(imgs[0],dict) else ""
            articles.append((str(a.get("headline") or "ESPN Fantasy Football"),web,img))
            if len(articles)==3:break
        for headline,web,img in articles:
            h=html.escape(headline);u=html.escape(web,quote=True);im=html.escape(img,quote=True)
            thumb=f'<img src="{im}" style="width:92px;height:64px;object-fit:cover;border-radius:9px;flex:0 0 92px" alt="">' if im else '<div style="width:92px;height:64px;border-radius:9px;background:#172430;flex:0 0 92px"></div>'
            st.markdown(f'<a href="{u}" target="_blank" style="display:flex;gap:10px;align-items:center;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #22313f;border-radius:13px;padding:8px 9px;margin-bottom:7px;min-height:80px">{thumb}<div style="min-width:0"><div style="font-size:11px;font-weight:900;line-height:1.25;color:#fff">{h}</div><div style="font-size:8px;color:#8fa0ae;margin-top:5px;font-weight:800">ESPN · Fantasy Football</div></div></a>',unsafe_allow_html=True)
        if not articles:st.caption("ESPN fantasy articles are temporarily unavailable.")
    except Exception:
        st.caption("ESPN fantasy articles are temporarily unavailable.")
'''
new_news='''    # ESPN news: 3 Fantasy Football stories + 2 general NFL stories.
    # Image-first card layout mirrors ESPN's visual hierarchy: thumbnail, headline, source.
    try:
        import json as _json
        from urllib.request import Request as _Request, urlopen as _urlopen

        def _espn_json(url):
            req=_Request(url,headers={"User-Agent":"Mozilla/5.0 (iPhone; Shiva Fantasy Football)","Accept":"application/json,text/plain,*/*"})
            with _urlopen(req,timeout=8) as resp:return _json.loads(resp.read().decode("utf-8"))

        def _link_from(obj):
            links=obj.get("links") or {}
            if isinstance(links,dict):
                for key in ("web","mobile"):
                    val=links.get(key) or {}
                    if isinstance(val,dict) and val.get("href"):return str(val["href"])
            for key in ("url","link","href"):
                if obj.get(key):return str(obj[key])
            return ""

        def _image_from(obj):
            imgs=obj.get("images") or obj.get("image") or []
            if isinstance(imgs,dict):imgs=[imgs]
            if isinstance(imgs,list):
                for im in imgs:
                    if isinstance(im,dict) and (im.get("url") or im.get("href")):return str(im.get("url") or im.get("href"))
            return ""

        def _collect(obj,out):
            if isinstance(obj,dict):
                title=str(obj.get("headline") or obj.get("title") or "").strip()
                url=_link_from(obj)
                if title and url and "espn.com" in url.casefold():
                    stamp=str(obj.get("published") or obj.get("publishedDate") or obj.get("date") or obj.get("lastModified") or obj.get("timestamp") or "")
                    out.append({"headline":title,"url":url,"image":_image_from(obj),"stamp":stamp,"description":str(obj.get("description") or "")})
                for v in obj.values():
                    if isinstance(v,(dict,list)):_collect(v,out)
            elif isinstance(obj,list):
                for v in obj:_collect(v,out)

        def _dedupe(items):
            seen=set();clean=[]
            for a in items:
                key=a["url"].split("?")[0]
                if key in seen:continue
                seen.add(key);clean.append(a)
            return clean

        def _render_news(items,label):
            cards=[]
            for a in items:
                h=html.escape(a["headline"]);u=html.escape(a["url"],quote=True);im=html.escape(a["image"],quote=True)
                cards.append(f"""<a class="espn-news-card" href="{u}" target="_blank" rel="noopener noreferrer"><div class="espn-news-img"><img src="{im}" alt=""></div><div class="espn-news-body"><div class="espn-news-headline">{h}</div><div class="espn-news-meta">ESPN · {label}</div></div></a>""")
            st.markdown("""<style>
            .espn-news-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:7px 0 14px}
            .espn-news-card{display:block;overflow:hidden;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #253644;border-radius:14px;box-shadow:0 5px 16px rgba(0,0,0,.16)}
            .espn-news-img{width:100%;aspect-ratio:16/9;background:#172430;overflow:hidden}
            .espn-news-img img{display:block;width:100%;height:100%;object-fit:cover}
            .espn-news-body{padding:9px 10px 10px}
            .espn-news-headline{font-size:11px;font-weight:950;line-height:1.25;color:#fff;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;min-height:41px}
            .espn-news-meta{font-size:8px;color:#8fa0ae;margin-top:7px;font-weight:850;text-transform:uppercase;letter-spacing:.25px}
            .espn-news-card:active{transform:scale(.985)}
            @media(max-width:360px){.espn-news-grid{gap:7px}.espn-news-body{padding:8px}.espn-news-headline{font-size:10px}}
            </style><div class="espn-news-grid">"""+''.join(cards)+"""</div>""",unsafe_allow_html=True)

        fantasy=[]
        try:
            fantasy_data=_espn_json("https://site.web.api.espn.com/apis/search/v2?limit=60&query=fantasy%20football")
            raw=[];_collect(fantasy_data,raw)
            for a in _dedupe(raw):
                txt=(a["headline"]+" "+a.get("description","")+" "+a["url"]).casefold()
                if ("fantasy football" in txt or "/fantasy/football/" in txt) and a.get("image"):fantasy.append(a)
            fantasy=sorted(fantasy,key=lambda a:a.get("stamp","") or "",reverse=True)[:3]
        except Exception:
            fantasy=[]

        nfl=[]
        try:
            nfl_data=_espn_json("https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=40")
            raw=[];_collect(nfl_data,raw)
            for a in _dedupe(raw):
                txt=(a["headline"]+" "+a.get("description","")+" "+a["url"]).casefold()
                if "/fantasy/football/" in txt or "fantasy football" in txt:continue
                if a.get("image"):nfl.append(a)
            nfl=sorted(nfl,key=lambda a:a.get("stamp","") or "",reverse=True)[:2]
        except Exception:
            nfl=[]

        st.markdown("#### Latest ESPN Fantasy Football")
        if fantasy:_render_news(fantasy,"Fantasy Football")
        else:st.caption("Fantasy headlines are refreshing.")
        st.markdown("#### Latest ESPN NFL")
        if nfl:_render_news(nfl,"NFL")
        else:st.caption("NFL headlines are refreshing.")
    except Exception:
        st.caption("ESPN headlines are refreshing.")
'''
if old_news not in source: raise RuntimeError("ESPN news source changed; refusing unsafe news patch.")
source=source.replace(old_news,new_news,1)

# Queue: add a compact + control beside DRAFT in every available-player row.
source=source.replace(
    'def draft_href(pid:str)->str:return f"?page=Draft&draft={quote_plus(pid)}"',
    'def draft_href(pid:str)->str:return f"?page=Draft&draft={quote_plus(pid)}"\ndef queue_href(pid:str)->str:return f"?page=Draft&queue_add={quote_plus(pid)}"',
    1,
)
source=source.replace(
    'draft_button=f\'<a class="draft-inline" href="{draft_href(str(r["id"]))}" target="_self">Draft</a>\' if draft_action else \'\'',
    'draft_button=(f\'<a class="queue-inline" href="{queue_href(str(r["id"]))}" target="_self" title="Add to Queue">＋</a><a class="draft-inline" href="{draft_href(str(r["id"]))}" target="_self">DRAFT</a>\') if draft_action else \'\'',
    1,
)
source=source.replace(
    'draft_param=str(qp.get("draft") or "")\nif draft_param:',
    'queue_param=str(qp.get("queue_add") or "")\nif queue_param:\n    if queue_param not in drafted_ids() and queue_param not in st.session_state.queue:st.session_state.queue.append(queue_param)\n    st.query_params.clear();st.query_params["page"]="Draft";st.rerun()\ndraft_param=str(qp.get("draft") or "")\nif draft_param:',
    1,
)

# Keep draft state recoverable: undo the user's latest pick plus all CPU picks after it.
source=source.replace(
    '    if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()\ndef player_db():',
    '''    ctrl1,ctrl2=st.columns(2)\n    with ctrl1:\n        if st.button("↶ Undo Last Pick",use_container_width=True,disabled=not bool(st.session_state.draft_log)):\n            last_user_idx=next((i for i in range(len(st.session_state.draft_log)-1,-1,-1) if st.session_state.draft_log[i]["team"]==st.session_state.user_slot),None)\n            if last_user_idx is not None:st.session_state.draft_log=st.session_state.draft_log[:last_user_idx]\n            else:st.session_state.draft_log=st.session_state.draft_log[:-1]\n            st.session_state["shiva_iq_recs"]=[];st.rerun()\n    with ctrl2:\n        if st.button("↻ Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["shiva_iq_recs"]=[];st.rerun()\ndef player_db():''',
    1,
)

# Shiva Blast: play the uploaded clip inline on the home screen when the button is pressed.
blast_block='''    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden}
      #shivaBlast{width:100%;min-height:46px;border-radius:12px;border:1px solid #ff3151;background:linear-gradient(145deg,#d51636,#8e0a22);color:#fff;font-weight:950;font-size:13px;cursor:pointer}
      #blastWrap{max-height:0;opacity:0;transform:translateY(-10px);overflow:hidden;transition:max-height .38s ease,opacity .28s ease,transform .38s ease;margin-top:0}
      #blastWrap.open{max-height:620px;opacity:1;transform:translateY(0);margin-top:10px}
      #blastVideo{display:block;width:100%;height:auto;max-height:560px;object-fit:contain;border-radius:14px;background:#000;box-shadow:0 8px 24px rgba(0,0,0,.28)}
    </style>
    <div><button id="shivaBlast">⚡ SHIVA BLAST</button></div>
    <div id="blastWrap"><video id="blastVideo" playsinline preload="metadata"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    <script>
      const btn=document.getElementById('shivaBlast');
      const wrap=document.getElementById('blastWrap');
      const video=document.getElementById('blastVideo');
      btn.addEventListener('click',()=>{
        wrap.classList.add('open');
        try{if(window.frameElement){window.frameElement.style.height='650px';}}catch(e){}
        video.currentTime=0;
        video.muted=false;
        const p=video.play();
        if(p&&p.catch)p.catch(()=>{video.controls=true;});
      });
      video.addEventListener('ended',()=>{video.currentTime=0;});
    </script>
    """,height=58,scrolling=False)
'''
source=source.replace('    # ESPN news: 3 Fantasy Football stories + 2 general NFL stories.',blast_block+'    # ESPN news: 3 Fantasy Football stories + 2 general NFL stories.',1)

exec(compile(source,str(Path(__file__).with_name("app_core.py")),"exec"),globals(),globals())
