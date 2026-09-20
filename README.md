**Resuming an existing setup? Start with [START-HERE.md](START-HERE.md).**

# People Atlas

A database-first RAG application with a React frontend, Python/FastAPI orchestration, containerized agents, MySQL, Pinecone, Google search via SerpApi, MCP tools, citations, and feedback.

**Delivery status:** the hosted preview uses 200 real historical HotpotQA passages and twelve biographical articles. It runs keyword extraction until the live backend is configured. Live MySQL/Pinecone/Gemini/search integrations require credentials and a container host. A/B preference review, export, reward-model training and KL-regularized policy training code are included; no actual human-feedback training run has been completed. Source is prepared for GitHub; the Sites source repository is separate from your GitHub account.

## Start here

1. Read [the step-by-step guide](docs/SETUP.md).
2. Review [architecture and network calls](docs/ARCHITECTURE.md).
3. Check [evaluation and feedback](docs/EVALUATION.md).
4. See [validation and limitations](docs/VALIDATION.md).

## Repository

- `app/page.tsx`: question interface, people directory, sources, feedback and traces.
- `app/api/atlas/route.ts`: same-origin server proxy; provider secrets never go to the browser.
- `lib/sample.ts`: explicit public-data preview mode, with lexical extraction rather than LLM claims.
- `backend/api.py`: authenticated API and bounded orchestration.
- `backend/agents.py`: one retrieval, research, or answer role per container.
- `backend/mcp_server.py`: canonical database/vector retrieval and Google search tools.
- `backend/providers.py`: model, embeddings, vector, and search HTTP adapters.
- `backend/schema.sql`: MySQL schema and original seed schema.
- `backend/ingest.py`: batch embedding and idempotent Pinecone upserts.
- `docker-compose.yml`: MySQL, MCP, three agents, API and ingestion task.
- `.github/workflows/ci.yml`: source validation and backend regression checks.

## Quick start

Requires Docker Compose, Node 22+, and the package manager version in `package.json`.

```bash
cp .env.example .env
# Edit .env with your own service values, then:
docker compose up --build -d
docker compose run --rm api python load_data.py
docker compose --profile tools run --rm ingest
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

For the local frontend's live mode, set `RAG_API_URL=http://127.0.0.1:8000` in `.env` and restart it. Leave that setting empty to explore public-data preview mode without provider credentials. The Python stack is live-only and will report missing configuration; it never silently substitutes mock model results.

Never commit `.env`, database exports containing private records, or service keys. GitHub stores the code and deployment configuration; MySQL stores records and Pinecone stores vectors.

## Added in this revision

- `backend/data`: attributed real HotpotQA corpus; evaluation answers kept separate.
- `backend/load_data.py`: additive schema migration and canonical corpus import.
- `components/preference-review.tsx`: human A/B comparison, tie and reject-both choices.
- `training`: preference export, reward model and experimental RLHF policy training.
- `backend/verify_integrations.py`: live verification with explicit PASS/FAIL/SKIPPED output.
- `infra/README.md`: Google Cloud deployment and credit restrictions.
- `docs/REQUIREMENTS.md`: requirement-by-requirement delivery status and account checklist.
