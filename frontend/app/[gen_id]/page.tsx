import { HD2Isolation } from "@/components/hd/HD2Isolation"

// Required by Next.js static export for dynamic routes
export function generateStaticParams() {
  return []
}

type Props = {
  params: Promise<{ gen_id: string }>
}

export default async function GenerationPage({ params }: Props) {
  const { gen_id } = await params
  return <HD2Isolation genId={gen_id} />
}
