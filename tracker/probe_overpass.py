# probe_overpass.py - OSM Overpass: orgs without website tag (no key needed)
# Run: py -3 probe_overpass.py
import json
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

QUERY = """
[out:json][timeout:30];
area["name"="Гомель"]["boundary"="administrative"]->.a;
(
  nwr(area.a)["amenity"="cafe"];
  nwr(area.a)["shop"];
);
out tags 60;
"""


def run(host):
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    req = urllib.request.Request(host, data=data, headers={
        "User-Agent": UA,
        "Accept": "application/json, */*",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    for host in ("https://overpass-api.de/api/interpreter",
                 "https://overpass.kumi.systems/api/interpreter"):
        try:
            j = run(host)
            els = j.get("elements", [])
            with_site = sum(1 for e in els if (e.get("tags") or {}).get("website"))
            with_phone = sum(1 for e in els if (e.get("tags") or {}).get("phone"))
            print("%-46s OK elements=%d with_website=%d with_phone=%d"
                  % (host, len(els), with_site, with_phone))
            # sample of no-website orgs
            sample = [e for e in els
                      if (e.get("tags") or {}).get("name") and not (e.get("tags") or {}).get("website")][:5]
            for e in sample:
                t = e["tags"]
                print("    - %s (%s) phone=%s" % (
                    t.get("name", "?")[:45], t.get("shop") or t.get("amenity"), t.get("phone", "-")))
            break
        except Exception as e:
            print("%-46s ERR %s" % (host, str(e)[:90]))


if __name__ == "__main__":
    main()
