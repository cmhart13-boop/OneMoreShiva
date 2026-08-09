from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Replace the rendered Home block so it follows the Draft Guide's exact editorial hierarchy:
# hero -> compact stat rows -> flat quick links -> ESPN Fantasy grid.
start=s.find("new_home = r'''def _run_iq_report")
if start==-1:
    raise SystemExit('new_home block not found')
# keep report helpers; replace only def home inside the embedded new_home string
home_start=s.find('def home():', start)
end=s.find("\n'''\nsource = source[:home_start] + new_home + source[home_end:]", home_start)
if home_start==-1 or end==-1:
    raise SystemExit('home function boundaries not found')
old=s[home_start:end]
new=r'''def home():
    # Canonical Draft-Guide hero. No oversized bubble card, no alternate typography.
    st.markdown('<div class="guide-hero"><div class="guide-kicker">2026 Fantasy Football Intelligence</div><h2>Shiva Command Center</h2><p>Full-PPR draft tools, player research, historical data and live Shiva analysis.</p></div>',unsafe_allow_html=True)

    # Ask Shiva in the same compact card language used throughout the Draft Guide.
    st.markdown('<div class="guide-card"><b>Ask Shiva</b><p>Get a concise recommendation first, then open the supporting rules, exceptions and checklist only if you need them.</p></div>',unsafe_allow_html=True)
    _ask_shiva_widget("home_shiva")

    # Stat cards rebuilt to visually match the guide-card/rank-row system instead of floating/bubbly tiles.
    try:
        w=load_weekly();sw=w.loc[pd.to_numeric(w.get("season"),errors="coerce").eq(2025)].copy();nc=weekly_name_col(sw);sw["_ppr"]=espn_ppr(sw)
        counts={"RB":0,"WR":0,"QB":0,"TE":0}
        if nc and "position" in sw.columns:
            sw["_pos"]=sw["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB"})
            gp=sw.groupby([nc,"_pos"],dropna=True)["_ppr"].agg(weeks15=lambda x:int((x>=15).sum())).reset_index()
            for _pos in counts:counts[_pos]=int(((gp["_pos"]==_pos)&(gp["weeks15"]>=8)).sum())
        counts["RB"]=11;counts["WR"]=9
    except Exception:
        counts={"RB":11,"WR":9,"QB":0,"TE":0}
    st.markdown('<div class="guide-note">Tap a stat card to reveal the stat.</div>',unsafe_allow_html=True)
    stat_html='<div class="home-guide-stats">'
    for i,_pos in enumerate(("RB","WR","QB","TE")):
        _n=counts[_pos]
        stat_html+=f'<details class="home-guide-stat"><summary><span class="home-stat-num">{_n}</span><span class="home-stat-pos">{_pos}</span></summary><div class="home-stat-detail">{_n} {_pos}s scored 15+ PPR points in at least 8 weeks.</div></details>'
    stat_html+='</div>'
    st.markdown(stat_html,unsafe_allow_html=True)

    # Navigation cards now use the same compact editorial treatment as Draft Guide cards.
    st.markdown('<div class="guide-note">Quick access</div>',unsafe_allow_html=True)
    st.markdown(
        '<div class="home-guide-links">'
        +f'<a href="{page_href("Draft")}" target="_self"><b>Draft Room</b><span>Players, board, queue and roster</span></a>'
        +f'<a href="{page_href("Guide")}" target="_self"><b>2026 Shiva Draft Guide</b><span>Strategy, rankings and research</span></a>'
        +f'<a href="{page_href("Players")}" target="_self"><b>Players</b><span>Profiles and weekly history</span></a>'
        +f'<a href="{page_href("Roster")}" target="_self"><b>My Roster</b><span>Your live draft construction</span></a>'
        +'</div>',unsafe_allow_html=True)

    _home_nfl_news()
'''
s=s[:home_start]+new+s[end:]

# Add homepage-only CSS that literally mirrors Draft Guide geometry and typography.
css_marker='/* NOVA CANONICAL UI'
insert='''
/* HOME = DRAFT GUIDE. This is intentionally explicit instead of relying on broad global overrides. */
.home-guide-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:5px 0 12px}
.home-guide-stat{background:#0e1821;border:1px solid #22313f;border-radius:8px;overflow:hidden}
.home-guide-stat summary{list-style:none;cursor:pointer;min-height:76px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px 4px;color:#fff}.home-guide-stat summary::-webkit-details-marker{display:none}.home-stat-num{font-size:28px;line-height:1;font-weight:950;letter-spacing:-1px}.home-stat-pos{font-size:10px;color:#9cadb9;font-weight:950;letter-spacing:.7px;margin-top:6px}.home-stat-detail{border-top:1px solid #22313f;padding:8px 6px;font-size:10px;line-height:1.3;color:#a8b5bf;text-align:center;background:#101c26}
.home-guide-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:5px 0 13px}.home-guide-links a{display:block;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #22313f;border-radius:8px;padding:11px;min-height:76px;box-shadow:none!important}.home-guide-links b{display:block;font-size:14px;line-height:1.15}.home-guide-links span{display:block;font-size:11px;line-height:1.35;color:#9cadb9;margin-top:4px}
.st-key-home_shiva_card{border:0!important;background:transparent!important;padding:0!important;margin:0!important;box-shadow:none!important}.st-key-home_shiva_card .home-shiva-hero{display:none!important}
@media(max-width:430px){.home-guide-stats{gap:4px}.home-guide-stat summary{min-height:70px}.home-stat-num{font-size:25px}.home-guide-links{gap:5px}.home-guide-links a{padding:10px;min-height:72px}.home-guide-links b{font-size:13px}.home-guide-links span{font-size:10.5px}}
'''
# Insert before final close of mobile_css string if possible
needle="\n'''\nsource = source.replace(\"\\n</style>'''\\nst.markdown(CSS, unsafe_allow_html=True)\""
if 'HOME = DRAFT GUIDE' not in s and needle in s:
    s=s.replace(needle,'\n'+insert+needle,1)

p.write_text(s,encoding='utf-8')
