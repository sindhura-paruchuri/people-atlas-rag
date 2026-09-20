'use client';
import { useEffect, useState } from 'react';
import { Search, ArrowUpRight, Network, Database, Globe, Users, MessageSquare, ThumbsUp, ThumbsDown, Layers, ChevronRight } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import PreferenceReview from '@/components/preference-review';
import { people as seeds } from '@/lib/sample';
type Result = {
    id: string;
    mode: string;
    answer: string;
    people: typeof seeds;
    sources: {
        id: string;
        title: string;
        text: string;
        url: string | null;
        type: string;
    }[];
    trace: {
        agent: string;
        status: string;
    }[];
    latency_ms: number;
};
export default function Home() {
    const [people, setPeople] = useState(seeds), [mode, setMode] = useState('preview'), [query, setQuery] = useState(''), [filter, setFilter] = useState(''), [web, setWeb] = useState(true), [busy, setBusy] = useState(false), [result, setResult] = useState<Result | null>(null), [error, setError] = useState(''), [feedback, setFeedback] = useState('');
    useEffect(() => { fetch('/api/atlas').then(r => r.json()).then((d: any) => { if (d.error)
        setError(d.error);
    else {
        setPeople(d.people);
        setMode(d.mode);
    } }).catch(() => setError('Unable to load directory.')); }, []);
    async function ask(q = query) { if (!q.trim() || busy)
        return; setQuery(q); setBusy(true); setError(''); setFeedback(''); try {
        const r = await fetch('/api/atlas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'query', query: q, allow_web: web }) });
        const d: any = await r.json();
        if (!r.ok)
            throw Error(d.error);
        setResult(d);
        return d;
    }
    catch (e) {
        setError((e as Error).message);
    }
    finally {
        setBusy(false);
    } }
    useEffect(() => { const ctx = (document as any).modelContext; if (!ctx?.registerTool)
        return; const c = new AbortController(); Promise.resolve(ctx.registerTool({ name: 'ask_people_atlas', description: 'Ask a question and display a sourced answer in People Atlas.', inputSchema: { type: 'object', properties: { query: { type: 'string', minLength: 1, maxLength: 2000 } }, required: ['query'], additionalProperties: false }, annotations: { readOnlyHint: false, untrustedContentHint: true }, execute: async (input: any) => { if (typeof input?.query !== 'string' || !input.query.trim() || input.query.length > 2000)
            throw Error('Invalid question'); return await ask(input.query); } }, { signal: c.signal })).catch(() => { }); return () => c.abort(); }, [web, busy]);
    async function vote(rating: number) { try {
        const r = await fetch('/api/atlas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'feedback', query_id: result?.id, rating }) });
        const d: any = await r.json();
        setFeedback(r.ok ? 'Feedback saved. Thank you.' : d.error);
    }
    catch {
        setFeedback('Could not save feedback.');
    } }
    const visible = people.filter(p => JSON.stringify(p).toLowerCase().includes(filter.toLowerCase()));
    return <div className="atlas"><header><a className="brand" href="/"><span className="brandmark"><Network size={23}/></span>people<span>atlas</span></a><span className="toplabel">KNOWLEDGE WORKSPACE</span><span className="mode">{mode === 'live' ? 'Live backend' : 'Public data preview'}</span></header><main><div className="intro"><div><div className="eyebrow">PEOPLE INTELLIGENCE / 01</div><h1>Find the people.<br /><span>See the evidence.</span></h1></div><p>Ask a question. Explore matching profiles.<br />Follow every answer back to its source.</p></div><Tabs defaultValue="ask"><TabsList className="atlas-tabs" variant="line"><TabsTrigger value="ask"><MessageSquare />Ask Atlas</TabsTrigger><TabsTrigger value="directory"><Users />People directory <span className="count">{people.length}</span></TabsTrigger></TabsList><TabsContent value="ask"><div className="workspace"><section className="query-panel"><div className="section-title"><span className="square"><Layers size={18}/></span><h2>Your research starts here</h2></div><form onSubmit={e => { e.preventDefault(); void ask(); }}><label htmlFor="question">What would you like to know?</label><textarea id="question" maxLength={2000} value={query} onChange={e => setQuery(e.target.value)} placeholder="Ask about a public figure, such as Peggy Seeger…"/><div className="query-bottom"><label className="toggle"><Switch checked={web} onCheckedChange={setWeb} aria-label="Allow web search"/>Search the web if needed</label><button className="primary" disabled={busy || !query.trim()}>{busy ? 'Searching…' : 'Ask Atlas'}<ArrowUpRight size={18}/></button></div></form><div className="suggestions"><span>TRY A QUESTION</span>{['Tell me about Peggy Seeger', 'Who is Allie Goertz?', 'Tell me about Henri Leconte'].map(q => <button key={q} disabled={busy} onClick={() => void ask(q)}>{q}<ChevronRight size={15}/></button>)}</div>{error && <p role="alert" className="error">{error}</p>}<div className="answer" aria-live="polite">{result ? <><div className="answer-heading"><h2>Answer</h2><span>{result.mode !== 'live' ? 'Historical excerpts' : `${result.latency_ms} ms`}</span></div><p className="answer-text">{result.answer}</p><div className="sources">{result.sources.map(s => <div className="source" key={s.id}><span className="source-num">{s.id}</span><div>{s.url ? <a href={s.url} target="_blank" rel="noreferrer">{s.title} ↗</a> : <strong>{s.title}</strong>}<p>{s.type} · {s.text.slice(0, 140)}</p></div></div>)}</div><div className="feedback"><span>Was this helpful?</span><button aria-label="Helpful" onClick={() => void vote(1)}><ThumbsUp size={17}/></button><button aria-label="Not helpful" onClick={() => void vote(-1)}><ThumbsDown size={17}/></button><small>{feedback}</small></div><PreferenceReview key={result.id} queryId={result.id} live={mode==='live'}/></> : <div className="empty-answer"><div className="empty-icon"><Search size={25}/></div><h3>A good answer starts with a good source.</h3><p>Your answer and supporting records will appear here.</p></div>}</div></section><aside className="evidence"><div className="section-title"><h2>Behind the answer</h2><Network size={20}/></div><p className="muted">Database first. Web when needed.</p><div className="pipeline">{[{ icon: Database, name: 'Retrieve', desc: 'Find relevant people and knowledge.' }, { icon: Globe, name: 'Research', desc: 'Fill evidence gaps with web sources.' }, { icon: Layers, name: 'Answer', desc: 'Use evidence to compose a cited answer.' }].map((s, i) => <div className="step" key={s.name}><div className="step-icon"><s.icon size={19}/></div><div><span className="step-number">0{i + 1}</span><h3>{s.name}</h3><p>{result?.trace[i]?.status || s.desc}</p></div></div>)}</div><div className="note"><strong>{mode !== 'live' ? 'Public dataset connected' : 'Connected workspace'}</strong><p>{mode !== 'live' ? '200 real HotpotQA excerpts. This preview uses keyword search. LLM, Pinecone, web search, and feedback storage need the live backend.' : 'Your questions are processed by the configured agent services.'}</p></div><div className="aside-bottom"><span>BUILT FOR TRACEABILITY</span><p>Sources stay visible.<br />Uncertainty stays explicit.</p></div></aside></div></TabsContent><TabsContent value="directory"><section className="directory"><div className="directory-head"><div><h2>People directory</h2><p>{mode !== 'live' ? '12 biographical articles from HotpotQA. Historical excerpts, not verified current profiles.' : 'Records from your connected database.'}</p></div><label className="filter"><Search size={18}/><input aria-label="Filter people" placeholder="Name or biography" value={filter} onChange={e => setFilter(e.target.value)}/></label></div><div className="people-grid">{visible.map((p, i) => <article className="person" key={p.id}><div className={'avatar avatar-' + i % 3}>{p.name.split(' ').map(n => n[0]).join('')}</div><h3>{p.name}</h3><p className="role">{p.role}</p><p className="location">{p.location}</p><p>{p.bio.slice(0,380)}{p.bio.length>380?'…':''}</p><a href={p.url} target="_blank" rel="noreferrer">Read source ↗</a><div className="skills">{p.skills.map(s => <span key={s}>{s}</span>)}</div></article>)}</div>{!visible.length && <p>No matching people. Try another search.</p>}</section></TabsContent></Tabs><footer><span>PEOPLE ATLAS</span><a href="https://huggingface.co/datasets/hotpotqa/hotpot_qa" target="_blank" rel="noreferrer">HotpotQA · CC BY-SA 4.0 · Historical excerpts</a></footer></main></div>;
}
