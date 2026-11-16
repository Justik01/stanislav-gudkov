# probe_cold4.py - dump link structures: zoon gomel root, 2gis by, onliner search
# Run: py -3 probe_cold4.py
import collections
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def pattern_stats(name, body, rx):
    hits = re.findall(rx, body)
    print("%s: %d hits" % (name, len(hits)))
    for h in hits[:10]:
        print("    " + str(h)[:110])
    return hits


def main():
    print("=== gomel.zoon.ru root ===")
    b = get("https://gomel.zoon.ru/")
    hrefs = re.findall(r'href="([^"]+)"', b)
    print("hrefs total=%d uniq=%d" % (len(hrefs), len(set(hrefs))))
    # bucket by shape
    shapes = collections.Counter()
    for h in set(hrefs):
        if re.match(r"^/[a-z-]+/\d+", h):
            shapes["org /slug/NNN"] += 1
        elif re.match(r"^/[a-z-]+/?$", h):
            shapes["section /slug/"] += 1
        elif h.startswith("http"):
            shapes["absolute"] += 1
        else:
            shapes["other"] += 1
    print(dict(shapes))
    for h in sorted(set(hrefs))[:25]:
        print("    " + h[:100])

    print("=== 2gis.by search page ===")
    b2 = get("https://2gis.by/minsk/search/%D0%BA%D0%B0%D1%84%D0%B5")
    print("size=%dK" % (len(b2) // 1024))
    for rx, label in [
        (r'"url"\s*:\s*"(https?://[^"]+)"', "json url fields"),
        (r'2gis\.by/[a-z]+/biz/\d+', "biz links"),
        (r'"site"\s*:\s*"[^"]+"', "site fields"),
        (r"rubricId/\d+", "rubric links"),
    ]:
        pattern_stats(label, b2, rx)

    print("=== onliner search raw ===")
    b3 = get("https://catalog.onliner.by/search?query=%D0%BA%D0%B0%D1%84%D0%B5")
    for rx, label in [
        (r'href="(//catalog\.onliner\.by/[^"]+)"', "proto-relative catalog links"),
        (r'"href"\s*:\s*"([^"]+)"', "json href"),
        (r'https?://[\w-]+\.(?:by|ru)\b', "any by/ru domains"),
    ]:
        pattern_stats(label, b3, rx)


if __name__ == "__main__":
    main()
