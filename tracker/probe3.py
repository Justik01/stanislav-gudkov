# probe3.py - HTML order feeds: Weblancer, Work24, Freelance.ru, Kwork
# ASCII-only comments. Run: py -3 tracker/probe3.py
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

PAGES = {
    "Weblancer projects": "https://www.weblancer.net/projects/",
    "Weblancer sites cat": "https://www.weblancer.net/projects/saity-pod-klyuch-58/",
    "Work24 orders": "https://work24.ru/orders",
    "Work24 main": "https://work24.ru/",
    "Freelance.ru projects": "https://freelance.ru/projects",
    "Kwork orders": "https://kwork.ru/orders",
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


def main():
    for name, url in PAGES.items():
        try:
            text = fetch(url)
        except Exception as e:
            print(f"{name:26} FAIL {str(e)[:50]}")
            continue
        # strip tags for keyword context, count link-like blocks
        links = len(re.findall(r'href="[^"]*(?:project|order|zakaz)[^"]*"', text, re.I))
        hits = len(KEYWORDS.findall(text))
        # try to detect "X hours ago" freshness markers
        fresh = len(re.findall(r"\d+\s*(?:мин|час|минут|hour|minute)", text, re.I))
        print(f"{name:26} OK len={len(text)} orderlinks={links} kwhits={hits} freshmarks={fresh}")


if __name__ == "__main__":
    sys.exit(main())
