"""Offline retrieval benchmark. No invented model accuracy or RLHF claims."""
import json
from core import rank
people=json.load(open('seed.json'))
cases=[('Python Austin',{'p001','p004'}),('MySQL',{'p002','p006'}),('RAG',{'p001','p005'}),('quantum entanglement',set())]
rows=[]
for query,expected in cases:
    actual={p['id'] for _,p in rank(query,people)[:3]}
    rows.append({'query':query,'precision_at_3':len(actual & expected)/len(actual) if actual else int(not expected),'recall_at_3':len(actual & expected)/len(expected) if expected else int(not actual),'retrieved':sorted(actual)})
print(json.dumps({'scope':'Fictional seed / lexical retrieval only, not live Pinecone or LLM quality','cases':rows},indent=2))
