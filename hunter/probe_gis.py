# probe_gis.py - test 2GIS demo key: items search with/without has_site
# Run: py -3 probe_gis.py
import json
import urllib.parse
import urllib.request

from config import GIS_API_KEY

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def call(params):
    url = "https://catalog.api.2gis.com/3.0/items?" + urllib.parse.urlencode(
        dict(params, key=GIS_API_KEY)
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    base = {"q": "кафе", "location": "30.9754,52.4345", "page_size": "5"}
    for hs in ("false", "true"):
        try:
            j = call(dict(base, has_site=hs))
            print("RAW: " + json.dumps(j, ensure_ascii=False)[:400])
            code = j.get("meta", {}).get("code")
            res = j.get("result", {})
            items = res.get("items", [])
            print("has_site=%s -> code=%s total=%s got=%d" % (
                hs, code, res.get("total"), len(items)))
            for it in items[:3]:
                print("    %s | %s | site=%s phone=%s" % (
                    str(it.get("name"))[:40],
                    str(it.get("address_name"))[:45],
                    it.get("website") or it.get("site") or "-",
                    str(it.get("phone") or "-")[:25],
                ))
            if items and hs == "false":
                print("    keys: " + ", ".join(sorted(items[0].keys())))
        except urllib.error.HTTPError as e:
            print("has_site=%s -> HTTP %d %s" % (hs, e.code, e.read().decode(errors="replace")[:200]))
        except Exception as e:
            print("has_site=%s -> ERR %s" % (hs, str(e)[:120]))


if __name__ == "__main__":
    main()
