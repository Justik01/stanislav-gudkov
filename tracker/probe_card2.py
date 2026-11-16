# probe_card2.py - discover public org page URL format for 2GIS
# Run: py -3 probe_card2.py
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
ORG_ID = "70000001042582394"  # Trident, Minsk


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    # 1. variants of direct org url
    for url in (
        "https://2gis.by/minsk/org/%s" % ORG_ID,
        "https://2gis.by/minsk/firm/%s" % ORG_ID,
        "https://2gis.by/minsk/geo/70030076174471815/%s" % ORG_ID,
        "https://2gis.ru/moscow/org/%s" % ORG_ID,
    ):
        try:
            body = fetch(url)
            print("OK  %s len=%dK" % (url, len(body) // 1024))
        except Exception as e:
            print("ERR %s %s" % (url, str(e)[:60]))

    # 2. SSR search page: does it embed org links?
    q = urllib.parse.quote("Тридент стоматология Минск")
    for base in ("https://2gis.by/minsk/search/", "https://2gis.ru/moscow/search/"):
        try:
            body = fetch(base + q)
            hits = sorted(set(re.findall(r'/(?:minsk|moscow)/(?:org|geo|firm)/[^"\']+', body)))
            print("%s -> len=%dK orgish=%d" % (base, len(body) // 1024, len(hits)))
            for h in hits[:5]:
                print("    " + h[:110])
        except Exception as e:
            print("%s ERR %s" % (base, str(e)[:70]))


if __name__ == "__main__":
    main()
