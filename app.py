from pathlib import Path

source = Path(__file__).with_name("app_core.py").read_text(encoding="utf-8")

# OneMoreShiva is the production source of truth.
source = source.replace('\"user_slot\":3', '\"user_slot\":1', 1)

# Splash is launch-only. Normal query-param navigation never replays it.
source = source.replace(
    'if not st.session_state.get("_shiva_startup_splash_seen", False):',
    'if not any(k in st.query_params for k in ("page","player","draft","queue_add")) and not st.session_state.get("_shiva_startup_splash_seen", False):',
    1,
)
source = source.replace('_splash_time.sleep(2.3)', '_splash_time.sleep(2.0)', 1)

# Shared phone-first visual overrides. These are deliberately additive so existing app behavior stays intact.
mobile_css = r'''
.data-status{display:none!important}

/* MOBILE NAV TRANSITION: prevent white document flash between bottom-nav pages. */
html,body{background:#071019!important;color-scheme:dark!important}.stApp,.stAppViewContainer,[data-testid="stAppViewContainer"]{background:#071019!important}

/* Draft Room top navigation: four equal full-width cards. */
.st-key-draft_view{display:block!important;width:100%!important;max-width:none!important;margin:2px 0 13px!important}
.st-key-draft_view>div,.st-key-draft_view [data-testid="stRadio"],.st-key-draft_view [data-baseweb="radio-group"]{width:100%!important;max-width:none!important}
.st-key-draft_view div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:7px!important;width:100%!important;max-width:none!important;align-items:stretch!important}
.st-key-draft_view div[role="radiogroup"] label{box-sizing:border-box!important;position:relative!important;width:100%!important;min-width:0!important;max-width:none!important;min-height:84px!important;border-radius:14px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:12px 3px 10px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;margin:0!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:14px;right:14px;bottom:7px;height:2px;border-radius:2px;background:#fff}
.st-key-draft_view div[role="radiogroup"] label>div:first-child{display:none!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%!important;text-align:center!important}
.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:13px!important;font-weight:950!important;white-space:nowrap!important;color:#aab8c4!important;line-height:1!important;text-transform:uppercase!important;text-align:center!important;margin:0!important}
.st-key-draft_view div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
.st-key-draft_view div[role="radiogroup"] label:nth-child(1) [data-testid="stMarkdownContainer"] p::before{content:"👥";display:block;font-size:24px;line-height:1.15;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(2) [data-testid="stMarkdownContainer"] p::before{content:"▦";display:block;font-size:27px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(3) [data-testid="stMarkdownContainer"] p::before{content:"☷";display:block;font-size:27px;line-height:1.05;margin-bottom:7px}
.st-key-draft_view div[role="radiogroup"] label:nth-child(4) [data-testid="stMarkdownContainer"] p::before{content:"🛡";display:block;font-size:23px;line-height:1.15;margin-bottom:7px}
.player-shell.draft-player{grid-template-columns:44px minmax(0,1fr) 45px 45px 64px!important}
.queue-inline{display:none!important}

/* Global mobile readability. */
.screen-head p{font-size:13px!important;line-height:1.4!important}
.hero-kicker{font-size:12px!important}.hero-card p{font-size:14px!important;line-height:1.45!important}.hero-card h2{font-size:28px!important}
.mini-stat{padding:15px 10px!important;min-height:132px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;overflow:hidden!important;position:relative!important}.mini-stat b{font-size:32px!important;line-height:1!important;color:#fff!important;font-weight:980!important;text-shadow:0 2px 8px rgba(0,0,0,.25)!important}.mini-stat span{font-size:13px!important;line-height:1.28!important;letter-spacing:0!important;text-transform:none!important;margin-top:11px!important;color:#eef4f7!important;font-weight:800!important}
.quick-card{min-height:112px!important;padding:17px!important}.quick-icon{font-size:29px!important}.quick-title{font-size:18px!important;line-height:1.18!important;margin-top:5px!important}.quick-sub{font-size:13px!important;line-height:1.4!important;margin-top:4px!important;color:#c3ced6!important}
.player-name{font-size:16px!important}.player-meta{font-size:11px!important}.data-cell span{font-size:9px!important}.data-cell b{font-size:13px!important}.draft-inline{font-size:12px!important}
.draft-chip{padding:10px!important}.draft-chip span{font-size:10px!important}.draft-chip b{font-size:18px!important}.on-clock{font-size:14px!important;line-height:1.25!important;padding:12px 13px!important}
.profile-sub{font-size:12px!important;line-height:1.4!important}.profile-metric{padding:11px!important}.profile-metric b{font-size:20px!important}.profile-metric span{font-size:10px!important;line-height:1.2!important}
.weekly-card .wk{font-size:13px!important}.weekly-card .opp{font-size:12px!important}.weekly-card .pts{font-size:17px!important}.weekly-card .detail{font-size:11px!important;line-height:1.25!important}
.roster-slot{padding:12px!important}.slot-tag{font-size:11px!important}.slot-player{font-size:14px!important}.slot-meta{font-size:11px!important}.shiva-box p{font-size:13px!important;line-height:1.4!important}.answer{font-size:14px!important;line-height:1.5!important}.stButton>button{font-size:14px!important}.bottom-nav a{font-size:11px!important}
.shiva-iq-title{font-size:16px!important}.shiva-iq-live{font-size:10px!important}.shiva-iq-copy{font-size:12px!important;line-height:1.4!important}.iq-label{font-size:9px!important}.iq-name{font-size:15px!important}.iq-meta{font-size:10px!important}.iq-reason{font-size:11px!important;line-height:1.35!important}.iq-draft{font-size:11px!important}.iq-locked{font-size:11px!important}

/* Home Ask Shiva + descriptive stat cards. */
.home-shiva-hero{background:linear-gradient(140deg,#182b3b,#0a1219 68%);border:1px solid #365167;border-radius:19px;padding:17px 16px 15px;margin:3px 0 8px;position:relative;overflow:hidden}.home-shiva-hero:after{content:"✦";position:absolute;right:12px;top:-12px;font-size:94px;color:#ec1738;opacity:.10}.home-shiva-kicker{font-size:11px;font-weight:950;color:#d9ff38;letter-spacing:1px;text-transform:uppercase}.home-shiva-title{font-size:27px;font-weight:980;color:#fff;letter-spacing:-.8px;line-height:1.05;margin-top:5px}.home-shiva-copy{font-size:14px;color:#b6c2cb;line-height:1.4;margin-top:6px;max-width:90%}.home-ask-label{font-size:12px;font-weight:900;color:#c6d2da;margin:2px 0 3px}.work-note{font-size:12px;color:#aebdc7;line-height:1.45}.work-note b{color:#fff}
.metric-rb{background:linear-gradient(135deg,rgba(240,161,94,.46) 0%,rgba(118,67,34,.28) 42%,#0e1821 100%)!important;border-color:rgba(240,161,94,.48)!important}.metric-wr{background:linear-gradient(135deg,rgba(93,164,242,.46) 0%,rgba(37,82,137,.28) 42%,#0e1821 100%)!important;border-color:rgba(93,164,242,.48)!important}.metric-ppg{background:linear-gradient(135deg,rgba(82,214,139,.43) 0%,rgba(31,102,67,.27) 42%,#0e1821 100%)!important;border-color:rgba(82,214,139,.46)!important}.metric-weeks{background:linear-gradient(135deg,rgba(229,195,75,.44) 0%,rgba(111,88,25,.27) 42%,#0e1821 100%)!important;border-color:rgba(229,195,75,.46)!important}.metric-rb b,.metric-rb span,.metric-wr b,.metric-wr span,.metric-ppg b,.metric-ppg span,.metric-weeks b,.metric-weeks span{color:#fff!important}
.quick-card.q-draft{border-color:#3b78a7!important;background:linear-gradient(135deg,rgba(59,120,167,.34) 0%,rgba(26,56,78,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(59,120,167,.15)}.quick-card.q-guide{border-color:#9a5ac9!important;background:linear-gradient(135deg,rgba(154,90,201,.34) 0%,rgba(70,40,91,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(154,90,201,.15)}.quick-card.q-players{border-color:#2c9b82!important;background:linear-gradient(135deg,rgba(44,155,130,.33) 0%,rgba(20,72,61,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(44,155,130,.15)}.quick-card.q-roster{border-color:#b8873d!important;background:linear-gradient(135deg,rgba(184,135,61,.34) 0%,rgba(82,58,26,.22) 42%,#111d27 100%)!important;box-shadow:inset 0 0 0 1px rgba(184,135,61,.15)}

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


/* Shiva answer presentation: readable summary first, details tucked into ESPN-style drawers. */
.shiva-answer-summary{margin:13px 0 9px;padding:14px 14px 13px;border-left:3px solid rgba(93,199,151,.62);border-radius:10px;background:linear-gradient(100deg,rgba(38,82,68,.22),rgba(13,24,32,.20) 58%,transparent);color:#f5f8fa;font-size:16px;line-height:1.55;font-weight:650;letter-spacing:-.08px}
.shiva-answer-summary b,.shiva-answer-summary strong{color:#fff;font-weight:900}
.shiva-answer-label{display:block;margin-bottom:6px;color:#86d9b3;font-size:10px;line-height:1;font-weight:950;letter-spacing:.8px;text-transform:uppercase}
.st-key-home_shiva_card details,.st-key-shiva_page_card details{margin:6px 0!important;border:1px solid rgba(104,126,143,.25)!important;border-radius:11px!important;background:linear-gradient(145deg,rgba(18,31,41,.74),rgba(10,19,27,.78))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important;overflow:hidden!important}
.st-key-home_shiva_card details summary,.st-key-shiva_page_card details summary{padding:11px 12px!important;color:#e7edf2!important;font-size:13px!important;font-weight:900!important;letter-spacing:.05px!important}
.st-key-home_shiva_card details [data-testid="stMarkdownContainer"],.st-key-shiva_page_card details [data-testid="stMarkdownContainer"]{padding:0 12px 10px!important}
.st-key-home_shiva_card details p,.st-key-home_shiva_card details li,.st-key-shiva_page_card details p,.st-key-shiva_page_card details li{font-size:14px!important;line-height:1.52!important;color:#c8d2da!important}
.st-key-home_shiva_card details ul,.st-key-home_shiva_card details ol,.st-key-shiva_page_card details ul,.st-key-shiva_page_card details ol{padding-left:20px!important;margin-top:5px!important}


/* MASTER DESIGN SYSTEM — Draft Guide is canonical across every page. */
:root{--surface:#0e1821!important;--surface2:#14212d!important;--line:#263745!important;--teal:#74e3d2!important}
.screen-head{margin:2px 0 9px!important}.screen-head h1{font-size:25px!important}.screen-head p{font-size:13px!important;line-height:1.4!important}
.hero-card,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat{border-color:rgba(77,101,120,.46)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 6px 18px rgba(0,0,0,.13)!important}
.stButton>button{border-color:rgba(78,103,121,.48)!important;background:linear-gradient(145deg,#14212d,#0d1821)!important;color:#eef4f7!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 5px 14px rgba(0,0,0,.12)!important}
.stButton>button[kind="primary"]{background:linear-gradient(145deg,rgba(45,116,107,.72),rgba(18,54,52,.88))!important;border-color:rgba(116,227,210,.42)!important;color:#fff!important}
.player-name{font-size:15px!important}.player-meta{font-size:11px!important}.quick-title{font-size:16px!important}.quick-sub{font-size:12px!important}.roster-slot{font-size:13px!important}
.bottom-nav a.active{background:linear-gradient(145deg,rgba(43,106,99,.28),rgba(18,39,43,.68))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important}.bottom-nav a{font-size:10px!important}
/* Shiva IQ brain/data feel */
.bottom-nav a[href*="Shiva"] .nav-icon{filter:drop-shadow(0 0 7px rgba(116,227,210,.24))}
.espn-fantasy-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:8px 0 14px}.espn-story{display:block;color:#fff!important;text-decoration:none!important;background:#0e1821;border:1px solid rgba(77,101,120,.46);border-radius:13px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,.13)}.espn-story img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#111}.espn-story-body{padding:10px}.espn-story-kicker{font-size:9px;color:#74e3d2;font-weight:950;text-transform:uppercase;letter-spacing:.6px}.espn-story-title{font-size:13px;line-height:1.25;font-weight:900;margin-top:4px}.espn-story-source{font-size:9px;color:#8fa0ae;margin-top:5px}

/* PROFESSIONAL V2 — Draft-Guide-led, restrained, editorial, mobile-first. */
:root{--pro-line:rgba(95,116,132,.34);--pro-teal:#74e3d2}
.app-top{padding:4px 1px 8px!important}.brand-badge{width:34px!important;height:34px!important;border-radius:8px!important;background:linear-gradient(145deg,#152634,#0c1821)!important;border:1px solid rgba(116,227,210,.20)!important;font-size:18px!important}.data-status{border-radius:7px!important;padding:5px 7px!important;background:#0b1b14!important;border-color:rgba(84,144,111,.30)!important}
.screen-head{margin:1px 0 9px!important}.screen-head h1{font-size:24px!important;letter-spacing:-.6px!important}.screen-head p{font-size:13px!important;line-height:1.35!important}
.hero-card,.home-shiva-hero,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell{border-radius:9px!important;border:1px solid var(--pro-line)!important;background:linear-gradient(145deg,rgba(16,29,40,.98),rgba(10,19,27,.98))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 5px 14px rgba(0,0,0,.14)!important}
.stButton>button,.stDownloadButton>button{border-radius:8px!important;min-height:44px!important;border:1px solid rgba(93,116,133,.38)!important;background:linear-gradient(145deg,#14212c,#0d1821)!important;color:#eef3f6!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important;font-weight:850!important;font-size:13px!important}
.stButton>button[kind="primary"],.st-key-home_shiva_go .stButton>button,.st-key-shiva_page_go .stButton>button{border-radius:8px!important;background:linear-gradient(145deg,rgba(39,102,96,.72),rgba(16,48,47,.92))!important;border-color:rgba(116,227,210,.32)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 4px 12px rgba(0,0,0,.12)!important;text-shadow:none!important}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{border-radius:8px!important;border-color:rgba(91,112,128,.38)!important;background:#0c161e!important}
.pos,.board-pos{border-radius:4px!important}.player-rank,.draft-inline,.profile-metric{border-radius:7px!important}.flip-face{border-radius:9px!important}.quick-card{padding:14px!important}.quick-icon{font-size:23px!important}.quick-title{font-size:16px!important}.quick-sub{font-size:12px!important;line-height:1.35!important}
.st-key-draft_view div[role="radiogroup"],.st-key-guide_tab div[role="radiogroup"]{gap:5px!important}.st-key-draft_view div[role="radiogroup"] label,.st-key-guide_tab div[role="radiogroup"] label{min-height:50px!important;border-radius:8px!important;padding:7px 4px!important;background:#0e1821!important;border:1px solid rgba(90,111,127,.36)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important}.st-key-draft_view div[role="radiogroup"] label>div:first-child,.st-key-guide_tab div[role="radiogroup"] label>div:first-child,.st-key-draft_view input[type="radio"],.st-key-guide_tab input[type="radio"]{display:none!important}.st-key-draft_view div[role="radiogroup"] label:has(input:checked),.st-key-guide_tab div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,rgba(42,91,86,.34),rgba(14,34,35,.88))!important;border-color:rgba(116,227,210,.28)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)!important}.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after,.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{display:none!important}.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p,.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:11px!important;line-height:1.12!important;text-transform:none!important}
.bottom-nav{height:72px!important;background:rgba(7,14,20,.98)!important;border-top:1px solid rgba(92,111,126,.28)!important;box-shadow:0 -5px 18px rgba(0,0,0,.24)!important}.bottom-nav a{border-radius:7px!important;min-height:54px!important;font-size:9.5px!important}.bottom-nav a.active{background:rgba(35,66,67,.34)!important;color:#fff!important}.nav-icon{font-size:19px!important}
.shiva-iq-navicon{position:relative;width:27px;height:22px;display:block}.iq-head-mini{position:absolute;left:1px;top:2px;width:15px;height:17px;border:1.4px solid rgba(218,229,235,.82);border-right-color:rgba(116,227,210,.55);border-radius:48% 44% 42% 50%;clip-path:polygon(0 0,100% 0,100% 68%,73% 70%,72% 100%,27% 100%,27% 82%,0 73%)}.iq-calc-mini{position:absolute;right:-1px;top:1px;font:700 5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;color:rgba(116,227,210,.72);text-align:left}
.shiva-iq-panel{position:relative;overflow:hidden;padding:17px 16px 16px;margin:4px 0 12px;min-height:150px}.shiva-iq-panel h2{font-size:25px;line-height:1.05;margin:0 0 6px;color:#fff;letter-spacing:-.6px}.shiva-iq-panel p{font-size:13px;line-height:1.45;color:#aebbc5;max-width:63%;margin:0}.iq-kicker{font-size:10px;color:#91dbc8;font-weight:900;letter-spacing:.8px;text-transform:uppercase;margin-bottom:5px}.iq-visual{position:absolute;right:4px;top:7px;width:132px;height:132px;opacity:.80}.iq-head{position:absolute;left:6px;top:13px;width:72px;height:92px;border:2px solid rgba(208,223,232,.46);border-right-color:rgba(116,227,210,.45);border-radius:48% 43% 40% 52%;clip-path:polygon(0 0,100% 0,100% 63%,79% 66%,77% 79%,63% 82%,62% 100%,28% 100%,28% 81%,10% 74%,0 60%)}.iq-head:after{content:"";position:absolute;left:21px;top:27px;width:31px;height:27px;border:1px solid rgba(116,227,210,.18);border-radius:50%;box-shadow:8px 7px 0 -7px rgba(116,227,210,.34),-8px -5px 0 -7px rgba(116,227,210,.26)}.iq-formulas{position:absolute;right:0;top:3px;width:64px;font:700 7px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace;color:rgba(116,227,210,.46);white-space:pre-line}.iq-formulas:before{content:"";position:absolute;left:-13px;top:9px;width:13px;height:1px;background:linear-gradient(90deg,rgba(116,227,210,.28),transparent);box-shadow:0 18px 0 rgba(116,227,210,.18),0 36px 0 rgba(116,227,210,.14),0 54px 0 rgba(116,227,210,.11)}
.iq-report-shell{padding:14px;margin:8px 0 12px}.iq-report-title{font-size:17px;font-weight:900;color:#fff}.iq-report-copy{font-size:12px;line-height:1.4;color:#9eacb7;margin-top:3px}.iq-presets{font-size:10px;color:#91a2ae;margin:5px 0 8px}.iq-result-note{font-size:12px;color:#aebbc5;margin:8px 0}

@media(max-width:430px){.stat-strip{gap:7px!important}.mini-stat{min-height:136px!important;padding:13px 7px!important}.mini-stat b{font-size:31px!important}.mini-stat span{font-size:12px!important;line-height:1.28!important}.quick-card{min-height:112px!important;padding:15px!important}.quick-icon{font-size:28px!important}.quick-title{font-size:17px!important}.quick-sub{font-size:12.5px!important}.st-key-draft_view div[role="radiogroup"]{gap:6px!important}.st-key-draft_view div[role="radiogroup"] label{min-height:84px!important;padding-left:2px!important;padding-right:2px!important}.st-key-draft_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:12px!important}.player-shell.draft-player{grid-template-columns:36px minmax(0,1fr) 37px 37px 58px!important;padding-left:6px!important;padding-right:6px!important}}

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


/* NOVA CANONICAL UI — Draft Guide typography/layout is the authority. */
:root{--sh-bg:#071019;--sh-card:#0e1821;--sh-card2:#101d27;--sh-line:rgba(74,96,113,.38);--sh-text:#f4f7f9;--sh-muted:#9cacb8;--sh-teal:#74e3d2;--sh-lime:#d9ff38}
html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif!important}
.app-top{display:flex!important;padding:5px 1px 9px!important;margin:0!important}.brand-wrap{display:flex!important;align-items:center!important;gap:8px!important}.brand-badge{border-radius:6px!important}.brand-name{display:block!important;font-size:20px!important;font-weight:950!important;letter-spacing:-.45px!important;color:#fff!important}.brand-sub{display:none!important}
.screen-head{margin:3px 0 10px!important}.screen-head h1{font-size:23px!important;line-height:1.08!important;font-weight:950!important;letter-spacing:-.55px!important}.screen-head p{font-size:12.5px!important;line-height:1.4!important;color:var(--sh-muted)!important;margin-top:4px!important}
h1,h2,h3,h4{letter-spacing:-.35px!important}.stMarkdown p,.stCaption{line-height:1.42!important}
.hero-card,.home-shiva-hero,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat,.guide-card,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell,.st-key-home_shiva_card{border-radius:7px!important;border:1px solid var(--sh-line)!important;background:linear-gradient(145deg,var(--sh-card2),var(--sh-card))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025),0 4px 11px rgba(0,0,0,.13)!important}
.stButton>button,.stDownloadButton>button{border-radius:6px!important;min-height:40px!important;padding:7px 10px!important;border:1px solid rgba(81,103,119,.42)!important;background:linear-gradient(180deg,#14222d,#0e1922)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important;font-size:12px!important;font-weight:900!important;letter-spacing:.05px!important}
.stButton>button[kind="primary"],.st-key-home_shiva_go .stButton>button,.st-key-shiva_page_go .stButton>button{border-radius:6px!important;background:linear-gradient(180deg,rgba(39,91,86,.76),rgba(17,48,46,.94))!important;border-color:rgba(116,227,210,.30)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.035)!important}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{border-radius:6px!important;background:#0a151d!important;border-color:rgba(81,103,119,.40)!important;font-size:13px!important}
/* Guide and Draft selectors: compact editorial tabs, not bubbles/cards. */
.st-key-guide_tab div[role="radiogroup"],.st-key-draft_view div[role="radiogroup"]{display:grid!important;gap:4px!important;width:100%!important}
.st-key-guide_tab div[role="radiogroup"]{grid-template-columns:repeat(5,minmax(0,1fr))!important}.st-key-draft_view div[role="radiogroup"]{grid-template-columns:repeat(4,minmax(0,1fr))!important}
.st-key-guide_tab div[role="radiogroup"] label,.st-key-draft_view div[role="radiogroup"] label{min-height:38px!important;padding:5px 3px!important;border-radius:5px!important;background:#0c171f!important;border:1px solid rgba(74,96,113,.36)!important;box-shadow:none!important;display:flex!important;align-items:center!important;justify-content:center!important}
.st-key-guide_tab div[role="radiogroup"] label>div:first-child,.st-key-draft_view div[role="radiogroup"] label>div:first-child,.st-key-guide_tab input[type="radio"],.st-key-draft_view input[type="radio"]{display:none!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked),.st-key-draft_view div[role="radiogroup"] label:has(input:checked){background:linear-gradient(180deg,rgba(42,91,86,.28),rgba(12,29,30,.86))!important;border-color:rgba(116,227,210,.25)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after,.st-key-draft_view div[role="radiogroup"] label:has(input:checked)::after{display:none!important;content:none!important}
.st-key-guide_tab div[role="radiogroup"] p,.st-key-draft_view div[role="radiogroup"] p{font-size:10px!important;line-height:1.05!important;font-weight:900!important;color:#b6c2cb!important;text-transform:none!important;white-space:normal!important;text-align:center!important;margin:0!important}.st-key-guide_tab div[role="radiogroup"] label:has(input:checked) p,.st-key-draft_view div[role="radiogroup"] label:has(input:checked) p{color:#f5fbfa!important}
/* Position filters are small squared pills, multi-select capable. */
.stMultiSelect [data-baseweb="tag"]{border-radius:4px!important;background:rgba(45,92,87,.38)!important;border:1px solid rgba(116,227,210,.20)!important;color:#fff!important;font-size:11px!important}
.quick-grid{gap:7px!important}.quick-card{padding:12px!important;min-height:90px!important}.quick-icon{font-size:19px!important}.quick-title{font-size:14px!important;line-height:1.15!important}.quick-sub{font-size:11px!important;line-height:1.32!important;color:var(--sh-muted)!important}.mini-stat{min-height:104px!important;padding:11px 6px!important}.mini-stat b{font-size:28px!important}.mini-stat span{font-size:11px!important}.flip-face{border-radius:7px!important}
.bottom-nav{height:68px!important}.bottom-nav a{border-radius:5px!important;min-height:50px!important;font-size:9px!important}.bottom-nav a.active{background:rgba(34,68,67,.28)!important}.nav-icon{font-size:18px!important}
/* Shiva IQ: restrained silhouette with calculation stream, no emoji brain. */
.shiva-iq-panel{min-height:154px!important;padding:16px!important}.shiva-iq-panel h2{font-size:24px!important}.shiva-iq-panel p{font-size:12.5px!important}.iq-visual{opacity:.76!important}.iq-head{border-radius:46% 41% 37% 50%!important}.iq-formulas{font-size:7px!important;color:rgba(116,227,210,.50)!important}.iq-report-title{font-size:16px!important}.iq-report-copy{font-size:12px!important}
@media(max-width:430px){.main .block-container{padding-left:11px!important;padding-right:11px!important}.screen-head h1{font-size:22px!important}.st-key-guide_tab div[role="radiogroup"] label,.st-key-draft_view div[role="radiogroup"] label{min-height:38px!important;border-radius:5px!important}.st-key-guide_tab div[role="radiogroup"] p,.st-key-draft_view div[role="radiogroup"] p{font-size:9.5px!important}.player-name{font-size:14px!important}.player-meta{font-size:10.5px!important}.quick-card{border-radius:7px!important}.stButton>button,.stDownloadButton>button{border-radius:6px!important}}

.shiva-iq-mark{width:34px;height:34px;display:inline-block;vertical-align:middle;filter:drop-shadow(0 0 5px rgba(37,140,255,.34))}.bottom-nav .shiva-iq-mark{width:23px;height:23px}.iq-visual .shiva-iq-mark{width:112px;height:112px;opacity:.9}


/* SURGICAL HOME SHIVA CARD — do not alter any other page/card/layout. */
.st-key-home_shiva_card{position:relative!important;margin:4px 0 12px!important;padding:15px 14px 14px!important;border-radius:17px!important;border:1px solid rgba(74,139,196,.34)!important;background:linear-gradient(145deg,rgba(13,31,45,.98),rgba(6,17,26,.99) 70%)!important;box-shadow:inset 0 1px 0 rgba(166,214,255,.10),inset 0 -1px 0 rgba(0,0,0,.38),0 7px 20px rgba(0,0,0,.20),0 0 0 .5px rgba(61,141,211,.12)!important;overflow:hidden!important}
.st-key-home_shiva_card:before{display:block!important;content:""!important;position:absolute!important;inset:0!important;pointer-events:none!important;background:radial-gradient(circle at 87% 14%,rgba(39,132,219,.12),transparent 29%),linear-gradient(110deg,rgba(38,116,181,.05),transparent 36%)!important}
.st-key-home_shiva_card .home-shiva-hero{position:relative!important;margin:0 0 12px!important;padding:2px 2px 15px!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;border-bottom:1px solid rgba(92,126,151,.25)!important;overflow:hidden!important;min-height:168px!important}
.st-key-home_shiva_card .home-shiva-kicker{position:relative!important;z-index:2!important;color:#4fa8f2!important;font-size:11px!important;letter-spacing:.9px!important}
.st-key-home_shiva_card .home-shiva-title{position:relative!important;z-index:2!important;color:#fff!important;font-size:27px!important;line-height:1.04!important;font-weight:950!important;letter-spacing:-.7px!important;margin:7px 0 8px!important;max-width:78%!important}
.st-key-home_shiva_card .home-shiva-copy{position:relative!important;z-index:2!important;color:#b8c5cf!important;font-size:14px!important;line-height:1.48!important;max-width:78%!important;margin:0!important}
.home-shiva-brain{position:absolute!important;right:-3px!important;top:3px!important;width:128px!important;height:128px!important;opacity:.72!important;filter:drop-shadow(0 0 9px rgba(37,140,255,.13))!important;pointer-events:none!important}
.st-key-home_shiva_card .home-ask-label{font-size:13px!important;font-weight:900!important;color:#f1f5f8!important;margin:0 0 7px!important}
.st-key-home_shiva_card .stTextArea textarea{background:#0b151e!important;border:1px solid rgba(91,118,139,.38)!important;border-radius:10px!important;box-shadow:inset 0 1px 2px rgba(0,0,0,.34)!important;color:#f4f7f9!important}
.st-key-home_shiva_go .stButton>button{min-height:50px!important;border-radius:10px!important;border:1px solid rgba(70,139,199,.45)!important;background:linear-gradient(105deg,rgba(34,108,174,.68),rgba(23,72,112,.44) 34%,rgba(12,29,42,.98) 74%)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.08),inset 0 -7px 16px rgba(0,0,0,.16),0 5px 13px rgba(0,0,0,.18)!important;color:#fff!important;font-size:15px!important;font-weight:950!important}

'''
source = source.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)", "\n" + mobile_css + "\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)", 1)


# Draft view selector remains directly below the Draft Room heading.
draft_start = source.index('def draft():')
draft_end = source.index('\ndef player_db():', draft_start)
draft_block = source[draft_start:draft_end]
old_line = '    screen_head("Draft Room","Live snake draft built for a phone.")\n    slot_options=list(range(1,st.session_state.team_count+1))'
new_line = '    screen_head("Draft Room","Live snake draft built for a phone.")\n    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")\n    slot_options=list(range(1,st.session_state.team_count+1))'
if old_line in draft_block:
    draft_block = draft_block.replace(old_line, new_line, 1)
    draft_block = draft_block.replace('    view=st.radio("Draft view",["Players","Board","Queue","Roster"],horizontal=True,label_visibility="collapsed",key="draft_view")\n', '', 1) if draft_block.count('view=st.radio("Draft view"') > 1 else draft_block
source = source[:draft_start] + draft_block + source[draft_end:]

# Keep draft actions recoverable with Undo + Reset.
source = source.replace(
    '    if st.button("Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.rerun()\ndef player_db():',
    '''    ctrl1,ctrl2=st.columns(2)\n    with ctrl1:\n        if st.button("↶ Undo Last Pick",use_container_width=True,disabled=not bool(st.session_state.draft_log)):\n            last_user_idx=next((i for i in range(len(st.session_state.draft_log)-1,-1,-1) if st.session_state.draft_log[i]["team"]==st.session_state.user_slot),None)\n            if last_user_idx is not None:st.session_state.draft_log=st.session_state.draft_log[:last_user_idx]\n            else:st.session_state.draft_log=st.session_state.draft_log[:-1]\n            st.session_state["shiva_iq_recs"]=[];st.rerun()\n    with ctrl2:\n        if st.button("↻ Reset Draft",use_container_width=True):st.session_state.draft_log=[];st.session_state.queue=[];st.session_state["shiva_iq_recs"]=[];st.rerun()\ndef player_db():''',
    1,
)

# Shared internal-data-first Shiva engine.
ask_start = source.index('def ask_shiva(question:str)->str:')
ask_end = source.index('\ndef home():', ask_start)
new_ask = r'''def _shiva_parse_top_n(question:str)->int:
    m=re.search(r"\btop\s+(\d{1,2})\b",question.casefold())
    return max(1,min(25,int(m.group(1)))) if m else 5

def _shiva_position(question:str)->str|None:
    q=question.casefold()
    aliases={"RB":["running back","running backs"," rb ","rbs"],"WR":["wide receiver","wide receivers"," wr ","wrs"],"QB":["quarterback","quarterbacks"," qb ","qbs"],"TE":["tight end","tight ends"," te ","tes"]}
    padded=f" {q} "
    for pos,words in aliases.items():
        if any(w in padded for w in words):return pos
    return None

def _shiva_years(question:str,weekly:pd.DataFrame)->list[int]:
    available=sorted(pd.to_numeric(weekly.get("season",pd.Series(dtype=float)),errors="coerce").dropna().astype(int).unique().tolist())
    if not available:return []
    explicit=sorted({int(y) for y in re.findall(r"\b20\d{2}\b",question) if int(y) in available})
    if len(explicit)>=2:
        lo,hi=min(explicit),max(explicit);return [y for y in available if lo<=y<=hi]
    if len(explicit)==1:return explicit
    q=question.casefold();m=re.search(r"last\s+(\d{1,2})\s+(?:years|seasons)",q)
    n=max(1,min(12,int(m.group(1)))) if m else 5
    return available[-n:]

def _shiva_name_col(weekly:pd.DataFrame)->str|None:
    return next((c for c in ("player_display_name","player_name","name") if c in weekly.columns),None)

def _shiva_internal_result(question:str)->dict:
    result={"answer":"","method":"","data_used":"","seasons":"","table":pd.DataFrame(),"internal":False}
    q=question.casefold().strip()
    try:weekly=load_weekly().copy()
    except Exception as exc:
        result["method"]=f"Internal weekly database could not be loaded: {exc}";return result
    nc=_shiva_name_col(weekly)
    if weekly.empty or not nc:return result
    weekly["_ppr"]=espn_ppr(weekly)
    years=_shiva_years(question,weekly)
    if years:weekly=weekly.loc[pd.to_numeric(weekly["season"],errors="coerce").isin(years)].copy()
    pos=_shiva_position(question)
    poscol="position" if "position" in weekly.columns else None
    if pos and poscol:
        weekly=weekly.loc[weekly[poscol].astype(str).str.upper().replace({"HB":"RB","FB":"RB","D/ST":"DST","DEF":"DST"}).eq(pos)].copy()
    names=[]
    for n in players["name"].astype(str).tolist():
        if name_key(n) and name_key(n) in name_key(question):names.append(n)
    metric="ppg"
    if "total" in q and ("point" in q or "ppr" in q):metric="total"
    if "15+" in q or "15 plus" in q or "15-point" in q or "15 point" in q:metric="weeks15"
    if any(x in q for x in ("average","per game","ppg")):metric="ppg"

    if names:
        rows=[]
        for name in names[:6]:
            pf=weekly.loc[weekly[nc].astype(str).map(name_key).eq(name_key(name))].copy()
            if pf.empty:continue
            pts=pf["_ppr"].dropna();rows.append({"Player":name,"Games":len(pts),"Total PPR":round(float(pts.sum()),1),"PPR/Game":round(float(pts.mean()),2) if len(pts) else None,"15+ PPR Weeks":int((pts>=15).sum())})
        if rows:
            df=pd.DataFrame(rows);result.update(internal=True,table=df,seasons=", ".join(map(str,years)) if years else "all available seasons",data_used="Internal weekly player history and ESPN full-PPR scoring")
            result["method"]="For each named player, Shiva filtered the internal weekly game log to the selected seasons, calculated PPR points for each game, then summarized games, total PPR, PPR per game, and 15+ point weeks."
            result["answer"]="Here’s the internal-data comparison:\n\n"+"\n".join(f"**{r['Player']}** — {r['PPR/Game']:.2f} PPR/game, {r['Total PPR']:.1f} total PPR, {r['15+ PPR Weeks']} weeks of 15+ points across {r['Games']} games." for r in rows)
            return result

    ranking_words=("top","best","highest","leaders","most")
    if any(w in q for w in ranking_words) and (pos or "player" in q or "ppr" in q or "point" in q):
        grouped=weekly.groupby(nc,dropna=True)["_ppr"].agg(Games="count",Total_PPR="sum",PPR_Game="mean",Weeks_15=lambda x:int((x>=15).sum())).reset_index().rename(columns={nc:"Player"})
        grouped=grouped.loc[grouped["Games"]>=3].copy()
        n=_shiva_parse_top_n(question)
        sortcol={"ppg":"PPR_Game","total":"Total_PPR","weeks15":"Weeks_15"}[metric]
        top=grouped.sort_values([sortcol,"Games"],ascending=[False,False]).head(n).copy()
        top["Total PPR"]=top["Total_PPR"].round(1);top["PPR/Game"]=top["PPR_Game"].round(2);top["15+ PPR Weeks"]=top["Weeks_15"].astype(int)
        table=top[["Player","Games","Total PPR","PPR/Game","15+ PPR Weeks"]].reset_index(drop=True);table.index=table.index+1
        metric_label={"ppg":"PPR per game","total":"total PPR points","weeks15":"15+ PPR-point weeks"}[metric]
        lines=[]
        for rank,(_,r) in enumerate(table.iterrows(),1):lines.append(f"**{rank}. {r['Player']}** — {r['PPR/Game']:.2f} PPR/game, {r['Total PPR']:.1f} total, {int(r['15+ PPR Weeks'])} weeks of 15+ points.")
        result.update(internal=True,table=table,seasons=", ".join(map(str,years)) if years else "all available seasons",data_used=f"Internal weekly game log{f' filtered to {pos}' if pos else ''} with ESPN full-PPR scoring",method=f"Shiva filtered the internal weekly database to {', '.join(map(str,years)) if years else 'the available seasons'}{f' and {pos}s' if pos else ''}, calculated PPR for each player-game, grouped by player, then ranked the results by {metric_label}. Players needed at least three games in the filtered sample.",answer=f"Using the app’s internal data, the top {len(table)}{f' {pos}s' if pos else ' players'} by {metric_label} are:\n\n"+"\n".join(lines))
        return result

    if any(x in q for x in ("who should i draft","who do i draft","draft next","best available","my roster")):
        avail=available_df().head(12).copy();rost=user_roster();cols=[c for c in ("name","pos","team","draft_adp","overall_rank") if c in avail.columns]
        table=avail[cols].rename(columns={"name":"Player","pos":"Pos","team":"Team","draft_adp":"ADP","overall_rank":"Rank"}).copy()
        roster_text=", ".join(f"{r['name']} ({r['pos']})" for _,r in rost.iterrows()) if not rost.empty else "No players drafted yet"
        first=table.iloc[0] if not table.empty else None
        answer=(f"Based on the live internal draft board, **{first['Player']} ({first['Pos']})** is the best available market-value option right now. " if first is not None else "The internal available-player pool is empty. ")+f"Your current roster: {roster_text}."
        result.update(internal=True,table=table,seasons="Current 2026 draft state",data_used="Live available-player pool, rankings/ADP, and your current drafted roster",method="Shiva read the app’s live roster and available-player pool first, then ordered the current options by the app’s draft market/ranking data before any AI explanation.",answer=answer)
        return result
    return result

def ask_shiva_full(question:str)->dict:
    internal=_shiva_internal_result(question)
    answer=internal.get("answer","")
    key=None
    try:key=st.secrets.get("OPENAI_API_KEY")
    except Exception:pass
    key=key or os.getenv("OPENAI_API_KEY")
    if key and OpenAI is not None:
        roster=user_roster();rt=", ".join(roster["name"].tolist()) if not roster.empty else "None"
        evidence=internal.get("table",pd.DataFrame())
        evidence_text=evidence.to_string(index=False) if isinstance(evidence,pd.DataFrame) and not evidence.empty else "No structured internal table was generated."
        system="You are Shiva, an elite fantasy-football analyst. ESPN full 1-point PPR is the default. INTERNAL APP DATA IS AUTHORITATIVE. Never alter, invent, or contradict supplied numbers. Return exactly four concise sections with these headings: SHORT ANSWER, WHY & QUICK RULES, EXCEPTIONS, ACTIONABLE CHECKLIST. SHORT ANSWER must be 2-3 sentences maximum and lead with the recommendation. Put supporting detail in WHY & QUICK RULES. Put caveats only in EXCEPTIONS. Put concrete next steps only in ACTIONABLE CHECKLIST. Keep mobile readability high; avoid giant paragraphs. If internal evidence does not answer the question, clearly say what is uncertain."
        prompt=f"Question: {question}\nCurrent roster: {rt}\nInternal answer: {answer or 'No deterministic internal answer'}\nInternal evidence:\n{evidence_text}\nMethod: {internal.get('method','')}\nGive the user a concise useful answer."
        try:
            ai=OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=[{"role":"system","content":system},{"role":"user","content":prompt}]).output_text
            if ai:answer=ai
        except Exception:
            if not answer:answer="Shiva’s AI explanation is temporarily unavailable, but the app’s internal data engine is still online. Try a statistical, player-history, ranking, or live-draft question."
    if not answer:
        answer="I can answer directly from Shiva’s internal database for player history, PPR scoring, multi-season leaders, rankings, ADP, and your live draft state. Try something like: “Top 5 RBs by PPR per game over the last 5 seasons.”"
        internal["method"]="No matching deterministic internal query pattern was found, so no statistic was fabricated."
        internal["data_used"]="No internal result generated"
        internal["seasons"]="—"
    internal["answer"]=answer
    return internal

def ask_shiva(question:str)->str:
    return ask_shiva_full(question).get("answer","")

def _render_shiva_work(item:dict,key:str):
    with st.expander("* See Shiva's work",expanded=False):
        st.markdown(f'<div class="work-note"><b>Data used:</b> {html.escape(str(item.get("data_used") or "Internal app data"))}<br><b>Seasons / scope:</b> {html.escape(str(item.get("seasons") or "—"))}<br><b>How Shiva calculated it:</b> {html.escape(str(item.get("method") or "No calculation details available."))}</div>',unsafe_allow_html=True)
        table=item.get("table")
        if isinstance(table,pd.DataFrame) and not table.empty:st.dataframe(table,use_container_width=True)

def _shiva_answer_sections(text:str)->dict:
    raw=str(text or "").strip()
    sections={"short":"","why":"","exceptions":"","checklist":""}
    if not raw:return sections
    lines=[x.strip() for x in raw.splitlines() if x.strip()]
    current="short"
    for line in lines:
        clean=re.sub(r"^[#*\-\s]+","",line).strip()
        low=clean.casefold().rstrip(":")
        if low.startswith("short answer"):
            current="short";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if low.startswith("why") or low.startswith("quick rule") or low.startswith("additional information"):
            current="why";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if low.startswith("exception"):
            current="exceptions";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        if "checklist" in low or low.startswith("before you pick") or low.startswith("actionable"):
            current="checklist";rest=clean.split(":",1)[1].strip() if ":" in clean else ""
            if rest:sections[current]+=("\n" if sections[current] else "")+rest
            continue
        sections[current]+=("\n" if sections[current] else "")+line
    if not sections["short"]:
        sections["short"]=raw
    return sections

def _ask_shiva_widget(prefix:str):
    q=st.text_area("Ask Shiva",placeholder="Ask about players, PPR history, rankings, your roster, or who to draft…",height=92,key=f"{prefix}_q",label_visibility="collapsed")
    if st.button("✦ GET SHIVA'S ANSWER",type="primary",use_container_width=True,key=f"{prefix}_go") and q.strip():
        with st.spinner("Reading Shiva's internal data…"):
            result=ask_shiva_full(q.strip())
        st.session_state[f"{prefix}_result"]={"question":q.strip(),**result}
        hist=st.session_state.get("ask_history",[])
        hist.insert(0,st.session_state[f"{prefix}_result"]);st.session_state["ask_history"]=hist[:12]
    item=st.session_state.get(f"{prefix}_result")
    if item:
        parts=_shiva_answer_sections(item.get("answer",""))
        short=parts.get("short","").strip()
        # Keep the default view fast: cap an unstructured response to its first useful paragraph/sentences.
        if "\n" in short and not any(parts.get(k) for k in ("why","exceptions","checklist")):
            chunks=[x.strip() for x in short.split("\n") if x.strip()]
            short=chunks[0] if chunks else short
        st.markdown(f'<div class="shiva-answer-summary"><span class="shiva-answer-label">Short answer</span>{html.escape(short).replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
        why=parts.get("why","").strip()
        exceptions=parts.get("exceptions","").strip()
        checklist=parts.get("checklist","").strip()
        # If an older/unstructured answer has no drawers yet, keep Shiva's calculation details available under Why & Quick Rules rather than dumping them on-screen.
        if not why:
            why=str(item.get("method") or "Shiva used the app’s internal data first, then summarized the result for the current question.")
        if not exceptions:
            exceptions="No specific exceptions were identified for this answer."
        if not checklist:
            checklist="Use the short answer as the default call, then check current roster construction, available-player value, and any late-breaking role or injury news before you pick."
        with st.expander("Why & Quick Rules",expanded=False):st.markdown(why)
        with st.expander("Exceptions",expanded=False):st.markdown(exceptions)
        with st.expander("Actionable Checklist",expanded=False):st.markdown(checklist)
        with st.expander("See Shiva's data",expanded=False):_render_shiva_work(item,prefix)

'''
source = source[:ask_start] + new_ask + source[ask_end:]

# Home: Shiva first, then descriptive stats, Blast, shortcuts, and four NFL stories.
home_start = source.index('def home():')
home_end = source.index('\ndef draft_guide():', home_start)
new_home = r'''def _run_iq_report(positions,season_count,metric,topn,min_games=3):
    weekly=load_weekly().copy();nc=_shiva_name_col(weekly)
    if weekly.empty or not nc:return pd.DataFrame(),[]
    weekly["_ppr"]=espn_ppr(weekly)
    seasons=sorted(pd.to_numeric(weekly["season"],errors="coerce").dropna().astype(int).unique())[-int(season_count):]
    weekly=weekly[pd.to_numeric(weekly["season"],errors="coerce").isin(seasons)].copy()
    if positions and "position" in weekly.columns:
        norm=weekly["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB","D/ST":"DST","DEF":"DST"})
        weekly=weekly[norm.isin(positions)].copy()
    out=weekly.groupby(nc)["_ppr"].agg(Games="count",Total_PPR="sum",PPR_Game="mean",Weeks_15=lambda x:int((x>=15).sum()),Best_Game="max").reset_index().rename(columns={nc:"Player"})
    out=out[out["Games"]>=int(min_games)].copy()
    col={"PPR per game":"PPR_Game","Total PPR":"Total_PPR","15+ PPR weeks":"Weeks_15","Best single game":"Best_Game"}[metric]
    out=out.sort_values([col,"Games"],ascending=[False,False]).head(int(topn)).reset_index(drop=True)
    out.index=out.index+1;out.index.name="Rank";out=out.reset_index()
    out["PPR_Game"]=out["PPR_Game"].round(2);out["Total_PPR"]=out["Total_PPR"].round(1);out["Best_Game"]=out["Best_Game"].round(1)
    return out,seasons

def _parse_iq_prompt(prompt):
    q=str(prompt or "").casefold();top=10;years=5;metric="PPR per game"
    m=re.search(r"top\s+(\d{1,2})",q)
    if m:top=max(1,min(50,int(m.group(1))))
    m=re.search(r"(?:last|past)\s+(\d{1,2})\s+(?:years|seasons)",q)
    if m:years=max(1,min(12,int(m.group(1))))
    positions=[];padded=f" {q} "
    aliases={"QB":["quarterback","quarterbacks"," qb ","qbs"],"RB":["running back","running backs"," rb ","rbs"],"WR":["wide receiver","wide receivers"," wr ","wrs"],"TE":["tight end","tight ends"," te ","tes"]}
    for p,words in aliases.items():
        if any(w in padded for w in words):positions.append(p)
    if "total" in q:metric="Total PPR"
    elif "15+" in q or "15 plus" in q or "consistency" in q:metric="15+ PPR weeks"
    elif "best game" in q or "ceiling" in q:metric="Best single game"
    return positions or ["QB","RB","WR","TE"],years,metric,top

def _shiva_report_builder():
    st.markdown('<div class="iq-report-shell"><div class="iq-report-title">Shiva IQ Reports</div><div class="iq-report-copy">Run a real query against the internal historical Full-PPR database, then export the exact result.</div></div>',unsafe_allow_html=True)
    prompt=st.text_input("Report request",placeholder="Top 5 running backs over the last 10 seasons by PPR per game",key="iq_report_prompt",label_visibility="collapsed")
    st.markdown('<div class="iq-presets">Examples: top 10 WRs last 5 seasons · most 15+ point weeks among RBs · top QBs last 3 seasons by total PPR</div>',unsafe_allow_html=True)
    if st.button("RUN SHIVA IQ REPORT",type="primary",use_container_width=True,key="iq_prompt_run") and prompt.strip():
        positions,years,metric,topn=_parse_iq_prompt(prompt);out,seasons=_run_iq_report(positions,years,metric,topn)
        st.session_state["iq_report_df"]=out;st.session_state["iq_report_scope"]=(positions,seasons,metric)
    with st.expander("Advanced report controls",expanded=False):
        positions=st.multiselect("Positions",["QB","RB","WR","TE"],default=["RB"],key="iq_report_pos")
        years=st.slider("Seasons",1,12,5,key="iq_report_years")
        metric=st.selectbox("Rank by",["PPR per game","Total PPR","15+ PPR weeks","Best single game"],key="iq_report_metric")
        topn=st.slider("Players",5,50,10,5,key="iq_report_topn");min_games=st.slider("Minimum games",1,40,3,key="iq_report_min_games")
        if st.button("RUN ADVANCED REPORT",use_container_width=True,key="iq_run_report"):
            out,seasons=_run_iq_report(positions,years,metric,topn,min_games);st.session_state["iq_report_df"]=out;st.session_state["iq_report_scope"]=(positions,seasons,metric)
    out=st.session_state.get("iq_report_df")
    if isinstance(out,pd.DataFrame) and not out.empty:
        positions,seasons,metric=st.session_state.get("iq_report_scope",([],[],"PPR per game"));scope=f"{', '.join(positions)} · {min(seasons)}–{max(seasons)} · {metric}" if seasons else metric
        st.markdown(f'<div class="iq-result-note">{html.escape(scope)} · {len(out)} players</div>',unsafe_allow_html=True);st.dataframe(out,use_container_width=True,hide_index=True)
        c1,c2=st.columns(2)
        with c1:st.download_button("DOWNLOAD CSV",out.to_csv(index=False).encode(),"shiva_iq_report.csv","text/csv",use_container_width=True)
        try:
            import io
            buf=io.BytesIO()
            with pd.ExcelWriter(buf,engine="openpyxl") as writer:out.to_excel(writer,index=False,sheet_name="Shiva IQ Report")
            with c2:st.download_button("DOWNLOAD EXCEL",buf.getvalue(),"shiva_iq_report.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        except Exception:
            with c2:st.caption("Excel export unavailable on this deployment.")

def _home_shiva_blast():
    components.html(r"""
    <style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden;width:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color-scheme:dark}
      #wrap{width:100%;box-sizing:border-box;background:transparent}
      #bar{display:flex;justify-content:flex-end;align-items:center;height:34px}
      #shivaBlast{width:122px;height:34px;border-radius:8px;border:1px solid rgba(74,156,255,.48);background:linear-gradient(135deg,rgba(37,140,255,.78),rgba(20,91,171,.62) 58%,rgba(11,48,91,.48));color:#fff;font-weight:900;font-size:9px;letter-spacing:.12px;cursor:pointer;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 4px 12px rgba(82,8,25,.12);backdrop-filter:blur(8px)}
      #shivaBlast.playing{background:linear-gradient(135deg,rgba(32,125,230,.88),rgba(15,72,140,.72));border-color:rgba(104,181,255,.62)}
      #shivaBlast:active{transform:translateY(1px)}
      #stage{display:none;margin-top:7px;width:100%;background:transparent}
      #stage.open{display:block}
      #blastVideo{display:block;width:100%;height:auto;max-height:68vh;object-fit:contain;border-radius:12px;background:#000;box-shadow:0 12px 34px rgba(0,0,0,.42);cursor:pointer}
    </style>
    <div id="wrap">
      <div id="bar"><button id="shivaBlast">SHIVA BLAST</button></div>
      <div id="stage"><video id="blastVideo" playsinline preload="auto"><source src="https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/Blasting_compressed.mp4" type="video/mp4"></video></div>
    </div>
    <script>
      const btn=document.getElementById('shivaBlast');
      const stage=document.getElementById('stage');
      const video=document.getElementById('blastVideo');
      const frame=window.frameElement;
      let playing=false;
      const closedFrame=()=>{try{if(!frame)return;frame.style.position='absolute';frame.style.top='0';frame.style.right='0';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='122px';frame.style.height='36px';frame.style.zIndex='20';frame.style.border='0';frame.style.background='transparent';frame.style.boxShadow='none';frame.style.margin='0';}catch(e){}};
      const openFrame=()=>{try{if(!frame)return;frame.style.position='relative';frame.style.top='auto';frame.style.right='auto';frame.style.left='auto';frame.style.bottom='auto';frame.style.width='100%';frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';frame.style.zIndex='10';frame.style.border='0';frame.style.background='transparent';frame.style.margin='2px 0 8px';}catch(e){}};
      const syncOpenHeight=()=>{if(!playing||!frame)return;try{frame.style.height=Math.min(Math.max(document.documentElement.scrollHeight+8,250),680)+'px';}catch(e){}};
      const closeBlast=()=>{playing=false;video.pause();video.currentTime=0;video.controls=false;stage.classList.remove('open');btn.classList.remove('playing');btn.textContent='SHIVA BLAST';closedFrame();};
      const openBlast=()=>{playing=true;stage.classList.add('open');btn.classList.add('playing');btn.textContent='✕ STOP BLAST';openFrame();video.currentTime=0;video.muted=false;requestAnimationFrame(syncOpenHeight);const p=video.play();if(p&&p.catch)p.catch(()=>{video.controls=true;syncOpenHeight();});};
      btn.addEventListener('click',()=>playing?closeBlast():openBlast());
      video.addEventListener('click',closeBlast);
      video.addEventListener('ended',()=>setTimeout(closeBlast,100));
      video.addEventListener('loadedmetadata',syncOpenHeight);
      try{new ResizeObserver(syncOpenHeight).observe(document.getElementById('wrap'));}catch(e){}
      closedFrame();
    </script>
    """,height=34,scrolling=False)

def _home_nfl_news():
    st.markdown("#### Fantasy News")
    try:
        import json as _json
        from urllib.request import Request as _Request, urlopen as _urlopen
        req=_Request("https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100",headers={"User-Agent":"Mozilla/5.0 (iPhone; Shiva Fantasy Football)"})
        with _urlopen(req,timeout=10) as resp:data=_json.loads(resp.read().decode("utf-8"))
        articles=[];seen=set()
        for a in data.get("articles",[]):
            headline=str(a.get("headline") or "").strip();description=str(a.get("description") or "").strip()
            links=a.get("links",{}) or {};web=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            if not headline or not web:continue
            hay=(headline+" "+description+" "+str(web)).casefold()
            if "/fantasy/football/" not in hay and "fantasy football" not in hay:continue
            if web in seen:continue
            seen.add(web)
            img=""
            for candidate in (a.get("images") or []):
                if isinstance(candidate,dict) and candidate.get("url"):
                    img=str(candidate.get("url"));break
            articles.append((headline,web,img,description))
        if not articles:
            st.caption("Fantasy news is refreshing from ESPN.");return
        cards=[]
        for headline,web,img,description in articles:
            h=html.escape(headline);u=html.escape(web,quote=True);d=html.escape(description)
            media=f'<div class="fantasy-news-img"><img src="{html.escape(img,quote=True)}" alt=""></div>' if img else ''
            desc=f'<div class="fantasy-news-desc">{d}</div>' if d else ''
            cards.append(f'<a class="fantasy-news-card" href="{u}" target="_blank" rel="noopener noreferrer">{media}<div class="fantasy-news-body"><div class="fantasy-news-headline">{h}</div>{desc}<div class="fantasy-news-meta">ESPN · Fantasy Football</div></div></a>')
        css='<style>.fantasy-news-list{display:flex;flex-direction:column;gap:9px;margin:7px 0 14px}.fantasy-news-card{display:grid;grid-template-columns:112px minmax(0,1fr);overflow:hidden;text-decoration:none!important;color:#fff!important;background:#0e1821;border:1px solid #253644;border-radius:9px;min-height:86px}.fantasy-news-card:not(:has(.fantasy-news-img)){grid-template-columns:1fr}.fantasy-news-img{width:112px;height:100%;min-height:86px;background:#172430;overflow:hidden}.fantasy-news-img img{display:block;width:100%;height:100%;object-fit:cover}.fantasy-news-body{padding:9px 10px 10px;min-width:0}.fantasy-news-headline{font-size:13px;font-weight:950;line-height:1.27;color:#fff}.fantasy-news-desc{font-size:10.5px;line-height:1.32;color:#9eacb7;margin-top:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.fantasy-news-meta{font-size:9px;color:#8fa0ae;margin-top:7px;font-weight:850;text-transform:uppercase;letter-spacing:.15px}@media(max-width:430px){.fantasy-news-card{grid-template-columns:96px minmax(0,1fr);min-height:80px}.fantasy-news-img{width:96px;min-height:80px}.fantasy-news-headline{font-size:12.5px}.fantasy-news-desc{font-size:10px}}</style><div class="fantasy-news-list">'+"".join(cards)+"</div>"
        st.markdown(css,unsafe_allow_html=True)
    except Exception:
        st.caption("Fantasy news is refreshing from ESPN.")

def home():
    with st.container(key="home_shiva_card"):
        st.markdown('<div class="home-shiva-hero"><div class="home-shiva-kicker">Your fantasy football copilot</div><div class="home-shiva-title">Shiva Draft Intelligence</div><div class="home-shiva-copy">Ask Shiva for help building your championship team. Player history, PPR scoring, rankings and your live draft data are checked inside the app first.</div><svg class="home-shiva-brain" viewBox="0 0 120 120" aria-hidden="true"><g fill="none" stroke="#258cff" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" opacity=".68"><path d="M31 100c5-14 3-22-3-31-5-8-7-18-4-29 5-18 21-30 41-30 23 0 42 17 42 39 0 13-5 23-13 31-5 5-7 11-7 20"/><path d="M42 31h19l9-8M42 45h31l10-10M42 60h25l11 10M42 76h20l9 10M77 28h17M80 45h20M79 62h17M74 80h18"/><circle cx="70" cy="23" r="2" fill="#258cff"/><circle cx="83" cy="35" r="2" fill="#258cff"/><circle cx="78" cy="70" r="2" fill="#258cff"/><circle cx="71" cy="86" r="2" fill="#258cff"/></g><path d="M38 48l5 10 11 5-11 5-5 10-5-10-11-5 11-5z" fill="#429cff" filter="url(#g)"/><defs><filter id="g"><feGaussianBlur stdDeviation="1.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs></svg></div>',unsafe_allow_html=True)
        st.markdown('<div class="home-ask-label">Ask Shiva anything</div>',unsafe_allow_html=True)
        _ask_shiva_widget("home_shiva")
    try:
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
        .flip-face{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;border:1px solid #2a3a47;border-radius:9px;background:#0e1821;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.14);overflow:hidden}
        .flip-front .flip-num{font-size:29px;line-height:.95;font-weight:980;color:#fff;letter-spacing:-1px}.flip-front .flip-pos{font-size:11px;line-height:1;margin-top:7px;font-weight:950;color:#9aabb8;letter-spacing:.8px}
        .flip-back{transform:rotateY(180deg);padding:7px 5px;text-align:center;background:#101c26}.flip-back b{font-size:10px;line-height:1.15;color:#fff;display:block}.flip-back span{font-size:8px;line-height:1.22;color:#a5b4bf;display:block;margin-top:4px;font-weight:750}
        @media(max-width:370px){.flip-stat-grid{gap:4px}.flip-stat label{height:80px}.flip-front .flip-num{font-size:25px}.flip-back b{font-size:9px}.flip-back span{font-size:7px}}
        </style><div class=\"stat-hint\">Tap a stat card to reveal the stat</div><div class=\"flip-stat-grid\">"""
        for i,_pos in enumerate(("RB","WR","QB","TE")):
            _n=counts[_pos]
            flip_cards+=f"<div class=\"flip-stat\"><input type=\"checkbox\" id=\"flip-stat-{i}\"><label for=\"flip-stat-{i}\"><div class=\"flip-inner\"><div class=\"flip-face flip-front\"><div class=\"flip-num\">{_n}</div><div class=\"flip-pos\">{_pos}</div></div><div class=\"flip-face flip-back\"><b>{_n} {_pos}s</b><span>15+ PPR points in 8+ weeks</span></div></div></label></div>"
        flip_cards+='</div>'
        st.markdown(flip_cards,unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="stat-strip"><div class="mini-stat metric-rb"><b>11</b><span>RB</span></div><div class="mini-stat metric-wr"><b>9</b><span>WR</span></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="quick-grid">'+f'<a class="quick-card q-draft" href="{page_href("Draft")}" target="_self"><div class="quick-icon">🏈</div><div class="quick-title">Draft Room</div><div class="quick-sub">Players, board, queue and roster</div></a>'+f'<a class="quick-card q-guide" href="{page_href("Guide")}" target="_self"><div class="quick-icon">📖</div><div class="quick-title">2026 Shiva Draft Guide</div><div class="quick-sub">Draft-day strategy and rankings</div></a>'+f'<a class="quick-card q-players" href="{page_href("Players")}" target="_self"><div class="quick-icon">👥</div><div class="quick-title">Players</div><div class="quick-sub">Profiles and weekly history</div></a>'+f'<a class="quick-card q-roster" href="{page_href("Roster")}" target="_self"><div class="quick-icon">☷</div><div class="quick-title">My Roster</div><div class="quick-sub">Your live construction by slot</div></a></div>',unsafe_allow_html=True)
    _home_nfl_news()
'''
source = source[:home_start] + new_home + source[home_end:]

# Dedicated Shiva page reuses the exact same engine and evidence UI as Home.
shiva_start = source.index('def shiva():')
shiva_end = source.index('\ndef roster_screen():', shiva_start)
new_shiva = r'''def shiva():
    st.markdown('<div class="shiva-iq-panel"><div class="iq-kicker">Internal data engine</div><h2>Shiva IQ</h2><p>Ask a draft question or run a structured report across the historical ESPN Full-PPR database.</p><div class="iq-visual"><svg class="shiva-iq-mark" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="#258cff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 51c2-7 2-10-1-14-3-4-4-9-3-14 2-9 10-15 20-15 11 0 20 8 20 19 0 6-2 10-6 14-2 2-3 5-3 10"/><path d="M23 18h9l4-4m-13 11h15l5-5m-20 12h12l5 5m-17 2h10l4 5m4-27h7m-6 8h10m-9 8h8"/><circle cx="36" cy="14" r="1.6" fill="#258cff"/><circle cx="43" cy="20" r="1.6" fill="#258cff"/><circle cx="40" cy="37" r="1.6" fill="#258cff"/><circle cx="37" cy="44" r="1.6" fill="#258cff"/></g><path d="M20 27l2.4 5.1L28 34.5l-5.6 2.4L20 42l-2.4-5.1-5.6-2.4 5.6-2.4z" fill="#3b9cff"/></svg><div class="iq-formulas">Σ PPR\nx̄=P/G\n15+ wk\nΔ ADP\n01 10 11\nRANK()</div></div></div>',unsafe_allow_html=True)
    st.markdown("### Ask Shiva")
    _ask_shiva_widget("shiva_page")
    _shiva_report_builder()
    history=st.session_state.get("ask_history",[])
    if history:
        with st.expander("Recent Shiva questions",expanded=False):
            for item in history[:5]:
                if isinstance(item,dict):st.markdown(f"**{html.escape(str(item.get('question','')))}**")

'''
source = source[:shiva_start] + new_shiva + source[shiva_end:]

# FINAL EVERY-PAGE DRAFT GUIDE DESIGN
source = source.replace("\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)", '\n'+'\n/* EVERY PAGE = DRAFT GUIDE. Final override, intentionally last. */\n[data-testid="stHeader"]{display:none!important;height:0!important;min-height:0!important}\n.stAppViewContainer{padding-top:0!important}.main{padding-top:0!important}.main .block-container,.block-container{padding-top:0!important;margin-top:0!important;max-width:1120px!important;padding-left:.55rem!important;padding-right:.55rem!important}\n.app-top{margin:0!important;padding:2px 1px 7px!important;min-height:0!important}.brand-wrap{gap:8px!important}.brand-badge{width:34px!important;height:34px!important;border-radius:7px!important;background:linear-gradient(145deg,#162735,#0a1219)!important;border:1px solid #294054!important;box-shadow:none!important}.brand-title{display:block!important;font-size:19px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.5px!important;color:#fff!important}.brand-sub{font-size:9px!important;color:#8fa0ae!important}.data-status{border-radius:6px!important;padding:5px 7px!important;font-size:9px!important}\n.screen-head{margin:2px 0 9px!important}.screen-head h1{font-size:24px!important;line-height:1.03!important;margin:0!important;font-weight:950!important;letter-spacing:-.7px!important}.screen-head p{font-size:13px!important;line-height:1.38!important;margin:4px 0 0!important;color:#9cadb9!important}\nh1,h2,h3,h4{font-weight:950!important;letter-spacing:-.45px!important}h3{font-size:18px!important}h4{font-size:16px!important}.stMarkdown p{font-size:13px!important;line-height:1.4!important}.stCaption{font-size:12px!important;color:#8fa0ae!important}\n/* Same surfaces as Draft Guide, everywhere. */\n.hero-card,.home-shiva-hero,.profile-hero,.shiva-box,.roster-slot,.player-shell,.pick-card,.weekly-card,.quick-card,.mini-stat,.strategy-box,.rounds,.draft-chip,.on-clock,.shiva-iq-panel,.iq-report-shell,.shiva-answer-summary,.espn-news-card,.flip-face{background:#0e1821!important;border:1px solid #22313f!important;border-radius:9px!important;box-shadow:none!important}\n/* Homepage becomes the Draft Guide visual language, not a separate design. */\n.st-key-home_shiva_card{background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;padding:0!important;margin:0 0 10px!important;overflow:visible!important}\n.st-key-home_shiva_card:before,.st-key-home_shiva_card:after,.home-shiva-hero:before,.home-shiva-hero:after{display:none!important;content:none!important}\n.home-shiva-hero{background:linear-gradient(145deg,#162735,#0a1219)!important;border:1px solid #294054!important;padding:16px!important;margin:2px 0 9px!important}.home-shiva-kicker,.hero-kicker,.iq-kicker{font-size:9px!important;color:#d9ff38!important;font-weight:950!important;letter-spacing:1px!important;text-transform:uppercase!important}.home-shiva-title{font-size:25px!important;line-height:1.02!important;font-weight:950!important;letter-spacing:-.65px!important;margin:5px 0!important}.home-shiva-copy{font-size:14px!important;line-height:1.38!important;color:#9cadb9!important;max-width:none!important;margin:0!important}.home-ask-label{font-size:12px!important;font-weight:900!important;color:#cbd5dc!important;margin:3px 0 5px!important}\n/* No colored shortcut bubbles. */\n.quick-grid{gap:7px!important;margin:7px 0 11px!important}.quick-card,.quick-card.q-draft,.quick-card.q-guide,.quick-card.q-players,.quick-card.q-roster{background:#0e1821!important;border-color:#22313f!important;border-radius:9px!important;box-shadow:none!important;padding:11px!important;min-height:82px!important}.quick-icon{font-size:19px!important}.quick-title{font-size:15px!important;line-height:1.15!important;font-weight:900!important;margin-top:3px!important}.quick-sub{font-size:11px!important;line-height:1.3!important;color:#8fa0ae!important;margin-top:3px!important}\n.flip-stat-grid{gap:6px!important}.flip-stat label{height:84px!important}.flip-face{background:#0e1821!important;border-color:#22313f!important;border-radius:9px!important}.flip-front .flip-num{font-size:29px!important}.flip-front .flip-pos{font-size:11px!important;color:#9cadb9!important}.flip-back{background:#101b24!important}.flip-back b{font-size:10px!important}.flip-back span{font-size:8px!important}.stat-hint{font-size:10px!important;color:#8fa0ae!important}\n.espn-news-grid{gap:7px!important;margin:7px 0 12px!important}.espn-news-card{background:#0e1821!important;border-color:#22313f!important;border-radius:9px!important;box-shadow:none!important}.espn-news-body{padding:8px 9px 9px!important}.espn-news-headline{font-size:13px!important;line-height:1.28!important}.espn-news-meta{font-size:9px!important;color:#8fa0ae!important}\n/* Buttons/inputs: compact ESPN/Draft Guide controls, not bubbles. */\n.stButton>button,.stDownloadButton>button{min-height:40px!important;border-radius:6px!important;border:1px solid #2b3d4b!important;background:#111d27!important;box-shadow:none!important;font-size:12px!important;font-weight:900!important;padding:7px 10px!important}.stButton>button[kind="primary"],.st-key-home_shiva_go .stButton>button,.st-key-shiva_page_go .stButton>button{background:linear-gradient(145deg,rgba(55,128,119,.32),rgba(17,43,43,.72))!important;border-color:rgba(116,227,210,.34)!important;color:#fff!important;text-shadow:none!important}.st-key-home_shiva_go:before,.st-key-shiva_page_go:before{display:none!important;content:none!important}\n.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{min-height:42px!important;border-radius:6px!important;background:#0c151d!important;border-color:#263745!important;font-size:13px!important}\n/* ALL radio/tab controls match the Guide controls. */\ndiv[role="radiogroup"]{gap:5px!important}div[role="radiogroup"] label{min-height:42px!important;border-radius:7px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;box-shadow:none!important;padding:6px 4px!important}div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,rgba(55,128,119,.28),rgba(17,43,43,.72))!important;border-color:rgba(116,227,210,.32)!important;box-shadow:none!important}div[role="radiogroup"] label:has(input:checked)::after{display:none!important;content:none!important}div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10.5px!important;line-height:1.08!important;font-weight:900!important;text-transform:none!important}\n.st-key-guide_tab div[role="radiogroup"] label,.st-key-draft_view div[role="radiogroup"] label{min-height:42px!important;border-radius:7px!important;padding:6px 4px!important}.st-key-guide_tab div[role="radiogroup"] label>div:first-child,.st-key-draft_view div[role="radiogroup"] label>div:first-child,.st-key-guide_tab input[type="radio"],.st-key-draft_view input[type="radio"]{display:none!important}.st-key-draft_view div[role="radiogroup"] label:nth-child(1) p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(2) p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(3) p::before,.st-key-draft_view div[role="radiogroup"] label:nth-child(4) p::before{display:none!important;content:none!important}\n.stMultiSelect [data-baseweb="tag"]{border-radius:5px!important;background:rgba(55,128,119,.25)!important;border:1px solid rgba(116,227,210,.25)!important;font-size:11px!important}\n/* Player, roster and profile typography is brought to Guide sizing. */\n.player-shell{padding:8px 9px!important;min-height:58px!important}.player-rank{border-radius:7px!important}.player-name{font-size:15px!important;line-height:1.12!important}.player-meta{font-size:10px!important}.data-cell span{font-size:8px!important}.data-cell b{font-size:12px!important}.draft-inline{border-radius:6px!important;box-shadow:none!important}.profile-hero{padding:14px!important}.profile-name-big{font-size:25px!important}.profile-sub{font-size:11px!important}.profile-metric{border-radius:7px!important}.weekly-card{padding:8px 9px!important}.roster-slot{padding:10px!important}.slot-player{font-size:14px!important}.slot-meta{font-size:10px!important}\n/* Shiva IQ follows the same restrained card system. */\n.shiva-iq-panel{background:linear-gradient(145deg,#162735,#0a1219)!important;border-color:#294054!important;padding:16px!important}.shiva-iq-panel h2{font-size:25px!important}.shiva-iq-panel p{font-size:13px!important;line-height:1.4!important;color:#9cadb9!important}.iq-report-shell{padding:11px!important}.iq-report-title{font-size:15px!important}.iq-report-copy{font-size:12px!important}.shiva-answer-summary{font-size:14px!important;line-height:1.45!important}\n/* Bottom nav stays quiet and compact. */\n.bottom-nav{height:68px!important;background:rgba(8,15,22,.98)!important;border-top:1px solid #263440!important;box-shadow:none!important}.bottom-nav a{border-radius:6px!important;min-height:50px!important;font-size:9px!important}.bottom-nav a.active{background:#172430!important}.nav-icon{font-size:18px!important}\n@media(max-width:430px){.main .block-container,.block-container{padding-top:0!important;padding-left:9px!important;padding-right:9px!important}.app-top{padding-top:1px!important}.home-shiva-title,.guide-hero h2{font-size:24px!important}.home-shiva-copy,.guide-hero p{font-size:13px!important}.quick-card{min-height:80px!important}.quick-title{font-size:14px!important}.player-name{font-size:14px!important}.stButton>button,.stDownloadButton>button{min-height:39px!important}}\n'+'\n</style>\'\'\'\nst.markdown(CSS, unsafe_allow_html=True)', 1)

exec(compile(source, str(Path(__file__).with_name("app_core.py")), "exec"), globals(), globals())
