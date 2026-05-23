import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import type { Node, Root } from "fumadocs-core/page-tree";
import { BookIcon } from "lucide-react";
import { appName, gitConfig } from "./shared";

export function baseOptions(): BaseLayoutProps {
  return {
    nav: { title: appName },
    githubUrl: `https://github.com/${gitConfig.user}/${gitConfig.repo}`,
  };
}

export function homeOptions(): BaseLayoutProps {
  return {
    ...baseOptions(),
    links: [
      { icon: <BookIcon />, text: "Docs", url: "/docs" },
      { icon: <BookIcon />, text: "Catalog", url: "/catalog" },
    ],
  };
}

export function makeSharedTree(docsNodes: Node[], catalogNodes: Node[] = []): Root {
  return {
    name: appName,
    children: [
      {
        type: "folder",
        name: "Documentation",
        icon: <BookIcon />,
        root: true,
        index: { type: "page", name: "Documentation", url: "/docs" },
        children: docsNodes,
      },
      {
        type: "folder",
        name: "Catalog",
        icon: <BookIcon />,
        root: true,
        index: { type: "page", name: "Catalog", url: "/catalog" },
        children: catalogNodes,
      },
    ],
  };
}
