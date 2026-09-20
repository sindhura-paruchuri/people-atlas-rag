# Human-feedback reinforcement learning

This directory now implements an **experimental RLHF training pipeline**, not just feedback logging. It trains a Bradley–Terry reward head from genuine A/B choices and updates a small open-weight language model with KL-regularized REINFORCE. This is a deliberately small educational implementation, not PPO, Gemini fine-tuning, or a claim of improved quality.

1. Connect the live RAG backend and answer questions.
2. Use **Generate answer comparison**. Review evidence and choose A/B, tie, or neither. Alternative generation consumes API quota. Ties/neither are preserved in MySQL but excluded from binary reward-model training.
3. Export from the project root, using the backend container's database access:

```bash
mkdir -p reviews
docker compose run --rm -v ./training:/training:ro -v ./reviews:/reviews api python /training/export_preferences.py /reviews
```

It writes train/validation JSONL grouped by query ID. Keep `reviews/` out of Git.
4. Install `training/requirements.txt` in an isolated training environment. Select a small causal model whose license permits your use. Model weights and downloads are external dependencies. Start with a small smoke run before spending GPU time.
5. Run:

```bash
python training/train_rlhf.py --model YOUR_TRAINABLE_MODEL --train reviews/train.jsonl --validation reviews/validation.jsonl --output runs/experiment-001 --steps 20
```

The trainer requires at least 10 training and 3 held-out genuine human comparisons. Those minima only enable a smoke run; they do not establish adequate statistical power. It saves policy/tokenizer weights, a reward head, training provenance, measured reward-model validation accuracy, and baseline/trained completions on held-out prompts. No human reviews or training metrics are fabricated.

**Release gate:** blindly review the held-out completions for groundedness, relevance, correct citations and refusals; compare to the baseline; reject regressions and reward hacking. Token/sequence limits make this a small-scale experiment. Larger models, distributed training, PPO, and production-grade statistical evaluation are not implemented. No training has been run yet because human preference data and training compute are absent.

Gemini remains the live answer provider. A trained checkpoint must be evaluated and served behind an OpenAI-compatible endpoint before deliberately changing `LLM_BASE_URL`, `LLM_MODEL`, and its server-side credential. Saving preferences never silently replaces the production model.
