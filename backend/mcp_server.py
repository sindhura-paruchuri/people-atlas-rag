"""Private MCP tools. Not exposed to the public internet by compose."""
import os
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import db
from core import rank, terms
from providers import embed,pinecone,web_search
mcp=FastMCP('People Atlas tools',host='0.0.0.0',port=8000,transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,allowed_hosts=['mcp:8000','localhost:8000','127.0.0.1:8000'],allowed_origins=[]))
@mcp.tool()
async def retrieve_people(query:str)->dict:
    """Read relevant canonical MySQL records and Pinecone vector matches."""
    if not query.strip() or len(query)>2000: raise ValueError('Invalid query')
    candidates={}
    for term in terms(query)[:10]:
        for d in db.documents(term,limit=50):candidates[d['id']]=d
    lexical=rank(query,list(candidates.values()))
    vector=(await embed([query]))[0]
    matches=(await pinecone('/query',{'vector':vector,'topK':6,'includeMetadata':False})).get('matches',[])
    canonical={d['id']:d for d in db.documents(ids=[m['id'] for m in matches])}
    scored={d['id']:(score,d) for score,d in lexical}
    for match in matches:
        if match['id'] in canonical:
            scored[match['id']]=(max(scored.get(match['id'],(0,None))[0],match['score']),canonical[match['id']])
    chosen=sorted(scored.values(),key=lambda x:x[0],reverse=True)[:6]
    return {'people':[p for p in db.public_people() if p['id'] in {d['id'] for _,d in chosen}],
            'sources':[{'title':d['title'],'text':d['content'][:4000],'url':d['source_url'],'type':'HotpotQA historical excerpt','score':score,'document_id':d['id']} for score,d in chosen]}
@mcp.tool()
async def search_public_web(query:str)->dict:
    """Get Google result snippets, filtered to configured domains; no database writes."""
    if not query.strip() or len(query)>2000: raise ValueError('Invalid query')
    return {'sources':await web_search(query)}
if __name__=='__main__': mcp.run(transport='streamable-http')
