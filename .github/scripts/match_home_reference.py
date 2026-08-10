from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')
marker = '# SHIVA HOME REFERENCE EXACT PASS'
if marker in s:
    raise SystemExit(0)

needle = 'exec(compile(source, str(Path(__file__).with_name("app_core.py")), "exec"), globals(), globals())'
if needle not in s:
    raise SystemExit('exec anchor not found')

patch = r"""
# SHIVA HOME REFERENCE EXACT PASS
_home_reference_css = r'''
/* Shiva Draft Intelligence reference — homepage top only. */
.st-key-home_shiva_card{position:relative!important;margin:6px 0 14px!important;padding:24px 20px 20px!important;border:2px solid #2f9cff!important;border-radius:28px!important;background:linear-gradient(145deg,#07131f 0%,#06101a 58%,#07141f 100%)!important;box-shadow:inset 0 0 0 1px rgba(79,171,255,.22),0 0 12px rgba(35,139,255,.34),0 0 30px rgba(35,139,255,.10)!important;overflow:hidden!important}
.st-key-home_shiva_card:before{display:block!important;content:""!important;position:absolute!important;inset:0!important;pointer-events:none!important;background:radial-gradient(circle at 86% 13%,rgba(40,135,235,.10),transparent 28%),linear-gradient(180deg,rgba(8,28,45,.10),transparent 55%)!important}.st-key-home_shiva_card:after{display:none!important;content:none!important}
.st-key-home_shiva_card .home-shiva-hero{position:relative!important;margin:0 0 18px!important;padding:3px 4px 22px!important;min-height:188px!important;border:0!important;border-radius:0!important;background:transparent!important;border-bottom:1px solid rgba(102,136,164,.34)!important;box-shadow:none!important;overflow:hidden!important}
.st-key-home_shiva_card .home-shiva-hero:before,.st-key-home_shiva_card .home-shiva-hero:after{display:none!important;content:none!important}
.st-key-home_shiva_card .home-shiva-kicker{position:relative!important;z-index:2!important;color:#39a9ff!important;font-size:13px!important;line-height:1.15!important;font-weight:950!important;letter-spacing:.65px!important;text-transform:uppercase!important;margin:0 0 13px!important}
.st-key-home_shiva_card .home-shiva-title{position:relative!important;z-index:2!important;color:#fff!important;font-size:31px!important;line-height:1.03!important;font-weight:980!important;letter-spacing:-1.15px!important;margin:0 0 14px!important;max-width:78%!important}
.st-key-home_shiva_card .home-shiva-copy{position:relative!important;z-index:2!important;color:#c1c9d0!important;font-size:16px!important;line-height:1.52!important;font-weight:500!important;max-width:82%!important;margin:0!important}
.st-key-home_shiva_card .home-shiva-brain{display:block!important;position:absolute!important;z-index:1!important;right:-3px!important;top:0!important;width:150px!important;height:150px!important;opacity:.48!important;filter:drop-shadow(0 0 8px rgba(37,140,255,.20))!important;pointer-events:none!important}
.st-key-home_shiva_card .home-ask-label{position:relative!important;z-index:2!important;color:#f4f6f8!important;font-size:15px!important;line-height:1.2!important;font-weight:950!important;margin:0 4px 11px!important}
.st-key-home_shiva_card .stTextArea{margin:0 0 14px!important}.st-key-home_shiva_card .stTextArea textarea{min-height:164px!important;height:164px!important;padding:24px 18px!important;border-radius:17px!important;border:1px solid rgba(92,122,148,.44)!important;background:#0a151f!important;color:#f4f7fa!important;font-size:16px!important;line-height:1.55!important;box-shadow:inset 0 1px 2px rgba(0,0,0,.45)!important;resize:none!important}.st-key-home_shiva_card .stTextArea textarea::placeholder{color:#aab4bd!important;opacity:.88!important}
.st-key-home_shiva_go{margin:0!important}.st-key-home_shiva_go:before{display:none!important;content:none!important}.st-key-home_shiva_go .stButton>button{min-height:76px!important;height:76px!important;border-radius:17px!important;border:1px solid #3b9df0!important;background:linear-gradient(108deg,#1267ad 0%,#11588f 27%,#123b59 58%,#0d1b28 100%)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.12),inset 0 -10px 24px rgba(0,0,0,.18),0 0 15px rgba(38,145,239,.22)!important;color:#fff!important;font-size:17px!important;font-weight:980!important;letter-spacing:.15px!important;text-shadow:none!important}.st-key-home_shiva_go .stButton>button:before{display:none!important;content:none!important}
@media(max-width:430px){.st-key-home_shiva_card{padding:20px 14px 16px!important;border-radius:25px!important}.st-key-home_shiva_card .home-shiva-hero{min-height:184px!important;padding-left:2px!important;padding-right:2px!important}.st-key-home_shiva_card .home-shiva-kicker{font-size:12px!important;margin-bottom:12px!important}.st-key-home_shiva_card .home-shiva-title{font-size:29px!important;max-width:82%!important;margin-bottom:13px!important}.st-key-home_shiva_card .home-shiva-copy{font-size:15px!important;line-height:1.5!important;max-width:84%!important}.st-key-home_shiva_card .home-shiva-brain{width:138px!important;height:138px!important;right:-9px!important;top:3px!important;opacity:.43!important}.st-key-home_shiva_card .home-ask-label{font-size:14px!important;margin-left:2px!important}.st-key-home_shiva_card .stTextArea textarea{min-height:158px!important;height:158px!important;font-size:15px!important;padding:22px 16px!important}.st-key-home_shiva_go .stButton>button{min-height:72px!important;height:72px!important;font-size:16px!important}}
'''
_target = "\n</style>" + chr(39)*3 + "\nst.markdown(CSS, unsafe_allow_html=True)"
if _target not in source:
    raise RuntimeError('CSS injection anchor not found')
source = source.replace(_target, "\n" + _home_reference_css + _target, 1)

"""
s = s.replace(needle, patch + needle, 1)
p.write_text(s, encoding='utf-8')
