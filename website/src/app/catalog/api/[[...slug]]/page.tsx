import { apiSource } from '@/lib/source'
import { APIPage } from '@/components/api-page'
import { DocsBody, DocsDescription, DocsPage, DocsTitle } from 'fumadocs-ui/layouts/docs/page'
import { notFound, redirect } from 'next/navigation'
import type { Metadata } from 'next'

export default async function Page(props: PageProps<'/catalog/api/[[...slug]]'>) {
  const params = await props.params
  if (!params.slug) redirect('/catalog/api/products/list_products_products_get')

  const page = apiSource.getPage(params.slug)
  if (!page) notFound()

  return (
    <DocsPage toc={page.data.toc} full>
      <DocsTitle>{page.data.title}</DocsTitle>
      <DocsDescription>{page.data.description}</DocsDescription>
      <DocsBody>
        <APIPage {...page.data.getAPIPageProps()} />
      </DocsBody>
    </DocsPage>
  )
}

export function generateStaticParams() {
  return apiSource.generateParams()
}

export async function generateMetadata(props: PageProps<'/catalog/api/[[...slug]]'>): Promise<Metadata> {
  const params = await props.params
  const page = apiSource.getPage(params.slug)
  if (!page) notFound()
  return {
    title: page.data.title,
    description: page.data.description,
  }
}
