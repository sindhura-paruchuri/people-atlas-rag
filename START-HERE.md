# Resume People Atlas locally

This package combines the real HotpotQA corpus and experimental RLHF workflow with the single Gemini key configuration. It contains 200 historical passages and 12 biographical articles. It does not contain your credentials or a trained model.

## Preserve your previous work

Back up your existing project folder first. If you modified code after the previous download, compare those changes before replacing files. Keep your existing `.env`, model names, Pinecone host/namespace and MySQL passwords. Never upload `.env`, API keys, or database volumes to chat or GitHub.

If you already used Docker, run `docker compose ls` in your old folder and note the project name. Keep using that folder, or use `docker compose -p YOUR_EXISTING_PROJECT ...` with every command below. Changing the folder name can select a different MySQL volume. Do not run `docker compose down -v`.

## 1. Local configuration

Start Docker Desktop. Install Python 3 and Node.js 22.13 or newer if absent. Open a terminal in the project folder containing `docker-compose.yml`.

```bash
python3 scripts/setup_local.py
```

On Windows, use `py` instead of `python3`. This command makes no network calls and preserves an existing `.env`. For a new configuration, it generates the database passwords and internal tokens automatically.

Edit `.env` locally. Fill in `GEMINI_API_KEY`, `PINECONE_API_KEY`, `SERPAPI_API_KEY`, and `PINECONE_HOST`. Keep `LLM_API_KEY` and `EMBEDDING_API_KEY` empty to share the Gemini key, or retain existing working overrides. Set `RAG_API_URL=http://127.0.0.1:8000` for the local frontend.

The new template uses `gemini-embedding-2` and `EMBEDDING_DIMENSIONS=3072`. Your Pinecone index must be dense, cosine, and dimension-matched. Use the index host from Pinecone, not its dashboard URL. Keep your previous embedding model if already indexed successfully. Do not mix vectors from different models, even when dimensions match. When intentionally changing models, use a new namespace and re-index the corpus. The provider returns its default dimensions; this setting validates that size rather than requesting a resized embedding.

## 2. Start, import, index, verify—in this order

Run each command separately. Stop at the first error.

```bash
docker compose up --build -d
docker compose ps
docker compose --profile tools run --rm ingest python load_data.py
docker compose --profile tools run --rm ingest
docker compose --profile tools run --rm ingest python verify_integrations.py
```

The import applies the additive documents/preferences migration and upserts the included corpus. It does not delete existing people, questions or feedback. The indexing command creates embeddings and writes them to Pinecone using stable document IDs. It refuses empty corpora and mismatched dimensions. Re-running updates the same IDs; it still uses provider quota. Allow a short propagation delay before verification if Pinecone just received its first vectors.

Verification reports PASS, FAIL or SKIPPED for MySQL read/write, embeddings/Pinecone query, MCP retrieval, Gemini, SerpApi, and the orchestrated answer/persistence path. A skipped test is not a pass. This is not a full production audit or an RLHF evaluation. Quota-limited calls can fail with HTTP 429; do not enable paid billing just to bypass a limit.

## 3. Open the local app

In a second terminal, in the same project folder:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

Open the URL printed by the frontend. Restart it after changing `.env`. Ask “Tell me about Peggy Seeger” with web search off. Confirm a cited answer and stored feedback. Then try a question outside the corpus with web search enabled and inspect the research trace and web sources. Generate an answer comparison and record your actual preference.

The hosted website cannot reach your computer at localhost. Until a reachable backend is configured there, it remains a public-data preview. Local operation does not require a paid cloud server or GPT API credits. Your own accounts' free quotas must cover external calls; this software cannot guarantee provider pricing or enforce billing limits for you. No paid resources are provisioned by these instructions.

## 4. RLHF after live RAG works

Follow `training/README.md`. Collect real A/B reviews, export them, and run the reward-model/policy training experiment locally using an appropriately licensed small model. CPU runs may be slow. Do not label the project as having a trained or improved model until a real run and held-out human evaluation are completed. Gemini is still the live answer provider; it is not fine-tuned by this pipeline.

## 5. GitHub

Your destination is https://github.com/sindhura-paruchuri/people-atlas-rag. No new repository is needed. If you already have a clone, apply the reviewed source changes in that clone and retain its history. Use authenticated GitHub access locally; never paste a token in chat. Before staging, inspect `git status` and confirm `.env`, reviews, checkpoints and logs are excluded. Merge any remote changes before pushing; do not force-push.

## If a step fails, send only this

- Which command failed and its final error lines, with credentials removed.
- Your operating system and the output of `docker compose ps`.
- Pinecone index dimension and metric; embedding model name; whether indexing printed completion.

Do not send `docker compose config`, `.env`, full provider request URLs, or unredacted logs: they can expose secrets. The verification command intentionally reports only error types and HTTP status codes.

## Verified for this revision

See `docs/SESSION-STATUS.md`. Your previous terminal failure was not available in the recovered conversation, so no claim is made that it has been reproduced.

Provider references: [Gemini compatible API](https://ai.google.dev/gemini-api/docs/openai), [embedding dimensions and model migration](https://ai.google.dev/gemini-api/docs/embeddings).
