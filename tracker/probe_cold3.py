# probe_cold3.py - discover real section urls (zoon gomel), onliner, 2gis.by
# Run: py -3 probe_cold3.py
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 20


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def show(name, url, rx, limit=8):
    try:
        status, body = get(url)
        hits = re.findall(rx, body)
        print("%-28s status=%d size=%dK hits=%d" % (name, status, len(body) // 1024, len(hits)))
        for h in hits[:limit]:
            print("    " + str(h)[:110])
        return body
    except Exception as e:
        print("%-28s ERR %s" % (name, str(e)[:90]))
        return ""


def main():
    # 1. zoon gomel root -> real section slugs
    b = show("gomel.zoon.ru root", "https://gomel.zoon.ru/",
             r'href="(https://gomel\.zoon\.ru/[a-z0-9-]+/?)"')
    slugs = sorted(set(re.findall(r"https://gomel\.zoon\.ru/([a-z0-9-]+)/?$", b)
                       or re.findall(r"/([a-z0-9-]+)/\"$", "")))
    # fallback: collect from absolute hits
    slugs = sorted(set(re.findall(r"https://gomel\.zoon\.ru/([a-z0-9-]+)/", b)))
    print("  slugs: " + ", ".join(slugs[:15]))

    # 2. first section -> org cards
    if slugs:
        sec = slugs[0]
        b2 = show("section " + sec, "https://gomel.zoon.ru/%s/" % sec,
                  r'href="(/%s/\d+[^"]*)"' % sec)
        m = re.search(r'href="(/%s/\d+[^"]*)"' % sec, b2)
        if m:
            org = "https://gomel.zoon.ru" + m.group(1)
            b3 = show("  org page", org,
                      r'href="(https?://(?!www\.zoon|gomel\.zoon)[^"]+\.[a-z]{2,}[^"]*)"')
            for hit in re.findall(r'href="(https?://(?!www\.zoon|gomel\.zoon)[^"]+)"', b3)[:6]:
                print("    site: " + hit[:100])

    # 3. onliner: correct search path
    show("onliner search cat", "https://catalog.onliner.by/search?query=%D0%BA%D0%B0%D1%84%D0%B5",
         r'"url":"(https?://catalog\.onliner\.by/[a-z-]+/[a-z0-9-]+)"')
    show("onliner sd section", "https://catalog.onliner.by/sd/abakus",
         r'"href":"?(https?://[\w.-]+\.(?:by|ru)[^",]*)"')

    # 4. 2gis Belarus
    show("2gis.by/minsk", "https://2gis.by/minsk", r'href="(/minsk/[^"]+)"')


if __name__ == "__main__":
    main()
