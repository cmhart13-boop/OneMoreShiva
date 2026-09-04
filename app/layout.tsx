import './globals.css'
import './homepage.css'
import type { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  title: 'Shiva',
  description: 'Fantasy Football Intelligence',
  manifest: '/manifest.webmanifest',
  icons: {
    icon: '/shiva-trophy.png',
    apple: '/shiva-trophy.png',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#071019',
  colorScheme: 'dark',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" style={{ backgroundColor: '#071019' }}>
      <body style={{ backgroundColor: '#071019' }}>{children}</body>
    </html>
  )
}
