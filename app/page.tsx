'use client'

import { useEffect, useState } from 'react'
import CoachView from '../components/CoachView'
import DraftView from '../components/DraftView'
import GuideView from '../components/GuideView'
import HomeView from '../components/HomeView'

type Tab = 'Home' | 'Draft' | 'Guide' | 'Coach'

export default function ShivaApp() {
  const [tab, setTab] = useState<Tab>('Home')
  const [launching, setLaunching] = useState(true)

  useEffect(() => {
    const timer = window.setTimeout(() => setLaunching(false), 1500)
    return () => window.clearTimeout(timer)
  }, [])

  return <>
    {launching && <div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy-clean.svg" alt="The Shiva trophy" /></div>}
    <main className="app-shell">
      <header className="brand-header">
        <img src="/shiva-trophy-clean.svg" alt="The Shiva trophy" className="brand-trophy" />
        <div className="brand-copy"><div className="brand-name">Shiva</div><div className="brand-subtitle">FANTASY FOOTBALL INTELLIGENCE</div></div>
      </header>

      <section className="content" key={tab}>
        {tab === 'Home' && <HomeView />}
        {tab === 'Draft' && <DraftView />}
        {tab === 'Guide' && <GuideView />}
        {tab === 'Coach' && <CoachView />}
      </section>

      <nav className="bottom-nav" aria-label="Primary navigation">
        {(['Home','Draft','Guide','Coach'] as Tab[]).map((item) => <button type="button" key={item} className={tab === item ? 'active' : ''} onClick={() => { setTab(item); window.scrollTo({ top: 0, behavior:'instant' as ScrollBehavior }) }}>
          {item === 'Home' ? <img src="/shiva-trophy-clean.svg" alt="" /> : <span className="nav-mark" aria-hidden="true">{item === 'Draft' ? 'D' : item === 'Guide' ? 'G' : 'C'}</span>}
          <span>{item}</span>
        </button>)}
      </nav>
    </main>
  </>
}
