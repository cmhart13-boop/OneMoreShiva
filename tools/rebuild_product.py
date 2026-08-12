from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "app_core.py"
PATCH = ROOT / "sitecustomize.py"
APP = ROOT / "app.py"
LEGACY = ROOT / "app_legacy.py"


def bake_runtime_patch(source: str) -> str:
    namespace: dict[str, object] = {}
    patch_source = PATCH.read_text(encoding="utf-8")
    exec(compile(patch_source, str(PATCH), "exec"), namespace)
    fn = namespace.get("_patch_app_core")
    if not callable(fn):
        raise RuntimeError("sitecustomize.py does not expose _patch_app_core")
    rebuilt = fn(source)
    if not isinstance(rebuilt, str) or rebuilt == source:
        raise RuntimeError("runtime patch produced no app_core.py changes")
    return rebuilt


def apply_product_system(source: str) -> str:
    s = source
    replacements = [
        ('page_title="Shiva Fantasy Football"', 'page_title="One More Shiva"'),
        ('"Command Center","Everything important, one thumb away."', '"Shiva Says","Your fantasy decision room — fast, clear, and built to help you win."'),
        ('Draft Intelligence', 'THE SHIVA EDGE'),
        ('Build the team before the room knows what happened.', 'Raise the floor. Keep the ceiling.'),
        ('Real rankings, full-PPR history, queue, draft board, roster and Shiva in one mobile workflow.', 'Turn rankings, weekly history, roster context and draft flow into decisions you can act on.'),
        ('"Analytics","Player database and historical Full-PPR analysis."', '"Shiva Lab","Compare players and inspect the historical Full-PPR evidence behind the call."'),
        ("label='Shiva IQ' if p=='Shiva' else p", "label={'Shiva':'Shiva Says','Guide':'Guide','Draft':'Draft','Analytics':'Shiva Lab'}.get(p,p)"),
    ]
    for old, new in replacements:
        s = s.replace(old, new, 1)

    marker = "\n</style>'''\nst.markdown(CSS, unsafe_allow_html=True)"
    if marker not in s:
        raise RuntimeError("CSS insertion marker missing")

    product_css = r'''
/* ONE MORE SHIVA — PRODUCT SYSTEM */
:root{--shiva-bg:#080d12;--shiva-card:#10171e;--shiva-card-2:#151f28;--shiva-line:rgba(201,211,220,.13);--shiva-text:#f7f8f9;--shiva-muted:#9aa7b2;--shiva-gold:#d8b35b;--shiva-gold-soft:#8f7437;--shiva-green:#61d095;--shiva-red:#f06a78;--shiva-blue:#6aa7ff}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:radial-gradient(circle at 50% -12%,#17232d 0,#0b1117 34%,#080d12 66%)!important}
.block-container{max-width:980px!important;padding-left:12px!important;padding-right:12px!important}
.app-top{padding:5px 2px 9px!important;border-bottom:1px solid var(--shiva-line)!important;margin-bottom:8px!important}.brand-badge{background:linear-gradient(145deg,#2a2f34,#0d1115)!important;border:1px solid rgba(216,179,91,.38)!important;box-shadow:inset 0 0 18px rgba(216,179,91,.06)!important}.brand-badge::after{content:'🏆';font-size:18px}.brand-badge{font-size:0!important}.brand-title,.brand-name{color:var(--shiva-text)!important;letter-spacing:-.35px!important}.brand-sub{color:var(--shiva-gold)!important;letter-spacing:.65px!important}.data-status{background:rgba(97,208,149,.07)!important;border-color:rgba(97,208,149,.22)!important;color:#8ee3b5!important}
.screen-head h1{font-size:26px!important;letter-spacing:-.8px!important}.screen-head p{font-size:12px!important;line-height:1.42!important;color:var(--shiva-muted)!important}
.hero-card{background:linear-gradient(145deg,#18232d 0,#10171e 58%,#0c1116 100%)!important;border:1px solid rgba(216,179,91,.20)!important;border-radius:16px!important;padding:17px!important;box-shadow:0 12px 30px rgba(0,0,0,.18)!important}.hero-card:after{content:'🏆'!important;filter:grayscale(.25)!important;opacity:.075!important}.hero-kicker{color:var(--shiva-gold)!important}.hero-card h2{font-size:28px!important;line-height:1.01!important;letter-spacing:-.95px!important}.hero-card p{font-size:12px!important;line-height:1.42!important;color:#aeb8c1!important}
.stat-strip{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}.mini-stat{min-height:94px!important;text-align:left!important;padding:13px!important;background:linear-gradient(145deg,#111a22,#0d141a)!important;border:1px solid var(--shiva-line)!important;border-radius:13px!important}.mini-stat b{font-size:28px!important;letter-spacing:-.8px!important}.mini-stat span{font-size:9px!important;line-height:1.35!important;color:var(--shiva-muted)!important;letter-spacing:.2px!important}
.quick-grid{gap:8px!important}.quick-card{min-height:92px!important;padding:14px!important;border-radius:14px!important;background:linear-gradient(145deg,#121b23,#0d141a)!important;border:1px solid var(--shiva-line)!important;transition:transform .12s ease,border-color .12s ease!important}.quick-card:active{transform:scale(.985)!important;border-color:rgba(216,179,91,.35)!important}.quick-icon{font-size:21px!important}.quick-title{font-size:14px!important}.quick-sub{font-size:10.5px!important;line-height:1.35!important}
.player-shell,.pick-card,.profile-hero,.weekly-card,.roster-slot,.shiva-box,.guide-card,.strategy-box,.shiva-iq-panel,.iq-report-shell{background:linear-gradient(145deg,#111a22,#0c1319)!important;border:1px solid var(--shiva-line)!important;border-radius:13px!important}.player-shell{min-height:70px!important;padding:9px 10px!important}.player-rank{background:#19242d!important;border:1px solid rgba(255,255,255,.035)!important}.draft-inline{background:linear-gradient(145deg,#d8b35b,#b38f40)!important;border-color:#e5c777!important;color:#17130b!important;box-shadow:none!important}.on-clock{background:linear-gradient(100deg,#47252b,#26161a)!important;border-color:rgba(240,106,120,.45)!important}.board-cell.clock{background:linear-gradient(145deg,#2c291b,#171711)!important;border-color:var(--shiva-gold)!important}.board-cell.mine{box-shadow:inset 0 0 0 1px rgba(216,179,91,.30)!important}
.bottom-nav{height:calc(68px + env(safe-area-inset-bottom))!important;padding:5px 12px calc(5px + env(safe-area-inset-bottom))!important;background:rgba(8,13,18,.96)!important;border-top:1px solid rgba(216,179,91,.13)!important;box-shadow:0 -8px 24px rgba(0,0,0,.30)!important}.bottom-nav a{height:54px!important;min-height:54px!important;font-size:10px!important;color:rgba(207,215,221,.60)!important}.bottom-nav a.active{color:#f8f7f4!important}.bottom-nav a.active span:last-child{color:var(--shiva-gold)!important}.bottom-nav .nav-icon{font-size:25px!important;height:28px!important}.bottom-nav .shiva-iq-mark{filter:sepia(.7) saturate(.55) hue-rotate(355deg)!important;opacity:.82!important}
.stButton>button,.stDownloadButton>button{border-radius:11px!important;border:1px solid rgba(216,179,91,.18)!important;background:#131b22!important;color:#f5f7f8!important}.stButton>button[kind="primary"]{background:linear-gradient(145deg,#d8b35b,#b38f40)!important;border-color:#ddbd70!important;color:#17130b!important}
textarea,input,[data-baseweb="select"]>div{background:#0e151b!important;border-color:rgba(216,179,91,.14)!important}
.home-fantasy-news-title{color:#f5f5f3!important;font-size:18px!important}.home-fantasy-news-title:before{content:'SHIVA BLAST';color:var(--shiva-gold);font-size:9px;letter-spacing:.8px;display:block;margin-bottom:3px}
@media(max-width:430px){.stat-strip{grid-template-columns:repeat(2,minmax(0,1fr))!important}.hero-card h2{font-size:26px!important}.bottom-nav{padding-left:8px!important;padding-right:8px!important}.bottom-nav a{font-size:9px!important}}
'''
    s = s.replace(marker, "\n" + product_css + marker, 1)

    analytics_anchor = "\ndef shiva():\n"
    if analytics_anchor in s and "\ndef shiva_compare():\n" not in s:
        compare_func = r'''
def shiva_compare():
    st.markdown("### Compare players")
    st.caption("Historical evidence + current ranking context. No fabricated projection confidence.")
    names=players["name"].dropna().astype(str).drop_duplicates().tolist()
    if len(names)<2:
        st.info("Player data is not available for comparison right now.")
        return
    c1,c2=st.columns(2)
    with c1:a=st.selectbox("Player A",names,index=0,key="compare_a")
    with c2:b=st.selectbox("Player B",names,index=min(1,len(names)-1),key="compare_b")
    if a==b:
        st.info("Choose two different players.")
        return
    rows=[]
    for nm in (a,b):
        pr=players.loc[players["name"].eq(nm)].iloc[0]
        rows.append((nm,str(pr.get("pos","")),pr.get("adp"),pr.get("rank")))
    cards=[]
    for nm,pos,adp,rank in rows:
        adp_text="—" if pd.isna(adp) else f"{float(adp):.1f}"
        rank_text="—" if pd.isna(rank) else str(int(rank))
        cards.append(f'<div class="mini-stat"><b>{html.escape(str(nm))}</b><span>{html.escape(str(pos))} · ADP {adp_text} · Rank {rank_text}</span></div>')
    st.markdown('<div class="stat-strip">'+''.join(cards)+'</div>',unsafe_allow_html=True)
    st.caption("Open either player profile for season-by-season and week-by-week Full-PPR history.")

'''
        s = s.replace(analytics_anchor, "\n" + compare_func + "def shiva():\n", 1)

    analytics_call = '    render_players(df,"Analytics","none",150)'
    if analytics_call in s and '    shiva_compare()\n' not in s:
        s = s.replace(analytics_call, '    shiva_compare()\n    st.markdown("### Player database")\n' + analytics_call, 1)

    return s


def write_entrypoint() -> None:
    APP.write_text(
        '"""One More Shiva production entrypoint.\n\nOne execution path: app.py -> app_core.py.\n"""\n'
        'from pathlib import Path\n\n'
        'core = Path(__file__).with_name("app_core.py")\n'
        'code = core.read_text(encoding="utf-8")\n'
        'exec(compile(code, str(core), "exec"), globals(), globals())\n',
        encoding="utf-8",
    )


def audit(source: str) -> None:
    ast.parse(APP.read_text(encoding="utf-8"))
    ast.parse(source)
    assert "Draft-Coach/main/current_rankings.csv" not in source
    assert "Draft-Coach/main/player_weekly_master_2014_2025.csv.gz" not in source
    assert "render_nfl_kickoff_countdown()" in source
    assert "Shiva Says" in source
    assert "SHIVA BLAST" in source
    assert "def shiva_compare():" in source
    assert (ROOT / "current_rankings.csv").exists()
    assert (ROOT / "player_weekly_master_2014_2025.csv.gz").exists()


def main() -> None:
    source = CORE.read_text(encoding="utf-8")
    source = bake_runtime_patch(source)
    source = apply_product_system(source)
    CORE.write_text(source, encoding="utf-8")
    write_entrypoint()
    if PATCH.exists():
        PATCH.unlink()
    if LEGACY.exists():
        LEGACY.unlink()
    audit(source)
    print("ONE MORE SHIVA REBUILD AUDIT PASSED")


if __name__ == "__main__":
    main()
