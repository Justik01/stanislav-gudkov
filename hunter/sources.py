# sources.py - fetch fresh orders (FL.ru RSS + Telegram public previews)
import html as html_mod
import json
import re
import urllib.request
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

from config import FL_RSS, MAX_FRESH_PER_RUN, SEEN_CAP, SEEN_FILE, TG_CHANNELS, USER_AGENT

TAG_RE = re.compile(r"<[^>]+>")


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


# --- seen (dedup) ---

def load_seen():
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def mark_seen(urls):
    seen = load_seen()
    seen.update(urls)
    SEEN_FILE.write_text(
        json.dumps(list(seen)[-SEEN_CAP:], ensure_ascii=False), encoding="utf-8"
    )


# --- collectors ---

def _fl_items():
    root = ElementTree.fromstring(fetch(FL_RSS))
    out = []
    for it in root.iter("item"):
        link = (it.findtext("link") or "").strip()
        if not link:
            continue
        try:
            date = parsedate_to_datetime(it.findtext("pubDate") or "").isoformat()
        except Exception:
            date = ""
        out.append({
            "source": "FL.ru",
            "title": (it.findtext("title") or "").strip(),
            "text": (it.findtext("description") or "").strip(),
            "url": link,
            "date": date,
        })
    return out


def _tg_items(username):
    page = fetch("https://t.me/s/" + username)
    out = []
    for chunk in page.split("tgme_widget_message_wrap")[1:]:
        m_url = re.search(r'href="(https://t\.me/[^"]+/\d+)"', chunk)
        m_dt = re.search(r'datetime="([^"]+)"', chunk)
        m_txt = re.search(r"tgme_widget_message_text[^>]*>(.*?)</div>", chunk, re.S)
        if not m_url:
            continue
        raw = m_txt.group(1) if m_txt else ""
        text = html_mod.unescape(TAG_RE.sub(" ", raw))
        text = re.sub(r"\s+", " ", text).strip()
        out.append({
            "source": "@" + username,
            "title": text[:100],
            "text": text,
            "url": m_url.group(1),
            "date": m_dt.group(1) if m_dt else "",
        })
    return out


def collect():
    """Fresh (unseen) items from all sources, capped."""
    seen = load_seen()
    fresh, errors = [], []
    try:
        fresh += _fl_items()
    except Exception as e:
        errors.append("FL.ru: " + str(e))
    for ch in TG_CHANNELS:
        try:
            fresh += _tg_items(ch)
        except Exception as e:
            errors.append(ch + ": " + str(e))
    fresh = [i for i in fresh if i["url"] not in seen]
    return fresh[:MAX_FRESH_PER_RUN], errors
