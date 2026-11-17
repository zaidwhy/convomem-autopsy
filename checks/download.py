"""Download a deterministic subset of ConvoMem core_benchmark/evidence_questions at a pinned revision.
Subset rule: per directory (category/N_evidence), the first K files in sorted filename order (K=45).
Usage: python -I checks/download.py [--dest data/convomem]"""
import json, urllib.request, os, sys, collections, hashlib
REV = "e3e9b39115b02346824c70d349350de738f8be41"
K = 45
dest = sys.argv[sys.argv.index("--dest")+1] if "--dest" in sys.argv else "data/convomem"
api = f"https://huggingface.co/api/datasets/Salesforce/ConvoMem/revision/{REV}?blobs=true"
d = json.load(urllib.request.urlopen(api))
pre = "core_benchmark/evidence_questions/"
by = collections.defaultdict(list)
for s in d["siblings"]:
    if s["rfilename"].startswith(pre):
        by[s["rfilename"].rsplit("/", 1)[0]].append((s["rfilename"], s["size"]))
sel = [x for k in sorted(by) for x in sorted(by[k])[:K]]
from concurrent.futures import ThreadPoolExecutor
def get(item):
    p, sz = item
    out = os.path.join(dest, p[len(pre):])
    if not (os.path.exists(out) and os.path.getsize(out) == sz):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        tmp = out + ".part"
        urllib.request.urlretrieve(f"https://huggingface.co/datasets/Salesforce/ConvoMem/resolve/{REV}/{p}", tmp)
        os.replace(tmp, out)
    return {"path": p, "size": sz, "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest()}
order = sel[::-1] if "--reverse" in sys.argv else sel
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, order))
man = sorted(res, key=lambda m: m["path"])
json.dump({"revision": REV, "K": K, "files": man}, open("out/manifest.json", "w"), indent=1)
print(len(man), "files", sum(m["size"] for m in man), "bytes")
