#!/usr/bin/env python3
"""
Refreshes Facebook's link previews for blog posts, right after a deploy.

Usage (the deploy workflow does this):
    python3 _tools/social_refresh.py OLD_SITEMAP.xml    # re-scrapes blog posts that are new or have a new <lastmod>
    REFRESH_ALL=1 python3 _tools/social_refresh.py      # re-scrapes every blog post
Running the deploy workflow by hand (Actions tab, Run workflow) sets REFRESH_ALL. Do that after changing
a post's main image, because an image swap doesn't change <lastmod>.

Setup (one time): the FB_ACCESS_TOKEN Actions secret holds a Facebook app access token. Create an app at
developers.facebook.com, then use the app's ID and secret as APP_ID|APP_SECRET, or copy its token from the
Access Token Tool. Until the secret exists this script just says so. Failures never fail a deploy.

LinkedIn has no public API for this. Its previews are refreshed by hand at linkedin.com/post-inspector.
"""
import json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = "https://graph.facebook.com/"
token = os.environ.get("FB_ACCESS_TOKEN", "").strip()
if not token:
    print("Facebook refresh: FB_ACCESS_TOKEN isn't set, skipping"); sys.exit(0)

def entries(xml):
    return dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]*)</lastmod>", xml))

new = entries(open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
posts = {u: lm for u, lm in new.items() if re.fullmatch(r"https://dyadgrow\.com/blog/(?!page/|topic/)[a-z0-9-]+", u)}
if os.environ.get("REFRESH_ALL"):
    urls = list(posts)
else:
    try: old = entries(open(sys.argv[1], encoding="utf-8").read())
    except (IndexError, OSError): old = {}
    urls = [u for u, lm in posts.items() if old.get(u) != lm] if old else []
if not urls:
    print("Facebook refresh: no new or updated posts"); sys.exit(0)
failed = 0
for u in urls:
    body = urllib.parse.urlencode({"id": u, "scrape": "true", "access_token": token}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(GRAPH, data=body), timeout=30) as r:
            d = json.load(r)
        print(f"  ok {u} ({d.get('image', [{}])[0].get('url', 'no image') if d.get('image') else 'no image'})")
    except Exception as e:   # the message from urllib never includes the token, only the status
        failed += 1; print(f"  failed {u}: {e}")
print(f"Facebook refresh: {len(urls) - failed} of {len(urls)} post(s) refreshed")
