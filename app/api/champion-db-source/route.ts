import { NextResponse } from 'next/server'
import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

const RAW_DB = 'https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'

export async function GET() {
  try {
    const r = await fetch(RAW_DB, { cache: 'no-store' })
    if (!r.ok) throw new Error(`GitHub raw ${r.status}`)
    const bytes = new Uint8Array(await r.arrayBuffer())
    const path = `/tmp/shiva-${Date.now()}.sqlite`
    await writeFile(path, bytes)
    const db = new DatabaseSync(path, { readOnly: true })
    const tables = db.prepare("select name from sqlite_master where type='table' order by name").all()
    const cols = db.prepare('pragma table_info(draft_roi_scores)').all()
    const rows = db.prepare('select * from draft_roi_scores order by league_name, season, overall_pick').all()
    db.close()
    return NextResponse.json({ ok: true, tables, columns: cols, rowCount: rows.length, rows })
  } catch (e) {
    return NextResponse.json({ ok: false, error: e instanceof Error ? e.message : String(e) }, { status: 500 })
  }
}
