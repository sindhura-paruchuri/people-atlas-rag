import { z } from 'zod';
import { people, sampleAnswer } from '@/lib/sample';
const input = z.discriminatedUnion('action', [
    z.object({ action: z.literal('query'), query: z.string().trim().min(1).max(2000), allow_web: z.boolean().default(true) }),
    z.object({ action: z.literal('feedback'), query_id: z.string().uuid(), rating: z.union([z.literal(-1), z.literal(1)]) }),
 z.object({action:z.literal('compare'),query_id:z.string().uuid()}),
 z.object({action:z.literal('preference'),comparison_id:z.string().uuid(),choice:z.enum(['a','b','tie','neither'])})
]);
export async function GET() {
    if (!process.env.RAG_API_URL)
        return Response.json({ mode: 'preview', people });
    try {
        const r = await fetch(`${process.env.RAG_API_URL}/people`, {
            headers: { Authorization: `Bearer ${process.env.RAG_API_TOKEN}` },
            signal: AbortSignal.timeout(15000)
        });
        if (!r.ok)
            throw Error();
        return Response.json({ mode: 'live', people: await r.json() });
    }
    catch {
        return Response.json({ error: 'The backend is unavailable. Check the service connection.' }, { status: 502 });
    }
}
export async function POST(request: Request) {
    let raw: unknown;
    try {
        raw = await request.json();
    }
    catch {
        return Response.json({ error: 'Invalid JSON' }, { status: 400 });
    }
    const parsed = input.safeParse(raw);
    if (!parsed.success)
        return Response.json({ error: 'Invalid request. Questions must contain 1–2,000 characters.' }, { status: 400 });
    const b = parsed.data;
    if (!process.env.RAG_API_URL) {
        if (b.action !== 'query')
            return Response.json({ error: 'Connect the backend to generate comparisons and save human feedback.' }, { status: 409 });
        return Response.json(sampleAnswer(b.query));
    }
    try {
        const r = await fetch(`${process.env.RAG_API_URL}/${b.action}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.RAG_API_TOKEN}` },
            body: JSON.stringify(b), signal: AbortSignal.timeout(90000)
        });
        if (!r.ok)
            return Response.json({ error: `Backend request failed (${r.status}).` }, { status: r.status });
        return Response.json(await r.json());
    }
    catch {
        return Response.json({ error: 'The backend did not respond. Please try again.' }, { status: 502 });
    }
}
