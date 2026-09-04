export const JOEL_GUIDE_FILE_ID = '1PqSzx9qlKZAFy5oFyHHGyFxo18iaGeei'
export const JOEL_GUIDE_EMBED = `https://drive.google.com/file/d/${JOEL_GUIDE_FILE_ID}/preview`
export const JOEL_GUIDE_LINK = `https://drive.google.com/file/d/${JOEL_GUIDE_FILE_ID}/view?usp=sharing`

export const guideHubs = [
  { id: 'big-board', title: 'PPR Big Board', desc: 'Full 150-player PPR board' },
  { id: 'strategy', title: 'Draft Strategy', desc: 'Overall rules + round-by-round build' },
  { id: 'charts', title: 'Charts', desc: 'All 2026 research charts in one place' },
  { id: 'positions', title: 'Position Data', desc: 'QB · RB · WR · TE · D/ST · K · OL' },
  { id: 'playcallers', title: 'Playcallers', desc: 'Original color-coded coaching tables' },
  { id: 'favorite-stats', title: '20 Favorite Stats', desc: 'Top source nuggets, luck metric excluded' },
  { id: 'rb-volume', title: 'RB Volume', desc: 'Volume signals + source context' },
  { id: 'gold-mine', title: 'Gold Mine', desc: 'Joel’s green target signals at a glance' },
  { id: 'players', title: 'Player Cards', desc: 'Quick player-profile shortcuts' },
] as const

export const strategyPositionNotes = [
  { pos: 'QB', title: 'Wait for the value pocket', body: 'Main target is roughly QB7-11 by ADP, often still available around Round 8. A late rushing QB is the secondary plan. Joel notes QB3-6 are going later this year, so a major fall can still be worth taking.' },
  { pos: 'RB', title: 'Build the early ceiling', body: 'Main target is three RBs inside roughly the top 25-30. RB/RB is a preferred start when the board cooperates because elite league-winning RB seasons overwhelmingly come from Rounds 1-2.' },
  { pos: 'WR', title: 'Attack Rounds 3 and 5', body: 'Joel prefers the Round 3 and Round 5 WR ranges over many comparable RBs. Late WR is also the ideal place to chase upside.' },
  { pos: 'TE', title: 'Best value, not forced value', body: 'All TE ranges can work. TE2-4 is viable when no RB/WR stands out; Round 7-8 is a good mid-round pocket; a strategic full punt is also acceptable.' },
] as const

export const strategyRules = [
  'Do not draft rankings 1-for-1. Use ADP to capture value instead of paying your ranking early.',
  'Do not make “beat ADP” the goal. Prefer the riskier player with a path to real ceiling over a safe RB30 who finishes RB29.',
  'No kicker or D/ST until the final two rounds unless your room forces something unusual.',
  'Late-round process profiles: rookie WRs, rushing QBs, talent on top offenses, and clear RB2/handcuff roles.',
  'Balance risk. Avoid stacking too many fragile or uncertain profiles on the same roster.',
  'Early waivers and even post-draft waivers matter more than they will later in the season.',
] as const

export const strategyRounds = [
  ['Round 1', 'RB'], ['Round 2', 'RB'], ['Round 3', 'WR'], ['Round 4', 'Best player available'],
  ['Round 5', 'WR'], ['Round 6', 'Best player available'], ['Round 7', 'Best player available'],
  ['Round 8', 'QB'], ['Round 9', 'Upside WR'], ['Round 10', 'Punt TE'], ['Round 11', 'Top handcuff'],
  ['Round 12', 'Upside QB'], ['Round 13', 'Favorite deep sleeper'], ['Round 14', 'D/ST'],
  ['Round 15', 'Kicker / IR player'],
] as const

export const chartViews = [
  { id: 'qb-volume', title: 'QB Volume', page: 16, tags: ['QB', 'Charts'], body: 'Compares projected QB volume rank with ADP. Joel’s rule: above the line identifies value; volume is more predictable than QB play and helps uncover late-round hits.' },
  { id: 'rb-efficiency', title: 'RB Efficiency', page: 16, tags: ['RB', 'Charts'], body: 'Rushing efficiency blends yards over expected, elusiveness and YAC after clean blocking; receiving efficiency blends yards per route and targets per route. Bubble size represents volume.' },
  { id: 'wr-efficiency', title: 'WR Efficiency', page: 16, tags: ['WR', 'Charts'], body: 'Uses first downs per route and adjusted yards per route. Joel flags first downs per route as a surprisingly strong predictor of future success.' },
  { id: 'qb-rushing', title: 'QB Rushing', page: 17, tags: ['QB', 'Charts'], body: 'Rushing is both highly valuable and sticky year to year. Designed runs are more consistent and carry extra value near the goal line.' },
  { id: 'fantasy-shootout', title: 'Fantasy Shootout', page: 17, tags: ['QB', 'RB', 'WR', 'TE', 'Charts'], body: 'Compares projected scoring offense with projected scoring defense to identify environments that can create fantasy shootouts or passing-heavy game scripts.' },
  { id: 'rb-dream-qb', title: "RB's Dream QB", page: 17, tags: ['RB', 'QB', 'Charts'], body: 'Shows the quarterback styles that create RB-friendly goal-line and checkdown environments. Joel uses Jared Goff as the example of a QB who rarely steals goal-line work and checks down often.' },
  { id: 'rb-volume', title: 'RB Volume', page: 17, tags: ['RB', 'Charts'], body: 'Joel marks the full RB Volume chart as coming soon on this source page. Shiva preserves that source status and pairs it with the guide’s volume findings rather than fabricating a missing chart.' },
] as const

export const positionViews = [
  { id: 'QB', title: 'QB', pages: [5, 12], chartIds: ['qb-volume', 'qb-rushing', 'fantasy-shootout'] },
  { id: 'RB', title: 'RB', pages: [5, 13], chartIds: ['rb-efficiency', 'rb-dream-qb', 'fantasy-shootout', 'rb-volume'] },
  { id: 'WR', title: 'WR', pages: [5, 13], chartIds: ['wr-efficiency', 'fantasy-shootout'] },
  { id: 'TE', title: 'TE', pages: [5, 12], chartIds: ['fantasy-shootout'] },
  { id: 'DST', title: 'D/ST', pages: [9], chartIds: [] },
  { id: 'K', title: 'Kicker', pages: [10], chartIds: [] },
  { id: 'OL', title: 'OL', pages: [14], chartIds: [] },
] as const

export const favoriteStats = [
  ['1', 'Draft-capital RB hit rate', 'Of the first 11 RBs selected top-25 in the NFL Draft since 2015, all 11 produced an RB1 fantasy season by Year 2. Jeanty and Hampton can extend that trend.'],
  ['2', 'Brian Thomas Jr. early CB gauntlet', 'His first eight-week cornerback schedule runs through a brutal group that includes Denzel Ward, Patrick Surtain, Christian Gonzalez, DJ Turner, Quinyon Mitchell, Derek Stingley and Sauce Gardner.'],
  ['3', 'Drake Maye fourth-quarter split', 'Maye was QB1 over quarters 1-3 last season but QB32 in fourth quarters. A less dominant New England game script can preserve late-game volume.'],
  ['5', 'Ladd McConkey + motion', 'McConkey’s yards per route rise 96% with motion. Mike McDaniel runs more motion than any offense, creating an obvious usage signal.'],
  ['6', 'Josh Allen’s six-year floor', 'Allen has finished top-two in fantasy points among quarterbacks in each of the last six seasons; nobody else has done it twice in that span.'],
  ['7', 'Rushing QB hit rate', 'Since 2015, passing-oriented QBs drafted in Rounds 2-5 have hit at 31%; rushing QBs are at 63%, while Josh Allen sits at 100%.'],
  ['8', 'Jaylen Warren receiving profile', 'Warren ranked top-two among RBs in targets per route, yards per route and missed tackles per reception in 2025. Pittsburgh also has 82 vacated RB targets.'],
  ['9', 'Achane receiving split', 'De’Von Achane averages 11.4 receiving PPG with Tua Tagovailoa and 3.4 across eight games without him.'],
  ['10', 'Josh McDaniels backfield tendency', 'Across 19 years as an OC/HC, McDaniels has given his RB1 at least 60% of team RB touches only five times; only three backs cleared 15 PPR PPG.'],
  ['11', 'Zac Taylor RB1 streak', 'Counting Chase Brown’s 2024 starts, Zac Taylor has produced a fantasy RB1 in each of his last six seasons as Cincinnati’s head coach.'],
  ['12', 'Andy Reid RB environment', 'Kansas City ranked fifth in RB PPG from 2014-2023 before falling to 29th over the last two seasons.'],
  ['13', 'Jadarian Price pass protection', 'Price carried a 38.5 college pass-blocking grade. Joel flags protection as a possible barrier to passing-down work.'],
  ['14', 'Jahmyr Gibbs scheme split', 'Gibbs ranked second in yards per attempt on gap concepts and 42nd on zone concepts in 2025. James Conner led the league in gap rate under Drew Petzing in 2024.'],
  ['15', 'Emeka Egbuka schedule reversal', 'Egbuka was the only WR to face a top-five fantasy WR defense five times without seeing a single bottom-five WR defense in 2025.'],
  ['16', 'Lamar dropped-TD upside', 'Lamar Jackson had five touchdowns dropped in 2025, most in the NFL, despite finishing last in pass attempts per game and playing only 13 games.'],
  ['17', 'Top-12 NFL Draft RB Year-2 ceiling', 'Before Ashton Jeanty, only CMC and Bijan among recent top-12 drafted RBs failed to reach 15+ PPG as rookies; both jumped to top-three RB finishes in Year 2.'],
  ['18', 'Davante end-zone regression flag', 'Davante Adams scored 7.9 PPG on end-zone targets in 2025, the highest mark since 2007 Randy Moss; Moss fell to 3.1 the following year.'],
  ['19', 'Slot WRs moving outside', 'DeVonta Smith, Luther Burden and Ladd McConkey were all far better in yards per route outside the slot and are expected to play more outside in 2026.'],
  ['20', '20+ PPG RBs come early', 'Over the last 10 years, only 2 of 33 RBs drafted in the first four fantasy rounds who reached 20+ PPG came from Rounds 3-4, versus 7 of 30 WRs.'],
  ['21', 'Cam Ward Year-2 precedent', 'Trevor Lawrence and Jared Goff both went from bottom-four fantasy QBs as rookies to QB11 in Year 2. Ward enters Year 2 after the league’s hardest fantasy QB schedule.'],
] as const

export const rbVolumeNotes = [
  'In total RB volume (expected fantasy points), San Francisco, Detroit and Atlanta were the top three; Pittsburgh ranked fourth with multiple RBs in the top 24 in volume.',
  'Joel’s RB efficiency bubble chart uses bubble size as volume and explicitly warns that more volume can depress efficiency rankings.',
  'The draft strategy still prioritizes getting three RBs inside roughly the top 25-30 because the ceiling cluster is concentrated early.',
] as const

export const featuredPlayers = ['Jahmyr Gibbs','Bijan Robinson','Puka Nacua','Ja\'Marr Chase','Josh Allen','Drake Maye','Dalton Kincaid','Luther Burden III','CeeDee Lamb','Jaylen Warren']
