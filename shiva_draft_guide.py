import html
import streamlit as st

PPR_BIG_BOARD = [
("RB","Jahmyr Gibbs"),("RB","Bijan Robinson"),("WR","Ja'Marr Chase"),("WR","Puka Nacua"),("RB","Christian McCaffrey"),("WR","Amon-Ra St. Brown"),("WR","Jaxon Smith-Njigba"),("RB","Jonathan Taylor"),("RB","James Cook III"),("WR","CeeDee Lamb"),("RB","Omarion Hampton"),("RB","Ashton Jeanty"),("WR","Justin Jefferson"),("RB","Chase Brown"),("RB","Kenneth Walker III"),("RB","Saquon Barkley"),("WR","Drake London"),("RB","De'Von Achane"),("TE","Brock Bowers"),("WR","A.J. Brown"),("WR","George Pickens"),("WR","Rashee Rice"),("WR","Nico Collins"),("RB","Derrick Henry"),("TE","Trey McBride"),("RB","Jeremiyah Love"),("WR","DeVonta Smith"),("WR","Malik Nabers"),("QB","Josh Allen"),("WR","Chris Olave"),("RB","Josh Jacobs"),("WR","Tee Higgins"),("RB","Breece Hall"),("WR","Jaylen Waddle"),("WR","Zay Flowers"),("RB","Kyren Williams"),("WR","Tetairoa McMillan"),("WR","Emeka Egbuka"),("WR","Luther Burden III"),("TE","Colston Loveland"),("RB","Javonte Williams"),("WR","Garrett Wilson"),("WR","Ladd McConkey"),("WR","DJ Moore"),("RB","Cam Skattebo"),("RB","Bucky Irving"),("RB","Travis Etienne Jr."),("TE","Tyler Warren"),("WR","Terry McLaurin"),("QB","Lamar Jackson")]

HALF_PPR_TOP = [
("RB","Jahmyr Gibbs"),("RB","Bijan Robinson"),("WR","Ja'Marr Chase"),("WR","Puka Nacua"),("RB","Christian McCaffrey"),("RB","Jonathan Taylor"),("WR","Amon-Ra St. Brown"),("WR","Jaxon Smith-Njigba"),("RB","James Cook III"),("RB","Omarion Hampton"),("RB","Ashton Jeanty"),("WR","CeeDee Lamb"),("WR","Justin Jefferson"),("RB","Kenneth Walker III"),("RB","Saquon Barkley"),("WR","Drake London"),("TE","Brock Bowers"),("RB","Derrick Henry"),("RB","Chase Brown"),("WR","George Pickens")]

POSITIONAL = {
"QB":["Josh Allen","Lamar Jackson","Drake Maye","Jayden Daniels","Joe Burrow","Jalen Hurts","Caleb Williams","Justin Herbert","Trevor Lawrence","Jaxson Dart"],
"RB":["Jahmyr Gibbs","Bijan Robinson","Christian McCaffrey","Jonathan Taylor","James Cook III","Omarion Hampton","Ashton Jeanty","Chase Brown","Kenneth Walker III","Saquon Barkley","De'Von Achane","Derrick Henry","Jeremiyah Love","Josh Jacobs","Breece Hall"],
"WR":["Ja'Marr Chase","Puka Nacua","Amon-Ra St. Brown","Jaxon Smith-Njigba","CeeDee Lamb","Justin Jefferson","Drake London","A.J. Brown","George Pickens","Rashee Rice","Nico Collins","DeVonta Smith","Malik Nabers","Chris Olave","Tee Higgins"],
"TE":["Brock Bowers","Trey McBride","Colston Loveland","Tyler Warren","Sam LaPorta","Harold Fannin Jr.","Tucker Kraft","Kyle Pitts Sr.","George Kittle","Dalton Kincaid"]}

ADJ = {
"QB":[("Josh Allen",23.2),("Matthew Stafford",20.6),("Patrick Mahomes",20.4),("Jaxson Dart",20.1),("Trevor Lawrence",19.9),("Drake Maye",19.8),("Dak Prescott",19.6),("Jacoby Brissett",18.9)],
"RB":[("Christian McCaffrey",24.8),("Jahmyr Gibbs",24.6),("Jonathan Taylor",23.8),("Bijan Robinson",22.0),("Chase Brown",21.0),("De'Von Achane",20.4),("Cam Skattebo",19.1),("Josh Jacobs",18.0)],
"WR":[("Puka Nacua",23.7),("Jaxon Smith-Njigba",20.4),("Amon-Ra St. Brown",20.3),("Ja'Marr Chase",20.1),("Drake London",19.7),("Rashee Rice",18.8),("Chris Olave",18.8),("CeeDee Lamb",16.6)],
"TE":[("Trey McBride",18.6),("Brock Bowers",16.4),("Tucker Kraft",16.2),("George Kittle",15.4),("Tyler Warren",13.1),("Dalton Kincaid",12.9),("Colston Loveland",12.9),("Travis Kelce",12.8)]}

NUGGETS = [
("Draft capital matters","Since 2015, the first 11 RBs selected top-25 in the NFL Draft all produced an RB1 fantasy season by Year 2. That puts major sophomore upside behind Ashton Jeanty and Omarion Hampton."),
("Rounds 1–2 are the RB ceiling zone","Joel's research found only 2 of 33 early-round RBs who reached 20+ PPR PPG came from Rounds 3–4. His preferred build starts RB/RB and aims for three RBs inside roughly the top 25–30."),
("Chase Brown environment","Cincinnati QBs were the NFL's top three in checkdown rate in 2025, and Zac Taylor has produced an RB1 in six straight seasons when Chase Brown's 2024 starts are counted."),
("Josh Allen is the outlier","Allen has finished top-two at QB in fantasy points six straight seasons. Joel also notes rushing QBs drafted in Rounds 2–5 have historically hit far more often than passing-only QBs."),
("Puka earns targets at a different level","Since 2024, Puka Nacua's targets per route sit at 36.8%; Joel notes no other qualified player is above 30%."),
("Dalton Kincaid: routes, not efficiency","Kincaid led 2025 TEs across a huge collection of per-route efficiency measures. The unlock is simply getting him on more routes."),
("Parker Washington late value","Over Jacksonville's final four games, Washington produced 454 receiving yards despite Brian Thomas Jr. and Jakobi Meyers each running more routes."),
("Luther Burden efficiency signal","Burden ranked eighth among WRs in fantasy points per snap as a rookie; six of the seven players ahead of him were fantasy WR1s."),
("CeeDee regression candidate — upward","Joel's 25-factor luck model rated CeeDee Lamb the unluckiest player of 2025, estimating roughly 2.7 PPG lost to bad-luck events."),
("Achane's receiving split matters","De'Von Achane has averaged 11.4 receiving PPG with Tua Tagovailoa in his career versus 3.4 in eight games without him."),
("Jaylen Warren receiving opportunity","Warren ranked top-two among RBs in targets per route, yards per route and missed tackles per reception in 2025; Pittsburgh also has 82 vacated RB targets."),
("Drake Maye game-script ceiling","Maye was QB1 over quarters 1–3 last season but QB32 in fourth quarters. A less dominant Patriots game script could preserve more late-game passing/rushing volume."),
("Jadarian Price caution","Price's college pass-blocking grade was 38.5. Joel flags pass protection as a potential obstacle to immediate passing-down work."),
("Kenneth Walker goal-line upside","Joel points to the possibility of stronger goal-line plus receiving usage in Walker's new environment, one of the reasons he ranks him aggressively."),
("Don't blindly follow rankings","Use rankings against ADP. If a player is ranked 62 but normally goes 85, the goal is to capture the value rather than drafting him at 62."),
]

CSS='''<style>
.guide-hero{background:linear-gradient(145deg,#162735,#0a1219);border:1px solid #294054;border-radius:18px;padding:16px;margin:4px 0 10px}.guide-kicker{font-size:9px;color:#d9ff38;font-weight:950;letter-spacing:1px;text-transform:uppercase}.guide-hero h2{font-size:25px;line-height:1.02;margin:5px 0;color:#fff}.guide-hero p{font-size:10px;color:#9cadb9;margin:0}.guide-card{background:#0e1821;border:1px solid #22313f;border-radius:13px;padding:11px;margin-bottom:7px}.guide-card b{font-size:12px;color:#fff}.guide-card p{font-size:10px;line-height:1.35;color:#a8b5bf;margin:4px 0 0}.rank-row{display:grid;grid-template-columns:31px 34px minmax(0,1fr);gap:7px;align-items:center;background:#0e1821;border:1px solid #22313f;border-radius:11px;padding:7px 9px;margin-bottom:4px}.rank-n{font-size:11px;font-weight:950;color:#8fa0ae}.rank-name{font-size:12px;font-weight:900;color:#fff}.pos-chip{border-radius:5px;text-align:center;padding:3px 2px;font-size:8px;font-weight:950;color:white}.pc-QB{background:#7257d8}.pc-RB{background:#19a89d}.pc-WR{background:#347fd9}.pc-TE{background:#e88135}.strategy-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin:7px 0 10px}.strategy-box{background:#111d27;border:1px solid #263745;border-radius:13px;padding:10px}.strategy-box span{font-size:8px;color:#8fa0ae;font-weight:900;text-transform:uppercase}.strategy-box b{display:block;font-size:12px;margin-top:2px}.adj-row{display:flex;justify-content:space-between;gap:8px;background:#0e1821;border-bottom:1px solid #22313f;padding:8px 9px;font-size:11px}.adj-row b{color:#d9ff38}.guide-note{font-size:9px;color:#8fa0ae;margin:6px 2px 10px}.rounds{font-size:10px;line-height:1.65;color:#c8d2d9;background:#0e1821;border:1px solid #22313f;border-radius:13px;padding:11px}
/* Draft Guide section navigation: same edge-to-edge card treatment as Draft Room. */
.st-key-guide_tab{display:block!important;width:100%!important;max-width:none!important;margin:2px 0 13px!important}
.st-key-guide_tab>div,.st-key-guide_tab [data-testid="stRadio"],.st-key-guide_tab [data-baseweb="radio-group"]{width:100%!important;max-width:none!important}
.st-key-guide_tab div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:6px!important;width:100%!important;max-width:none!important;align-items:stretch!important}
.st-key-guide_tab div[role="radiogroup"] label{box-sizing:border-box!important;position:relative!important;width:100%!important;min-width:0!important;max-width:none!important;min-height:76px!important;border-radius:14px!important;background:#0e1821!important;border:1px solid #2b3d4b!important;padding:10px 2px 9px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;margin:0!important;box-shadow:0 4px 14px rgba(0,0,0,.10)!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked){background:linear-gradient(145deg,#d51636,#9d0d27)!important;border-color:#ff3b59!important;box-shadow:0 6px 18px rgba(213,22,54,.22)!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked)::after{content:"";position:absolute;left:12px;right:12px;bottom:7px;height:2px;border-radius:2px;background:#fff}
.st-key-guide_tab div[role="radiogroup"] label>div:first-child{display:none!important}
.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%!important;text-align:center!important}
.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:9px!important;font-weight:950!important;line-height:1.08!important;color:#aab8c4!important;text-transform:uppercase!important;text-align:center!important;margin:0!important;white-space:normal!important}
.st-key-guide_tab div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p{color:#fff!important}
@media(max-width:430px){.st-key-guide_tab div[role="radiogroup"]{gap:5px!important}.st-key-guide_tab div[role="radiogroup"] label{min-height:72px!important}.st-key-guide_tab div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:8px!important}}
</style>'''

def _rows(items):
    return ''.join(f'<div class="rank-row"><div class="rank-n">{i}</div><div class="pos-chip pc-{p}">{p}</div><div class="rank-name">{html.escape(n)}</div></div>' for i,(p,n) in enumerate(items,1))

def render_draft_guide():
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown('<div class="guide-hero"><div class="guide-kicker">2026 Draft Intelligence</div><h2>The Shiva Draft Guide</h2><p>Joel Smyth research converted into fast, full-PPR draft decisions for a phone.</p></div>',unsafe_allow_html=True)
    tab=st.radio('Guide section',['Game Plan','PPR Board','Position','Research','Half PPR'],horizontal=True,label_visibility='collapsed',key='guide_tab')
    if tab=='Game Plan':
        st.markdown('<div class="strategy-grid"><div class="strategy-box"><span>Rounds 1–2</span><b>Attack elite RB</b></div><div class="strategy-box"><span>RB Goal</span><b>3 of top ~25–30</b></div><div class="strategy-box"><span>WR Windows</span><b>Rounds 3 + 5</b></div><div class="strategy-box"><span>QB Window</span><b>QB7–11 / Rd 8</b></div></div>',unsafe_allow_html=True)
        st.markdown('<div class="rounds"><b>Median 12-team PPR build</b><br>R1 RB · R2 RB · R3 WR · R4 BPA · R5 WR · R6 BPA · R7 BPA · R8 QB · R9 Upside WR · R10 Top Handcuff · R11 Punt TE · R12 Upside QB · R13 Deep Sleeper · R14 D/ST · R15 K/IR</div>',unsafe_allow_html=True)
        st.markdown('#### Draft Rules')
        rules=[('ADP is part of the price','Rankings tell you who you like; ADP tells you when you need to pay.'),('Do not draft for a tiny ADP win','Prioritize players whose ceiling can materially beat their draft slot.'),('Late-round process','Rookie WRs, rushing QBs, talent attached to elite offenses and clear RB2/handcuff roles.'),('Balance risk','Avoid stacking too many injury/availability bets on one roster.'),('Waivers start immediately','Post-draft and early-season waivers can be the highest-leverage adds of the year.')]
        for a,b in rules: st.markdown(f'<div class="guide-card"><b>{a}</b><p>{b}</p></div>',unsafe_allow_html=True)
    elif tab=='PPR Board':
        st.caption('Joel Smyth 2026 full-PPR Big Board · top 50')
        st.markdown(_rows(PPR_BIG_BOARD),unsafe_allow_html=True)
    elif tab=='Position':
        pos=st.radio('Position',['RB','WR','QB','TE'],horizontal=True,label_visibility='collapsed',key='guide_pos')
        st.markdown(_rows([(pos,n) for n in POSITIONAL[pos]]),unsafe_allow_html=True)
        st.markdown('#### 2025 Adjusted PPG')
        st.markdown('<div class="guide-note">Context-adjusted 2025 production from the guide — injuries, role changes, QB context and complete-game samples are considered.</div>',unsafe_allow_html=True)
        for n,v in ADJ[pos]: st.markdown(f'<div class="adj-row"><span>{html.escape(n)}</span><b>{v:.1f}</b></div>',unsafe_allow_html=True)
    elif tab=='Research':
        st.markdown('#### Draft-Changing Signals')
        for a,b in NUGGETS: st.markdown(f'<div class="guide-card"><b>{html.escape(a)}</b><p>{html.escape(b)}</p></div>',unsafe_allow_html=True)
        st.markdown('#### Research Lens')
        for a,b in [('QB volume','Projected opportunity versus ADP; Joel notes QB volume is substantially more predictable than QB play.'),('QB rushing','Designed runs and scrambles are sticky year-to-year and especially valuable near the goal line.'),('RB efficiency','Blend rushing efficiency, receiving efficiency and volume instead of relying on raw yards per carry.'),('WR efficiency','First downs per route and formation-adjusted yards per route are highlighted as forward-looking signals.'),('Offensive line','2025 run blocking, returning-starter cohesion, offseason movement and designed QB runs feed the 2026 run-block outlook.'),('Playcaller','Track fantasy PPG history, RB/WR scoring, RB1 share, screen rate, pace, motion, formations and run scheme.')]: st.markdown(f'<div class="guide-card"><b>{a}</b><p>{b}</p></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="guide-card"><b>Half-PPR reference</b><p>Kept intentionally secondary. Use this only when drafting a half-PPR league; the rest of Shiva defaults to full PPR.</p></div>',unsafe_allow_html=True)
        st.markdown(_rows(HALF_PPR_TOP),unsafe_allow_html=True)
        st.markdown('<div class="guide-note">Format signal: players earning a larger share of fantasy production through receptions gain relative value in full PPR; touchdown/rushing-heavy profiles tend to hold more value in half-PPR.</div>',unsafe_allow_html=True)