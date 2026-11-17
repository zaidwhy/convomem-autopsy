"""Append reviewer verdicts to out/hand_review.jsonl. Usage: python -I checks/record_review.py <group> <file.tsv>
TSV columns: item_id<TAB>verdict<TAB>reason<TAB>quote   (verdict: correct|key_error|ambiguous|unanswerable_from_context|evidence_label_wrong_answer_right)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT
OK = {"correct", "key_error", "ambiguous", "unanswerable_from_context", "evidence_label_wrong_answer_right"}
group = sys.argv[1]
with open(os.path.join(OUT, "hand_review.jsonl"), "a", encoding="utf-8") as fh:
    for line in open(sys.argv[2], encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        iid, verdict, reason, quote = line.split("\t")
        assert verdict in OK, verdict
        assert len(quote.split()) < 25, iid
        fh.write(json.dumps({"id": iid, "group": group, "verdict": verdict, "reason": reason, "quote": quote}) + "\n")
