'use client'

import { FormEvent, useEffect, useState } from 'react'
import { activateLeague, importSaveActivate, PENDING_LEAGUE_KEY, type LeagueImportRequest } from '../lib/league-client'
import type { LeagueProvider, SavedLeague } from '../lib/types'

type SessionUser = { id: string; email: string; firstName?: string; lastName?: string }
type Mode = 'signin' | 'signup'

const REMEMBERED_EMAIL_KEY = 'shiva-remembered-email'

export default function AuthButton() {
  const [user, setUser] = useState<SessionUser | null>(null)
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<Mode>('signin')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberEmail, setRememberEmail] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [leagues, setLeagues] = useState<SavedLeague[]>([])
  const [leagueId, setLeagueId] = useState('')
  const [provider, setProvider] = useState<LeagueProvider>('espn')
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
    try {
      const remembered = window.localStorage.getItem(REMEMBERED_EMAIL_KEY) || ''
      if (remembered) {
        setEmail(remembered)
        setRememberEmail(true)
      }
    } catch {}

    fetch('/api/auth/session', { cache: 'no-store' })
      .then(async (response) => response.ok ? response.json() : null)
      .then((data) => {
        const nextUser = data?.user ?? null
        setUser(nextUser)
        if (nextUser) loadLeagues().catch(() => {})
      })
      .catch(() => setUser(null))
  }, [])

  useEffect(() => {
    const requireAuth = (event: Event) => {
      const detail = (event as CustomEvent<LeagueImportRequest>).detail
      if (detail) localStorage.setItem(PENDING_LEAGUE_KEY, JSON.stringify(detail))
      setMode('signup')
      setError('Create an account or sign in to save this league. It will continue automatically.')
      setOpen(true)
    }
    window.addEventListener('shiva:require-auth', requireAuth)
    return () => window.removeEventListener('shiva:require-auth', requireAuth)
  }, [])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, firstName, lastName }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Unable to sign in.')
      if (data.user) {
        setUser(data.user)
        setPassword('')
        try {
          if (rememberEmail) window.localStorage.setItem(REMEMBERED_EMAIL_KEY, String(data.user.email || email).trim().toLowerCase())
          else window.localStorage.removeItem(REMEMBERED_EMAIL_KEY)
        } catch {}
        const pendingRaw = localStorage.getItem(PENDING_LEAGUE_KEY)
        if (pendingRaw) {
          setError('Importing your league…')
          await importSaveActivate(JSON.parse(pendingRaw))
          setOpen(false)
        }
        await loadLeagues()
      } else if (mode === 'signup' && data.confirmationRequired) {
        setMode('signin')
        setPassword('')
        if (rememberEmail) {
          try { window.localStorage.setItem(REMEMBERED_EMAIL_KEY, email.trim().toLowerCase()) } catch {}
        }
        setError('Account created. Check your email to confirm it, then sign in.')
      } else if (mode === 'signup') {
        setMode('signin')
        setPassword('')
        setError('Account created. You can sign in now.')
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
      await importSaveActivate({ provider, leagueId:leagueId.trim(), season, nickname, swid, espnS2 })
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
      if (league.league_data) activateLeague(league.league_data, league.team_id)
      else await importSaveActivate({ provider:league.provider || 'espn', leagueId:league.league_id, season:league.season })
      setOpen(false)
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

  const greeting = user?.firstName ? `Hi, ${user.firstName}` : user ? 'Account' : 'Sign In'
  const fullName = [user?.firstName, user?.lastName].filter(Boolean).join(' ')

  return <div className="account-control">
    <button type="button" className={`account-button${user ? ' signed-in' : ''}`} aria-label={user ? `Open Shiva account${user.firstName ? ` for ${user.firstName}` : ''}` : 'Open account sign in'} onClick={() => setOpen(true)}>
      <span className="account-silhouette" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img">
          <circle cx="12" cy="7.5" r="3.5" fill="currentColor" />
          <path d="M5 20c.45-4.35 2.9-6.65 7-6.65s6.55 2.3 7 6.65H5Z" fill="currentColor" />
        </svg>
      </span>
      <span className="account-button-label">{greeting}</span>
    </button>

    {open && <div className="account-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false) }}>
      <section className="account-modal" role="dialog" aria-modal="true" aria-label="Shiva account">
        <button type="button" className="account-close" aria-label="Close" onClick={() => setOpen(false)}>×</button>
        <div className="account-brand">
          <img src="/shiva-trophy.png" alt="" />
          <div><strong>Shiva</strong><span>Your leagues. Your teams. Your account.</span></div>
        </div>

        {user ? <div className="account-signed-in">
          <div className="account-identity"><span>Signed in as</span><strong>{fullName || user.email}</strong>{fullName ? <small>{user.email}</small> : null}</div>
          <div className="account-leagues-head"><strong>My Leagues</strong><span>{leagues.length}</span></div>
          <div className="account-league-list">
            {leagues.length ? leagues.map((league) => <div className="account-league-row" key={league.id}>
              <button type="button" className="account-league-main" disabled={busy} onClick={() => useLeague(league)}>
                <b>{league.nickname || league.league_name || `League ${league.league_id}`}</b>
                <small>{league.team_name || `${(league.provider || 'espn').toUpperCase()} · ${league.season}`}</small>
              </button>
              <button type="button" className="account-league-remove" aria-label="Remove league" disabled={busy} onClick={() => removeLeague(league.id)}>×</button>
            </div>) : <p className="account-empty">No saved leagues yet.</p>}
          </div>
          <form className="account-form account-league-form" onSubmit={addLeague}>
            <div className="account-form-title">Add Your League</div>
            <label>Provider<select value={provider} onChange={(event) => setProvider(event.target.value as LeagueProvider)}><option value="espn">ESPN</option><option value="sleeper">Sleeper</option></select></label>
            <div className="account-form-grid"><label>League ID<input inputMode="numeric" required value={leagueId} onChange={(event) => setLeagueId(event.target.value)} placeholder={provider === 'sleeper' ? 'Sleeper league ID' : 'ESPN league ID'} /></label><label>Season<input inputMode="numeric" required value={season} onChange={(event) => setSeason(Number(event.target.value))} /></label></div>
            <label>Nickname <span className="optional">optional</span><input value={nickname} onChange={(event) => setNickname(event.target.value)} placeholder="Shiva 2.0" /></label>
            {provider === 'espn' && <details className="account-private"><summary>Private ESPN league</summary><label>SWID<input type="password" value={swid} onChange={(event) => setSwid(event.target.value)} /></label><label>espn_s2<input type="password" value={espnS2} onChange={(event) => setEspnS2(event.target.value)} /></label><p>Used only to connect this session. Shiva does not save these credentials.</p></details>}
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
            {mode === 'signin' && email ? <p className="account-returning">Welcome back — your email is remembered.</p> : null}
            {mode === 'signup' ? <div className="account-name-grid"><label>First name<input type="text" autoComplete="given-name" required value={firstName} onChange={(event) => setFirstName(event.target.value)} /></label><label>Last name<input type="text" autoComplete="family-name" required value={lastName} onChange={(event) => setLastName(event.target.value)} /></label></div> : null}
            <label>Email<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label className="account-remember"><input type="checkbox" checked={rememberEmail} onChange={(event) => setRememberEmail(event.target.checked)} />Remember me on this device</label>
            <label>Password<input type="password" minLength={8} autoComplete={mode === 'signin' ? 'current-password' : 'new-password'} required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
            {error && <p className="account-error">{error}</p>}
            <button type="submit" className="account-submit" disabled={busy}>{busy ? 'Working…' : mode === 'signin' ? 'Sign In' : 'Create Account'}</button>
          </form>
        </>}
      </section>
    </div>}
  </div>
}
