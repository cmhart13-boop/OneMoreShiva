#!/usr/bin/env python3
import csv, gzip, json, math, statistics
from collections import defaultdict
from pathlib import Path

SRC = Path('player_weekly_master_2014_2025.csv.gz')
OUTDIR = Path('analysis_output')
OUTDIR.mkdir(exist_ok=True)

NUM_FIELDS = [
    'carries','receptions','rushing_yards','rushing_tds','receiving_yards','receiving_tds',
    'passing_yards','passing_tds','passing_interceptions','passing_2pt_conversions',
    'rushing_2pt_conversions','receiving_2pt_conversions','fumbles_lost_total',
    'fumble_recovery_tds','special_teams_tds'
]

def fnum(v):
    try:
        if v is None or v == '': return 0.0
        return float(v)
    except Exception:
        return 0.0

def pearson(xs, ys):
    n=len(xs)
    if n<2:return None
    mx=sum(xs)/n; my=sum(ys)/n
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx=sum((x-mx)**2 for x in xs); dy=sum((y-my)**2 for y in ys)
    return num/math.sqrt(dx*dy) if dx>0 and dy>0 else None

def ranks(vals):
    order=sorted(range(len(vals)), key=lambda i: vals[i])
    out=[0.0]*len(vals); i=0
    while i<len(order):
        j=i+1
        while j<len(order) and vals[order[j]]==vals[order[i]]: j+=1
        r=(i+1+j)/2.0
        for k in range(i,j): out[order[k]]=r
        i=j
    return out

def spearman(xs,ys):
    return pearson(ranks(xs),ranks(ys)) if len(xs)>=2 else None

def mean(vals): return sum(vals)/len(vals) if vals else None

def median(vals): return statistics.median(vals) if vals else None

def pct(v): return round(v,6) if v is not None else None

agg={}
with gzip.open(SRC,'rt',newline='',encoding='utf-8-sig') as f:
    rdr=csv.DictReader(f)
    for row in rdr:
        if row.get('season_type') != 'REG' or row.get('position') != 'RB':
            continue
        pid=(row.get('player_id') or '').strip()
        if not pid or pid in {'0','0.0','nan'}: continue
        try: season=int(float(row.get('season','0') or 0))
        except: continue
        if season<2014 or season>2025: continue
        key=(pid,season)
        if key not in agg:
            agg[key]={
                'player_id':pid,'season':season,
                'player':(row.get('player_display_name') or row.get('player_name') or '').strip(),
                'teams':[], 'weeks':set(),
                **{k:0.0 for k in NUM_FIELDS}
            }
        a=agg[key]
        nm=(row.get('player_display_name') or row.get('player_name') or '').strip()
        if nm: a['player']=nm
        team=(row.get('team') or row.get('recent_team') or '').strip()
        if team and team not in a['teams']: a['teams'].append(team)
        wk=row.get('week')
        try: a['weeks'].add(int(float(wk)))
        except: pass
        for fld in NUM_FIELDS: a[fld]+=fnum(row.get(fld))

# derive player-seasons
seasons={}
for key,a in agg.items():
    touches=a['carries']+a['receptions']
    # ESPN-style standard Full PPR scoring for RBs, reconstructed from raw weekly stats.
    ppr=(
        a['passing_yards']*0.04 + a['passing_tds']*4 - a['passing_interceptions']*2
        + a['rushing_yards']*0.1 + a['rushing_tds']*6
        + a['receptions'] + a['receiving_yards']*0.1 + a['receiving_tds']*6
        + (a['passing_2pt_conversions']+a['rushing_2pt_conversions']+a['receiving_2pt_conversions'])*2
        - a['fumbles_lost_total']*2 + a['fumble_recovery_tds']*6 + a['special_teams_tds']*6
    )
    games=len(a['weeks'])
    seasons[key]={
        'player_id':a['player_id'],'player':a['player'],'season':a['season'],
        'team':'/'.join(a['teams']), 'carries':round(a['carries'],1),'receptions':round(a['receptions'],1),
        'touches':round(touches,1),'ppr_points':round(ppr,2),'games':games,
        'ppr_ppg':round(ppr/games,3) if games else 0.0,
    }

pairs=[]
for (pid,season),cur in seasons.items():
    if season>2024 or cur['touches']<200: continue
    nxt=seasons.get((pid,season+1))
    if nxt:
        ng=nxt['games']; np=nxt['ppr_points']; nppg=nxt['ppr_ppg']; nt=nxt['touches']; nteam=nxt['team']
        absent=0
    else:
        ng=0; np=0.0; nppg=0.0; nt=0.0; nteam=''; absent=1
    retention=nppg/cur['ppr_ppg'] if cur['ppr_ppg']>0 else 0.0
    severe=int(nppg < cur['ppr_ppg']*0.70)
    improved=int(nppg >= cur['ppr_ppg'])
    pairs.append({
        'season':season,'player_id':pid,'player':cur['player'],'team':cur['team'],
        'carries':cur['carries'],'receptions':cur['receptions'],'touches':cur['touches'],
        'prior_ppr_points':cur['ppr_points'],'prior_games':cur['games'],'prior_ppr_ppg':cur['ppr_ppg'],
        'next_season':season+1,'next_team':nteam,'next_touches':nt,'next_ppr_points':np,
        'next_games':ng,'next_ppr_ppg':nppg,'ppg_retention':round(retention,6),
        'absent_next_year':absent,'severe_decline_30pct':severe,'retained_or_improved':improved
    })
pairs.sort(key=lambda r:(r['season'],-r['touches'],r['player']))

# touch buckets
bucket_defs=[(200,224),(225,249),(250,274),(275,299),(300,324),(325,349),(350,374),(375,399),(400,999)]
buckets=[]
for lo,hi in bucket_defs:
    rows=[r for r in pairs if lo<=r['touches']<=hi]
    if not rows: continue
    label=f'{lo}-{hi}' if hi<999 else '400+'
    buckets.append({
        'touch_bucket':label,'min_touches':lo,'max_touches':None if hi==999 else hi,'n':len(rows),
        'avg_prior_touches':round(mean([r['touches'] for r in rows]),2),
        'avg_prior_ppr_ppg':round(mean([r['prior_ppr_ppg'] for r in rows]),3),
        'avg_next_ppr_ppg':round(mean([r['next_ppr_ppg'] for r in rows]),3),
        'median_next_ppr_ppg':round(median([r['next_ppr_ppg'] for r in rows]),3),
        'avg_next_games':round(mean([r['next_games'] for r in rows]),2),
        'avg_next_touches':round(mean([r['next_touches'] for r in rows]),2),
        'avg_ppg_retention':round(mean([r['ppg_retention'] for r in rows]),4),
        'absent_rate':round(mean([r['absent_next_year'] for r in rows]),4),
        'severe_decline_rate':round(mean([r['severe_decline_30pct'] for r in rows]),4),
        'retain_or_improve_rate':round(mean([r['retained_or_improved'] for r in rows]),4),
    })

# threshold scan
thresholds=[]
for t in range(250,401,5):
    low=[r for r in pairs if 200<=r['touches']<t]
    high=[r for r in pairs if r['touches']>=t]
    if not low or not high: continue
    def sm(rows):
        return {
            'n':len(rows),'avg_next_ppg':mean([r['next_ppr_ppg'] for r in rows]),
            'avg_retention':mean([r['ppg_retention'] for r in rows]),
            'absent_rate':mean([r['absent_next_year'] for r in rows]),
            'severe_rate':mean([r['severe_decline_30pct'] for r in rows]),
            'improve_rate':mean([r['retained_or_improved'] for r in rows]),
        }
    l=sm(low); h=sm(high)
    score=(l['avg_retention']-h['avg_retention']) + 0.5*(h['severe_rate']-l['severe_rate']) + 0.5*(h['absent_rate']-l['absent_rate'])
    thresholds.append({
        'threshold':t,'low_n':l['n'],'high_n':h['n'],
        'low_avg_next_ppg':round(l['avg_next_ppg'],3),'high_avg_next_ppg':round(h['avg_next_ppg'],3),
        'next_ppg_delta_high_minus_low':round(h['avg_next_ppg']-l['avg_next_ppg'],3),
        'low_avg_retention':round(l['avg_retention'],4),'high_avg_retention':round(h['avg_retention'],4),
        'retention_delta_high_minus_low':round(h['avg_retention']-l['avg_retention'],4),
        'low_absent_rate':round(l['absent_rate'],4),'high_absent_rate':round(h['absent_rate'],4),
        'absent_rate_delta':round(h['absent_rate']-l['absent_rate'],4),
        'low_severe_decline_rate':round(l['severe_rate'],4),'high_severe_decline_rate':round(h['severe_rate'],4),
        'severe_decline_delta':round(h['severe_rate']-l['severe_rate'],4),
        'high_retain_or_improve_rate':round(h['improve_rate'],4),'risk_score':round(score,5)
    })

eligible=[r for r in thresholds if r['high_n']>=15 and r['low_n']>=30]
# Prefer earliest meaningful risk step; otherwise highest composite risk score with adequate sample.
meaningful=[r for r in eligible if r['retention_delta_high_minus_low']<=-0.10 and r['severe_decline_delta']>=0.10]
if meaningful:
    chosen=min(meaningful,key=lambda r:r['threshold'])
elif eligible:
    chosen=max(eligible,key=lambda r:r['risk_score'])
else:
    chosen=max(thresholds,key=lambda r:r['risk_score']) if thresholds else None

xs=[r['touches'] for r in pairs]
nextppg=[r['next_ppr_ppg'] for r in pairs]
ret=[r['ppg_retention'] for r in pairs]
ng=[r['next_games'] for r in pairs]
summary={
    'objective':'Measure correlation between RB regular-season touches (carries + receptions) and following-season performance, and identify where the curve turns negative.',
    'source':'player_weekly_master_2014_2025.csv.gz in OneMoreShiva repository; validated coverage audit in File Library.',
    'exposure_seasons':'2014-2024','outcome_seasons':'2015-2025','minimum_touches':200,
    'sample_player_seasons':len(pairs),
    'pearson_touches_vs_next_ppg':pct(pearson(xs,nextppg)),
    'spearman_touches_vs_next_ppg':pct(spearman(xs,nextppg)),
    'pearson_touches_vs_ppg_retention':pct(pearson(xs,ret)),
    'spearman_touches_vs_ppg_retention':pct(spearman(xs,ret)),
    'pearson_touches_vs_next_games':pct(pearson(xs,ng)),
    'selected_tripwire':chosen,
    'scoring_note':'ESPN-style Full PPR reconstructed from raw passing/rushing/receiving/2PT/fumble-lost/fumble-recovery-TD/special-teams-TD fields. Absent next season is scored as 0 games, 0 points, 0 PPG.',
    'classification_note':'Exploratory correlation, not causal proof. Threshold selection requires >=15 high-side observations and >=30 low-side observations where possible.'
}

with open(OUTDIR/'rb_touch_summary.json','w',encoding='utf-8') as f: json.dump({'summary':summary,'buckets':buckets,'thresholds':thresholds},f,indent=2)
with open(OUTDIR/'rb_touch_player_seasons.csv','w',newline='',encoding='utf-8') as f:
    fields=list(pairs[0].keys()) if pairs else []
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(pairs)
print(json.dumps(summary,indent=2))
