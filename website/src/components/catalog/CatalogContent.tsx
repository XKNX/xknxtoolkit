"use client";

import { Suspense, useEffect, useState, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import MultiSelect from "./MultiSelect";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";

const API = process.env.NEXT_PUBLIC_CATALOG_API_URL ?? "http://localhost:8000";

const MEDIUM_TYPES = ["TP", "PL110", "RF", "IP"];

interface Manufacturer {
  id: string;
  name: string | null;
}
interface HardwareProgram {
  id: string;
  medium_types: string[];
  application: { is_secure_enabled: boolean | null } | null;
}
interface Hardware {
  id: string;
  manufacturer_id: string;
  name: string | null;
  order_number: string | null;
  description: string | null;
  is_rail_mounted: boolean | null;
  programs: HardwareProgram[];
}

const LIMIT = 50;

const columnHelper = createColumnHelper<Hardware>();

function parseList(param: string | null): string[] {
  return param ? param.split(",").filter(Boolean) : [];
}

function CatalogContentInner() {
  const params = useSearchParams();
  const router = useRouter();

  const mfrIds = useMemo(() => parseList(params.get("m")), [params]);
  const mediums = useMemo(() => parseList(params.get("medium")), [params]);
  const sectionId = params.get("s") ?? "";
  const search = params.get("q") ?? "";
  const secureOnly = params.get("secure") === "true";
  const railMounted = params.get("rail") === "true";
  const page = Number(params.get("page") ?? "0");

  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [items, setItems] = useState<Hardware[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/manufacturers`)
      .then((r) => r.json())
      .then(setManufacturers);
  }, []);

  const mfrMap = useMemo(
    () => Object.fromEntries(manufacturers.map((m) => [m.id, m.name ?? m.id])),
    [manufacturers],
  );

  const mfrKey = mfrIds.join(",");
  const mediumKey = mediums.join(",");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const qs = new URLSearchParams({ limit: String(LIMIT), offset: String(page * LIMIT) });
    if (sectionId) {
      qs.set("section_id", sectionId);
    } else {
      for (const id of mfrIds) qs.append("manufacturer_id", id);
    }
    for (const mt of mediums) qs.append("medium_type", mt);
    if (secureOnly) qs.set("is_secure_enabled", "true");
    if (railMounted) qs.set("is_rail_mounted", "true");
    if (search) qs.set("search", search);

    fetch(`${API}/hardware?${qs}`)
      .then((r) => r.json())
      .then((data: Hardware[]) => {
        if (cancelled) return;
        setItems(data);
        setHasMore(data.length === LIMIT);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, mfrKey, sectionId, mediumKey, secureOnly, railMounted, search]);

  function push(updates: Record<string, string | null>, keepPage = false) {
    const next = new URLSearchParams(params.toString());
    for (const [k, v] of Object.entries(updates)) {
      if (v === null || v === "") next.delete(k);
      else next.set(k, v);
    }
    if (!keepPage) next.delete("page");
    router.push(`/docs/catalog/browse-hardware?${next}`);
  }

  function pushList(key: string, values: string[]) {
    push({ [key]: values.join(",") || null });
  }

  function goToPage(p: number) {
    push({ page: p > 0 ? String(p) : null }, true);
  }

  const columns = useMemo(
    () => [
      columnHelper.accessor((h) => h.name ?? "—", {
        id: "name",
        header: "Name",
        cell: (info) => {
          const h = info.row.original;
          return (
            <div>
              <div className="font-medium text-sm text-fd-foreground truncate">
                {info.getValue()}
              </div>
              {h.description && (
                <div className="text-xs text-fd-muted-foreground truncate mt-0.5">
                  {h.description}
                </div>
              )}
            </div>
          );
        },
      }),
      columnHelper.accessor("manufacturer_id", {
        id: "manufacturer",
        header: () => (
          <MultiSelect
            options={manufacturers.map((m) => ({ value: m.id, label: m.name ?? m.id }))}
            value={mfrIds}
            onChange={(v) => pushList("m", v)}
            placeholder="All manufacturers"
            className="w-full"
          />
        ),
        cell: (info) => (
          <span className="text-xs text-fd-muted-foreground">{mfrMap[info.getValue()] ?? "—"}</span>
        ),
      }),
      columnHelper.accessor("order_number", {
        header: "Order #",
        cell: (info) => (
          <span className="text-xs text-fd-muted-foreground">{info.getValue() ?? "—"}</span>
        ),
      }),
      columnHelper.display({
        id: "medium",
        header: () => (
          <MultiSelect
            options={MEDIUM_TYPES.map((mt) => ({ value: mt, label: mt }))}
            value={mediums}
            onChange={(v) => pushList("medium", v)}
            placeholder="All media"
            className="w-full"
          />
        ),
        cell: ({ row: { original: h } }) => {
          const mts = [...new Set(h.programs.flatMap((p) => p.medium_types))];
          return (
            <div className="flex gap-1">
              {mts.map((mt) => (
                <span
                  key={mt}
                  className="text-xs px-1.5 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground"
                >
                  {mt}
                </span>
              ))}
            </div>
          );
        },
      }),
      columnHelper.display({
        id: "tags",
        header: () => (
          <div className="flex items-center gap-3 whitespace-nowrap">
            <label className="flex items-center gap-1 text-xs font-medium text-fd-foreground cursor-pointer select-none">
              <input
                type="checkbox"
                className="accent-fd-primary"
                checked={secureOnly}
                onChange={(e) => push({ secure: e.target.checked ? "true" : null })}
              />
              Secure
            </label>
            <label className="flex items-center gap-1 text-xs font-medium text-fd-foreground cursor-pointer select-none">
              <input
                type="checkbox"
                className="accent-fd-primary"
                checked={railMounted}
                onChange={(e) => push({ rail: e.target.checked ? "true" : null })}
              />
              Rail
            </label>
          </div>
        ),
        cell: ({ row: { original: h } }) => {
          const isSecure = h.programs.some((p) => p.application?.is_secure_enabled);
          return (
            <div className="flex gap-1 flex-wrap">
              {isSecure && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
                  Secure
                </span>
              )}
              {h.is_rail_mounted && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground">
                  DIN Rail
                </span>
              )}
            </div>
          );
        },
      }),
      // eslint-disable-next-line react-hooks/exhaustive-deps
    ],
    [manufacturers, mfrMap, mfrIds, mediums, secureOnly, railMounted],
  );

  const table = useReactTable({
    data: items,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div
      id="products"
      className="flex flex-col border border-fd-border rounded-lg overflow-hidden"
      style={{ height: "calc(100dvh - var(--fd-nav-height, 3.5rem) - 2rem)" }}
    >
      <div className="flex-1 overflow-y-auto overflow-x-auto">
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col className="w-[38%]" />
            <col className="w-[20%]" />
            <col className="w-[10%]" />
            <col className="w-[10%]" />
            <col className="w-[22%]" />
          </colgroup>
          <thead className="bg-fd-muted/50 border-b border-fd-border sticky top-0 z-10">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-3 py-2.5 text-left font-medium text-fd-foreground align-top"
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowCount() === 0 && !loading && (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-6 text-sm text-fd-muted-foreground text-center"
                >
                  No products found.
                </td>
              </tr>
            )}
            {table.getRowModel().rows.map((row, i) => (
              <tr
                key={row.id}
                className={`cursor-pointer hover:bg-fd-accent transition-colors ${i > 0 ? "border-t border-fd-border" : ""}`}
                onClick={() =>
                  router.push(`/docs/catalog/hardware/${encodeURIComponent(row.original.id)}`)
                }
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-3 py-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between px-4 py-2.5 border-t border-fd-border bg-fd-muted/30">
        <button
          className="text-xs px-3 py-1.5 rounded border border-fd-border text-fd-foreground hover:bg-fd-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          disabled={page === 0 || loading}
          onClick={() => goToPage(page - 1)}
        >
          ← Previous
        </button>
        <span className="text-xs text-fd-muted-foreground">
          {loading ? "Loading…" : `Page ${page + 1}`}
        </span>
        <button
          className="text-xs px-3 py-1.5 rounded border border-fd-border text-fd-foreground hover:bg-fd-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          disabled={!hasMore || loading}
          onClick={() => goToPage(page + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}

export default function CatalogContent() {
  return (
    <Suspense>
      <CatalogContentInner />
    </Suspense>
  );
}
