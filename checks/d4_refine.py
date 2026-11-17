"""Post-hoc refinement of D4 (see PLAN change log). For each D4 group in out/dups.jsonl, load the gold answers and mark the group
'semantic' if the minimum pairwise token Jaccard of the normalised golds is below 0.5, else 'paraphrase'.
Writes out/d4_refined.jsonl. Run: python -I checks/d4_refine.py"""
import json, os, sys, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, get_item, norm

rows = []
for line in open(os.path.join(OUT, "dups.jsonl"), encoding="utf-8"):
    d = json.loads(line)
    if d["kind"] != "D4_contradiction":
        continue
    golds = [norm(get_item(i)["answer"]).split() for i in d["ids"]]
    mj = min(len(set(a) & set(b)) / max(1, len(set(a) | set(b))) for a, b in itertools.combinations(golds, 2))
    rows.append({"ids": d["ids"], "cat": d["ids"][0].split("|")[0], "min_gold_jaccard": round(mj, 3),
                 "class": "semantic" if mj < 0.5 else "paraphrase"})
with open(os.path.join(OUT, "d4_refined.jsonl"), "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
c = collections.Counter((r["cat"], r["class"]) for r in rows)
print(len(rows), "groups;", {f"{k[0]}:{k[1]}": v for k, v in c.items()},
      "items in semantic groups:", sum(len(r["ids"]) for r in rows if r["class"] == "semantic"))
