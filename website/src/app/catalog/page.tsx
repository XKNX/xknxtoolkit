import { Suspense } from 'react'
import CatalogContent from '@/components/catalog/CatalogContent'

export const metadata = { title: 'KNX Catalog' }

export default function CatalogPage() {
  return (
    <div className="[grid-area:main] flex flex-col w-full mx-auto px-4 py-4 md:px-6 xl:px-8 h-[calc(100dvh-var(--fd-nav-height,3.5rem))]">
      <Suspense>
        <CatalogContent />
      </Suspense>
    </div>
  )
}
