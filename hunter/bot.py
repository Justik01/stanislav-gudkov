# bot.py - hunter daemon: hourly digest + button stats (stdlib only)
# Run: py -3 hunter/bot.py
import json
import logging
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from config import (
    CHAT_FILE, COLLECT_EVERY_SEC, LOG_FILE, MAX_DIGEST, STATS_FILE, TG_BOT_TOKEN,
)
import llm_filter
import sources

API = "https://api.telegram.org/bot" + TG_BOT_TOKEN + "/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger("hunter")

# next digest time (module-global so /start can trigger an immediate run)
_state = {"next_run": 0.0}


def tg(method, payload=None, timeout=45):
    body = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        API + method, data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def get_chat_id():
    if CHAT_FILE.exists():
        return CHAT_FILE.read_text().strip()
    return ""


def save_chat_id(cid):
    CHAT_FILE.write_text(str(cid), encoding="utf-8")


# --- digest ---

def _fmt_item(it):
    lines = ["📦 " + it["title"][:150], "Источник: " + it["source"]]
    if it.get("budget"):
        lines.append("Бюджет: " + it["budget"])
    if it.get("reason"):
        lines.append("Почему: " + it["reason"])
    if it.get("date"):
        lines.append("Дата: " + it["date"][:16])
    lines.append("Ссылка: " + it["url"])
    return "\n".join(lines)


def send_item(chat_id, it):
    kb = {"inline_keyboard": [[
        {"text": "взял", "callback_data": "act:took"},
        {"text": "мимо", "callback_data": "act:skip"},
    ]]}
    r = tg("sendMessage", {
        "chat_id": chat_id,
        "text": _fmt_item(it),
        "reply_markup": kb,
        "disable_web_page_preview": True,
    })
    if r.get("ok"):
        return r["result"]["message_id"]
    log.error("sendMessage failed: %s", r)
    return None


def run_digest():
    chat_id = get_chat_id()
    items, errors = sources.collect()
    for e in errors:
        log.warning("collect error: %s", e)
    if not items:
        log.info("no fresh items")
        return
    if not chat_id:
        log.info("waiting for /start in bot (%d fresh items kept)", len(items))
        return
    verdicts = llm_filter.classify(items)
    relevant = [v for v in verdicts if v["relevant"]]
    dropped = [v for v in verdicts if not v["relevant"]]
    sent = 0
    skipped_cap = 0
    for it in relevant:
        if sent >= MAX_DIGEST:
            skipped_cap += 1
            continue
        if send_item(chat_id, it):
            sent += 1
            sources.mark_seen([it["url"]])
    sources.mark_seen([v["url"] for v in dropped])
    if skipped_cap:
        sources.mark_seen([v["url"] for v in relevant[MAX_DIGEST:]])
        log.info("cap reached, dropped %d relevant", skipped_cap)
    log.info(
        "digest: fresh=%d relevant=%d sent=%d irrelevant=%d",
        len(items), len(relevant), sent, len(dropped),
    )


# --- telegram events ---

def _record_stats(action, text, url):
    stats = []
    if STATS_FILE.exists():
        try:
            stats = json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except Exception:
            stats = []
    m_src = re.search(r"Источник: (.+)", text)
    m_title = re.search(r"📦 (.+)", text)
    stats.append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "source": (m_src.group(1).strip() if m_src else "?"),
        "title": (m_title.group(1).strip()[:120] if m_title else "?"),
        "url": url,
    })
    STATS_FILE.write_text(
        json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def on_callback(cb):
    cbq = cb.get("callback_query") or {}
    data = cbq.get("data", "")
    msg = cbq.get("message") or {}
    mid, text = msg.get("message_id"), msg.get("text") or ""
    chat_id = ((msg.get("chat") or {}).get("id")) or get_chat_id()
    try:
        tg("answerCallbackQuery", {"callback_query_id": cbq.get("id", "")})
    except Exception:
        pass
    if data not in ("act:took", "act:skip") or not mid:
        return
    action = "took" if data == "act:took" else "skip"
    m_url = re.search(r"Ссылка: (\S+)", text)
    _record_stats(action, text, m_url.group(1) if m_url else "")
    try:
        tg("editMessageText", {
            "chat_id": chat_id, "message_id": mid,
            "text": text + ("\n\n✅ ВЗЯЛ" if action == "took" else "\n\n⏭ Мимо"),
        })
    except Exception as e:
        log.warning("editMessageText: %s", e)
    log.info("callback: %s | %s", action, text.split("\n")[0][:80])


def on_message(msg):
    cid = str((msg.get("chat") or {}).get("id", ""))
    if not cid or str(msg.get("from", {}).get("id", "")).endswith(""):
        pass
    if not cid:
        return
    if not get_chat_id():
        save_chat_id(cid)
        log.info("chat_id saved: %s - digest unlocked", cid)
        try:
            tg("sendMessage", {
                "chat_id": cid,
                "text": "✅ Охотник запущен. Дайджест заказов будет сюда раз в час.",
            })
        except Exception:
            pass
    _state["next_run"] = 0.0  # trigger immediate digest


def handle_update(u):
    if "callback_query" in u:
        on_callback(u["callback_query"])
    elif "message" in u:
        on_message(u["message"])


# --- main loop ---

def main():
    if not TG_BOT_TOKEN:
        print("FATAL: TG_BOT_TOKEN not set (hunter/.env)")
        sys.exit(1)
    try:
        me = tg("getMe")
        log.info("bot: @%s", me["result"]["username"])
    except Exception as e:
        log.error("getMe failed: %s", e)
        sys.exit(1)
    offset = 0
    while True:
        now = time.time()
        if now >= _state["next_run"]:
            try:
                run_digest()
            except Exception:
                log.exception("digest failed")
            _state["next_run"] = time.time() + COLLECT_EVERY_SEC
        try:
            r = tg("getUpdates", {"offset": offset, "timeout": 30}, timeout=45)
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                try:
                    handle_update(u)
                except Exception:
                    log.exception("update handle failed")
        except Exception as e:
            log.warning("getUpdates: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
