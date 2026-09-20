"""Explicit live checks. Uses configured API quota; never reports skips as passes."""
import asyncio,json,os,uuid
from pathlib import Path
from sqlalchemy import text
import db
from providers import embed,pinecone,llm,web_search,request
from agents import tool
async def main():
    checks=[]
    async def check(name,required,fn):
        if any(not (os.getenv(k) or (os.getenv('GEMINI_API_KEY') if k in ('LLM_API_KEY','EMBEDDING_API_KEY') else None)) for k in required):
            checks.append({'integration':name,'status':'SKIPPED','detail':'Missing configuration'});return
        try:
            detail=await fn();checks.append({'integration':name,'status':'PASS','detail':detail})
        except Exception as e:
            detail=type(e).__name__
            if hasattr(e, 'response'): detail += ' HTTP ' + str(e.response.status_code)
            checks.append({'integration':name,'status':'FAIL','detail':detail})
    async def mysql():
        ident=str(uuid.uuid4())
        with db.engine.connect() as c:
            tx=c.begin()
            try:
                assert c.execute(text('SELECT COUNT(*) FROM documents')).scalar()>0
                c.execute(text('INSERT INTO queries(id,question,result_json,created_at) VALUES(:id,:q,:r,CURRENT_TIMESTAMP)'),{'id':ident,'q':'integration verification','r':'{}'})
                c.execute(text('INSERT INTO feedback(query_id,rating) VALUES(:id,1)'),{'id':ident})
                assert c.execute(text('SELECT rating FROM feedback WHERE query_id=:id'),{'id':ident}).scalar()==1
            finally:tx.rollback()
        return 'Canonical corpus read; query/feedback writes read back and rolled back'
    async def vectors():
        v=(await embed(['Peggy Seeger']))[0]
        assert v and all(isinstance(x,(int,float)) for x in v)
        r=await pinecone('/query',{'vector':v,'topK':3,'includeMetadata':False})
        assert r.get('matches'),'Index empty; run ingest first'
        ids=[m['id'] for m in r['matches']];assert db.documents(ids=ids),'Vector IDs not in canonical corpus'
        return {'embedding_dimensions':len(v),'canonical_matches':len(ids)}
    async def mcp():
        r=await tool('retrieve_people',{'query':'Peggy Seeger'})
        assert any(s['title']=='Peggy Seeger' for s in r['sources'])
        return 'MCP initialize and retrieve_people succeeded with expected source'
    async def model():
        answer,usage=await llm([{'role':'user','content':'Reply with the word connected.'}]);assert answer.strip()
        return {'nonempty_response':True,'usage':usage}
    async def search():
        sources=await web_search('HotpotQA official dataset');assert sources
        return {'results':len(sources)}
    async def pipeline():
        r=await request('POST','http://api:8000/query',headers={'Authorization':'Bearer '+os.environ['RAG_API_TOKEN']},json={'query':'Tell me about Peggy Seeger','allow_web':False})
        assert r.get('sources') and r.get('citation_valid') and r.get('answer')
        assert db.get_query(r['id'])
        return {'query_id':r['id'],'sources':len(r['sources']),'persisted':True}
    await check('MySQL read/write',['DATABASE_URL'],mysql)
    await check('Embedding + Pinecone query',['EMBEDDING_API_KEY','PINECONE_API_KEY','PINECONE_HOST'],vectors)
    await check('MCP tool session',['MCP_URL','EMBEDDING_API_KEY','PINECONE_API_KEY'],mcp)
    await check('LLM API',['LLM_API_KEY','LLM_MODEL','LLM_BASE_URL'],model)
    await check('Google via SerpApi',['SERPAPI_API_KEY'],search)
    await check('Orchestrated RAG and persistence',['RAG_API_TOKEN','INTERNAL_TOKEN','LLM_API_KEY','EMBEDDING_API_KEY','PINECONE_API_KEY'],pipeline)
    print(json.dumps(checks,indent=2))
    return 0 if all(c['status']=='PASS' for c in checks) else 1
if __name__=='__main__':raise SystemExit(asyncio.run(main()))
