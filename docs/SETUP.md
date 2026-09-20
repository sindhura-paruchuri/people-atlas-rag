> For the current resume workflow and existing-account configuration, follow [START-HERE.md](../START-HERE.md) first. It supersedes older account-creation and cloud-budget suggestions below.

# Updated setup: real public corpus and RLHF

The current preview uses 200 real historical HotpotQA passages and 12 public-figure biographies, replacing the fictional preview. It remains keyword extraction until the live backend is connected.

1. Create a private empty GitHub repository named `people-atlas-rag`.
2. Create a Gemini API project/key, Pinecone Starter account, and SerpApi account.
3. Copy `.env.example` to `.env` and configure private keys on the backend host. Confirm embedding dimensions before creating the Pinecone index. Use namespace `hotpotqa-v1`.
4. Start Docker Compose; run `docker compose run --rm api python load_data.py` before ingestion.
5. Run `docker compose --profile tools run --rm ingest`.
6. Run `docker compose run --rm api python verify_integrations.py`; retain the measured outcomes.
7. Expose the authenticated API through HTTPS and set the website server's `RAG_API_URL` and matching token.
8. Review answers, collect genuine A/B preferences, then follow `training/README.md`. Training is a separate compute job and never an automatic consequence of clicking a rating.

For a downloaded ZIP, initialize Git in the extracted project before pushing:

```bash
git init -b main
git add .
git commit -m "Initialize People Atlas"
git remote add origin https://github.com/sindhura-paruchuri/people-atlas-rag.git
git push -u origin main
```

This requires GitHub authentication and an existing destination repository. Do not include real `.env` values.

See `infra/README.md` for hosting and credit restrictions, `training/README.md` for RLHF, and `REQUIREMENTS.md` for the exact remaining account details.
