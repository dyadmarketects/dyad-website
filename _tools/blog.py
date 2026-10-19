#!/usr/bin/env python3
"""
DYAD Marketects blog builder.

Source posts live in _blog/posts/<date>-<slug>.post. The deploy workflow never publishes
_blog/ or _tools/. Each source file starts with a JSON metadata block inside an HTML comment,
followed by the article body as plain HTML (no <h1>; the page title is the only H1):

    <!--
    {
      "title": "Visible headline",
      "seo_title": "Title tag, 60 characters or fewer",
      "description": "Meta description, 140 to 160 characters",
      "slug": "url-slug",
      "date": "2026-10-16",
      "updated": "2026-10-16",
      "service": "branding-logo-design | web-design | video-photo-production | social-media-marketing",
      "tags": ["Branding", "Albuquerque"],
      "image": "images/gorman-website-card.webp",
      "image_alt": "Describe the image",
      "summary": ["Key takeaway 1", "Key takeaway 2", "Key takeaway 3"],
      "faq": [["Question?", "Answer in plain text (no HTML)."]]
    }
    -->
    <p>Article body...</p>

Before/after slider: put this on its own line in the body (images must exist in the repo, same size and framing):
    [[compare before="images/x-before.webp" after="images/x-after.webp" alt="What the images show" caption="Optional caption" before_label="Before" after_label="After"]]
Readers drag (or tap) across the image to compare.

Run:  python3 _tools/blog.py
It writes blog/<slug>.html, blog/index.html, feed.xml, refreshes the blog
entries in sitemap.xml, and refreshes the "From the blog" block on each service page.
"""
import html, json, os, re, sys, datetime
from zoneinfo import ZoneInfo
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dyadgrow.com"
P = lambda *a: os.path.join(ROOT, *a)
esc = lambda s: html.escape(s, quote=True)
TZ = ZoneInfo("America/Denver")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from journey import J as JOURNEY, UPDATED as JOURNEY_UPDATED   # Vince's timeline: homepage cards + in-depth /about timeline
iso = lambda d: datetime.datetime.fromisoformat(d + "T08:00:00").replace(tzinfo=TZ).isoformat()   # 8am Mountain, DST-aware
PER_PAGE = 24          # posts per blog index page (/blog/, /blog/page/2, ...)
# Shown under every post. Google asks sites to be open about how content is made; set to "" to hide.
AI_NOTE = "Drafted with AI assistance from DYAD project notes, then reviewed, edited and fact-checked by Vincent King."

SERVICES = {
    "branding-logo-design":   dict(name="Branding & Logo Design",            bg="var(--pink)",     fg="#fff",        accent="var(--lime)", icon="icon-cap-1.webp"),
    "web-design":             dict(name="Web Design & Development",          bg="var(--lavender)", fg="var(--ink)",  accent="var(--pink)", icon="icon-cap-2.webp"),
    "video-photo-production": dict(name="Video & Photo Production",          bg="var(--magenta)",  fg="#fff",        accent="var(--lime)", icon="icon-cap-3.webp"),
    "social-media-marketing": dict(name="Social Media & Content Marketing",  bg="var(--lime)",     fg="var(--ink)",  accent="var(--pink)", icon="icon-cap-4.webp"),
}
ORG = {"@type": "ProfessionalService", "@id": SITE + "/#org", "name": "DYAD Marketects", "alternateName": ["DYAD", "DYAD Marketing", "DYAD Grow", "dyadgrow"],
       "url": SITE + "/", "logo": SITE + "/assets/img/logo-header.webp",
       "address": {"@type": "PostalAddress", "addressLocality": "Albuquerque", "addressRegion": "NM", "addressCountry": "US"},
       "sameAs": ["https://www.facebook.com/dyadmarketects", "https://www.instagram.com/dyadmarketects/",
                  "https://www.linkedin.com/company/dyad-marketects", "https://maps.google.com/?cid=12864398712172302748"]}
AUTHOR = {"@type": "Person", "@id": SITE + "/#vincent-king", "name": "Vincent King", "jobTitle": "Founder & CEO, DYAD Marketects",
          "url": SITE + "/about", "image": SITE + "/assets/img/about-portrait.webp", "sameAs": ["https://www.linkedin.com/in/vincent-inkosi-king/"]}

# ---------- shared chrome, taken from the live service page so the blog always matches the site ----------
def chrome():
    s = open(P("web-design.html"), encoding="utf-8").read()
    gtag = s[s.index("<!-- Google tag"):s.index("<style>")]
    style = s[s.index("<style>") + 7:s.index("</style>")]
    style = re.sub(r"/\*blog-cards\*/.*?/\*/blog-cards\*/", "", style, flags=re.S)
    hdr = s[s.index('<header class="top">'):s.index("</nav>\n</div>", s.index('<div class="mm"')) + len("</nav>\n</div>")]
    hdr = hdr.replace('class="nl cur"', 'class="nl"').replace(' aria-current="page"', "")
    foot = s[s.index("<footer"):s.index("</footer>") + 9].replace(' aria-current="page"', "")   # replaced by the shared footer in _tools/site_chrome.py
    js_start = s.index("<script>", s.index("</footer>"))
    js = s[js_start:s.index("</script>", js_start) + 9]
    return gtag, style, hdr, foot, js

BLOG_CSS = """
  .post-hero{ background:var(--hbg); color:var(--hfg); padding:clamp(48px,8vw,96px) 6vw clamp(44px,6vw,72px); }
  .post-hero .in{ max-width:860px; margin:0 auto; }
  .post-hero h1{ font-size:clamp(28px,4.4vw,50px); }
  .post-hero h1 .script{ color:var(--hacc); }
  .meta{ font-family:'JetBrains Mono', ui-monospace, monospace; font-size:12px; letter-spacing:.06em; text-transform:uppercase; margin-top:20px; display:flex; flex-wrap:wrap; gap:6px 14px; opacity:.9; }
  .meta a{ text-decoration:underline; text-underline-offset:3px; }
  article.post{ max-width:760px; margin:0 auto; padding:clamp(40px,6vw,72px) 6vw 20px; box-sizing:content-box; }
  article.post figure.lead-img{ margin:0 0 30px; } article.post figure.lead-img img{ width:100%; height:auto; border-radius:16px; }
  article.post figure figcaption{ font-size:13.5px; color:#666; margin-top:8px; }
  .tldr{ background:#fff; border-left:4px solid var(--pink); border-radius:12px; padding:20px 24px; margin:0 0 34px; box-shadow:0 10px 26px rgba(0,0,0,.05); }
  .tldr strong{ font-family:'Arian LT Heavy', sans-serif; text-transform:uppercase; font-size:13px; letter-spacing:.04em; display:block; margin-bottom:8px; }
  .tldr ul{ margin:0; padding-left:20px; } .tldr li{ font-size:15.5px; margin:4px 0; }
  .body h2{ font-size:clamp(21px,2.6vw,28px); margin:42px 0 14px; }
  .body h3{ font-size:17px; margin:28px 0 8px; }
  .body p, .body li{ font-size:17px; line-height:1.75; } .body p + p{ margin-top:16px; }
  .body ul, .body ol{ padding-left:22px; margin:14px 0 18px; } .body li{ margin:6px 0; }
  .body a{ color:var(--pink-text, #c40c43); text-decoration:underline; text-underline-offset:3px; font-weight:600; }
  .body blockquote{ margin:26px 0; padding:18px 22px; background:#fff; border-radius:12px; border-left:4px solid var(--lavender); }
  .body blockquote p{ font-size:16.5px; } .body blockquote cite{ display:block; margin-top:8px; font-style:normal; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:12px; text-transform:uppercase; color:var(--pink); }
  .body img{ width:100%; height:auto; border-radius:14px; margin:20px 0; }
  .body .ba{ margin:28px 0; }
  .ba-frame{ position:relative; border-radius:16px; overflow:hidden; background:#fff; box-shadow:0 16px 40px rgba(0,0,0,.1); user-select:none; touch-action:pan-y; }
  .body .ba-frame img{ display:block; width:100%; height:auto; margin:0; border-radius:0; }
  .ba-before{ position:absolute; inset:0; clip-path:inset(0 calc(100% - var(--pos)) 0 0); }
  .ba-line{ position:absolute; top:0; bottom:0; left:var(--pos); width:3px; margin-left:-1.5px; background:var(--pink); pointer-events:none; }
  .ba-knob{ position:absolute; top:50%; left:50%; width:44px; height:44px; margin:-22px 0 0 -22px; border-radius:50%; background:var(--pink); box-shadow:0 6px 18px rgba(245,17,83,.45); }
  .ba-knob::before, .ba-knob::after{ content:""; position:absolute; top:15px; border-style:solid; border-width:7px; border-color:transparent; }
  .ba-knob::before{ left:4px; border-right-color:#fff; } .ba-knob::after{ right:4px; border-left-color:#fff; }
  .ba-tag{ position:absolute; top:14px; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; padding:6px 10px; border-radius:20px; background:rgba(10,10,10,.75); color:#fff; pointer-events:none; }
  .ba-l{ left:14px; } .ba-r{ right:14px; background:var(--pink); }
  .ba-range{ position:absolute; inset:0; width:100%; height:100%; margin:0; opacity:0; cursor:ew-resize; -webkit-appearance:none; appearance:none; }
  .ba-range::-webkit-slider-thumb{ -webkit-appearance:none; width:60px; height:100vh; } .ba-range::-moz-range-thumb{ width:60px; height:1000px; border:0; }
  .ba-frame:has(.ba-range:focus-visible) .ba-knob{ outline:3px solid var(--ink); outline-offset:3px; }
  .ba figcaption{ font-size:14px; color:#555; margin-top:10px; text-align:center; }
  .body .note{ background:#fff7d6; border-radius:10px; padding:12px 16px; font-size:15px; }
  .svc-cta{ display:flex; align-items:center; gap:18px; margin:44px 0 10px; padding:22px; border-radius:16px; background:var(--hbg); color:var(--hfg); text-decoration:none; transition:transform .35s cubic-bezier(.22,1,.36,1), box-shadow .35s ease; }
  .svc-cta:hover{ transform:translateY(-3px); box-shadow:0 16px 34px rgba(0,0,0,.14); }
  .svc-cta img{ width:56px; height:56px; object-fit:contain; flex:none; }
  .svc-cta small{ display:block; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; opacity:.85; }
  .svc-cta b{ font-family:'Arian LT Heavy', sans-serif; text-transform:uppercase; font-size:17px; }
  .byline{ display:flex; gap:14px; align-items:center; margin:30px 0 0; padding-top:24px; border-top:1px solid rgba(0,0,0,.1); font-size:15px; }
  .byline .ainote{ display:block; margin-top:8px; font-size:12.5px; color:#5c5a55; }
  .pager{ display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-top:34px; }
  .pager a, .pager span{ font-family:'Arian LT Demi', sans-serif; font-size:13px; text-transform:uppercase; padding:10px 16px; border-radius:30px; border:1.5px solid var(--ink); text-decoration:none; }
  .pager span[aria-current]{ background:var(--ink); color:#fff; }
  .tlist{ list-style:none; padding:0; margin:0; display:grid; gap:14px; }
  .tlist li{ background:#fff; border-radius:14px; padding:18px 20px; box-shadow:0 8px 20px rgba(0,0,0,.04); }
  .tlist .yr{ font-family:'Arian LT Heavy', sans-serif; color:var(--pink); font-size:22px; }
  .tlist h3{ font-size:15px; margin:4px 0 6px; } .tlist p{ font-size:15.5px; }
  .byline img{ width:56px; height:56px; border-radius:50%; object-fit:cover; background:#ddd; }
  .posts{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }
  .pcard{ background:#fff; border-radius:16px; overflow:hidden; text-decoration:none; color:var(--ink); display:flex; flex-direction:column; box-shadow:0 10px 26px rgba(0,0,0,.06); transition:transform .4s cubic-bezier(.22,1,.36,1), box-shadow .4s ease; }
  .pcard:hover{ transform:translateY(-4px); box-shadow:0 20px 40px rgba(245,17,83,.18); }
  .pcard img{ width:100%; height:auto; aspect-ratio:16/10; object-fit:cover; }
  .pcard .b{ padding:18px 20px 22px; display:flex; flex-direction:column; gap:8px; flex:1; }
  .pcard .tag{ align-self:flex-start; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; border-radius:20px; padding:3px 10px; }
  .pcard h3{ font-size:16px; margin:0; } .pcard p{ font-size:15px; color:#444; }
  .pcard time{ margin-top:auto; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:11.5px; color:#5f5f5f; text-transform:uppercase; }
  .t-branding-logo-design{ background:var(--pink-bg, #e6104e); color:#fff; } .t-web-design{ background:var(--lavender); color:var(--ink); }
  .t-video-photo-production{ background:var(--magenta); color:#fff; } .t-social-media-marketing{ background:var(--lime); color:var(--ink); }
"""

def page(title, desc, canonical, ogimg, ldblocks, body, hero_vars, og_type="website", extra_head="", extra_css="", robots="index, follow, max-image-preview:large, max-snippet:-1"):
    gtag, style, hdr, foot, js = chrome()
    ld = "".join('<script type="application/ld+json">\n' + json.dumps(b, ensure_ascii=False) + "\n</script>\n" for b in ldblocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="author" content="Vincent King">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="DYAD Marketects Blog" href="{SITE}/feed.xml">
<link rel="preload" href="/assets/fonts/arian-lt-heavy.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/mont-light.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="DYAD Marketects">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{ogimg}">
{extra_head}{gtag}<style>{style}{BLOG_CSS}
  :root{{ {hero_vars} }}
{extra_css}</style>
{ld}</head>
<body>

{hdr}

{body}

{foot}
{js}
</body>
</html>
"""

def compare_html(m, fn):
    a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    for k in ("before", "after", "alt"):
        if not a.get(k): sys.exit(f"{fn}: [[compare]] needs {k}=\"...\"")
    for k in ("before", "after"):
        if not os.path.isfile(P(a[k])): sys.exit(f"{fn}: [[compare]] image not found: {a[k]}")
    bl, al = esc(a.get("before_label", "Before")), esc(a.get("after_label", "After"))
    cap = f'<figcaption>{esc(a["caption"])}</figcaption>' if a.get("caption") else ""
    return (f'<figure class="ba"><div class="ba-frame" style="--pos:50%">'
            f'<img src="/{a["after"]}" alt="{after_alt(a, al)}" loading="lazy" decoding="async">'
            f'<img class="ba-before" src="/{a["before"]}" alt="{esc(bl + ": " + a["alt"])}" loading="lazy" decoding="async">'
            f'<span class="ba-line" aria-hidden="true"><span class="ba-knob"></span></span>'
            f'<span class="ba-tag ba-l" aria-hidden="true">{bl}</span><span class="ba-tag ba-r" aria-hidden="true">{al}</span>'
            f'<input class="ba-range" type="range" min="0" max="100" value="50" aria-label="Slide to compare {bl.lower()} and {al.lower()}" '
            f'oninput="this.parentNode.style.setProperty(\'--pos\',this.value+\'%\')"></div>{cap}</figure>')

def after_alt(a, al): return esc(al + ": " + a["alt"])

def load_posts():
    posts = []
    d = P("_blog", "posts")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".post"): continue
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
        if not m: sys.exit(f"{fn}: missing metadata comment")
        try: meta = json.loads(m.group(1))
        except json.JSONDecodeError as e: sys.exit(f"{fn}: bad JSON in metadata: {e}")
        meta["body"] = re.sub(r"\[\[compare\s+(.*?)\]\]", lambda mm, fn=fn: compare_html(mm, fn), m.group(2).strip())
        meta["body"] = re.sub(r"<p>\s*(<figure class=\"ba\">.*?</figure>)\s*</p>", r"\1", meta["body"], flags=re.S)
        for k in ("title", "seo_title", "description", "slug", "date", "service"):
            if not meta.get(k): sys.exit(f"{fn}: missing '{k}'")
        if meta["service"] not in SERVICES: sys.exit(f"{fn}: unknown service {meta['service']}")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["slug"]): sys.exit(f"{fn}: bad slug")
        for k in ("date", "updated"):
            try: datetime.date.fromisoformat(meta.get(k, meta["date"]))
            except ValueError: sys.exit(f"{fn}: '{k}' must be YYYY-MM-DD")
        if fn != f"{meta['date']}-{meta['slug']}.post": sys.exit(f"{fn}: rename to {meta['date']}-{meta['slug']}.post")
        if not isinstance(meta.get("tags", []), list): sys.exit(f"{fn}: tags must be a list")
        if not isinstance(meta.get("summary", []), list): sys.exit(f"{fn}: summary must be a list")
        if any(not (isinstance(x, list) and len(x) == 2) for x in meta.get("faq", [])): sys.exit(f"{fn}: faq must be [[question, answer], ...]")
        if not os.path.isfile(P(meta.get("image", "assets/img/og-image.jpg"))): sys.exit(f"{fn}: image not found: {meta.get('image')}")
        if re.search(r"<h1[\s>]", meta["body"], re.I): sys.exit(f"{fn}: don't use <h1> in the body (the title is the H1)")
        if meta.get("draft") is True: continue
        meta.setdefault("updated", meta["date"]); meta.setdefault("tags", []); meta.setdefault("summary", []); meta.setdefault("faq", [])
        meta.setdefault("image", "assets/img/og-image.jpg"); meta.setdefault("image_alt", meta["title"])
        text = re.sub(r"<[^>]+>", " ", meta["body"]); meta["words"] = len(text.split())
        meta["mins"] = max(1, round(meta["words"] / 230))
        posts.append(meta)
    slugs = [p["slug"] for p in posts]
    dup = sorted({x for x in slugs if slugs.count(x) > 1})
    if dup: sys.exit(f"duplicate slug(s): {dup}")
    tq = [p.get("target_query", "").strip().lower() for p in posts]
    dq = sorted({q for q in tq if q and tq.count(q) > 1})
    if dq: sys.exit(f"two posts target the same search query: {dq}")
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts

def nice(d): return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")

def vars_for(svc):
    s = SERVICES[svc]; return f"--hbg:{s['bg']}; --hfg:{s['fg']}; --hacc:{s['accent']};"

def card(p):
    s = SERVICES[p["service"]]
    return (f'<a class="pcard" href="/blog/{p["slug"]}"><img src="/{p["image"]}" alt="{esc(p["image_alt"])}" loading="lazy" decoding="async" width="800" height="500">'
            f'<div class="b"><span class="tag t-{p["service"]}">{esc(s["name"])}</span><h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p>'
            f'<time datetime="{p["date"]}">{nice(p["date"])} · {p["mins"]} min read</time></div></a>')

def build_post(p, posts):
    url = f"{SITE}/blog/{p['slug']}"; s = SERVICES[p["service"]]
    img = f"{SITE}/{p['image']}"
    score = lambda q: (len(set(q["tags"]) & set(p["tags"])) + 2 * (q["service"] == p["service"]), q["date"])
    related = sorted([q for q in posts if q is not p], key=score, reverse=True)[:3]
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "@id": url + "#post", "headline": p["title"], "description": p["description"],
         "url": url, "mainEntityOfPage": url, "datePublished": iso(p["date"]), "dateModified": iso(p["updated"]), "inLanguage": "en-US",
         "image": img, "wordCount": p["words"], "keywords": ", ".join(p["tags"]), "articleSection": s["name"],
         "author": AUTHOR, "publisher": ORG, "isPartOf": {"@type": "Blog", "@id": SITE + "/blog/#blog", "name": "DYAD Marketects Blog"},
         "about": {"@type": "Service", "name": s["name"], "url": f"{SITE}/{p['service']}", "provider": {"@id": SITE + "/#org"}}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]},
    ]
    related_html = ('<section class="blk"><div class="wrap">\n  <div class="kicker">Keep reading</div><h2>More from the blog</h2>\n  <div class="posts">'
                    + "".join(card(q) for q in related) + '</div>\n</div></section>\n') if related else ""
    faq_html = ""
    if p["faq"]:
        faq_html = '<section class="faq"><h2>Frequently asked questions</h2>' + "".join(
            f'<details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(p["faq"])) + "</section>"
    tldr = ("<aside class=\"tldr\"><strong>Quick answer</strong><ul>" + "".join(f"<li>{esc(x)}</li>" for x in p["summary"]) + "</ul></aside>") if p["summary"] else ""
    upd = f' · Updated <time datetime="{p["updated"]}">{nice(p["updated"])}</time>' if p["updated"] != p["date"] else ""
    body = f"""<section class="post-hero">
  <div class="in">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / <span aria-current="page">{esc(p['title'])}</span></nav>
    <h1>{esc(p['title'])}</h1>
    <div class="meta"><span>By <a href="/about" rel="author">Vincent King</a></span><span><a href="/blog/topic/{p['service']}">{esc(s['name'])}</a></span><span><time datetime="{p['date']}">{nice(p['date'])}</time>{upd}</span><span>{p['mins']} min read</span></div>
  </div>
</section>

<main>
<article class="post">
  <figure class="lead-img"><img src="/{p['image']}" alt="{esc(p['image_alt'])}" width="800" height="500" fetchpriority="high"></figure>
  {tldr}
  <div class="body">
{p['body']}
  </div>
  <div class="faq">{faq_html}</div>
  <a class="svc-cta" href="/{p['service']}"><img src="/assets/img/{s['icon']}" alt=""><span><small>Work with DYAD Marketects</small><b>{esc(s['name'])} in Albuquerque &rarr;</b></span></a>
  <div class="byline"><img src="/assets/img/about-portrait-112.webp" alt="Vincent King" width="56" height="56" loading="lazy"><div><b>Vincent King</b> is the founder of DYAD Marketects, an Albuquerque branding, web design and marketing studio. <a href="/about" rel="author">More about Vince</a>{('<br><small class="ainote">' + esc(AI_NOTE) + '</small>') if AI_NOTE else ''}</div></div>
</article>

{related_html}
<section class="blk cta"><div class="wrap">
  <h2>Let&rsquo;s grow your <span class="script">brand.</span></h2>
  <p>Tell us about your project. We&rsquo;ll usually be in touch within 1 to 2 business days.</p>
  <a class="btn light" href="/#contact">Book a call</a>
</div></section>
</main>"""
    out = page(p["seo_title"], p["description"], url, img, ld, body, vars_for(p["service"]), og_type="article",
               extra_head=f'<meta property="article:published_time" content="{iso(p["date"])}">\n<meta property="article:modified_time" content="{iso(p["updated"])}">\n<meta property="article:author" content="Vincent King">\n')
    open(P("blog", p["slug"] + ".html"), "w", encoding="utf-8").write(out)

def listing(items, url, title, desc, h1, crumbs, lead, active, pager="", extra_ld=None):
    chips = '<nav class="bfil" aria-label="Blog topics">' + (f'<a href="/blog/"{" aria-current=\"page\"" if active == "all" else ""}>All posts</a>') + "".join(
        f'<a href="/blog/topic/{k}"{" aria-current=\"page\"" if active == k else ""}>{esc(v["name"])}</a>' for k, v in SERVICES.items()) + "</nav>"
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#page", "url": url, "name": title, "description": desc,
           "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "en-US",
           "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/blog/{p['slug']}"} for i, p in enumerate(items)]}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}] + (extra_ld or [])
    crumb_html = " / ".join(f'<a href="{u.replace(SITE, "")}">{esc(n)}</a>' for n, u in crumbs[:-1]) + f' / <span aria-current="page">{esc(crumbs[-1][0])}</span>'
    body = f"""<section class="hero">
  <div class="hero-in" style="grid-template-columns:1fr">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
    </div>
  </div>
</section>
<main>
<section class="blk"><div class="wrap">
  {chips}
  <div class="posts">{''.join(card(p) for p in items) or '<p>New posts on this topic are on the way. <a href="/blog/" style="color:#c40c43;font-weight:600">See all posts</a></p>'}</div>
  {pager}
</div></section>
<section class="blk cta"><div class="wrap">
  <h2>Let&rsquo;s grow your <span class="script">brand.</span></h2>
  <p>Tell us about your project. We&rsquo;ll usually be in touch within 1 to 2 business days.</p>
  <a class="btn light" href="/#contact">Book a call</a>
</div></section>
</main>"""
    css = """  .hero{ background:var(--pink-bg, #e6104e); color:#fff; } .hero h1 .script{ color:var(--lime); }
  .bfil{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px; }
  .bfil a{ font-family:'Arian LT Demi', sans-serif; font-size:12px; letter-spacing:.04em; text-transform:uppercase; border:1.5px solid var(--ink); border-radius:30px; padding:9px 16px; text-decoration:none; }
  .bfil a[aria-current], .bfil a:hover{ background:var(--ink); color:#fff; }
"""
    return page(title, desc, url, SITE + "/assets/img/og-image.jpg?v=2", ld, body, "--hbg:var(--pink); --hfg:#fff; --hacc:var(--lime);", extra_css=css,
                robots="index, follow, max-image-preview:large, max-snippet:-1" if items else "noindex, follow")

def build_index(posts):
    pages = [posts[i:i + PER_PAGE] for i in range(0, max(len(posts), 1), PER_PAGE)] or [[]]
    n = len(pages)
    blog_ld = {"@context": "https://schema.org", "@type": "Blog", "@id": SITE + "/blog/#blog", "name": "DYAD Marketects Blog", "url": SITE + "/blog/",
               "description": "Branding, web design, video and social media advice for Albuquerque and New Mexico businesses.",
               "publisher": ORG, "inLanguage": "en-US"}
    for i, items in enumerate(pages, 1):
        url = SITE + "/blog/" if i == 1 else f"{SITE}/blog/page/{i}"
        href = lambda k: "/blog/" if k == 1 else f"/blog/page/{k}"
        pager = ""
        if n > 1:
            pager = '<nav class="pager" aria-label="Blog pages">' + (f'<a href="{href(i-1)}" rel="prev">&larr; Newer</a>' if i > 1 else "") + "".join(
                (f'<span aria-current="page">{k}</span>' if k == i else f'<a href="{href(k)}">{k}</a>') for k in range(1, n + 1)) + (
                f'<a href="{href(i+1)}" rel="next">Older &rarr;</a>' if i < n else "") + "</nav>"
        crumbs = [("Home", SITE + "/"), ("Blog", SITE + "/blog/")] + ([(f"Page {i}", url)] if i > 1 else [])
        title = "Blog | Branding & Marketing Tips for Albuquerque | DYAD Marketects" + (f" (Page {i})" if i > 1 else "")
        out = listing(items, url, title, "Branding, web design, video and social media advice for Albuquerque and New Mexico businesses from DYAD Marketects (DYAD Grow).",
                      'The DYAD <span class="script">Blog</span>', crumbs,
                      "Straight answers on branding, websites, video and social media for Albuquerque and New Mexico businesses, from the DYAD Marketects studio.",
                      "all", pager, [blog_ld] if i == 1 else None)
        dest = P("blog", "index.html") if i == 1 else P("blog", "page", f"{i}.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True); open(dest, "w", encoding="utf-8").write(out)
    for f in (os.listdir(P("blog", "page")) if os.path.isdir(P("blog", "page")) else []):
        if f.endswith(".html") and not (f[:-5].isdigit() and 2 <= int(f[:-5]) <= n): os.remove(P("blog", "page", f))
    os.makedirs(P("blog", "topic"), exist_ok=True)
    for k, v in SERVICES.items():
        url = f"{SITE}/blog/topic/{k}"
        items = [p for p in posts if p["service"] == k]
        out = listing(items, url, f"{v['name']} Tips for Albuquerque Businesses | DYAD Blog",
                      f"{v['name']} advice for Albuquerque and New Mexico businesses from the DYAD Marketects blog.",
                      f'{esc(v["name"])} <span class="script">tips</span>',
                      [("Home", SITE + "/"), ("Blog", SITE + "/blog/"), (v["name"], url)],
                      f'Practical {esc(v["name"].lower())} advice from DYAD Marketects. Ready for help? See our <a href="/{k}" style="color:inherit;text-decoration:underline">{esc(v["name"].lower())} services in Albuquerque</a>.',
                      k)
        open(P("blog", "topic", k + ".html"), "w", encoding="utf-8").write(out)

def build_home_timeline():
    """Homepage timeline cards, generated from _tools/journey.py. Each card's Immerse button opens its in-depth section on /about."""
    f = P("index.html"); t = open(f, encoding="utf-8").read()
    start, end = "<!--journey:cards-->", "<!--/journey:cards-->"
    if start not in t:
        m = re.search(r'(<div class="timeline-scroll" id="timelineScroll">)(.*?)(\s*</div><button class="sc-btn prev")', t, re.S)
        if not m: sys.exit("error: homepage timeline not found")
        t = t[:m.end(1)] + start + end + t[m.start(3):]
    ids = [j["id"] for j in JOURNEY]
    if len(ids) != len(set(ids)): sys.exit("error: duplicate id in _tools/journey.py")
    cards = "".join(f'\n    <div class="t-card"><div class="t-year">{j["year"]}</div><h4>{j["title"]}</h4><p>{j["summary"]}</p>'
                    f'<a class="t-immerse" href="/about#{j["id"]}" aria-label="Immerse: {esc(re.sub("<[^>]+>|&[a-z]+;", "", j["title"]))}">Immerse <span aria-hidden="true">&#8599;</span></a></div>' for j in JOURNEY)
    t = re.sub(re.escape(start) + ".*?" + re.escape(end), lambda m: start + cards + "\n    " + end, t, flags=re.S)
    open(f, "w", encoding="utf-8").write(t)

def journey_html():
    """In-depth timeline on /about: one anchored section per milestone with story, YouTube videos, photo gallery and sources."""
    dims = json.load(open(P("_tools", "journey_dims.json")))
    def fig(name, cap):
        if name.startswith("@"):
            src = name[1:]; w, h = dims[name]; full = src; sm = src; srcset = ""
        else:
            if name not in dims: sys.exit(f"error: journey image {name} missing from journey_dims.json")
            w, h = dims[name]; full = f"/assets/img/journey/{name}.webp"; sm = f"/assets/img/journey/{name}-700.webp"
            srcset = f' srcset="{sm} 700w, {full} {w}w" sizes="(max-width:700px) 92vw, 420px"'
        alt = re.sub("<[^>]+>", "", cap)
        return (f'<figure class="jg-item"><a href="{full}" class="jg-open" data-cap="{esc(html.unescape(alt))}"><img src="{sm}"{srcset} alt="{esc(html.unescape(alt))}" '
                f'width="{w}" height="{h}" loading="lazy" decoding="async"></a><figcaption>{cap}</figcaption></figure>')
    def video(vid, title):
        return (f'<div class="yt"><button type="button" class="yt-btn" data-id="{vid}" aria-label="Play video: {esc(title)}">'
                f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
                f'<span class="yt-play" aria-hidden="true"></span></button><p class="yt-t">{esc(title)}</p></div>')
    out = []
    for i, j in enumerate(JOURNEY):
        vids = "".join(video(*v) for v in j.get("videos", []))
        media = "".join(fig(*m) for m in j.get("media", []))
        src = "".join("<li>" + (f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' if u else t) + "</li>" for t, u in j.get("sources", []))
        out.append(f"""
  <article class="jn" id="{j['id']}" style="--jc:var(--{['pink','magenta','lavender','lime'][i % 4]})">
    <div class="jn-head rv rv-up"><div class="jn-yr">{j['year']}</div><h3>{j['title']}</h3></div>
    <div class="jn-story rv rv-up">{j['story']}</div>
    {f'<div class="jn-vids rv rv-up">{vids}</div>' if vids else ''}
    {f'<div class="jg">{media}</div>' if media else ''}
    {f'<div class="jn-src"><b>Sources</b><ul>{src}</ul></div>' if src else ''}
  </article>""")
    chips = "".join(f'<a href="#{j["id"]}">{j["year"]}</a>' for j in JOURNEY)
    return chips, "".join(out)

def build_about(posts):
    """Author page for Vincent King (/about): bio and timeline pulled from the homepage, plus his posts."""
    s = open(P("index.html"), encoding="utf-8").read()
    m = re.search(r"<p[^>]*>\s*Vincent Inkosi King is the founder.*?</p>", s, re.S)
    bio = m.group(0) if m else "<p>Vincent King is the founder of DYAD Marketects, an Albuquerque, New Mexico branding, web design and content studio.</p>"
    bio = re.sub(r"<p[^>]*>", "<p>", bio, count=1)
    chips, journey = journey_html()
    url = SITE + "/about"
    person = dict(AUTHOR, **{"@context": "https://schema.org", "givenName": "Vincent", "familyName": "King",
                             "alternateName": ["Vincent Inkosi King", "Vince King"], "worksFor": {"@id": SITE + "/#org"},
                             "alumniOf": [{"@type": "EducationalOrganization", "name": "Albuquerque Academy"}, {"@type": "CollegeOrUniversity", "name": "University of New Mexico"}, {"@type": "CollegeOrUniversity", "name": "Central New Mexico Community College"}],
                             "knowsAbout": ["Branding", "Logo design", "Web design", "Digital marketing", "Social media marketing", "Video production", "Immersive media", "3D animation"]})
    ld = [{"@context": "https://schema.org", "@type": "ProfilePage", "@id": url + "#page", "url": url, "name": "About Vincent King, founder of DYAD Marketects",
           "dateModified": iso(max([p["updated"] for p in posts] or [datetime.date.today().isoformat()])), "mainEntity": person, "isPartOf": {"@id": SITE + "/#website"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "About Vincent King", "item": url}]}]
    mine = posts[:6]
    body = f"""<script>document.documentElement.classList.add('js');</script>
<section class="hero ab-hero">
  <div class="hero-in">
    <div class="ab-copy">
      <nav class="crumbs rv rv-up" aria-label="Breadcrumb"><a href="/">Home</a> / <span aria-current="page">About Vincent King</span></nav>
      <h1 class="rv rv-up" style="--d:.08s">Vincent <span class="script">King</span></h1>
      <p class="lead rv rv-up" style="--d:.16s">Founder &amp; CEO of DYAD Marketects, a branding, web design and marketing studio in Albuquerque, New Mexico.</p>
      <div class="btns rv rv-up" style="--d:.24s"><a class="btn light" href="/#contact">Book a call</a><a class="btn alt" href="https://www.linkedin.com/in/vincent-inkosi-king/" rel="me noopener" target="_blank">LinkedIn</a></div>
    </div>
    <figure class="ab-hero-img rv rv-hero"><img src="/assets/img/about/about-lets-grow.webp" srcset="/assets/img/about/about-lets-grow-800.webp 800w, /assets/img/about/about-lets-grow.webp 1600w" sizes="(max-width:900px) 92vw, 52vw" alt="Vincent King pointing at the camera with a LinkedIn post and social media icons behind him, under the words Let's Grow" width="1600" height="900" fetchpriority="high"></figure>
  </div>
</section>
<main>
<section class="blk"><div class="wrap ab-split">
  <div class="ab-text">
    <div class="kicker rv rv-up">About me &amp; my journey</div><h2 class="rv rv-up">Design and data, one system</h2>
    <div class="rv rv-up" style="--d:.1s">{bio}</div>
  </div>
  <figure class="ab-fig rv rv-right"><img src="/assets/img/about/about-duality.webp" srcset="/assets/img/about/about-duality-700.webp 700w, /assets/img/about/about-duality.webp 1400w" sizes="(max-width:900px) 92vw, 46vw" alt="Two sides of Vincent King: one surrounded by bursts of color, the other by data charts" width="1400" height="906" loading="lazy" decoding="async"></figure>
</div></section>
<section class="blk" style="padding-top:0"><div class="wrap">
  <figure class="ab-wide rv rv-zoom"><img src="/assets/img/about/about-speaking.webp" srcset="/assets/img/about/about-speaking-700.webp 700w, /assets/img/about/about-speaking.webp 1400w" sizes="(max-width:1100px) 92vw, 1100px" alt="Vincent King speaking to an audience with a microphone in front of a presentation screen" width="1400" height="906" loading="lazy" decoding="async"></figure>
</div></section>
<section class="blk jr" id="journey" style="padding-top:0"><div class="wrap">
  <div class="jr-intro">
    <div>
      <div class="kicker rv rv-up">Timeline</div><h2 class="rv rv-up">How I got <span class="script">here</span></h2>
      <p class="rv rv-up">My path has been a little unusual, so here&rsquo;s the proof: the projects, the people and the receipts, year by year. Jump to any year or scroll the whole story.</p>
      <nav class="jr-chips rv rv-up" aria-label="Jump to a year">{chips}</nav>
    </div>
    <aside class="ab-poster"><figure class="rv rv-tilt"><img src="/assets/img/about/about-design-data.webp" alt="DYAD poster of Vincent King with the words Design x Data Yields Agile Development" width="900" height="1125" loading="lazy" decoding="async"></figure></aside>
  </div>
  <div class="jr-line">{journey}
  </div>
</div></section>
<div class="lb" id="lb" hidden><button type="button" class="lb-x" aria-label="Close">&times;</button><button type="button" class="lb-p" aria-label="Previous photo">&#8249;</button><figure><img alt=""><figcaption></figcaption></figure><button type="button" class="lb-n" aria-label="Next photo">&#8250;</button></div>
{('<section class="blk" style="padding-top:0"><div class="wrap"><div class="kicker">Writing</div><h2>Latest posts by Vince</h2><div class="posts">' + "".join(card(p) for p in mine) + '</div><p style="margin-top:18px"><a href="/blog/" style="color:#c40c43;font-weight:600">See all posts &rarr;</a></p></div></section>') if mine else ''}
<section class="blk cta"><div class="wrap">
  <h2>Let&rsquo;s grow your <span class="script">brand.</span></h2>
  <p>Tell us about your project. We&rsquo;ll usually be in touch within 1 to 2 business days.</p>
  <a class="btn light" href="/#contact">Book a call</a>
</div></section>
</main>
<script>
(function(){{
  var els=[].slice.call(document.querySelectorAll('.rv, .jg-item'));
  if(!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches){{ els.forEach(function(e){{ e.classList.add('in'); }}); return; }}
  var io=new IntersectionObserver(function(es){{ es.forEach(function(en){{ if(en.isIntersecting){{ en.target.classList.add('in'); io.unobserve(en.target); }} }}); }},{{rootMargin:'0px 0px -8% 0px',threshold:.12}});
  els.forEach(function(e,i){{ if(e.matches('.jg-item')) e.style.setProperty('--d',([].indexOf.call(e.parentNode.children,e)%3)*0.08+'s'); io.observe(e); }});
}})();
(function(){{
  /* YouTube: load the player only when someone presses play (faster page, no YouTube cookies until then) */
  document.addEventListener('click', function(e){{
    var b=e.target.closest('.yt-btn'); if(!b) return;
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0';
    f.title=b.getAttribute('aria-label').replace('Play video: ','');
    f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen'; f.allowFullscreen=true;
    b.replaceWith(f);
  }});
  /* arriving from a homepage Immerse button: settle on the right milestone once fonts and images have laid out */
  if(location.hash.length>1){{ var tgt=document.getElementById(location.hash.slice(1));
    if(tgt){{ var fix=function(){{ tgt.scrollIntoView(); }}; window.addEventListener('load', function(){{ setTimeout(fix,60); }}); if(document.fonts) document.fonts.ready.then(fix); }} }}
  /* photo lightbox, per milestone */
  var lb=document.getElementById('lb'); if(!lb) return;
  var img=lb.querySelector('img'), cap=lb.querySelector('figcaption'), set=[], at=0, last=null;
  function show(i){{ at=(i+set.length)%set.length; var a=set[at]; img.src=a.getAttribute('href'); img.alt=a.dataset.cap; cap.textContent=a.dataset.cap; }}
  function close(){{ lb.hidden=true; document.documentElement.style.overflow=''; if(last) last.focus(); }}
  document.addEventListener('click', function(e){{
    var a=e.target.closest('.jg-open'); if(!a) return; e.preventDefault(); last=a;
    set=[].slice.call(a.closest('.jg').querySelectorAll('.jg-open')); show(set.indexOf(a));
    lb.hidden=false; document.documentElement.style.overflow='hidden'; lb.querySelector('.lb-x').focus();
  }});
  lb.addEventListener('click', function(e){{
    if(e.target.closest('.lb-x') || e.target===lb) close();
    else if(e.target.closest('.lb-p')) show(at-1);
    else if(e.target.closest('.lb-n')) show(at+1);
  }});
  document.addEventListener('keydown', function(e){{
    if(lb.hidden) return;
    if(e.key==='Escape') close(); else if(e.key==='ArrowLeft') show(at-1); else if(e.key==='ArrowRight') show(at+1);
  }});
}})();
</script>"""
    css = """  .hero{ background:var(--pink-bg, #e6104e); color:#fff; } .hero h1 .script{ color:var(--lime); } .blk p + p{ margin-top:14px; }
  main{ overflow-x:clip; }
  .ab-hero{ overflow:hidden; padding-top:clamp(40px,6vw,80px); padding-bottom:clamp(30px,5vw,60px); }
  .ab-hero .hero-in{ grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr); max-width:1240px; }
  .ab-hero-img{ margin:0; } .ab-hero-img img{ width:100%; height:auto; filter:drop-shadow(0 30px 40px rgba(0,0,0,.25)); }
  .ab-split{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:clamp(28px,5vw,70px); align-items:center; }
  .ab-fig, .ab-wide, .ab-poster figure{ margin:0; } .ab-fig img, .ab-wide img, .ab-poster img{ width:100%; height:auto; }
  .ab-poster img{ border-radius:20px; box-shadow:0 30px 60px rgba(0,0,0,.18); }
  /* in-depth timeline */
  .jr-intro{ display:grid; grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr); gap:clamp(28px,5vw,64px); align-items:center; margin-bottom:clamp(30px,5vw,60px); }
  .jr-intro h2 .script{ color:var(--pink); }
  .jr-intro p{ max-width:56ch; }
  .jr-chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:22px; }
  .jr-chips a{ font-family:'Arian LT Heavy', sans-serif; font-size:14px; color:var(--ink); background:#fff; border-radius:30px; padding:8px 14px; box-shadow:0 6px 16px rgba(0,0,0,.06); transition:background .2s ease, color .2s ease, transform .2s ease; }
  .jr-chips a:hover{ background:var(--pink); color:#fff; transform:translateY(-2px); }
  .ab-poster img{ max-height:560px; width:auto; max-width:100%; display:block; margin-left:auto; }
  .jr-line{ position:relative; padding-left:clamp(26px,4vw,48px); }
  .jr-line::before{ content:""; position:absolute; left:6px; top:8px; bottom:8px; width:2px; background:linear-gradient(var(--pink),var(--magenta),var(--lavender),var(--lime)); border-radius:2px; }
  .jn{ position:relative; padding:0 0 clamp(44px,6vw,80px); scroll-margin-top:110px; }
  .jn::before{ content:""; position:absolute; left:calc(-1 * clamp(26px,4vw,48px) + 1px); top:10px; width:12px; height:12px; border-radius:50%; background:var(--jc); box-shadow:0 0 0 5px var(--paper, #eeeeee), 0 0 0 7px var(--jc); }
  .jn:target .jn-head h3{ color:var(--pink); }
  .jn-head{ display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; margin-bottom:14px; }
  .jn-yr{ font-family:'Arian LT Heavy', sans-serif; font-size:clamp(34px,5vw,54px); line-height:1; color:var(--pink); }
  .jn-head h3{ font-size:clamp(19px,2.2vw,26px); text-transform:uppercase; margin:0; transition:color .4s ease; }
  .jn-story{ max-width:72ch; } .jn-story h4{ font-family:'Arian LT Heavy', sans-serif; font-size:17px; color:var(--ink); text-transform:uppercase; margin:28px 0 8px; letter-spacing:.02em; }
  .jn-story ul{ margin:10px 0 0 20px; } .jn-story li{ margin:6px 0; font-size:16px; line-height:1.6; }
  .jn-story a{ color:var(--pink-text, #c40c43); text-decoration:underline; text-underline-offset:3px; }
  .jn-vids{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr)); gap:18px; margin-top:24px; max-width:980px; }
  .yt-btn, .yt iframe{ display:block; width:100%; aspect-ratio:16/9; border:0; border-radius:16px; overflow:hidden; background:#000; }
  .yt-btn{ position:relative; padding:0; cursor:pointer; box-shadow:0 18px 40px rgba(0,0,0,.18); }
  .yt-btn img{ width:100%; height:100%; object-fit:cover; opacity:.85; transition:opacity .3s ease, transform .6s cubic-bezier(.16,1,.3,1); }
  .yt-btn:hover img{ opacity:1; transform:scale(1.04); }
  .yt-play{ position:absolute; left:50%; top:50%; width:72px; height:72px; margin:-36px 0 0 -36px; border-radius:50%; background:var(--pink); box-shadow:0 10px 30px rgba(245,17,83,.5); transition:transform .3s ease; }
  .yt-play::after{ content:""; position:absolute; left:29px; top:22px; border-style:solid; border-width:14px 0 14px 22px; border-color:transparent transparent transparent #fff; }
  .yt-btn:hover .yt-play{ transform:scale(1.1); }
  .yt-btn:focus-visible{ outline:3px solid var(--pink); outline-offset:4px; }
  .yt-t{ font-size:14px !important; margin-top:10px !important; color:#555; }
  .jg{ columns:3 220px; column-gap:14px; margin-top:24px; }
  .jg-item{ break-inside:avoid; margin:0 0 14px; }
  .jg-item a{ display:block; border-radius:12px; overflow:hidden; background:#ddd; }
  .jg-item img{ width:100%; height:auto; display:block; transition:transform .7s cubic-bezier(.16,1,.3,1); }
  .jg-item a:hover img{ transform:scale(1.05); }
  .jg-item figcaption{ font-size:13px; line-height:1.45; color:#555; margin-top:7px; }
  .jn-src{ margin-top:18px; font-size:13.5px; color:#555; } .jn-src ul{ margin:6px 0 0 18px; } .jn-src a{ color:var(--pink-text, #c40c43); text-decoration:underline; }
  .js .jg-item{ opacity:0; transform:translateY(30px) scale(.97); transition:opacity .8s ease var(--d,0s), transform 1s cubic-bezier(.16,1,.3,1) var(--d,0s); }
  .js .jg-item.in{ opacity:1; transform:none; }
  .lb{ position:fixed; inset:0; z-index:10000; background:rgba(10,10,10,.96); display:flex; align-items:center; justify-content:center; padding:4vh 64px; }
  .lb[hidden]{ display:none; }
  .lb figure{ margin:0; max-width:100%; max-height:100%; display:flex; flex-direction:column; align-items:center; }
  .lb img{ max-width:100%; max-height:82vh; border-radius:10px; object-fit:contain; }
  .lb figcaption{ color:#eee; font-size:14px; margin-top:12px; text-align:center; max-width:70ch; }
  .lb button{ position:absolute; background:rgba(255,255,255,.12); color:#fff; border:0; border-radius:50%; width:48px; height:48px; font-size:30px; line-height:1; cursor:pointer; }
  .lb button:hover{ background:var(--pink); }
  .lb-x{ top:18px; right:18px; } .lb-p{ left:12px; top:50%; margin-top:-24px; } .lb-n{ right:12px; top:50%; margin-top:-24px; }
  @media (max-width:700px){ .lb{ padding:60px 10px; } .lb-p, .lb-n{ top:auto; bottom:14px; margin:0; } .lb-p{ left:calc(50% - 60px); } .lb-n{ right:calc(50% - 60px); } .jg{ columns:2 140px; column-gap:10px; } .jg-item figcaption{ font-size:12px; } }
  @media (max-width:900px){
    .ab-hero .hero-in, .ab-split, .jr-intro{ grid-template-columns:1fr; }
    .ab-hero-img{ order:-1; }
    .ab-poster{ max-width:360px; margin:0 auto; } .ab-poster img{ margin:0 auto; }
  }
  /* intro animations (only when JS is on; nothing is hidden for crawlers or no-JS visitors) */
  .js .rv{ opacity:0; transition:opacity .9s cubic-bezier(.16,1,.3,1) var(--d,0s), transform 1.1s cubic-bezier(.16,1,.3,1) var(--d,0s), clip-path 1.2s cubic-bezier(.16,1,.3,1) var(--d,0s), filter 1s ease var(--d,0s); will-change:transform,opacity; }
  .js .rv-up{ transform:translateY(34px); }
  /* figures fade; the image inside does the motion (clip-path on the observed element would hide it from the observer) */
  .js .rv-right, .js .rv-zoom, .js .rv-hero{ transition:opacity .6s ease var(--d,0s); }
  .js .rv-right img, .js .rv-zoom img, .js .rv-hero img{ transition:transform 1.2s cubic-bezier(.16,1,.3,1) var(--d,0s), clip-path 1.3s cubic-bezier(.16,1,.3,1) var(--d,0s), filter 1s ease var(--d,0s); }
  .js .rv-right img{ transform:translateX(50px) rotate(1.5deg); clip-path:inset(0 0 0 100%); }
  .js .rv-zoom img{ transform:scale(.9); clip-path:inset(12% 12% 12% 12% round 32px); filter:blur(6px); }
  .js .rv-tilt{ transform:perspective(900px) rotateY(-18deg) translateY(40px); }
  .js .rv-hero{ --d:.15s; }
  .js .rv-hero img{ transform:scale(1.08) translateY(20px); filter:blur(14px) drop-shadow(0 30px 40px rgba(0,0,0,.25)); clip-path:circle(0% at 50% 45%); transition-duration:1.5s, 1.6s, 1.2s; }
  .js .rv.in{ opacity:1; transform:none; }
  .js .rv.in img{ transform:none; filter:drop-shadow(0 0 0 transparent); clip-path:inset(0 0 0 0); }
  .js .rv-hero.in img{ clip-path:circle(150% at 50% 45%); filter:drop-shadow(0 30px 40px rgba(0,0,0,.25)); }
  .js .rv-hero.in{ animation:abFloat 7s ease-in-out 2s infinite; }
  @keyframes abFloat{ 0%,100%{ transform:translateY(0); } 50%{ transform:translateY(-10px); } }
  @media (prefers-reduced-motion: reduce){ .js .jg-item, .js .rv, .js .rv img{ opacity:1 !important; transform:none !important; filter:none !important; clip-path:none !important; } .js .rv-hero.in{ animation:none; } }
"""
    out = page("About Vincent King | Founder of DYAD Marketects, Albuquerque",
               "Vincent King is the founder of DYAD Marketects, an Albuquerque branding, web design and marketing studio, with 20+ years in immersive media, design and digital marketing.",
               url, SITE + "/assets/img/about/about-lets-grow.webp", ld, body, "--hbg:var(--pink); --hfg:#fff; --hacc:var(--lime);",
               og_type="profile", extra_css=css,
               extra_head='<link rel="preload" as="image" href="/assets/img/about/about-lets-grow.webp" imagesrcset="/assets/img/about/about-lets-grow-800.webp 800w, /assets/img/about/about-lets-grow.webp 1600w" imagesizes="(max-width:900px) 92vw, 52vw">\n')
    open(P("about.html"), "w", encoding="utf-8").write(out)

def build_feed(posts):
    now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
    items = "".join(f"""
  <item>
    <title>{esc(p['title'])}</title>
    <link>{SITE}/blog/{p['slug']}</link>
    <guid isPermaLink="true">{SITE}/blog/{p['slug']}</guid>
    <pubDate>{format_datetime(datetime.datetime.fromisoformat(iso(p['date'])))}</pubDate>
    <category>{esc(SERVICES[p['service']]['name'])}</category>
    <description>{esc(p['description'])}</description>
  </item>""" for p in posts[:30])
    open(P("feed.xml"), "w", encoding="utf-8").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>DYAD Marketects Blog</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Branding, web design, video and social media advice for Albuquerque and New Mexico businesses.</description>
  <language>en-us</language>
  <lastBuildDate>{now}</lastBuildDate>{items}
</channel>
</rss>
""")

def build_sitemap(posts):
    sm = open(P("sitemap.xml"), encoding="utf-8").read()
    sm = re.sub(r"\s*<url>\s*<loc>https://dyadgrow\.com/(blog/|about<)[^<]*</loc>.*?</url>", "", sm, flags=re.S)
    sm = re.sub(r"\s*<url>\s*<loc>https://dyadgrow\.com/about</loc>.*?</url>", "", sm, flags=re.S)
    today = datetime.date.today().isoformat()
    newest = max([p["updated"] for p in posts] or [today])
    entry = lambda loc, lm: f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lm}</lastmod>\n  </url>\n"
    add = entry(SITE + "/about", max(newest, JOURNEY_UPDATED)) + entry(SITE + "/blog/", newest)
    for i in range(2, -(-len(posts) // PER_PAGE) + 1): add += entry(f"{SITE}/blog/page/{i}", newest)
    for k in SERVICES:
        mine = [p["updated"] for p in posts if p["service"] == k]
        if mine: add += entry(f"{SITE}/blog/topic/{k}", max(mine))
    add += "".join(entry(f"{SITE}/blog/{p['slug']}", p["updated"]) for p in posts)
    sm = sm.replace("</urlset>", add + "</urlset>")
    # service pages list their latest posts, so their lastmod moves when a new post for that service ships
    for k in SERVICES:
        n = max((p["updated"] for p in posts if p["service"] == k), default=None)
        if n: sm = re.sub(rf"(<loc>{re.escape(SITE)}/{k}</loc>\s*<lastmod>)([^<]+)", lambda m: m.group(1) + max(m.group(2), n), sm)
    open(P("sitemap.xml"), "w", encoding="utf-8").write(sm)

def build_service_blocks(posts):
    """Refresh the 'From the blog' block on each service page (between markers)."""
    for svc, s in SERVICES.items():
        f = P(svc + ".html"); t = open(f, encoding="utf-8").read()
        mine = [p for p in posts if p["service"] == svc][:3]
        block = ""
        if mine:
            block = ('<section class="blk" style="padding-top:0"><div class="wrap">\n  <div class="kicker">From the blog</div><h2>'
                     + esc(s["name"]) + ' tips</h2>\n  <div class="posts">' + "".join(card(p) for p in mine)
                     + '</div>\n  <p style="margin-top:18px"><a href="/blog/" style="color:#c40c43;font-weight:600">See all posts &rarr;</a></p>\n</div></section>\n')
        start, end = "<!--blog:latest-->", "<!--/blog:latest-->"
        if start not in t:
            anchor = '<section class="blk"><div class="wrap">\n  <div class="kicker">More services</div>'
            if anchor not in t: print("warn: no anchor in", svc); continue
            t = t.replace(anchor, start + end + "\n" + anchor, 1)
        t = re.sub(re.escape(start) + ".*?" + re.escape(end), start + "\n" + block + end, t, flags=re.S)
        t = re.sub(r"/\*blog-cards\*/.*?/\*/blog-cards\*/\n?", "", t, flags=re.S)
        if mine:
            css = "/*blog-cards*/\n" + BLOG_CSS[BLOG_CSS.index("  .posts{"):] + "/*/blog-cards*/\n"
            t = t.replace("</style>", css + "</style>", 1)
        open(f, "w", encoding="utf-8").write(t)

def build_home_block(posts):
    """'From the blog' strip on the homepage, just above the FAQ (never near the loader or hero)."""
    f = P("index.html"); t = open(f, encoding="utf-8").read()
    start, end = "<!--blog:home-->", "<!--/blog:home-->"
    if start not in t:
        anchor = '<section id="faq">'
        if anchor not in t: print("warn: homepage FAQ anchor not found"); return
        t = t.replace(anchor, start + end + "\n" + anchor, 1)
    block = ""
    if posts:
        cards = "".join(
            f'<a class="hb-card" href="/blog/{p["slug"]}"><img src="/{p["image"]}" alt="{esc(p["image_alt"])}" loading="lazy" decoding="async" width="800" height="500">'
            f'<span class="hb-tag">{esc(SERVICES[p["service"]]["name"])}</span><span class="hb-t">{esc(p["title"])}</span>'
            f'<time datetime="{p["date"]}">{nice(p["date"])}</time></a>' for p in posts[:3])
        block = f"""
<section id="blog-latest" class="hb">
  <div class="kicker">From the blog</div>
  <h2 class="section-title">Fresh from the studio</h2>
  <div class="hb-grid">{cards}</div>
  <a class="hb-all" href="/blog/">See all posts &rarr;</a>
  <style>
    .hb .hb-grid{{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:20px; margin-top:34px; }}
    .hb-card{{ display:flex; flex-direction:column; gap:10px; background:#fff; border-radius:16px; overflow:hidden; padding-bottom:20px; box-shadow:0 10px 26px rgba(0,0,0,.06); transition:transform .4s cubic-bezier(.22,1,.36,1), box-shadow .4s ease; }}
    .hb-card:hover{{ transform:translateY(-4px); box-shadow:0 20px 40px rgba(245,17,83,.18); }}
    .hb-card img{{ width:100%; height:auto; aspect-ratio:16/10; object-fit:cover; }}
    .hb-tag{{ margin:4px 20px 0; font-family:var(--mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:#c40c43; }}
    .hb-t{{ margin:0 20px; font-family:var(--display-heavy); font-weight:800; text-transform:uppercase; font-size:16px; line-height:1.25; color:var(--ink); }}
    .hb-card time{{ margin:auto 20px 0; font-family:var(--mono); font-size:11.5px; color:#5f5f5f; text-transform:uppercase; }}
    .hb-all{{ display:inline-block; margin-top:26px; font-family:var(--display-demi); font-weight:600; text-transform:uppercase; font-size:13px; letter-spacing:.04em; color:#c40c43; }}
  </style>
</section>
"""
    t = re.sub(re.escape(start) + ".*?" + re.escape(end), lambda m: start + block + end, t, flags=re.S)
    open(f, "w", encoding="utf-8").write(t)

if __name__ == "__main__":
    os.makedirs(P("blog"), exist_ok=True)
    posts = load_posts()
    keep = {p["slug"] + ".html" for p in posts} | {"index.html"}
    for fn in os.listdir(P("blog")):
        if fn.endswith(".html") and fn not in keep: os.remove(P("blog", fn))
    for p in posts: build_post(p, posts)
    build_home_timeline(); build_index(posts); build_about(posts); build_feed(posts); build_sitemap(posts); build_service_blocks(posts); build_home_block(posts)
    print(f"built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))
