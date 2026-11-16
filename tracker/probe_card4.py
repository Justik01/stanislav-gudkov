# probe_card4.py - verify phone belongs to the firm, not a "related" card
# Run: py -3 probe_card4.py
import re
import sys

sys.path.insert(0, r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker")
from probe_card import fetch  # noqa: E402

CASES = [
    ("Моя стоматология", "https://2gis.by/minsk/firm/70000001042386292", "+375293233388"),
    ("Тридент", "https://2gis.by/minsk/firm/70000001042582394", "+375293233388"),
    ("Combiauto", "https://2gis.by/minsk/firm/70000001118444243", "+375291070911"),
]

for name, url, phone in CASES:
    body = fetch(url)
    # is there a separate block for the current firm? find firm name position vs phone position
    pos_phone = body.find(phone)
    # look backwards for the nearest "name" of the current firm
    pos_firm = body.find(name)
    # count how many firms' names appear inside the contacts section
    ctx = body[max(0, pos_phone - 400): pos_phone + 100].replace("\n", " ")
    print("== %s phone@%d firmname@%d" % (name, pos_phone, pos_firm))
    print("   ctx: ..." + ctx[-320:])
    # other firms mentioned near phone?
    others = re.findall(r'"name"\s*:\s*"([^"]{3,50})"', ctx)
    print("   names in ctx:", others[:5])
