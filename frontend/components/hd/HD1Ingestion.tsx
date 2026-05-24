"use client"
import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { API_BASE } from "@/lib/api/client"

export default function HD1Ingestion() {
  const router = useRouter()
  const [tab, setTab] = useState<"upload" | "url">("upload")
  const [url, setUrl] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  async function submit() {
    setLoading(true)
    setError(null)
    const token = localStorage.getItem("aw_token")
    if (!token) { router.push("/"); return }
    try {
      const idempotencyKey = `hd1-${Date.now()}`
      let res: Response
      if (tab === "url") {
        if (!url.trim()) { setError("Please enter a product URL"); setLoading(false); return }
        const formData = new FormData()
        formData.append("source_url", url.trim())
        res = await fetch(`${API_BASE}/api/generations`, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Idempotency-Key": idempotencyKey },
          body: formData,
        })
      } else {
        if (!file) { setError("Please select an image"); setLoading(false); return }
        if (file.size > 10 * 1024 * 1024) { setError("Image must be under 10MB"); setLoading(false); return }
        const formData = new FormData()
        formData.append("source_image", file)
        res = await fetch(`${API_BASE}/api/generations`, {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}`, "Idempotency-Key": idempotencyKey },
          body: formData,
        })
      }
      if (res.status === 401) { localStorage.removeItem("aw_token"); router.push("/"); return }
      if (res.status === 413) { setError("Image too large. Maximum 10MB."); setLoading(false); return }
      const data = await res.json()
      if (data.gen_id) {
        router.push(`/${data.gen_id}`)
      } else {
        setError(data.detail?.message ?? "Something went wrong")
        setLoading(false)
      }
    } catch {
      setError("Cannot connect to server")
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--brand-bg)" }}>

      {/* Top nav */}
      <div className="border-b px-6 py-4 flex items-center justify-between"
           style={{ borderColor: "var(--brand-border)", background: "var(--brand-surface)" }}>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center"
               style={{ background: "var(--brand-primary)" }}>
            <span className="text-white font-bold text-xs">A</span>
          </div>
          <span className="font-bold text-white">
            Ad<span className="text-teal-400">creo</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-500 text-xs">Step</span>
          <div className="flex gap-1">
            {[1,2,3,4,5,6].map(n => (
              <div key={n}
                   className="w-6 h-1.5 rounded-full"
                   style={{ background: n === 1 ? "var(--brand-primary)" : "var(--brand-border)" }} />
            ))}
          </div>
          <span className="text-slate-500 text-xs">1 of 6</span>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              Add your product
            </h1>
            <p className="text-slate-400 text-sm">
              Upload an image or paste a product URL — we handle the rest
            </p>
          </div>

          {/* Tab switcher */}
          <div className="flex rounded-xl p-1 mb-6 border"
               style={{ background: "var(--brand-surface)", borderColor: "var(--brand-border)" }}>
            {(["upload", "url"] as const).map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setError(null) }}
                className="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all duration-150"
                style={{
                  background: tab === t ? "var(--brand-primary)" : "transparent",
                  color: tab === t ? "white" : "var(--brand-fg-muted)",
                }}
              >
                {t === "upload" ? "📸  Upload Image" : "🔗  Paste URL"}
              </button>
            ))}
          </div>

          {/* Upload tab */}
          {tab === "upload" && (
            <div
              onClick={() => fileRef.current?.click()}
              className="rounded-2xl border-2 border-dashed p-10 text-center
                         cursor-pointer transition-all duration-150 mb-6 group"
              style={{
                borderColor: file ? "var(--brand-primary)" : "var(--brand-border)",
                background: file ? "rgba(13,148,136,0.05)" : "var(--brand-surface)",
              }}
              onMouseEnter={e => {
                if (!file) (e.currentTarget as HTMLElement).style.borderColor = "var(--brand-primary)"
              }}
              onMouseLeave={e => {
                if (!file) (e.currentTarget as HTMLElement).style.borderColor = "var(--brand-border)"
              }}
            >
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f) {
                    setFile(f)
                    setError(null)
                    const reader = new FileReader()
                    reader.onload = () => setPreview(reader.result as string)
                    reader.readAsDataURL(f)
                  }
                }}
              />
              {file && preview ? (
                <div className="flex flex-col items-center gap-3">
                  <img src={preview} alt="preview"
                       className="w-24 h-24 object-contain rounded-xl border"
                       style={{ borderColor: "var(--brand-border)" }} />
                  <div>
                    <div className="text-white text-sm font-medium">{file.name}</div>
                    <div className="text-slate-500 text-xs mt-0.5">
                      {(file.size / 1024 / 1024).toFixed(1)} MB · Click to change
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-teal-400 text-xs font-medium">
                    <span>✓</span> Ready to analyse
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-14 h-14 rounded-2xl flex items-center justify-center"
                       style={{ background: "var(--brand-border)" }}>
                    <span className="text-2xl">↑</span>
                  </div>
                  <div>
                    <div className="text-white text-sm font-medium">
                      Drop your product image here
                    </div>
                    <div className="text-slate-500 text-xs mt-1">
                      PNG, JPG up to 10MB · Plain background works best
                    </div>
                  </div>
                  <div className="px-4 py-1.5 rounded-lg text-sm font-medium border
                                  transition-colors"
                       style={{
                         borderColor: "var(--brand-primary)",
                         color: "var(--brand-primary)",
                       }}>
                    Browse files
                  </div>
                </div>
              )}
            </div>
          )}

          {/* URL tab */}
          {tab === "url" && (
            <div className="mb-6 space-y-3">
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                  🔗
                </span>
                <input
                  type="url"
                  placeholder="https://yourstore.com/product-page"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full rounded-xl pl-10 pr-4 py-3.5 text-white
                             text-sm placeholder:text-slate-600 focus:outline-none
                             transition-colors border"
                  style={{
                    background: "var(--brand-surface)",
                    borderColor: url ? "var(--brand-primary)" : "var(--brand-border)",
                  }}
                />
              </div>
              <p className="text-slate-500 text-xs pl-1">
                Works with Shopify, Amazon, Flipkart and most product pages
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-4 px-4 py-3 bg-red-950 border border-red-800
                            rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* CTA */}
          <button
            onClick={submit}
            disabled={loading || (tab === "upload" && !file) || (tab === "url" && !url.trim())}
            className="w-full py-4 rounded-xl font-semibold text-white text-sm
                       transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: loading || (tab === "upload" && !file) || (tab === "url" && !url.trim())
                ? "var(--brand-border)"
                : "linear-gradient(135deg, var(--brand-primary), var(--brand-primary-hover))",
              boxShadow: "0 4px 15px rgba(13,148,136,0.3)",
            }}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent
                                 rounded-full animate-spin" />
                Analysing your product...
              </span>
            ) : (
              "Analyse Product →"
            )}
          </button>

          {/* Trust badges */}
          <div className="flex items-center justify-center gap-4 mt-6">
            {["✓ Free during beta", "✓ SGI Compliant", "✓ AI-powered"].map(t => (
              <span key={t} className="text-slate-600 text-xs">{t}</span>
            ))}
          </div>

        </div>
      </div>
    </div>
  )
}
