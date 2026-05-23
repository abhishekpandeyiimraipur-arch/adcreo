"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { API_BASE } from "@/lib/api/client"

export default function Home() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    if (token) {
      router.push("/new")
    } else {
      setChecking(false)
    }
  }, [router])

  async function handleDevLogin() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/dev-token`)
      const data = await res.json()
      if (data.token) {
        localStorage.setItem("aw_token", data.token)
        router.push("/new")
      }
    } catch {
      setError("Cannot connect to server. Is the backend running?")
      setLoading(false)
    }
  }

  if (checking) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-amber-400 text-sm animate-pulse">Loading...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="w-full max-w-sm px-8">
        <div className="mb-12 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Ad<span className="text-amber-400">creo</span>
          </h1>
          <p className="text-zinc-500 text-sm mt-2">
            India-first AI video ad platform
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-white text-base font-semibold mb-1">
            Create your first ad
          </h2>
          <p className="text-zinc-500 text-sm mb-6">
            Beta access · No account needed
          </p>

          {error && (
            <div className="mb-4 px-3 py-2 bg-red-950 border border-red-800
                            rounded-lg text-red-400 text-xs">
              {error}
            </div>
          )}

          <button
            onClick={handleDevLogin}
            disabled={loading}
            className="w-full bg-amber-400 hover:bg-amber-300 disabled:opacity-50
                       text-black font-semibold text-sm py-3 px-4 rounded-lg
                       transition-colors duration-150"
          >
            {loading ? "Connecting..." : "Start Creating →"}
          </button>

          <p className="text-zinc-600 text-xs text-center mt-4">
            Beta · Invite only · Free during beta
          </p>
        </div>
      </div>
    </div>
  )
}
