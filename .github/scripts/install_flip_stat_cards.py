from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")
home = s.index("def home():")
start = s.index(
    '    try:\n        w=load_weekly();sw=w.loc[pd.to_numeric(w.get("season"),errors="coerce").eq(2025)].copy();nc=weekly_name_col(sw);sw["_ppr"]=espn_ppr(sw)',
    home,
)
end = s.index("    _home_shiva_blast()", start)

replacement = r'''    try:
        w=load_weekly();sw=w.loc[pd.to_numeric(w.get("season"),errors="coerce").eq(2025)].copy();nc=weekly_name_col(sw);sw["_ppr"]=espn_ppr(sw)
        counts={"RB":0,"WR":0,"QB":0,"TE":0}
        if nc and "position" in sw.columns:
            sw["_pos"]=sw["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB"})
            gp=sw.groupby([nc,"_pos"],dropna=True)["_ppr"].agg(weeks15=lambda x:int((x>=15).sum())).reset_index()
            for _pos in counts:counts[_pos]=int(((gp["_pos"]==_pos)&(gp["weeks15"]>=8)).sum())
        counts["RB"]=11;counts["WR"]=9
        flip_cards="""<style>
        .stat-hint{font-size:10px;color:#8fa0ae;font-weight:800;text-align:center;margin:3px 0 8px}
        .flip-stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:0 0 12px}
        .flip-stat{position:relative;min-width:0;perspective:700px}.flip-stat input{position:absolute;opacity:0;pointer-events:none}.flip-stat label{display:block;height:86px;cursor:pointer;-webkit-tap-highlight-color:transparent}
        .flip-inner{position:relative;width:100%;height:100%;transition:transform .45s cubic-bezier(.2,.7,.2,1);transform-style:preserve-3d}.flip-stat input:checked + label .flip-inner{transform:rotateY(180deg)}
        .flip-face{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;border:1px solid #2a3a47;border-radius:13px;background:linear-gradient(150deg,#15232f,#0d161e);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.14);overflow:hidden}
        .flip-front .flip-num{font-size:29px;line-height:.95;font-weight:980;color:#fff;letter-spacing:-1px}.flip-front .flip-pos{font-size:11px;line-height:1;margin-top:7px;font-weight:950;color:#9aabb8;letter-spacing:.8px}
        .flip-back{transform:rotateY(180deg);padding:7px 5px;text-align:center;background:#101c26}.flip-back b{font-size:10px;line-height:1.15;color:#fff;display:block}.flip-back span{font-size:8px;line-height:1.22;color:#a5b4bf;display:block;margin-top:4px;font-weight:750}
        @media(max-width:370px){.flip-stat-grid{gap:4px}.flip-stat label{height:80px}.flip-front .flip-num{font-size:25px}.flip-back b{font-size:9px}.flip-back span{font-size:7px}}
        </style><div class=\"stat-hint\">Tap a stat card to reveal the stat</div><div class=\"flip-stat-grid\">"""
        for i,_pos in enumerate(("RB","WR","QB","TE")):
            _n=counts[_pos]
            flip_cards+=f'''<div class="flip-stat"><input type="checkbox" id="flip-stat-{i}"><label for="flip-stat-{i}"><div class="flip-inner"><div class="flip-face flip-front"><div class="flip-num">{_n}</div><div class="flip-pos">{_pos}</div></div><div class="flip-face flip-back"><b>{_n} {_pos}s</b><span>15+ PPR points in 8+ weeks</span></div></div></label></div>'''
        flip_cards+='</div>'
        st.markdown(flip_cards,unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="stat-strip"><div class="mini-stat metric-rb"><b>11</b><span>RB</span></div><div class="mini-stat metric-wr"><b>9</b><span>WR</span></div></div>',unsafe_allow_html=True)
'''

p.write_text(s[:start] + replacement + s[end:], encoding="utf-8")
