#!/usr/bin/env python3
import csv, json
from pathlib import Path
p=Path('analysis_output')
obj=json.loads((p/'rb_touch_summary.json').read_text())
for name,key in [('rb_touch_buckets.csv','buckets'),('rb_touch_thresholds.csv','thresholds')]:
    rows=obj[key]
    if rows:
        with (p/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with (p/'rb_touch_player_seasons.csv').open(newline='',encoding='utf-8') as src:
    rows=list(csv.DictReader(src))
high=[r for r in rows if float(r['touches'])>=325]
with (p/'rb_touch_high_workload_cases.csv').open('w',newline='',encoding='utf-8') as f:
    if high:
        w=csv.DictWriter(f,fieldnames=list(high[0].keys())); w.writeheader(); w.writerows(high)
print(f'wrote {len(high)} high-workload cases')
