"""Summarise out/hand_review.jsonl. The random group and the flagged group are never mixed."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, wilson

rows = [json.loads(x) for x in open(os.path.join(OUT, "hand_review.jsonl"), encoding="utf-8")]
flags = {x["id"]: x["flags"] for x in json.load(open(os.path.join(OUT, "sample_ids.json"), encoding="utf-8"))["flagged"]}
res = {}
for g in ("random", "flagged"):
    sub = [r for r in rows if r["group"] == g]
    n = len(sub)
    c = collections.Counter(r["verdict"] for r in sub)
    res[g] = {"n": n, "verdicts": dict(c)}
    for v in ("key_error", "ambiguous", "unanswerable_from_context", "evidence_label_wrong_answer_right"):
        lo, hi = wilson(c.get(v, 0), n)
        res[g][v] = {"k": c.get(v, 0), "rate": c.get(v, 0) / n, "wilson95": [lo, hi]}
    res[g]["note_prefix"] = dict(collections.Counter(r["reason"].split(":")[0] for r in sub if ":" in r["reason"].split(" ")[0] + ":"
                                                     and r["reason"].split(":")[0] in ("SIBLING-CONFLICT", "LEAK")))
cat = collections.defaultdict(collections.Counter)
for r in rows:
    if r["group"] == "random":
        cat[r["id"].split("|")[0]][r["verdict"]] += 1
res["random_by_category"] = {k: dict(v) for k, v in cat.items()}
byflag = collections.defaultdict(collections.Counter)
for r in rows:
    if r["group"] == "flagged":
        for f in flags[r["id"]]:
            byflag[f][r["verdict"]] += 1
res["flagged_by_flag"] = {k: dict(v) for k, v in byflag.items()}
json.dump(res, open(os.path.join(OUT, "review_summary.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(res, indent=1))
