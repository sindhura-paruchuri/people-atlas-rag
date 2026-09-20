# Recovery and validation — 2026-09-18

## Recovered and preserved

- Current workspace: real HotpotQA corpus (200 passages, 12 biographical articles), MySQL document migration/importer, A/B preferences, export and experimental RLHF trainer.
- Previous ready ZIP: older fictional people corpus with shared Gemini key support. It did not contain the newer data/training additions.
- Merged shared Gemini key support into the newer workspace. Default new configuration follows the prior `gemini-embedding-2` selection; existing local settings are never overwritten by setup.
- Your actual terminal errors and any subsequent local code edits were not available. This revision cannot claim to reproduce or preserve unseen local changes; compare them before replacing your project.

## Changes

- Shared Gemini API key with optional service overrides; live verification recognizes that shared key.
- Indexing rejects an empty corpus or mismatched Pinecone dimensions before embedding/upsert.
- Embedding responses must contain exactly one finite, dimension-matched vector per input, in matching order.
- Offline configuration helper generates local passwords/tokens only when `.env` does not exist.
- START-HERE.md gives non-destructive resume steps, including importing before indexing and preserving the Compose project/volume.
- Account requirements updated: existing Gemini, Pinecone and SerpApi accounts are acknowledged; paid cloud is not required for local use.

## Validation

- Backend regression suite: 22 passed (mocked providers; not live integrations).
- Frontend production build: passed.
- Real corpus and training source included; no new RLHF training run performed.
- No local `.env`, provider keys or Docker runtime are available here. MySQL/container networking, provider calls, Pinecone ingestion/query, live UI feedback and a meaningful RLHF experiment remain unverified.
- Provider documentation confirms Gemini Embedding 2 and default 3072 dimensions; account/model access must still be verified live. Different embedding models require re-embedding, even with equal dimensions.

References: https://ai.google.dev/gemini-api/docs/embeddings and https://ai.google.dev/gemini-api/docs/openai
