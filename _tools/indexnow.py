#!/usr/bin/env python3
"""
IndexNow: tells Bing (and Copilot, Yandex, Seznam, Naver) which pages changed, right after a deploy.

Usage (the deploy workflow does this):
    python3 _tools/indexnow.py OLD_SITEMAP.xml        # compares with the freshly built sitemap.xml
It submits every URL that is new or whose <lastmod> changed. Nothing changed means nothing is sent.
The key file /4e5ef9bac0f06f4a6a1645f34ab17671.txt in the site root proves we own the domain. Failures never fail a deploy.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "dyadgrow.com"
KEY = "4e5ef9bac0f06f4a6a1645f34ab17671"

def entries(xml):
    return dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]*)</lastmod>", xml))

new = entries(open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
try: old = entries(open(sys.argv[1], encoding="utf-8").read())
except (IndexError, OSError): old = {}
if not old:
    print("IndexNow: no previous sitemap to compare with, nothing sent"); sys.exit(0)
changed = [u for u, lm in new.items() if old.get(u) != lm][:100]
if not changed:
    print("IndexNow: no new or updated pages"); sys.exit(0)
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": changed}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r: print(f"IndexNow: HTTP {r.status} for {len(changed)} URL(s)")
except Exception as e:
    print(f"IndexNow: request failed ({e})")
print("\n".join("  " + u for u in changed))
