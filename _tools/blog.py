#!/usr/bin/env python3
"""
DYAD Marketects blog builder.

Source posts live in _blog/posts/*.post (robots.txt keeps crawlers out of _blog/ and _tools/;
the .post extension keeps them from being treated as web pages). Each source file starts with a JSON metadata block inside an
HTML comment, followed by the article body as plain HTML:

    <!--
    {
      "title": "Visible headline",
      "seo_title": "Title tag, 60 characters or fewer",
      "description": "Meta description, 150 to 160 characters",
      "slug": "url-slug",
      "date": "2026-10-16",
      "updated": "2026-10-16",
      "service": "branding-logo-design | web-design | video-photo-production | social-media-marketing",
      "tags": ["Branding", "Albuquerque"],
      "image": "images/gorman-website-card.webp",
      "image_alt": "Describe the image",
      "summary": ["Key takeaway 1", "Key takeaway 2", "Key takeaway 3"],
      "faq": [["Question?", "Answer."]]
    }
    -->
    <p>Article body...</p>

Run:  python3 _tools/blog.py
It writes blog/<slug>.html, blog/index.html, feed.xml, refreshes the blog
entries in sitemap.xml, and refreshes the "From the blog" block on each service page.
"""
import html, json, os, re, sys, datetime
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dyadgrow.com"
P = lambda *a: os.path.join(ROOT, *a)
esc = lambda s: html.escape(s, quote=True)

SERVICES = {
    "branding-logo-design":   dict(name="Branding & Logo Design",            bg="var(--pink)",     fg="#fff",        accent="var(--lime)", icon="icon-cap-1.webp"),
    "web-design":             dict(name="Web Design & Development",          bg="var(--lavender)", fg="var(--ink)",  accent="var(--pink)", icon="icon-cap-2.webp"),
    "video-photo-production": dict(name="Video & Photo Production",          bg="var(--magenta)",  fg="#fff",        accent="var(--lime)", icon="icon-cap-3.webp"),
    "social-media-marketing": dict(name="Social Media & Content Marketing",  bg="var(--lime)",     fg="var(--ink)",  accent="var(--pink)", icon="icon-cap-4.webp"),
}
ORG = {"@type": "ProfessionalService", "@id": SITE + "/#org", "name": "DYAD Marketects", "alternateName": ["DYAD Grow", "DYAD"],
       "url": SITE + "/", "logo": SITE + "/assets/img/logo-header.webp",
       "address": {"@type": "PostalAddress", "addressLocality": "Albuquerque", "addressRegion": "NM", "addressCountry": "US"},
       "sameAs": ["https://www.facebook.com/dyadmarketects", "https://www.instagram.com/dyadmarketects/",
                  "https://www.linkedin.com/company/dyad-marketects", "https://maps.google.com/?cid=12864398712172302748"]}
AUTHOR = {"@type": "Person", "@id": SITE + "/#vincent-king", "name": "Vincent King", "jobTitle": "Founder & CEO, DYAD Marketects",
          "url": SITE + "/#about", "sameAs": ["https://www.linkedin.com/in/vincent-inkosi-king/"]}

# ---------- shared chrome, taken from the live service page so the blog always matches the site ----------
def chrome():
    s = open(P("web-design.html"), encoding="utf-8").read()
    gtag = s[s.index("<!-- Google tag"):s.index("<style>")]
    style = s[s.index("<style>") + 7:s.index("</style>")]
    hdr = s[s.index('<header class="top">'):s.index("</nav>\n</div>", s.index('<div class="mm"')) + len("</nav>\n</div>")]
    hdr = hdr.replace('class="nl cur"', 'class="nl"').replace(' aria-current="page"', "")
    foot = s[s.index("<footer>"):s.index("</footer>") + 9].replace(' aria-current="page"', "")
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
  .body a{ color:var(--pink); text-decoration:underline; text-underline-offset:3px; font-weight:600; }
  .body blockquote{ margin:26px 0; padding:18px 22px; background:#fff; border-radius:12px; border-left:4px solid var(--lavender); }
  .body blockquote p{ font-size:16.5px; } .body blockquote cite{ display:block; margin-top:8px; font-style:normal; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:12px; text-transform:uppercase; color:var(--pink); }
  .body img{ width:100%; height:auto; border-radius:14px; margin:20px 0; }
  .body .note{ background:#fff7d6; border-radius:10px; padding:12px 16px; font-size:15px; }
  .svc-cta{ display:flex; align-items:center; gap:18px; margin:44px 0 10px; padding:22px; border-radius:16px; background:var(--hbg); color:var(--hfg); text-decoration:none; transition:transform .35s cubic-bezier(.22,1,.36,1), box-shadow .35s ease; }
  .svc-cta:hover{ transform:translateY(-3px); box-shadow:0 16px 34px rgba(0,0,0,.14); }
  .svc-cta img{ width:56px; height:56px; object-fit:contain; flex:none; }
  .svc-cta small{ display:block; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; opacity:.85; }
  .svc-cta b{ font-family:'Arian LT Heavy', sans-serif; text-transform:uppercase; font-size:17px; }
  .byline{ display:flex; gap:14px; align-items:center; margin:30px 0 0; padding-top:24px; border-top:1px solid rgba(0,0,0,.1); font-size:15px; }
  .byline img{ width:56px; height:56px; border-radius:50%; object-fit:cover; background:#ddd; }
  .posts{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }
  .pcard{ background:#fff; border-radius:16px; overflow:hidden; text-decoration:none; color:var(--ink); display:flex; flex-direction:column; box-shadow:0 10px 26px rgba(0,0,0,.06); transition:transform .4s cubic-bezier(.22,1,.36,1), box-shadow .4s ease; }
  .pcard:hover{ transform:translateY(-4px); box-shadow:0 20px 40px rgba(245,17,83,.18); }
  .pcard img{ width:100%; height:auto; aspect-ratio:16/10; object-fit:cover; }
  .pcard .b{ padding:18px 20px 22px; display:flex; flex-direction:column; gap:8px; flex:1; }
  .pcard .tag{ align-self:flex-start; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; border-radius:20px; padding:3px 10px; }
  .pcard h3{ font-size:16px; margin:0; } .pcard p{ font-size:15px; color:#444; }
  .pcard time{ margin-top:auto; font-family:'JetBrains Mono', ui-monospace, monospace; font-size:11.5px; color:#777; text-transform:uppercase; }
  .t-branding-logo-design{ background:var(--pink); color:#fff; } .t-web-design{ background:var(--lavender); color:var(--ink); }
  .t-video-photo-production{ background:var(--magenta); color:#fff; } .t-social-media-marketing{ background:var(--lime); color:var(--ink); }
"""

def page(title, desc, canonical, ogimg, ldblocks, body, hero_vars, og_type="website", extra_head="", extra_css=""):
    gtag, style, hdr, foot, js = chrome()
    ld = "".join('<script type="application/ld+json">\n' + json.dumps(b, ensure_ascii=False) + "\n</script>\n" for b in ldblocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
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

def load_posts():
    posts = []
    d = P("_blog", "posts")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".post"): continue
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
        if not m: sys.exit(f"{fn}: missing metadata comment")
        meta = json.loads(m.group(1)); meta["body"] = m.group(2).strip()
        for k in ("title", "seo_title", "description", "slug", "date", "service"):
            if not meta.get(k): sys.exit(f"{fn}: missing '{k}'")
        if meta["service"] not in SERVICES: sys.exit(f"{fn}: unknown service {meta['service']}")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["slug"]): sys.exit(f"{fn}: bad slug")
        if meta.get("draft"): continue
        meta.setdefault("updated", meta["date"]); meta.setdefault("tags", []); meta.setdefault("summary", []); meta.setdefault("faq", [])
        meta.setdefault("image", "assets/img/og-image.jpg"); meta.setdefault("image_alt", meta["title"])
        text = re.sub(r"<[^>]+>", " ", meta["body"]); meta["words"] = len(text.split())
        meta["mins"] = max(1, round(meta["words"] / 230))
        posts.append(meta)
    slugs = [p["slug"] for p in posts]
    if len(slugs) != len(set(slugs)): sys.exit("duplicate slug")
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
    related = [q for q in posts if q is not p and q["service"] == p["service"]][:3] or [q for q in posts if q is not p][:3]
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "@id": url + "#post", "headline": p["title"], "description": p["description"],
         "url": url, "mainEntityOfPage": url, "datePublished": p["date"], "dateModified": p["updated"], "inLanguage": "en-US",
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
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
        faq_html = '<section class="faq"><h2>Frequently asked questions</h2>' + "".join(
            f'<details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(p["faq"])) + "</section>"
    tldr = ("<aside class=\"tldr\"><strong>Quick answer</strong><ul>" + "".join(f"<li>{esc(x)}</li>" for x in p["summary"]) + "</ul></aside>") if p["summary"] else ""
    upd = f' · Updated <time datetime="{p["updated"]}">{nice(p["updated"])}</time>' if p["updated"] != p["date"] else ""
    body = f"""<section class="post-hero">
  <div class="in">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / <span aria-current="page">{esc(s['name'])}</span></nav>
    <h1>{esc(p['title'])}</h1>
    <div class="meta"><span>By <a href="/#about">Vincent King</a></span><span><time datetime="{p['date']}">{nice(p['date'])}</time>{upd}</span><span>{p['mins']} min read</span></div>
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
  <div class="byline"><img src="/assets/img/about-portrait.webp" alt="Vincent King" width="56" height="56" loading="lazy"><div><b>Vincent King</b> is the founder of DYAD Marketects, an Albuquerque branding, web design and marketing studio. <a href="/#about">More about Vince</a></div></div>
</article>

{related_html}
<section class="blk cta"><div class="wrap">
  <h2>Let&rsquo;s grow your <span class="script">brand.</span></h2>
  <p>Tell us about your project. We&rsquo;ll usually be in touch within 1 to 2 business days.</p>
  <a class="btn light" href="/#contact">Book a call</a>
</div></section>
</main>"""
    out = page(p["seo_title"], p["description"], url, img, ld, body, vars_for(p["service"]), og_type="article",
               extra_head=f'<meta property="article:published_time" content="{p["date"]}">\n<meta property="article:modified_time" content="{p["updated"]}">\n<meta property="article:author" content="Vincent King">\n')
    open(P("blog", p["slug"] + ".html"), "w", encoding="utf-8").write(out)

def build_index(posts):
    url = SITE + "/blog/"
    ld = [{"@context": "https://schema.org", "@type": "Blog", "@id": url + "#blog", "name": "DYAD Marketects Blog", "url": url,
           "description": "Branding, web design, video and social media advice for Albuquerque and New Mexico businesses.",
           "publisher": ORG, "inLanguage": "en-US",
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}", "datePublished": p["date"]} for p in posts[:50]]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]}]
    filters = '<div class="bfil" role="group" aria-label="Filter posts"><button class="on" data-f="all">All</button>' + "".join(
        f'<button data-f="{k}">{esc(v["name"])}</button>' for k, v in SERVICES.items()) + "</div>"
    body = f"""<section class="hero">
  <div class="hero-in" style="grid-template-columns:1fr">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span aria-current="page">Blog</span></nav>
      <h1>The DYAD <span class="script">Blog</span></h1>
      <p class="lead">Straight answers on branding, websites, video and social media for Albuquerque and New Mexico businesses, from the DYAD Marketects studio.</p>
    </div>
  </div>
</section>
<main>
<section class="blk"><div class="wrap">
  {filters}
  <div class="posts" id="posts">{''.join(card(p).replace('<a class="pcard"', f'<a class="pcard" data-s="{p["service"]}"', 1) for p in posts) or '<p>New posts are on the way.</p>'}</div>
</div></section>
<section class="blk cta"><div class="wrap">
  <h2>Let&rsquo;s grow your <span class="script">brand.</span></h2>
  <p>Tell us about your project. We&rsquo;ll usually be in touch within 1 to 2 business days.</p>
  <a class="btn light" href="/#contact">Book a call</a>
</div></section>
</main>
<style>
  .bfil{{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px; }}
  .bfil button{{ font-family:'Arian LT Demi', sans-serif; font-size:12px; letter-spacing:.04em; text-transform:uppercase; border:1.5px solid var(--ink); background:transparent; border-radius:30px; padding:9px 16px; cursor:pointer; }}
  .bfil button.on, .bfil button:hover{{ background:var(--ink); color:#fff; }}
</style>
<script>
document.querySelectorAll('.bfil button').forEach(function(b){{ b.addEventListener('click',function(){{
  document.querySelectorAll('.bfil button').forEach(function(x){{ x.classList.toggle('on', x===b); }});
  document.querySelectorAll('#posts .pcard').forEach(function(c){{ c.style.display = (b.dataset.f==='all' || c.dataset.s===b.dataset.f) ? '' : 'none'; }});
}}); }});
</script>"""
    out = page("Blog | Branding & Marketing Tips for Albuquerque | DYAD Marketects",
               "Branding, web design, video and social media advice for Albuquerque and New Mexico businesses from DYAD Marketects (DYAD Grow).",
               url, SITE + "/assets/img/og-image.jpg?v=2", ld, body, "--hbg:var(--pink); --hfg:#fff; --hacc:var(--lime);",
               extra_css="  .hero{ background:var(--pink); color:#fff; } .hero h1 .script{ color:var(--lime); }\n")
    open(P("blog", "index.html"), "w", encoding="utf-8").write(out)

def build_feed(posts):
    now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
    items = "".join(f"""
  <item>
    <title>{esc(p['title'])}</title>
    <link>{SITE}/blog/{p['slug']}</link>
    <guid isPermaLink="true">{SITE}/blog/{p['slug']}</guid>
    <pubDate>{format_datetime(datetime.datetime.fromisoformat(p['date'] + 'T08:00:00-06:00'))}</pubDate>
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
    sm = re.sub(r"\s*<url>\s*<loc>https://dyadgrow\.com/blog/[^<]*</loc>.*?</url>", "", sm, flags=re.S)
    newest = posts[0]["updated"] if posts else datetime.date.today().isoformat()
    add = f"  <url>\n    <loc>{SITE}/blog/</loc>\n    <lastmod>{max(p['updated'] for p in posts) if posts else newest}</lastmod>\n  </url>\n"
    add += "".join(f"  <url>\n    <loc>{SITE}/blog/{p['slug']}</loc>\n    <lastmod>{p['updated']}</lastmod>\n  </url>\n" for p in posts)
    sm = sm.replace("</urlset>", add + "</urlset>")
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
                     + '</div>\n  <p style="margin-top:18px"><a href="/blog/" style="color:var(--pink);font-weight:600">See all posts &rarr;</a></p>\n</div></section>\n')
        start, end = "<!--blog:latest-->", "<!--/blog:latest-->"
        if start not in t:
            anchor = '<section class="blk"><div class="wrap">\n  <div class="kicker">More services</div>'
            if anchor not in t: print("warn: no anchor in", svc); continue
            t = t.replace(anchor, start + end + "\n" + anchor, 1)
        t = re.sub(re.escape(start) + ".*?" + re.escape(end), start + "\n" + block + end, t, flags=re.S)
        if mine and ".pcard{" not in t:
            css = BLOG_CSS[BLOG_CSS.index("  .posts{"):]
            t = t.replace("</style>", css + "</style>", 1)
        open(f, "w", encoding="utf-8").write(t)

if __name__ == "__main__":
    os.makedirs(P("blog"), exist_ok=True)
    posts = load_posts()
    keep = {p["slug"] + ".html" for p in posts} | {"index.html"}
    for fn in os.listdir(P("blog")):
        if fn.endswith(".html") and fn not in keep: os.remove(P("blog", fn))
    for p in posts: build_post(p, posts)
    build_index(posts); build_feed(posts); build_sitemap(posts); build_service_blocks(posts)
    print(f"built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))
