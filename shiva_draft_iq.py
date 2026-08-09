from __future__ import annotations

import html
from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# Shiva Blast uses components.html on the Home screen. Streamlit normally reserves only the
# original iframe height, so expanding the video inside the iframe can visually overlap the
# cards below it. Patch only the Shiva Blast component so its actual Streamlit host container
# grows with the video and collapses again when playback ends. Other components are untouched.
_original_components_html = components.html


def _shiva_components_html(body, *args, **kwargs):
    if isinstance(body, str) and 'id="shivaBlast"' in body:
        host_helper = r'''
      function setShivaHostHeight(h){
        try{
          const frame=window.frameElement;
          if(frame){
            frame.style.height=h+'px';
            frame.setAttribute('height',String(h));
            const iframeWrap=frame.parentElement;
            const elementWrap=frame.closest('[data-testid="stElementContainer"]');
            [iframeWrap,elementWrap].forEach((el)=>{
              if(!el)return;
              el.style.height=h+'px';
              el.style.minHeight=h+'px';
              el.style.overflow='hidden';
              el.style.transition='height .34s ease,min-height .34s ease';
            });
          }
          window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:h},'*');
        }catch(e){}
      }
'''
        body = body.replace(
            "      const video=document.getElementById('blastVideo');\n",
            "      const video=document.getElementById('blastVideo');\n" + host_helper,
            1,
        )
        body = body.replace(
            "        try{window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:650},'*');if(window.frameElement){window.frameElement.style.height='650px';}}catch(e){}",
            "        setShivaHostHeight(650);",
            1,
        )
        body = body.replace(
            "      video.addEventListener('ended',()=>{video.currentTime=0;});",
            "      video.addEventListener('ended',()=>{wrap.classList.remove('open');video.pause();video.currentTime=0;setTimeout(()=>setShivaHostHeight(64),360);});",
            1,
        )
    return _original_components_html(body, *args, **kwargs)


if components.html is not _shiva_components_html:
    components.html = _shiva_components_html


def _num(value, fallback=999.0) -> float:
    try:
        n = float(value)
        return n if np.isfinite(n) else fallback
    except Exception:
        return fallback


def _position_need(pos: str, counts: dict[str, int], round_no: int) -> float:
    pos = str(pos).upper().replace("D/ST", "DST").replace("DEF", "DST")
    rb, wr, qb, te = counts.get("RB", 0), counts.get("WR", 0), counts.get("QB", 0), counts.get("TE", 0)

    if pos == "RB":
        need = 20.0 if rb < 2 else 8.0 if rb == 2 else -2.0
        if round_no <= 3 and rb < 2:
            need += 8.0
        if wr == 0 and rb >= 2:
            need -= 8.0
        return need
    if pos == "WR":
        need = 22.0 if wr < 2 else 7.0 if wr == 2 else -2.0
        if wr == 0 and rb >= 2:
            need += 18.0
        if round_no <= 4 and wr < 2:
            need += 6.0
        return need
    if pos == "TE":
        if te:
            return -8.0
        return 5.0 if round_no <= 2 else 13.0 if round_no <= 6 else 8.0
    if pos == "QB":
        if qb:
            return -12.0
        if round_no <= 2:
            return -22.0
        if round_no == 3:
            return -5.0
        if round_no <= 7:
            return 9.0
        return 13.0
    if pos in {"DST", "K"}:
        return -65.0 if round_no < 10 else 3.0
    return 0.0


def get_draft_recommendations(
    available: pd.DataFrame,
    roster: pd.DataFrame,
    current_pick: int,
    round_no: int,
    limit: int = 3,
) -> list[dict]:
    if available.empty:
        return []

    counts = roster["pos"].astype(str).str.upper().value_counts().to_dict() if not roster.empty and "pos" in roster else {}
    pool = available.copy().head(80)
    pool["_adp"] = pd.to_numeric(pool.get("draft_adp"), errors="coerce")
    pool["_rank"] = pd.to_numeric(pool.get("overall_rank"), errors="coerce")
    pool["_market"] = pool["_adp"].fillna(pool["_rank"]).fillna(999.0)

    max_reach = 8 if round_no <= 2 else 14 if round_no <= 4 else 22 if round_no <= 7 else 34
    realistic = pool.loc[(pool["_market"] - float(current_pick) <= max_reach) | (pool["_market"] <= float(current_pick))].copy()
    if len(realistic) >= 6:
        pool = realistic

    scored = []
    for _, row in pool.iterrows():
        pos = str(row.get("pos", "")).upper().replace("D/ST", "DST").replace("DEF", "DST")
        market = _num(row.get("_market"))
        delta = float(current_pick) - market
        value_score = min(28.0, delta * 1.25) if delta >= 0 else max(-48.0, delta * 2.2)
        need_score = _position_need(pos, counts, round_no)
        rank_score = max(-12.0, 16.0 - max(0.0, market - current_pick) * 0.45)
        score = 60.0 + value_score + need_score + rank_score
        scored.append({
            "row": row,
            "score": score,
            "need": need_score,
            "value": value_score,
            "delta": delta,
            "market": market,
            "pos": pos,
        })

    if not scored:
        return []

    by_score = sorted(scored, key=lambda x: (-x["score"], x["market"]))
    by_need = sorted(scored, key=lambda x: (-x["need"], -x["score"], x["market"]))
    by_value = sorted(scored, key=lambda x: (-x["value"], -x["score"], x["market"]))

    chosen: list[tuple[str, dict]] = []
    used: set[str] = set()
    for label, bucket in (("BEST PICK", by_score), ("BEST ROSTER FIT", by_need), ("BEST VALUE", by_value)):
        candidate = next((x for x in bucket if str(x["row"].get("id")) not in used), None)
        if candidate is None:
            continue
        pid = str(candidate["row"].get("id"))
        used.add(pid)
        chosen.append((label, candidate))
        if len(chosen) >= limit:
            break

    results = []
    for label, item in chosen:
        row = item["row"]
        pos = item["pos"]
        market = item["market"]
        delta = item["delta"]
        if item["need"] >= 25:
            reason = f"Fills your biggest roster need without abandoning the Round {round_no} value tier."
        elif delta >= 8:
            reason = f"Strong value: ADP {market:.1f}, now available at pick {current_pick}."
        elif delta >= 0:
            reason = f"Fits this pick range and gives you positive ADP value at {pos}."
        else:
            reason = f"A reasonable {pos} target here; the reach stays inside Shiva IQ's Round {round_no} guardrail."
        results.append({
            "label": label,
            "id": str(row.get("id")),
            "name": str(row.get("name", "Unknown")),
            "pos": pos,
            "team": str(row.get("team", "")),
            "adp": market,
            "reason": reason,
        })
    return results


def render_shiva_draft_iq(
    available: pd.DataFrame,
    roster: pd.DataFrame,
    current_pick: int,
    round_no: int,
    is_user_pick: bool,
    draft_href: Callable[[str], str],
) -> None:
    st.markdown(
        """
        <style>
        .shiva-iq-shell{background:linear-gradient(145deg,#131f2a,#0a1219);border:1px solid #2b4151;border-radius:16px;padding:12px;margin:7px 0 10px;box-shadow:0 8px 24px rgba(0,0,0,.16)}
        .shiva-iq-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:7px}.shiva-iq-title{font-size:14px;font-weight:950;color:#fff}.shiva-iq-live{font-size:8px;font-weight:950;color:#74e3d2;border:1px solid #285c58;border-radius:999px;padding:4px 7px;background:#092c2a}.shiva-iq-copy{font-size:9px;color:#92a3af;line-height:1.35}
        .iq-rec{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;background:#0d1821;border:1px solid #223542;border-radius:12px;padding:9px 10px;margin-top:6px}.iq-label{font-size:7px;color:#d9ff38;font-weight:950;letter-spacing:.6px}.iq-name{font-size:12px;color:#fff;font-weight:950;margin-top:2px}.iq-meta{font-size:8px;color:#94a5b1;margin-top:2px}.iq-reason{font-size:8px;color:#b8c5ce;margin-top:4px;line-height:1.3}.iq-draft{display:flex;align-items:center;justify-content:center;min-width:55px;min-height:35px;padding:0 8px;border-radius:9px;background:#74e3d2;color:#092c2a!important;text-decoration:none!important;font-size:9px;font-weight:950}.iq-locked{font-size:9px;color:#7f909c;padding-top:2px}
        @media(min-width:1000px){.shiva-iq-shell{max-width:440px}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="shiva-iq-shell"><div class="shiva-iq-head"><div class="shiva-iq-title">✦ SHIVA DRAFT IQ</div><div class="shiva-iq-live">LIVE DRAFT CONTEXT</div></div><div class="shiva-iq-copy">Reads your roster, the live available-player pool, current pick and ADP before recommending anyone.</div></div>',
        unsafe_allow_html=True,
    )

    if not is_user_pick:
        st.markdown('<div class="iq-locked">Shiva IQ will unlock when you are on the clock.</div>', unsafe_allow_html=True)
        return

    if st.button("✦ WHO SHOULD I DRAFT?", key="shiva_iq_help", type="primary", use_container_width=True):
        st.session_state["shiva_iq_recs"] = get_draft_recommendations(available, roster, current_pick, round_no)
        st.session_state["shiva_iq_pick"] = current_pick

    recs = st.session_state.get("shiva_iq_recs", [])
    if st.session_state.get("shiva_iq_pick") != current_pick:
        recs = []
        st.session_state["shiva_iq_recs"] = []

    for rec in recs:
        name = html.escape(rec["name"])
        team = html.escape(rec["team"])
        pos = html.escape(rec["pos"])
        reason = html.escape(rec["reason"])
        href = html.escape(draft_href(rec["id"]), quote=True)
        st.markdown(
            f'<div class="iq-rec"><div><div class="iq-label">{rec["label"]}</div><div class="iq-name">{name}</div><div class="iq-meta">{pos} · {team} · ADP {rec["adp"]:.1f}</div><div class="iq-reason">{reason}</div></div><a class="iq-draft" href="{href}" target="_self">DRAFT</a></div>',
            unsafe_allow_html=True,
        )
