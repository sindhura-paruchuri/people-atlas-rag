# Requirements and remaining access

| Requirement | Included | Remaining verification |
|---|---|---|
| Website with queries, answers, sources and people | Yes; real public-data preview | Live API connection and browser end-to-end checks |
| Real dataset | 200 HotpotQA passages, 12 biographical articles | Larger corpus if needed; historical source caveats remain |
| MySQL persistence | Schema, migration, importer, query/feedback/preference storage | Real database credentials, service, restart/read-write tests |
| Pinecone vector database | Embeddings, namespace, upserts, query, canonical hydration | Account, key, dimension-matched index and live checks |
| Database-first retrieval; Google fallback | Orchestrator, MCP tools and SerpApi adapter | API accounts and live fallback test |
| LLM integration | Gemini-compatible configurable provider | AI Studio API key and verified model/quota |
| Multiple agents in containers | Retrieval, research, answer roles; API orchestrator | Docker host and service networking checks |
| MCP server | Private Streamable HTTP server and client sessions | Live container session and provider tool results |
| Human feedback | Ratings and persisted A/B/tie/neither review | Real human reviews |
| RLHF | Reward-head training + KL-regularized REINFORCE, export and evaluation outputs | Dependencies, trainable model, human data, compute, completed training and blind evaluation |
| GitHub | Source, ignore rules and CI | Existing private repository and authenticated push |
| Cloud deployment | Compose stack and deployment runbook | Project, billing eligibility, cost decision, deployment access |
| Evaluation | Regression tests, separated gold data, live verification runner | Live measurements and trained-checkpoint comparison |

## Current account status and remaining input

Gemini, Pinecone and SerpApi accounts/keys are ready according to the user. The GitHub destination is `https://github.com/sindhura-paruchuri/people-atlas-rag`. Do not create duplicate accounts or a second repository.

The secrets are not configured in this workspace. Run the local steps in `START-HERE.md` with your existing secrets. Share only sanitized failures, the embedding model and Pinecone dimensions/metric. No paid cloud is required for the local workflow. Hosted live operation still needs a reachable backend; local MCP software does not provide that hosting. Human preference data and actual training/evaluation remain required for RLHF results.

## Delivery boundary

Code being included is not the same as a verified live integration. The downloadable project is an updated implementation, not a claim that accounts are connected, a GPU job has completed, or GitHub has received a push. Every external step must produce an actual successful result before its status is changed.
