import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

type OpenAIResponse = {
  output_text?: string
  output?: Array<{ content?: Array<{ type?: string; text?: string; refusal?: string }> }>
  status?: string
  incomplete_details?: { reason?: string } | null
  error?: { message?: string } | null
}

type FantasyPlayer = {
  name: string
  team?: string
  pos?: string
  rank?: number | null
}

function extractAnswer(data: OpenAIResponse) {
  if (typeof data.output_text === 'string' && data.output_text.trim()) return data.output_text.trim()
  return (data.output || [])
    .flatMap((item) => item.content || [])
    .map((item) => typeof item.text === 'string' ? item.text : typeof item.refusal === 'string' ? item.refusal : '')
    .filter(Boolean)
    .join('\n')
    .trim()
}

function normalize(value: string) {
  return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '')
}

function levenshtein(a: string, b: string) {
  if (a === b) return 0
  if (!a.length) return b.length
  if (!b.length) return a.length
  const prev = Array.from({ length:b.length + 1 }, (_, i) => i)
  for (let i = 1; i <= a.length; i += 1) {
    const next = [i]
    for (let j = 1; j <= b.length; j += 1) {
      next[j] = Math.min(
        next[j - 1] + 1,
        prev[j] + 1,
        prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1),
      )
    }
    for (let j = 0; j < next.length; j += 1) prev[j] = next[j]
  }
  return prev[b.length]
}

function maxDistance(length: number) {
  if (length <= 4) return 1
  if (length <= 6) return 2
  return 3
}

function resolvePlayerMentions(question: string, players: FantasyPlayer[]) {
  const words = question
    .split(/\s+/)
    .map((word) => ({ raw:word.replace(/^[^A-Za-z0-9]+|[^A-Za-z0-9]+$/g, ''), key:normalize(word) }))
    .filter((word) => word.key.length >= 4)

  const resolved: Array<{ typed:string; player:FantasyPlayer; distance:number }> = []
  const used = new Set<string>()

  for (const word of words) {
    const candidates = players.map((player) => {
      const parts = player.name.split(/\s+/).filter(Boolean)
      const first = normalize(parts[0] || '')
      const last = normalize(parts[parts.length - 1] || '')
      const full = normalize(player.name)
      const distances = [first, last, full].filter(Boolean).map((candidate) => levenshtein(word.key, candidate))
      return { player, distance:Math.min(...distances) }
    }).sort((a, b) => a.distance - b.distance || (a.player.rank ?? 9999) - (b.player.rank ?? 9999))

    const best = candidates[0]
    const second = candidates[1]
    if (!best) continue
    const threshold = maxDistance(word.key.length)
    const uniquelyBest = !second || best.distance < second.distance || best.distance === 0
    if (best.distance <= threshold && uniquelyBest && !used.has(best.player.name)) {
      resolved.push({ typed:word.raw, player:best.player, distance:best.distance })
      used.add(best.player.name)
    }
  }

  return resolved
}

async function loadFantasyPlayers(request: NextRequest) {
  try {
    const url = new URL('/api/rankings', request.url)
    const response = await fetch(url, { cache:'no-store' })
    if (!response.ok) return [] as FantasyPlayer[]
    const data = await response.json()
    return Array.isArray(data?.players)
      ? data.players
          .filter((player: any) => typeof player?.name === 'string' && player.name.trim())
          .map((player: any) => ({ name:String(player.name), team:String(player.team || ''), pos:String(player.pos || ''), rank:Number.isFinite(player.rank) ? Number(player.rank) : null }))
      : [] as FantasyPlayer[]
  } catch {
    return [] as FantasyPlayer[]
  }
}

async function askOpenAI(key: string, question: string, context: string, maxOutputTokens: number) {
  const response = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || 'gpt-5-mini',
      instructions: 'You are Shiva, a fantasy-football-only decision assistant. Treat supplied resolved player mentions as authoritative. A fantasy user will often use only a last name, shorthand, or a close misspelling. Resolve it to the obvious NFL fantasy player and answer the football question directly. Never ask the user to provide a full player name when the supplied player directory or resolved mentions identify the player. If league/roster context is supplied, prioritize it. Be decisive and concise. Never invent current injury or projection facts that are not supplied.',
      input: `${context ? `Context:\n${context}\n\n` : ''}Question: ${question}`,
      reasoning: { effort: 'low' },
      max_output_tokens: maxOutputTokens,
    }),
    cache: 'no-store',
  })
  const data = await response.json().catch(() => ({})) as OpenAIResponse
  if (!response.ok) throw new Error(data?.error?.message || `AI API returned ${response.status}`)
  return data
}

export async function POST(request: NextRequest) {
  const key = process.env.OPENAI_API_KEY
  if (!key) return NextResponse.json({ error: 'Shiva Intelligence API is not configured on this deployment.' }, { status: 503 })

  try {
    const body = await request.json()
    const question = String(body.question || '').trim()
    const suppliedContext = String(body.context || '').slice(0, 12000)
    if (!question) return NextResponse.json({ error: 'Ask Shiva a question.' }, { status: 400 })

    const players = await loadFantasyPlayers(request)
    const resolved = resolvePlayerMentions(question, players)
    const resolvedContext = resolved.length
      ? `Resolved player mentions: ${resolved.map((item) => `${item.typed} → ${item.player.name}${item.player.pos ? ` (${item.player.pos}${item.player.team ? `, ${item.player.team}` : ''})` : ''}`).join('; ')}`
      : ''
    const directory = players.length
      ? `Fantasy player directory: ${players.slice(0, 350).map((player) => `${player.name}${player.pos ? ` (${player.pos}${player.team ? `, ${player.team}` : ''})` : ''}`).join(', ')}`
      : ''
    const context = [suppliedContext, resolvedContext, directory].filter(Boolean).join('\n').slice(0, 30000)

    let data = await askOpenAI(key, question, context, 1200)
    let answer = extractAnswer(data)

    if (!answer) {
      data = await askOpenAI(key, question, context, 2200)
      answer = extractAnswer(data)
    }

    if (!answer) {
      const reason = data.incomplete_details?.reason || data.status || 'no text output'
      throw new Error(`Shiva did not return an answer (${reason}). Please try again.`)
    }

    return NextResponse.json({ answer, resolvedPlayers:resolved.map((item) => item.player.name) })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Shiva Intelligence is temporarily unavailable.' }, { status: 502 })
  }
}
