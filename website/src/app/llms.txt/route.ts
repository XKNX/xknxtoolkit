import * as docs from "@/lib/source/docs";
import * as handbook from "@/lib/source/handbook";
import { llms } from "fumadocs-core/source";

export const revalidate = false;

export function GET() {
  return new Response([
    llms(handbook.source).index(),
    llms(docs.source).index(),
  ]);
}
