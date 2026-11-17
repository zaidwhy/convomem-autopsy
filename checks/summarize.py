"""Aggregate out/flags.jsonl into out/summary.json and out/summary.md (count, denominator, rate, Wilson 95%)."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CATS, OUT, wilson

rows = [json.loads(x) for x in open(os.path.join(OUT, "flags.jsonl"), encoding="utf-8")]
raw = json.load(open(os.path.join(OUT, "summary_raw.json"), encoding="utf-8"))
dups = [json.loads(x) for x in open(os.path.join(OUT, "dups.jsonl"), encoding="utf-8")]

# metric -> (label, applicable-row predicate, hit predicate)
M = {
    "D1_empty_or_missing": (lambda r: True, lambda r: r["D1"]),
    "D2_personId_mismatch": (lambda r: not r["D1"], lambda r: r.get("D2")),
    "D3_evidence_pointer_missing": (lambda r: not r["D1"], lambda r: r.get("D3")),
    "D4_same_question_diff_answer": (lambda r: not r["D1"], lambda r: r.get("D4")),
    "S1_near_dup_question": (lambda r: not r["D1"], lambda r: r.get("S1_near")),
    "S1_near_dup_diff_gold": (lambda r: not r["D1"], lambda r: r.get("S1_near_contra")),
    "S2_short_gold_not_in_evidence": (lambda r: r.get("S2") is not None, lambda r: r.get("S2")),
    "S2_strict_miss_all_factual": (lambda r: "S2_strict_miss" in r, lambda r: r.get("S2_strict_miss")),
    "S2_strict_miss_short_gold": (lambda r: r.get("S2_short"), lambda r: r.get("S2_strict_miss")),
    "S2_num_digit_gold_not_in_evidence": (lambda r: "S2_num" in r, lambda r: r.get("S2_num")),
    "S3_stale_answer": (lambda r: "S3_stale" in r, lambda r: r.get("S3_stale")),
    "S3_order_inverted": (lambda r: not r["D1"] and r["n_ev"] > 1, lambda r: r.get("order_inverted")),
    "S4_abstention_gold_not_refusal": (lambda r: "S4" in r, lambda r: r.get("S4")),
    "S5_gold_in_question": (lambda r: not r["D1"], lambda r: r.get("S5")),
    "S6_evidence_text_multiple_matches": (lambda r: not r["D1"], lambda r: r.get("S6_multi")),
    "S6_evidence_also_in_unflagged_conv": (lambda r: not r["D1"], lambda r: r.get("S6_flag_mismatch")),
    "S6_n_ev_convs_ne_n_ev": (lambda r: not r["D1"], lambda r: r.get("n_ev_convs") != r.get("n_ev")),
    "S7_no_person_or_memory_cue": (lambda r: not r["D1"], lambda r: r.get("S7")),
    "FFFD_in_question_or_answer": (lambda r: not r["D1"], lambda r: r.get("fffd_qa")),
    "FFFD_in_evidence_text": (lambda r: not r["D1"], lambda r: r.get("fffd_ev")),
    "FFFD_in_any_conversation_message": (lambda r: not r["D1"], lambda r: r.get("fffd_conv")),
    "yes_no_question": (lambda r: not r["D1"], lambda r: r.get("yn_q")),
    "yes_no_gold_given_yn_question": (lambda r: r.get("yn_q"), lambda r: r.get("yn_gold") is not None),
    "gold_is_yes_given_yn_gold": (lambda r: r.get("yn_gold") is not None, lambda r: r.get("yn_gold") == "yes"),
}
out = {"revision": "e3e9b39115b02346824c70d349350de738f8be41", "n_items": len(rows), "metrics": {}, "trivial": raw["trivial"],
       "global_exact_dup_question_groups": raw["global_exact_dup_question_groups"],
       "dup_kinds": dict(collections.Counter(d["kind"] for d in dups)), "signatures": raw["signatures"]}
lines = ["| metric | stratum | hits | denominator | rate | Wilson 95% |", "|---|---|---|---|---|---|"]
for name, (app, hit) in M.items():
    for cat in ["ALL"] + CATS:
        sub = [r for r in rows if (cat == "ALL" or r["cat"] == cat) and app(r)]
        k = sum(1 for r in sub if hit(r))
        n = len(sub)
        lo, hi = wilson(k, n)
        out["metrics"][f"{name}|{cat}"] = {"hits": k, "n": n, "rate": (k / n if n else None), "ci": [lo, hi]}
        if n:
            lines.append(f"| {name} | {cat} | {k} | {n} | {k / n:.4f} | [{lo:.4f}, {hi:.4f}] |")
json.dump(out, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), indent=1)
open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(len(rows), "items summarised")
