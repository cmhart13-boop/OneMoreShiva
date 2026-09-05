import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

type OpenAIResponse = {
  output_text?: string
  output?: Array<{ content?: Array<{ type?: string; text?: string; refusal?: string }> }>
  status?: string
  incomplete_details?: { reason?: string } | null
  error?: { message?: string } | null
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

async function askOpenAI(key: string, question: string, context: string, maxOutputTokens: number) {
  const response = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || 'gpt-5-mini',
      instructions: 'You are Shiva, a concise fantasy-football decision assistant. Use the supplied roster and league context when relevant. Be decisive, explain the strongest evidence briefly, and never invent current injury or projection facts. If a player name looks misspelled, infer the likely intended fantasy-relevant player from context and briefly note the interpretation rather than refusing to answer.',
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
    const context = String(body.context || '').slice(0, 12000)
    if (!question) return NextResponse.json({ error: 'Ask Shiva a question.' }, { status: 400 })

    let data = await askOpenAI(key, question, context, 1200)
    let answer = extractAnswer(data)

    // Some Responses API calls can finish without a text item when the output budget is
    // consumed by reasoning. Retry once with a larger budget instead of showing a dead-end message.
    if (!answer) {
      data = await askOpenAI(key, question, context, 2200)
      answer = extractAnswer(data)
    }

    if (!answer) {
      const reason = data.incomplete_details?.reason || data.status || 'no text output'
      throw new Error(`Shiva did not return an answer (${reason}). Please try again.`)
    }

    return NextResponse.json({ answer })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Shiva Intelligence is temporarily unavailable.' }, { status: 502 })
  }
}
