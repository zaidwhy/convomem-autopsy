"""Record the post-hoc full-read verdicts (group "flagged_full") into out/hand_review.jsonl.

The verdicts were decided by reading the items (see PLAN.md change log, "post hoc"); this script only encodes them
and adds metadata computed from the data. Idempotent: skips (id, group) pairs already present.
Run: python -I checks/flagged_full.py
"""
import difflib, itertools, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, get_item, norm

PARAPHRASE_GROUPS = {4, 5, 6, 19}  # indices into the "semantic" D4 groups of out/d4_refined.jsonl (read by hand)
PATH = os.path.join(OUT, "hand_review.jsonl")
rows = [json.loads(x) for x in open(PATH, encoding="utf-8")]
done = {(r["id"], r["group"]) for r in rows}
prior_read = {r["id"] for r in rows if r["group"] in ("random", "flagged")}
out = []


def add(**kw):
    if (kw["id"], "flagged_full") not in done:
        kw["group"] = "flagged_full"
        out.append(kw)


def words(s, n=18):
    return " ".join(s.split()[:n])


# 1. D4 semantic groups
groups = [json.loads(x) for x in open(os.path.join(OUT, "d4_refined.jsonl"), encoding="utf-8")]
groups = [g for g in groups if g["class"] == "semantic"]
for gi, g in enumerate(groups):
    items = [get_item(i) for i in g["ids"]]
    conv_ids = [{c["id"] for c in it["conversations"] if c["containsEvidence"]} for it in items]
    distinct = not any(a & b for a, b in itertools.combinations(conv_ids, 2))
    same_file = len({i.split("|")[1] for i in g["ids"]}) == 1  # one file = one persona x one evidence-count directory
    para = gi in PARAPHRASE_GROUPS
    for iid, it in zip(g["ids"], items):
        add(id=iid, check="D4",
            verdict="correct",
            reason=("D4(c): sibling golds say the same thing in different words; no conflict."
                    if para else
                    "D4(a): gold matches this item's own evidence; sibling item has the identical question, different evidence conversation and a different gold."),
            quote=words(it["message_evidences"][-1]["text"]),
            d4_group=gi, d4_class=("paraphrase" if para else "context_dependent"), group_size=len(g["ids"]),
            siblings_same_file=same_file, siblings_distinct_evidence_conv_ids=distinct)

# 2. D3 items not read before
for line in open(os.path.join(OUT, "flags.jsonl"), encoding="utf-8"):
    f = json.loads(line)
    if not f.get("D3") or f["id"] in prior_read:
        continue
    it = get_item(f["id"])
    cand = [m["text"] for c in it["conversations"] if c["containsEvidence"] for m in c["messages"]]
    ncand = [norm(t) for t in cand]
    ratios, substr, first = [], False, None
    for e in it["message_evidences"]:
        tn = norm(e["text"])
        if any(tn in m for m in ncand):
            continue
        best = max(ncand, key=lambda m: difflib.SequenceMatcher(None, tn, m, autojunk=False).ratio())
        ratios.append(difflib.SequenceMatcher(None, tn, best, autojunk=False).ratio())
        substr = substr or (best in tn)
        first = first or e["text"]
    r = min(ratios)
    kind = ("evidence label is longer than the conversation line (line is contained in it)" if substr
            else "evidence label reworded vs conversation line")
    if it["answer"] and f["cat"] == "abstention_evidence":
        why = "refusal still right: no answer to the question in the evidence-bearing conversation lines checked"
    else:
        why = "gold supported by the conversation text or recomputed from it"
    add(id=f["id"], check="D3", verdict="evidence_label_wrong_answer_right",
        reason=f"Not a formatting artefact (alphanumeric-only match also fails); {kind}, min best ratio {r:.2f}; {why}.",
        quote=words(first), min_ratio=round(r, 3), label_longer_than_conv_line=substr)

# 3. S5 items
S5 = {
    "assistant_facts_evidence|1|0ca7f1fa-ba51-4f86-9c09-21a6ff295db2|63": ("binary_guess", "the question offers two options, hearts or liver"),
    "assistant_facts_evidence|1|4308b9d3-abb6-439b-94d5-246da7e0c420|68": ("binary_guess", "the question offers two options, Traditional or Roth"),
    "assistant_facts_evidence|1|581a7aa3-5c47-4995-98b8-bfc97915f8b5|30": ("answerable_from_question", "'use' is the obvious plain-word replacement for the quoted jargon verb"),
    "assistant_facts_evidence|1|617e451b-db92-4a23-a44a-7ad699dc1000|61": ("partly_guessable", "a generic podcast name is a likely guess from 'cycling podcast', not certain"),
    "user_evidence|1|3da2788d-3839-4060-8281-e12305b4b520|53": ("binary_guess", "the question offers two options, rescue or breeder"),
    "user_evidence|1|4c69f758-cc00-48db-a908-7485ef3c3d99|16": ("answerable_from_question", "the gold string is the certification named in the question"),
    "user_evidence|1|6778a296-5b31-4ed2-a576-eaa706712df9|45": ("answerable_from_question", "the gold is the channel name already spelled in the question"),
    "user_evidence|2|0050e213-5032-42a0-8041-b5eef2f8ab91|77": ("answerable_from_question", "the question states the duration (two months) that is the gold"),
}
for iid, (cls, why) in S5.items():
    it = get_item(iid)
    add(id=iid, check="S5", verdict="correct",
        reason=f"LEAK ({cls}): gold agrees with evidence; a reader without memory could {'answer' if cls == 'answerable_from_question' else 'guess'}: {why}.",
        quote=words(it["question"], 20), leak_class=cls)

with open(PATH, "a", encoding="utf-8") as fh:
    for r in out:
        fh.write(json.dumps(r) + "\n")
print(len(out), "records appended")
