# probe_cold.py - probe sources for company leads (site-less businesses)
# Run: py -3 probe_cold.py  -> prints reachability + website-field availability
import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 20

SITE_RE = re.compile(r"https?://(?!www\.(zoon|firmy|yell|2gis|avito|yandex|google))[\w.-]+\.[a-z]{2,}", re.I)


def get(url, headers=None, timeout=TIMEOUT):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def probe(name, fn):
    try:
        note = fn()
        print("%-34s OK   %s" % (name, note[:120]))
    except urllib.error.HTTPError as e:
        print("%-34s HTTP %d %s" % (name, e.code, (e.read().decode(errors="replace")[:80]).replace("\n", " ")))
    except Exception as e:
        print("%-34s ERR  %s" % (name, str(e)[:90]))


def p_2gis():
    url = "https://catalog.api.2gis.com/3.0/items?" + urllib.parse.urlencode(
        {"q": "кафе", "city_id": "4", "key": "rg"}  # no real key on purpose
    )
    status, body = get(url)
    return "status=%d body=%s" % (status, body[:80])


def p_places(ai_key):
    def f():
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + urllib.parse.urlencode(
            {"query": "cafe Gomel", "key": ai_key}
        )
        status, body = get(url)
        j = json.loads(body)
        return "status=%s results=%s" % (j.get("status"), len(j.get("results", [])))
    return f


def p_yandex():
    url = "https://yandex.ru/maps/213/moscow/?" + urllib.parse.urlencode({"text": "кафе"})
    status, body = get(url)
    orgs = set(re.findall(r"/org/\d+", body))
    return "status=%d org_links=%d size=%dK" % (status, len(orgs), len(body) // 1024)


def _zoon(host):
    status, body = get("https://" + host + "/")
    orgs = set(re.findall(r"/[a-z0-9-]+/\d+/", body))
    sites = SITE_RE.findall(body)
    return "status=%d orgish_links=%d ext_sites=%d" % (status, len(orgs), len(sites))


def _firmy(host):
    status, body = get("https://" + host + "/")
    cards = len(re.findall(r'href="/(?:[^"]+/)?\d+/', body))
    sites = SITE_RE.findall(body)
    return "status=%d card_links=%d ext_sites=%d" % (status, cards, len(sites))


def p_2gis_html():
    status, body = get("https://gomel.2gis.com/")
    return "status=%d size=%dK" % (status, len(body) // 1024)


def main():
    # google key via env (never stored in the file)
    import os
    gkey = os.environ.get("GOOGLE_KEY", "")

    print("--- api endpoints ---")
    probe("2gis catalog API (no key)", p_2gis)
    if gkey:
        probe("google places (key present)", p_places(gkey))
    else:
        probe("google places (no key yet)", p_places("x"))

    print("--- html catalogs ---")
    probe("yandex maps (org pages)", p_yandex)
    probe("gomel.2gis.com html", p_2gis_html)
    probe("zoon.ru root", lambda: _zoon("www.zoon.ru"))
    probe("gomel.zoon.ru", lambda: _zoon("gomel.zoon.ru"))
    probe("firmy.ru (gomel)", lambda: _firmy("gomel.firmy.ru"))
    probe("yell.ru (msk)", lambda: _firmy("www.yell.ru"))


if __name__ == "__main__":
    main()
