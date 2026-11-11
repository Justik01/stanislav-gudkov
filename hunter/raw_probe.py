# raw_probe.py - inspect raw OpenRouter response for a 20-item batch
import json
import urllib.request

import sources
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, USER_AGENT
from llm_filter import PROMPT


def main():
    items = sources._fl_items()[:20]
    data = [
        {"i": k, "src": it["source"], "text": (it["title"] + " — " + it["text"])[:700]}
        for k, it in enumerate(items)
    ]
    payload = PROMPT + "\n\nДанные (JSON):\n" + json.dumps(data, ensure_ascii=False)
    body = json.dumps({
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": payload}],
        "temperature": 0,
        "max_tokens": 12000,
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENROUTER_API_KEY,
            "X-Title": "client-search-hunter",
            "User-Agent": USER_AGENT,
        },
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=180).read().decode("utf-8"))
    if "error" in resp:
        print("API ERROR:", json.dumps(resp["error"])[:300])
        return
    ch = resp.get("choices", [{}])[0]
    msg = ch.get("message", {})
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning") or ""
    print("model:      " + str(resp.get("model")))
    print("finish:     " + str(ch.get("finish_reason")))
    print("content len:%d" % len(content))
    print("reasoning:  %d" % len(reasoning))
    print("usage:      " + json.dumps(resp.get("usage", {})))
    print("content head: " + content[:200].replace("\n", " "))
    print("reasoning head: " + reasoning[:150].replace("\n", " "))


if __name__ == "__main__":
    main()
