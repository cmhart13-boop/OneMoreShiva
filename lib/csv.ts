export type CsvRecord = Record<string, string>

export function parseCsv(text: string): CsvRecord[] {
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let quoted = false

  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i]
    if (quoted) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"'
          i += 1
        } else {
          quoted = false
        }
      } else {
        field += ch
      }
      continue
    }
    if (ch === '"') {
      quoted = true
    } else if (ch === ',') {
      row.push(field)
      field = ''
    } else if (ch === '\n') {
      row.push(field.replace(/\r$/, ''))
      rows.push(row)
      row = []
      field = ''
    } else {
      field += ch
    }
  }

  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ''))
    rows.push(row)
  }

  if (!rows.length) return []
  const headers = rows[0].map((value) => value.trim())
  return rows.slice(1).filter((values) => values.some((value) => value !== '')).map((values) => {
    const out: CsvRecord = {}
    headers.forEach((header, index) => {
      out[header] = values[index] ?? ''
    })
    return out
  })
}

export function numberOrNull(value: unknown): number | null {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

export function normalizeName(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]/g, '')
}
