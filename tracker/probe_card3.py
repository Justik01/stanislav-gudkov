# probe_card3.py - find phone structure on 2GIS firm page
# Run: py -3 probe_card3.py
import re
import sys

sys.path.insert(0, r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker")
from probe_card import fetch  # noqa: E402

body = fetch("https://2gis.by/minsk/firm/70000001042582394")

print("tel links :", sorted(set(re.findall(r'href="tel:([^"]+)"', body)))[:6])
print("phone json:", sorted(set(re.findall(r'"phone"\s*:\s*"([^"]+)"', body)))[:6])
print("contacts  :", sorted(set(re.findall(r'"value"\s*:\s*"(\+375[^"]+)"', body)))[:6])
for m in list(re.finditer(r".{60}\+375293233388.{40}", body))[:2]:
    print("CTX:", m.group(0).replace("\n", " ")[:140])
