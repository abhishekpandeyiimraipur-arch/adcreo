// frontend/components/hd/HD4Vault.tsx
"use client"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? ""

interface Script {
  framework: string
  framework_angle: string
  full_text: string
  hook: string
  body: string
  cta: string
  critic_score: number
}

interface GenerationData {
  gen_id: string
  status: string
  safe_scripts: Script[]
  selected_script_id: number
  product_brief: {
    product_name: string
    category: string
    price_inr?: number
    key_features?: string[]
  } | string
  plan_tier?: string
}

interface Props {
  genId: string
  onAdvance: () => void
}

const FRAMEWORK_LABELS: Record<string, string> = {
  pas_micro: "Problem → Agitate → Solve",
  clinical_flex: "Clinical Flex",
  myth_buster: "Myth Buster",
  asmr_trigger: "ASMR Trigger",
  usage_ritual: "Usage Ritual",
  hyper_local_comfort: "Hyper Local",
  spec_drop_flex: "Spec Drop",
  premium_upgrade: "Premium Upgrade",
  roi_durability_flex: "ROI & Durability",
  festival_occasion_hook: "Festival Hook",
  scarcity_drop: "Scarcity Drop",
  social_proof: "Social Proof",
}

export default function HD4Vault({ genId, onAdvance }: Props) {
  const router = useRouter()
  const [gen, setGen] = useState<GenerationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [confirming, setConfirming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const hydrate = useCallback(async () => {
    const token = localStorage.getItem("aw_token")
    if (!token) { router.push("/"); return }
    try {
      const res = await fetch(`${API_BASE}/api/generations/${genId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) { router.push("/"); return }
      const data: GenerationData = await res.json()
      setGen(data)
    } catch {
      setError("Failed to load strategy")
    } finally {
      setLoading(false)
    }
  }, [genId, router])

  useEffect(() => { hydrate() }, [hydrate])

  async function handleConfirm() {
    setConfirming(true)
    setError(null)
    const token = localStorage.getItem("aw_token")
    try {
      const res = await fetch(
        `${API_BASE}/api/generations/${genId}/approve-strategy`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            "Idempotency-Key": `approve-strategy-${genId}`,
          },
        }
      )
      if (res.status === 402) {
        setError("You have no credits remaining. Contact us to add credits.")
        return
      }
      if (res.status === 403) {
        setError("Upgrade your plan to render videos.")
        return
      }
      if (res.status === 409) {
        setError("Another action is in progress. Please refresh.")
        return
      }
      if (!res.ok) {
        setError("Something went wrong. Please try again.")
        return
      }
      // Success — funds_locked → shell router hydrates → moves to HD5
      onAdvance()
    } catch {
      setError("Connection error. Please try again.")
    } finally {
      setConfirming(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-amber-400 text-sm animate-pulse">
        Preparing your ad plan...
      </div>
    </div>
  )

  if (!gen) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-red-400 text-sm">{error ?? "Strategy not found"}</div>
    </div>
  )

  // Parse product_brief if string
  const brief = typeof gen.product_brief === "string"
    ? JSON.parse(gen.product_brief)
    : gen.product_brief

  // Get selected script (selected_script_id is 1-indexed)
  const selectedIdx = (gen.selected_script_id ?? 1) - 1
  const script = gen.safe_scripts?.[selectedIdx] ?? gen.safe_scripts?.[0]

  if (!script) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-red-400 text-sm">Strategy data missing. Please go back.</div>
    </div>
  )

  const frameworkLabel = FRAMEWORK_LABELS[script.framework] ?? script.framework

  return (
    <div className="min-h-screen bg-black flex flex-col">

      {/* ── Top bar ─────────────────────────────────────────────── */}
      <div className="border-b border-zinc-800 px-6 py-3 flex items-center justify-between">
        <div>
          <span className="text-amber-400 text-xs font-medium tracking-widest uppercase">
            Step 4 of 6
          </span>
          <h1 className="text-white font-bold text-lg leading-tight">
            Your Ad Plan
          </h1>
        </div>
        <div className="text-zinc-600 text-xs text-right">
          <div>{brief?.product_name ?? "Your product"}</div>
          <div className="text-zinc-700">{brief?.category}</div>
        </div>
      </div>

      {/* ── Strategy Card ─────────────────────────────────────── */}
      <div className="flex-1 overflow-auto px-4 py-8 max-w-2xl mx-auto w-full">

        <div className="bg-zinc-950 border border-zinc-800 rounded-2xl p-6 space-y-5">

          {/* Product row */}
          <div className="flex justify-between items-start">
            <div>
              <div className="text-zinc-500 text-xs uppercase tracking-widest mb-1">
                Product
              </div>
              <div className="text-white font-semibold">
                {brief?.product_name}
              </div>
              {brief?.price_inr && (
                <div className="text-zinc-400 text-sm">₹{brief.price_inr}</div>
              )}
            </div>
            <div className="text-right">
              <div className="text-zinc-500 text-xs uppercase tracking-widest mb-1">
                Category
              </div>
              <div className="text-zinc-300 text-sm">{brief?.category}</div>
            </div>
          </div>

          <div className="border-t border-zinc-800" />

          {/* Framework row */}
          <div>
            <div className="text-zinc-500 text-xs uppercase tracking-widest mb-1">
              Ad Framework
            </div>
            <div className="flex items-center gap-2">
              <span className="text-white font-medium">{frameworkLabel}</span>
              <span className="text-zinc-600 text-xs">·</span>
              <span className="text-amber-400 text-xs">{script.framework_angle}</span>
            </div>
          </div>

          <div className="border-t border-zinc-800" />

          {/* Script row */}
          <div>
            <div className="text-zinc-500 text-xs uppercase tracking-widest mb-2">
              Script
            </div>
            <p className="text-zinc-200 text-sm leading-relaxed">
              {script.full_text}
            </p>
            <div className="mt-2 text-amber-400 text-xs">
              CTA: {script.cta}
            </div>
          </div>

          <div className="border-t border-zinc-800" />

          {/* Duration row */}
          <div className="flex justify-between">
            <div>
              <div className="text-zinc-500 text-xs uppercase tracking-widest mb-1">
                Duration
              </div>
              <div className="text-zinc-300 text-sm">15 seconds</div>
            </div>
            <div className="text-right">
              <div className="text-zinc-500 text-xs uppercase tracking-widest mb-1">
                Format
              </div>
              <div className="text-zinc-300 text-sm">1:1 + 9:16</div>
            </div>
          </div>

          <div className="border-t border-zinc-800" />

          {/* Compliance row */}
          <div className="flex gap-4 text-xs">
            <span className="text-green-400">✓ SGI Compliant</span>
            <span className="text-green-400">✓ C2PA Signed</span>
            <span className="text-green-400">✓ 5-yr Audit</span>
          </div>

          <div className="border-t border-zinc-800" />

          {/* Cost row */}
          <div className="flex justify-between items-center">
            <div className="text-zinc-500 text-sm">Cost</div>
            <div className="text-white font-semibold">1 Credit</div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 p-3 bg-red-950 border border-red-800 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* CTA button */}
        <button
          onClick={handleConfirm}
          disabled={confirming}
          className="mt-6 w-full py-4 bg-amber-500 hover:bg-amber-400 disabled:bg-zinc-700
                     text-black font-bold rounded-xl transition-colors text-sm"
        >
          {confirming
            ? "Locking credit & starting render..."
            : "✓ Confirm & Use 1 Credit → Render"}
        </button>

        <button
          onClick={() => router.back()}
          className="mt-3 w-full py-3 text-zinc-500 text-sm hover:text-zinc-300 transition-colors"
        >
          ← Edit Script
        </button>
      </div>
    </div>
  )
}
