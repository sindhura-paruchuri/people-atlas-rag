"""Apply additive migration and import public corpus with idempotent upserts."""
import json
from pathlib import Path
from sqlalchemy import text
import db
root=Path(__file__).resolve().parent
with db.engine.begin() as c:
    for statement in (root/'migrations/002_documents_preferences.sql').read_text().split(';'):
        if statement.strip():c.execute(text(statement))
    for d in json.loads((root/'data/corpus.json').read_text()):
        c.execute(text('INSERT INTO documents(id,title,content,source_url,kind,dataset,license) VALUES(:id,:title,:text,:url,:kind,:dataset,:license) ON DUPLICATE KEY UPDATE content=:text,source_url=:url'),d)
print('Imported public documents. Run ingest.py next.')
