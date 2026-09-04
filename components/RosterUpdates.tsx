'use client'

import { useEffect, useMemo, useState } from 'react'
import { PlayerAvatar } from './PlayerMedia'
import type { NewsArticle } from '../lib/types'

type StoredRosterRow = {
  teamId: number
  player: string
  playerId: string
  injuryStatus?: string
}

type StoredLeague = {
  roster?: StoredRosterRow[]
}

type RosterUpdate = {
  player: string
  playerId: string
  injuryStatus?: string
  article: NewsArticle
}

const INJURY_TERMS = /injur|questionable|doubtful|out\b|limited|practice|hamstring|ankle|knee|shoulder|concussion|illness|return|inactive|status/i

function readRoster() {
  try {
    const raw = window.sessionStorage.getItem('shiva-league')
    const teamRaw = window.sessionStorage.getItem('shiva-team-id')
    if (!raw || !teamRaw) return [] as StoredRosterRow[]
    const league = JSON.parse(raw) as StoredLeague
    const teamId = Number(teamRaw)
    return (league.roster || []).filter((row) => row.teamId === teamId && row.player && row.playerId)
  } catch {
    return [] as StoredRosterRow[]
  }
}

function timestamp(article: NewsArticle) {
  const value = article.published ? new Date(article.published).getTime() : 0
  return Number.isFinite(value) ? value : 0
}

export default function RosterUpdates() {
  const [roster, setRoster] = useState<StoredRosterRow[]>([])
  const [updates, setUpdates] = useState<RosterUpdate[]>([])
  const [expanded, setExpanded] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const sync = () => setRoster(readRoster())
    sync()
    const timer = window.setInterval(sync, 1500)
    return () => window.clearInterval(timer)
  }, [])

  const rosterKey = useMemo(() => roster.map((row) => `${row.playerId}:${row.injuryStatus || ''}`).join('|'), [roster])

  useEffect(() => {
    if (!roster.length) {
      setUpdates([])
      return
    }

    let active = true
    setLoading(true)

    Promise.all(roster.slice(0, 18).map(async (row) => {
      try {
        const response = await fetch(`/api/news?player=${encodeURIComponent(row.player)}`)
        const data = await response.json()
        const articles = (data.articles || []) as NewsArticle[]
        const article = [...articles].sort((a, b) => {
          const aInjury = INJURY_TERMS.test(`${a.headline || ''} ${a.description || ''}`) ? 1 : 0
          const bInjury = INJURY_TERMS.test(`${b.headline || ''} ${b.description || ''}`) ? 1 : 0
          return bInjury - aInjury || timestamp(b) - timestamp(a)
        })[0]
        return article ? { player:row.player, playerId:row.playerId, injuryStatus:row.injuryStatus, article } : null
      } catch {
        return null
      }
    })).then((items) => {
      if (!active) return
      const next = items.filter(Boolean) as RosterUpdate[]
      next.sort((a, b) => {
        const aPriority = (a.injuryStatus && a.injuryStatus !== 'ACTIVE' ? 2 : 0) + (INJURY_TERMS.test(`${a.article.headline || ''} ${a.article.description || ''}`) ? 1 : 0)
        const bPriority = (b.injuryStatus && b.injuryStatus !== 'ACTIVE' ? 2 : 0) + (INJURY_TERMS.test(`${b.article.headline || ''} ${b.article.description || ''}`) ? 1 : 0)
        return bPriority - aPriority || timestamp(b.article) - timestamp(a.article)
      })
      setUpdates(next.slice(0, 6))
      setLoading(false)
    })

    return () => { active = false }
  }, [rosterKey])

  if (!roster.length) return null

  return <section className="roster-updates" aria-label="Recent updates for your roster">
    <div className="section-heading roster-updates-heading">
      <div><div className="section-kicker">YOUR ROSTER</div><h2>Recent Updates</h2></div>
      <span className="live-dot">ESPN LIVE</span>
    </div>

    {loading && !updates.length ? <div className="panel loading-panel">Checking your players for recent ESPN updates…</div> : null}

    {!loading && !updates.length ? <div className="panel loading-panel">No recent ESPN player updates found right now.</div> : null}

    {updates.length ? <div className="roster-update-list">
      {updates.map((update) => {
        const key = `${update.player}-${update.article.published || update.article.headline}`
        const isOpen = expanded === key
        const injuryMention = INJURY_TERMS.test(`${update.article.headline || ''} ${update.article.description || ''}`)
        return <article className={`roster-update-card${isOpen ? ' expanded' : ''}`} key={key}>
          <button type="button" className="roster-update-toggle" aria-expanded={isOpen} onClick={() => setExpanded(isOpen ? null : key)}>
            <PlayerAvatar playerId={update.playerId} name={update.player} />
            <div className="roster-update-copy">
              <div className="roster-update-player"><b>{update.player}</b>{update.injuryStatus && update.injuryStatus !== 'ACTIVE' ? <span>{update.injuryStatus}</span> : injuryMention ? <span>NEWS</span> : null}</div>
              <p>{update.article.headline}</p>
            </div>
            <span className="roster-update-chevron" aria-hidden="true">{isOpen ? '−' : '+'}</span>
          </button>
          {isOpen ? <div className="roster-update-detail">
            {update.article.image ? <img src={update.article.image} alt="" loading="lazy" decoding="async" /> : null}
            <p>{update.article.description || update.article.headline}</p>
            {update.article.url ? <a href={update.article.url} target="_blank" rel="noreferrer">Open ESPN story →</a> : null}
          </div> : null}
        </article>
      })}
    </div> : null}
  </section>
}
