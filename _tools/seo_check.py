#!/usr/bin/env python3
"""
SEO safety check for the built site. Run it after the builders:
    python3 _tools/blog.py && python3 _tools/site_chrome.py && python3 _tools/seo_check.py

It reports (never fixes):
  - internal links and images that point at files that don't exist
  - internal links to /page.html when the page's canonical URL is extensionless
  - indexable pages without an absolute https://dyadgrow.com canonical
  - JSON-LD blocks that don't parse, and blog posts missing the fields Google needs
  - sitemap URLs that don't exist, are noindex, or whose canonical points somewhere else
  - on indexable pages: titles over 60 characters, meta descriptions outside 70 to 160 characters,
    a missing or repeated H1, titles or descriptions duplicated on another page, and <img> tags
    without width and height (index.html is skipped for images: its loader and hero are hand built)

It only prints warnings and exits 0, so it can never block a blog post or a deploy.
Pass --strict to exit 1 when something is found (handy when testing locally).
"""
import html.parser, json, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dyadgrow.com"
SKIP_DIRS = {".git", ".github", "_blog", "_tools", "node_modules", "_site"}
warnings = []
warn = lambda f, msg: warnings.append(f"{f}: {msg}")


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ld, self.canonical, self.robots, self._ld = [], [], None, "", None
        self.title, self.desc, self.h1, self.nodims, self._title = "", None, 0, 0, False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "link" and (a.get("rel") or "").lower() == "canonical": self.canonical = a.get("href")
        if tag == "meta" and (a.get("name") or "").lower() == "robots": self.robots = (a.get("content") or "").lower()
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = ""
        if tag == "title": self._title = True
        if tag == "meta" and (a.get("name") or "").lower() == "description": self.desc = a.get("content") or ""
        if tag == "h1": self.h1 += 1
        if tag == "img" and a.get("src") and not (a.get("width") and a.get("height")): self.nodims += 1
        for k in ("href", "src", "poster", "data-src", "data-src-m"):
            if a.get(k): self.refs.append(a[k])
        for k in ("srcset", "imagesrcset"):
            if a.get(k): self.refs += [c.strip().split(" ")[0] for c in a[k].split(",") if c.strip()]

    def handle_data(self, d):
        if self._ld is not None: self._ld += d
        if self._title: self.title += d

    def handle_endtag(self, tag):
        if tag == "script" and self._ld is not None: self.ld.append(self._ld); self._ld = None
        if tag == "title": self._title = False


def target(ref, page_dir):
    """Map an internal URL to a file path in the repo, or None for external/non-file links."""
    ref = ref.strip()
    if ref.startswith(SITE): ref = ref[len(SITE):] or "/"
    if re.match(r"^(https?:|mailto:|tel:|javascript:|data:|#|//|\{|\$)", ref) or "${" in ref: return None
    path = urllib.parse.unquote(urllib.parse.urlsplit(ref).path)
    if not path: return None
    full = os.path.normpath(os.path.join(ROOT, path.lstrip("/")) if path.startswith("/") else os.path.join(page_dir, path))
    return full


def exists(full):
    if os.path.isfile(full): return True
    if os.path.isdir(full) and os.path.isfile(os.path.join(full, "index.html")): return True
    return os.path.isfile(full + ".html")


def url_to_file(loc):
    p = loc[len(SITE):] or "/"
    f = os.path.join(ROOT, p.lstrip("/"))
    if p.endswith("/"): return os.path.join(f, "index.html")
    return f if f.endswith(".html") else f + ".html"


pages = {}
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
    for fn in files:
        if not fn.endswith(".html"): continue
        f = os.path.join(d, fn); rel = os.path.relpath(f, ROOT)
        src = open(f, encoding="utf-8", errors="replace").read()
        if "<html" not in src[:500].lower() and "<!doctype" not in src[:200].lower(): continue   # fragments
        pg = Page(); pg.feed(src); pages[rel] = pg
        indexable = "noindex" not in pg.robots
        if indexable and not (pg.canonical or "").startswith(SITE): warn(rel, f"indexable page without an absolute {SITE} canonical")
        for ref in set(pg.refs):
            full = target(ref, d)
            if full is None: continue
            if not exists(full): warn(rel, f"broken internal link or file: {ref}")
            elif ref.split("?")[0].split("#")[0].endswith(".html") and os.path.isfile(full) and full.startswith(ROOT):
                warn(rel, f"links to {ref}; use the extensionless URL")
        for i, block in enumerate(pg.ld, 1):
            try: data = json.loads(block)
            except ValueError as e: warn(rel, f"JSON-LD block {i} does not parse ({e})"); continue
            for node in (data.get("@graph", [data]) if isinstance(data, dict) else data):
                if isinstance(node, dict) and node.get("@type") == "BlogPosting":
                    missing = [k for k in ("headline", "image", "datePublished", "dateModified", "author") if not node.get(k)]
                    if missing: warn(rel, "BlogPosting missing " + ", ".join(missing))

seen_titles, seen_descs = {}, {}
for rel, pg in sorted(pages.items()):
    if "noindex" in pg.robots: continue
    t, dsc = pg.title.strip(), (pg.desc or "").strip()
    if not t: warn(rel, "missing <title>")
    elif len(t) > 60: warn(rel, f"title is {len(t)} characters (60 or fewer shows in full in search results)")
    if not dsc: warn(rel, "missing meta description")
    elif not 70 <= len(dsc) <= 160: warn(rel, f"meta description is {len(dsc)} characters (aim for 70 to 160)")
    if pg.h1 != 1: warn(rel, f"{pg.h1} H1 headings (use exactly one)")
    if t and t in seen_titles: warn(rel, f"same title as {seen_titles[t]}")
    if dsc and dsc in seen_descs: warn(rel, f"same meta description as {seen_descs[dsc]}")
    seen_titles.setdefault(t, rel); seen_descs.setdefault(dsc, rel)
    if pg.nodims and rel != "index.html": warn(rel, f"{pg.nodims} image(s) without width and height (causes layout shift)")

sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
    f = url_to_file(loc); rel = os.path.relpath(f, ROOT)
    if not os.path.isfile(f): warn("sitemap.xml", f"{loc} has no page ({rel})"); continue
    pg = pages.get(rel)
    if pg and "noindex" in pg.robots: warn("sitemap.xml", f"{loc} is noindex")
    if pg and pg.canonical and pg.canonical.rstrip("/") != loc.rstrip("/"): warn("sitemap.xml", f"{loc} canonical is {pg.canonical}")

print(f"SEO check: {len(pages)} pages, {len(warnings)} warning(s)")
for w in warnings: print(("::warning::" if os.environ.get("GITHUB_ACTIONS") else "  ") + w)
sys.exit(1 if warnings and "--strict" in sys.argv else 0)
