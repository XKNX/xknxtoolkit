import { source } from "@/lib/source/docs";
import { createFromSource } from "fumadocs-core/search/server";
import type { SortedResult } from "fumadocs-core/server";

const docsSearch = createFromSource(source, { language: "english" });

const CATALOG_API = process.env.CATALOG_API_URL ?? "http://localhost:8000";

interface HardwareResult {
  id: string;
  name: string | null;
  order_number: string | null;
  manufacturer_id: string;
}

async function searchCatalog(query: string): Promise<SortedResult[]> {
  const qs = new URLSearchParams({ search: query, limit: "5" });
  const items: HardwareResult[] = await fetch(`${CATALOG_API}/hardware?${qs}`).then((r) =>
    r.json(),
  );
  return items.map((h) => ({
    id: `catalog-${h.id}`,
    url: `/handbook/catalog/hardware/${encodeURIComponent(h.id)}`,
    type: "page" as const,
    content: h.name ?? h.order_number ?? h.id,
    breadcrumbs: ["Catalog", h.manufacturer_id],
  }));
}

export async function GET(request: Request): Promise<Response> {
  const query = new URL(request.url).searchParams.get("query") ?? "";

  if (!query) return docsSearch.GET(request);

  const [docsResults, catalogResults] = await Promise.all([
    docsSearch.GET(request).then((r) => r.json() as Promise<SortedResult[]>),
    searchCatalog(query).catch(() => [] as SortedResult[]),
  ]);

  return Response.json([...catalogResults, ...docsResults]);
}
