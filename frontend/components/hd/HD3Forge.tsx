"use client"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { API_BASE } from "@/lib/api/client"
import { connectSSE } from "@/lib/sse/client"

// ── Types ─────────────────────────────────────────────────────────────
interface Script {
  framework: string
  framework_angle: string
  full_text: string
  hook?: string
  body?: string
  cta?: string
  critic_score: number
  suggested_tone?: string
}

interface GenerationData {
  gen_id: string
  status: string
  safe_scripts?: Script[]
  selected_script_id?: number
  refined_script?: Script
  chat_turns_used?: number
  product_brief?: { product_name?: string; category?: string }
  tts_language?: string
}

interface Props {
  genId: string
  onAdvance: () => void
}

const FRAMEWORK_LABELS: Record<string, string> = {
  pas_micro:          "Problem → Solution",
  usage_ritual:       "Usage Ritual",
  social_proof:       "Social Proof",
  hyper_local_comfort:"Local Comfort",
  myth_buster:        "Myth Buster",
  roi_durability_flex:"ROI & Durability",
  premium_upgrade:    "Premium Upgrade",
  scarcity_fomo:      "Scarcity / FOMO",
  founder_story:      "Founder Story",
  ingredient_hero:    "Ingredient Hero",
  transformation_arc: "Transformation",
  festival_moment:    "Festival Moment",
}

const ANGLE_COLORS: Record<string, string> = {
  logic:      "text-blue-400",
  emotion:    "text-pink-400",
  conversion: "text-green-400",
}

// ── Component ──────────────────────────────────────────────────────────
export default function HD3Forge({ genId, onAdvance }: Props) {
  const router = useRouter()
  const [gen, setGen]                 = useState<GenerationData | null>(null)
  const [loading, setLoading]         = useState(true)
  const [selectedIdx, setSelectedIdx] = useState(0)
  const [advancing, setAdvancing]     = useState(false)
  const [error, setError]             = useState<string | null>(null)

  // Chat state (Part 2)
  const [chatMessage, setChatMessage] = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError]     = useState<string | null>(null)
  const [turnsUsed, setTurnsUsed]     = useState(0)

  // ── Hydrate ──────────────────────────────────────────────────────────
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
      setTurnsUsed(data.chat_turns_used ?? 0)
      // Pre-select top scorer
      if (data.selected_script_id) {
        setSelectedIdx((data.selected_script_id ?? 1) - 1)
      }
    } catch {
      setError("Failed to load scripts")
    } finally {
      setLoading(false)
    }
  }, [genId, router])

  useEffect(() => { hydrate() }, [hydrate])

  // ── Fallback poll — fires once after 20s if scripts still empty ───
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!gen || (gen.safe_scripts ?? []).length === 0) {
        hydrate()
      }
    }, 20000)
    return () => clearTimeout(timer)
  }, [gen, hydrate])

  // ── SSE — wait for scripts_ready ─────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    const cleanup = connectSSE({
      genId, token,
      onEvent: (evt) => {
        const st = evt.status || (evt as { state?: string }).state
        if (st === "scripts_ready") hydrate()
        if (st === "strategy_preview") onAdvance()
      },
    })
    return cleanup
  }, [genId, hydrate, onAdvance])

  // ── Advance to HD-4 ───────────────────────────────────────────────────
  async function handleAdvance() {
    setAdvancing(true)
    setError(null)
    const token = localStorage.getItem("aw_token")
    try {
      const res = await fetch(`${API_BASE}/api/generations/${genId}/advance`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          "Idempotency-Key": `advance-hd3-${genId}`,
        },
        body: JSON.stringify({ selected_script_id: selectedIdx + 1 }),
      })
      if (res.status === 409) { setError("Another session is active. Refresh and try again."); return }
      if (!res.ok) { setError("Failed to advance. Try again."); return }
      // SSE will fire strategy_preview → onAdvance()
    } catch {
      setError("Connection error")
    } finally {
      setAdvancing(false)
    }
  }

  // ── Co-Pilot chat ─────────────────────────────────────────────────────
  async function handleChat() {
    if (!chatMessage.trim() || turnsUsed >= 3) return
    setChatLoading(true)
    setChatError(null)
    const token = localStorage.getItem("aw_token")
    try {
      const res = await fetch(`${API_BASE}/api/generations/${genId}/chat`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          "Idempotency-Key": `chat-${genId}-${Date.now()}`,
        },
        body: JSON.stringify({ message: chatMessage.trim() }),
      })
      const data = await res.json()
      if (!res.ok) {
        setChatError(data.detail?.error_code ?? "Refinement failed")
        return
      }
      setChatMessage("")
      setTurnsUsed(data.turns_used)
      await hydrate() // Refresh to show refined script
    } catch {
      setChatError("Connection error")
    } finally {
      setChatLoading(false)
    }
  }

  // ── Loading state ─────────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-black flex items-center justify-center flex-col gap-3">
      <div className="text-amber-400 text-sm animate-pulse">
        Writing your scripts...
      </div>
      <div className="text-zinc-600 text-xs">This takes about 15 seconds</div>
    </div>
  )

  const scripts = gen?.safe_scripts ?? []
  const refinedScript = gen?.refined_script
  const selectedScript = refinedScript ?? scripts[selectedIdx]
  const turnsRemaining = 3 - turnsUsed

  return (
    <div className="min-h-screen bg-black flex flex-col">

      {/* ── Top bar ─────────────────────────────────────────────────── */}
      <div className="border-b border-zinc-800 px-6 py-3 flex items-center justify-between">
        <div>
          <span className="text-amber-400 text-xs font-medium tracking-widest uppercase">
            Step 3 of 6
          </span>
          <h1 className="text-white font-bold text-lg leading-tight">
            Choose your script
          </h1>
        </div>
        <div className="text-zinc-600 text-xs text-right">
          <div>{gen?.product_brief?.product_name ?? "Your product"}</div>
          <div className="text-zinc-700">{gen?.product_brief?.category}</div>
        </div>
      </div>

      {/* ── Main content ────────────────────────────────────────────── */}
      <div className="flex-1 overflow-auto px-4 py-6 max-w-5xl mx-auto w-full">

        {/* Script tiles */}
        {scripts.length === 0 ? (
          <div className="text-zinc-500 text-sm text-center py-20 animate-pulse">
            Generating scripts...
          </div>
        ) : (
          <>
            <div className="text-zinc-500 text-xs mb-4 uppercase tracking-widest">
              Select a script framework
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {scripts.map((script, idx) => {
                const isSelected = idx === selectedIdx
                const label = FRAMEWORK_LABELS[script.framework] ?? script.framework
                const angleColor = ANGLE_COLORS[script.framework_angle] ?? "text-zinc-400"
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedIdx(idx)}
                    className={`text-left p-5 rounded-xl border transition-all duration-150 ${
                      isSelected
                        ? "border-amber-400 bg-zinc-900"
                        : "border-zinc-800 bg-zinc-950 hover:border-zinc-600"
                    }`}
                  >
                    {/* Framework label + score */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        {idx === 0 && (
                          <span className="text-amber-400 text-xs mr-1">★</span>
                        )}
                        <span className="text-white text-xs font-semibold">
                          {label}
                        </span>
                        <div className={`text-xs mt-0.5 ${angleColor}`}>
                          {script.framework_angle}
                        </div>
                      </div>
                      <div className={`text-xl font-bold ${
                        script.critic_score >= 80 ? "text-green-400" :
                        script.critic_score >= 60 ? "text-yellow-400" : "text-zinc-500"
                      }`}>
                        {script.critic_score}
                      </div>
                    </div>

                    {/* Script preview */}
                    <p className="text-zinc-300 text-xs leading-relaxed line-clamp-4">
                      {script.full_text}
                    </p>

                    {/* CTA line */}
                    {script.cta && (
                      <div className="mt-3 text-amber-400 text-xs">
                        CTA: {script.cta}
                      </div>
                    )}

                    {isSelected && (
                      <div className="mt-3 pt-3 border-t border-zinc-700">
                        <span className="text-amber-400 text-xs font-medium">
                          ✓ Selected
                        </span>
                      </div>
                    )}
                  </button>
                )
              })}
            </div>

            {/* ── Co-Pilot Chat ─────────────────────────────────────── */}
            <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-5 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-white text-sm font-semibold">
                    Co-Pilot Refinement
                  </div>
                  <div className="text-zinc-500 text-xs mt-0.5">
                    Refine the selected script with AI
                  </div>
                </div>
                <div className={`text-xs font-medium px-2 py-1 rounded-full ${
                  turnsRemaining > 1 ? "bg-zinc-800 text-zinc-400" :
                  turnsRemaining === 1 ? "bg-yellow-950 text-yellow-400" :
                  "bg-red-950 text-red-400"
                }`}>
                  {turnsRemaining} turn{turnsRemaining !== 1 ? "s" : ""} left
                </div>
              </div>

              {/* Quick chips */}
              <div className="flex gap-2 mb-4 flex-wrap">
                {["Make it punchier", "Make it Hinglish", "Add Diwali energy"].map(chip => (
                  <button
                    key={chip}
                    onClick={() => setChatMessage(chip)}
                    disabled={turnsUsed >= 3 || chatLoading}
                    className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-40
                               text-zinc-300 text-xs rounded-full transition-colors"
                  >
                    {chip}
                  </button>
                ))}
              </div>

              {/* Refined script preview */}
              {refinedScript && (
                <div className="mb-4 p-3 bg-zinc-900 rounded-lg border border-amber-400/20">
                  <div className="text-amber-400 text-xs mb-1">Refined version</div>
                  <p className="text-zinc-300 text-xs leading-relaxed">
                    {refinedScript.full_text}
                  </p>
                </div>
              )}

              {/* Chat error */}
              {chatError && (
                <div className="mb-3 px-3 py-2 bg-red-950 border border-red-800
                                rounded-lg text-red-400 text-xs">
                  {chatError}
                </div>
              )}

              {/* Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={e => setChatMessage(e.target.value.slice(0, 500))}
                  onKeyDown={e => e.key === "Enter" && handleChat()}
                  disabled={turnsUsed >= 3 || chatLoading}
                  placeholder={
                    turnsUsed >= 3
                      ? "No turns remaining"
                      : "e.g. Make it more emotional..."
                  }
                  className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg
                             px-3 py-2 text-white text-xs placeholder:text-zinc-600
                             focus:outline-none focus:border-amber-400 disabled:opacity-40
                             transition-colors"
                />
                <button
                  onClick={handleChat}
                  disabled={!chatMessage.trim() || turnsUsed >= 3 || chatLoading}
                  className="px-4 py-2 bg-amber-400 hover:bg-amber-300 disabled:opacity-40
                             text-black text-xs font-semibold rounded-lg transition-colors"
                >
                  {chatLoading ? "..." : "Refine"}
                </button>
              </div>
            </div>
          </>
        )}

        {/* Error */}
        {error && (
          <div className="mb-4 px-3 py-2 bg-red-950 border border-red-800
                          rounded-lg text-red-400 text-xs">
            {error}
          </div>
        )}
      </div>

      {/* ── Sticky bottom CTA ────────────────────────────────────────── */}
      <div className="border-t border-zinc-800 px-6 py-4 bg-black">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="text-zinc-600 text-xs">
            {scripts.length > 0 && (
              <>Script {selectedIdx + 1} of {scripts.length} selected</>
            )}
          </div>
          <button
            onClick={handleAdvance}
            disabled={advancing || scripts.length === 0}
            className="bg-amber-400 hover:bg-amber-300 disabled:opacity-40
                       text-black font-semibold text-sm py-3 px-8 rounded-lg
                       transition-colors duration-150"
          >
            {advancing ? "Building strategy..." : "Continue to Strategy →"}
          </button>
        </div>
      </div>

    </div>
  )
}
