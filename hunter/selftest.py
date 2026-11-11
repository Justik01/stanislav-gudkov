# selftest.py - verify bot token, collectors and LLM filter (run: py -3 selftest.py)
import json
import urllib.request

from config import OPENROUTER_MODELS, TG_BOT_TOKEN
import llm_filter
import sources


def main():
    # 1. bot token
    try:
        req = urllib.request.Request(
            "https://api.telegram.org/bot" + TG_BOT_TOKEN + "/getMe"
        )
        me = json.loads(urllib.request.urlopen(req, timeout=20).read())
        print("bot token: OK, @" + (me["result"]["username"] if me.get("ok") else "?"))
    except Exception as e:
        print("bot token: FAIL - " + str(e)[:100])
        return

    # 2. collectors
    items, errors = sources.collect()
    print("collect: %d fresh items, %d source errors" % (len(items), len(errors)))
    for e in errors:
        print("  err: " + e[:90])
    for it in items[:3]:
        print("  - [%s] %s" % (it["source"], it["title"][:60]))

    # 3. LLM filter on up to 5 items
    if items:
        print("llm models: " + OPENROUTER_MODELS)
        res = llm_filter.classify(items[:5])
        for r in res:
            print("  llm: %-5s | %-30s | %s" % (
                str(r["relevant"]), (r["reason"] or "")[:30], r["title"][:40]
            ))
    print("selftest done")


if __name__ == "__main__":
    main()
