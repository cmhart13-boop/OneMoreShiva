import html
import re
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st


# Source: Joel Smyth's Draft Guide 2026 (uploaded project source).
# Source-derived guide content stays separate from the app's live/current data.
PPR_BIG_BOARD = [
    ("RB","Jahmyr Gibbs"),("RB","Bijan Robinson"),("WR","Ja'Marr Chase"),
    ("WR","Puka Nacua"),("RB","Christian McCaffrey"),("WR","Amon-Ra St. Brown"),
    ("WR","Jaxon Smith-Njigba"),("RB","Jonathan Taylor"),("RB","James Cook III"),
    ("WR","CeeDee Lamb"),("RB","Omarion Hampton"),("RB","Ashton Jeanty"),
    ("WR","Justin Jefferson"),("RB","Chase Brown"),("RB","Kenneth Walker III"),
    ("RB","Saquon Barkley"),("WR","Drake London"),("RB","De'Von Achane"),
    ("TE","Brock Bowers"),("WR","A.J. Brown"),("WR","George Pickens"),
    ("WR","Rashee Rice"),("WR","Nico Collins"),("RB","Derrick Henry"),
    ("TE","Trey McBride"),("RB","Jeremiyah Love"),("WR","DeVonta Smith"),
    ("WR","Malik Nabers"),("QB","Josh Allen"),("WR","Chris Olave"),
    ("RB","Josh Jacobs"),("WR","Tee Higgins"),("RB","Breece Hall"),
    ("WR","Jaylen Waddle"),("WR","Zay Flowers"),("RB","Kyren Williams"),
    ("WR","Tetairoa McMillan"),("WR","Emeka Egbuka"),("WR","Luther Burden III"),
    ("TE","Colston Loveland"),("RB","Javonte Williams"),("WR","Garrett Wilson"),
    ("WR","Ladd McConkey"),("WR","DJ Moore"),("RB","Cam Skattebo"),
    ("RB","Bucky Irving"),("RB","Travis Etienne Jr."),("TE","Tyler Warren"),
    ("WR","Terry McLaurin"),("QB","Lamar Jackson"),
]

POSITIONAL = {
    "QB":["Josh Allen","Lamar Jackson","Drake Maye","Jayden Daniels","Joe Burrow","Jalen Hurts",
          "Caleb Williams","Justin Herbert","Trevor Lawrence","Jaxson Dart","Brock Purdy","Dak Prescott"],
    "RB":["Jahmyr Gibbs","Bijan Robinson","Christian McCaffrey","Jonathan Taylor","James Cook III",
          "Omarion Hampton","Ashton Jeanty","Chase Brown","Kenneth Walker III","Saquon Barkley",
          "De'Von Achane","Derrick Henry","Jeremiyah Love","Josh Jacobs","Breece Hall"],
    "WR":["Ja'Marr Chase","Puka Nacua","Amon-Ra St. Brown","Jaxon Smith-Njigba","CeeDee Lamb",
          "Justin Jefferson","Drake London","A.J. Brown","George Pickens","Rashee Rice","Nico Collins",
          "DeVonta Smith","Malik Nabers","Chris Olave","Tee Higgins"],
    "TE":["Brock Bowers","Trey McBride","Colston Loveland","Tyler Warren","Sam LaPorta",
          "Harold Fannin Jr.","Tucker Kraft","Kyle Pitts Sr.","George Kittle","Dalton Kincaid"],
}

ARTICLES = [
    ("draft-capital-matters","Draft capital matters",
     "Since 2015, the first 11 RBs selected top-25 in the NFL Draft all produced an RB1 fantasy season by Year 2. That puts major sophomore upside behind Ashton Jeanty and Omarion Hampton.",
     ["Ashton Jeanty","Omarion Hampton"]),
    ("rb-ceiling-zone","Rounds 1–2 are the RB ceiling zone",
     "Smyth's research says only 2 of 33 early-round RBs who reached 20+ PPR PPG came from Rounds 3–4. His preferred build starts RB/RB and aims for three RBs inside roughly the top 25–30.",
     []),
    ("chase-brown-environment","Chase Brown environment",
     "Cincinnati QBs were the NFL's top three in checkdown rate in 2025, and Zac Taylor has produced an RB1 in six straight seasons when Chase Brown's 2024 starts are counted.",
     ["Chase Brown"]),
    ("josh-allen-outlier","Josh Allen is the outlier",
     "Allen has finished top-two at QB in fantasy points six straight seasons. Smyth also notes rushing QBs drafted in Rounds 2–5 have historically hit far more often than passing-only QBs.",
     ["Josh Allen"]),
    ("puka-targets","Puka earns targets at a different level",
     "Since 2024, Puka Nacua's targets per route sit at 36.8%; Smyth notes no other qualified player is above 30%.",
     ["Puka Nacua"]),
    ("kincaid-routes","Dalton Kincaid: routes, not efficiency",
     "Kincaid led 2025 TEs across a large collection of per-route efficiency measures. The unlock is simply getting him on more routes.",
     ["Dalton Kincaid"]),
    ("parker-washington","Parker Washington late value",
     "Over Jacksonville's final four games, Washington produced 454 receiving yards despite Brian Thomas Jr. and Jakobi Meyers each running more routes.",
     ["Parker Washington"]),
    ("luther-burden","Luther Burden efficiency signal",
     "Burden ranked eighth among WRs in fantasy points per snap as a rookie; six of the seven players ahead of him were fantasy WR1s.",
     ["Luther Burden III"]),
    ("ceedee-luck","CeeDee regression candidate — upward",
     "Smyth's 25-factor luck model rated CeeDee Lamb the unluckiest player of 2025, estimating roughly 2.7 PPG lost to bad-luck events.",
     ["CeeDee Lamb"]),
    ("achane-split","Achane's receiving split matters",
     "De'Von Achane has averaged 11.4 receiving PPG with Tua Tagovailoa in his career versus 3.4 in eight games without him.",
     ["De'Von Achane"]),
    ("jaylen-warren","Jaylen Warren receiving opportunity",
     "Warren ranked top-two among RBs in targets per route, yards per route and missed tackles per reception in 2025; Pittsburgh also has 82 vacated RB targets.",
     ["Jaylen Warren"]),
    ("drake-maye","Drake Maye game-script ceiling",
     "Maye was QB1 over quarters 1–3 last season but QB32 in fourth quarters. A less dominant Patriots game script could preserve more late-game passing/rushing volume.",
     ["Drake Maye"]),
    ("jadarian-price","Jadarian Price caution",
     "Price's college pass-blocking grade was 38.5. Smyth flags pass protection as a potential obstacle to immediate passing-down work.",
     ["Jadarian Price"]),
    ("kenneth-walker","Kenneth Walker goal-line upside",
     "Smyth points to the possibility of stronger goal-line plus receiving usage in Walker's new environment, one of the reasons he ranks him aggressively.",
     ["Kenneth Walker III"]),
    ("rankings-vs-adp","Don't blindly follow rankings",
     "Use rankings against ADP. If a player is ranked 62 but normally goes 85, the goal is to capture the value rather than drafting him at 62.",
     []),
]

GUIDE_SECTIONS = [
    ("Rankings","rankings","2026 big board + positional rankings"),
    ("Draft Strategy","strategy","Round-by-round build and position rules"),
    ("Research","research","Research notes and clickable stat features"),
    ("Luck Metric","luck","How Smyth frames 2025 luck"),
    ("Player Cards","player-cards","Featured-player shortcuts into app profiles"),
]

CSS = r'''
<style>
.guide-hero{border-radius:18px;padding:21px 17px;background:linear-gradient(145deg,#17212a,#0d141a);border:1px solid rgba(213,177,92,.25);margin:4px 0 13px}
.guide-kicker{font-size:11px;color:#dfc57f;font-weight:950;letter-spacing:1px;text-transform:uppercase}
.guide-hero h2{font-size:29px;line-height:1.04;margin:6px 0 8px;color:#fff}
.guide-hero p{font-size:14px;line-height:1.45;color:#9cadb9;margin:0}
.guide-toc{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:10px 0 15px}
.guide-toc a,.article-card,.player-card-link{display:block;text-decoration:none!important}
.guide-section-card{height:100%;background:#101820;border:1px solid #2b3741;border-radius:14px;padding:13px}
.guide-section-card b{display:block;color:#fff;font-size:15px}.guide-section-card span{display:block;color:#8798a5;font-size:11px;line-height:1.3;margin-top:4px}
.guide-section-card em{display:block;color:#dfc57f;font-style:normal;font-weight:900;font-size:11px;margin-top:9px}
.guide-back{display:inline-block!important;color:#dfc57f!important;text-decoration:none!important;font-weight:900;font-size:12px;margin:1px 0 12px}
.guide-subhead{font-size:20px;font-weight:950;color:#fff;margin:7px 0 8px}
.rank-row{display:grid;grid-template-columns:31px 34px minmax(0,1fr);gap:7px;align-items:center;background:#0e1821;border:1px solid #22313f;border-radius:11px;padding:9px 10px;margin-bottom:5px;min-height:56px}
.rank-n{font-size:13px;font-weight:950;color:#8fa0ae}.rank-name{font-size:15px;font-weight:900;color:#fff}
.pos-chip{border-radius:5px;text-align:center;padding:3px 2px;font-size:8px;font-weight:950;color:white}.pc-QB{background:#7257d8}.pc-RB{background:#19a89d}.pc-WR{background:#347fd9}.pc-TE{background:#e88135}
.guide-player-link{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;color:#fff!important;text-decoration:none!important}
.guide-player-link span{font-size:10px;color:#d8b35b;font-weight:900;white-space:nowrap}
.st-key-guide_rank_filters [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important;gap:7px!important;margin:5px 0 9px}
.st-key-guide_rank_filters [data-testid="stColumn"]{flex:1 1 0!important;min-width:0!important;width:20%!important}
.st-key-guide_rank_filters .stButton>button{min-height:38px!important;padding:5px 7px!important;border-radius:11px!important;font-size:12px!important;font-weight:950!important;letter-spacing:.2px!important;-webkit-tap-highlight-color:transparent!important;transition:none!important;white-space:nowrap!important}
.st-key-guide_rank_filters .stButton>button[kind="primary"]{border-color:rgba(240,216,143,.72)!important;background:linear-gradient(145deg,rgba(213,177,92,.24),rgba(213,177,92,.10))!important;color:#fff!important;box-shadow:0 0 0 1px rgba(213,177,92,.12),0 0 18px rgba(213,177,92,.12)!important}
.st-key-guide_rank_filters .stButton>button[kind="secondary"]{background:#0d161d!important;border-color:#30404b!important;color:#9eabb3!important}
.strategy-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin:7px 0 12px}
.strategy-box{background:#111d27;border:1px solid #263745;border-radius:14px;padding:13px}.strategy-box span{font-size:10px;color:#8fa0ae;font-weight:900;text-transform:uppercase}.strategy-box b{display:block;font-size:15px;margin-top:3px;color:#fff}
.rounds{font-size:13px;line-height:1.6;color:#c8d2d9;background:#0e1821;border:1px solid #22313f;border-radius:14px;padding:14px;margin-bottom:10px}
.article-grid{display:grid;grid-template-columns:1fr;gap:8px}.article-card{background:#0e1821;border:1px solid #263745;border-radius:13px;padding:13px}.article-card b{display:block;color:#fff;font-size:15px}.article-card p{font-size:12px;line-height:1.4;color:#9eacb6;margin:5px 0 0}.article-card span{display:block;color:#dfc57f;font-size:10px;font-weight:900;margin-top:8px}
.article-body{background:#0e1821;border:1px solid #263745;border-radius:15px;padding:16px}.article-body h3{font-size:23px;margin:0 0 9px;color:#fff}.article-body p{font-size:15px;line-height:1.55;color:#c5d0d7;margin:0}
.player-feature-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.player-feature{background:#0e1821;border:1px solid #263745;border-radius:13px;padding:12px}.player-feature b{color:#fff;font-size:14px}.player-feature span{display:block;color:#dfc57f;font-size:10px;font-weight:900;margin-top:7px}
@media(max-width:560px){.guide-toc,.strategy-grid,.player-feature-grid{grid-template-columns:1fr 1fr}.guide-hero h2{font-size:27px}.st-key-guide_rank_filters [data-testid="stHorizontalBlock"]{gap:5px!important}.st-key-guide_rank_filters .stButton>button{min-height:36px!important;font-size:10.5px!important;padding:4px 2px!important}}
</style>
'''


def _guide_href(section=None, article=None):
    bits = ["page=Guide"]
    if section:
        bits.append("guide_view=" + quote_plus(section))
    if article:
        bits.append("guide_article=" + quote_plus(article))
    return "?" + "&".join(bits)


def _player_href(name, players, profile_href):
    if players is None or not isinstance(players, pd.DataFrame) or players.empty or profile_href is None:
        return None
    if "name" not in players.columns:
        return None
    m = players.loc[players["name"].astype(str).str.casefold().eq(str(name).casefold())]
    if m.empty:
        return None
    return profile_href(m.iloc[0], "Guide")


def _rank_rows(items, players=None, profile_href=None):
    out = []
    for i, (pos, name) in enumerate(items, 1):
        safe = html.escape(name)
        href = _player_href(name, players, profile_href)
        if href:
            safe = f'<a class="guide-player-link" href="{href}" target="_self">{safe}<span>Player profile →</span></a>'
        out.append(
            f'<div class="rank-row"><div class="rank-n">{i}</div><div class="pos-chip pc-{pos}">{pos}</div><div class="rank-name">{safe}</div></div>'
        )
    return "".join(out)


def _render_home():
    cards = []
    for title, slug, desc in GUIDE_SECTIONS:
        cards.append(
            f'<a href="{_guide_href(slug)}" target="_self"><div class="guide-section-card">'
            f'<b>{html.escape(title)}</b><span>{html.escape(desc)}</span><em>Open section →</em></div></a>'
        )
    st.markdown('<div class="guide-toc">' + "".join(cards) + '</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rounds"><b>Built like a site, not a PDF.</b><br>'
        'Tap a section to open it. Rankings link into player profiles when that player exists in the app. '
        'Research headlines open dedicated article views, and player features jump directly to their player page.</div>',
        unsafe_allow_html=True,
    )


def _set_rank_view(mode):
    st.session_state["joel_rank_view"] = mode


def _render_rankings(players, profile_href):
    st.markdown(f'<a class="guide-back" href="{_guide_href()}" target="_self">← Guide contents</a>', unsafe_allow_html=True)
    st.markdown('<div class="guide-subhead">2026 Rankings</div>', unsafe_allow_html=True)
    rank_views = ("PPR Big Board", "QB", "RB", "WR", "TE")
    if st.session_state.get("joel_rank_view") not in rank_views:
        st.session_state["joel_rank_view"] = "PPR Big Board"
    mode = st.session_state["joel_rank_view"]
    with st.container(key="guide_rank_filters"):
        cols = st.columns(len(rank_views), gap="small")
        for col, option in zip(cols, rank_views):
            with col:
                st.button(
                    option,
                    key=f"joel_rank_btn_{option.replace(' ', '_')}",
                    type="primary" if mode == option else "secondary",
                    use_container_width=True,
                    on_click=_set_rank_view,
                    args=(option,),
                )
    mode = st.session_state["joel_rank_view"]
    if mode == "PPR Big Board":
        st.caption("Joel Smyth 2026 PPR Big Board · first 50 shown here as interactive rows.")
        st.markdown(_rank_rows(PPR_BIG_BOARD, players, profile_href), unsafe_allow_html=True)
    else:
        st.caption(f"Joel Smyth 2026 {mode} positional rankings · leading tier.")
        st.markdown(_rank_rows([(mode, n) for n in POSITIONAL[mode]], players, profile_href), unsafe_allow_html=True)


def _render_strategy():
    st.markdown(f'<a class="guide-back" href="{_guide_href()}" target="_self">← Guide contents</a>', unsafe_allow_html=True)
    st.markdown('<div class="guide-subhead">My Draft Strategy</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="strategy-grid">'
        '<div class="strategy-box"><span>QB</span><b>Target the QB7–11 ADP zone; late rushing QB as Plan B</b></div>'
        '<div class="strategy-box"><span>RB</span><b>Try to land 3 RBs from roughly the top 25–30</b></div>'
        '<div class="strategy-box"><span>WR</span><b>Attack Rounds 3 and 5; chase late WR upside</b></div>'
        '<div class="strategy-box"><span>TE</span><b>Best-player-available; punt strategically if value never appears</b></div>'
        '</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="rounds"><b>12-team PPR · median desired build</b><br>'
        'R1 RB · R2 RB · R3 WR · R4 BPA · R5 WR · R6 BPA · R7 BPA · R8 QB · '
        'R9 Upside WR · R10 Top Handcuff · R11 Punt TE · R12 Upside QB · '
        'R13 Favorite Deep Sleeper · R14 D/ST · R15 Kicker/IR player</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="rounds"><b>Overall rules</b><br>'
        '1. Do not draft off rankings without understanding ADP.<br>'
        '2. “Don’t Beat ADP” — chase true-value upside rather than a one-slot win.<br>'
        '3. No K or D/ST until the last two rounds unless you want to intimidate everyone.<br>'
        '4. Favor good “process players” late: rookie WRs, rushing QBs, talent on elite offenses, and cemented RB2/handcuffs.<br>'
        '5. Balance risk across the roster.<br>'
        '6. Early waivers and even post-draft waivers matter more than they will later in the season.</div>',
        unsafe_allow_html=True,
    )


def _render_research(players, profile_href):
    st.markdown(f'<a class="guide-back" href="{_guide_href()}" target="_self">← Guide contents</a>', unsafe_allow_html=True)
    st.markdown('<div class="guide-subhead">Research & Top Stats</div>', unsafe_allow_html=True)
    cards = []
    for slug, title, body, names in ARTICLES:
        preview = html.escape(body[:150]) + ("…" if len(body) > 150 else "")
        cards.append(
            f'<a class="article-card" href="{_guide_href("research", slug)}" target="_self">'
            f'<b>{html.escape(title)}</b><p>{preview}</p><span>Read feature →</span></a>'
        )
    st.markdown('<div class="article-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)


def _render_article(slug, players, profile_href):
    article = next((x for x in ARTICLES if x[0] == slug), None)
    if not article:
        _render_research(players, profile_href)
        return
    _, title, body, names = article
    st.markdown(f'<a class="guide-back" href="{_guide_href("research")}" target="_self">← Research</a>', unsafe_allow_html=True)
    st.markdown(f'<div class="article-body"><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>', unsafe_allow_html=True)
    if names:
        st.markdown('<div class="guide-subhead" style="font-size:16px">Related players</div>', unsafe_allow_html=True)
        for name in names:
            href = _player_href(name, players, profile_href)
            if href:
                st.markdown(
                    f'<a class="player-card-link" href="{href}" target="_self"><div class="player-feature"><b>{html.escape(name)}</b><span>Open player profile →</span></div></a>',
                    unsafe_allow_html=True,
                )


def _render_luck():
    st.markdown(f'<a class="guide-back" href="{_guide_href()}" target="_self">← Guide contents</a>', unsafe_allow_html=True)
    st.markdown('<div class="guide-subhead">2025 Fantasy Luck Metric</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rounds">Smyth describes a 25-factor luck model using situations such as overtime points, '
        'points lost to penalty, tackles at the 1, QB dropped TDs, Week 18 spikes, in-game quarters missed to injury, '
        'DPIs, trick plays and busted coverage. The guide then separates the 25 unluckiest and 25 luckiest players from 2025.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<a class="article-card" href="{_guide_href("research", "ceedee-luck")}" target="_self">'
        '<b>CeeDee Lamb: upward regression candidate</b><p>Open the guide feature tied to the luck model.</p><span>Open feature →</span></a>',
        unsafe_allow_html=True,
    )


def _render_player_cards(players, profile_href):
    st.markdown(f'<a class="guide-back" href="{_guide_href()}" target="_self">← Guide contents</a>', unsafe_allow_html=True)
    st.markdown('<div class="guide-subhead">Top Player Cards Preview</div>', unsafe_allow_html=True)
    featured = [
        "Ashton Jeanty","Omarion Hampton","Chase Brown","Josh Allen","Puka Nacua",
        "Dalton Kincaid","Parker Washington","Luther Burden III","CeeDee Lamb",
        "De'Von Achane","Jaylen Warren","Drake Maye","Kenneth Walker III"
    ]
    cards = []
    for name in featured:
        href = _player_href(name, players, profile_href)
        if href:
            cards.append(
                f'<a class="player-card-link" href="{href}" target="_self"><div class="player-feature">'
                f'<b>{html.escape(name)}</b><span>Open player profile →</span></div></a>'
            )
        else:
            cards.append(f'<div class="player-feature"><b>{html.escape(name)}</b><span>Profile unavailable in current app data</span></div>')
    st.markdown('<div class="player-feature-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)


def render_draft_guide(players=None, profile_href=None, load_weekly=None, weekly_name_col=None, espn_ppr=None):
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="guide-hero"><div class="guide-kicker">2026 Draft Intelligence</div>'
        '<h2>Joel Smyth’s Draft Guide</h2>'
        '<p>Interactive edition: open sections, read research as real content pages, and jump from rankings or player features directly into Shiva player profiles.</p></div>',
        unsafe_allow_html=True,
    )

    article = st.query_params.get("guide_article")
    if article:
        _render_article(str(article), players, profile_href)
        return

    section = str(st.query_params.get("guide_view") or "").strip()
    if section == "rankings":
        _render_rankings(players, profile_href)
    elif section == "strategy":
        _render_strategy()
    elif section == "research":
        _render_research(players, profile_href)
    elif section == "luck":
        _render_luck()
    elif section == "player-cards":
        _render_player_cards(players, profile_href)
    else:
        _render_home()
