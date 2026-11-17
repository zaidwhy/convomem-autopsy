"""No-memory baseline for ConvoMem evidence_questions, against a LOCAL Ollama model.

Two passes per item:
  nocontext : the question alone.
  control   : the same question after a transcript of an UNRELATED item's evidence conversation
              (wrong-conversation control; chosen by seeded shuffle, never the item's own persona).
Resumable: results are appended to the output JSONL and (id, pass) pairs already present are skipped.
Scoring (deterministic, NOT the benchmark's own LLM judge, which is not reproducible offline):
  factual categories : correct if normalised gold is contained in the normalised response, or content-token
                       recall of gold in the response >= 0.8; token F1 also stored.
  abstention         : correct if the response matches the refusal pattern (checks/common.py REFUSAL).
  preference         : response stored, score null (rubric answers need a judge).
Endpoint is fixed to http://127.0.0.1:11434 (never localhost: IPv6 hang on this machine).

Examples:
  python -I checks/no_memory_baseline.py --dry-run
  python -I checks/no_memory_baseline.py --model llama3.1:8b --limit 300 --out out/no_memory_llama31.jsonl
"""
import argparse, json, os, random, sys, time, urllib.request, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CATS, OUT, REFUSAL, found, iter_items, norm, recall

ENDPOINT = "http://127.0.0.1:11434"
SYSTEM = "You are a helpful assistant. Answer the user's question briefly. If you do not know, say you do not know."


def f1(gold, pred):
    g, p = norm(gold).split(), norm(pred).split()
    k = sum((collections.Counter(g) & collections.Counter(p)).values())
    if not g or not p or k == 0:
        return 0.0
    pr, rc = k / len(p), k / len(g)
    return 2 * pr * rc / (pr + rc)


def transcript(item):
    convs = [c for c in item["conversations"] if c.get("containsEvidence")] or item["conversations"]
    return "\n".join(f"{m.get('speaker', '?')}: {m.get('text', '')}" for m in convs[0]["messages"])


def build_prompts(items, passes, seed):
    # seeded, deterministic sampling for reproducibility, not security
    rnd = random.Random(seed)  # craft-guard: allow sec-weak-random because deterministic seeded sampling, not security
    ids = list(items)
    for iid in ids:
        it = items[iid]
        pid = iid.split("|")[2]
        if "nocontext" in passes:
            yield iid, "nocontext", SYSTEM, it["question"]
        if "control" in passes:
            others = [o for o in ids if o.split("|")[2] != pid]
            wrong = items[rnd.choice(others)]
            yield iid, "control", SYSTEM, (
                "Here is an earlier conversation with the user:\n\n" + transcript(wrong) +
                "\n\nNow answer this question:\n" + it["question"])


def score(cat, gold, resp):
    if cat == "preference_evidence":
        return None, None
    if cat == "abstention_evidence":
        return bool(REFUSAL.search(resp)), None
    ok = found(gold, resp) or recall(gold, resp) >= 0.8
    return bool(ok), round(f1(gold, resp), 4)


def ask(model, system, user, seed):
    body = json.dumps({"model": model, "stream": False,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "options": {"temperature": 0, "seed": seed, "num_predict": 200}}).encode()
    req = urllib.request.Request(ENDPOINT + "/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["message"]["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--limit", type=int, default=300, help="items, stratified round-robin over the 6 categories")
    ap.add_argument("--seed", type=int, default=20261118)
    ap.add_argument("--passes", default="nocontext,control")
    ap.add_argument("--out", default=os.path.join(OUT, "no_memory_results.jsonl"))
    ap.add_argument("--dry-run", action="store_true", help="print first 3 prompts, no network, no file writes")
    a = ap.parse_args()
    passes = a.passes.split(",")
    rnd = random.Random(a.seed)  # craft-guard: allow sec-weak-random because deterministic seeded sampling, not security
    allitems = {iid: it for iid, cat, n, pid, i, it in iter_items()}
    by_cat = collections.defaultdict(list)
    for iid in sorted(allitems):
        by_cat[iid.split("|")[0]].append(iid)
    for c in by_cat.values():
        rnd.shuffle(c)
    chosen = []
    while len(chosen) < a.limit and any(by_cat.values()):
        for c in CATS:
            if by_cat[c] and len(chosen) < a.limit:
                chosen.append(by_cat[c].pop())
    sub = {i: allitems[i] for i in chosen}
    if a.dry_run:
        for n, (iid, p, s, u) in enumerate(build_prompts(sub, passes, a.seed)):
            if n >= 3:
                break
            print(f"--- prompt {n + 1}: id={iid} pass={p} model={a.model} endpoint={ENDPOINT} temperature=0 seed={a.seed}")
            print("[system]", s)
            print("[user]", u[:600] + (" ...[truncated for display]" if len(u) > 600 else ""))
        print(f"dry-run: {len(sub)} items selected, no network call made")
        return
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out, encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue  # truncated last line from an interrupted run: redo that pair
            done.add((r["id"], r["pass"]))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "a", encoding="utf-8") as fh:
        for iid, p, s, u in build_prompts(sub, passes, a.seed):
            if (iid, p) in done:
                continue
            t = time.time()
            resp = ask(a.model, s, u, a.seed)
            ok, f = score(iid.split("|")[0], sub[iid]["answer"], resp)
            fh.write(json.dumps({"id": iid, "pass": p, "model": a.model, "response": resp, "correct": ok, "f1": f,
                                 "secs": round(time.time() - t, 2)}) + "\n")
            fh.flush()


if __name__ == "__main__":
    main()
