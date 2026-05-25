import { source } from "@/lib/source/docs";
import { createFromSource } from "fumadocs-core/search/server";
import type { SortedResult } from "fumadocs-core/server";

const docsSearch = createFromSource(source, { language: "english" });

const CATALOG_API = process.env.CATALOG_API_URL ?? "http://localhost:8000";

interface Product {
  id: string;
  product_name: string | null;
  catalog_item_name: string | null;
  order_number: string | null;
}

async function searchCatalog(query: string): Promise<SortedResult[]> {
  const qs = new URLSearchParams({ search: query, limit: "5" });
  const products: Product[] = await fetch(`${CATALOG_API}/products?${qs}`).then((r) => r.json());
  return products.map((p) => ({
    id: `catalog-${p.id}`,
    url: `/catalog/products/${encodeURIComponent(p.id)}`,
    type: "page" as const,
    content: p.catalog_item_name ?? p.product_name ?? p.order_number ?? "",
    breadcrumbs: ["Catalog"],
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
