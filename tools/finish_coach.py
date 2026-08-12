from pathlib import Path
import ast
p=Path(__file__).resolve().parents[1]/'app_core.py'
s=p.read_text(encoding='utf-8')
s=s.replace('render_season_hub(players,load_weekly,weekly_for_player,espn_ppr)','render_season_hub(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)',1)
p.write_text(s,encoding='utf-8')
ast.parse(s)
assert 'render_season_hub(players,load_weekly,weekly_for_player,espn_ppr,weekly_name_col)' in s
print('SHIVA COACH FINAL WIRING PASSED')
