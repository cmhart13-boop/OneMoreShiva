'use client'

import { FormEvent, useEffect, useState } from 'react'

type SessionUser = { id: string; email: string }
type Mode = 'signin' | 'signup'
type SavedLeague = {
  id: string
  league_id: string
  season: number
  nickname?: string | null
  team_id?: number | null
  league_name?: string | null
  team_name?: string | null
}

export default function AuthButton() {
  const [user, setUser] = useState<SessionUser | null>(null)
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<Mode>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [leagues, setLeagues] = useState<SavedLeague[]>([])
  const [leagueId, setLeagueId] = useState('')
  const [season, setSeason] = useState(2026)
  const [nickname, setNickname] = useState('')
  const [swid, setSwid] = useState('')
  const [espnS2, setEspnS2] = useState('')

  async function loadLeagues() {
    const response = await fetch('/api/leagues', { cache: 'no-store' })
    if (!response.ok) return
    const data = await response.json()
    setLeagues(data.leagues || [])
  }

  useEffect(() => {
    fetch('/api/auth/session', { cache: 'no-store' })
      .then(async (response) => response.ok ? response.json() : null)
      .then((data) => {
        const nextUser = data?.user ?? null
        setUser(nextUser)
        if (nextUser) loadLeagues().catch(() => {})
      })
      .catch(() => setUser(null))
  }, [])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Unable to sign in.')
      if (data.user) {
        setUser(data.user)
        setPassword('')
        await loadLeagues()
      } else if (mode === 'signup') {
        setMode('signin')
        setError('Account created. Check your email if confirmation is required, then sign in.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in.')
    } finally {
      setBusy(false)
    }
  }

  async function signOut() {
    setBusy(true)
    try {
      await fetch('/api/auth/signout', { method: 'POST' })
      setUser(null)
      setLeagues([])
      setOpen(false)
      try {
        window.sessionStorage.removeItem('shiva-league')
        window.sessionStorage.removeItem('shiva-team-id')
      } catch {}
    } finally {
      setBusy(false)
    }
  }

  async function addLeague(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!leagueId.trim()) return
    setBusy(true)
    setError('')
    try {
      const espnResponse = await fetch('/api/espn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ leagueId: leagueId.trim(), season, swid, espnS2 }),
      })
      const leagueData = await espnResponse.json()
      if (!espnResponse.ok) throw new Error(leagueData.error || 'ESPN connection failed.')
      const team = leagueData.teams?.[0] ?? null
      const saveResponse = await fetch('/api/leagues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          leagueId: leagueId.trim(),
          season,
          nickname,
          teamId: team?.id ?? null,
          leagueName: leagueData.league?.name || null,
          teamName: team?.name || null,
        }),
      })
      const saved = await saveResponse.json()
      if (!saveResponse.ok) throw new Error(saved.error || 'Unable to save league.')
      try {
        window.sessionStorage.setItem('shiva-league', JSON.stringify(leagueData))
        if (team?.id !== undefined) window.sessionStorage.setItem('shiva-team-id', String(team.id))
      } catch {}
      setLeagueId('')
      setNickname('')
      setSwid('')
      setEspnS2('')
      await loadLeagues()
      setOpen(false)
      window.location.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to add league.')
    } finally {
      setBusy(false)
    }
  }

  async function useLeague(league: SavedLeague) {
    setBusy(true)
    setError('')
    try {
      const response = await fetch('/api/espn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ leagueId: league.league_id, season: league.season }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'This league needs its ESPN private credentials again.')
      const teamId = league.team_id ?? data.teams?.[0]?.id ?? null
      try {
        window.sessionStorage.setItem('shiva-league', JSON.stringify(data))
        if (teamId !== null) window.sessionStorage.setItem('shiva-team-id', String(teamId))
      } catch {}
      setOpen(false)
      window.location.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load league.')
    } finally {
      setBusy(false)
    }
  }

  async function removeLeague(id: string) {
    setBusy(true)
    setError('')
    try {
      const response = await fetch(`/api/leagues?id=${encodeURIComponent(id)}`, { method: 'DELETE' })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Unable to remove league.')
      await loadLeagues()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to remove league.')
    } finally {
      setBusy(false)
    }
  }

  return <div className="account-control">
    <button type="button" className={`account-button${user ? ' signed-in' : ''}`} onClick={() => setOpen(true)}>
      <span className="account-icon" aria-hidden="true">{user ? user.email.charAt(0).toUpperCase() : '●'}</span>
      <span>{user ? user.email.split('@')[0] : 'Sign In'}</span>
    </button>

    {open && <div className="account-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false) }}>
      <section className="account-modal" role="dialog" aria-modal="true" aria-label="Shiva account">
        <button type="button" className="account-close" aria-label="Close" onClick={() => setOpen(false)}>×</button>
        <div className="account-brand">
          <img src="/shiva-trophy.png" alt="" />
          <div><strong>Shiva</strong><span>Your leagues. Your teams. Your account.</span></div>
        </div>

        {user ? <div className="account-signed-in">
          <div className="account-identity"><span>Signed in as</span><strong>{user.email}</strong></div>
          <div className="account-leagues-head"><strong>My Leagues</strong><span>{leagues.length}</span></div>
          <div className="account-league-list">
            {leagues.length ? leagues.map((league) => <div className="account-league-row" key={league.id}>
              <button type="button" className="account-league-main" disabled={busy} onClick={() => useLeague(league)}>
                <b>{league.nickname || league.league_name || `League ${league.league_id}`}</b>
                <small>{league.team_name || `ESPN · ${league.season}`}</small>
              </button>
              <button type="button" className="account-league-remove" aria-label="Remove league" disabled={busy} onClick={() => removeLeague(league.id)}>×</button>
            </div>) : <p className="account-empty">No saved leagues yet.</p>}
          </div>
          <form className="account-form account-league-form" onSubmit={addLeague}>
            <div className="account-form-title">Add ESPN League</div>
            <div className="account-form-grid"><label>League ID<input inputMode="numeric" required value={leagueId} onChange={(event) => setLeagueId(event.target.value)} /></label><label>Season<input inputMode="numeric" required value={season} onChange={(event) => setSeason(Number(event.target.value))} /></label></div>
            <label>Nickname <span className="optional">optional</span><input value={nickname} onChange={(event) => setNickname(event.target.value)} placeholder="Shiva 2.0" /></label>
            <details className="account-private"><summary>Private ESPN league</summary><label>SWID<input type="password" value={swid} onChange={(event) => setSwid(event.target.value)} /></label><label>espn_s2<input type="password" value={espnS2} onChange={(event) => setEspnS2(event.target.value)} /></label><p>Used only to connect this session. Shiva does not save these credentials.</p></details>
            {error && <p className="account-error">{error}</p>}
            <button type="submit" className="account-submit" disabled={busy}>{busy ? 'Working…' : 'Add League'}</button>
          </form>
          <button type="button" className="account-signout" disabled={busy} onClick={signOut}>Sign Out</button>
        </div> : <>
          <div className="account-tabs">
            <button type="button" className={mode === 'signin' ? 'active' : ''} onClick={() => { setMode('signin'); setError('') }}>Sign In</button>
            <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => { setMode('signup'); setError('') }}>Create Account</button>
          </div>
          <form className="account-form" onSubmit={submit}>
            <label>Email<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>Password<input type="password" minLength={8} autoComplete={mode === 'signin' ? 'current-password' : 'new-password'} required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
            {error && <p className="account-error">{error}</p>}
            <button type="submit" className="account-submit" disabled={busy}>{busy ? 'Working…' : mode === 'signin' ? 'Sign In' : 'Create Account'}</button>
          </form>
        </>}
      </section>
    </div>}
  </div>
}
