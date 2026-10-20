import { redirect } from "next/navigation";

export default async function LegacyDocumentAccessRequestPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  redirect(`/documents/${encodeURIComponent(slug)}/lire`);
}
