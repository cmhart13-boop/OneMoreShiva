import { NextRequest, NextResponse } from 'next/server'

const accessCookie = 'shiva-access-token'
const refreshCookie = 'shiva-refresh-token'
const fallbackUrl = 'https://wrhgxzweksizelffgcii.supabase.co'
const fallbackKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndyaGd4endla3NpemVsZmZnY2lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg0OTEwNzQsImV4cCI6MjEwNDA2NzA3NH0.r-H9jzQr_m6vuS_b09B_hAVekzxvuCjP5oDsSc5me4A'

function config() {
  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || fallbackUrl
  const key = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || fallbackKey
  return { url: url.replace(/\/$/, ''), key }
}

function cookieOptions(maxAge: number) {
  return { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax' as const, path: '/', maxAge }
}

function publicUser(user: any) {
  if (!user?.id || !user?.email) return null
  return { id: String(user.id), email: String(user.email) }
}

async function supabase(path: string, init: RequestInit = {}) {
  const { url, key } = config()
  return fetch(`${url}/auth/v1${path}`, {
    ...init,
    headers: { apikey: key, 'Content-Type': 'application/json', ...(init.headers || {}) },
    cache: 'no-store',
  })
}

function setSession(response: NextResponse, data: any) {
  if (data?.access_token) response.cookies.set(accessCookie, data.access_token, cookieOptions(Number(data.expires_in || 3600)))
  if (data?.refresh_token) response.cookies.set(refreshCookie, data.refresh_token, cookieOptions(60 * 60 * 24 * 30))
}

function clearSession(response: NextResponse) {
  response.cookies.set(accessCookie, '', cookieOptions(0))
  response.cookies.set(refreshCookie, '', cookieOptions(0))
}

async function errorResponse(response: Response) {
  const data = await response.json().catch(() => ({}))
  return NextResponse.json({ error: data?.msg || data?.error_description || data?.message || 'Account request failed.' }, { status: response.status || 400 })
}

export async function GET(request: NextRequest, context: { params: Promise<{ action: string }> }) {
  const { action } = await context.params
  if (action !== 'session') return NextResponse.json({ error: 'Not found.' }, { status: 404 })

  try {
    let access = request.cookies.get(accessCookie)?.value
    const refresh = request.cookies.get(refreshCookie)?.value
    if (!access) return NextResponse.json({ user: null })

    let userResponse = await supabase('/user', { headers: { Authorization: `Bearer ${access}` } })
    let refreshed: any = null

    if (!userResponse.ok && refresh) {
      const refreshResponse = await supabase('/token?grant_type=refresh_token', { method: 'POST', body: JSON.stringify({ refresh_token: refresh }) })
      if (refreshResponse.ok) {
        refreshed = await refreshResponse.json()
        access = refreshed.access_token
        userResponse = await supabase('/user', { headers: { Authorization: `Bearer ${access}` } })
      }
    }

    if (!userResponse.ok) {
      const response = NextResponse.json({ user: null })
      clearSession(response)
      return response
    }

    const user = await userResponse.json()
    const response = NextResponse.json({ user: publicUser(user) })
    if (refreshed) setSession(response, refreshed)
    return response
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Account service unavailable.' }, { status: 503 })
  }
}

export async function POST(request: NextRequest, context: { params: Promise<{ action: string }> }) {
  const { action } = await context.params

  try {
    if (action === 'signout') {
      const access = request.cookies.get(accessCookie)?.value
      if (access) await supabase('/logout', { method: 'POST', headers: { Authorization: `Bearer ${access}` } }).catch(() => null)
      const response = NextResponse.json({ ok: true })
      clearSession(response)
      return response
    }

    const body = await request.json().catch(() => ({}))
    const email = String(body?.email || '').trim().toLowerCase()
    const password = String(body?.password || '')
    if (!email || password.length < 8) return NextResponse.json({ error: 'Enter a valid email and a password of at least eight characters.' }, { status: 400 })

    const redirectTo = `${request.nextUrl.origin}/`
    const authResponse = action === 'signup'
      ? await supabase(`/signup?redirect_to=${encodeURIComponent(redirectTo)}`, { method: 'POST', body: JSON.stringify({ email, password }) })
      : action === 'signin'
        ? await supabase('/token?grant_type=password', { method: 'POST', body: JSON.stringify({ email, password }) })
        : null

    if (!authResponse) return NextResponse.json({ error: 'Not found.' }, { status: 404 })
    if (!authResponse.ok) return errorResponse(authResponse)

    const data = await authResponse.json()
    const hasSession = Boolean(data?.access_token)
    const response = NextResponse.json({
      user: hasSession ? publicUser(data.user) : null,
      confirmationRequired: action === 'signup' && !hasSession,
    })
    if (hasSession) setSession(response, data)
    return response
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Account service unavailable.' }, { status: 503 })
  }
}
