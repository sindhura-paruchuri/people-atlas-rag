# HotpotQA subset attribution

Source: https://huggingface.co/datasets/hotpotqa/hotpot_qa
Original project: https://hotpotqa.github.io/
License: CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/
Authors: Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W. Cohen, Ruslan Salakhutdinov, Christopher D. Manning (2018).
Paper: https://arxiv.org/abs/1809.09600

Derived from the first 20 rows of the distractor/train split, retrieved September 2026. Changes: deduplicated titles, concatenated context sentences, assigned stable IDs and source links, manually selected twelve biographical article titles. This derived data remains CC BY-SA 4.0. Individual source links lead to Wikipedia articles whose current revision may differ from these historical excerpts. Preserve attribution and license when redistributing.

`corpus.json` contains only context documents. `evaluation.json` contains gold questions and answers and MUST NOT be indexed. This development subset is not an independent held-out benchmark and its text contains historical claims. Larger imports can be prepared with `prepare_data.py`.
