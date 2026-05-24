import { execSync } from "node:child_process";
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  readdirSync,
  copyFileSync,
  rmSync,
} from "node:fs";
import { join, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { glob } from "glob";
import { rimraf } from "rimraf";
import { convert, frontmatter } from "fumadocs-python";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "../..");
const websiteRoot = join(__dirname, "..");
const websiteContent = join(__dirname, "../content");

// Custom write function that strips 2 path segments (namespace + module name)
// instead of fumadocs-python's write() which strips only 1.
// Files from convert() have virtual paths like:
//   <namespace>/<moduleName>/foo/bar.mdx
// We want them written to:
//   <outDir>/foo/bar.mdx
function writeStrip2(files, { outDir, namespace, moduleName }) {
  const prefix = `${namespace}/${moduleName}/`;
  for (const file of files) {
    if (!file.path.startsWith(prefix)) continue;
    const relPath = file.path.slice(prefix.length);
    const dest = join(outDir, relPath);
    mkdirSync(dirname(dest), { recursive: true });
    const body =
      Object.keys(file.frontmatter ?? {}).length > 0
        ? `${frontmatter(file.frontmatter)}\n\n${file.content}`
        : file.content;
    writeFileSync(dest, body);
  }
}

// Package config:
// - apiOutDir: where MDX API docs are written
// - docsOutDir: where hand-written .mdx docs are copied (null for catalog)
// - apiBaseUrl: the URL base for API pages
const packages = [
  {
    name: "models",
    module: "xknxmono.models",
    namespace: "xknxmono",
    moduleName: "models",
    srcDir: "packages/models/src",
    apiOutDir: "content/docs/models/api",
    docsOutDir: "content/docs/models",
    apiBaseUrl: "/docs/models/api",
  },
  {
    name: "product",
    module: "xknxmono.product",
    namespace: "xknxmono",
    moduleName: "product",
    srcDir: "packages/product/src",
    apiOutDir: "content/docs/product/api",
    docsOutDir: "content/docs/product",
    apiBaseUrl: "/docs/product/api",
  },
  {
    name: "catalog",
    module: "xknxmono.catalog",
    namespace: "xknxmono",
    moduleName: "catalog",
    srcDir: "packages/catalog/src",
    apiOutDir: "content/docs/catalog/api",
    docsOutDir: null,
    apiBaseUrl: "/docs/catalog/api",
  },
  {
    name: "project",
    module: "xknx.project",
    namespace: "xknx",
    moduleName: "project",
    srcDir: "packages/project/src",
    apiOutDir: "content/docs/project/api",
    docsOutDir: "content/docs/project",
    apiBaseUrl: "/docs/project/api",
  },
  {
    name: "keyring",
    module: "xknx.keyring",
    namespace: "xknx",
    moduleName: "keyring",
    srcDir: "packages/keyring/src",
    apiOutDir: "content/docs/keyring/api",
    docsOutDir: "content/docs/keyring",
    apiBaseUrl: "/docs/keyring/api",
  },
];

// Derive changelog output path from the api output dir (sibling of api/)
function changelogOutPath(pkg) {
  return join(websiteRoot, pkg.apiOutDir, "../changelog.mdx");
}

// Clean up generated api dirs and changelog files before regenerating
for (const pkg of packages) {
  const apiDir = join(websiteRoot, pkg.apiOutDir);
  await rimraf(apiDir);
  const changelogPath = changelogOutPath(pkg);
  if (existsSync(changelogPath)) rmSync(changelogPath);
}

for (const pkg of packages) {
  const pkgDir = join(root, "packages", pkg.name);
  const srcDir = join(root, pkg.srcDir);
  const docsDir = join(pkgDir, "docs");
  const apiOutDir = join(websiteRoot, pkg.apiOutDir);

  console.log(`\n--- ${pkg.name} ---`);

  // Clean and recreate api output dir
  await rimraf(apiOutDir);
  mkdirSync(apiOutDir, { recursive: true });

  // Generate API reference JSON from Python source
  console.log(`  fumapy-generate ${pkg.module}...`);
  const jsonPath = join(srcDir, `${pkg.module}.json`);
  execSync(
    `uv run --directory ${root} fumapy-generate ${pkg.module} --dir ${srcDir}`,
    { cwd: srcDir, stdio: "inherit" },
  );

  // Convert JSON to MDX using baseUrl, then write with 2-segment stripping
  // convert() generates virtual paths: <namespace>/<moduleName>/...
  // and hrefs like: <baseUrl>/<namespace>/<moduleName>/...
  // writeStrip2 places files at: apiOutDir/...  (served at apiBaseUrl/...)
  const mod = JSON.parse(readFileSync(jsonPath, "utf-8"));
  const files = convert(mod, { baseUrl: pkg.apiBaseUrl });
  writeStrip2(files, {
    outDir: apiOutDir,
    namespace: pkg.namespace,
    moduleName: pkg.moduleName,
  });
  console.log(`  wrote ${files.length} API pages → ${pkg.apiOutDir}/`);

  // Fix hrefs: convert() generates <baseUrl>/<namespace>/<moduleName>/...
  // but files are served at <baseUrl>/... (2 segments stripped).
  const generated = await glob(`${apiOutDir}/**/*.mdx`);
  const hrefPrefixSlash = `${pkg.apiBaseUrl}/${pkg.namespace}/${pkg.moduleName}/`;
  const hrefPrefixQuote = `${pkg.apiBaseUrl}/${pkg.namespace}/${pkg.moduleName}"`;
  for (const file of generated) {
    let src = readFileSync(file, "utf-8");
    let fixed = src
      .replaceAll(hrefPrefixSlash, `${pkg.apiBaseUrl}/`)
      .replaceAll(hrefPrefixQuote, `${pkg.apiBaseUrl}"`);
    if (fixed !== src) writeFileSync(file, fixed);
  }
  if (generated.length > 0)
    console.log(`  fixed hrefs in ${generated.length} files`);

  // Copy hand-written .mdx files from packages/<pkg>/docs/ to content/<pkg>/
  // (not for catalog - its browser is served via the app route)
  if (pkg.docsOutDir && existsSync(docsDir)) {
    const docsOutDir = join(websiteRoot, pkg.docsOutDir);
    mkdirSync(docsOutDir, { recursive: true });
    for (const file of readdirSync(docsDir, { recursive: true })) {
      if (extname(String(file)) !== ".mdx") continue;
      const src = join(docsDir, String(file));
      const dest = join(docsOutDir, String(file));
      mkdirSync(dirname(dest), { recursive: true });
      copyFileSync(src, dest);
    }
    console.log(`  overlaid hand-written .mdx from docs/ → ${pkg.docsOutDir}/`);
  }

  // Convert CHANGELOG.md → changelog.mdx and write next to index.mdx
  const changelogSrc = join(pkgDir, "CHANGELOG.md");
  if (existsSync(changelogSrc)) {
    const md = readFileSync(changelogSrc, "utf-8");
    // Strip the leading "# Changelog" h1 — the frontmatter title serves that role
    const body = md.replace(/^#\s+Changelog\s*\n/, "");
    const fm = frontmatter({ title: "Changelog", description: `Release history for xknx-${pkg.name}.`, icon: "History" });
    const dest = changelogOutPath(pkg);
    mkdirSync(dirname(dest), { recursive: true });
    writeFileSync(dest, `${fm}\n\n${body}`);
    console.log(`  converted CHANGELOG.md → ${pkg.apiOutDir}/../changelog.mdx`);
  }
}
