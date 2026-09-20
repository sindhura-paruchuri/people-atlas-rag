"""Export actual human choices only. Run in backend container after reviews."""
import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,'/app' if Path('/app/db.py').exists() else str(Path(__file__).resolve().parents[1]/'backend'))
import db
from sqlalchemy import text
out=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/preferences');out.mkdir(parents=True,exist_ok=True)
with db.engine.connect() as c:
    rows=c.execute(text("SELECT c.*,p.choice,p.reviewer FROM comparisons c JOIN preferences p ON p.comparison_id=c.id WHERE p.choice IN ('a','b')")).mappings().all()
files={name:(out/(name+'.jsonl')).open('w') for name in ['train','validation']}
try:
    for row in rows:
        # All reviews for one query stay in one split. Do not train on held-out queries.
        split='validation' if int(hashlib.sha256(row['query_id'].encode()).hexdigest(),16)%5==0 else 'train'
        record={'query_id':row['query_id'],'prompt':row['prompt'],'chosen':row['answer_a'] if row['choice']=='a' else row['answer_b'],'rejected':row['answer_b'] if row['choice']=='a' else row['answer_a'],'reviewer':row['reviewer'],'provenance':'human_ui_preference'}
        files[split].write(json.dumps(record)+'\n')
finally:
    for f in files.values():f.close()
print(f'Exported {len(rows)} decisive human preferences; ties and neither excluded.')
