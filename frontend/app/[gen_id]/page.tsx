import { HD2IsolationWrapper } from "@/components/hd/HD2IsolationWrapper"

// Tells Next.js static export to generate the template shell
export function generateStaticParams() {
  return []
}

export default function GenerationPage() {
  return <HD2IsolationWrapper />
}
