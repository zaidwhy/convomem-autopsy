"""Checks 1-3 and the static part of 4. Deterministic. Writes out/flags.jsonl, out/dups.jsonl, out/summary_raw.json.
Run: python -I checks/run_checks.py"""
import sys, os, json, difflib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FFFD = "�"
AUX = {"is", "are", "do", "does", "did", "can", "could", "will", "would", "has", "have", "should", "was", "were"}
os.makedirs(OUT, exist_ok=True)


def msgs_of(conv):
    return [(m.get("speaker"), m.get("text") if isinstance(m.get("text"), str) else "") for m in conv.get("messages", [])]


def analyse(item_id, cat, n_dir, pid_file, idx, it):
    f = {"id": item_id, "cat": cat, "n": n_dir}
    q, a = it.get("question"), it.get("answer")
    ev = it.get("message_evidences")
    convs = it.get("conversations")
    f["D1"] = (not isinstance(q, str) or not q.strip() or not isinstance(a, str) or not a.strip()
               or not isinstance(ev, list) or not ev or not isinstance(convs, list) or not convs)
    if f["D1"]:
        return f
    f["D2"] = it.get("personId") != pid_file
    ev_texts = [(e.get("speaker"), e.get("text") if isinstance(e.get("text"), str) else "") for e in ev]
    ev_all = " ".join(t for _, t in ev_texts)
    f["fffd_qa"] = any(FFFD in x for x in (q, a))
    f["fffd_ev"] = any(FFFD in t for _, t in ev_texts)
    f["fffd_conv"] = any(FFFD in t for c in convs for _, t in msgs_of(c))
    f["fffd_any"] = f["fffd_qa"] or f["fffd_ev"] or f["fffd_conv"]
    ev_convs = [c for c in convs if c.get("containsEvidence")]
    other_convs = [c for c in convs if not c.get("containsEvidence")]
    f["n_convs"], f["n_ev_convs"], f["n_ev"] = len(convs), len(ev_convs), len(ev)
    cand = [(ci, mi, s, norm(t)) for ci, c in enumerate(convs) if c.get("containsEvidence")
            for mi, (s, t) in enumerate(msgs_of(c))]
    missing, multi, pos, in_nonev = 0, 0, [], 0
    for sp, t in ev_texts:
        tn = norm(t)
        hits = [(ci, mi) for ci, mi, s, mn in cand if tn and tn in mn]
        if not hits:
            for ci, mi, s, mn in cand:
                if s != sp:
                    continue
                sm = difflib.SequenceMatcher(None, tn, mn, autojunk=False)
                if sm.real_quick_ratio() >= 0.9 and sm.quick_ratio() >= 0.9 and sm.ratio() >= 0.9:
                    hits = [(ci, mi)]
                    break
            if not hits:
                missing += 1
        if len(hits) > 1:
            multi += 1
        pos.append(hits[0] if hits else None)
        if tn:
            for c in other_convs:
                if any(tn in norm(x) for _, x in msgs_of(c)):
                    in_nonev += 1
                    break
    f["D3"] = missing > 0
    f["D3_count"] = missing
    f["S6_multi"] = multi > 0
    f["S6_flag_mismatch"] = in_nonev > 0
    f["S6_zero_ev_convs"] = len(ev_convs) == 0
    pp = [p for p in pos if p]
    f["order_inverted"] = pp != sorted(pp)
    if cat in ("preference_evidence", "implicit_connection_evidence", "abstention_evidence"):
        f["S2"] = None  # rubric-style or refusal gold answers: no answer string to look for
    else:
        strict = found(a, ev_all)
        rec = recall(a, ev_all)
        f["S2_recall"] = round(rec, 3)
        f["S2_short"] = len(norm(a).split()) <= 8
        f["S2_strict_miss"] = not strict
        f["S2"] = bool(f["S2_short"] and not strict and rec < 0.8)
        digs = [t for t in norm(a).split() if t.isdigit()]
        evt = set(norm(ev_all).split())
        f["S2_num"] = bool(digs and not any(d in evt for d in digs))
    if cat == "changing_evidence" and len(ev_texts) > 1:
        last = ev_texts[-1][1]
        earlier = " ".join(t for _, t in ev_texts[:-1])
        f["S3_stale"] = (not found(a, last)) and found(a, earlier)
    if cat == "abstention_evidence":
        f["S4"] = not REFUSAL.search(a)
    an = norm(a)
    f["S5"] = bool(len(an) >= 3 and an not in ("yes", "no") and found(a, q) and cat != "preference_evidence")
    f["S7"] = not has_person_or_cue(q)
    qt = norm(q).split()
    f["yn_q"] = bool(qt and qt[0] in AUX)
    f["yn_gold"] = an.split()[0] if an.split() and an.split()[0] in ("yes", "no") else None
    f["a_len"] = len(a)
    return f


def main():
    rows, byp = [], collections.defaultdict(list)
    sig = collections.Counter()
    ans_by_cat = collections.defaultdict(list)
    for item_id, cat, n, pid, i, it in iter_items():
        sig[(cat, tuple(sorted(it.keys())))] += 1
        r = analyse(item_id, cat, n, pid, i, it)
        rows.append(r)
        if not r["D1"]:
            byp[pid].append((item_id, cat, norm(it["question"]), norm(it["answer"])))
            if cat != "preference_evidence":
                ans_by_cat[cat].append(it["answer"])
    dups, exact_global = [], collections.defaultdict(list)
    d4, near, near_contra = set(), set(), set()
    for pid, L in byp.items():
        seen = collections.defaultdict(list)
        for iid, cat, qn, an in L:
            seen[(cat, qn)].append((iid, an))
            exact_global[qn].append(iid)
        for (cat, qn), g in seen.items():
            if len(g) > 1:
                kind = "D4_contradiction" if len({x[1] for x in g}) > 1 else "exact_dup_same_answer"
                dups.append({"kind": kind, "ids": [x[0] for x in g]})
                if kind == "D4_contradiction":
                    d4.update(x[0] for x in g)
        toks = [(iid, set(qn.split()), set(an.split())) for iid, cat, qn, an in L]
        for x in range(len(toks)):
            a = toks[x]
            for y in range(x + 1, len(toks)):
                b = toks[y]
                if not a[1] or not b[1] or min(len(a[1]), len(b[1])) / max(len(a[1]), len(b[1])) < 0.8:
                    continue
                if len(a[1] & b[1]) / len(a[1] | b[1]) >= 0.8:
                    near.update((a[0], b[0]))
                    if len(a[2] & b[2]) / max(1, len(a[2] | b[2])) < 0.5:
                        near_contra.update((a[0], b[0]))
                        dups.append({"kind": "near_dup_different_gold", "ids": [a[0], b[0]]})
    for r in rows:
        r["D4"] = r["id"] in d4
        r["S1_near"] = r["id"] in near
        r["S1_near_contra"] = r["id"] in near_contra
    with open(os.path.join(OUT, "flags.jsonl"), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "dups.jsonl"), "w", encoding="utf-8") as fh:
        for d in dups:
            fh.write(json.dumps(d) + "\n")

    def strat(ans):
        c = collections.Counter(norm(x) for x in ans)
        k = len(ans)
        mc = c.most_common(1)[0][0]
        out = {"n": k, "distinct": len(c), "chance_uniform": 1 / len(c)}
        for lab, pred in (("most_common", mc), ("longest", norm(max(ans, key=len))), ("first", norm(ans[0]))):
            hit = c[pred]
            lo, hi = wilson(hit, k)
            out[lab] = {"answer_norm_prefix": pred[:40], "hits": hit, "rate": hit / k, "ci": [lo, hi]}
        return out

    triv = {cat: strat(ans) for cat, ans in ans_by_cat.items()}
    triv["ALL_non_preference"] = strat([x for v in ans_by_cat.values() for x in v])
    triv["FACTUAL_user_assistant_changing"] = strat([x for c in ("user_evidence", "assistant_facts_evidence", "changing_evidence")
                                                     for x in ans_by_cat[c]])
    json.dump({"signatures": [{"cat": k[0], "keys": list(k[1]), "n": v} for k, v in sig.items()],
               "trivial": triv,
               "global_exact_dup_question_groups": sum(1 for v in exact_global.values() if len(v) > 1),
               "n_items": len(rows)}, open(os.path.join(OUT, "summary_raw.json"), "w", encoding="utf-8"), indent=1)
    print("items", len(rows), "dups", len(dups))


if __name__ == "__main__":
    main()
