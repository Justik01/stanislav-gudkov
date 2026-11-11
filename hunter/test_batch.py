# test_batch.py - validate classify() on a real 20-item batch (the failing path)
import llm_filter
import sources


def main():
    items = sources._fl_items()[:20]  # bypass seen - raw FL.ru feed
    verdicts = llm_filter.classify(items)
    llm = [v for v in verdicts if "LLM недоступен" not in v["reason"]]
    rel = [v for v in verdicts if v["relevant"]]
    print("batch=20 llm_verdicts=%d relevant=%d" % (len(llm), len(rel)))
    for v in verdicts[:6]:
        print("  %-5s | %-32s | %s" % (
            str(v["relevant"]), (v["reason"] or "")[:32], v["title"][:40]
        ))
    if not llm:
        print("RESULT: LLM path FAILED – all regex fallback")
    else:
        print("RESULT: LLM path OK")


if __name__ == "__main__":
    main()
