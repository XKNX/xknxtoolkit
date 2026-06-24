import Link from "next/link";
import { notFound } from "next/navigation";
import { DocsPage } from "fumadocs-ui/layouts/docs/page";
import { SegmentHexViewer } from "@/components/catalog/ApplicationHexViewer";

const API = process.env.CATALOG_API_URL ?? "http://localhost:8000";

// ─── IR types (PascalCase, matching xsdata JSON output) ──────────────────────

interface IrComObject {
  Id: string;
  Name: string;
  Text: string;
  Number: number;
  DatapointType: string[];
  CommunicationFlag: string;
  ReadFlag: string;
  WriteFlag: string;
  TransmitFlag: string;
  UpdateFlag: string;
  ReadOnInitFlag: string;
}

interface IrParameter {
  Id: string;
  Name: string;
  Text: string;
  Value: string;
  ParameterType: string;
}

interface IrUnion {
  Parameter: IrParameter[];
}

interface IrParameterRef {
  Id: string;
  RefId: string;
  Value: string | null;
  Name: string | null;
  Text: string | null;
}

interface IrEnumOption {
  Value: number;
  Text: string;
}

interface IrParamTypeChoice {
  Enumeration?: IrEnumOption[];
  SizeInBit?: number;
  Type?: string;
  minInclusive?: number | null;
  maxInclusive?: number | null;
  Minimum?: number | null;
  Maximum?: number | null;
  UIHint?: string | null;
}

interface IrParameterType {
  Id: string;
  Name: string;
  choice: IrParamTypeChoice | null;
}

interface IrSegmentBase {
  Id: string;
  Size: number;
  Data: string | null;
  Name: string | null;
}

interface IrAbsoluteSegment extends IrSegmentBase {
  Address: number;
  UserMemory: boolean;
}

interface IrRelativeSegment extends IrSegmentBase {
  Offset: number;
}

interface IrModuleDefStatic {
  Parameters?: { choice: (IrParameter | IrUnion)[] };
  ParameterRefs?: { ParameterRef: IrParameterRef[] };
  ComObjects?: { ComObject: IrComObject[] };
}

interface IrModuleDef {
  Id: string;
  Name: string | null;
  Static: IrModuleDefStatic;
  Arguments?: { Argument: { Id: string; Name: string }[] };
}

interface IrApp {
  Id: string;
  Name: string;
  MaskVersion: string;
  ApplicationNumber: number;
  ApplicationVersion: number;
  IsSecureEnabled: boolean;
  Static: {
    ComObjectTable?: { ComObject: IrComObject[] };
    Parameters?: { choice: (IrParameter | IrUnion)[] };
    ParameterRefs?: { ParameterRef: IrParameterRef[] };
    ParameterTypes?: { ParameterType: IrParameterType[] };
    Code?: {
      AbsoluteSegment: IrAbsoluteSegment[];
      RelativeSegment: IrRelativeSegment[];
    };
  };
  ModuleDefs?: { ModuleDef: IrModuleDef[] };
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function flatParams(choice: (IrParameter | IrUnion)[]): IrParameter[] {
  const out: IrParameter[] = [];
  for (const item of choice ?? []) {
    if ("ParameterType" in item) out.push(item);
    else if ("Parameter" in item) out.push(...item.Parameter);
  }
  return out;
}

function enabled(flag: string) {
  return flag === "Enabled";
}

function describeType(choice: IrParamTypeChoice | null): string {
  if (!choice) return "—";
  if (choice.Enumeration) return `enum (${choice.Enumeration.length})`;
  const min = choice.minInclusive ?? choice.Minimum;
  const max = choice.maxInclusive ?? choice.Maximum;
  const range = min != null && max != null ? ` [${min}–${max}]` : "";
  const bits = choice.SizeInBit != null ? ` ${choice.SizeInBit}b` : "";
  const type = choice.Type ?? "int";
  return `${type}${bits}${range}`;
}

// ─── Small UI components ──────────────────────────────────────────────────────

function FlagCell({ active, label, abbr }: { active: boolean; label: string; abbr: string }) {
  return (
    <span
      title={label}
      className={`inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold ${
        active ? "bg-fd-primary/15 text-fd-primary" : "text-fd-muted-foreground/30"
      }`}
    >
      {abbr}
    </span>
  );
}

function DptBadge({ code }: { code: string }) {
  return (
    <span className="text-[11px] px-1.5 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground font-mono">
      {code}
    </span>
  );
}

function SectionHeader({ id, title, count }: { id: string; title: string; count: number }) {
  return (
    <h2 id={id} className="text-lg font-semibold text-fd-foreground mb-3">
      {title}
      <span className="ml-2 text-sm font-normal text-fd-muted-foreground">({count})</span>
    </h2>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default async function ApplicationPage({
  params,
}: {
  params: Promise<{ id: string; programId: string }>;
}) {
  const { id, programId } = await params;

  const res = await fetch(
    `${API}/hardware/${encodeURIComponent(id)}/programs/${encodeURIComponent(programId)}/application`,
    { headers: { Accept: "application/json" } },
  );
  if (!res.ok) notFound();

  const app: IrApp = await res.json();

  const comObjects = app.Static.ComObjectTable?.ComObject ?? [];
  const absSegs = app.Static.Code?.AbsoluteSegment ?? [];
  const relSegs = app.Static.Code?.RelativeSegment ?? [];
  const allParams = flatParams(app.Static.Parameters?.choice ?? []);
  const paramRefs = app.Static.ParameterRefs?.ParameterRef ?? [];
  const paramTypes = app.Static.ParameterTypes?.ParameterType ?? [];
  const moduleDefs = app.ModuleDefs?.ModuleDef ?? [];

  const paramById = new Map(allParams.map((p) => [p.Id, p]));
  const typeById = new Map(paramTypes.map((pt) => [pt.Id, pt]));

  const totalSegs = absSegs.length + relSegs.length;
  const manufacturerId = app.Id.split("_")[0];

  const toc = [
    ...(totalSegs > 0 ? [{ title: `Code Segments (${totalSegs})`, url: "#code", depth: 2 }] : []),
    ...(comObjects.length > 0
      ? [{ title: `Communication Objects (${comObjects.length})`, url: "#com-objects", depth: 2 }]
      : []),
    ...(paramRefs.length > 0
      ? [{ title: `Parameters (${paramRefs.length})`, url: "#parameters", depth: 2 }]
      : []),
    ...(moduleDefs.length > 0
      ? [{ title: `Module Definitions (${moduleDefs.length})`, url: "#modules", depth: 2 }]
      : []),
  ];

  return (
    <DocsPage footer={{ enabled: false }} breadcrumb={{ enabled: false }} toc={toc}>
      <Link
        href={`/handbook/catalog/hardware/${encodeURIComponent(id)}`}
        className="text-sm text-fd-muted-foreground hover:text-fd-foreground transition-colors"
      >
        ← Back to hardware
      </Link>

      <h1 className="text-2xl font-semibold text-fd-foreground mt-4">{app.Name}</h1>
      <div className="text-fd-muted-foreground mt-1 text-sm">{manufacturerId}</div>
      <div className="flex items-center gap-3 mt-2 flex-wrap">
        <span className="text-xs text-fd-muted-foreground font-mono">
          v{app.ApplicationNumber}.{app.ApplicationVersion}
        </span>
        {app.MaskVersion && (
          <span className="text-xs text-fd-muted-foreground font-mono">{app.MaskVersion}</span>
        )}
        {app.IsSecureEnabled && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
            Secure
          </span>
        )}
      </div>
      <div className="mt-1 text-xs text-fd-muted-foreground/40 font-mono break-all">{app.Id}</div>

      {/* ── Code Segments ─────────────────────────────────────────────── */}
      {totalSegs > 0 && (
        <div id="code" className="mt-8">
          <SectionHeader id="code-h" title="Code Segments" count={totalSegs} />
          <div className="space-y-6">
            {[...absSegs].sort((a, b) => a.Address - b.Address).map((seg) => (
              <div key={seg.Id}>
                <div className="flex items-baseline gap-3 mb-2">
                  <span className="text-sm font-medium text-fd-foreground">
                    {seg.Name ?? seg.Id.split("_AS-")[1] ?? seg.Id}
                  </span>
                  <span className="text-xs text-fd-muted-foreground font-mono">
                    addr 0x{seg.Address.toString(16).toUpperCase()} · {seg.Size} B
                  </span>
                  {seg.UserMemory && (
                    <span className="text-xs px-1.5 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground">
                      user memory
                    </span>
                  )}
                </div>
                {seg.Data ? (
                  <SegmentHexViewer data={seg.Data} height="280px" />
                ) : (
                  <div className="text-xs text-fd-muted-foreground/50 italic">No data</div>
                )}
              </div>
            ))}
            {[...relSegs].sort((a, b) => a.Offset - b.Offset).map((seg) => (
              <div key={seg.Id}>
                <div className="flex items-baseline gap-3 mb-2">
                  <span className="text-sm font-medium text-fd-foreground">
                    {seg.Name ?? seg.Id.split("_RS-")[1] ?? seg.Id}
                  </span>
                  <span className="text-xs text-fd-muted-foreground font-mono">
                    offset 0x{seg.Offset.toString(16).toUpperCase()} · {seg.Size} B
                  </span>
                </div>
                {seg.Data ? (
                  <SegmentHexViewer data={seg.Data} height="280px" />
                ) : (
                  <div className="text-xs text-fd-muted-foreground/50 italic">No data</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Com Objects ───────────────────────────────────────────────── */}
      {comObjects.length > 0 && (
        <div id="com-objects" className="mt-8">
          <SectionHeader id="com-objects-h" title="Communication Objects" count={comObjects.length} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-fd-border text-left">
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground w-12">#</th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">Name</th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">DPT</th>
                  <th className="pb-2 text-xs font-medium text-fd-muted-foreground">
                    <span title="C=Communication R=Read W=Write T=Transmit U=Update I=Read on Init">
                      Flags
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-fd-border/50">
                {comObjects.map((co) => (
                  <tr key={co.Id} className="hover:bg-fd-muted/30 transition-colors">
                    <td className="py-2 pr-4 text-fd-muted-foreground font-mono text-xs">
                      {co.Number}
                    </td>
                    <td className="py-2 pr-4 text-fd-foreground">{co.Name}</td>
                    <td className="py-2 pr-4">
                      <div className="flex flex-wrap gap-1">
                        {co.DatapointType.length > 0 ? (
                          co.DatapointType.map((d, i) => <DptBadge key={`${d}-${i}`} code={d} />)
                        ) : (
                          <span className="text-xs text-fd-muted-foreground/40">—</span>
                        )}
                      </div>
                    </td>
                    <td className="py-2">
                      <div className="flex gap-0.5">
                        <FlagCell active={enabled(co.CommunicationFlag)} label="Communication" abbr="C" />
                        <FlagCell active={enabled(co.ReadFlag)} label="Read" abbr="R" />
                        <FlagCell active={enabled(co.WriteFlag)} label="Write" abbr="W" />
                        <FlagCell active={enabled(co.TransmitFlag)} label="Transmit" abbr="T" />
                        <FlagCell active={enabled(co.UpdateFlag)} label="Update" abbr="U" />
                        <FlagCell active={enabled(co.ReadOnInitFlag)} label="Read on Init" abbr="I" />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Parameters ────────────────────────────────────────────────── */}
      {paramRefs.length > 0 && (
        <div id="parameters" className="mt-8">
          <SectionHeader id="parameters-h" title="Parameters" count={paramRefs.length} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-fd-border text-left">
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">Name</th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">Text</th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">Default</th>
                  <th className="pb-2 text-xs font-medium text-fd-muted-foreground">Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-fd-border/50">
                {paramRefs.map((ref) => {
                  const param = paramById.get(ref.RefId);
                  const pt = param ? typeById.get(param.ParameterType) : undefined;
                  const name = ref.Name ?? param?.Name ?? "—";
                  const text = ref.Text ?? param?.Text ?? "";
                  const value = ref.Value ?? param?.Value ?? "";
                  const enumMatch = pt?.choice?.Enumeration?.find(
                    (o) => String(o.Value) === value,
                  );
                  return (
                    <tr key={ref.Id} className="hover:bg-fd-muted/30 transition-colors">
                      <td className="py-2 pr-4 text-fd-foreground text-xs">{name}</td>
                      <td className="py-2 pr-4 text-fd-muted-foreground text-xs">
                        {text || <span className="opacity-40">—</span>}
                      </td>
                      <td className="py-2 pr-4 font-mono text-xs">
                        {enumMatch ? (
                          <>
                            {enumMatch.Text}
                            <span className="text-fd-muted-foreground/50 ml-1">({value})</span>
                          </>
                        ) : (
                          value || <span className="text-fd-muted-foreground/40">—</span>
                        )}
                      </td>
                      <td className="py-2 text-fd-muted-foreground text-xs">
                        {pt ? describeType(pt.choice) : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Module Definitions ────────────────────────────────────────── */}
      {moduleDefs.length > 0 && (
        <div id="modules" className="mt-8">
          <SectionHeader id="modules-h" title="Module Definitions" count={moduleDefs.length} />
          <div className="space-y-6">
            {moduleDefs.map((md) => {
              const mdParams = flatParams(md.Static.Parameters?.choice ?? []);
              const mdRefs = md.Static.ParameterRefs?.ParameterRef ?? [];
              const mdCos = md.Static.ComObjects?.ComObject ?? [];
              const mdArgs = md.Arguments?.Argument ?? [];
              const mdParamById = new Map(mdParams.map((p) => [p.Id, p]));

              return (
                <div key={md.Id} className="rounded-lg border border-fd-border p-4">
                  <div className="flex items-baseline gap-3 mb-3">
                    <span className="font-medium text-sm text-fd-foreground">
                      {md.Name ?? md.Id}
                    </span>
                    <span className="text-xs text-fd-muted-foreground font-mono">{md.Id}</span>
                  </div>

                  <div className="flex gap-4 text-xs text-fd-muted-foreground mb-3 flex-wrap">
                    {mdArgs.length > 0 && <span>{mdArgs.length} argument{mdArgs.length !== 1 ? "s" : ""}</span>}
                    {mdRefs.length > 0 && <span>{mdRefs.length} parameter ref{mdRefs.length !== 1 ? "s" : ""}</span>}
                    {mdCos.length > 0 && <span>{mdCos.length} com object{mdCos.length !== 1 ? "s" : ""}</span>}
                  </div>

                  {mdArgs.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-medium text-fd-muted-foreground mb-1">Arguments</div>
                      <div className="flex flex-wrap gap-1.5">
                        {mdArgs.map((arg) => (
                          <span
                            key={arg.Id}
                            className="text-xs px-2 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground font-mono"
                          >
                            {arg.Name ?? arg.Id}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {mdCos.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-medium text-fd-muted-foreground mb-1">Com Objects</div>
                      <table className="w-full text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-fd-border/50 text-left">
                            <th className="pb-1 pr-3 font-medium text-fd-muted-foreground w-10">#</th>
                            <th className="pb-1 pr-3 font-medium text-fd-muted-foreground">Name</th>
                            <th className="pb-1 pr-3 font-medium text-fd-muted-foreground">DPT</th>
                            <th className="pb-1 font-medium text-fd-muted-foreground">Flags</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-fd-border/30">
                          {mdCos.map((co) => (
                            <tr key={co.Id}>
                              <td className="py-1 pr-3 font-mono text-fd-muted-foreground">{co.Number}</td>
                              <td className="py-1 pr-3 text-fd-foreground">{co.Name}</td>
                              <td className="py-1 pr-3">
                                <div className="flex flex-wrap gap-1">
                                  {co.DatapointType.length > 0
                                    ? co.DatapointType.map((d, i) => (
                                        <DptBadge key={`${d}-${i}`} code={d} />
                                      ))
                                    : <span className="opacity-40">—</span>}
                                </div>
                              </td>
                              <td className="py-1">
                                <div className="flex gap-0.5">
                                  <FlagCell active={enabled(co.CommunicationFlag)} label="Communication" abbr="C" />
                                  <FlagCell active={enabled(co.ReadFlag)} label="Read" abbr="R" />
                                  <FlagCell active={enabled(co.WriteFlag)} label="Write" abbr="W" />
                                  <FlagCell active={enabled(co.TransmitFlag)} label="Transmit" abbr="T" />
                                  <FlagCell active={enabled(co.UpdateFlag)} label="Update" abbr="U" />
                                  <FlagCell active={enabled(co.ReadOnInitFlag)} label="Read on Init" abbr="I" />
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {mdRefs.length > 0 && (
                    <div>
                      <div className="text-xs font-medium text-fd-muted-foreground mb-1">Parameters</div>
                      <table className="w-full text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-fd-border/50 text-left">
                            <th className="pb-1 pr-3 font-medium text-fd-muted-foreground">Name</th>
                            <th className="pb-1 pr-3 font-medium text-fd-muted-foreground">Text</th>
                            <th className="pb-1 font-medium text-fd-muted-foreground">Default</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-fd-border/30">
                          {mdRefs.map((ref) => {
                            const param = mdParamById.get(ref.RefId);
                            const mdPt = param ? typeById.get(param.ParameterType) : undefined;
                            const value = ref.Value ?? param?.Value ?? "";
                            const enumMatch = mdPt?.choice?.Enumeration?.find(
                              (o) => String(o.Value) === value,
                            );
                            return (
                              <tr key={ref.Id}>
                                <td className="py-1 pr-3 text-fd-foreground">
                                  {ref.Name ?? param?.Name ?? "—"}
                                </td>
                                <td className="py-1 pr-3 text-fd-muted-foreground">
                                  {ref.Text ?? param?.Text ?? ""}
                                </td>
                                <td className="py-1 font-mono">
                                  {enumMatch ? (
                                    <>
                                      {enumMatch.Text}
                                      <span className="text-fd-muted-foreground/50 ml-1">({value})</span>
                                    </>
                                  ) : (
                                    value || <span className="opacity-40">—</span>
                                  )}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </DocsPage>
  );
}
