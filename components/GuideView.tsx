'use client'

import { useEffect, useMemo, useState } from 'react'
import {
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

type ChartAsset = { src?: string; alt: string }

const chartAssets: Record<ChartId, ChartAsset> = {
  'qb-volume': { src: '/guide/charts/qb-volume.jpg', alt: 'QB Volume graph' },
  'rb-efficiency': { src: '/guide/charts/rb-efficiency.webp', alt: 'RB Efficiency graph' },
  'wr-efficiency': { src: '/guide/charts/wr-efficiency.webp', alt: 'WR Efficiency graph' },
  'qb-rushing': { src: '/guide/charts/qb-rushing.webp', alt: 'QB Rushing graph' },
  'fantasy-shootout': { src: '/guide/charts/fantasy-shootout.webp', alt: 'Fantasy Shootout graph' },
  'rb-dream-qb': { src: '/guide/charts/rb-dream-qb.webp', alt: "An RB's Dream QB graph" },
  'rb-volume': { alt: 'RB Volume graph status' },
}

function shivaCopy(value: string) {
  return value
    .replace(/Joel Smyth’s/gi, 'Shiva’s')
    .replace(/Joel Smyth's/gi, 'Shiva’s')
    .replace(/Joel’s/gi, 'Shiva’s')
    .replace(/Joel's/gi, 'Shiva’s')
    .replace(/Joel/gi, 'Shiva')
}

function FullGuideLink({ page, label = 'Full Draft Guide PDF' }: { page?: number; label?: string }) {
  return <a className="guide-pdf-pill" href={`${JOEL_GUIDE_LINK}${page ? `#page=${page}` : ''}`} target="_blank" rel="noreferrer">{label} ↗</a>
}

function HubPills({ active, onSelect }: { active: Hub | null; onSelect: (hub: Hub) => void }) {
  return <div className="guide-topic-pills" aria-label="2026 Draft Guide topics">
    {guideHubs.map((item) => <button key={item.id} type="button" className={active === item.id ? 'active' : ''} onClick={() => onSelect(item.id)}>{item.title}</button>)}
    <FullGuideLink />
  </div>
}

export default function GuideView() {
  const [hub, setHub] = useState<Hub | null>(null)
  const [position, setPosition] = useState<PositionId>('QB')
  const [players, setPlayers] = useState<Player[]>([])
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerDetailData | null>(null)
  const [expandedChart, setExpandedChart] = useState<ChartId | null>(null)

  useEffect(() => {
    fetch('/api/rankings').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([]))
  }, [])

  const selectedPosition = useMemo(() => positionViews.find((item) => item.id === position) || positionViews[0], [position])
  const findPlayer = (name: string) => players.find((item) => item.name.toLowerCase() === name.toLowerCase())
  const openPlayer = (player?: Player) => player && setSelectedPlayer({ ...player, id: player.espnId || player.id })
  const heroAllen = findPlayer('Josh Allen')
  const heroGibbs = findPlayer('Jahmyr Gibbs')
  const expanded = expandedChart ? chartViews.find((item) => item.id === expandedChart) : null

  const chartGallery = (ids?: readonly string[]) => {
    const visible = ids ? chartViews.filter((chart) => ids.includes(chart.id)) : chartViews
    return <div className="guide-chart-gallery">
      {visible.map((chart) => {
        const asset = chartAssets[chart.id as ChartId]
        const available = Boolean(asset?.src)
        return <article className={`guide-chart-card${available ? '' : ' chart-coming-soon'}`} key={chart.id}>
          {available ? <button type="button" className="guide-chart-image-button" onClick={() => setExpandedChart(chart.id as ChartId)} aria-label={`Expand ${chart.title}`}>
            <img src={asset.src} alt={asset.alt} loading="lazy" />
            <span>Tap to expand</span>
          </button> : <div className="guide-chart-unavailable"><strong>RB Volume</strong><span>Graph coming soon in the published source.</span></div>}
          <div className="guide-chart-copy"><span>{chart.tags.join(' · ')}</span><h2>{chart.title}</h2><p>{shivaCopy(chart.body)}</p></div>
        </article>
      })}
    </div>
  }

  if (!hub) return <>
    <section className="draft-guide-hero">
      <div className="draft-guide-hero-copy"><span>2026</span><h1>Shiva’s Draft Guide</h1><p>SHIVA SOURCE INTELLIGENCE · FULL PPR</p></div>
      <div className="draft-guide-players" aria-hidden="true">
        <img src={playerHeadshotUrl(heroAllen?.espnId || heroAllen?.id || '3918298', true)} alt="" />
        <img src={playerHeadshotUrl(heroGibbs?.espnId || heroGibbs?.id || '4429795', true)} alt="" />
      </div>
    </section>
    <HubPills active={null} onSelect={setHub} />
    <div className="guide-hub-grid">{guideHubs.map((item) => <button key={item.id} type="button" className="guide-hub-card" onClick={() => setHub(item.id)}><h2>{item.title}</h2><p>{shivaCopy(item.desc)}</p><span>Open →</span></button>)}</div>
  </>

  return <>
    <div className="guide-sticky-nav">
      <button className="back-link" onClick={() => setHub(null)}>← Guide contents</button>
      <HubPills active={hub} onSelect={setHub} />
    </div>

    {hub === 'big-board' && <>
      <div className="section-kicker">FULL PPR</div><h1>2026 PPR Big Board</h1>
      <p className="lede">Use the full board for all 150 players and its original ranking color cues.</p>
      <FullGuideLink page={4} label="Open PPR Big Board" />
    </>}

    {hub === 'strategy' && <>
      <div className="section-kicker">12-TEAM PPR</div><h1>Draft Strategy</h1>
      <div className="guide-rule-list">{strategyRules.map((rule, index) => <article key={rule}><b>{index + 1}</b><p>{shivaCopy(rule)}</p></article>)}</div>
      <div className="strategy-grid guide-position-strategy">{strategyPositionNotes.map((item) => <article className="panel" key={item.pos}><span className="eyebrow">{item.pos}</span><h2>{item.title}</h2><p>{shivaCopy(item.body)}</p></article>)}</div>
      <div className="round-plan guide-round-plan">{strategyRounds.map(([round, target]) => <div key={round}><b>{round}</b><p>{target}</p></div>)}</div>
      <FullGuideLink page={11} label="Open Full Strategy Page" />
    </>}

    {hub === 'charts' && <>
      <div className="section-kicker">RESEARCH CHARTS</div><h1>Charts</h1>
      {chartGallery()}
    </>}

    {hub === 'positions' && <>
      <div className="section-kicker">POSITION DATA</div><h1>Position Data</h1>
      <div className="guide-chart-pills position-data-tabs">{positionViews.map((item) => <button type="button" key={item.id} className={position === item.id ? 'active' : ''} onClick={() => setPosition(item.id)}>{item.title}</button>)}</div>
      {selectedPosition.chartIds.length > 0 ? chartGallery(selectedPosition.chartIds) : <p className="lede">Open the full source table for the original position rankings and color treatment.</p>}
      <div className="guide-pdf-actions">{selectedPosition.pages.map((page, index) => <FullGuideLink key={`${selectedPosition.id}-${page}`} page={page} label={index === 0 ? `Open ${selectedPosition.title} Rankings` : `Open ${selectedPosition.title} PPG Data`} />)}</div>
    </>}

    {hub === 'playcallers' && <>
      <div className="section-kicker">COACHING ENVIRONMENT</div><h1>Playcallers</h1>
      <article className="guide-chart-note source-color-note"><div><span>COLOR-CODED READ</span><h2>The table is the analysis.</h2></div><p>Yellow identifies a new team. Pink identifies a first-time playcaller. Green-to-red rank shading communicates quality at a glance.</p></article>
      <FullGuideLink page={15} label="Open Playcaller Table" />
    </>}

    {hub === 'favorite-stats' && <>
      <div className="section-kicker">SOURCE NUGGETS</div><h1>20 Favorite Stats</h1>
      <div className="favorite-stat-list">{favoriteStats.map(([rank, title, body], index) => <article key={rank}><div><span>{index + 1}</span><small>Shiva #{rank}</small></div><section><h2>{title}</h2><p>{shivaCopy(body)}</p></section></article>)}</div>
      <div className="guide-pdf-actions"><FullGuideLink page={19} label="Open Stats 50–26" /><FullGuideLink page={20} label="Open Stats 25–1" /></div>
    </>}

    {hub === 'rb-volume' && <>
      <div className="section-kicker">RUNNING BACKS</div><h1>RB Volume</h1>
      <div className="guide-rule-list">{rbVolumeNotes.map((note, index) => <article key={note}><b>{index + 1}</b><p>{shivaCopy(note)}</p></article>)}</div>
      {chartGallery(['rb-efficiency', 'rb-dream-qb', 'rb-volume'])}
    </>}

    {hub === 'gold-mine' && <>
      <div className="section-kicker">TARGET SIGNALS</div><h1>Gold Mine</h1>
      <p className="lede">Green is Target, yellow is I’ll Pass, red is Avoiding.</p>
      <div className="gold-mine-key"><span className="target">Target</span><span className="pass">I’ll Pass</span><span className="avoid">Avoiding</span></div>
      <FullGuideLink page={5} label="Open Color-Coded Rankings" />
    </>}

    {hub === 'players' && <>
      <div className="section-kicker">PLAYER SHORTCUTS</div><h1>Player Cards</h1><p className="lede">Quick access to players repeatedly referenced throughout the guide.</p>
      <div className="player-card-grid">{featuredPlayers.map((name) => { const player = findPlayer(name); return <button type="button" className="player-card clickable-player" key={name} onClick={() => openPlayer(player)}><div className="player-inline"><PlayerAvatar playerId={player?.espnId || player?.id} name={name} /><span className="board-position">{player?.pos || '—'}</span></div><h2>{name}</h2><p>{player ? `${player.team} · Overall ${player.rank < 10000 ? `#${player.rank}` : '—'} · ADP ${player.adp?.toFixed(1) ?? '—'}` : 'Guide research target'}</p></button> })}</div>
    </>}

    {expanded && chartAssets[expanded.id as ChartId]?.src && <div className="guide-chart-lightbox" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setExpandedChart(null) }}>
      <section role="dialog" aria-modal="true" aria-label={`${expanded.title} expanded`}>
        <button type="button" className="guide-chart-close" aria-label="Close expanded chart" onClick={() => setExpandedChart(null)}>×</button>
        <h2>{expanded.title}</h2>
        <img src={chartAssets[expanded.id as ChartId].src} alt={chartAssets[expanded.id as ChartId].alt} />
        <p>{shivaCopy(expanded.body)}</p>
      </section>
    </div>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </>
}
