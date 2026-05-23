import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Adcreo — AI Video Ads for India",
  description: "India-first agentic AI video ad platform for D2C brands",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-white antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
