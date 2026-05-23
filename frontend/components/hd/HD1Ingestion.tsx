"use client"
import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { API_BASE } from "@/lib/api/client"

export default function HD1Ingestion() {
  const router  = useRouter()
  const [tab, setTab]         = useState<"upload" | "url">("upload")
  const [url, setUrl]         = useState("")
  const [file, setFile]       = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
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
          headers: {
            "Authorization": `Bearer ${token}`,
            "Idempotency-Key": idempotencyKey,
          },
          body: formData,
        })
      } else {
        if (!file) { setError("Please select an image"); setLoading(false); return }
        if (file.size > 10 * 1024 * 1024) {
          setError("Image must be under 10MB")
          setLoading(false)
          return
        }
        const formData = new FormData()
        formData.append("source_image", file)
        res = await fetch(`${API_BASE}/api/generations`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Idempotency-Key": idempotencyKey,
          },
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
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="w-full max-w-lg">

        {/* Header */}
        <div className="mb-8">
          <div className="text-amber-400 text-xs font-medium tracking-widest uppercase mb-2">
            Step 1 of 6
          </div>
          <h1 className="text-white text-2xl font-bold">Add your product</h1>
          <p className="text-zinc-500 text-sm mt-1">
            Upload a product image or paste a URL
          </p>
        </div>

        {/* Tab switcher */}
        <div className="flex bg-zinc-900 rounded-lg p-1 mb-6 border border-zinc-800">
          <button
            onClick={() => { setTab("upload"); setError(null) }}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              tab === "upload"
                ? "bg-zinc-700 text-white"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Upload Image
          </button>
          <button
            onClick={() => { setTab("url"); setError(null) }}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              tab === "url"
                ? "bg-zinc-700 text-white"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Paste URL
          </button>
        </div>

        {/* Upload tab */}
        {tab === "upload" && (
          <div
            onClick={() => fileRef.current?.click()}
            className="border-2 border-dashed border-zinc-700 hover:border-amber-400
                       rounded-xl p-12 text-center cursor-pointer transition-colors mb-6"
          >
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) { setFile(f); setError(null) }
              }}
            />
            {file ? (
              <div className="text-white">
                <div className="text-2xl mb-2">🖼️</div>
                <div className="text-sm font-medium">{file.name}</div>
                <div className="text-zinc-500 text-xs mt-1">
                  {(file.size / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            ) : (
              <div className="text-zinc-500">
                <div className="text-3xl mb-3">↑</div>
                <div className="text-sm">Click to upload product image</div>
                <div className="text-xs mt-1">PNG, JPG up to 10MB</div>
              </div>
            )}
          </div>
        )}

        {/* URL tab */}
        {tab === "url" && (
          <div className="mb-6">
            <input
              type="url"
              placeholder="https://yourstore.com/product-page"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg
                         px-4 py-3 text-white text-sm placeholder:text-zinc-600
                         focus:outline-none focus:border-amber-400 transition-colors"
            />
            <p className="text-zinc-600 text-xs mt-2">
              We'll extract the product image automatically
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-4 px-3 py-2 bg-red-950 border border-red-800
                          rounded-lg text-red-400 text-xs">
            {error}
          </div>
        )}

        {/* CTA */}
        <button
          onClick={submit}
          disabled={loading || (tab === "upload" && !file) || (tab === "url" && !url)}
          className="w-full bg-amber-400 hover:bg-amber-300 disabled:opacity-40
                     text-black font-semibold text-sm py-3 px-4 rounded-lg
                     transition-colors duration-150"
        >
          {loading ? "Analysing product..." : "Analyse Product →"}
        </button>

      </div>
    </div>
  )
}
