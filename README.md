# ConvoMem autopsy

An audit of the answer key and the shortcuts in [ConvoMem](https://arxiv.org/abs/2511.10523)
(Salesforce AI Research, `Salesforce/ConvoMem` on Hugging Face), a conversational-memory benchmark
that had one public defect report when this started. The checks and the sample were fixed in
`PLAN.md` before any of them ran.

**Short version: the key is sound in the sample, and one category needs no memory at all.**

| Question | Answer |
|---|---|
| Wrong gold answers? | None found in 120 reviewed items. In the 60 drawn at random: 0 definite errors (Wilson 95% upper bound 6.0%), 2 ambiguous. |
| Answerable without memory? | Factual categories: no. A 3B model with the question alone scores 7 of 200 by string match, and none of the 7 is a real answer on reading. |
| A free category? | Yes. Every abstention gold is one constant refusal string. The same 3B model with no conversation gets 49 of 50, and the category is 21.7% of the items examined. |
| Guessable yes/no items? | "Yes" is the gold for 298 of the 473 yes/no golds (63.0%). |
| Leaked answers? | 8 of 45,159 questions contain their gold answer; 4 are answerable from the question alone. |
| Same question, different gold? | 72 items in 34 groups. All are context-dependent or paraphrases; none is a contradiction. |

Everything above, with intervals, per-category tables and the items by id, is in
[`FINDING.md`](FINDING.md).

## Scope

Hugging Face revision `e3e9b39115b02346824c70d349350de738f8be41`, `core_benchmark/evidence_questions`,
the first 45 files per category and evidence-count directory: 858 files, 45,159 items, about 65%
of that directory by size. `pre_mixed_testcases` and `filler_conversations` were not analysed.
`GATE.md` records why this benchmark was chosen and what prior reports exist (`prior_reports.csv`).

## Run it

Python 3, standard library only. The download is about 800 MB.

```
python -I checks/download.py       # pinned revision, writes data/convomem and out/manifest.json
python -I checks/run_checks.py     # about 2 minutes
python -I checks/summarize.py      # out/summary.md
python -I checks/show_item.py "<item id>" --brief
```

The no-memory baseline needs a local Ollama server:

```
python -I checks/no_memory_baseline.py --model llama3.2:3b --limit 300 --out out/no_memory_llama3.2_3b.jsonl
```

## Limits

- Both reviewers of the 120 items were language models, one blind to the other. No human read
  them. Agreement on the random 60 was 57 of 60; on 40 of the flagged items it was 13 of 40
  (FINDING.md gives the breakdown). Neither reviewer found a definite key error in either set.
- A subset by file order, not a random sample of personas.
- The no-memory baseline is one small model with string scoring, not the benchmark's own judge.
  The preference category was not scored.
- Nothing here says anything about any system's score on ConvoMem.

## Licences

Code in this repository is MIT. ConvoMem's data is CC BY-NC 4.0 and is not redistributed here;
the review files in `out/` quote short spans from it for non-commercial research, with item ids
that resolve against the pinned revision.
