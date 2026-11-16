# probe_gis2.py - try param combos against 2GIS items API
# Run: py -3 probe_gis2.py
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


CASES = [
    ("q only", {"q": "кафе"}),
    ("q+loc", {"q": "кафе", "location": "30.9754,52.4345"}),
    ("q+loc+radius", {"q": "кафе", "location": "30.9754,52.4345", "radius": "5000"}),
    ("rubric+sort_point", {"rubric_id": "161", "sort_point": "30.9754,52.4345"}),
    ("q+loc msk", {"q": "кафе", "location": "37.6176,55.7558"}),
    ("q+loc has_site msk", {"q": "кафе", "location": "37.6176,55.7558", "has_site": "false"}),
]


def main():
    for name, params in CASES:
        try:
            j = call(params)
            code = j.get("meta", {}).get("code")
            res = j.get("result", {})
            total = res.get("total")
            items = res.get("items", [])
            print("%-22s code=%s total=%s got=%d" % (name, code, total, len(items)))
            if items:
                print("    keys: " + ", ".join(sorted(items[0].keys())))
                print("    sample: " + json.dumps(items[0], ensure_ascii=False)[:300])
        except urllib.error.HTTPError as e:
            print("%-22s HTTP %d %s" % (name, e.code, e.read().decode(errors="replace")[:150]))
        except Exception as e:
            print("%-22s ERR %s" % (name, str(e)[:120]))


if __name__ == "__main__":
    main()
