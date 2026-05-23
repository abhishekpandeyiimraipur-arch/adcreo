"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import HD1Ingestion from "@/components/hd/HD1Ingestion"

export default function NewGenerationPage() {
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("aw_token")
    if (!token) { router.push("/") }
  }, [router])

  return <HD1Ingestion />
}
