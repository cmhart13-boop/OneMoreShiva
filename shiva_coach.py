from __future__ import annotations

import html
from datetime import date
import numpy as np
import pandas as pd
import streamlit as st

KICKOFF = date(2026, 9, 9)


def _pts_for_player(load_weekly, weekly_for_player, espn_ppr, name: str) -> pd.DataFrame:
    try:
        weekly = load_weekly()
        pf = weekly_for_player(weekly, name)
        if pf.empty:
            return pd.DataFrame()
        pf = pf.copy()
        pf["_ppr"] = espn_ppr(pf)
        pf = pf.loc[pd.to_numeric(pf.get("week"), errors="coerce").between(1, 18, inclusive="both")]
        return pf.loc[pf["_ppr"].notna()].copy()
    except Exception:
        return pd.DataFrame()


def player_evidence(players, load_weekly, weekly_for_player, espn_ppr, name: str) -> dict:
    row = players.loc[players["name"].astype(str).eq(str(name))]
    current = row.iloc[0] if not row.empty else pd.Series(dtype=object)
    pf = _pts_for_player(load_weekly, weekly_for_player, espn_ppr, name)
    if pf.empty:
        return {
            "name": name, "pos": str(current.get("pos", "")), "team": str(current.get("team", "")),
            "rank": current.get("overall_rank", current.get("rank", np.nan)),
            "adp": current.get("draft_adp", current.get("adp", np.nan)),
            "games": 0, "ppg": np.nan, "floor": np.nan, "ceiling": np.nan,
            "rate15": np.nan, "boom25": np.nan, "bust10": np.nan, "recent": np.nan,
        }
    pts = pd.to_numeric(pf["_ppr"], errors="coerce").dropna()
    seasons = pd.to_numeric(pf.get("season"), errors="coerce")
    latest = int(seasons.dropna().max()) if seasons.notna().any() else None
    latest_pts = pd.to_numeric(pf.loc[seasons.eq(latest), "_ppr"], errors="coerce").dropna() if latest else pts
    return {
        "name": name,
        "pos": str(current.get("pos", "")), "team": str(current.get("team", "")),
        "rank": current.get("overall_rank", current.get("rank", np.nan)),
        "adp": current.get("draft_adp", current.get("adp", np.nan)),
        "games": int(len(pts)),
        "ppg": float(latest_pts.mean()) if len(latest_pts) else float(pts.mean()),
        "floor": float(latest_pts.quantile(.25)) if len(latest_pts) else float(pts.quantile(.25)),
        "ceiling": float(latest_pts.quantile(.90)) if len(latest_pts) else float(pts.quantile(.90)),
        "rate15": float((latest_pts >= 15).mean() * 100) if len(latest_pts) else np.nan,
        "boom25": float((latest_pts >= 25).mean() * 100) if len(latest_pts) else np.nan,
        "bust10": float((latest_pts < 10).mean() * 100) if len(latest_pts) else np.nan,
        "recent": float(latest_pts.tail(4).mean()) if len(latest_pts) else np.nan,
        "season": latest,
    }


def _n(v, digits=1, suffix=""):
    try:
        if pd.isna(v): return "—"
        return f"{float(v):.{digits}f}{suffix}"
    except Exception:
        return "—"


def _rank(v):
    try:
        if pd.isna(v): return "—"
        return str(int(float(v)))
    except Exception:
        return "—"


def compare_call(a: dict, b: dict) -> tuple[str, list[str]]:
    # Transparent evidence weighting; no fake probability/confidence score.
    def score(x):
        rank_component = 0 if pd.isna(x.get("rank")) else max(0, 220 - float(x["rank"])) / 22
        values = [
            (x.get("floor"), 1.35),
            (x.get("ppg"), 1.0),
            (x.get("ceiling"), .35),
            (None if pd.isna(x.get("rate15")) else float(x["rate15"]) / 10, .9),
            (None if pd.isna(x.get("bust10")) else -float(x["bust10"]) / 12, 1.0),
            (rank_component, .8),
        ]
        return sum(float(v) * w for v, w in values if v is not None and not pd.isna(v))
    sa, sb = score(a), score(b)
    winner, loser = (a, b) if sa >= sb else (b, a)
    reasons=[]
    if not pd.isna(winner.get("floor")) and not pd.isna(loser.get("floor")) and winner["floor"] > loser["floor"]:
        reasons.append(f"higher weekly floor ({winner['floor']:.1f} vs {loser['floor']:.1f})")
    if not pd.isna(winner.get("rate15")) and not pd.isna(loser.get("rate15")) and winner["rate15"] > loser["rate15"]:
        reasons.append(f"more 15+ point weeks ({winner['rate15']:.0f}% vs {loser['rate15']:.0f}%)")
    if not pd.isna(winner.get("ceiling")) and not pd.isna(loser.get("ceiling")) and winner["ceiling"] > loser["ceiling"]:
        reasons.append(f"better 90th-percentile ceiling ({winner['ceiling']:.1f} vs {loser['ceiling']:.1f})")
    if not pd.isna(winner.get("bust10")) and not pd.isna(loser.get("bust10")) and winner["bust10"] < loser["bust10"]:
        reasons.append(f"fewer sub-10 bust weeks ({winner['bust10']:.0f}% vs {loser['bust10']:.0f}%)")
    return winner["name"], reasons[:3]


def render_compare(players, load_weekly, weekly_for_player, espn_ppr, title="Who should I take?"):
    st.markdown(f"<div class='coach-section-title'>{html.escape(title)}</div>", unsafe_allow_html=True)
    names = players["name"].dropna().astype(str).drop_duplicates().tolist()
    if len(names) < 2:
        st.info("Player data is not available for comparison right now.")
        return
    c1,c2=st.columns(2)
    with c1: a_name=st.selectbox("Player A", names, index=0, key=f"cmp_a_{title}")
    with c2: b_name=st.selectbox("Player B", names, index=min(1,len(names)-1), key=f"cmp_b_{title}")
    if a_name == b_name:
        st.info("Choose two different players.")
        return
    a=player_evidence(players, load_weekly, weekly_for_player, espn_ppr, a_name)
    b=player_evidence(players, load_weekly, weekly_for_player, espn_ppr, b_name)
    winner,reasons=compare_call(a,b)
    cards=[]
    for x in (a,b):
        cards.append(f"""<div class='coach-player-card {'winner' if x['name']==winner else ''}'>
        <div class='coach-player-top'><div><b>{html.escape(x['name'])}</b><span>{html.escape(x['pos'])} · {html.escape(x['team'])}</span></div><div class='coach-rank'>#{_rank(x['rank'])}</div></div>
        <div class='coach-metrics'><div><strong>{_n(x['floor'])}</strong><span>Floor</span></div><div><strong>{_n(x['ppg'])}</strong><span>PPG</span></div><div><strong>{_n(x['ceiling'])}</strong><span>Ceiling</span></div><div><strong>{_n(x['rate15'],0,'%')}</strong><span>15+ Weeks</span></div></div></div>""")
    st.markdown("<div class='coach-compare-grid'>"+"".join(cards)+"</div>",unsafe_allow_html=True)
    reason_text = "; ".join(reasons) if reasons else "the strongest overall combination of floor, ceiling, consistency and current ranking context"
    st.markdown(f"<div class='shiva-says-call'><span>SHIVA SAYS</span><b>{html.escape(winner)}</b><p>{html.escape(reason_text)}.</p></div>",unsafe_allow_html=True)


def render_shiva_moments():
    st.markdown("<div class='coach-section-title'>Shiva Moments</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='moment-list'>
      <div class='moment'><span>LINEUP EDGE</span><b>Never burn FLEX on Thursday</b><p>If a Thursday player is in FLEX, move him to his positional slot. You preserve more replacement options for Sunday if someone gets hurt.</p></div>
      <div class='moment'><span>DRAFT EDGE</span><b>Draft the room, not just the board</b><p>If the managers picking twice before you already filled QB, you can often let your QB target come back and use the current pick on a scarcer position.</p></div>
      <div class='moment'><span>ROSTER EDGE</span><b>Raise the floor without killing the ceiling</b><p>Build around repeatable 15+ point producers, then use selected roster spots on players with legitimate week-winning upside.</p></div>
    </div>""", unsafe_allow_html=True)


def render_draft_moment(draft_log, next_pick: int, team_count: int, user_slot: int):
    if not draft_log: return
    # Look at the managers who pick before the user's next turn. If all already roster a QB,
    # surface the exact room-reading behavior the product is meant to coach.
    cur = int(next_pick)
    round_no = (cur-1)//team_count + 1
    user_next = None
    for p in range(cur+1, cur + team_count*2 + 1):
        r=(p-1)//team_count+1; w=(p-1)%team_count+1; team=w if r%2 else team_count-w+1
        if team == user_slot:
            user_next=p; break
    if not user_next: return
    teams_between=[]
    for p in range(cur+1,user_next):
        r=(p-1)//team_count+1; w=(p-1)%team_count+1; team=w if r%2 else team_count-w+1
        if team not in teams_between: teams_between.append(team)
    if not teams_between: return
    qb_by_team={t:any(str(x.get('pos','')).upper()=='QB' for x in draft_log if int(x.get('team',-1))==t) for t in teams_between}
    if teams_between and all(qb_by_team.values()):
        st.markdown(f"<div class='draft-moment'><span>SHIVA MOMENT</span><b>The managers between your picks already have quarterbacks.</b><p>If your QB target isn't an obvious tier-break, consider taking the scarcer RB/WR/TE now and letting the quarterback come back to you at pick {user_next}.</p></div>",unsafe_allow_html=True)


def render_season_hub(players, load_weekly, weekly_for_player, espn_ppr):
    preseason = date.today() < KICKOFF
    phase = "PRESEASON MODE" if preseason else "IN-SEASON MODE"
    st.markdown(f"<div class='coach-phase'>{phase}</div>",unsafe_allow_html=True)
    st.markdown("<div class='coach-hero'><span>SHIVA SAYS</span><h2>Make the decision. See the why.</h2><p>Floor, ceiling and consistency first. Extra detail only when you want it.</p></div>",unsafe_allow_html=True)
    render_compare(players, load_weekly, weekly_for_player, espn_ppr, "Compare players")
    render_shiva_moments()
    if preseason:
        st.info("Weekly opponent, injury and lineup alerts will activate when current-season weekly data is available. Nothing here invents 2026 game-week information before it exists.")


CSS = r'''<style>
.coach-phase{font-size:10px;font-weight:950;letter-spacing:.85px;color:#d8b35b;margin:4px 1px 7px}.coach-hero{background:linear-gradient(145deg,#171f27,#0d1318);border:1px solid rgba(216,179,91,.24);border-radius:16px;padding:17px;margin-bottom:14px}.coach-hero>span,.shiva-says-call>span,.draft-moment>span,.moment>span{font-size:9px;font-weight:950;letter-spacing:.85px;color:#d8b35b}.coach-hero h2{font-size:25px;line-height:1.03;margin:4px 0 6px;color:#fff}.coach-hero p{font-size:13px;line-height:1.4;color:#aab5bd;margin:0}.coach-section-title{font-size:20px;font-weight:950;letter-spacing:-.45px;color:#f6f8f9;margin:14px 0 8px}.coach-compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.coach-player-card{background:#101820;border:1px solid rgba(200,211,219,.14);border-radius:14px;padding:13px}.coach-player-card.winner{border-color:rgba(216,179,91,.55);box-shadow:inset 0 0 0 1px rgba(216,179,91,.08)}.coach-player-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.coach-player-top b{font-size:15px;color:#fff}.coach-player-top span{display:block;font-size:10px;color:#91a0ab;margin-top:2px}.coach-rank{font-size:12px;font-weight:900;color:#d8b35b}.coach-metrics{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px}.coach-metrics div{background:#0b1116;border-radius:9px;padding:8px}.coach-metrics strong{display:block;font-size:19px;line-height:1;color:#f7f8f9}.coach-metrics span{font-size:9px;color:#8f9ca6;text-transform:uppercase;font-weight:850}.shiva-says-call,.draft-moment{background:linear-gradient(145deg,#211f17,#12110d);border:1px solid rgba(216,179,91,.34);border-radius:14px;padding:13px;margin:9px 0 13px}.shiva-says-call b,.draft-moment b{display:block;font-size:18px;color:#fff;margin:3px 0}.shiva-says-call p,.draft-moment p{font-size:12px;line-height:1.42;color:#b3bac0;margin:0}.moment-list{display:grid;gap:8px}.moment{background:#101820;border:1px solid rgba(200,211,219,.13);border-radius:14px;padding:13px}.moment b{display:block;font-size:15px;color:#fff;margin:3px 0}.moment p{font-size:12px;line-height:1.42;color:#9eabb5;margin:0}@media(max-width:430px){.coach-compare-grid{grid-template-columns:1fr}.coach-player-card{padding:12px}.coach-metrics{grid-template-columns:repeat(4,1fr)}.coach-metrics div{padding:7px 5px}.coach-metrics strong{font-size:16px}.coach-metrics span{font-size:8px}.coach-hero h2{font-size:23px}}
</style>'''


def inject_css():
    st.markdown(CSS,unsafe_allow_html=True)
