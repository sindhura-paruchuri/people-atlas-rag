# Validation status

## Completed locally

- Frontend production build: passed.
- TypeScript type checking: passed after correcting JSON response types.
- Python source compilation: passed.
- Twelve backend regression tests: passed. Covers auth, input validation, database-first routing, web fallback, disabled web, persistence invocation, unknown feedback query, backend failure, retrieval heuristics, citations, and source URL schemes.
- MCP server and agent modules: imported successfully with installed dependencies. Direct dependencies are pinned to the versions used for these checks.

The API tests mock remote agents and database persistence. They verify orchestration behavior, not external provider availability or actual SQL writes.

## Requires connected infrastructure

- Docker Compose runtime and networking: Docker is not available in the authoring environment.
- Real MySQL initialization, persistence, and restart recovery.
- Real MCP HTTP session across container boundaries.
- Pinecone ingestion/query consistency and actual embedding dimensions.
- Live Google search, domain filtering, and LLM grounded-answer behavior.
- Live feedback persistence.
- Full browser/visual QA and browser WebMCP validation: not performed; no supported browser context was opened in this task.
- GitHub push and CI execution: pending an authenticated account and chosen repository.

## Before sharing as a production application

Use the step-by-step guide to connect the services. Exercise a database hit, an insufficient-evidence fallback, web disabled, provider timeout, prompt-injection text, invalid citation, empty search result, and feedback across a database restart. Add application authentication and rate/budget limits before expanding access. Measure live quality rather than copying the fictional benchmark scores.

## Current revision

- Downloaded actual public HotpotQA rows and validated 200 unique context documents and 12 selected biographical articles.
- 18 backend regression tests passed, including dataset/gold separation and preference validation/persistence calls.
- TypeScript checks passed after the public-data and review changes.
- RLHF code added: training has not run on real human preferences. GPU/model/provider checks remain pending.
- Live checker added: missing credentials report SKIPPED and a nonzero exit status, never PASS.

- CPU training mechanics smoke test uses a random tiny model and explicitly mocked records, not real human preferences; it does not establish model quality. See `training/test_training.py`.
