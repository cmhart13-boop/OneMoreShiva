from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd

ESPN_BASE = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"
LINEUP_SLOTS = {0:"QB",2:"RB",4:"WR",6:"TE",16:"DST",17:"K",20:"BE",21:"IR",23:"FLEX"}


@dataclass(frozen=True)
class LeagueAuth:
    league_id: str
    season: int
    swid: str = ""
    espn_s2: str = ""

    def cookie(self) -> str:
        parts=[]
        if self.swid.strip(): parts.append(f"SWID={self.swid.strip()}")
        if self.espn_s2.strip(): parts.append(f"espn_s2={self.espn_s2.strip()}")
        return "; ".join(parts)


def _request_json(url: str, *, auth: LeagueAuth | None = None, headers: dict[str,str] | None = None) -> Any:
    hdr={"User-Agent":"Mozilla/5.0 (One More Shiva; verified fantasy client)","Accept":"application/json"}
    if headers: hdr.update(headers)
    if auth and auth.cookie(): hdr["Cookie"]=auth.cookie()
    req=Request(url,headers=hdr)
    with urlopen(req,timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def league_url(auth: LeagueAuth, views: list[str] | None = None) -> str:
    base=f"{ESPN_BASE}/seasons/{int(auth.season)}/segments/0/leagues/{auth.league_id}"
    if not views: return base
    return base+"?"+"&".join(f"view={v}" for v in views)


def fetch_league(auth: LeagueAuth) -> dict:
    data=_request_json(league_url(auth,["mSettings","mTeam","mRoster","mStatus"]),auth=auth)
    if not isinstance(data,dict) or not data.get("teams"):
        raise RuntimeError("ESPN returned no league teams. Check league ID, season, and private-league cookies if required.")
    return data


def fetch_player_pool(auth: LeagueAuth, limit: int = 300) -> list[dict]:
    fantasy_filter={"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"limit":int(limit),"sortPercOwned":{"sortPriority":1,"sortAsc":False}}}
    data=_request_json(
        league_url(auth,["kona_player_info"]),
        auth=auth,
        headers={"x-fantasy-filter":json.dumps(fantasy_filter,separators=(",",":"))},
    )
    players=data.get("players",[]) if isinstance(data,dict) else []
    return players if isinstance(players,list) else []


def _player_name(entry: dict) -> str:
    p=(entry or {}).get("playerPoolEntry",entry) or {}
    player=p.get("player",{}) or {}
    return str(player.get("fullName") or player.get("name") or "").strip()


def _player_id(entry: dict) -> str:
    p=(entry or {}).get("playerPoolEntry",entry) or {}
    player=p.get("player",{}) or {}
    return str(player.get("id") or "")


def _pro_team(entry: dict) -> str:
    p=(entry or {}).get("playerPoolEntry",entry) or {}
    player=p.get("player",{}) or {}
    return str(player.get("proTeamId") or "")


def parse_league(data: dict) -> dict:
    members={str(x.get("id")):x for x in data.get("members",[]) if isinstance(x,dict)}
    teams=[]
    roster_rows=[]
    for t in data.get("teams",[]):
        tid=int(t.get("id",0) or 0)
        owners=[]
        for oid in t.get("owners",[]) or []:
            m=members.get(str(oid),{})
            nm=(str(m.get("firstName") or "")+" "+str(m.get("lastName") or "")).strip()
            if nm: owners.append(nm)
        team_name=(str(t.get("location") or "")+" "+str(t.get("nickname") or "")).strip() or str(t.get("name") or f"Team {tid}")
        teams.append({"team_id":tid,"team":team_name,"owners":", ".join(owners),"wins":(t.get("record",{}).get("overall",{}) or {}).get("wins"),"losses":(t.get("record",{}).get("overall",{}) or {}).get("losses")})
        roster=(t.get("roster",{}) or {}).get("entries",[]) or []
        for e in roster:
            ppe=e.get("playerPoolEntry",{}) or {}
            player=ppe.get("player",{}) or {}
            slot=int(e.get("lineupSlotId",20) or 20)
            roster_rows.append({
                "team_id":tid,"team":team_name,"player_id":str(player.get("id") or ""),
                "player":str(player.get("fullName") or ""),"slot_id":slot,"slot":LINEUP_SLOTS.get(slot,str(slot)),
                "pro_team_id":player.get("proTeamId"),"injury_status":player.get("injuryStatus"),
                "percent_owned":ppe.get("ratings",{}).get("0",{}).get("positionalRanking") if isinstance(ppe.get("ratings"),dict) else None,
            })
    status=data.get("status",{}) or {}
    settings=data.get("settings",{}) or {}
    return {
        "league_id":str(data.get("id") or ""),
        "season":int(data.get("seasonId") or status.get("currentMatchupPeriod") or 0),
        "name":str(settings.get("name") or "ESPN League"),
        "scoring_period":status.get("currentScoringPeriod"),
        "matchup_period":status.get("currentMatchupPeriod"),
        "teams":pd.DataFrame(teams),
        "roster":pd.DataFrame(roster_rows),
        "raw":data,
    }


def parse_free_agents(entries: list[dict]) -> pd.DataFrame:
    rows=[]
    for outer in entries:
        ppe=(outer or {}).get("playerPoolEntry",outer) or {}
        player=ppe.get("player",{}) or {}
        status=str(ppe.get("status") or outer.get("status") or "")
        rows.append({
            "player_id":str(player.get("id") or ""),
            "player":str(player.get("fullName") or ""),
            "status":status,
            "pro_team_id":player.get("proTeamId"),
            "injury_status":player.get("injuryStatus"),
            "percent_owned":ppe.get("percentOwned"),
            "percent_started":ppe.get("percentStarted"),
        })
    return pd.DataFrame(rows)


def current_scoreboard() -> dict:
    return _request_json("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard")


def team_game_day(team_abbr: str) -> tuple[str|None, datetime|None]:
    try:
        data=current_scoreboard()
        needle=str(team_abbr or "").upper()
        for ev in data.get("events",[]):
            comp=(ev.get("competitions") or [{}])[0]
            labels=[]
            for c in comp.get("competitors",[]) or []:
                t=c.get("team",{}) or {}
                labels.extend([str(t.get("abbreviation") or "").upper(),str(t.get("shortDisplayName") or "").upper(),str(t.get("displayName") or "").upper()])
            if needle and needle in labels:
                dt=datetime.fromisoformat(str(ev.get("date")).replace("Z","+00:00"))
                return dt.strftime("%A"),dt
    except Exception:
        pass
    return None,None


def espn_news(limit: int = 100) -> list[dict]:
    data=_request_json(f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit={int(limit)}")
    return data.get("articles",[]) if isinstance(data,dict) else []


def player_news(player_name: str, limit: int = 12) -> list[dict]:
    name=str(player_name or "").strip()
    if not name: return []
    terms={name.casefold(),name.split()[-1].casefold()}
    hits=[]
    for a in espn_news(100):
        text=(str(a.get("headline") or "")+" "+str(a.get("description") or "")).casefold()
        if any(t and t in text for t in terms):
            links=a.get("links",{}) or {}
            url=(links.get("web",{}) or {}).get("href") or (links.get("mobile",{}) or {}).get("href")
            hits.append({"headline":str(a.get("headline") or ""),"description":str(a.get("description") or ""),"published":str(a.get("published") or a.get("lastModified") or ""),"url":url or ""})
            if len(hits)>=limit: break
    return hits
