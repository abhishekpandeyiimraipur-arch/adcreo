"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { GoogleLogin } from "@react-oauth/google"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://89.167.27.232:8000"

export default function Home() {
  const router              = useRouter()
  const [error, setError]   = useState<string | null>(null)
  const [checking, setChecking] = useState(true)

  // If token already exists → skip straight to /new
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
      if (!res.ok || !data.token) {
        setError("Sign-in failed. Please try again.")
        return
      }
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
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-amber-400 text-sm animate-pulse">Loading...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="w-full max-w-sm px-8">

        {/* Logo */}
        <div className="mb-12 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Ad<span className="text-amber-400">creo</span>
          </h1>
          <p className="text-zinc-500 text-sm mt-2">
            India-first AI video ad platform
          </p>
        </div>

        {/* Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-white text-base font-semibold mb-1">
            Create your first ad
          </h2>
          <p className="text-zinc-500 text-sm mb-6">
            Beta access · Sign in to continue
          </p>

          {error && (
            <div className="mb-4 px-3 py-2 bg-red-950 border border-red-800
                            rounded-lg text-red-400 text-xs">
              {error}
            </div>
          )}

          {/* Google Login button — rendered by @react-oauth/google */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="filled_black"
              shape="rectangular"
              size="large"
              text="signin_with_google"
            />
          </div>

          <p className="text-zinc-600 text-xs text-center mt-4">
            Beta · Invite only · Free during beta
          </p>
        </div>

      </div>
    </div>
  )
}
