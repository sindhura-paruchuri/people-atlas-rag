# Evaluation, feedback, and learning

## What is implemented

- Query/evidence/answer/latency/model-usage persistence in MySQL.
- One updatable thumbs-up/down rating per query in this single-workspace prototype.
- Citation-ID validity checks and refusal when the output lacks usable citations.
- A small offline lexical retrieval benchmark over fictional seed records.
- Regression checks for retrieval gaps, source URLs, and bad citations.

Run the offline checks from `backend`:

```bash
python -m unittest discover -s tests -v
python evaluate.py
```

The benchmark reports actual precision and recall for four explicitly labeled seed cases. It is not evidence of live Pinecone accuracy, answer faithfulness, or production quality.

## How to evaluate the live application

Build a reviewed dataset of representative questions with relevant person IDs, expected evidence sources, expected web-fallback behavior, and answers or refusals. Separate tuning cases from a held-out test set. Include unknown people, ambiguous identities, partial skill matches, stale records, conflicting sources, empty search results, and prompt-injection text inside evidence.

Measure recall@k and precision@k for retrieved IDs; citation correctness and factual support through human review; correct refusal rate; fallback routing accuracy; p50/p95 latency; provider token usage and cost. Record model, embedding, index, prompt, and threshold versions with every benchmark. Automatic citation syntax validity is not faithfulness.

## Feedback-to-improvement loop

Review negative ratings together with question and evidence. Label whether the failure arose in missing data, retrieval, routing, source quality, or generation. Improve data, filters, prompts, or reranking; evaluate the change on held-out questions before rollout. Never automatically ingest an arbitrary user correction as a verified fact.

This is evaluation-driven retrieval improvement. There is no automatic online self-training. The new `training/` directory contains an experimental reward-model and RLHF trainer; it has not yet been run on genuine human preference data. Real RLHF is a distinct future training project: collect consented preference pairs, audit them, train/evaluate a reward or preference model, use an appropriate fine-tuning algorithm, and compare against a frozen baseline. The collected binary ratings alone do not constitute RLHF.


The bundled HotpotQA development evaluation answers are separate from indexed documents. Do not claim held-out generalization from these development examples. A/B preferences are split by query ID before reward-model training; assess generated answers independently before any checkpoint promotion.
