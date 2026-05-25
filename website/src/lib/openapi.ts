import { createOpenAPI } from "fumadocs-openapi/server";
import { resolve } from "node:path";

export const openapi = createOpenAPI({
  input: [resolve(process.cwd(), "../packages/catalog/openapi.json")],
});
