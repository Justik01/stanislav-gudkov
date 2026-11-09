# probe2.py - round 2: find working RSS urls + measure posts-per-day rates
# ASCII-only comments. Run: py -3 tracker/probe2.py
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

RSS_CANDIDATES = {
    "Weblancer /rss": "https://www.weblancer.net/rss/",
    "Weblancer /jobs.rss?cat": "https://www.weblancer.net/jobs.rss?category=58",
    "Freelance.ru /rss": "https://freelance.ru/rss",
    "Freelance.ru /jobs/feed": "https://freelance.ru/jobs/feed",
    "Habr projects rss": "https://habr.com/ru/rss/projects/all/?fl=ru",
    "Habr habr/freelance": "https://habr.com/ru/rss/hubs/freelance/?fl=ru",
    "Work24 /feed": "https://work24.ru/feed",
    "Work24 /rss.xml": "https://work24.ru/rss.xml",
    "FL.ru cat=saity (param)": "https://www.fl.ru/rss/all.xml?category=saity",
    "FL.ru /rss/saity": "https://www.fl.ru/rss/saity.xml",
}

# TG channels: measure rate over last 20 visible posts
TG_CHANNELS = {
    "job_developer": "https://t.me/s/job_developer",
    "freelance7": "https://t.me/s/freelance7",
    "tilda_profiI": "https://t.me/s/tilda_profiI",
    "freelance_orders": "https://t.me/s/freelance_orders",
    "design_profiI": "https://t.me/s/design_profiI",
    "sova_freelance": "https://t.me/s/sova_freelance",
    "work_finde": "https://t.me/s/work_finde",
    "Koteyka_Freelancer": "https://t.me/s/Koteyka_Freelancer",
    "freelance_jobs_ru": "https://t.me/s/freelance_jobs_ru",
    "distantsiya": "https://t.me/s/distantsiya",
    "freelancebaraholka": "https://t.me/s/freelancebaraholka",
    "freelancetalk": "https://t.me/s/freelancetalk",
    "programming_jobs": "https://t.me/s/programming_jobs",
    "it_orders": "https://t.me/s/it_orders",
    "digitaltender": "https://t.me/s/digitaltender",
    "kadrof_work": "https://t.me/s/kadrof_work",
}

KEYWORDS = re.compile(
    r"(сайт|лендинг|верстк|вёрстк|tilda|тинько|wordpress|вордпресс|webflow|"
    r"телеграм[- ]?бот|tg[- ]?бот|чат[- ]?бот|бот для|бота|"
    r"автоматизац|парсер|интеграц|crm|n8n|"
    r"дизайн сайта|редизайн|интернет[- ]?магазин|адаптив)",
    re.IGNORECASE,
)


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def rss_probe():
    print("== RSS candidates ==")
    for name, url in RSS_CANDIDATES.items():
        try:
            text = fetch(url)
        except Exception as e:
            print(f"{name:34} FAIL {str(e)[:45]}")
            continue
        try:
            root = ElementTree.fromstring(text)
        except ElementTree.ParseError:
            print(f"{name:34} OK but not XML")
            continue
        items = list(root.iter("item"))
        # count items in last 24h
        fresh = rel24 = 0
        for it in items:
            pd = it.findtext("pubDate") or ""
            try:
                dt = parsedate_to_datetime(pd)
            except Exception:
                continue
            if datetime.now(timezone.utc) - dt < timedelta(hours=24):
                fresh += 1
                blob = (it.findtext("title") or "") + " " + (it.findtext("description") or "")
                if KEYWORDS.search(blob):
                    rel24 += 1
        print(f"{name:34} OK items={len(items)} last24h={fresh} relevant24h={rel24}")


def tg_probe():
    print("== TG channels (rate over visible window) ==")
    for name, url in TG_CHANNELS.items():
        try:
            text = fetch(url)
        except Exception as e:
            print(f"{name:26} FAIL {str(e)[:45]}")
            continue
        # message blocks with date
        blocks = re.findall(
            r'tgme_widget_message_wrap[^>]*>(.*?)</div>\s*</div>\s*</div>',
            text, re.S,
        )
        if not blocks:
            print(f"{name:26} OK but 0 messages (private/wrong name)")
            continue
        dates = []
        rel = 0
        for b in blocks:
            m = re.search(r'datetime="([^"]+)"', b)
            if m:
                try:
                    dates.append(datetime.fromisoformat(m.group(1).replace("Z", "+00:00")))
                except ValueError:
                    pass
            if KEYWORDS.search(b):
                rel += 1
        if len(dates) >= 2:
            span_h = (max(dates) - min(dates)).total_seconds() / 3600
            rate = len(blocks) / span_h * 24 if span_h > 0 else 0
            span_s = f"{span_h:.0f}h"
        else:
            rate, span_s = 0, "?"
        print(f"{name:26} OK msgs={len(blocks)} relevant={rel} span={span_s} ~{rate:.1f}/day")


if __name__ == "__main__":
    rss_probe()
    tg_probe()
    sys.exit(0)
