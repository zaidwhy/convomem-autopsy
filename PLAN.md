# PLAN: ConvoMem autopsy (written before hand review; written after seeing only the file schema and the first item of one file, which was a user_evidence item about a spreadsheet colour)

## Target
- Benchmark: ConvoMem (Salesforce AI Research), arXiv 2511.10523, HF `Salesforce/ConvoMem`, data licence cc-by-nc-4.0.
- Data revision: HF commit `e3e9b39115b02346824c70d349350de738f8be41` (2025-11-18).
- Scope: `core_benchmark/evidence_questions/**` only (not `pre_mixed_testcases`, not `filler_conversations`, not `legacy_benchmarks`, which are LoCoMo/LongMemEval re-packagings and out of scope).
- Subset: full set is about 1.22 GB, over the 1 GB budget. `checks/download.py` takes, per directory (category x N_evidence), the first 45 files in sorted filename order (each file = one persona). About 794 MB. All counts below are for this subset, which is not a random sample of personas (sorted by uuid, so effectively arbitrary but not randomised).
- Item = one element of a file's `evidence_items` list. Item id = `{category}|{N}|{personId}|{index}`. Fields: question, answer, message_evidences[{speaker,text}], conversations[{messages[{speaker,text}], id, containsEvidence}], category (topic label), scenario_description, personId.
- Question type = evidence category: user_evidence, assistant_facts_evidence, changing_evidence, abstention_evidence, preference_evidence, implicit_connection_evidence. Secondary stratum: N (number of evidence messages).

## Normalisation (used everywhere)
Unicode NFKC, lowercase, curly quotes to straight, U+FFFD removed, punctuation to spaces, whitespace collapsed. Numbers: thousands separators removed, number words zero..twenty to digits, "k" suffix expanded ("15k" = "15000"), ordinal suffixes stripped. Dates: month names/abbreviations map to month numbers; a gold string counts as found if any of {original, digits-normalised, ISO yyyy-mm-dd, "month day", "day month"} variants occur.

## Definitions
DEFINITE (automatic) defects:
- D1 empty/missing/non-string question, answer, or empty message_evidences, or no conversations.
- D2 item personId differs from the personId in its file name.
- D3 evidence pointer missing: a message_evidences text is not found (normalised substring, or difflib ratio >= 0.9 against the best single message of the same speaker) in any conversation with containsEvidence=true.
- D4 contradiction: two items with identical normalised question in the same persona and category whose normalised answers differ.
SUSPECT (flagged, never counted as defects):
- S1 near-duplicate question (token Jaccard >= 0.8 on normalised text, within persona; global exact duplicates reported separately), with different gold (answer token Jaccard < 0.5) reported as "near-dup contradiction suspect".
- S2 gold answer (normalised/variants, answer length >= 3 chars, not yes/no) not contained in the concatenated message_evidences. Not applied to preference_evidence (rubric-style answers; reported n/a) or abstention.
- S3 changing_evidence only: gold found in an earlier evidence message but not in the last one ("stale answer"); evidence messages not appearing in the conversations in the listed order.
- S4 abstention_evidence: gold answer is not a refusal-type string (pattern list in `checks/common.py`).
- S5 gold contained in the question text.
- S6 evidence text found in more than one message across the evidence conversations (README claims "exactly once"); containsEvidence conversation count different from N.
- S7 world-knowledge heuristic: no first/second-person pronoun and no memory cue words (earlier, previous, mentioned, told, said, discussed, we, our, my, me, I, you, your) in the question.
- Reported counters, not defects: U+FFFD occurrences in question, answer, evidence text, and in any conversation message (encoding corruption); yes/no question rate and yes rate.

## Trivial strategies (check 3; ConvoMem is open-ended, there are no answer options, so option position/length checks do not apply and are not run)
Accuracy under normalised exact match of: always-most-common-answer (global and per category), always-longest-answer, always-first-answer. Chance reference = expected accuracy of a uniform random pick among distinct normalised gold answers of that stratum. Wilson 95% interval for each. Preference items excluded from exact match (rubric answers).

## No-memory baseline
`checks/no_memory_baseline.py` written, tested only with `--dry-run`. Not run. The benchmark's own scorer is an LLM judge (Scala code), not deterministic; the script scores with normalised containment of the gold answer and token F1 and says so. The abstention category is scored by refusal-pattern match.

## Hand review
- Random sample: 60 items, 10 per category (6 categories), drawn by `checks/draw_sample.py` with `random.Random(20261118)` over the sorted item id list of each category. Ids are appended to the change log below before any item is read.
- Flagged sample: SUSPECT items from S2, S3, S4, S5, S6, S7 (and S1), seeded draw (same seed, separate stream) of up to 60, stratified across flag types; ids recorded in the change log before reading.
- Review reads message_evidences and the evidence-bearing conversations. Verdicts: correct / key_error (gold contradicts evidence, quotable line required) / ambiguous / unanswerable_from_context / evidence_label_wrong_answer_right. For abstention items: "correct" means the question really has no answer in the evidence conversations. Be conservative; key_error needs a quote under 25 words.
- Headline rate: key_error share of the 60 random items, Wilson 95%. The flagged set is reported separately.

## Predictions (written before any check was run)
| Quantity | Prediction |
|---|---|
| D1 empty fields | 0 |
| D2 personId mismatch | 0 |
| D3 evidence pointer missing | under 1% of items |
| D4 contradictions | under 0.5% |
| Exact duplicate questions (within persona+category) | under 1% |
| Items with any U+FFFD in question/answer/evidence | 1 to 5% (a replacement character was visible in a conversation message of the first item) |
| S2 gold not in evidence | user 10%, assistant 25%, changing 15%, implicit 50% |
| S4 abstention non-refusal gold | 10% |
| S5 gold in question | under 2% |
| Most-common-answer accuracy | under 3% |
| S7 world-knowledge flag | under 3% |
| Yes/no questions | under 5% |
| Hand-review key_error rate, random 60 | 3% (interval will span about 1% to 11%) |

## Change log
- 2026-11-18: initial plan.
