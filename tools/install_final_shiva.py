from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'app_core.py'
s=p.read_text(encoding='utf-8')

imp='from shiva_product import render_full_product\n'
anchor='from shiva_coach import inject_css as inject_coach_css, render_season_hub, render_draft_moment\n'
if imp not in s:
    if anchor not in s: raise SystemExit('coach import anchor missing')
    s=s.replace(anchor,anchor+imp,1)

# Coach becomes the complete product hub.
old='    render_season_hub(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)'
new='    render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)'
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('season coach render anchor missing')

# One Shiva identity: remove every generic trophy pseudo-element from product chrome.
s=s.replace(".brand-badge::after{content:'🏆';font-size:18px}",".brand-badge::after{content:none!important;display:none!important}")
s=s.replace('.hero-card:after{content:"🏆";position:absolute;right:-5px;top:2px;font-size:88px;opacity:.08;transform:rotate(10deg)}','.hero-card:after{content:none!important;display:none!important}')
s=s.replace(".hero-card:after{content:'🏆'!important;filter:grayscale(.25)!important;opacity:.075!important}",".hero-card:after{content:none!important;display:none!important}")

# Four thumb-friendly destinations in the permanent mobile nav.
s=s.replace('grid-template-columns:repeat(6,1fr);padding:6px 6px', 'grid-template-columns:repeat(4,1fr);padding:6px 8px')

# Make the actual Shiva mark the dominant logo, not a little icon in a generic badge.
extra=r'''
/* FINAL SHIVA IDENTITY */
.brand-badge{background:transparent!important;border:0!important;box-shadow:none!important;width:48px!important;height:58px!important;padding:0!important;border-radius:0!important;overflow:visible!important}
.shiva-trophy-mark{width:42px!important;height:58px!important;filter:drop-shadow(0 5px 8px rgba(0,0,0,.28))}
.brand-badge::after,.hero-card::after{content:none!important;display:none!important}
.brand-wrap{gap:8px!important}.brand-title{font-size:20px!important}.brand-sub{font-size:9.5px!important}.app-top{min-height:64px!important;padding-top:4px!important}
.bottom-nav{grid-template-columns:repeat(4,1fr)!important}.bottom-nav a{font-size:10.5px!important}
@media(max-width:430px){.brand-badge{width:44px!important;height:54px!important}.shiva-trophy-mark{width:39px!important;height:54px!important}.brand-title{font-size:19px!important}}
'''
marker="\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)"
if '/* FINAL SHIVA IDENTITY */' not in s:
    if marker not in s: raise SystemExit('CSS marker missing')
    s=s.replace(marker,'\n'+extra+marker,1)

p.write_text(s,encoding='utf-8')
ast.parse(s)

checks={
 'full product import':'from shiva_product import render_full_product' in s,
 'full product route':'render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)' in s,
 'single trophy css':'.brand-badge::after{content:none' in s or '.brand-badge::after,.hero-card::after{content:none' in s,
 'four nav':'grid-template-columns:repeat(4,1fr)!important' in s,
 'no draft coach coupling':'Draft-Coach' not in s,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit('FAILED '+', '.join(failed))
print('FINAL SHIVA PRODUCTION INSTALL PASS')
