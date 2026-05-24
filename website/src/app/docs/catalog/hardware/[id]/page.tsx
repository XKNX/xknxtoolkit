import Link from 'next/link'
import { DocsPage } from 'fumadocs-ui/layouts/docs/page'

const API = process.env.CATALOG_API_URL ?? 'http://localhost:8000'

const MEDIUM_LABELS: Record<string, string> = {
  'MT-0': 'TP',
  'MT-1': 'PL110',
  'MT-2': 'RF',
  'MT-5': 'IP',
  'MT-6': 'KNX IP',
}

interface Application {
  id: string
  name: string
  application_number: number | null
  application_version: number | null
  mask_version: string | null
  is_secure_enabled: boolean | null
}

interface HardwareProgram {
  id: string
  hardware_id: string
  medium_types: string[]
  registration_status: string | null
  registration_number: string | null
  registration_date: string | null
  application: Application | null
}

interface Hardware {
  id: string
  manufacturer_id: string
  name: string | null
  order_number: string | null
  description: string | null
  is_rail_mounted: boolean | null
  width_mm: number | null
  serial_number: string | null
  version_number: number | null
  bus_current: number | null
  has_application_program: boolean | null
  is_coupler: boolean | null
  is_power_supply: boolean | null
  is_ip_enabled: boolean | null
  no_download_without_plugin: boolean | null
  default_language: string | null
  programs: HardwareProgram[]
}

interface Manufacturer {
  id: string
  name: string | null
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  if (value === null || value === undefined || value === '') return null
  return (
    <div>
      <div className="text-xs text-fd-muted-foreground">{label}</div>
      <div className="text-sm font-medium text-fd-foreground mt-0.5">{value}</div>
    </div>
  )
}

function Badge({ children, color = 'secondary' }: { children: React.ReactNode; color?: 'secondary' | 'blue' | 'green' | 'amber' }) {
  const styles = {
    secondary: 'bg-fd-secondary text-fd-secondary-foreground',
    blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    green: 'bg-green-500/10 text-green-600 dark:text-green-400',
    amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded font-medium ${styles[color]}`}>{children}</span>
  )
}

export default async function HardwarePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const hardware: Hardware = await fetch(`${API}/hardware/${encodeURIComponent(id)}`).then(r => r.json())
  const manufacturer: Manufacturer = await fetch(`${API}/manufacturers/${hardware.manufacturer_id}`).then(r => r.json())

  const allMediumTypes = [...new Set(hardware.programs.flatMap(p => p.medium_types))]
  const isSecure = hardware.programs.some(p => p.application?.is_secure_enabled)

  const toc = [
    { title: 'Overview', url: '#overview', depth: 2 },
    ...(hardware.programs.length > 0 ? [{ title: 'Programs', url: '#programs', depth: 2 }] : []),
    ...(hardware.description ? [{ title: 'Description', url: '#description', depth: 2 }] : []),
  ]

  return (
    <DocsPage footer={{ enabled: false }} breadcrumb={{ enabled: false }} toc={toc}>
      <Link href="/docs/catalog/browse-hardware" className="text-sm text-fd-muted-foreground hover:text-fd-foreground transition-colors">
        ← Back to catalog
      </Link>

      <h1 id="overview" className="text-2xl font-semibold text-fd-foreground mt-4">
        {hardware.name ?? hardware.id}
      </h1>
      <div className="text-fd-muted-foreground mt-1">{manufacturer.name ?? hardware.manufacturer_id}</div>

      <div className="flex gap-2 mt-3 flex-wrap">
        {isSecure && <Badge color="blue">Secure</Badge>}
        {hardware.is_rail_mounted && <Badge>DIN Rail</Badge>}
        {hardware.is_coupler && <Badge>Coupler</Badge>}
        {hardware.is_power_supply && <Badge color="amber">Power Supply</Badge>}
        {hardware.is_ip_enabled && <Badge>IP</Badge>}
        {allMediumTypes.map(mt => (
          <Badge key={mt}>{MEDIUM_LABELS[mt] ?? mt}</Badge>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-2 gap-x-8 gap-y-4">
        <Field label="Order number" value={hardware.order_number} />
        <Field label="Serial number" value={hardware.serial_number} />
        <Field label="Hardware version" value={hardware.version_number} />
        <Field label="Bus current" value={hardware.bus_current != null && hardware.bus_current > 0 ? `${hardware.bus_current} mA` : null} />
        <Field
          label="Width"
          value={hardware.width_mm != null && hardware.width_mm > 0
            ? `${hardware.width_mm} mm (${Math.round(hardware.width_mm / 17.5)} TE)`
            : null}
        />
        <Field label="Default language" value={hardware.default_language} />
        <Field label="Has application program" value={hardware.has_application_program != null ? (hardware.has_application_program ? 'Yes' : 'No') : null} />
        <Field label="No download without plugin" value={hardware.no_download_without_plugin ? 'Yes' : null} />
      </div>

      {hardware.programs.length > 0 && (
        <div id="programs" className="mt-8">
          <h2 className="text-lg font-semibold text-fd-foreground mb-3">
            Programs ({hardware.programs.length})
          </h2>
          <div className="space-y-4">
            {hardware.programs.map(prog => (
              <div key={prog.id} className="rounded-lg border border-fd-border p-4">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="flex gap-2 flex-wrap">
                    {prog.medium_types.map(mt => (
                      <Badge key={mt}>{MEDIUM_LABELS[mt] ?? mt}</Badge>
                    ))}
                    {prog.application?.is_secure_enabled && <Badge color="blue">Secure</Badge>}
                  </div>
                  {prog.application && (
                    <Link
                      href={`/docs/catalog/hardware/${encodeURIComponent(id)}/programs/${encodeURIComponent(prog.id)}/application`}
                      className="text-xs text-fd-primary hover:underline shrink-0"
                    >
                      View application →
                    </Link>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-x-8 gap-y-3">
                  {prog.application && (
                    <>
                      <Field label="Application" value={prog.application.name} />
                      <Field label="Mask version" value={prog.application.mask_version} />
                      <Field label="App number" value={prog.application.application_number} />
                      <Field label="App version" value={prog.application.application_version} />
                    </>
                  )}
                  <Field label="Registration status" value={prog.registration_status} />
                  <Field label="Registration number" value={prog.registration_number} />
                  <Field label="Registration date" value={prog.registration_date} />
                </div>
                <div className="mt-3 text-xs text-fd-muted-foreground/40 break-all">{prog.id}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {hardware.description && (
        <div id="description" className="mt-8">
          <h2 className="text-lg font-semibold text-fd-foreground mb-2">Description</h2>
          <p className="text-sm text-fd-foreground whitespace-pre-line">{hardware.description}</p>
        </div>
      )}

      <div className="mt-8 text-xs text-fd-muted-foreground/40 break-all">
        {hardware.id}
      </div>
    </DocsPage>
  )
}
