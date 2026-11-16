# enrich_leads.py - add phone (+site if any) to leads from public 2GIS firm pages
# Run: py -3 enrich_leads.py [city] [limit]   e.g.  py -3 enrich_leads.py Минск 20
import json
import re
import sys
import time
import urllib.request

from config import USER_AGENT

LEADS_FILE = r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker\leads.json"

# city -> (base url). RU cities live on 2gis.ru, Minsk on 2gis.by
BASE = {
    "Минск": "https://2gis.by/minsk",
    "Москва": "https://2gis.ru/moscow",
    "Санкт-Петербург": "https://2gis.ru/spb",
    "Екатеринбург": "https://2gis.ru/ekaterinburg",
    "Новосибирск": "https://2gis.ru/novosibirsk",
    "Казань": "https://2gis.ru/kazan",
    "Нижний Новгород": "https://2gis.ru/nizhny-novgorod",
    "Самара": "https://2gis.ru/samara",
    "Краснодар": "https://2gis.ru/krasnodar",
    "Воронеж": "https://2gis.ru/voronezh",
}

TEL_RE = re.compile(r'href="tel:([^"]+)"')
SITE_RE = re.compile(r'"type"\s*:\s*"site"\s*,\s*"value"\s*:\s*"([^"]+)"')
EMAIL_RE = re.compile(r'"type"\s*:\s*"email"\s*,\s*"value"\s*:\s*"([^"]+)"')
GROUPS_RE = re.compile(r'"contact_groups"\s*:\s*\[')


def own_contacts(body):
    """First contact_groups array on the page = the firm's own contacts.
    Other phones on the page belong to ad banners (verified 2026-11-16)."""
    dec = json.JSONDecoder()
    for m in GROUPS_RE.finditer(body):
        start = body.index("[", m.start())
        try:
            groups, _ = dec.raw_decode(body[start:])
        except Exception:
            continue
        if not isinstance(groups, list) or not groups:
            continue
        phones, sites, emails = [], [], []
        for g in groups:
            for c in (g or {}).get("contacts", []):
                t, v = c.get("type"), c.get("value") or ""
                if t == "phone" and v:
                    phones.append(v)
                elif t == "site" and v:
                    sites.append(v)
                elif t == "email" and v:
                    emails.append(v)
        if phones or sites or emails:
            return phones, sites, emails
    return [], [], []


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def enrich_one(lead):
    base = BASE.get(lead["city"])
    if not base:
        return None
    url = "%s/firm/%s" % (base, lead["id"])
    try:
        body = fetch(url)
    except Exception as e:
        return {"error": str(e)[:60]}
    phones, sites, emails = own_contacts(body)
    return {"phone": phones[0] if phones else "", "phones": phones[:4],
            "site": sites[0] if sites else "", "email": emails[0] if emails else "",
            "card": url}


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    city = args[0] if args else "Минск"
    limit = int(args[1]) if len(args) > 1 else 20
    leads = json.load(open(LEADS_FILE, encoding="utf-8"))
    todo = [l for l in leads
            if l["city"] == city and (force or not l.get("phone"))][:limit]
    print("to enrich: %d" % len(todo))
    ok = 0
    for i, lead in enumerate(todo, 1):
        res = enrich_one(lead)
        if res is None:
            print("%2d. %s -> no base url" % (i, lead["name"][:40]))
            continue
        if "error" in res:
            print("%2d. %s -> ERR %s" % (i, lead["name"][:40], res["error"]))
            continue
        lead.update({k: v for k, v in res.items()})
        lead["enriched"] = "2026-11-16"
        ok += 1
        print("%2d. %-42s phone=%-16s site=%s" % (
            i, lead["name"][:42], res["phone"] or "-", res["site"] or "-"))
        time.sleep(0.5)
    json.dump(leads, open(LEADS_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with_phone = sum(1 for l in leads if l.get("phone"))
    print("enriched %d; total with phone: %d / %d" % (ok, with_phone, len(leads)))


if __name__ == "__main__":
    main()
