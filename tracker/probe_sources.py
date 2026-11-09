# probe_sources.py - check accessibility of candidate sources for client-search
# ASCII-only comments. Run: py -3 tracker/probe_sources.py
import re
import sys
import urllib.request
from xml.etree import ElementTree

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# candidate sources: name -> url
SOURCES = {
    # RSS feeds
    "FL.ru RSS (all)": "https://www.fl.ru/rss/all.xml",
    "FL.ru RSS (sites cat)": "https://www.fl.ru/rss/all.xml?category=saity",
    "Weblancer RSS": "https://www.weblancer.net/jobs.rss",
    "Freelance.ru RSS": "https://freelance.ru/jobs.rss",
    "Habr freelance RSS": "https://habr.com/ru/rss/hubs/freelance/projects/?fl=ru",
    "Work24 RSS": "https://work24.ru/rss",
    # HTML pages (order feeds)
    "Kwork orders page": "https://kwork.ru/orders",
    "FL.ru projects page": "https://www.fl.ru/projects",
    # Telegram public previews (t.me/s/)
    "TG job_developer": "https://t.me/s/job_developer",
    "TG freelance7": "https://t.me/s/freelance7",
    "TG tilda_profil": "https://t.me/s/tilda_profiI",
    "TG freelance_jobs_ru": "https://t.me/s/freelance_jobs_ru",
    "TG freelance_orders": "https://t.me/s/freelance_orders",
    "TG design_profiI": "https://t.me/s/design_profiI",
    "TG distantsiya": "https://t.me/s/distantsiya",
    "TG sova_freelance": "https://t.me/s/sova_freelance",
    "TG work_finde": "https://t.me/s/work_finde",
    "TG Koteyka_Freelancer": "https://t.me/s/Koteyka_Freelancer",
    "TG freelancebaraholka": "https://t.me/s/freelancebaraholka",
    "TG freelancetalk": "https://t.me/s/freelancetalk",
}

# relevance keywords: sites / bots / automation (Stas's profile)
KEYWORDS = re.compile(
    r"(сайт|лендинг|верстк|вёрстк|tilda|тинько|wordpress|вордпресс|webflow|"
    r"телеграм[- ]?бот|tg[- ]?бот|чат[- ]?бот|бот для|бота|"
    r"автоматизац|парсер|интеграц|crm|n8n|запис[а-я]* на сайт|"
    r"дизайн сайта|редизайн|интернет[- ]?магазин|адаптив)",
    re.IGNORECASE,
)


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def count_rss(text):
    """Count items and relevant items in RSS XML."""
    total = rel = 0
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return 0, 0
    for item in root.iter("item"):
        total += 1
        blob = " ".join(
            (item.findtext(k) or "") for k in ("title", "description")
        )
        if KEYWORDS.search(blob):
            rel += 1
    return total, rel


def count_tg(text):
    """Count messages in t.me/s/ preview and relevant ones."""
    # each message block has class tgme_widget_message_wrap
    blocks = re.findall(
        r'tgme_widget_message_wrap[^>]*>(.*?)</div>\s*</div>\s*</div>',
        text, re.S,
    )
    total = len(blocks)
    rel = sum(1 for b in blocks if KEYWORDS.search(b))
    return total, rel


def count_html(text):
    """Fallback: count keyword hits as rough signal."""
    rel = len(KEYWORDS.findall(text))
    return -1, rel  # total unknown


def main():
    print(f"{'source':38} {'status':8} {'total':>6} {'relevant':>8}")
    for name, url in SOURCES.items():
        try:
            text = fetch(url)
            status = "OK"
        except Exception as e:
            print(f"{name:38} {'FAIL':8} {str(e)[:40]}")
            continue
        if "rss" in name.lower() or url.endswith(".xml") or "rss" in url:
            total, rel = count_rss(text)
        elif "t.me/s/" in url:
            total, rel = count_tg(text)
        else:
            total, rel = count_html(text)
        tstr = str(total) if total >= 0 else "?"
        print(f"{name:38} {status:8} {tstr:>6} {rel:>8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
