import * as handbook from "@/lib/source/handbook";
import * as docs from "@/lib/source/docs";

export const revalidate = false;

export async function GET() {
  const scanned = await Promise.all([
    ...handbook.source.getPages().map(handbook.getLLMText),
    ...docs.source.getPages().map(handbook.getLLMText),
  ]);

  return new Response(scanned.join("\n\n"));
}
