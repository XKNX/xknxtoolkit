import { NextRequest, NextResponse } from "next/server";
import { isMarkdownPreferred, rewritePath } from "fumadocs-core/negotiation";
import { handbookContentRoute, handbookRoute, docsContentRoute, docsRoute } from "@/lib/shared";

const rewriteDocs = (pathname: string) => {
  const handbook = rewritePath(
    `${handbookRoute}{/*path}`,
    `${handbookContentRoute}{/*path}/content.md`,
  );
  const docs = rewritePath(`${docsRoute}{/*path}`, `${docsContentRoute}{/*path}/content.md`);
  return handbook.rewrite(pathname) || docs.rewrite(pathname);
};

const rewriteSuffix = (pathname: string) => {
  const handbook = rewritePath(
    `${handbookRoute}{/*path}.md`,
    `${handbookContentRoute}{/*path}/content.md`,
  );
  const docs = rewritePath(`${docsRoute}{/*path}.md`, `${docsContentRoute}{/*path}/content.md`);
  return handbook.rewrite(pathname) || docs.rewrite(pathname);
};

export default function proxy(request: NextRequest) {
  const result = rewriteSuffix(request.nextUrl.pathname);
  if (result) {
    return NextResponse.rewrite(new URL(result, request.nextUrl));
  }

  if (isMarkdownPreferred(request)) {
    const result = rewriteDocs(request.nextUrl.pathname);

    if (result) {
      return NextResponse.rewrite(new URL(result, request.nextUrl));
    }
  }

  return NextResponse.next();
}
