// frontend/components/hd/HD5Kiln.tsx
"use client"
import { useEffect, useState } from "react"
import { connectSSE } from "@/lib/sse/client"

interface Props {
  genId: string
  initialStatus: string
  onComplete: () => void
}

type Stage = {
  key: string
  label: string
  substatus: string[]
}

const STAGES: Stage[] = [
  { key: "tts",     label: "Generating voiceover",  substatus: ["funds_locked", "rendering"] },
  { key: "i2v",     label: "Generating video clips", substatus: ["rendering"] },
  { key: "reflect", label: "Quality check",          substatus: ["reflecting"] },
  { key: "compose", label: "Composing final ad",     substatus: ["composing"] },
]

function getStageIndex(status: string): number {
  if (["funds_locked", "rendering"].includes(status)) return 0
  if (status === "reflecting") return 2
  if (status === "composing")  return 3
  return 0
}

export default function HD5Kiln({ genId, initialStatus, onComplete }: Props) {
  const [currentStatus, setCurrentStatus] = useState(initialStatus)
  const activeIdx = getStageIndex(currentStatus)

  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    const cleanup = connectSSE({
      genId,
      token,
      onEvent: (evt) => {
        const st = evt.status ?? (evt as { state?: string }).state
        if (!st) return
        setCurrentStatus(st)
        if (["preview_ready", "export_queued", "export_ready"].includes(st)) {
          onComplete()
        }
        if (["failed_render", "failed_export"].includes(st)) {
          setCurrentStatus(st)
        }
      },
    })
    return cleanup
  }, [genId, onComplete])

  const isFailed = ["failed_render", "failed_export"].includes(currentStatus)

  return (
    <div className="min-h-screen bg-black flex flex-col">

      {/* ── Top bar ────────────────────────────────────────────── */}
      <div className="border-b border-zinc-800 px-6 py-3">
        <span className="text-amber-400 text-xs font-medium tracking-widest uppercase">
          Step 5 of 6
        </span>
        <h1 className="text-white font-bold text-lg leading-tight">
          Rendering your ad
        </h1>
      </div>

      {/* ── Stage rows ─────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-md space-y-4">

          {isFailed ? (
            <div className="p-6 bg-red-950 border border-red-800 rounded-xl text-center">
              <div className="text-red-400 font-semibold mb-2">Render failed</div>
              <div className="text-zinc-400 text-sm">
                Your credit has been refunded. Please try again from HD-4.
              </div>
            </div>
          ) : (
            <>
              {STAGES.map((stage, idx) => {
                const done    = idx < activeIdx
                const active  = idx === activeIdx
                const pending = idx > activeIdx

                return (
                  <div
                    key={stage.key}
                    className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                      active  ? "border-amber-400 bg-zinc-900"
                      : done  ? "border-zinc-700 bg-zinc-950"
                      : "border-zinc-800 bg-zinc-950 opacity-40"
                    }`}
                  >
                    {/* Status icon */}
                    <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0">
                      {done ? (
                        <span className="text-green-400 text-lg">✓</span>
                      ) : active ? (
                        <div className="w-4 h-4 border-2 border-amber-400 border-t-transparent
                                        rounded-full animate-spin" />
                      ) : (
                        <div className="w-3 h-3 rounded-full bg-zinc-700" />
                      )}
                    </div>

                    {/* Label */}
                    <div>
                      <div className={`text-sm font-medium ${
                        active ? "text-white" : done ? "text-zinc-400" : "text-zinc-600"
                      }`}>
                        {stage.label}
                      </div>
                      {active && (
                        <div className="text-amber-400 text-xs mt-0.5 animate-pulse">
                          In progress...
                        </div>
                      )}
                      {done && (
                        <div className="text-zinc-600 text-xs mt-0.5">Complete</div>
                      )}
                    </div>
                  </div>
                )
              })}

              <div className="text-center text-zinc-600 text-xs pt-4">
                This takes 2–3 minutes. Do not close this tab.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
