import json, os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
engine = create_engine(os.environ['DATABASE_URL'], pool_pre_ping=True)
def people(q='', limit=100):
    with engine.connect() as conn:
        rows = conn.execute(text('SELECT id,name,role,location,skills,bio FROM people WHERE name LIKE :q OR skills LIKE :q OR location LIKE :q OR bio LIKE :q LIMIT :lim'), {'q':f'%{q}%', 'lim':min(limit,100)}).mappings().all()
    return [dict(r, skills=json.loads(r['skills']) if isinstance(r['skills'], str) else r['skills']) for r in rows]
def by_ids(ids):
    if not ids: return []
    placeholders=','.join(f':p{i}' for i in range(len(ids)))
    with engine.connect() as conn:
        rows=conn.execute(text(f'SELECT id,name,role,location,skills,bio FROM people WHERE id IN ({placeholders})'),{f'p{i}':v for i,v in enumerate(ids)}).mappings().all()
    return [dict(r,skills=json.loads(r['skills']) if isinstance(r['skills'],str) else r['skills']) for r in rows]
def save_query(result, query):
    with engine.begin() as conn:
        conn.execute(text('INSERT INTO queries (id,question,result_json,created_at) VALUES (:id,:q,:r,:t)'), {'id':result['id'],'q':query,'r':json.dumps(result),'t':datetime.now(timezone.utc).replace(tzinfo=None)})
def feedback(query_id, rating):
    with engine.begin() as conn:
        exists=conn.execute(text('SELECT id FROM queries WHERE id=:id'),{'id':query_id}).first()
        if not exists: return False
        conn.execute(text('INSERT INTO feedback(query_id,rating) VALUES(:id,:rating) ON DUPLICATE KEY UPDATE rating=:rating'),{'id':query_id,'rating':rating})
    return True

def documents(q='', ids=None, limit=100):
    with engine.connect() as c:
        if ids is not None:
            if not ids:return []
            marks=','.join(f':d{i}' for i in range(len(ids)))
            rows=c.execute(text(f'SELECT * FROM documents WHERE id IN ({marks})'),{f'd{i}':v for i,v in enumerate(ids)}).mappings().all()
        else:
            rows=c.execute(text('SELECT * FROM documents WHERE title LIKE :q OR content LIKE :q ORDER BY id LIMIT :lim'),{'q':f'%{q}%','lim':min(limit,100)}).mappings().all()
    return [dict(r) for r in rows]

def public_people():
    with engine.connect() as c:
        rows=c.execute(text("SELECT * FROM documents WHERE kind='person' ORDER BY title LIMIT 100")).mappings().all()
    return [{'id':r['id'],'name':r['title'],'role':'Biographical article','location':'Historical Wikipedia excerpt','skills':[],'bio':r['content'],'url':r['source_url']} for r in rows]

def get_query(ident):
    with engine.connect() as c:r=c.execute(text('SELECT question,result_json FROM queries WHERE id=:id'),{'id':ident}).mappings().first()
    if not r:return None
    return r['question'],json.loads(r['result_json']) if isinstance(r['result_json'],str) else r['result_json']

def save_comparison(ident,query_id,prompt,a,b,model):
    with engine.begin() as c:c.execute(text('INSERT INTO comparisons(id,query_id,prompt,answer_a,answer_b,model) VALUES(:id,:qid,:p,:a,:b,:m)'),{'id':ident,'qid':query_id,'p':prompt,'a':a,'b':b,'m':model})

def save_preference(ident,choice):
    with engine.begin() as c:
        if not c.execute(text('SELECT id FROM comparisons WHERE id=:id'),{'id':ident}).first():return False
        c.execute(text("INSERT INTO preferences(comparison_id,choice,reviewer) VALUES(:id,:choice,'workspace-owner') ON DUPLICATE KEY UPDATE choice=:choice"),{'id':ident,'choice':choice})
    return True
