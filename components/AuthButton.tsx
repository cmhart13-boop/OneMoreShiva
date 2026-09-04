'use client'

import { FormEvent, useEffect, useState } from 'react'

type SessionUser = { id: string; email: string }
type Mode = 'signin' | 'signup'

export default function AuthButton() {
  const [user, setUser] = useState<SessionUser | null>(null)
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<Mode>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/auth/session', { cache: 'no-store' })
      .then(async (response) => response.ok ? response.json() : null)
      .then((data) => setUser(data?.user ?? null))
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
        setOpen(false)
        setPassword('')
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
      setOpen(false)
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
          <span>Signed in as</span>
          <strong>{user.email}</strong>
          <button type="button" className="account-submit" disabled={busy} onClick={signOut}>Sign Out</button>
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
