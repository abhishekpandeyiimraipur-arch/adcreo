"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { GoogleLogin } from "@react-oauth/google"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://89.167.27.232:8000"

export default function Home() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    if (token) {
      router.push("/new")
    } else {
      setChecking(false)
    }
  }, [router])

  async function handleGoogleSuccess(credentialResponse: { credential?: string }) {
    setError(null)
    const credential = credentialResponse.credential
    if (!credential) { setError("Sign-in failed. Please try again."); return }
    try {
      const res = await fetch(`${API_BASE}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential }),
      })
      const data = await res.json()
      if (!res.ok || !data.token) { setError("Sign-in failed. Please try again."); return }
      localStorage.setItem("aw_token", data.token)
      router.push("/new")
    } catch {
      setError("Sign-in failed. Please try again.")
    }
  }

  function handleGoogleError() {
    setError("Sign-in failed. Please try again.")
  }

  if (checking) return (
    <div className="min-h-screen flex items-center justify-center"
         style={{ background: "var(--brand-bg)" }}>
      <div className="text-teal-400 text-sm animate-pulse">Loading...</div>
    </div>
  )

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: "linear-gradient(135deg, #0F172A 0%, #0D2137 50%, #0F172A 100%)" }}
    >
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2
                        w-96 h-96 rounded-full opacity-10"
             style={{ background: "radial-gradient(circle, #0D9488, transparent)" }} />
      </div>

      <div className="relative w-full max-w-sm">

        {/* Logo */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12
                          rounded-2xl mb-4"
               style={{ background: "linear-gradient(135deg, #0D9488, #0F766E)" }}>
            <span className="text-white font-bold text-lg">A</span>
          </div>
          <h1 className="text-4xl font-bold tracking-tight">
            <span className="text-white">Ad</span>
            <span className="text-teal-400">creo</span>
          </h1>
          <p className="text-slate-400 text-sm mt-2">
            India-first AI video ad platform
          </p>
          <div className="flex items-center justify-center gap-2 mt-3">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full
                             text-xs font-medium bg-teal-900 text-teal-300 border
                             border-teal-700">
              Beta
            </span>
            <span className="text-slate-600 text-xs">Free during beta</span>
          </div>
        </div>

        {/* Card */}
        <div className="rounded-2xl border p-8 shadow-2xl"
             style={{
               background: "var(--brand-surface)",
               borderColor: "var(--brand-border)",
               boxShadow: "0 25px 50px rgba(0,0,0,0.5)"
             }}>

          <div className="mb-6 text-center">
            <h2 className="text-white text-xl font-semibold mb-1">
              Create your first ad
            </h2>
            <p className="text-slate-400 text-sm">
              Sign in to get started — takes 2 minutes
            </p>
          </div>

          {/* How it works */}
          <div className="mb-6 space-y-2">
            {[
              { step: "1", text: "Upload your product image" },
              { step: "2", text: "AI writes 3 ad scripts" },
              { step: "3", text: "Get a 15s video ad" },
            ].map(({ step, text }) => (
              <div key={step} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full flex items-center justify-center
                                text-xs font-bold text-white shrink-0"
                     style={{ background: "var(--brand-primary)" }}>
                  {step}
                </div>
                <span className="text-slate-300 text-sm">{text}</span>
              </div>
            ))}
          </div>

          <div className="border-t mb-6" style={{ borderColor: "var(--brand-border)" }} />

          {error && (
            <div className="mb-4 px-3 py-2 bg-red-950 border border-red-800
                            rounded-lg text-red-400 text-xs text-center">
              {error}
            </div>
          )}

          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="filled_black"
              shape="rectangular"
              size="large"
              text="signin_with"
            />
          </div>

          <p className="text-slate-600 text-xs text-center mt-4">
            Invite only · Your data stays private
          </p>
        </div>

        {/* Footer */}
        <p className="text-slate-600 text-xs text-center mt-6">
          Built for Indian D2C brands · adcreo.in
        </p>

      </div>
    </div>
  )
}
