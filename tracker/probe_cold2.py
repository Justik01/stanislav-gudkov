# probe_cold2.py - deeper probe: zoon listing pages + onliner catalog + blizko
# Run: py -3 probe_cold2.py
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 20


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def probe(name, url, checks):
    try:
        status, body = get(url)
        out = ["status=%d", "size=%dK" % (len(body) // 1024)]
        for label, rx in checks:
            out.append("%s=%d" % (label, len(re.findall(rx, body))))
        print("%-30s %s" % (name, " ".join(out)))
        return body
    except Exception as e:
        print("%-30s ERR %s" % (name, str(e)[:90]))
        return ""


def main():
    print("--- zoon listing (gomel, restaurants) ---")
    b = probe(
        "gomel.zoon.ru/eda",
        "https://gomel.zoon.ru/eda/",
        [("org_cards", r'href="/eda/\d+'), ("site_btn", r"Перейти на сайт|site_btn|data-site")],
    )
    # find first org card link for detail probe
    m = re.search(r'href="(/eda/\d+[^"]*)"', b)
    if m:
        org_url = "https://gomel.zoon.ru" + m.group(1)
        print("  sample org: " + org_url)
        b2 = probe(
            "  zoon org page",
            org_url,
            [("ext_site", r"https?://(?!www\.zoon|gomel\.zoon)[\w-]+\.[a-z]{2,}"),
             ("phones", r"\+375|\+7 \("), ("site_label", r"Сайт")],
        )
        # where does the external site link live?
        for hit in re.findall(r'href="(https?://(?!www\.zoon|gomel\.zoon)[^"]+)"', b2)[:5]:
            print("    link: " + hit[:100])

    print("--- onliner catalog (BY) ---")
    b = probe(
        "catalog.onliner.by",
        "https://catalog.onliner.by/sd",
        [("companies", r"/sd/[a-z0-9-]+$|/sd/[a-z0-9-]+\""), ("site_links", r"https?://[\w-]+\.(by|ru)(?![/.\w])")],
    )
    b = probe(
        "  onliner search",
        "https://catalog.onliner.by/search?query=%D0%BA%D0%B0%D1%84%D0%B5",
        [("cards", r"catalog/product-card|/sd/[a-z0-9-]+")],
    )

    print("--- other catalogs ---")
    probe("blizko.ru", "https://www.blizko.ru/", [("orgs", r'href="/[^"]+/\d+'), ("ext", r"https?://[\w-]+\.[a-z]{2,}")])
    probe("2gis.com BY (minske)", "https://minsk.2gis.com/", [("size", r"x")])  # size only


if __name__ == "__main__":
    main()
