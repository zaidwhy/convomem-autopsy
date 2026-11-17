"""Agreement between the second reviewer (out/second_review.jsonl) and the first reviewer
(out/hand_review.jsonl), joined on item id, reported separately for the random 60 and the flagged 40.
Usage: python -I checks/review_agreement.py"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import wilson

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALIAS = {"key_error": "definite_key_error", "unanswerable_from_context": "unanswerable"}


def load(name):
    out = {}
    with open(os.path.join(ROOT, "out", name), encoding="utf8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def kappa(pairs):
    n = len(pairs)
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def main():
    first, second = load("hand_review.jsonl"), load("second_review.jsonl")
    for grp in ("random", "flagged_full"):
        ids = [i for i, r in second.items() if r["group"] == grp]
        missing = [i for i in ids if i not in first]
        pairs, rows = [], []
        for i in ids:
            if i in first:
                a = ALIAS.get(first[i]["verdict"], first[i]["verdict"])
                b = ALIAS.get(second[i]["verdict"], second[i]["verdict"])
                pairs.append((a, b)); rows.append((i, a, b))
        n = len(pairs); k = sum(a == b for a, b in pairs)
        lo, hi = wilson(k, n)
        kap = kappa(pairs)
        print(f"== {grp}: n={n} (missing in first file: {len(missing)})")
        print(f"agreement {k}/{n} = {k/n:.3f}  Wilson95 [{lo:.3f}, {hi:.3f}]  kappa = {kap if kap is None else round(kap, 3)}")
        labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
        c = Counter(pairs)
        w = max(len(l) for l in labels) + 2
        print("rows = first reviewer, cols = second reviewer")
        print(" " * w + "".join(f"{l[:12]:>14}" for l in labels))
        for a in labels:
            print(f"{a:<{w}}" + "".join(f"{c[(a, b)]:>14}" for b in labels))
        print("disagreements:")
        for i, a, b in rows:
            if a != b:
                print(f"- {i}\n    first : {a} | {first[i].get('reason')}\n    second: {b} | {second[i].get('reason')}")
        print()


if __name__ == "__main__":
    main()
