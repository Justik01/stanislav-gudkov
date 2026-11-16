# probe_cold7.py - discover real section links on gomel.zoon.ru root
# Run: py -3 probe_cold7.py
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
req = urllib.request.Request("https://gomel.zoon.ru/", headers={"User-Agent": UA})
body = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")

print("size=%dK" % (len(body) // 1024))
# all self-links
self_links = sorted(set(re.findall(r'href="([^"]*gomel\.zoon\.ru[^"]*)"', body)))
print("self absolute: %d" % len(self_links))
for h in self_links[:20]:
    print("    " + h[:120])
# all hrefs containing digits (org pages live /slug/NNN)
digits = sorted(set(re.findall(r'href="([^"]*\d{4,}[^"]*)"', body)))
print("with digits: %d" % len(digits))
for h in digits[:20]:
    print("    " + h[:120])
# context of '/restoran'
for m in list(re.finditer(r".{60}/restoran.{60}", body))[:3]:
    print("CTX " + m.group(0).replace("\n", " ")[:150])
