# FINDING: ConvoMem `evidence_questions` autopsy

Benchmark: ConvoMem (Salesforce AI Research), arXiv 2511.10523, HF `Salesforce/ConvoMem`, data licence CC BY-NC 4.0 (code Apache-2.0).
Data revision: HF commit `e3e9b39115b02346824c70d349350de738f8be41` (2025-11-18). File hashes in `out/manifest.json`.
Scope: `core_benchmark/evidence_questions/**`, first 45 files (sorted by name; one persona per file) per category and evidence-count directory: 858 files, 45,159 items, 794 MB. The full directory is about 1.22 GB, so this is a subset, not a random sample of personas. `pre_mixed_testcases` and `filler_conversations` were not analysed.
Protocol: `PLAN.md` was committed before any check ran. Deviations are in its change log. Predictions are compared with results below.

## Headline

Zero definite key errors in 60 randomly drawn items (hand review, 0/60, Wilson 95% [0.0%, 6.0%]). Two of the 60 were judged ambiguous (3.3%, [0.9%, 11.4%]). On the defect classes that matter most for an answer key, this release is clean in the sample. The defects found are of another kind: sibling items that ask the identical question with different gold answers, 8 questions whose text contains the gold answer, and one constant gold string for the whole abstention category.

## Results of the scripted checks (all 45,159 items)

| check | hits | denominator | rate | Wilson 95% |
|---|---|---|---|---|
| D1 empty/missing field | 0 | 45159 | 0.00% | [0.00%, 0.01%] |
| D2 personId differs from file persona | 0 | 45159 | 0.00% | [0.00%, 0.01%] |
| D3 evidence text not found in evidence conversations (exact or ratio >= 0.9) | 158 | 45159 | 0.35% | [0.30%, 0.41%] |
| D4 same persona+category+question, different normalised gold (raw) | 100 | 45159 | 0.22% | [0.18%, 0.27%] |
| S1 near-duplicate question within persona | 327 | 45159 | 0.72% | [0.65%, 0.81%] |
| S1 near-dup with different gold (raw) | 149 | 45159 | 0.33% | [0.28%, 0.39%] |
| S2 short gold (<=8 tokens) not in evidence | 1290 | 27315 | 4.72% | [4.48%, 4.98%] |
| S2 strict miss, short gold only | 2743 | 6051 | 45.33% | [44.08%, 46.59%] |
| S2_num gold digits absent from evidence | 2161 | 27315 | 7.91% | [7.60%, 8.24%] |
| S3 stale answer (changing) | 14 | 10204 | 0.14% | [0.08%, 0.23%] |
| S3 evidence order differs from conversation order | 0 | 26412 | 0.00% | [0.00%, 0.01%] |
| S4 abstention gold not a refusal string | 0 | 8917 | 0.00% | [0.00%, 0.04%] |
| S5 gold inside question text | 8 | 45159 | 0.02% | [0.01%, 0.03%] |
| S6 evidence text matches more than one message | 117 | 45159 | 0.26% | [0.22%, 0.31%] |
| S6 evidence also in an unflagged conversation | 0 | 45159 | 0.00% | [0.00%, 0.01%] |
| S6 evidence-conversation count differs from evidence count | 24 | 45159 | 0.05% | [0.04%, 0.08%] |
| S7 no person or memory cue in question (world-knowledge heuristic) | 7242 | 45159 | 16.04% | [15.70%, 16.38%] |
| U+FFFD anywhere (question, answer, evidence, conversations) | 0 | 45159 | 0.00% | [0.00%, 0.01%] |
| yes/no-form question | 4119 | 45159 | 9.12% | [8.86%, 9.39%] |
| gold is "yes" among yes/no golds | 298 | 473 | 63.00% | [58.56%, 67.23%] |

Per category (hits, rate):

| check | user | assistant_facts | changing | abstention | preference | implicit |
|---|---|---|---|---|---|---|
| items | 9866 | 7245 | 10204 | 8917 | 4062 | 4865 |
| D3 | 21 (0.21%) | 62 (0.86%) | 14 (0.14%) | 57 (0.64%) | 0 | 4 (0.08%) |
| D4 raw | 0 | 6 (0.08%) | 79 (0.77%) | 0 | 0 | 15 (0.31%) |
| S1 near-dup | 9 (0.09%) | 23 (0.32%) | 161 (1.58%) | 116 (1.30%) | 0 | 18 (0.37%) |
| S2 short gold not in evidence | 244 (2.47%) | 192 (2.65%) | 854 (8.37%) | n/a | n/a | n/a |
| S2 strict miss, short gold | 423/1630 (25.95%) | 353/1693 (20.85%) | 1967/2728 (72.10%) | n/a | n/a | n/a |
| S5 | 4 | 4 | 0 | 0 | 0 | 0 |
| S7 | 718 (7.28%) | 166 (2.29%) | 3556 (34.85%) | 1848 (20.72%) | 720 (17.73%) | 234 (4.81%) |

S2 is n/a for abstention, preference and implicit_connection: their gold is a refusal string or rubric text ("A good response should ..."), not an answer string. Full tables with intervals: `out/summary.md`, `out/summary.json`.

D4 refinement (post-hoc, see PLAN change log): 47 raw D4 groups (100 items). 34 groups (72 items, 0.16% of items) have golds with token Jaccard below 0.5; the other 13 are paraphrases of one gold. Semantic groups by category: changing 26, implicit 5, assistant_facts 3. File: `out/d4_refined.jsonl`.

## Trivial strategies (check 3)

ConvoMem is open-ended: there are no answer options, so option position, longest option and unshared-option checks do not apply and were not run. Normalised exact match, one constant prediction for all items (preference excluded, rubric gold):

| stratum | n | distinct golds | best constant | hits | rate | Wilson 95% | uniform-random chance |
|---|---|---|---|---|---|---|---|
| abstention | 8917 | 1 | "There is no information in prior conversation(s) ..." | 8917 | 100.00% | [99.96%, 100%] | 100% (one distinct gold) |
| user, assistant_facts, changing | 27315 | 26675 | "15" | 13 | 0.05% | [0.03%, 0.08%] | 0.004% |
| all non-preference | 41097 | 31541 | the abstention string | 8917 | 21.70% | [21.31%, 22.09%] | 0.003% |

Every one of the 8917 abstention items has the same gold string, so "always refuse" scores 100% on that category and 21.7% overall. This follows from the design (abstention is scored as refusal). It means the abstention category cannot separate a memory system from an always-refuse policy unless the scores on the other categories are read next to it. Among the 473 yes/no golds, "always yes" gets 63.0% [58.6%, 67.2%] against 50% chance; those items are 1.0% of the subset.

## Hand review (check 5)

Sample: 60 random (10 per category, seed 20261118, ids committed in `PLAN.md` before reading) and 60 flagged (up to 60 from SUSPECT and D flags, seed+1, round-robin over flag types). The reviewer read the evidence messages and, where relevant, the neighbouring conversation lines. Verdicts and quotes: `out/hand_review.jsonl`. One reader (a model), not a second human; conversations were not read in full.

Random sample (n=60):

| verdict | count | rate | Wilson 95% |
|---|---|---|---|
| correct | 58 | 96.7% | |
| definite key error | 0 | 0.0% | [0.0%, 6.0%] |
| ambiguous | 2 | 3.3% | [0.9%, 11.4%] |
| unanswerable from context | 0 | 0.0% | [0.0%, 6.0%] |
| evidence label wrong, answer right | 0 | 0.0% | [0.0%, 6.0%] |

The two ambiguous items: `changing_evidence|2|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|91` (evidence says Company A was acquired by Company B; the question asks which to focus on; gold "Company B" is an inference) and `preference_evidence|1|334374ad-67b7-40e1-b60b-3990b18d1612|17` (the evidence is the user's private note colour system, the rubric applies it to a client QBR agenda).

Flagged set (n=60), reported separately and not part of the rate above: 0 key errors, 0 ambiguous, 8 "evidence label wrong, answer right", 52 correct. All 8 label cases were D3 items: the labelled evidence text differs from the conversation line (an extra clause, or two lines merged) while the answer is supported. Of the 52 correct, 12 carry a sibling-item conflict note and 7 a leak note (below).

Precision of each flag against key errors in the flagged set: S2 0 of 9, S2_num 0 of 9, S3 stale 0 of 7, S7 0 of 18, D3 0 of 8 (all 8 wording mismatches), D4 and S1 0 of 14 and 0 of 13 (12 genuine sibling conflicts and the rest paraphrase pairs), S5 0 of 7 (7 of 7 are leaks). None of the 18 S7 items was a world-knowledge question; all depend on conversation specifics, so the S7 heuristic does not identify memory-free questions.

Gold answers computed from evidence were recomputed by hand and are correct: student loan 15000 minus 10000 = 5000; pet first-year cost 350+500+12x75+4x120+250 = 2480 and recurring 75+40 = 115; six-category overshoot (plastics 35 vs 20, 75 percent, the largest); reversed ranked wine list (Chardonnay); 5000+500 = 5500 units.

## The clearest defects (none is a definite key error)

By the conservative rule (a quotable contradiction between gold and evidence) the samples contain no definite key error. The ten clearest other defects, labelled as what they are.

Sibling-item conflicts: the item agrees with its own evidence, but another item of the same persona asks the identical question with a different gold. Whether these collide depends on whether both items land in one context; that was not tested (see limitations).
1. `changing_evidence|3|46c13060-46dd-448f-b6c7-5e932c5e8a06|50` - "Where are we planning to hike this weekend?" gold "Rattlesnake Ledge"; siblings give "Discovery Park in Seattle." and "Ebey's Landing on Whidbey Island."
2. `changing_evidence|3|2421a17c-5d96-467e-b68b-2b175771bb38|25` - "What book is my book club reading this month?" gold 'The Midnight Library'; sibling gold 'Dune'.
3. `changing_evidence|5|13f89975-b741-47b1-885c-f6e811ff91c5|10` - "What color am I painting my home office?" gold 'Charcoal Gray'; sibling gold deep forest green.
4. `changing_evidence|4|21863ea9-dde4-4917-87d4-2c4af770144a|49` - "Who is Buster's veterinarian?" gold Dr. Rodriguez; siblings give Dr. Garcia and Dr. Singh.
5. `changing_evidence|5|5d7bb371-4109-47a2-b1b8-c816675c69d3|7` - "What is the company's work-from-home policy?" gold four office days; sibling gold two remote days.

Answer inside the question (S5: 8 items in the subset; the first pass read 7, the extension read all 8):
6. `assistant_facts_evidence|1|4308b9d3-abb6-439b-94d5-246da7e0c420|68` - the question offers "Traditional or Roth", gold "Roth".
7. `user_evidence|2|0050e213-5032-42a0-8041-b5eef2f8ab91|77` - the question says "moved into my townhouse two months ago", gold "Two months."
8. `user_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|16` - gold "Digital Marketing Analytics" is the question's own phrase.
9. `user_evidence|1|6778a296-5b31-4ed2-a576-eaa706712df9|45` - gold "urgent-deal-support", the question says "urgent deal support".
10. `assistant_facts_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|30` - the question quotes a jargon verb and asks for the shorter word the assistant suggested in its place; gold "use".

## Confirmed flaws (post-hoc full reads, group `flagged_full`)

Added after the first write-up, at the coordinator's request, and logged in `PLAN.md` before reading. These are census reads of every item a check flagged, not samples, and they are kept out of the random-sample result above (0/60 key errors, unchanged). Verdicts: `out/hand_review.jsonl`, records with `"group": "flagged_full"` (230 records; 14 of the 72 D4 items and 8 D3 items were also read in the first pass under `flagged`).

| flaw | count | denominator | rate, Wilson 95% | read in full | example ids |
|---|---|---|---|---|---|
| Evidence label text is not verbatim in the item's conversations; the answer is still supported | 158 | 45159 items | 0.35% [0.30%, 0.41%] | yes, all 158 | `changing_evidence|2|66a40728-11a8-4f6a-8064-fbf12953a97d|64`, `assistant_facts_evidence|1|03d6ce14-747d-43cb-8b31-d9c73391f58c|41` |
| Evidence label present only under a formatting difference (whitespace, quotes, unicode): a check artefact | 0 | 158 D3 items | 0.00% [0.00%, 2.37%] | yes | none (an alphanumeric-only match also failed for all 150 new items) |
| Answer not supported anywhere in the item's conversations (definite defect) | 0 | 45159 items | 0.00% [0.00%, 0.01%] | yes, all 158 D3 items | none |
| Same persona, identical question, different gold, each gold right for its own evidence (context-dependent question) | 63 items in 30 groups | 45159 items | 0.14% [0.11%, 0.18%] | yes, all 72 D4-semantic items | `changing_evidence|3|46c13060-46dd-448f-b6c7-5e932c5e8a06|50`, `changing_evidence|4|21863ea9-dde4-4917-87d4-2c4af770144a|49` |
| Same, golds contradict each other on the same evidence (definite key error) | 0 | 72 items, 34 groups | 0.00% [0.00%, 5.07%] of items | yes | none |
| Sibling golds are paraphrases of one answer (no conflict) | 9 items in 4 groups | 72 items | n/a | yes | `changing_evidence|2|142d7f3e-1d53-445e-9ad2-920df96b43ea|12` group (Thursday at 1 PM), `changing_evidence|3|443a4f82-82c4-4d72-8d82-63137b353a26|19` (virtual kick-off pair) |
| Gold answer inside the question text; a reader with no memory could answer or guess | 8 | 45159 items | 0.02% [0.01%, 0.04%] | yes, all 8 | `user_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|16`, `assistant_facts_evidence|1|4308b9d3-abb6-439b-94d5-246da7e0c420|68` |
| Abstention category has one constant gold string | 8917 | 8917 abstention items | 100% [99.96%, 100%] | yes (census) | `abstention_evidence|1|53c017a4-a4f6-4c03-bb43-97e01aff46c4|21`, `abstention_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|98` |

Details of the three reads:

- D4 (72 items, 34 semantic groups). 30 groups (63 items) are class (a): each gold fits its own evidence and the evidence conversations differ. 4 groups (9 items) are class (c): paraphrases (client meeting Thursday at 1 PM, thermostat Thursday, exhibition Sunday, virtual kick-off). 0 groups are class (b): no pair shares an evidence conversation, so no gold contradicts another on the same evidence. Metadata only: in all 34 groups the sibling items have different evidence-conversation ids; 12 groups have siblings in the same file (same persona and evidence-count directory), 22 in different files. `pre_mixed_testcases` was not downloaded, so whether siblings ever share a context window is still untested. The 63 are a property of the design (a question that depends on which conversation is in context) until that is checked; they are not wrong against their own evidence.
- D3 (158 items, all read). All 158 are wording or label differences with the answer intact. Of the 150 read in the extension: 64 have an evidence label that is longer than the conversation line (the line is contained in the label, for example an extra opening clause or two lines merged), 62 have a best-match ratio of at least 0.85 (the check threshold of 0.90 split near-identical text), and 39 have a ratio below 0.6 (the labelled line is essentially absent from the conversation; 55 of the 150 are abstention items, where the refusal is still right because no conversation line gives the answer). None is a formatting artefact, so the corrected rate of formatting artefacts is 0 and the 0.35% stays as "evidence label not verbatim", with 0 unsupported answers.
- S5 (8 items, all read). A reader with no memory could answer from the question alone in 4: `user_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|16` (gold is the certification named in the question), `user_evidence|1|6778a296-5b31-4ed2-a576-eaa706712df9|45` (channel name already in the question), `user_evidence|2|0050e213-5032-42a0-8041-b5eef2f8ab91|77` (the duration is stated in the question), `assistant_facts_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|30` ('use' replacing a quoted jargon verb). A 50% guess between two options named in the question in 3 (`assistant_facts_evidence|1|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|63`, `assistant_facts_evidence|1|4308b9d3-abb6-439b-94d5-246da7e0c420|68`, `user_evidence|1|3da2788d-3839-4060-8281-e12305b4b520|53`). Partly guessable in 1 (`assistant_facts_evidence|1|617e451b-db92-4a23-a44a-7ad699dc1000|61`).

Still unread: the S2, S2_num, S7 and S1 near-duplicate flag populations beyond the 60-item flagged sample (1290, 2161, 7242 and 327 items; in the sample these flags had 0 key errors, and S7 found no world-knowledge question). The unflagged remainder of the subset (the 60-item random sample is the only evidence there) and the roughly 35% of data (by size) outside the subset.

## What prior reports already covered

Not counted above (`prior_reports.csv`): ConvoMem GitHub issue 1 (49% of `pre_mixed_testcases` cases contain evidence from more than one personId; different files from those analysed here). No third-party audit of `evidence_questions` was found in about 7 web searches, the GitHub tracker (1 issue) and the HF discussions (0). The sibling-conflict result concerns the same persona-sharing design but a different, per-item property. Other benchmarks' trackers (PersonaMem issues 41, 42, 21; MemoryAgentBench issue 10; HaluMem issue 5) were read only for target selection.

## Predictions versus results

| quantity | predicted | observed |
|---|---|---|
| D1, D2 | 0 | 0, 0 |
| D3 | under 1% | 0.35% |
| D4 | under 0.5% | 0.22% raw, 0.16% semantic (post-hoc) |
| exact duplicate questions | under 1% | 33 same-answer groups and 47 conflicting groups; both under 1% |
| U+FFFD in text | 1 to 5% | 0%. Wrong: the replacement character seen in the terminal was Windows console rendering of em dashes and curly quotes; the files contain no U+FFFD. |
| S2 user / assistant / changing / implicit | 10 / 25 / 15 / 50% | 2.5 / 2.7 / 8.4 / n/a. Measured on short golds only, after a pre-run definition change; the implicit guess was wrong in kind (rubric gold). |
| S4 | 10% | 0%: one constant gold string |
| S5 | under 2% | 0.02% |
| most-common-answer accuracy | under 3% | 0.05% on factual categories; 100% on abstention (not predicted) |
| S7 | under 3% | 16.0%, but 0 of 18 reviewed were world-knowledge: the heuristic is weak |
| yes/no questions | under 5% | 9.1% question form, 1.0% yes/no gold |
| random-sample key error | 3% | 0% (0/60, upper bound 6.0%) |

## Limitations

- Subset of the data (858 files, about 65% by size), chosen by file-name order. Personas in the omitted files were not examined.
- The 60-item random sample gives an upper bound of 6.0% on the key-error rate; it cannot rule out a 1 to 3% rate. No per-category rate can be estimated from 10 items.
- Hand review by one reader, on evidence lines and their neighbours. For abstention items the check was that those lines do not give the answer, not an exhaustive search of every conversation. Long golds were read truncated in places (the visible part was checked).
- D3 uses ratio >= 0.9. All 158 D3 items were read in the post-hoc extension (8 in the first pass, 150 after); see the confirmed-flaws section.
- The post-hoc full reads checked D4 golds against the question and the final evidence message of each item (plus earlier evidence where a gold was computed or only partly visible), not against every filler line.
- Sibling conflicts: whether two siblings appear in one test-case context was not checked, because `pre_mixed_testcases` (roughly 28 GB by the HF file listing) was not downloaded. If siblings never share a context they do no harm; if they do, the gold is ambiguous there.
- S2 is a string heuristic. The 45% strict-miss rate on short golds mostly reflects sentence-form golds ("Your favorite local coffee shop is ...") against short evidence.
- The benchmark's necessity claim (question unanswerable without the evidence) was not tested; no LLM was run.
- Item ids are `category|N|personId|index`: N is the evidence-count directory, index is the position in the file's `evidence_items`.

## What this does NOT show

- No claim about any system's score, rank or leaderboard position on ConvoMem.
- No claim that the no-memory baseline was run. `checks/no_memory_baseline.py` exists and was tested only with `--dry-run`; no LLM was called by any part of this work.
- No claim about `pre_mixed_testcases`, `filler_conversations`, the personas, or the LoCoMo and LongMemEval re-packagings in the same repository.
- No claim that the benchmark's own validation pipeline (answerability and necessity tests, described in the code repository README) ran as described; only its output was examined.
- No claim that the key-error rate is zero, only that none was found in 120 reviewed items.

## Reproduce

From a clean clone (network needed for the download, about 800 MB; Python 3, standard library only):

```
python -I checks/download.py            # pinned revision; writes data/convomem and out/manifest.json
python -I checks/run_checks.py          # about 2 minutes; writes out/flags.jsonl (gitignored), out/dups.jsonl, out/summary_raw.json
python -I checks/summarize.py           # out/summary.json, out/summary.md
python -I checks/d4_refine.py           # out/d4_refined.jsonl
python -I checks/draw_sample.py         # out/sample_ids.json (same ids as recorded in PLAN.md)
python -I checks/review_summary.py      # out/review_summary.json from out/hand_review.jsonl
python -I checks/show_item.py "<item id>" --brief    # print one item to the terminal
```

No-memory baseline (not run; needs a local Ollama server on 127.0.0.1:11434 and a pulled model):

```
python -I checks/no_memory_baseline.py --dry-run
python -I checks/no_memory_baseline.py --model llama3.1:8b --limit 300 --out out/no_memory_llama31.jsonl
```

An end-to-end re-run from a fresh clone was not executed; each script was run in place.
