from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# Put the final mobile/editorial overrides at the END of mobile_css so older media rules cannot win.
needle="\n'''\nsource = source.replace(\"\\n</style>'''\\nst.markdown(CSS, unsafe_allow_html=True)\""
final_css=r'''
/* FINAL PROFESSIONAL OVERRIDE — intentionally last in mobile_css. */
.st-key-home_shiva_card{border-radius:9px!important;border:1px solid rgba(95,116,132,.34)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 5px 14px rgba(0,0,0,.14)!important}
.st-key-home_shiva_go:before,.st-key-shiva_page_go:before{display:none!important;content:none!important}
.st-key-draft_view div[role="radiogroup"] label:nth-child(1) [data-testid="stMarkdownContainer"] p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(2) [data-testid="stMarkdownContainer"] p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(3) [data-testid="stMarkdownContainer"] p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(4) [data-testid="stMarkdownContainer"] p::before{display:none!important;content:none!important}
.st-key-draft_view div[role="radiogroup"] label,.st-key-guide_tab div[role="radiogroup"] label{border-radius:8px!important;min-height:50px!important;padding:7px 4px!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p,.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;line-height:1.12!important;text-transform:none!important}
@media(max-width:430px){
.st-key-draft_view div[role="radiogroup"]{gap:5px!important}.st-key-draft_view div[role="radiogroup"] label,.st-key-guide_tab div[role="radiogroup"] label{min-height:48px!important;padding:6px 3px!important;border-radius:8px!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p,.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10.5px!important}
.quick-card{border-radius:9px!important;padding:13px!important;min-height:98px!important}.quick-icon{font-size:21px!important}.quick-title{font-size:15px!important}.quick-sub{font-size:11.5px!important}
.stButton>button,.stDownloadButton>button{border-radius:8px!important;min-height:43px!important}
.mini-stat{border-radius:9px!important;min-height:118px!important}.player-shell,.profile-hero,.weekly-card,.roster-slot,.draft-chip,.on-clock{border-radius:9px!important}
}
'''
if 'FINAL PROFESSIONAL OVERRIDE' not in s and needle in s:
    s=s.replace(needle,'\n'+final_css+needle,1)
p.write_text(s,encoding='utf-8')

# Draft Guide injects its own CSS after app CSS, so make it match the same restrained design system.
g=Path('shiva_draft_guide.py')
t=g.read_text(encoding='utf-8')
t=t.replace('border-radius:18px','border-radius:9px').replace('border-radius:14px','border-radius:8px').replace('border-radius:13px','border-radius:9px').replace('border-radius:11px','border-radius:8px')
t=t.replace('min-height:76px!important','min-height:50px!important').replace('min-height:72px!important','min-height:48px!important')
t=t.replace('padding:10px 2px 9px!important','padding:7px 4px!important')
t=t.replace('font-size:10px!important}}','font-size:10.5px!important}}')
# Keep the guide selected state subtle and remove any bottom underline artifact.
t=t.replace('.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:12px;right:12px;bottom:7px;height:2px;border-radius:2px;background:rgba(116,227,210,.55)}','.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{display:none!important;content:none!important}')
g.write_text(t,encoding='utf-8')
