import './globals.css'
import './homepage.css'
import './home-refinements.css'
import './overview-home.css'
import './typography.css'
import './player-ui.css'
import './test-theme.css'
import './auth.css'
import './league-tools.css'
import './call-refinements.css'
import './user-requested-fixes.css'
import './guide-source.css'
import './shiva-batch-queue.css'
import './rebuild.css'
import './approved-reference.css'
import './og-interface.css'
import './home-exact-pass.css'
import './live-hero-components.css'
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
    statusBarStyle: 'black',
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
    z-index: 2147483647 !important;
    background: #071019 !important;
    background-color: #071019 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  .launch-screen::before,
  .launch-screen::after {
    content: none !important;
    display: none !important;
  }
  .launch-screen img {
    display: block !important;
    width: min(97.5vw, 488px) !important;
    max-height: 82dvh !important;
    object-fit: contain !important;
    margin: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }
`

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" style={{ background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black" />
        <meta name="theme-color" content="#071019" />
        <link rel="apple-touch-startup-image" href="/apple-splash.svg" />
        <link rel="preload" as="image" href="/shiva-trophy.png" />
        <link rel="preload" as="image" href="/og-home-hero.jpg" />
        <style dangerouslySetInnerHTML={{ __html: firstPaintCss }} />
      </head>
      <body style={{ margin: 0, minHeight: '100dvh', background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>{children}</body>
    </html>
  )
}
