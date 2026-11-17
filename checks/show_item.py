"""Print an item's question, gold, evidence messages and the evidence-bearing conversation messages to the terminal.
Usage: python -I checks/show_item.py <item_id> [--context 2]   (terminal only, writes nothing)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_item, norm


def main():
    iid = sys.argv[1]
    ctx = int(sys.argv[sys.argv.index("--context") + 1]) if "--context" in sys.argv else 2
    it = get_item(iid)
    print("ID", iid)
    print("Q:", it["question"])
    print("GOLD:", it["answer"])
    evn = [norm(e["text"]) for e in it["message_evidences"]]
    for k, e in enumerate(it["message_evidences"]):
        print(f"EV{k} [{e['speaker']}]:", e["text"])
    for ci, c in enumerate(it["conversations"]):
        if not c.get("containsEvidence"):
            continue
        ms = c["messages"]
        hit = [i for i, m in enumerate(ms) if any(x and x in norm(m["text"]) for x in evn)]
        print(f"-- conv {ci} ({len(ms)} msgs), evidence at {hit}")
        show = sorted({j for i in hit for j in range(max(0, i - ctx), min(len(ms), i + ctx + 1))})
        for j in show:
            print(f"   [{j}] {ms[j]['speaker']}: {ms[j]['text'][:500]}")


if __name__ == "__main__":
    main()
