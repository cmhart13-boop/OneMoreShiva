'use client'

import { useMemo, useState } from 'react'

type Tab = 'Home' | 'Draft' | 'Guide' | 'Coach'

const guideCards = [
  ['Rankings', '2026 big board + positional rankings'],
  ['Draft Strategy', 'Round-by-round build and position rules'],
  ['Research', 'Research notes and clickable stat features'],
  ['Luck Metric', 'How the guide frames 2025 luck'],
  ['Player Cards', 'Featured-player shortcuts into app profiles'],
]

export default function ShivaApp() {
  const [tab, setTab] = useState<Tab>('Home')
  const title = useMemo(() => ({ Home: 'The Shiva Edge', Draft: '2026 Shiva Draft', Guide: '2026 Shiva Draft Guide', Coach: 'Shiva Coach' }[tab]), [tab])

  return (
    <main className="app-shell">
      <header className="brand-header">
        <img src="/shiva-trophy.png" alt="The Shiva trophy" className="brand-trophy" />
        <div><div className="brand-name">Shiva</div><div className="brand-subtitle">FANTASY FOOTBALL INTELLIGENCE</div></div>
      </header>

      <section className="content">
        <h1>{title}</h1>
        {tab === 'Home' && <>
          <p className="lede">Historical evidence, not a mystery score.</p>
          <div className="edge-grid">
            <article className="panel"><div className="eyebrow">RAISE THE FLOOR</div><h2>Consistent 15+ scoring</h2><div className="metric-row"><div><strong>Drake Maye</strong><span>QB · 20.7 PPG</span></div><b>94%</b></div><button>Floor Rankings →</button></article>
            <article className="panel"><div className="eyebrow">KEEP THE CEILING</div><h2>Week-winning upside</h2><div className="metric-row"><div><strong>Christian McCaffrey</strong><span>RB · 24.5 PPG</span></div><b>47%</b></div><button>Ceiling Rankings →</button></article>
          </div>
          <h2 className="section-title">Shiva Blast</h2>
          <p className="lede">Current ESPN fantasy/NFL context with the article image and actual story link.</p>
          <div className="blast-placeholder" />
        </>}

        {tab === 'Guide' && <>
          <p className="lede">Full-PPR intelligence built for draft-day decisions.</p>
          <div className="guide-grid">{guideCards.map(([name, desc]) => <article className="guide-card" key={name}><h2>{name}</h2><p>{desc}</p><span>Open section →</span></article>)}</div>
        </>}

        {tab === 'Draft' && <>
          <p className="lede">Choose your draft position, then start a mock draft.</p>
          <div className="panel form-panel"><label htmlFor="slot">Draft position</label><select id="slot" defaultValue="1">{Array.from({length:12},(_,i)=><option key={i+1}>{i+1}</option>)}</select><button>Start Mock Draft</button></div>
        </>}

        {tab === 'Coach' && <>
          <p className="lede">Fantasy decision room.</p>
          <div className="coach-pills"><button className="active">Overview</button><button>Waivers</button><button>Lineup</button><button>Trade</button></div>
          <div className="panel"><h2>Shiva says</h2><p>Coach tools are being migrated into the native Vercel application layer.</p></div>
        </>}
      </section>

      <nav className="bottom-nav" aria-label="Primary navigation">
        {(['Home','Draft','Guide','Coach'] as Tab[]).map(item => <button key={item} className={tab===item?'active':''} onClick={()=>setTab(item)}>{item==='Home' && <img src="/shiva-trophy.png" alt="" />}<span>{item}</span></button>)}
      </nav>
    </main>
  )
}
