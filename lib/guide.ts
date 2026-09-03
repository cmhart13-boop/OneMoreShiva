export const guideSections = [
  { id: 'rankings', title: 'Rankings', desc: '2026 big board + positional rankings' },
  { id: 'strategy', title: 'Draft Strategy', desc: 'Round-by-round build and position rules' },
  { id: 'research', title: 'Research', desc: 'Research notes and clickable stat features' },
  { id: 'luck', title: 'Luck Metric', desc: 'How the guide frames 2025 luck' },
  { id: 'players', title: 'Player Cards', desc: 'Featured-player shortcuts into app profiles' },
] as const

export const researchArticles = [
  { id:'draft-capital-matters', title:'Draft capital matters', body:'Since 2015, the first 11 RBs selected top-25 in the NFL Draft all produced an RB1 fantasy season by Year 2. That puts major sophomore upside behind Ashton Jeanty and Omarion Hampton.', players:['Ashton Jeanty','Omarion Hampton'] },
  { id:'rb-ceiling-zone', title:'Rounds 1–2 are the RB ceiling zone', body:'Only 2 of 33 early-round RBs who reached 20+ PPR PPG came from Rounds 3–4. The preferred build starts RB/RB when the value is there and aims for three RBs inside roughly the top 25–30.', players:[] },
  { id:'chase-brown-environment', title:'Chase Brown environment', body:'Cincinnati QBs were the NFL’s top three in checkdown rate in 2025, and Zac Taylor has produced an RB1 in six straight seasons when Chase Brown’s 2024 starts are counted.', players:['Chase Brown'] },
  { id:'josh-allen-outlier', title:'Josh Allen is the outlier', body:'Allen has finished top-two at QB in fantasy points six straight seasons. The research also notes rushing QBs drafted in Rounds 2–5 have historically hit far more often than passing-only QBs.', players:['Josh Allen'] },
  { id:'puka-targets', title:'Puka earns targets at a different level', body:'Since 2024, Puka Nacua’s targets per route sit at 36.8%; no other qualified player is above 30%.', players:['Puka Nacua'] },
  { id:'kincaid-routes', title:'Dalton Kincaid: routes, not efficiency', body:'Kincaid led 2025 tight ends across a broad set of per-route efficiency measures. The unlock is simply getting him on more routes.', players:['Dalton Kincaid'] },
  { id:'parker-washington', title:'Parker Washington late value', body:'Over Jacksonville’s final four games, Washington produced 454 receiving yards despite Brian Thomas Jr. and Jakobi Meyers each running more routes.', players:['Parker Washington'] },
  { id:'luther-burden', title:'Luther Burden efficiency signal', body:'Burden ranked eighth among WRs in fantasy points per snap as a rookie; six of the seven players ahead of him were fantasy WR1s.', players:['Luther Burden III'] },
  { id:'ceedee-luck', title:'CeeDee regression candidate — upward', body:'The 25-factor luck model rated CeeDee Lamb the unluckiest player of 2025, estimating roughly 2.7 PPG lost to bad-luck events.', players:['CeeDee Lamb'] },
  { id:'achane-split', title:'Achane receiving split matters', body:'De’Von Achane has averaged 11.4 receiving PPG with Tua Tagovailoa in his career versus 3.4 in eight games without him.', players:['De’Von Achane'] },
  { id:'jaylen-warren', title:'Jaylen Warren receiving opportunity', body:'Warren ranked top-two among RBs in targets per route, yards per route and missed tackles per reception in 2025; Pittsburgh also has 82 vacated RB targets.', players:['Jaylen Warren'] },
  { id:'drake-maye', title:'Drake Maye game-script ceiling', body:'Maye was QB1 over quarters 1–3 last season but QB32 in fourth quarters. A less dominant Patriots game script could preserve more late-game passing and rushing volume.', players:['Drake Maye'] },
  { id:'rankings-vs-adp', title:'Do not blindly follow rankings', body:'Use rankings against ADP. If a player is ranked 62 but normally goes 85, the goal is to capture the value rather than drafting him at 62.', players:[] },
]

export const strategyRounds = [
  ['Rounds 1–2', 'Prioritize elite RB/WR ceiling. Do not force QB unless Josh Allen falls into a clear value pocket.'],
  ['Rounds 3–5', 'Finish the weekly RB/WR core. Elite TE and rushing-QB value can enter here.'],
  ['Rounds 6–9', 'Attack falling ADP, upside WRs, ambiguous backfields and breakout profiles.'],
  ['Rounds 10–12', 'Build bench ceiling. Quarterback or tight end can be finished if you waited.'],
  ['Late rounds', 'Defense and kicker last. Preserve upside roster spots for players whose roles can grow.'],
]

export const featuredPlayers = ['Jahmyr Gibbs','Bijan Robinson','Puka Nacua','Ja\'Marr Chase','Josh Allen','Drake Maye','Dalton Kincaid','Luther Burden III','CeeDee Lamb','Jaylen Warren']
