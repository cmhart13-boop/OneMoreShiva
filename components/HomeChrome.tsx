'use client'

import { useEffect, useState } from 'react'

export default function HomeChrome() {
  const [homeVisible, setHomeVisible] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const sync = () => setHomeVisible(Boolean(document.querySelector('.og-home')))
    sync()
    const observer = new MutationObserver(sync)
    observer.observe(document.body, { childList: true, subtree: true })
    return () => observer.disconnect()
  }, [])

  if (!homeVisible) return null

  return <div className="home-live-chrome" aria-label="Home controls">
    <button type="button" className="home-live-bell" aria-label="Notifications" aria-expanded={open} onClick={() => setOpen(value => !value)}>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg>
      <span className="home-live-badge">3</span>
    </button>
    {open && <div className="home-live-popover" role="dialog" aria-label="Notifications panel">
      <strong>Notifications</strong>
      <p>League alerts and Shiva updates will appear here.</p>
      <button type="button" onClick={() => setOpen(false)}>Close</button>
    </div>}
  </div>
}
