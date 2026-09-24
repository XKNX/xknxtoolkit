import Link from "next/link";

const packages = [
  {
    name: "xknx-models",
    description: "Every version of KNX's data model, unified into one representation.",
  },
  {
    name: "xknx-product",
    description: "Everything inside a KNX product archive, ready to explore.",
  },
  {
    name: "xknx-project",
    description: "Inspect and edit KNX project files with a clean, typed API.",
  },
  {
    name: "xknx-keys",
    description: "Read, write, and manage your KNX Secure keyring.",
  },
];

export default function HomePage() {
  return (
    <main className="flex flex-col flex-1">
      <section className="flex flex-col items-center justify-center text-center py-24 px-4 gap-6">
        <h1 className="text-5xl font-bold tracking-tight">XKNX Toolkit</h1>
        <p className="text-fd-muted-foreground text-lg max-w-xl">
          A Python library suite for working with KNX project files, product archives, security
          keys, and data models.
        </p>
        <div className="flex gap-3 flex-wrap justify-center">
          <Link
            href="/docs"
            className="rounded-md bg-fd-primary text-fd-primary-foreground px-5 py-2.5 text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Read the docs
          </Link>
          <a
            href="https://github.com/XKNX/xknxtoolkit"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-fd-border px-5 py-2.5 text-sm font-medium hover:bg-fd-accent transition-colors"
          >
            GitHub
          </a>
        </div>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-4xl mx-auto w-full px-4 pb-24">
        {packages.map((pkg) => (
          <div
            key={pkg.name}
            className="rounded-lg border border-fd-border p-6 flex flex-col gap-2"
          >
            <h2 className="font-semibold font-mono text-sm">{pkg.name}</h2>
            <p className="text-fd-muted-foreground text-sm">{pkg.description}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
