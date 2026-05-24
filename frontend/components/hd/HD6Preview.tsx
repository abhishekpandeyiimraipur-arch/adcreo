// frontend/components/hd/HD6Preview.tsx
"use client"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { connectSSE } from "@/lib/sse/client"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? ""

interface Exports {
  square_url:   string
  portrait_url: string
}

interface GenerationData {
  gen_id:      string
  status:      string
  preview_url: string | null
  exports:     Exports | null
}

interface Props {
  genId:          string
  initialStatus:  string
  initialData:    GenerationData
}

export default function HD6Preview({ genId, initialStatus, initialData }: Props) {
  const router = useRouter()
  const [status, setStatus]   = useState(initialStatus)
  const [data, setData]       = useState<GenerationData>(initialData)
  const [checked, setChecked] = useState({
    commercial_use: false,
    image_rights:   false,
    ai_disclosure:  false,
  })
  const [declaring, setDeclaring] = useState(false)
  const [declared,  setDeclared]  = useState(false)
  const [error, setError]         = useState<string | null>(null)


  // ── SSE — wait for export_ready ───────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    const cleanup = connectSSE({
      genId,
      token,
      onEvent: (evt) => {
        const st = evt.status ?? (evt as { state?: string }).state
        if (!st) return
        setStatus(st)
        if (st === "export_ready") {
          // Re-hydrate to get exports URLs
          hydrate()
        }
      },
    })
    return cleanup
  }, [genId])

  const hydrate = useCallback(async () => {
    const token = localStorage.getItem("aw_token")
    if (!token) { router.push("/"); return }
    try {
      const res = await fetch(`${API_BASE}/api/generations/${genId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) { router.push("/"); return }
      const d: GenerationData = await res.json()
      setData(d)
      setStatus(d.status)
    } catch {
      setError("Failed to refresh. Please reload.")
    }
  }, [genId, router])

  // ── Poll on mount if preview_url missing (SSE race fix) ──────────
  useEffect(() => {
    if (!data.preview_url) {
      const timer = setTimeout(() => hydrate(), 3000)
      return () => clearTimeout(timer)
    }
  }, [data.preview_url, hydrate])

  // ── Declaration submit ─────────────────────────────────────────────
  async function handleDeclare() {
    const allChecked = checked.commercial_use &&
                       checked.image_rights &&
                       checked.ai_disclosure
    if (!allChecked) {
      setError("Please accept all three declarations to proceed.")
      return
    }
    setDeclaring(true)
    setError(null)
    const token = localStorage.getItem("aw_token")
    try {
      const res = await fetch(
        `${API_BASE}/api/generations/${genId}/declaration`,
        {
          method: "POST",
          headers: {
            Authorization:     `Bearer ${token}`,
            "Content-Type":    "application/json",
            "Idempotency-Key": `declaration-${genId}`,
          },
          body: JSON.stringify({
            commercial_use: checked.commercial_use,
            image_rights:   checked.image_rights,
            ai_disclosure:  checked.ai_disclosure,
          }),
        }
      )
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        setError(body?.detail?.message ?? "Declaration failed. Please try again.")
        return
      }
      setDeclared(true)
      setStatus("export_queued")
    } catch {
      setError("Connection error. Please try again.")
    } finally {
      setDeclaring(false)
    }
  }

  // ── Render ─────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-black flex flex-col">

      {/* ── Top bar ──────────────────────────────────────────────── */}
      <div className="border-b border-zinc-800 px-6 py-3">
        <span className="text-amber-400 text-xs font-medium tracking-widest uppercase">
          Step 6 of 6
        </span>
        <h1 className="text-white font-bold text-lg leading-tight">
          Your Ad
        </h1>
      </div>

      <div className="flex-1 overflow-auto px-4 py-8 max-w-2xl mx-auto w-full space-y-6">

        {/* ── Video preview ───────────────────────────────────────── */}
        {data.preview_url ? (
          <div className="rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950">
            <video
              src={data.preview_url}
              controls
              muted
              loop
              playsInline
              className="w-full max-h-[480px] object-contain"
            />
            <div className="px-4 py-2 text-zinc-600 text-xs">
              Watermarked preview — clean version downloads after declaration
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-8 text-center">
            <div className="text-zinc-500 text-sm animate-pulse">
              Loading preview...
            </div>
          </div>
        )}

        {/* ── Declaration checkboxes (shown before export_queued) ──── */}
        {!declared && status === "preview_ready" && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-5 space-y-4">
            <div className="text-white text-sm font-semibold">
              Declaration — IT Rules 2026
            </div>
            <div className="text-zinc-500 text-xs">
              All three must be accepted before downloading.
            </div>

            {[
              {
                key: "commercial_use" as const,
                label: "I confirm this video is for legitimate commercial use"
              },
              {
                key: "image_rights" as const,
                label: "I confirm I own or have rights to the product image used"
              },
              {
                key: "ai_disclosure" as const,
                label: "I agree to disclose AI involvement in this ad as required by law"
              },
            ].map(({ key, label }) => (
              <label
                key={key}
                className="flex items-start gap-3 cursor-pointer group"
              >
                <div className="mt-0.5 shrink-0">
                  <input
                    type="checkbox"
                    checked={checked[key]}
                    onChange={(e) =>
                      setChecked(prev => ({ ...prev, [key]: e.target.checked }))
                    }
                    className="w-4 h-4 accent-amber-400"
                  />
                </div>
                <span className="text-zinc-300 text-sm leading-relaxed group-hover:text-white transition-colors">
                  {label}
                </span>
              </label>
            ))}

            {error && (
              <div className="p-3 bg-red-950 border border-red-800 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={handleDeclare}
              disabled={declaring || !Object.values(checked).every(Boolean)}
              className="w-full py-3 bg-amber-500 hover:bg-amber-400
                         disabled:bg-zinc-700 disabled:text-zinc-500
                         text-black font-bold rounded-xl transition-colors text-sm"
            >
              {declaring ? "Submitting declaration..." : "Accept & Generate Downloads"}
            </button>
          </div>
        )}

        {/* ── Export queued / processing ───────────────────────────── */}
        {["export_queued", "export_ready"].includes(status) &&
         !data.exports && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-6 text-center">
            <div className="w-6 h-6 border-2 border-amber-400 border-t-transparent
                            rounded-full animate-spin mx-auto mb-3" />
            <div className="text-white text-sm font-medium">
              Processing final export...
            </div>
            <div className="text-zinc-500 text-xs mt-1">
              C2PA signing + watermark removal in progress
            </div>
          </div>
        )}

        {/* ── Download buttons (export_ready) ─────────────────────── */}
        {data.exports && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-5 space-y-3">
            <div className="text-white text-sm font-semibold mb-4">
              ✓ Your ad is ready — C2PA signed
            </div>

            <a
              href={data.exports.portrait_url}
              download="adcreo-ad-9x16.mp4"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between w-full py-3 px-4
                         bg-amber-500 hover:bg-amber-400 text-black font-bold
                         rounded-xl transition-colors text-sm"
            >
              <span>Download 9:16 (Reels/Stories)</span>
              <span className="text-xs font-normal opacity-70">Portrait · 480p</span>
            </a>

            <div className="pt-2 flex gap-3 text-xs text-zinc-600">
              <span>✓ SGI Compliant</span>
              <span>✓ C2PA Signed</span>
              <span>✓ Audit Logged</span>
            </div>
          </div>
        )}

        {/* ── Start new ────────────────────────────────────────────── */}
        {data.exports && (
          <button
            onClick={() => router.push("/")}
            className="w-full py-3 text-zinc-500 text-sm hover:text-zinc-300 transition-colors"
          >
            + Create another ad
          </button>
        )}

      </div>
    </div>
  )
}
