import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Bill.com Processing',
  description: 'Process Bill.com vendor payments and reconcile to payment holds',
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

