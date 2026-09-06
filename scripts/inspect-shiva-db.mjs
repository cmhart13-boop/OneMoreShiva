import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

const url = 'https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'
const r = await fetch(url)
if (!r.ok) throw new Error(`db download ${r.status}`)
const path = '/tmp/shiva-report.sqlite'
await writeFile(path, new Uint8Array(await r.arrayBuffer()))
const db = new DatabaseSync(path, { readOnly: true })
console.log('SHIVA_REPORT_TABLES', JSON.stringify(db.prepare("select name from sqlite_master where type='table' order by name").all()))
for (const {name} of db.prepare("select name from sqlite_master where type='table' order by name").all()) {
  console.log('SHIVA_REPORT_SCHEMA', name, JSON.stringify(db.prepare(`pragma table_info(${name})`).all()))
  console.log('SHIVA_REPORT_COUNT', name, JSON.stringify(db.prepare(`select count(*) as n from ${name}`).get()))
}
const cols = db.prepare('pragma table_info(draft_roi_scores)').all().map(x=>x.name)
console.log('SHIVA_REPORT_COLS', JSON.stringify(cols))
console.log('SHIVA_REPORT_SEASONS', JSON.stringify(db.prepare('select league_name, min(season) as minSeason, max(season) as maxSeason, count(distinct season) as seasons, count(*) as rows from draft_roi_scores group by league_name').all()))
console.log('SHIVA_REPORT_SAMPLE', JSON.stringify(db.prepare('select * from draft_roi_scores limit 3').all()))
db.close()
