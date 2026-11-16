# probe_cold5.py - find JSON APIs: onliner, zoon embedded data, 2gis public key
# Run: py -3 probe_cold5.py
import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def get(url, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def hit(name, url, headers=None):
    try:
        body = get(url, headers)
        head = body[:160].replace("\n", " ")
        print("%-34s OK len=%d :: %s" % (name, len(body), head))
        return body
    except urllib.error.HTTPError as e:
        print("%-34s HTTP %d %s" % (name, e.code, e.read().decode(errors="replace")[:80].replace("\n", " ")))
    except Exception as e:
        print("%-34s ERR %s" % (name, str(e)[:80]))
    return ""


def main():
    # 1. onliner public catalog API
    q = urllib.parse.quote("кафе")
    b = hit("onliner api shops", "https://catalog.api.onliner.by/search/shops?query=" + q)
    if b:
        try:
            j = json.loads(b)
            arr = j if isinstance(j, list) else j.get("results") or j.get("shop") or []
            print("   -> items: %d" % len(arr))
            if arr:
                first = arr[0]
                print("   -> keys: " + ", ".join(list(first.keys())[:20]))
                cat = first.get("catalog") or first
                print("   -> name=%s url=%s" % (str(cat.get("name"))[:40], cat.get("url")))
        except Exception as e:
            print("   -> parse: " + str(e)[:60])

    # 2. zoon: search for embedded data / api hosts
    zb = hit("gomel.zoon.ru", "https://gomel.zoon.ru/")
    for label, rx in [
        ("api hosts", r'https?://[\w-]*api[\w.-]*\.(?:zoon|zoon)[\w.]*[^"\']*'),
        ("website key", r'"website"|"site_url"|"site"\s*:'),
        ("state json", r"__NEXT_DATA__|window\.__|initialState"),
        ("catalog links", r'/catalog/|/restoran'),
    ]:
        f = re.findall(rx, zb)
        print("   %-14s %d %s" % (label, len(f), f[:3]))

    # 3. 2gis: embedded key / api base
    gb = hit("2gis.by search", "https://2gis.by/minsk/search/%D0%BA%D0%B0%D1%84%D0%B5")
    for label, rx in [
        ("api refs", r'"(?:apiUrl|api_url|baseUrl)"\s*:\s*"([^"]+)"'),
        ("keys", r'[?&]key=([A-Za-z0-9]{10,})'),
        ("publicToken", r'"public_token"\s*:\s*"([^"]+)"|publicToken["\s:=]+([A-Za-z0-9._-]{20,})'),
        ("catalog.api", r"catalog\.api\.2gis[^\"]*"),
    ]:
        f = re.findall(rx, gb)
        print("   %-14s %d %s" % (label, len(f), str(f[:3])[:150]))

    # 4. onliner alternative: search shops page contains firm links?
    sp = hit("onliner sd search html", "https://catalog.onliner.by/sd/" + q)
    if sp:
        links = re.findall(r'href="(//catalog\.onliner\.by/[^"]+)"', sp)
        print("   -> catalog links: %d %s" % (len(links), links[:5]))


if __name__ == "__main__":
    main()
