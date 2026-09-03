import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  const key = process.env.OPENAI_API_KEY
  if (!key) return NextResponse.json({ error: 'Shiva Intelligence API is not configured on this deployment.' }, { status: 503 })
  try {
    const body = await request.json()
    const question = String(body.question || '').trim()
    const context = String(body.context || '').slice(0, 12000)
    if (!question) return NextResponse.json({ error: 'Ask Shiva a question.' }, { status: 400 })
    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'gpt-5-mini',
        instructions: 'You are Shiva, a concise fantasy-football decision assistant. Use the supplied roster/ranking context when relevant. Be decisive, explain the strongest evidence briefly, and never invent current injury or projection facts.',
        input: `${context ? `Context:\n${context}\n\n` : ''}Question: ${question}`,
        max_output_tokens: 700,
      }),
      cache: 'no-store',
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data?.error?.message || `AI API returned ${response.status}`)
    const answer = data.output_text || (data.output || []).flatMap((item: any) => item.content || []).map((item: any) => item.text || '').filter(Boolean).join('\n')
    return NextResponse.json({ answer: answer || 'Shiva could not produce a response.' })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Shiva Intelligence is temporarily unavailable.' }, { status: 502 })
  }
}
