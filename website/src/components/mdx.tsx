import defaultMdxComponents from "fumadocs-ui/mdx";
import * as PythonComponents from "fumadocs-python/components";
import CatalogContent from "@/components/catalog/CatalogContent";
import type { MDXComponents } from "mdx/types";

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    ...PythonComponents,
    CatalogContent,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;

declare global {
  type MDXProvidedComponents = ReturnType<typeof getMDXComponents>;
}
