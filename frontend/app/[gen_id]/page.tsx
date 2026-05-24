"use client"
import { useEffect, useState, useCallback } from "react"
import { useParams, useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api/client"
import { connectSSE } from "@/lib/sse/client"
import { HD2Isolation } from "@/components/hd/HD2Isolation"
import HD3Forge from "@/components/hd/HD3Forge"
import HD4Vault from "@/components/hd/HD4Vault"
import HD5Kiln from "@/components/hd/HD5Kiln"
import HD6Preview from "@/components/hd/HD6Preview"

// ── Status → Screen mapping (server-driven, per BEF §10.4) ──────────
type GenStatus =
  | "queued" | "extracting" | "brief_ready"
  | "scripting" | "critiquing" | "safety_checking" | "scripts_ready"
  | "strategy_preview" | "awaiting_funds" | "funds_locked"
  | "rendering" | "reflecting" | "composing" | "preview_ready"
  | "export_queued" | "export_ready"
  | "failed_category" | "failed_compliance" | "failed_safety"
  | "failed_render" | "failed_export"

interface GenerationState {
  gen_id: string
  status: GenStatus
  screen_descriptor?: { screen: string }
  confidence_score?: number
  isolated_png_url?: string
  safe_scripts?: unknown[]
  selected_script_id?: number
  strategy_card?: unknown
  preview_url?: string
  b_roll_available?: boolean
  plan_tier?: string
}

function statusToScreen(status: GenStatus): string {
  if (["queued", "extracting", "brief_ready"].includes(status)) return "HD2"
  if (["scripting", "critiquing", "safety_checking", "scripts_ready"].includes(status)) return "HD3"
  if (["strategy_preview", "awaiting_funds"].includes(status)) return "HD4"
  if (["funds_locked", "rendering", "reflecting", "composing"].includes(status)) return "HD5"
  if (["preview_ready", "export_queued", "export_ready", "failed_export"].includes(status)) return "HD6"
  if (["failed_category", "failed_compliance", "failed_safety"].includes(status)) return "ERROR"
  return "HD2"
}

export default function GenerationPage() {
  const params = useParams()
  const router = useRouter()
  const genId  = params.gen_id as string

  const [gen, setGen]       = useState<GenerationState | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState<string | null>(null)

  // ── Hydrate generation state ────────────────────────────────────────
  const hydrate = useCallback(async () => {
    try {
      const token = localStorage.getItem("aw_token")
      if (!token) { router.push("/"); return }
      const data = await apiFetch<GenerationState>(`/api/generations/${genId}`)
      setGen(data)
    } catch (e: unknown) {
      const err = e as { status?: number }
      if (err?.status === 401) { router.push("/"); return }
      setError("Failed to load generation")
    } finally {
      setLoading(false)
    }
  }, [genId, router])

  useEffect(() => { hydrate() }, [hydrate])

  // ── SSE — live status updates ────────────────────────────────────────
  useEffect(() => {
    if (!gen) return
    const token = localStorage.getItem("aw_token")
    const cleanup = connectSSE({
      genId,
      token,
      onEvent: (evt) => {
        if (evt.status || (evt as { state?: string }).state) {
          const newStatus = (evt.status || (evt as { state?: string }).state) as GenStatus
          setGen(prev => prev ? { ...prev, status: newStatus } : prev)
          // Re-hydrate on key transitions to get fresh data
          if (["brief_ready", "scripts_ready", "strategy_preview",
               "preview_ready", "export_ready"].includes(newStatus)) {
            hydrate()
          }
        }
      },
    })
    return cleanup
  }, [gen?.gen_id, genId, hydrate])

  // ── Loading state ───────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-amber-400 text-sm animate-pulse">Loading...</div>
    </div>
  )

  if (error || !gen) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-red-400 text-sm">{error ?? "Generation not found"}</div>
    </div>
  )

  const screen = gen.screen_descriptor?.screen ?? statusToScreen(gen.status)

  // ── Screen router ───────────────────────────────────────────────────
  if (screen === "HD2" || gen.status === "brief_ready" ||
      gen.status === "extracting" || gen.status === "queued") {
    return (
      <HD2Isolation
        genId={genId}
        onContinue={hydrate}
        onReupload={() => router.push("/")}
      />
    )
  }

  if (screen === "HD3" ||
      gen.status === "scripting" ||
      gen.status === "critiquing" ||
      gen.status === "safety_checking" ||
      gen.status === "scripts_ready" ||
      gen.status === "regenerating") {
    return (
      <HD3Forge
        genId={genId}
        onAdvance={hydrate}
      />
    )
  }

  if (screen === "HD4" ||
      gen.status === "strategy_preview" ||
      gen.status === "awaiting_funds") {
    return (
      <HD4Vault
        genId={genId}
        onAdvance={hydrate}
      />
    )
  }

  if (screen === "HD5" ||
      gen.status === "funds_locked" ||
      gen.status === "rendering" ||
      gen.status === "reflecting" ||
      gen.status === "composing") {
    return (
      <HD5Kiln
        genId={genId}
        initialStatus={gen.status}
        onComplete={hydrate}
      />
    )
  }

  if (screen === "HD6" ||
      gen.status === "preview_ready" ||
      gen.status === "export_queued" ||
      gen.status === "export_ready" ||
      gen.status === "failed_export") {
    return (
      <HD6Preview
        genId={genId}
        initialStatus={gen.status}
        initialData={gen as any}
      />
    )
  }

  // Fallback — should never reach here
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-zinc-500 text-sm">
        Unknown state: {gen.status}
      </div>
    </div>
  )
}
