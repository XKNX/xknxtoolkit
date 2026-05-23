import { DocsLayout } from 'fumadocs-ui/layouts/docs'
import { baseOptions, makeSharedTree } from '@/lib/layout.shared'
import { apiSource } from '@/lib/source'
import { LayoutGridIcon } from 'lucide-react'

export default function CatalogLayout({ children }: LayoutProps<'/catalog'>) {
  const tree = {
    name: 'Catalog',
    children: [
      { type: 'page' as const, name: 'Browse Products', url: '/catalog', icon: <LayoutGridIcon /> },
      { type: 'separator' as const, name: 'API Reference' },
      ...apiSource.getPageTree().children,
    ],
  }
  return (
    <DocsLayout {...baseOptions()} tree={tree}>
      {children}
    </DocsLayout>
  )
}
