import os, asyncio, httpx
from core import safe_url

def _api_key(primary):
    value = os.getenv(primary) or os.getenv('GEMINI_API_KEY')
    if not value:
        raise RuntimeError(f'Missing {primary} or GEMINI_API_KEY')
    return value

async def request(method, url, **kwargs):
    # Bounded retry for idempotent retrieval/model requests; never logs secrets.
    async with httpx.AsyncClient(timeout=25) as client:
        for attempt in range(3):
            r=await client.request(method,url,**kwargs)
            if r.status_code in (429,502,503,504) and attempt<2:
                await asyncio.sleep(0.5*(2**attempt));continue
            r.raise_for_status();return r.json()
async def llm(messages):
    base=os.environ['LLM_BASE_URL'].rstrip('/')
    result=await request('POST',base+'/chat/completions',headers={'Authorization':'Bearer '+_api_key('LLM_API_KEY')},json={'model':os.environ['LLM_MODEL'],'messages':messages,'temperature':0,'max_tokens':900})
    return result['choices'][0]['message']['content'],result.get('usage',{})
async def embed(texts):
    if not texts:
        return []
    base = os.environ['EMBEDDING_BASE_URL'].rstrip('/')
    model = os.environ['EMBEDDING_MODEL']
    key = _api_key('EMBEDDING_API_KEY')
    if base in ('https://generativelanguage.googleapis.com/v1beta/openai',
                'https://generativelanguage.googleapis.com/v1beta'):
        # Native Gemini batch responses guarantee request order and do not
        # require OpenAI's optional/missing index field. Separate requests
        # also avoid combining multiple documents into one embedding.
        model = model.removeprefix('models/')
        from urllib.parse import quote
        endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/' + quote(model, safe='') + ':batchEmbedContents'
        data = await request('POST', endpoint, headers={'x-goog-api-key': key},
            json={'requests': [{'model': 'models/' + model,
                                'content': {'parts': [{'text': t}]}} for t in texts]})
        vectors = [row['values'] for row in data['embeddings']]
    else:
        data = await request('POST', base + '/embeddings',
            headers={'Authorization': 'Bearer ' + key},
            json={'model': model, 'input': texts})
        rows = data['data']
        if any(type(row.get('index')) is not int for row in rows):
            raise ValueError('Embedding provider omitted input indices; cannot safely align vectors')
        rows = sorted(rows, key=lambda row: row['index'])
        if [row['index'] for row in rows] != list(range(len(texts))):
            raise ValueError('Embedding response does not contain one vector per document')
        vectors = [row['embedding'] for row in rows]
    if len(vectors) != len(texts):
        raise ValueError('Embedding response does not contain one vector per document')
    import math
    expected = int(os.getenv('EMBEDDING_DIMENSIONS', '3072'))
    if any(len(v) != expected or not all(isinstance(n, (float, int)) and math.isfinite(n) for n in v) for v in vectors):
        raise ValueError('Embedding dimensions or values invalid; check EMBEDDING_DIMENSIONS and your index')
    return vectors
async def pinecone(path, payload):
    return await request('POST',os.environ['PINECONE_HOST'].rstrip('/')+path,headers={'Api-Key':os.environ['PINECONE_API_KEY'],'X-Pinecone-Api-Version':'2025-10'},json=payload if path == '/describe_index_stats' else {'namespace':os.getenv('PINECONE_NAMESPACE','hotpotqa-v1'),**payload})
async def web_search(query):
    data=await request('GET','https://serpapi.com/search.json',params={'engine':'google','q':query,'api_key':os.environ['SERPAPI_API_KEY'],'num':5})
    if data.get('error'): raise RuntimeError('Web search provider error')
    allowed=[d.strip().lower() for d in os.getenv('WEB_ALLOWED_DOMAINS','').split(',') if d.strip()]
    from urllib.parse import urlparse
    results=[]
    for r in data.get('organic_results',[]):
        url=safe_url(r.get('link'))
        if not url: continue
        host=urlparse(url).hostname
        if allowed and not any(host==d or host.endswith('.'+d) for d in allowed): continue
        results.append({'title':r.get('title','Web source')[:300],'text':r.get('snippet','')[:2000],'url':url,'type':'web snippet','score':0})
    return results
