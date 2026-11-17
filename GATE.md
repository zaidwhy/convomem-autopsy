# GATE: target selection (2026-11-18)

Searches used: 7 web searches, plus GitHub/HF API calls (issue trackers, dataset metadata). Excluded by brief: LongMemEval, LoCoMo.

## Three best candidates

1. **ConvoMem** (Salesforce/ConvoMem). CHOSEN. HF licence cc-by-nc-4.0, code repo Apache-2.0, 75,336 QA pairs, evidence messages are labelled per item, six categories incl. abstention, 3.8k HF downloads, 26 GitHub stars, listed as a supported benchmark in supermemory/memorybench. Only one independent report on its tracker, and it covers the `pre_mixed_testcases` files only, not `evidence_questions`.
2. **PersonaMem v1** (bowen-upenn/PersonaMem-v1, COLM 2025). MIT, 208 stars, 4-option multiple choice, ~252 MB. Rejected: its tracker already holds independent reports of exactly the checks requested (no-context baseline 49.2% on 128k, issue 41; option length leak on v2, issue 42; "error samples", issue 21). Little left that is not a repeat.
3. **MemoryAgentBench** (ai-hyz/MemoryAgentBench, ICLR-track paper arXiv 2507.05257). MIT, 489 stars, 11k HF downloads, 77 MB. Rejected: it is a re-packaging of existing datasets (includes LongMemEval-derived items, which are off limits here) and issue 10 already reports that questions are answerable from world knowledge without context.
(Also looked at: HaluMem, licence cc-by-nc-nd-4.0, issue 5 "A thread of errors in the dataset" already lists item errors.)

## Why ConvoMem
Widely enough used (vendor harness support, Salesforce, arXiv paper), downloadable, licence permits analysis, the benchmark documents its own validation pipeline (README "Answerability Test", "Necessity Test", "Evidence Integrity: verify evidence messages appear exactly once") which gives checkable claims, and no audit of the core `evidence_questions` data was found.

## Sources verified (fetched, not recalled)
- arXiv abs page https://arxiv.org/abs/2511.10523 : title "Convomem Benchmark: Why Your First 150 Conversations Don't Need RAG", authors Egor Pakhomov, Erik Nijkamp, Caiming Xiong, submitted 13 Nov 2025, cs.CL. The abstract page describes no validation process.
- HF dataset card https://huggingface.co/datasets/Salesforce/ConvoMem : front matter `license: cc-by-nc-4.0`; revision analysed `e3e9b39115b02346824c70d349350de738f8be41` (lastModified 2025-11-18, from HF API).
- GitHub https://github.com/SalesforceAIResearch/ConvoMem : README says "Apache License 2.0" (applies to code), HF card says CC BY-NC 4.0 (applies to data). Dataset README fetched with grep for licence/attribution/terms: only the front-matter licence line was present.

## Licence finding and handling
CC BY-NC 4.0 permits copying, sharing and adapting for non-commercial purposes with attribution. Analysis is permitted. Redistribution is permitted non-commercially but this project is local-only. As a precaution: `data/` is gitignored, `out/*.jsonl` and FINDING.md store item ids (file path + index), and short fragments (under 25 words) only. No full conversations are copied into tracked files.

## Prior-work search (recorded; none of it counted as a finding of this autopsy)
| Source | URL | Covers |
|---|---|---|
| ConvoMem GitHub issue 1 | https://github.com/SalesforceAIResearch/ConvoMem/issues/1 | 49% of `pre_mixed_testcases` cases contain evidence from more than one personId. Different files from the ones analysed here. |
| ConvoMem HF discussions | https://huggingface.co/datasets/Salesforce/ConvoMem/discussions | 0 discussions (API: count 0). |
| Web search "ConvoMem errors/answer key/critique" | (search results) | No third-party audit found; only the paper and summaries. |
| PersonaMem issues 41, 42, 21 | https://github.com/bowen-upenn/PersonaMem/issues/41 (and /42, /21) | Other benchmark; why it was rejected. |
| MemoryAgentBench issue 10 | https://github.com/HUST-AI-HYZ/MemoryAgentBench/issues/10 | Other benchmark; world-knowledge answerability. |
| HaluMem issue 5 | https://github.com/MemTensor/HaluMem/issues/5 | Other benchmark; item errors. |
| LoCoMo / LongMemEval audits | (web search) | Excluded benchmarks. |
Absence of an audit is "none found in about 7 searches plus the two trackers", not proof that none exists.
