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
- 2026-11-18 (before any full check run, before the hand-review ids were drawn): calibration on 8 arbitrary files (550 items; not the hand-review draw) showed that implicit_connection_evidence gold answers are rubric text ("A good response should ..."), like preference_evidence, and that long multi-evidence gold answers are paraphrased syntheses. Definition changes: S2 is n/a for implicit_connection_evidence (reported n/a); S2 is flagged only when the normalised gold has 8 or fewer tokens; a new SUSPECT S2_num flags gold answers containing digits where no digit token of the gold appears in the evidence (catches computed totals, noisy by design); S2_strict_miss and recall are reported for all factual items. I read about 12 question/gold/evidence lines from these calibration items; they are not in the hand-review sample unless the seeded draw selects them.
- 2026-11-18: full checks run (45159 items, 858 files); samples drawn by checks/draw_sample.py (ids also in out/sample_ids.json). No sampled item had been read at the time of this entry. The abstention category has a single constant gold answer in all 8917 items (found by the trivial-strategy check), so S4 is 0 by construction.
```
RANDOM (seed 20261118, 10 per category, order = category order user, assistant_facts, changing, abstention, preference, implicit):
user_evidence|1|6778a296-5b31-4ed2-a576-eaa706712df9|40
user_evidence|2|443a4f82-82c4-4d72-8d82-63137b353a26|9
user_evidence|1|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|63
user_evidence|1|154abccb-c6b1-46b5-a1ae-56f2ca0fa3ac|32
user_evidence|1|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|30
user_evidence|1|6e1f20a7-0300-4f1e-9a4e-58ae0fa6b212|33
user_evidence|2|55031d4d-fdf6-4587-b77f-b40fc4e4d097|51
user_evidence|2|3561c082-8305-4543-96da-776fce1ff2bc|27
user_evidence|4|21863ea9-dde4-4917-87d4-2c4af770144a|76
user_evidence|3|142d7f3e-1d53-445e-9ad2-920df96b43ea|19
assistant_facts_evidence|3|7fac8a2b-7a81-42a0-a890-c7dc26d6a2ee|55
assistant_facts_evidence|1|26dfecae-3263-42be-9ed1-4d520830dd0b|57
assistant_facts_evidence|1|334374ad-67b7-40e1-b60b-3990b18d1612|81
assistant_facts_evidence|3|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|48
assistant_facts_evidence|5|33f68d2f-4463-4a91-880a-e513451a9577|3
assistant_facts_evidence|1|0050e213-5032-42a0-8041-b5eef2f8ab91|34
assistant_facts_evidence|1|33f68d2f-4463-4a91-880a-e513451a9577|79
assistant_facts_evidence|1|66a40728-11a8-4f6a-8064-fbf12953a97d|57
assistant_facts_evidence|1|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|43
assistant_facts_evidence|1|488705b9-6156-463a-b99b-07677f63db83|37
changing_evidence|2|03d6ce14-747d-43cb-8b31-d9c73391f58c|11
changing_evidence|2|4e7ed0f2-3172-4080-9b90-dcddb0202240|43
changing_evidence|3|0050e213-5032-42a0-8041-b5eef2f8ab91|52
changing_evidence|3|373af224-ef7f-4ac5-9242-c71c4406ea56|35
changing_evidence|2|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|91
changing_evidence|5|5d7bb371-4109-47a2-b1b8-c816675c69d3|12
changing_evidence|4|5d7bb371-4109-47a2-b1b8-c816675c69d3|29
changing_evidence|2|4e7ed0f2-3172-4080-9b90-dcddb0202240|45
changing_evidence|3|488705b9-6156-463a-b99b-07677f63db83|28
changing_evidence|2|3da2788d-3839-4060-8281-e12305b4b520|81
abstention_evidence|1|53c017a4-a4f6-4c03-bb43-97e01aff46c4|21
abstention_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|98
abstention_evidence|1|334374ad-67b7-40e1-b60b-3990b18d1612|58
abstention_evidence|3|419774f1-7859-4431-bc6d-1b77e6d51b01|1
abstention_evidence|2|639b1360-a1f6-4877-81eb-5d5179ac8eb2|29
abstention_evidence|1|53c017a4-a4f6-4c03-bb43-97e01aff46c4|46
abstention_evidence|1|142d7f3e-1d53-445e-9ad2-920df96b43ea|44
abstention_evidence|3|21863ea9-dde4-4917-87d4-2c4af770144a|5
abstention_evidence|1|46c13060-46dd-448f-b6c7-5e932c5e8a06|60
abstention_evidence|1|617e451b-db92-4a23-a44a-7ad699dc1000|86
preference_evidence|1|657f756f-62e3-46f3-ba05-e8d9afb9ef06|20
preference_evidence|1|465ce3ec-d796-40a6-87d6-b52f5edec483|68
preference_evidence|1|13f89975-b741-47b1-885c-f6e811ff91c5|85
preference_evidence|1|5bcaabf7-e488-405a-b7a0-8fde2d6a727a|89
preference_evidence|1|33f68d2f-4463-4a91-880a-e513451a9577|34
preference_evidence|1|60fc52e4-14b9-42bf-abfa-5059dc56d613|14
preference_evidence|1|334374ad-67b7-40e1-b60b-3990b18d1612|17
preference_evidence|1|53c017a4-a4f6-4c03-bb43-97e01aff46c4|74
preference_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|27
preference_evidence|1|29eb193c-9192-4741-bd11-47f2a2ac0ae1|33
implicit_connection_evidence|1|21863ea9-dde4-4917-87d4-2c4af770144a|4
implicit_connection_evidence|1|2421a17c-5d96-467e-b68b-2b175771bb38|5
implicit_connection_evidence|2|21836554-a95b-4d3e-a8ad-d376af985a71|44
implicit_connection_evidence|2|33f68d2f-4463-4a91-880a-e513451a9577|14
implicit_connection_evidence|2|3da2788d-3839-4060-8281-e12305b4b520|30
implicit_connection_evidence|1|488705b9-6156-463a-b99b-07677f63db83|49
implicit_connection_evidence|2|449033a5-c4a8-4f0f-973d-7b59a5656413|19
implicit_connection_evidence|2|13f89975-b741-47b1-885c-f6e811ff91c5|36
implicit_connection_evidence|2|334374ad-67b7-40e1-b60b-3990b18d1612|23
implicit_connection_evidence|1|38e5f5f7-b664-4ac2-b728-f07ae4d81730|29

FLAGGED (seed+1, round-robin over flag types):
changing_evidence|2|66a40728-11a8-4f6a-8064-fbf12953a97d|64  D3
changing_evidence|3|66a40728-11a8-4f6a-8064-fbf12953a97d|52  D4,S7
changing_evidence|3|66a40728-11a8-4f6a-8064-fbf12953a97d|28  S1_near_contra,S7
changing_evidence|2|3561c082-8305-4543-96da-776fce1ff2bc|25  S2
assistant_facts_evidence|2|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|19  S2_num
changing_evidence|4|46c13060-46dd-448f-b6c7-5e932c5e8a06|1  S3_stale,S7
assistant_facts_evidence|1|4308b9d3-abb6-439b-94d5-246da7e0c420|68  S5
changing_evidence|4|0050e213-5032-42a0-8041-b5eef2f8ab91|7  S7
changing_evidence|6|e4672e2e-3497-49ec-acb8-e7e33a2d97b9|68  D3
changing_evidence|3|46c13060-46dd-448f-b6c7-5e932c5e8a06|50  D4,S1_near_contra
assistant_facts_evidence|1|5bcaabf7-e488-405a-b7a0-8fde2d6a727a|26  S1_near_contra
changing_evidence|2|465ce3ec-d796-40a6-87d6-b52f5edec483|36  S2
assistant_facts_evidence|4|ac9249cf-db75-47a8-9ada-ec883528d07f|6  S2_num
changing_evidence|3|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|64  S3_stale
user_evidence|2|0050e213-5032-42a0-8041-b5eef2f8ab91|77  S5
changing_evidence|6|ebeea231-5e4a-4cae-a96d-d1090ea97513|61  S7
abstention_evidence|2|0050e213-5032-42a0-8041-b5eef2f8ab91|10  D3
changing_evidence|3|2421a17c-5d96-467e-b68b-2b175771bb38|25  D4
changing_evidence|4|488705b9-6156-463a-b99b-07677f63db83|15  D4,S1_near_contra,S2
changing_evidence|2|449033a5-c4a8-4f0f-973d-7b59a5656413|36  S2,S7
user_evidence|6|e4672e2e-3497-49ec-acb8-e7e33a2d97b9|40  S2_num
changing_evidence|3|488705b9-6156-463a-b99b-07677f63db83|72  S3_stale
user_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|16  S5
abstention_evidence|2|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|25  S7
abstention_evidence|1|06f8095e-9b97-4230-bf08-2b75ef6b0708|3  D3,S7
changing_evidence|5|13f89975-b741-47b1-885c-f6e811ff91c5|10  D4,S1_near_contra
changing_evidence|2|142d7f3e-1d53-445e-9ad2-920df96b43ea|22  D4,S1_near_contra,S7
changing_evidence|2|46c13060-46dd-448f-b6c7-5e932c5e8a06|85  S2,S2_num
assistant_facts_evidence|4|b47c1a1c-1808-4277-8a49-6527cf33c9b9|55  S2_num
changing_evidence|2|488705b9-6156-463a-b99b-07677f63db83|75  S3_stale
assistant_facts_evidence|1|617e451b-db92-4a23-a44a-7ad699dc1000|61  S5
changing_evidence|2|46c13060-46dd-448f-b6c7-5e932c5e8a06|32  S7
assistant_facts_evidence|1|03d6ce14-747d-43cb-8b31-d9c73391f58c|41  D3
changing_evidence|4|21863ea9-dde4-4917-87d4-2c4af770144a|49  D4,S1_near_contra,S7
implicit_connection_evidence|1|3da2788d-3839-4060-8281-e12305b4b520|12  D4,S1_near_contra
changing_evidence|3|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|46  S2
user_evidence|5|c0069684-23da-42ed-9ed2-82ef3670e318|44  S2_num
changing_evidence|3|1415aa1f-f0d8-43c4-920f-319ac8402308|32  S3_stale
assistant_facts_evidence|1|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|63  S5
changing_evidence|2|4a8730ba-6eb1-4e6c-b2d2-009f50070cfe|56  S7
user_evidence|2|29eb193c-9192-4741-bd11-47f2a2ac0ae1|44  D3
changing_evidence|2|142d7f3e-1d53-445e-9ad2-920df96b43ea|34  D4
changing_evidence|5|5d7bb371-4109-47a2-b1b8-c816675c69d3|7  D4,S1_near_contra,S7
user_evidence|1|639b1360-a1f6-4877-81eb-5d5179ac8eb2|58  S2
user_evidence|3|581a7aa3-5c47-4995-98b8-bfc97915f8b5|5  S2_num
changing_evidence|3|21863ea9-dde4-4917-87d4-2c4af770144a|75  S3_stale
user_evidence|1|6778a296-5b31-4ed2-a576-eaa706712df9|45  S5
changing_evidence|3|46c13060-46dd-448f-b6c7-5e932c5e8a06|10  S7
assistant_facts_evidence|3|e4672e2e-3497-49ec-acb8-e7e33a2d97b9|73  D3
implicit_connection_evidence|1|657f756f-62e3-46f3-ba05-e8d9afb9ef06|19  D4,S1_near_contra
implicit_connection_evidence|1|38e5f5f7-b664-4ac2-b728-f07ae4d81730|24  D4,S1_near_contra
changing_evidence|2|21836554-a95b-4d3e-a8ad-d376af985a71|6  S2,S2_num,S7
assistant_facts_evidence|3|28ae265c-22fe-4798-bbcc-fa98a8a3c9fa|20  S2_num
changing_evidence|3|154abccb-c6b1-46b5-a1ae-56f2ca0fa3ac|42  S3_stale
assistant_facts_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|30  S5
changing_evidence|4|46c13060-46dd-448f-b6c7-5e932c5e8a06|48  S7
assistant_facts_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|4  D3
changing_evidence|5|21863ea9-dde4-4917-87d4-2c4af770144a|36  D4,S1_near_contra,S7
changing_evidence|2|142d7f3e-1d53-445e-9ad2-920df96b43ea|12  D4,S1_near_contra,S7
changing_evidence|2|449033a5-c4a8-4f0f-973d-7b59a5656413|76  S2
```
- 2026-11-18 (after hand review): (1) D4 as defined (exact normalised question, different normalised gold) turned out to include paraphrase pairs ("Thursday at 1 PM" vs "The client meeting is scheduled for Thursday at 1 PM."). Post-hoc, `checks/d4_refine.py` splits D4 groups into "semantic" (minimum pairwise gold token Jaccard below 0.5) and "paraphrase". The raw D4 numbers stay in the report; the refined split is labelled post-hoc. (2) Hand review is complete: 60 random and 60 flagged items, verdicts in out/hand_review.jsonl. (3) Wilson interval lower bound is clamped to 0 in checks/common.py (cosmetic). (4) No sampled item was added or dropped after reading began.
- 2026-11-18 (post hoc, logged BEFORE reading; requested after the first write-up): extend hand review to all flagged items not yet read, recorded with group "flagged_full" so they never enter the random-sample rate. Scope: (1) all 72 items in D4 groups classed "semantic" in out/d4_refined.jsonl, verdict per group: (a) each gold right for its own evidence, evidence conversations differ (context-dependent question), (b) golds contradict on the SAME evidence (definite key error, quote), (c) paraphrase or superset (no conflict); plus from metadata only whether siblings share a file / conversation id; pre_mixed_testcases not downloaded. (2) all remaining D3 items (150 not yet read): answer supported with different wording / answer unsupported anywhere in the item's conversations (definite defect) / evidence present under a formatting difference (check artefact). A scripted pre-sort by alphanumeric-only containment is used to propose "formatting artefact", and its output is read. (3) all 8 S5 items: could a no-memory reader answer from the question alone. No LLM, no Ollama, no downloads.
