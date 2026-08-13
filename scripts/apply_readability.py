from pathlib import Path

p = Path('app_core.py')
s = p.read_text(encoding='utf-8')
old = '{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics,"Coach":season_coach}[page]();bottom_nav(page)'
new = '''{"Home":home,"Draft":draft,"Guide":draft_guide,"Players":player_db,"Shiva":home,"Roster":roster_screen,"Analytics":analytics,"Coach":season_coach}[page]()
st.markdown(r"""<style>
.screen-head h1{font-size:30px!important}.screen-head p{font-size:16px!important;line-height:1.45!important}.brand-sub{font-size:15px!important}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,.stCaption,.stCaption p{font-size:15px!important;line-height:1.45!important}
.stMarkdown p,.stMarkdown li{font-size:16px!important;line-height:1.5!important}.stButton>button{font-size:16px!important}
.stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stNumberInput label{font-size:15px!important}
.player-meta,.slot-meta,.board-meta,.board-pick,.profile-sub,.mini-stat span,.data-cell span,.draft-chip span,.hero-kicker,.guide-kicker,.guide-note,.adj-row,.rounds,.strategy-box span,.rank-n,.pos-chip,.news-meta,.news-desc,.news-link,.home-v2-sub,.home-v2-kicker,.leader-meta,.edge-rank-meta,.edge-rank,.edge-rank-stat span,.edge-method,.kick-label,.kick-date,.kick-unit span,.iq-label,.iq-meta,.iq-reason,.iq-locked,.shiva-iq-copy,.shiva-iq-live{font-size:14px!important;line-height:1.4!important}
.player-name,.slot-player,.board-name,.leader-name,.rank-name,.news-title,.strategy-box b,.guide-card b,.guide-card p,.edge-rank-name{font-size:17px!important;line-height:1.35!important}
.shiva-iq-title{font-size:22px!important}.iq-name{font-size:18px!important}.iq-draft{font-size:14px!important;min-height:42px!important}.home-edge p{font-size:17px!important}.edge-panel-copy{font-size:16px!important}
</style>""", unsafe_allow_html=True)
bottom_nav(page)'''
if old not in s:
    raise SystemExit('dispatch marker not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
