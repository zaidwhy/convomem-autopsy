"""Build the id list for the blind second review: the 60 random-sample ids plus 40 ids drawn
(random.Random(4242)) from the flagged_full group of the first review file.
Only the 'id' and 'group' fields of out/hand_review.jsonl are read. Writes out/second_review_ids.json."""
import json, random, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = json.load(open(os.path.join(ROOT, "out", "sample_ids.json"), encoding="utf8"))["random"]
pool = []
with open(os.path.join(ROOT, "out", "hand_review.jsonl"), encoding="utf8") as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            if r["group"] == "flagged_full":
                pool.append(r["id"])
pool = sorted(set(pool))
flagged = random.Random(4242).sample(pool, 40)
json.dump({"random": rnd, "flagged_full": flagged, "flagged_pool_size": len(pool)},
          open(os.path.join(ROOT, "out", "second_review_ids.json"), "w", encoding="utf8"), indent=1)
print(len(rnd), len(flagged), len(pool))
