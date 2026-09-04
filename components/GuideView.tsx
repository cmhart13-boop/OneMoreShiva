'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  JOEL_GUIDE_EMBED,
  JOEL_GUIDE_LINK,
  chartViews,
  favoriteStats,
  featuredPlayers,
  guideHubs,
  positionViews,
  rbVolumeNotes,
  strategyPositionNotes,
  strategyRounds,
  strategyRules,
} from '../lib/guide'
import { PlayerAvatar, PlayerDetailOverlay, playerHeadshotUrl, type PlayerDetailData } from './PlayerMedia'
import type { Player } from '../lib/types'

type Hub = typeof guideHubs[number]['id']
type PositionId = typeof positionViews[number]['id']
type ChartId = typeof chartViews[number]['id']

function SourcePage({ page, title }: { page: number; title: string }) {
  return <section className="joel-source-card">
    <div className="joel-source-heading">
      <div><span>ORIGINAL JOEL SMYTH SOURCE</span><h3>{title}</h3></div>
      <a href={`${JOEL_GUIDE_LINK}#page=${page}`} target="_blank" rel="noreferrer">Open full-size ↗</a>
    </div>
    <div className="joel-source-frame" aria-label={`${title}, page ${page}`}>
      <iframe src={`${JOEL_GUIDE_EMBED}#page=${page}`} title={`${title} — Joel Smyth Draft Guide page ${page}`} loading="lazy" />
    </div>
    <p className="joel-source-help">Swipe inside the source viewer and use its zoom controls. Joel’s original colors, labels and table layout are intentionally preserved.</p>
  </section>
}

function HubPills({ active, onSelect }: { active: Hub | null; onSelect: (hub: Hub) => void }) {
  return <div className="guide-topic-pills" aria-label="2026 Draft Guide topics">
    {guideHubs.map((hub) => <button key={hub.id} type="button" className={active === hub.id ? 'active' : ''} onClick={() => onSelect(hub.id)}>{hub.title}</button>)}
  </div>
}

export default function GuideView() {
  const [hub, setHub] = useState<Hub | null>(null)
  const [chartId, setChartId] = useState<ChartId>('qb-volume')
  const [position, setPosition] = useState<PositionId>('QB')
  const [players, setPlayers] = useState<Player[]>([])
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerDetailData | null>(null)

  useEffect(() => {
    fetch('/api/rankings').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([]))
  }, [])

  const selectedChart = useMemo(() => chartViews.find((item) => item.id === chartId) || chartViews[0], [chartId])
  const selectedPosition = useMemo(() => positionViews.find((item) => item.id === position) || positionViews[0], [position])
  const findPlayer = (name: string) => players.find((item) => item.name.toLowerCase() === name.toLowerCase())
  const openPlayer = (player?: Player) => player && setSelectedPlayer({ ...player, id: player.espnId || player.id })
  const heroAllen = findPlayer('Josh Allen')
  const heroGibbs = findPlayer('Jahmyr Gibbs')

  if (!hub) return <>
    <section className="draft-guide-hero">
      <div className="draft-guide-hero-copy"><span>2026</span><h1>Shiva’s Draft Guide</h1><p>JOEL SMYTH SOURCE INTELLIGENCE · FULL PPR</p></div>
      <div className="draft-guide-players" aria-hidden="true">
        <img src={playerHeadshotUrl(heroAllen?.espnId || heroAllen?.id || '3918298', true)} alt="" />
        <img src={playerHeadshotUrl(heroGibbs?.espnId || heroGibbs?.id || '4429795', true)} alt="" />
      </div>
    </section>
    <p className="guide-source-intro">Organized by topic instead of PDF page. The same research can appear in more than one relevant section so you can browse by subject or by position without losing context.</p>
    <HubPills active={null} onSelect={setHub} />
    <div className="guide-hub-grid">{guideHubs.map((item) => <button key={item.id} type="button" className="guide-hub-card" onClick={() => setHub(item.id)}><h2>{item.title}</h2><p>{item.desc}</p><span>Open →</span></button>)}</div>
  </>

  return <>
    <div className="guide-sticky-nav">
      <button className="back-link" onClick={() => setHub(null)}>← Guide contents</button>
      <HubPills active={hub} onSelect={setHub} />
    </div>

    {hub === 'big-board' && <>
      <div className="section-kicker">FULL PPR</div><h1>2026 PPR Big Board</h1>
      <p className="lede">The complete source board is kept in Joel’s original layout so all ranking color cues remain intact.</p>
      <SourcePage page={4} title="PPR Big Board — all 150 players" />
    </>}

    {hub === 'strategy' && <>
      <div className="section-kicker">12-TEAM PPR</div><h1>Draft Strategy</h1>
      <p className="lede">The source page stays intact below, while Shiva separates its rules into quick-reading layers.</p>
      <div className="guide-rule-list">{strategyRules.map((rule, index) => <article key={rule}><b>{index + 1}</b><p>{rule}</p></article>)}</div>
      <div className="strategy-grid guide-position-strategy">{strategyPositionNotes.map((item) => <article className="panel" key={item.pos}><span className="eyebrow">{item.pos}</span><h2>{item.title}</h2><p>{item.body}</p></article>)}</div>
      <div className="round-plan guide-round-plan">{strategyRounds.map(([round, target]) => <div key={round}><b>{round}</b><p>{target}</p></div>)}</div>
      <SourcePage page={11} title="My Draft Strategy" />
    </>}

    {hub === 'charts' && <>
      <div className="section-kicker">RESEARCH CHARTS</div><h1>Charts</h1>
      <p className="lede">All chart topics live here, and the same chart is also surfaced inside its relevant position tab.</p>
      <div className="guide-chart-pills">{chartViews.map((chart) => <button type="button" key={chart.id} className={chartId === chart.id ? 'active' : ''} onClick={() => setChartId(chart.id)}>{chart.title}</button>)}</div>
      <article className="guide-chart-note"><div><span>{selectedChart.tags.join(' · ')}</span><h2>{selectedChart.title}</h2></div><p>{selectedChart.body}</p></article>
      <SourcePage page={selectedChart.page} title={`Charts of 2026 — ${selectedChart.title}`} />
    </>}

    {hub === 'positions' && <>
      <div className="section-kicker">POSITION DATA</div><h1>Position Data</h1>
      <div className="guide-chart-pills position-data-tabs">{positionViews.map((item) => <button type="button" key={item.id} className={position === item.id ? 'active' : ''} onClick={() => setPosition(item.id)}>{item.title}</button>)}</div>
      {selectedPosition.chartIds.length > 0 && <div className="position-related"><span>Also filed under {selectedPosition.title}</span><div>{selectedPosition.chartIds.map((id) => { const chart = chartViews.find((item) => item.id === id); return chart ? <button key={id} type="button" onClick={() => { setHub('charts'); setChartId(id as ChartId) }}>{chart.title} →</button> : null })}</div></div>}
      {selectedPosition.pages.map((page, index) => <SourcePage key={`${selectedPosition.id}-${page}`} page={page} title={index === 0 ? `${selectedPosition.title} rankings / source table` : `${selectedPosition.title} adjusted 2025 PPG`} />)}
    </>}

    {hub === 'playcallers' && <>
      <div className="section-kicker">COACHING ENVIRONMENT</div><h1>Playcallers</h1>
      <article className="guide-chart-note source-color-note"><div><span>KEEP JOEL’S COLORS</span><h2>The table is the analysis.</h2></div><p>Yellow identifies a new team. Pink identifies a first-time playcaller. The green-to-red rank shading is intentionally untouched because the color pattern communicates quality at a glance.</p></article>
      <SourcePage page={15} title="Playcaller Table" />
    </>}

    {hub === 'favorite-stats' && <>
      <div className="section-kicker">SOURCE NUGGETS</div><h1>20 Favorite Stats</h1>
      <p className="lede">Twenty high-value facts from Joel’s Top 50. The luck-metric item is intentionally excluded and replaced with the next source stat so this section still contains 20.</p>
      <div className="favorite-stat-list">{favoriteStats.map(([rank, title, body], index) => <article key={rank}><div><span>{index + 1}</span><small>Joel #{rank}</small></div><section><h2>{title}</h2><p>{body}</p></section></article>)}</div>
      <SourcePage page={19} title="Top 50 Stats — 50 through 26" />
      <SourcePage page={20} title="Top 50 Stats — 25 through 1" />
    </>}

    {hub === 'rb-volume' && <>
      <div className="section-kicker">RUNNING BACKS</div><h1>RB Volume</h1>
      <div className="guide-rule-list">{rbVolumeNotes.map((note, index) => <article key={note}><b>{index + 1}</b><p>{note}</p></article>)}</div>
      <button type="button" className="cross-topic-button" onClick={() => { setHub('charts'); setChartId('rb-efficiency') }}>Open RB Efficiency chart →</button>
      <SourcePage page={17} title="RB Volume source status + RB’s Dream QB chart" />
    </>}

    {hub === 'gold-mine' && <>
      <div className="section-kicker">TARGET SIGNALS</div><h1>Gold Mine</h1>
      <p className="lede">A fast visual pass through Joel’s source markings. Green is Target, yellow is I’ll Pass, red is Avoiding. Shiva does not recolor or reinterpret those labels.</p>
      <div className="gold-mine-key"><span className="target">Target</span><span className="pass">I’ll Pass</span><span className="avoid">Avoiding</span></div>
      <SourcePage page={5} title="PPR Positional Rankings — Joel’s target / pass / avoid colors" />
    </>}

    {hub === 'players' && <>
      <div className="section-kicker">PLAYER SHORTCUTS</div><h1>Player Cards</h1><p className="lede">Quick access to players repeatedly referenced throughout the guide.</p>
      <div className="player-card-grid">{featuredPlayers.map((name) => { const player = findPlayer(name); return <button type="button" className="player-card clickable-player" key={name} onClick={() => openPlayer(player)}><div className="player-inline"><PlayerAvatar playerId={player?.espnId || player?.id} name={name} /><span className="board-position">{player?.pos || '—'}</span></div><h2>{name}</h2><p>{player ? `${player.team} · Overall ${player.rank < 10000 ? `#${player.rank}` : '—'} · ADP ${player.adp?.toFixed(1) ?? '—'}` : 'Guide research target'}</p></button> })}</div>
    </>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </>
}
