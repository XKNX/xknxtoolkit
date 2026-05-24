import Link from "next/link";
import { notFound } from "next/navigation";
import { DocsPage } from "fumadocs-ui/layouts/docs/page";
import { SegmentHexViewer } from "@/components/catalog/ApplicationHexViewer";

const API = process.env.CATALOG_API_URL ?? "http://localhost:8000";

interface ComObjectFlags {
  communication: boolean;
  read: boolean;
  write: boolean;
  transmit: boolean;
  update: boolean;
  read_on_init: boolean;
}

interface ComObject {
  id: string;
  name: string;
  number: number;
  dpt_codes: string[];
  flags: ComObjectFlags;
}

interface EnumOption {
  value: string;
  text: string;
}

interface ParamType {
  kind: string;
  options: EnumOption[];
  min_value: number | null;
  max_value: number | null;
  size_bits: number | null;
}

interface Parameter {
  id: string;
  ref_id: string;
  name: string;
  text: string;
  value: string;
  param_type: ParamType | null;
}

interface AbsoluteSegment {
  id: string;
  address: number;
  size: number;
  data: string | null; // base64
  mask: string | null; // base64
  name: string | null;
  user_memory: boolean;
}

interface RelativeSegment {
  id: string;
  offset: number;
  size: number;
  data: string | null; // base64
  mask: string | null; // base64
  name: string | null;
}

interface Code {
  absolute_segments: AbsoluteSegment[];
  relative_segments: RelativeSegment[];
}

interface ApplicationDetail {
  application_id: string;
  name: string;
  manufacturer_id: string;
  com_objects: ComObject[];
  parameters: Parameter[];
  code: Code | null;
}

function FlagCell({
  active,
  label,
  abbr,
}: {
  active: boolean;
  label: string;
  abbr: string;
}) {
  return (
    <span
      title={label}
      className={`inline-flex items-center justify-center w-5 h-5 rounded text-[10px] font-bold ${
        active
          ? "bg-fd-primary/15 text-fd-primary"
          : "text-fd-muted-foreground/30"
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

function ParamValueDisplay({ param }: { param: Parameter }) {
  if (!param.param_type) {
    return <span className="font-mono text-xs">{param.value}</span>;
  }
  if (param.param_type.kind === "enum" && param.param_type.options.length > 0) {
    const match = param.param_type.options.find((o) => o.value === param.value);
    return (
      <span className="text-xs">
        {match ? match.text : param.value}
        <span className="text-fd-muted-foreground/50 ml-1">
          ({param.value})
        </span>
      </span>
    );
  }
  return <span className="font-mono text-xs">{param.value}</span>;
}

function ParamTypeDisplay({ pt }: { pt: ParamType }) {
  if (pt.kind === "enum") {
    return (
      <span className="text-xs text-fd-muted-foreground">
        enum ({pt.options.length} options)
      </span>
    );
  }
  if (pt.kind === "number" || pt.kind === "unsigned" || pt.kind === "signed") {
    const range =
      pt.min_value != null && pt.max_value != null
        ? ` [${pt.min_value}–${pt.max_value}]`
        : "";
    const bits = pt.size_bits != null ? ` ${pt.size_bits}b` : "";
    return (
      <span className="text-xs text-fd-muted-foreground font-mono">
        {pt.kind}
        {bits}
        {range}
      </span>
    );
  }
  return <span className="text-xs text-fd-muted-foreground">{pt.kind}</span>;
}

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

  const app: ApplicationDetail = await res.json();

  const totalSegments =
    (app.code?.absolute_segments.length ?? 0) +
    (app.code?.relative_segments.length ?? 0);

  const toc = [
    ...(totalSegments > 0
      ? [{ title: `Code Segments (${totalSegments})`, url: "#code", depth: 2 }]
      : []),
    ...(app.com_objects.length > 0
      ? [
          {
            title: `Communication Objects (${app.com_objects.length})`,
            url: "#com-objects",
            depth: 2,
          },
        ]
      : []),
    ...(app.parameters.length > 0
      ? [
          {
            title: `Parameters (${app.parameters.length})`,
            url: "#parameters",
            depth: 2,
          },
        ]
      : []),
  ];

  return (
    <DocsPage
      footer={{ enabled: false }}
      breadcrumb={{ enabled: false }}
      toc={toc}
    >
      <Link
        href={`/handbook/catalog/hardware/${encodeURIComponent(id)}`}
        className="text-sm text-fd-muted-foreground hover:text-fd-foreground transition-colors"
      >
        ← Back to hardware
      </Link>

      <h1 className="text-2xl font-semibold text-fd-foreground mt-4">
        {app.name}
      </h1>
      <div className="text-fd-muted-foreground mt-1 text-sm">
        {app.manufacturer_id}
      </div>
      <div className="mt-1 text-xs text-fd-muted-foreground/50 font-mono break-all">
        {app.application_id}
      </div>

      {app.code && totalSegments > 0 && (
        <div id="code" className="mt-8">
          <h2 className="text-lg font-semibold text-fd-foreground mb-3">
            Code Segments
            <span className="ml-2 text-sm font-normal text-fd-muted-foreground">
              ({totalSegments})
            </span>
          </h2>
          <div className="space-y-6">
            {[...app.code.absolute_segments]
              .sort((a, b) => a.address - b.address)
              .map((seg) => (
                <div key={seg.id}>
                  <div className="flex items-baseline gap-3 mb-2">
                    <span className="text-sm font-medium text-fd-foreground">
                      {seg.name ?? seg.id.split("_AS-")[1] ?? seg.id}
                    </span>
                    <span className="text-xs text-fd-muted-foreground font-mono">
                      addr 0x{seg.address.toString(16).toUpperCase()} ·{" "}
                      {seg.size} B
                    </span>
                    {seg.user_memory && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-fd-secondary text-fd-secondary-foreground">
                        user memory
                      </span>
                    )}
                  </div>
                  {seg.data ? (
                    <SegmentHexViewer data={seg.data} height="280px" />
                  ) : (
                    <div className="text-xs text-fd-muted-foreground/50 italic">
                      No data
                    </div>
                  )}
                </div>
              ))}
            {[...app.code.relative_segments]
              .sort((a, b) => a.offset - b.offset)
              .map((seg) => (
                <div key={seg.id}>
                  <div className="flex items-baseline gap-3 mb-2">
                    <span className="text-sm font-medium text-fd-foreground">
                      {seg.name ?? seg.id.split("_RS-")[1] ?? seg.id}
                    </span>
                    <span className="text-xs text-fd-muted-foreground font-mono">
                      offset 0x{seg.offset.toString(16).toUpperCase()} ·{" "}
                      {seg.size} B
                    </span>
                  </div>
                  {seg.data ? (
                    <SegmentHexViewer data={seg.data} height="280px" />
                  ) : (
                    <div className="text-xs text-fd-muted-foreground/50 italic">
                      No data
                    </div>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {app.com_objects.length > 0 && (
        <div id="com-objects" className="mt-8">
          <h2 className="text-lg font-semibold text-fd-foreground mb-3">
            Communication Objects
            <span className="ml-2 text-sm font-normal text-fd-muted-foreground">
              ({app.com_objects.length})
            </span>
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-fd-border text-left">
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground w-12">
                    #
                  </th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">
                    Name
                  </th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">
                    DPT
                  </th>
                  <th className="pb-2 text-xs font-medium text-fd-muted-foreground">
                    <span title="C=Communication R=Read W=Write T=Transmit U=Update I=Read on Init">
                      Flags
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-fd-border/50">
                {app.com_objects.map((co) => (
                  <tr
                    key={co.id}
                    className="hover:bg-fd-muted/30 transition-colors"
                  >
                    <td className="py-2 pr-4 text-fd-muted-foreground font-mono text-xs">
                      {co.number}
                    </td>
                    <td className="py-2 pr-4 text-fd-foreground">{co.name}</td>
                    <td className="py-2 pr-4">
                      <div className="flex flex-wrap gap-1">
                        {co.dpt_codes.length > 0 ? (
                          co.dpt_codes.map((d, i) => (
                            <DptBadge key={`${d}-${i}`} code={d} />
                          ))
                        ) : (
                          <span className="text-xs text-fd-muted-foreground/40">
                            —
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-2">
                      <div className="flex gap-0.5">
                        <FlagCell
                          active={co.flags.communication}
                          label="Communication"
                          abbr="C"
                        />
                        <FlagCell
                          active={co.flags.read}
                          label="Read"
                          abbr="R"
                        />
                        <FlagCell
                          active={co.flags.write}
                          label="Write"
                          abbr="W"
                        />
                        <FlagCell
                          active={co.flags.transmit}
                          label="Transmit"
                          abbr="T"
                        />
                        <FlagCell
                          active={co.flags.update}
                          label="Update"
                          abbr="U"
                        />
                        <FlagCell
                          active={co.flags.read_on_init}
                          label="Read on Init"
                          abbr="I"
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {app.parameters.length > 0 && (
        <div id="parameters" className="mt-8">
          <h2 className="text-lg font-semibold text-fd-foreground mb-3">
            Parameters
            <span className="ml-2 text-sm font-normal text-fd-muted-foreground">
              ({app.parameters.length})
            </span>
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-fd-border text-left">
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">
                    Name
                  </th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">
                    Text
                  </th>
                  <th className="pb-2 pr-4 text-xs font-medium text-fd-muted-foreground">
                    Value
                  </th>
                  <th className="pb-2 text-xs font-medium text-fd-muted-foreground">
                    Type
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-fd-border/50">
                {app.parameters.map((p) => (
                  <tr
                    key={p.id}
                    className="hover:bg-fd-muted/30 transition-colors"
                  >
                    <td className="py-2 pr-4 text-fd-foreground">
                      {p.name || (
                        <span className="text-fd-muted-foreground/40">—</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-fd-muted-foreground text-xs">
                      {p.text || (
                        <span className="text-fd-muted-foreground/40">—</span>
                      )}
                    </td>
                    <td className="py-2 pr-4">
                      <ParamValueDisplay param={p} />
                    </td>
                    <td className="py-2">
                      {p.param_type ? (
                        <ParamTypeDisplay pt={p.param_type} />
                      ) : (
                        <span className="text-xs text-fd-muted-foreground/40">
                          —
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DocsPage>
  );
}
