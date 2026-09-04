'use client'

import { useState } from 'react'
import CoachView, { type CoachTab } from './CoachView'
import DraftView from './DraftView'

type CoachHubView = 'My Team' | 'My League' | 'Start / Sit' | 'Grade My Draft' | 'Mock Draft' | 'Players'

const HUB_TABS: CoachHubView[] = ['My Team','My League','Start / Sit','Grade My Draft','Mock Draft','Players']
const COACH_TAB_MAP: Partial<Record<CoachHubView, CoachTab>> = {
  'My Team': 'Lineup',
  'My League': 'League',
  'Start / Sit': 'Start / Sit',
  'Players': 'Players',
}

export default function CoachHub() {
  const [view, setView] = useState<CoachHubView>('My Team')
  const [detailTab, setDetailTab] = useState<CoachTab | null>(null)
  const coachTab = detailTab ?? COACH_TAB_MAP[view]
  const chooseView = (next: CoachHubView) => {
    setView(next)
    setDetailTab(null)
  }

  return <div className="coach-hub">
    <div className="coach-hub-heading">
      <div className="section-kicker">SHIVA COACH</div>
      <h1>Shiva Coach</h1>
    </div>

    <div className="coach-hub-tabs" aria-label="Shiva Coach tools">
      {HUB_TABS.map((item) => <button type="button" key={item} className={view === item ? 'active' : ''} onClick={() => chooseView(item)}>{item}</button>)}
    </div>

    <div className="coach-hub-content">
      {view === 'Mock Draft' && <DraftView />}
      {view === 'Grade My Draft' && <><div className="section-kicker">DRAFT REVIEW</div><h2 className="screen-subtitle">Grade My Draft</h2><div className="empty-state">Connect your ESPN league and open this tool after your draft. The grading workflow is ready for the completed draft data once it is available.</div></>}
      {coachTab && <CoachView showTabs={false} activeTab={coachTab} onTabChange={setDetailTab} />}
    </div>
  </div>
}
