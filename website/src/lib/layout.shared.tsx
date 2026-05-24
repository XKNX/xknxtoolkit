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
      { icon: <DatabaseIcon />, text: "Handbook", url: "/handbook" },
      { icon: <BookIcon />, text: "Documentation", url: "/docs" },
    ],
  };
}
