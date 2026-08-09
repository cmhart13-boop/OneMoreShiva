from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

anchor="@media(max-width:430px){.stat-strip{gap:7px!important}"
if anchor not in s:
    raise SystemExit('mobile CSS anchor not found')

css=r'''
/* Ask Shiva: ESPN-style intelligence card. No red. */
.st-key-home_shiva_go,.st-key-shiva_page_go{position:relative!important;margin-top:6px!important}
.st-key-home_shiva_go:before,.st-key-shiva_page_go:before{content:"";position:absolute;inset:-7px -5px -8px;border-radius:17px;pointer-events:none;background:
radial-gradient(circle at 18% 42%,rgba(63,151,255,.18) 0 1px,transparent 2px),
radial-gradient(circle at 32% 64%,rgba(63,151,255,.12) 0 1px,transparent 2px),
linear-gradient(90deg,transparent 0 13%,rgba(71,157,255,.08) 13.5% 14%,transparent 14.5% 34%,rgba(71,157,255,.06) 34.5% 35%,transparent 35.5% 100%);
opacity:.7;filter:blur(.1px)}
.st-key-home_shiva_go .stButton>button,.st-key-shiva_page_go .stButton>button{
min-height:52px!important;border-radius:14px!important;border:1px solid rgba(92,170,255,.46)!important;color:#fff!important;font-size:15px!important;font-weight:950!important;letter-spacing:.15px!important;
background:linear-gradient(110deg,rgba(30,116,207,.72) 0%,rgba(23,86,151,.52) 28%,rgba(18,39,58,.92) 58%,#0d1821 100%)!important;
box-shadow:inset 0 1px 0 rgba(255,255,255,.12),inset 0 -10px 22px rgba(0,0,0,.17),0 8px 18px rgba(13,71,126,.22),0 0 20px rgba(62,148,255,.10)!important;
text-shadow:0 1px 8px rgba(255,255,255,.10)!important;position:relative!important;overflow:hidden!important}
.st-key-home_shiva_go .stButton>button:before,.st-key-shiva_page_go .stButton>button:before{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(120deg,rgba(255,255,255,.09),transparent 26%,transparent 68%,rgba(64,157,255,.08));border-radius:inherit}
.st-key-home_shiva_go .stButton>button:hover,.st-key-shiva_page_go .stButton>button:hover{border-color:rgba(112,188,255,.62)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.14),0 8px 20px rgba(13,71,126,.25),0 0 24px rgba(62,148,255,.14)!important}
.st-key-home_shiva_go .stButton>button:active,.st-key-shiva_page_go .stButton>button:active{transform:translateY(1px) scale(.995)!important}

/* Subtle "computer brain / crunching numbers" texture behind Shiva intelligence, kept intentionally quiet. */
.home-shiva-hero:before,.shiva-box:before{content:"01  17  32  08  64  11   •   1010  1101  0110";position:absolute;right:12px;bottom:10px;max-width:46%;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:8px;line-height:1.6;letter-spacing:1.2px;color:rgba(96,177,255,.10);text-align:right;white-space:normal;pointer-events:none;transform:skewX(-5deg)}
.home-shiva-hero{box-shadow:inset 0 1px 0 rgba(255,255,255,.03),0 8px 24px rgba(0,0,0,.12)}
'''

s=s.replace(anchor,css+'\n'+anchor,1)
p.write_text(s,encoding='utf-8')
