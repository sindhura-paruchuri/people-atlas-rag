# Cloud deployment

The website is already hosted. One Linux Compute Engine VM can run the current Docker Compose backend, including private MCP and MySQL. MySQL uses a named durable disk volume. This is a portfolio deployment; use managed MySQL, per-service secrets, backup/restore drills, app-user authorization and rate limits before expanding beyond owner access.

## Account details needed

Google Cloud project ID, billing/trial status, preferred region, agreed budget, and authenticated deployment access. Do not share passwords, card details, SSH private keys, or service-account JSON in chat. Provider credentials go into the VM's restricted `.env` or Secret Manager. GitHub access is separate.

## Deployment order

1. Review estimated VM, disk, network and backup cost for the chosen region. Select a modest CPU-only Linux VM; do not provision GPU training resources during backend setup.
2. Install Docker Engine and Compose on the VM; deploy the GitHub source checkout.
3. Copy `.env.example` to a private `.env`, configure service values, then run `docker compose up --build -d`.
4. Run `docker compose run --rm api python load_data.py` to apply additive tables and load the public corpus.
5. Run `docker compose --profile tools run --rm ingest` to populate the matching Pinecone index. Use the new `hotpotqa-v1` namespace.
6. Run `docker compose run --rm api python verify_integrations.py`. Save the output; do not call failed/skipped checks verified.
7. Put only the API behind an HTTPS reverse proxy or authenticated tunnel. The Docker network keeps MySQL, agent containers and MCP private. Restrict firewall rules. The API already requires its bearer credential; add request-rate and cost controls at the edge.
8. Configure the website's `RAG_API_URL` and `RAG_API_TOKEN` as server environment values and republish. The hosted frontend cannot call a laptop's localhost.
9. Verify a full question, source links, feedback, A/B preference, and database persistence after restart. Back up the MySQL volume. Do not use `docker compose down -v` unless intentionally deleting it.

## Credit restrictions (checked September 2026)

Eligible new customers can receive $300 for 90 days. Eligibility is account-specific. Trial credits do not cover Gemini Developer API usage through AI Studio or your direct Pinecone/SerpApi accounts. Non-billable trial accounts cannot add GPUs to VM instances. Upgrading billing can permit GPU use subject to availability and quota, but also enables charges beyond eligible credits. Budget alerts are not a hard spending cap.

Official references:
- https://cloud.google.com/free/docs/free-cloud-features
- https://ai.google.dev/gemini-api/docs/billing

RLHF has a separate training environment. Do not assume backend trial credits guarantee GPU availability or a free training run.
