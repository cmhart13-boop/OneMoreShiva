import './globals.css'
import './homepage.css'
import './home-refinements.css'
import './typography.css'
import './player-ui.css'
import './test-theme.css'
import './auth.css'
import './league-tools.css'
import './call-refinements.css'
import './user-requested-fixes.css'
import './guide-source.css'
import type { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Shiva',
  description: 'Fantasy Football Intelligence',
  manifest: '/manifest.webmanifest',
  icons: {
    icon: '/shiva-trophy.png',
    apple: '/shiva-trophy.png',
  },
  appleWebApp: {
    capable: true,
    title: 'Shiva',
    statusBarStyle: 'black-translucent',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#071019',
  colorScheme: 'dark',
}

const firstPaintCss = `
  html, body {
    margin: 0 !important;
    min-height: 100% !important;
    background: #071019 !important;
    background-color: #071019 !important;
    color-scheme: dark !important;
  }
  body {
    min-height: 100vh !important;
    min-height: 100dvh !important;
  }
  .launch-screen {
    position: fixed !important;
    inset: 0 !important;
    background: #071019 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
  }
  .launch-screen::before {
    content: 'SHIVA' !important;
    display: block !important;
    color: #f7f8f6 !important;
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    font-size: clamp(46px, 13vw, 78px) !important;
    font-weight: 950 !important;
    line-height: .9 !important;
    letter-spacing: -.055em !important;
    text-transform: uppercase !important;
    text-align: center !important;
  }
  .launch-screen img {
    display: block !important;
    margin: 0 !important;
  }
`

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" style={{ background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="theme-color" content="#071019" />
        <link rel="apple-touch-startup-image" href="/apple-splash.svg" />
        <link rel="preload" as="image" href="/shiva-trophy.png" />
        <style dangerouslySetInnerHTML={{ __html: firstPaintCss }} />
      </head>
      <body style={{ margin: 0, minHeight: '100dvh', background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>{children}</body>
    </html>
  )
}
