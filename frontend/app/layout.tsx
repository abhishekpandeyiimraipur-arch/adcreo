"use client"
import "./globals.css"
import { GoogleOAuthProvider } from "@react-oauth/google"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-white antialiased min-h-screen">
        <GoogleOAuthProvider
          clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? ""}
        >
          {children}
        </GoogleOAuthProvider>
      </body>
    </html>
  )
}
