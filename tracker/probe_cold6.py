# probe_cold6.py - zoon listing + org card: can we extract company site/phone?
# Run: py -3 probe_cold6.py
import json
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    # 1. listing
    b = get("https://gomel.zoon.ru/restoran/")
    print("listing size=%dK" % (len(b) // 1024))
    org_links = sorted(set(re.findall(r'href="(/restoran/[^"]*\d{4,}[^"]*)"', b)))
    print("org links: %d %s" % (len(org_links), org_links[:5]))
    # also generic: /slug/NNNNN
    generic = sorted(set(re.findall(r'href="(/[a-z-]+/\d{5,}/?)"', b)))
    print("generic /slug/NNNNN: %d %s" % (len(generic), generic[:5]))

    # 2. where does "website" appear?
    for m in re.finditer(r".{80}\"website\".{120}", b):
        print("CTX: " + m.group(0).replace("\n", " ")[:240])
        break

    # 3. pick an org page
    cand = org_links[0] if org_links else (generic[0] if generic else "")
    if not cand:
        # maybe listing is SPA too - check for json blob with item data
        print("no direct org links - SPA? searching item json...")
        for rx in [r'"url"\s*:\s*"(/[^"]+\d+)"', r'"href"\s*:\s*"(/[^"]+\d+)"']:
            f = sorted(set(re.findall(rx, b)))[:5]
            print("  %s -> %s" % (rx[:20], f))
        return

    org = "https://gomel.zoon.ru" + cand
    print("ORG: " + org)
    o = get(org)
    print("org size=%dK" % (len(o) // 1024))
    ext = sorted(set(re.findall(r'href="(https?://(?!zoon|www\.zoon|gomel\.zoon)[^"]+)"', o)))
    print("ext links: %d" % len(ext))
    for e in ext[:8]:
        print("    " + e[:110])
    # phones
    phones = sorted(set(re.findall(r"\+375[\d\s()-]{7,}", o)))
    print("phones: %s" % phones[:4])
    # "website" block context
    for m in re.finditer(r".{100}website.{160}", o):
        print("CTX: " + m.group(0).replace("\n", " ")[:280])
        break


if __name__ == "__main__":
    main()
