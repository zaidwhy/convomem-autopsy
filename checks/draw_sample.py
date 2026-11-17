"""Draw the hand-review samples (ids only). Needs out/flags.jsonl. Run: python -I checks/draw_sample.py"""
import json, os, random, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CATS, OUT

SEED = 20261118
FLAGS = ["D3", "D4", "S1_near_contra", "S2", "S2_num", "S3_stale", "S4", "S5", "S6_flag_mismatch", "S7"]


def main():
    rows = [json.loads(x) for x in open(os.path.join(OUT, "flags.jsonl"), encoding="utf-8")]
    rnd = random.Random(SEED)  # craft-guard: allow sec-weak-random because seeded sampling for reproducibility, not security
    by_cat = collections.defaultdict(list)
    for r in rows:
        by_cat[r["cat"]].append(r["id"])
    rand_ids = []
    for c in CATS:
        rand_ids += rnd.sample(sorted(by_cat[c]), 10)
    rset = set(rand_ids)
    rnd2 = random.Random(SEED + 1)  # craft-guard: allow sec-weak-random because seeded sampling for reproducibility, not security
    pools = collections.defaultdict(list)
    for r in rows:
        if r["id"] in rset:
            continue
        hit = [f for f in FLAGS if r.get(f)]
        for f in hit:
            pools[f].append((r["id"], hit))
    for f in pools:
        pools[f].sort()
        rnd2.shuffle(pools[f])
    flagged, seen = [], set()
    while len(flagged) < 60 and any(pools[f] for f in FLAGS):
        for f in FLAGS:
            while pools[f] and pools[f][-1][0] in seen:
                pools[f].pop()
            if pools[f] and len(flagged) < 60:
                iid, hit = pools[f].pop()
                seen.add(iid)
                flagged.append({"id": iid, "flags": hit})
    json.dump({"seed": SEED, "random": rand_ids, "flagged": flagged,
               "flag_pool_sizes": {f: sum(1 for r in rows if r.get(f)) for f in FLAGS}},
              open(os.path.join(OUT, "sample_ids.json"), "w", encoding="utf-8"), indent=1)
    print(len(rand_ids), "random,", len(flagged), "flagged")


if __name__ == "__main__":
    main()
