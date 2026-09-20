"""Index unchanged canonical documents, with explicit resume and request pacing."""
import argparse
import asyncio
import os
import httpx
from sqlalchemy import text
import db
from providers import embed, pinecone, request

async def main(resume_from=0, batch_size=10, pause_seconds=65):
    if resume_from < 0 or not 1 <= batch_size <= 50 or pause_seconds < 0:
        raise ValueError('Invalid resume count, batch size or pause')
    with db.engine.connect() as c:
        ids = list(c.execute(text('SELECT id FROM documents ORDER BY id')).scalars())
    count = len(ids)
    if not count:
        raise RuntimeError('No documents loaded. Run load_data.py first.')
    if resume_from > count:
        raise ValueError('Resume count exceeds document count')
    stats = await pinecone('/describe_index_stats', {})
    if stats.get('dimension') != int(os.getenv('EMBEDDING_DIMENSIONS', '3072')):
        raise ValueError('Pinecone dimension does not match EMBEDDING_DIMENSIONS')
    # Resume is only for the same corpus, namespace and embedding model.
    # Confirm skipped IDs really exist before consuming more embedding quota.
    for start in range(0, resume_from, 50):
        batch = ids[start:min(start + 50, resume_from)]
        result = await request('GET', os.environ['PINECONE_HOST'].rstrip('/') + '/vectors/fetch',
            headers={'Api-Key': os.environ['PINECONE_API_KEY'], 'X-Pinecone-Api-Version': '2025-10'},
            params=[('namespace', os.getenv('PINECONE_NAMESPACE', 'hotpotqa-v1'))] + [('ids', ident) for ident in batch])
        if any(ident not in result.get('vectors', {}) for ident in batch):
            raise ValueError('Some skipped vectors are missing. Confirm the namespace or allow Pinecone propagation before resuming.')
    total = resume_from
    print(f'Resuming at {total}/{count}. Keep the corpus, model and namespace unchanged.', flush=True)
    for start in range(total, count, batch_size):
        if pause_seconds:
            print(f'Waiting {pause_seconds:g} seconds before the next embedding batch...', flush=True)
            await asyncio.sleep(pause_seconds)
        batch = ids[start:start + batch_size]
        records_by_id = {r['id']: r for r in db.documents(ids=batch)}
        records = [records_by_id[ident] for ident in batch]
        try:
            vectors = await embed([r['title'] + '. ' + r['content'] for r in records])
            await pinecone('/vectors/upsert', {'vectors': [
                {'id': r['id'], 'values': v, 'metadata': {'kind': r['kind']}}
                for r, v in zip(records, vectors)]})
        except httpx.HTTPStatusError as exc:
            print(f'Provider HTTP {exc.response.status_code}. Stopping; last confirmed progress: {total}/{count}.', flush=True)
            if exc.response.status_code == 429:
                print('Quota/rate limit reached. Check AI Studio usage; a daily quota requires its reset. Do not repeatedly restart.', flush=True)
            print(f'After resolving the limit/error, resume with: python ingest.py --resume-from {total}', flush=True)
            return 1
        total += len(records)
        print(f'Indexed {total}/{count} records', flush=True)
    print('Indexing complete; run verification after Pinecone propagation.', flush=True)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume-from', type=int, default=0,
                        help='Previously indexed count; same corpus/model/namespace only')
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--pause-seconds', type=float, default=65)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.resume_from, args.batch_size, args.pause_seconds)))
