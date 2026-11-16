# cold_leads.py - collect companies WITHOUT a website via 2GIS Places API
# Run: py -3 cold_leads.py [max_per_combo]  -> tracker/leads.json
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime

from config import GIS_API_KEY, USER_AGENT

ITEMS_URL = "https://catalog.api.2gis.com/3.0/items"
OUT_FILE = r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker\leads.json"

# cities that answer on the demo key (BY = Minsk only, checked 2026-11-16)
CITIES = {
    "Минск": "27.5615,53.9023",
    "Москва": "37.6176,55.7558",
    "Санкт-Петербург": "30.3351,59.9343",
    "Екатеринбург": "60.6122,56.8389",
    "Новосибирск": "82.9346,55.0084",
    "Казань": "49.1064,55.7963",
    "Нижний Новгород": "44.0020,56.2965",
    "Самара": "50.1002,53.2001",
    "Краснодар": "38.9753,45.0355",
    "Воронеж": "39.1843,51.6720",
}

# niches where a missing website = lost clients (site is the pitch)
QUERIES = [
    "стоматология", "салон красоты", "автосервис", "юрист",
    "строительство", "мебель", "фитнес", "ветеринарная клиника",
    "оптика", "пекарня", "свадебный салон", "школа иностранного языка",
    "маникюр", "барбершоп", "магазин цветов", "ремонт квартир",
    "репетитор", "детский сад", "медицинский центр", "клининг",
]

PAGE_SIZE = 10   # API hard limit (20+ -> 400)
MAX_PAGES = 8    # 80 leads per city+query combo
DEMO_QUOTA = 900 # demo key = 1000 req/month, keep safety margin

_requests = {"n": 0}


def call(params):
    if _requests["n"] >= DEMO_QUOTA:
        raise RuntimeError("quota cap %d reached" % DEMO_QUOTA)
    _requests["n"] += 1
    url = ITEMS_URL + "?" + urllib.parse.urlencode(dict(params, key=GIS_API_KEY))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_combo(city, query, per_combo):
    """Leads (no website) for one city+query, paginated."""
    out = []
    for page in range(1, MAX_PAGES + 1):
        if len(out) >= per_combo:
            break
        try:
            j = call({
                "q": query, "location": CITIES[city], "has_site": "false",
                "page_size": str(PAGE_SIZE), "page": str(page),
            })
        except Exception as e:
            if "quota" in str(e):
                raise
            print("  ! %s/%s page %d: %s" % (city, query, page, str(e)[:80]))
            break
        if j.get("meta", {}).get("code") != 200:
            break
        items = (j.get("result") or {}).get("items") or []
        if not items:
            break
        for it in items:
            out.append({
                "id": it.get("id", ""),
                "name": it.get("name", ""),
                "address": it.get("address_name", ""),
                "comment": it.get("address_comment", ""),
                "city": city,
                "query": query,
                "has_site": False,
                "status": "new",     # new -> contacted -> replied -> deal / dead
                "found": datetime.now().strftime("%Y-%m-%d"),
            })
        time.sleep(0.3)
    return out[:per_combo]


def load_existing():
    try:
        with open(OUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def main():
    import sys
    per_combo = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    existing = load_existing()
    seen = {l["id"] for l in existing}
    fresh = []
    combos = len(CITIES) * len(QUERIES)
    done = 0
    for city in CITIES:
        for query in QUERIES:
            done += 1
            try:
                leads = fetch_combo(city, query, per_combo)
            except RuntimeError as e:
                print("stop: %s" % e)
                city = None
                break
            new = [l for l in leads if l["id"] not in seen]
            seen.update(l["id"] for l in new)
            fresh.extend(new)
        if city is None:
            break
        print("%-18s cumulative new=%d" % (city, len(fresh)))

    existing.extend(fresh)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=1)
    print("total leads: %d (new %d, combos %d, requests<=%d)"
          % (len(existing), len(fresh), combos, combos * MAX_PAGES))


if __name__ == "__main__":
    main()
