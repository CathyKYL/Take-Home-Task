import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AP Sorting Agent',
  description: 'An agent that automatically sorts your accounting records into "Ready for Payment" or "Payment Hold."',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}


