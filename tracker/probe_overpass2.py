# probe_overpass2.py - minimal GET query across overpass mirrors
# Run: py -3 probe_overpass2.py
import json
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
Q = '[out:json];nwr(52.40,30.95,52.48,31.05)["amenity"="cafe"];out tags 10;'

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def main():
    for host in MIRRORS:
        url = host + "?" + urllib.parse.urlencode({"data": Q})
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "application/json, */*"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                j = json.loads(r.read().decode("utf-8"))
            els = j.get("elements", [])
            with_site = sum(1 for e in els if (e.get("tags") or {}).get("website"))
            print("%-52s OK els=%d with_site=%d" % (host, len(els), with_site))
        except Exception as e:
            print("%-52s ERR %s" % (host, str(e)[:70]))


if __name__ == "__main__":
    main()
