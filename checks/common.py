"""Shared helpers: loading, normalisation, matching, Wilson interval."""
import json, os, re, glob, math, unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data", "convomem")
OUT = os.path.join(ROOT, "out")
CATS = ["user_evidence", "assistant_facts_evidence", "changing_evidence",
        "abstention_evidence", "preference_evidence", "implicit_connection_evidence"]

NUMW = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
MONTHS = {m: str(i + 1) for i, m in enumerate(
    "january february march april may june july august september october november december".split())}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = "9"
STOP = set("a an the of to in on at for and or is are was were be been it its this that with as by from i my me we our you your he she they them his her their do does did has have had not no".split())

REFUSAL = re.compile(r"(don'?t know|do not know|not mention|no information|haven'?t (been )?(told|mention|share|provid)|"
                     r"didn'?t (mention|say|share|provide|tell)|did not (mention|say|share|provide|tell)|not provided|cannot (find|answer|determine)|can'?t (find|answer|determine)|"
                     r"unable|no record|not specified|not available|(don'?t|do not) have|no mention|never (mention|told|said|share)|not (been )?(stated|shared|discussed|given)|"
                     r"isn'?t (mention|specified|provided)|wasn'?t (mention|specified|provided)|no details|not sure|unknown)", re.I)

_pro = re.compile(r"\b(i|my|me|mine|myself|we|our|us|you|your|yours)\b|\bi'(m|ve|d|ll)\b", re.I)
_cue = re.compile(r"\b(earlier|previous|previously|mentioned|told|said|discussed|last time|before|recall|remember|conversation|chat)\b", re.I)


def has_person_or_cue(q):
    return bool(_pro.search(q) or _cue.search(q))


def norm(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKC", s).replace("\ufffd", "").lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    s = re.sub(r"\b(\d+(?:\.\d+)?)\s*k\b", lambda m: str(int(float(m.group(1)) * 1000)), s)
    s = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", s)
    s = re.sub(r"[^\w\s]", " ", s)
    toks = []
    raw = s.split()
    for i, t in enumerate(raw):
        if t in NUMW:
            t = NUMW[t]
        elif t in MONTHS and not (t in ("may", "mar") and not ((i + 1 < len(raw) and raw[i + 1].isdigit()) or (i > 0 and raw[i - 1].isdigit()))):
            t = MONTHS[t]
        elif t.isdigit():
            t = str(int(t))
        toks.append(t)
    return " ".join(toks)


def contains(gold_n, text_n):
    if not gold_n:
        return False
    return (" " + gold_n + " ") in (" " + text_n + " ")


def found(gold, text):
    """True if gold (normalised, with simple date-order variant) is in text."""
    g, t = norm(gold), norm(text)
    if contains(g, t):
        return True
    p = g.split()
    if len(p) == 2 and all(x.isdigit() for x in p) and contains(p[1] + " " + p[0], t):
        return True
    return False


def content_tokens(s):
    return [t for t in norm(s).split() if t not in STOP]


def recall(gold, text):
    g = content_tokens(gold)
    if not g:
        return 0.0
    ts = set(norm(text).split())
    return sum(1 for t in g if t in ts) / len(g)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def files():
    return sorted(glob.glob(os.path.join(DATA, "*", "*", "*.json")))


def parse_path(p):
    p = p.replace("\\", "/")
    parts = p.split("/")
    cat, nev, fn = parts[-3], parts[-2], parts[-1]
    return cat, int(nev.split("_")[0]), fn[:36]


def iter_items(paths=None):
    """Yield (item_id, cat, n_evidence_dir, pid_in_filename, idx, item_dict)."""
    for p in (paths or files()):
        cat, n, pid = parse_path(p)
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for i, it in enumerate(d.get("evidence_items", [])):
            yield f"{cat}|{n}|{pid}|{i}", cat, n, pid, i, it


def get_item(item_id):
    cat, n, pid, i = item_id.split("|")
    for p in glob.glob(os.path.join(DATA, cat, f"{n}_evidence", f"{pid}_*.json")):
        with open(p, encoding="utf-8") as f:
            return json.load(f)["evidence_items"][int(i)]
    raise KeyError(item_id)
