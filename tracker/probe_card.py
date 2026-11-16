# probe_card.py - check if public 2GIS org page exposes phone/website
# Run: py -3 probe_card.py
import json
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
LEADS = r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker\leads.json"

PHONE_RE = re.compile(r"\+375[\d\s()-]{7,}|\+7 \(\d{3}\) [\d-]{7,}")
SITE_RE = re.compile(r"https?://(?!www\.2gis|2gis\.|ams2|d2|static)[\w.-]+\.(?:by|ru|com|net|org)(?:/[^\"'<> ]*)?")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    leads = [x for x in json.load(open(LEADS, encoding="utf-8")) if x["city"] == "Минск"][:3]
    for ld in leads:
        for tmpl in ("https://2gis.by/minsk/org/{id}", "https://2gis.ru/minsk/org/{id}"):
            url = tmpl.format(id=ld["id"])
            try:
                body = fetch(url)
                phones = sorted(set(PHONE_RE.findall(body)))
                sites = sorted(set(SITE_RE.findall(body)))[:6]
                print("%-45s %s len=%dK" % (ld["name"][:42], url.split("/")[2], len(body) // 1024))
                print("    phones:", phones[:4])
                print("    sites :", sites)
                break
            except Exception as e:
                print("%-45s %s ERR %s" % (ld["name"][:42], url.split("/")[2], str(e)[:70]))


if __name__ == "__main__":
    main()
