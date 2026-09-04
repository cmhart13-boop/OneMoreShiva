from __future__ import annotations

import html
import io
import json
from datetime import date, datetime
from urllib.request import Request, urlopen

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


def _key(v: str) -> str:
    return "".join(ch for ch in str(v).casefold() if ch.isalnum())


def compare_call(a: dict, b: dict) -> tuple[str, list[str]]:
    def score(x):
        rank_component = 0 if pd.isna(x.get("rank")) else max(0, 220 - float(x["rank"])) / 22
        values = [
            (x.get("floor"), 1.35), (x.get("ppg"), 1.0), (x.get("ceiling"), .35),
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


def render_compare(players, load_weekly, weekly_for_player, espn_ppr, title="Who should I start?"):
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
    st.caption("This lean uses the historical weekly database plus current ranking context. It does not invent a weekly projection or fake confidence percentage.")


@st.cache_data(ttl=900, show_spinner=False)
def _espn_news():
    req=Request("https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100",headers={"User-Agent":"Mozilla/5.0 (iPhone; One More Shiva)"})
    with urlopen(req,timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def render_player_watch(players):
    st.markdown("<div class='coach-section-title'>Player Watch</div>",unsafe_allow_html=True)
    st.caption("Live ESPN fantasy/NFL mentions. Useful for injury and role context; it is not a fabricated injury database.")
    names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    player=st.selectbox("Watch player",names,key="watch_player")
    terms={str(player).casefold(),str(player).split()[-1].casefold()}
    try:
        data=_espn_news()
        hits=[]
        for a in data.get("articles",[]):
            headline=str(a.get("headline") or "")
            desc=str(a.get("description") or "")
            text=(headline+" "+desc).casefold()
            if not any(t and t in text for t in terms): continue
            links=a.get("links",{}) or {}
            web=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            published=str(a.get("published") or a.get("lastModified") or "")
            hits.append((headline,desc,web,published))
        if not hits:
            st.info("No recent ESPN article in the current feed mentions this player.")
            return
        for headline,desc,web,published in hits[:8]:
            meta="ESPN"
            if published:
                try: meta += " · "+datetime.fromisoformat(published.replace("Z","+00:00")).strftime("%b %-d")
                except Exception: pass
            link=f'<a href="{html.escape(web,quote=True)}" target="_blank" rel="noopener">Open story →</a>' if web else ''
            st.markdown(f"<div class='watch-card'><span>{html.escape(meta)}</span><b>{html.escape(headline)}</b><p>{html.escape(desc)}</p>{link}</div>",unsafe_allow_html=True)
    except Exception:
        st.info("ESPN Player Watch is temporarily unavailable.")


@st.cache_data(ttl=900, show_spinner=False)
def _espn_scoreboard():
    req=Request("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",headers={"User-Agent":"Mozilla/5.0 (One More Shiva)"})
    with urlopen(req,timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _team_game_day(team_abbr: str):
    try:
        data=_espn_scoreboard()
        for ev in data.get("events",[]):
            comps=(ev.get("competitions") or [{}])[0]
            teams=[]
            for c in comps.get("competitors",[]):
                t=c.get("team",{}) or {}
                teams.extend([str(t.get("abbreviation") or "").upper(),str(t.get("shortDisplayName") or "").upper()])
            if str(team_abbr).upper() in teams:
                dt=datetime.fromisoformat(str(ev.get("date")).replace("Z","+00:00"))
                return dt.strftime("%A"), dt
    except Exception:
        pass
    return None,None


def render_lineup_check(players):
    st.markdown("<div class='coach-section-title'>Lineup Check</div>",unsafe_allow_html=True)
    st.caption("This is the rule engine behind automatic lineup alerts. Until league sync supplies your lineup, choose the player currently sitting in FLEX.")
    pool=players.loc[players["pos"].astype(str).isin(["RB","WR","TE"])].copy()
    names=pool["name"].dropna().astype(str).drop_duplicates().tolist()
    flex=st.selectbox("Who is in your FLEX?",names,key="flex_player") if names else None
    if not flex:return
    row=pool.loc[pool["name"].eq(flex)].iloc[0]
    team=str(row.get("team", ""))
    day,_=_team_game_day(team)
    if day == "Thursday":
        st.markdown(f"<div class='lineup-alert danger'><span>SHIVA MOMENT</span><b>Move {html.escape(flex)} out of FLEX.</b><p>{html.escape(team)} plays Thursday. Put him in his {html.escape(str(row.get('pos','')))} slot and preserve FLEX for Sunday injury/availability changes.</p></div>",unsafe_allow_html=True)
    elif day:
        st.markdown(f"<div class='lineup-alert good'><span>LINEUP CHECK</span><b>No Thursday FLEX trap detected.</b><p>{html.escape(flex)} is currently scheduled for {html.escape(day)}.</p></div>",unsafe_allow_html=True)
    else:
        st.info("The current ESPN scoreboard does not yet expose a game day for this player's team. The Thursday FLEX rule will fire automatically when schedule data is available.")


def _actual_week_table(load_weekly, espn_ppr, weekly_name_col):
    w=load_weekly().copy()
    nc=weekly_name_col(w)
    if not nc:return pd.DataFrame()
    w["_player_key"]=w[nc].astype(str).map(_key)
    w["_actual_ppr"]=espn_ppr(w)
    if "position" in w.columns:w["_pos"]=w["position"].astype(str).str.upper().replace({"HB":"RB","FB":"RB"})
    else:w["_pos"]="ALL"
    return w


def render_analyst_tracker(load_weekly, espn_ppr, weekly_name_col):
    st.markdown("<div class='coach-section-title'>Analyst Tracker</div>",unsafe_allow_html=True)
    st.caption("Upload a weekly rankings snapshot and Shiva grades the analysts against what actually happened. Required columns: analyst, player, rank, season, week. Optional: position.")
    sample=pd.DataFrame([{"analyst":"Analyst A","player":"Player Name","rank":1,"season":2025,"week":1,"position":"RB"}])
    st.download_button("Download rankings template",sample.to_csv(index=False).encode(),file_name="shiva_analyst_rankings_template.csv",mime="text/csv",use_container_width=True)
    up=st.file_uploader("Upload rankings CSV",type=["csv"],key="analyst_upload")
    if up is None:return
    try: ranks=pd.read_csv(up)
    except Exception:
        st.error("That CSV could not be read.");return
    required={"analyst","player","rank","season","week"}
    if not required.issubset(ranks.columns):
        st.error("Missing required columns: "+", ".join(sorted(required-set(ranks.columns))));return
    w=_actual_week_table(load_weekly,espn_ppr,weekly_name_col)
    if w.empty:
        st.info("Historical weekly results are unavailable right now.");return
    ranks=ranks.copy();ranks["_player_key"]=ranks["player"].astype(str).map(_key)
    ranks["season"]=pd.to_numeric(ranks["season"],errors="coerce");ranks["week"]=pd.to_numeric(ranks["week"],errors="coerce");ranks["rank"]=pd.to_numeric(ranks["rank"],errors="coerce")
    if "position" in ranks.columns:ranks["_pos"]=ranks["position"].astype(str).str.upper()
    else:ranks["_pos"]="ALL"
    cols=["_player_key","season","week","_actual_ppr","_pos"]
    actual=w[cols].dropna(subset=["season","week","_actual_ppr"]).copy()
    if (ranks["_pos"]!="ALL").any():
        actual["actual_rank"]=actual.groupby(["season","week","_pos"])["_actual_ppr"].rank(method="min",ascending=False)
        merged=ranks.merge(actual,on=["_player_key","season","week","_pos"],how="inner")
    else:
        actual["actual_rank"]=actual.groupby(["season","week"])["_actual_ppr"].rank(method="min",ascending=False)
        merged=ranks.merge(actual.drop(columns=["_pos"]),on=["_player_key","season","week"],how="inner")
    if merged.empty:
        st.info("No uploaded player/week rows matched the historical weekly database.");return
    rows=[]
    for analyst,g in merged.groupby("analyst"):
        corr=g["rank"].corr(g["actual_rank"],method="spearman") if len(g)>=3 else np.nan
        mae=(g["rank"]-g["actual_rank"]).abs().mean()
        rows.append({"Analyst":analyst,"Matched":len(g),"Rank error":round(float(mae),1),"Spearman":round(float(corr),3) if not pd.isna(corr) else np.nan})
    out=pd.DataFrame(rows).sort_values(["Rank error","Spearman"],ascending=[True,False])
    st.dataframe(out,use_container_width=True,hide_index=True)
    best=out.iloc[0]
    st.markdown(f"<div class='shiva-says-call'><span>SHIVA SAYS</span><b>{html.escape(str(best['Analyst']))} graded best in this sample.</b><p>Average ranking error: {best['Rank error']} spots across {int(best['Matched'])} matched player-weeks.</p></div>",unsafe_allow_html=True)


def render_shiva_moments():
    st.markdown("<div class='coach-section-title'>Shiva Moments</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='moment-list'>
      <div class='moment'><span>LINEUP EDGE</span><b>Never burn FLEX on Thursday</b><p>If a Thursday player is in FLEX, move him to his positional slot. You preserve more replacement options for Sunday if someone gets hurt.</p></div>
      <div class='moment'><span>DRAFT EDGE</span><b>Draft the room, not just the board</b><p>If the managers picking twice before you already filled QB, you can often let your QB target come back and use the current pick on a scarcer position.</p></div>
      <div class='moment'><span>ROSTER EDGE</span><b>Raise the floor without killing the ceiling</b><p>Build around repeatable 15+ point producers, then use selected roster spots on players with legitimate week-winning upside.</p></div>
    </div>""", unsafe_allow_html=True)


def render_draft_moment(draft_log, next_pick: int, team_count: int, user_slot: int):
    if not draft_log:return
    cur=int(next_pick);user_next=None
    for p in range(cur+1,cur+team_count*2+1):
        r=(p-1)//team_count+1;w=(p-1)%team_count+1;team=w if r%2 else team_count-w+1
        if team==user_slot:user_next=p;break
    if not user_next:return
    teams_between=[]
    for p in range(cur+1,user_next):
        r=(p-1)//team_count+1;w=(p-1)%team_count+1;team=w if r%2 else team_count-w+1
        if team not in teams_between:teams_between.append(team)
    if not teams_between:return
    qb_by_team={t:any(str(x.get('pos','')).upper()=='QB' for x in draft_log if int(x.get('team',-1))==t) for t in teams_between}
    if teams_between and all(qb_by_team.values()):
        st.markdown(f"<div class='draft-moment'><span>SHIVA MOMENT</span><b>The managers between your picks already have quarterbacks.</b><p>If your QB target isn't an obvious tier-break, consider taking the scarcer RB/WR/TE now and letting the quarterback come back to you at pick {user_next}.</p></div>",unsafe_allow_html=True)


def render_season_hub(players, load_weekly, weekly_for_player, espn_ppr, weekly_name_col=None):
    preseason=date.today()<KICKOFF
    phase="PRESEASON MODE" if preseason else "IN-SEASON MODE"
    st.markdown(f"<div class='coach-phase'>{phase}</div>",unsafe_allow_html=True)
    st.markdown("<div class='coach-hero'><span>SHIVA SAYS</span><h2>Make the decision. See the why.</h2><p>Floor, ceiling and consistency first. Extra detail only when you want it.</p></div>",unsafe_allow_html=True)
    tab=st.radio("Coach view",["Start / Sit","Player Watch","Lineup","Analysts","Moments"],horizontal=True,label_visibility="collapsed",key="coach_view")
    if tab=="Start / Sit":render_compare(players,load_weekly,weekly_for_player,espn_ppr,"Who should I start?")
    elif tab=="Player Watch":render_player_watch(players)
    elif tab=="Lineup":render_lineup_check(players)
    elif tab=="Analysts":
        if weekly_name_col is None:st.info("Analyst grading is waiting for the weekly-name mapper.")
        else:render_analyst_tracker(load_weekly,espn_ppr,weekly_name_col)
    else:render_shiva_moments()
    if preseason:
        st.caption("Preseason note: weekly opponent-specific recommendations remain intentionally limited until 2026 regular-season game data exists.")


CSS=r'''<style>
.coach-phase{font-size:10px;font-weight:950;letter-spacing:.85px;color:#d8b35b;margin:4px 1px 7px}.coach-hero{background:linear-gradient(145deg,#171f27,#0d1318);border:1px solid rgba(216,179,91,.24);border-radius:16px;padding:17px;margin-bottom:14px}.coach-hero>span,.shiva-says-call>span,.draft-moment>span,.moment>span,.lineup-alert>span{font-size:9px;font-weight:950;letter-spacing:.85px;color:#d8b35b}.coach-hero h2{font-size:25px;line-height:1.03;margin:4px 0 6px;color:#fff}.coach-hero p{font-size:13px;line-height:1.4;color:#aab5bd;margin:0}.coach-section-title{font-size:20px;font-weight:950;letter-spacing:-.45px;color:#f6f8f9;margin:14px 0 8px}.coach-compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.coach-player-card{background:#101820;border:1px solid rgba(200,211,219,.14);border-radius:14px;padding:13px}.coach-player-card.winner{border-color:rgba(216,179,91,.55);box-shadow:inset 0 0 0 1px rgba(216,179,91,.08)}.coach-player-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.coach-player-top b{font-size:15px;color:#fff}.coach-player-top span{display:block;font-size:10px;color:#91a0ab;margin-top:2px}.coach-rank{font-size:12px;font-weight:900;color:#d8b35b}.coach-metrics{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px}.coach-metrics div{background:#0b1116;border-radius:9px;padding:8px}.coach-metrics strong{display:block;font-size:19px;line-height:1;color:#f7f8f9}.coach-metrics span{font-size:9px;color:#8f9ca6;text-transform:uppercase;font-weight:850}.shiva-says-call,.draft-moment,.lineup-alert{background:linear-gradient(145deg,#211f17,#12110d);border:1px solid rgba(216,179,91,.34);border-radius:14px;padding:13px;margin:9px 0 13px}.shiva-says-call b,.draft-moment b,.lineup-alert b{display:block;font-size:18px;color:#fff;margin:3px 0}.shiva-says-call p,.draft-moment p,.lineup-alert p{font-size:12px;line-height:1.42;color:#b3bac0;margin:0}.lineup-alert.danger{border-color:rgba(240,106,120,.55);background:linear-gradient(145deg,#29191d,#151012)}.lineup-alert.good{border-color:rgba(97,208,149,.35);background:linear-gradient(145deg,#12221a,#0c1510)}.moment-list{display:grid;gap:8px}.moment{background:#101820;border:1px solid rgba(200,211,219,.13);border-radius:14px;padding:13px}.moment b{display:block;font-size:15px;color:#fff;margin:3px 0}.moment p{font-size:12px;line-height:1.42;color:#9eabb5;margin:0}.watch-card{background:#101820;border:1px solid rgba(200,211,219,.13);border-radius:14px;padding:13px;margin-bottom:8px}.watch-card span{font-size:9px;color:#8f9ca6;font-weight:850}.watch-card b{display:block;font-size:15px;color:#fff;margin:4px 0}.watch-card p{font-size:12px;line-height:1.4;color:#9eabb5;margin:0 0 6px}.watch-card a{font-size:11px;color:#d8b35b!important;text-decoration:none!important;font-weight:900}.st-key-coach_view div[role="radiogroup"]{grid-template-columns:repeat(5,minmax(0,1fr))!important}.st-key-coach_view div[role="radiogroup"] label{min-height:48px!important}.st-key-coach_view div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:10px!important}@media(max-width:430px){.coach-compare-grid{grid-template-columns:1fr}.coach-player-card{padding:12px}.coach-metrics{grid-template-columns:repeat(4,1fr)}.coach-metrics div{padding:7px 5px}.coach-metrics strong{font-size:16px}.coach-metrics span{font-size:8px}.coach-hero h2{font-size:23px}.st-key-coach_view div[role="radiogroup"]{display:flex!important;overflow-x:auto!important;gap:5px!important}.st-key-coach_view div[role="radiogroup"] label{min-width:94px!important}}
</style>'''


def inject_css():
    st.markdown(CSS,unsafe_allow_html=True)
