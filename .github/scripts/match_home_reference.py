from pathlib import Path

p=Path('app.py')
s=p.read_text(encoding='utf-8')

# 1) Make the entire Shiva intelligence area one real Streamlit container/card.
old='''def home():\n    st.markdown('<div class="home-shiva-hero"><div class="home-shiva-kicker">Your fantasy football copilot</div><div class="home-shiva-title">Shiva Draft Intelligence</div><div class="home-shiva-copy">Ask Shiva for help building your championship team. Player history, PPR scoring, rankings and your live draft data are checked inside the app first.</div></div>',unsafe_allow_html=True)\n    st.markdown('<div class="home-ask-label">Ask Shiva anything</div>',unsafe_allow_html=True)\n    _ask_shiva_widget("home_shiva")\n    try:'''
new='''def home():\n    with st.container(key="home_shiva_card"):\n        st.markdown('<div class="home-shiva-hero"><div class="home-shiva-kicker">Your fantasy football copilot</div><div class="home-shiva-title">Shiva Draft Intelligence</div><div class="home-shiva-copy">Ask Shiva for help building your championship team. Player history, PPR scoring, rankings and your live draft data are checked inside the app first.</div></div>',unsafe_allow_html=True)\n        st.markdown('<div class="home-ask-label">Ask Shiva anything</div>',unsafe_allow_html=True)\n        _ask_shiva_widget("home_shiva")\n    try:'''
if old not in s:
    raise SystemExit('home Shiva block anchor not found')
s=s.replace(old,new,1)

# 2) Add a final CSS override so the reference styling wins over earlier experiments.
anchor="@media(max-width:430px){.stat-strip{gap:7px!important}"
idx=s.find(anchor)
if idx < 0:
    raise SystemExit('mobile CSS anchor not found')
css=r'''
/* FINAL HOME REFERENCE PASS — clean ESPN-like depth, restrained borders. */
.st-key-home_shiva_card{
  position:relative!important;
  margin:8px 0 13px!important;
  padding:15px 14px 14px!important;
  border:1px solid rgba(91,117,138,.48)!important;
  border-radius:18px!important;
  background:linear-gradient(145deg,rgba(16,29,40,.96),rgba(7,16,24,.98) 72%)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.045),inset 0 -1px 0 rgba(0,0,0,.30),0 9px 22px rgba(0,0,0,.22)!important;
  overflow:hidden!important;
}
.st-key-home_shiva_card:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 88% 15%,rgba(53,137,220,.08),transparent 29%);}
.st-key-home_shiva_card .home-shiva-hero{
  margin:0 0 12px!important;padding:2px 1px 15px!important;border:0!important;border-radius:0!important;background:transparent!important;
  border-bottom:1px solid rgba(106,128,145,.28)!important;box-shadow:none!important;overflow:visible!important;
}
.st-key-home_shiva_card .home-shiva-hero:after{color:#3188d8!important;opacity:.10!important;font-size:78px!important;right:8px!important;top:0!important}
.st-key-home_shiva_card .home-shiva-hero:before{right:4px!important;bottom:12px!important;color:rgba(89,163,226,.09)!important}
.st-key-home_shiva_card .home-shiva-kicker{color:#55a8ee!important;font-size:11px!important;letter-spacing:.8px!important}
.st-key-home_shiva_card .home-shiva-title{font-size:27px!important;letter-spacing:-.7px!important}
.st-key-home_shiva_card .home-shiva-copy{font-size:14px!important;line-height:1.48!important;color:#b7c2cb!important;max-width:92%!important}
.st-key-home_shiva_card .home-ask-label{margin:0 0 7px!important;font-size:13px!important;font-weight:900!important;color:#f1f5f8!important}
.st-key-home_shiva_card .stTextArea textarea{background:#0d151d!important;border:1px solid rgba(91,112,128,.42)!important;border-radius:12px!important;box-shadow:inset 0 1px 2px rgba(0,0,0,.35)!important;color:#f4f7f9!important}
.st-key-home_shiva_card .stTextArea textarea:focus{border-color:rgba(74,132,181,.62)!important;box-shadow:0 0 0 1px rgba(74,132,181,.12),inset 0 1px 2px rgba(0,0,0,.35)!important}
.st-key-home_shiva_go{margin-top:8px!important}
.st-key-home_shiva_go:before{display:none!important}
.st-key-home_shiva_go .stButton>button{
  min-height:50px!important;border-radius:12px!important;
  border:1px solid rgba(74,135,185,.56)!important;
  background:linear-gradient(105deg,rgba(33,103,164,.72) 0%,rgba(24,69,108,.48) 32%,rgba(14,30,43,.98) 72%,#0c171f 100%)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),inset 0 -8px 16px rgba(0,0,0,.18),0 5px 14px rgba(0,0,0,.22)!important;
  color:#fff!important;font-size:15px!important;font-weight:950!important;
}
.st-key-home_shiva_go .stButton>button:before{opacity:.35!important}

/* Stat cards and shortcut cards use quiet ESPN-style edge definition, not neon outlines. */
.flip-face{border-color:rgba(92,112,128,.38)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 5px 14px rgba(0,0,0,.18)!important;background:linear-gradient(145deg,#14212c,#0b141c 78%)!important}
.quick-card{border-color:rgba(91,112,128,.36)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 6px 16px rgba(0,0,0,.18)!important}
.quick-card.q-draft{border-color:rgba(55,122,169,.42)!important;background:linear-gradient(135deg,rgba(27,83,120,.23),#111d27 46%,#0d171f 100%)!important}
.quick-card.q-guide{border-color:rgba(126,82,158,.40)!important;background:linear-gradient(135deg,rgba(92,52,121,.22),#151726 48%,#0e151e 100%)!important}
.quick-card.q-players{border-color:rgba(57,118,105,.34)!important}.quick-card.q-roster{border-color:rgba(132,104,64,.34)!important}
'''
s=s[:idx]+css+'\n'+s[idx:]

p.write_text(s,encoding='utf-8')
