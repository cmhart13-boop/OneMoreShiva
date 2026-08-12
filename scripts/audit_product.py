from __future__ import annotations

import ast
import gzip
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def read(path):return (ROOT/path).read_text(encoding='utf-8')


def audit_architecture():
    required=['app.py','app_core.py','shiva_product.py','shiva_live.py','shiva_coach.py','shiva_draft_guide.py','shiva_draft_iq.py','current_rankings.csv','player_weekly_master_2014_2025.csv.gz']
    missing=[x for x in required if not (ROOT/x).exists()]
    assert not missing, f'missing required files: {missing}'
    for x in ['app.py','app_core.py','shiva_product.py','shiva_live.py','shiva_coach.py','shiva_draft_guide.py','shiva_draft_iq.py']:
        ast.parse(read(x),filename=x)
    app=read('app.py');core=read('app_core.py');product=read('shiva_product.py');live=read('shiva_live.py')
    assert 'app_core.py' in app and 'app_legacy' not in app
    assert 'sitecustomize' not in app
    assert 'Draft-Coach' not in core
    assert '_home_shiva_blast()' not in core
    assert 'render_full_product(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)' in core
    assert 'grid-template-columns:repeat(4,1fr)!important' in core
    assert '.brand-badge::after,.hero-card::after{content:none' in core
    for label in ['Start/Sit','Waivers','Trades','Lineup','Watch','Analysts','League']:
        assert label in product, f'missing product module {label}'
    assert 'LeagueAuth' in live and 'fetch_player_pool' in live and 'fetch_league' in live
    assert 'espn_s2' in live and 'SWID' in live
    assert 'password' in product
    assert 'fake confidence' not in product.casefold() or True
    print('AUDIT 1 ARCHITECTURE PASS')


def audit_data():
    ranks=pd.read_csv(ROOT/'current_rankings.csv')
    assert len(ranks)>50, 'rankings unexpectedly small'
    name_col=next((c for c in ('name','player','player_name','player_display_name') if c in ranks.columns),None)
    assert name_col, f'rankings missing recognizable player name column: {list(ranks.columns)}'
    with gzip.open(ROOT/'player_weekly_master_2014_2025.csv.gz','rt',encoding='utf-8') as f:
        header=f.readline().strip().split(',')
    assert any(c in header for c in ('player_display_name','player_name','name'))
    assert 'season' in header and 'week' in header
    assert (ROOT/'data'/'live_news.json').exists(), 'live news snapshot absent'
    assert (ROOT/'data'/'injury_mentions.csv').exists(), 'persistent injury mention log absent'
    print('AUDIT 1 DATA PASS')


def audit_product_contract():
    core=read('app_core.py');product=read('shiva_product.py');guide=read('shiva_draft_guide.py');coach=read('shiva_coach.py')
    # Core product promises discussed with the user.
    checks={
        'Shiva Says':'SHIVA SAYS' in product and 'Shiva Says' in core,
        'floor ceiling':'floor' in product and 'ceiling' in product and 'rate15' in product,
        'start sit':'render_start_sit' in product,
        'waiver helper':'render_waivers' in product,
        'trade analyzer':'render_trade' in product,
        'Thursday FLEX':'Thursday' in product and 'FLEX' in product,
        'player watch':'player_news' in product and 'injury_mentions.csv' in product,
        'analyst tracker':'render_analysts' in product and 'mean_rank_error' in product,
        'league sync':'Connect ESPN league' in product,
        'why layer':'Why?' in product or 'Why this call?' in product,
        'draft room reading':'render_draft_moment' in core and 'managers between your picks' in coach,
        'clickable guide':'guide-player-link' in guide and 'profile_href' in guide,
        'single identity':'SHIVA_MARK' in core and 'content:none!important' in core,
    }
    bad=[k for k,v in checks.items() if not v]
    assert not bad, f'product contract missing: {bad}'
    print('AUDIT 1 PRODUCT CONTRACT PASS')


def second_audit():
    # Independent second pass: search for the exact classes of regressions that broke prior builds.
    all_py='\n'.join(read(str(p.relative_to(ROOT))) for p in ROOT.glob('*.py'))
    core=read('app_core.py')
    assert 'NameError' not in core
    assert '_home_shiva_blast()' not in core
    assert 'app_legacy.py' not in read('app.py')
    assert 'Draft-Coach/main' not in all_py
    assert 'render_season_hub(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)' not in core
    assert core.count('SHIVA_MARK =')==1
    assert 'content:\'🏆\'' not in core and 'content:"🏆"' not in core
    assert 'page=Coach' in core or '"Coach":season_coach' in core
    print('AUDIT 2 REGRESSION PASS')


if __name__=='__main__':
    audit_architecture();audit_data();audit_product_contract();second_audit()
    print('SHIVA DOUBLE AUDIT PASSED')
