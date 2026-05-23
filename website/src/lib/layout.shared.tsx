import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { BookIcon, DatabaseIcon } from "lucide-react";
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
      { icon: <BookIcon />, text: "Docs", url: "/docs/home" },
      { icon: <DatabaseIcon />, text: "Catalog", url: "/catalog" },
    ],
  };
}
