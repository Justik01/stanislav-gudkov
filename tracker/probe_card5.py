# probe_card5.py - classify tel: links: own contacts vs ads block
# Run: py -3 probe_card5.py
import re
import sys

sys.path.insert(0, r"C:\Users\user\Documents\agent-memory\projects\client-search\tracker")
from probe_card import fetch  # noqa: E402

body = fetch("https://2gis.by/minsk/firm/70000001042582394")  # Trident

print("== all href=tel occurrences ==")
for m in re.finditer(r'href="tel:([^"]+)"', body):
    ctx = body[max(0, m.start() - 260):m.start()].replace("\n", " ")
    cls = re.findall(r'class="([^"]+)"[^>]*href="tel', ctx)
    print("  %-16s ...%s" % (m.group(1), ctx[-170:]))

print()
print("== structured contact values ==")
for m in re.finditer(r'"type"\s*:\s*"(phone|site|email)"\s*,\s*"value"\s*:\s*"([^"]+)"', body):
    ctx = body[max(0, m.start() - 220):m.start()].replace("\n", " ")
    print("  %-6s %-18s ...%s" % (m.group(1), m.group(2), ctx[-150:]))
