import './globals.css'
import './homepage.css'
import './typography.css'
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
`

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" style={{ background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <style dangerouslySetInnerHTML={{ __html: firstPaintCss }} />
      </head>
      <body style={{ margin: 0, minHeight: '100dvh', background: '#071019', backgroundColor: '#071019', colorScheme: 'dark' }}>{children}</body>
    </html>
  )
}
