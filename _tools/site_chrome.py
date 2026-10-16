#!/usr/bin/env python3
"""
Shared site chrome: keeps every page's President's Club tab, social bar and footer identical to the homepage.

The homepage (index.html) is the single source of truth. This script:
  1. copies the CSS for those pieces into assets/css/site-chrome.css and their script into assets/js/site-chrome.js
  2. copies the homepage markup (President's Club + social bar, and the footer) into every other .html page,
     rewriting homepage-relative links (#about, privacy.html, assets/...) so they work from any folder
  3. adds the stylesheet/script tags to each page's <head> if missing

Run it after any change to the homepage chrome and after building the blog:
    python3 _tools/blog.py && python3 _tools/site_chrome.py
The deploy workflow runs both on every push, so new pages get the chrome automatically.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
SKIP_DIRS = {".git", ".github", "_blog", "_tools", "assets", "images", "immerse", "videos", "node_modules"}

home = open(P("index.html"), encoding="utf-8").read()

def between(text, start, end, include_end=True):
    i = text.index(start); j = text.index(end, i)
    return text[i:j + (len(end) if include_end else 0)]

# ---------- 1. CSS + JS ----------
style = home[home.index("<style>"):home.index("</style>")]
side_social = between(style, "  .side-tab{ position:fixed;", "  /* ---------- HERO ---------- */", False)
pc_css = between(style, "  /* ===== President's Club slide-out ===== */", "  /* ===== About: You Are the DYAD Movement ===== */", False)
foot_css = between(style, "  footer{ background:var(--ink); color:#fff;", "  @media (max-width:480px){ .footer-grid", False)
foot_css += re.search(r"  @media \(max-width:480px\)\{ \.footer-grid[^\n]*\n", style).group(0)
foot_css += "  .footer-grid p{ font-size:15px; color:#d0ccc2; }\n"
foot_css = foot_css.replace("  footer{", "  footer.site-footer{")

css = """/* Shared site chrome (President's Club tab, social bar, footer).
   Generated from the homepage by _tools/site_chrome.py. Do not edit by hand: edit index.html and rerun the script. */
.pc, .social-col, .site-footer{
  --ink:#0a0a0a; --paper:#eeeeee; --pink:#f51153; --lime:#b6fd29; --lavender:#b697fc; --magenta:#bd6ec9;
  --line:rgba(0,0,0,0.1); --mono:'JetBrains Mono', ui-monospace, monospace; --display-heavy:'Arian LT Heavy', sans-serif;
  --display-demi:'Arian LT Demi', sans-serif; --heavy:'Mont Heavy', sans-serif; --body:'Mont Light', sans-serif;
}
.pc *, .social-col *, .site-footer *{ box-sizing:border-box; }
.pc .kicker{ display:flex; align-items:center; gap:8px; font-family:var(--mono); font-size:12px; letter-spacing:.12em; color:var(--pink); text-transform:uppercase; }
.pc .emph-word{ font-family:'Hyperwave One', sans-serif; text-transform:none; color:var(--pink); display:inline-block; font-size:2em !important; line-height:.8; }
.pc p, .pc h3{ margin:0; -webkit-text-stroke:0; } .pc-panel{ font-family:var(--body); font-weight:300; text-align:left; }
.side-tab{ font-family:inherit; }
.site-footer{ font-family:var(--body); font-weight:300; text-align:left; font-size:16px; line-height:normal; }
.site-footer a{ color:inherit; margin:0; text-decoration:none; }
.site-footer .footer-col a{ color:#d8d5cd; } .site-footer .footer-col a:hover{ color:var(--pink); }
.site-footer h6{ margin:0 0 16px; font-weight:400; }
.site-footer p{ -webkit-text-stroke:0; }
@media (max-width:700px){ .site-footer{ padding-bottom:90px !important; } }
""" + side_social + pc_css + foot_css
for cls in (".footer-grid", ".footer-col", ".footer-logo-img", ".footer-bottom"):
    css = css.replace(cls, ".site-footer " + cls)
css = css.replace(".site-footer .site-footer", ".site-footer")
css = "\n".join(l[2:] if l.startswith("  ") else l for l in css.split("\n"))
os.makedirs(P("assets", "css"), exist_ok=True); os.makedirs(P("assets", "js"), exist_ok=True)
open(P("assets", "css", "site-chrome.css"), "w", encoding="utf-8").write(css)
js_i = home.index("/* ===== President's Club slide-out: hover"); js_j = home.index("})();", js_i) + 5
open(P("assets", "js", "site-chrome.js"), "w", encoding="utf-8").write(
    "/* Shared site chrome behavior (President's Club slide-out). Generated from the homepage by _tools/site_chrome.py. */\n" + home[js_i:js_j] + "\n")

# ---------- 2. markup ----------
def absolutize(html):
    html = re.sub(r'(href|src)="#', r'\1="/#', html)
    html = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)([^"]+)"', r'\1="/\2"', html)
    html = re.sub(r'href="/(privacy|terms)\.html"', r'href="/\1.html"', html)
    return html

side = between(home, '<div class="pc" id="presClub">', '<!-- ============ HERO')
side = side[:side.rindex("</div>") + 6]          # President's Club + social bar
footer = between(home, "<footer>", "</footer>").replace("<footer>", '<footer class="site-footer">', 1)
side, footer = absolutize(side), absolutize(footer)
# the homepage's "Cookie settings" button reopens its banner; on other pages it links to the choice on the privacy page
footer = footer.replace('<button type="button" class="cookie-settings-link" id="cookieSettings">Cookie settings</button>',
                        '<a href="/privacy.html#cookie-choice" style="text-decoration:underline;">Cookie settings</a>')
SIDE = "<!--chrome:side-->\n" + side + "\n<!--/chrome:side-->"
HEAD = '<link rel="stylesheet" href="/assets/css/site-chrome.css">\n<script src="/assets/js/site-chrome.js" defer></script>\n'

def pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in files:
            if f.endswith(".html") and not (d == ROOT and f == "index.html"):
                yield os.path.join(d, f)

n = 0
for f in pages():
    t = open(f, encoding="utf-8").read()
    if "<body" not in t or "</head>" not in t: continue
    o = t
    if "/assets/css/site-chrome.css" not in t:
        t = t.replace("</head>", HEAD + "</head>", 1)
    if "<!--chrome:side-->" in t:
        t = re.sub(r"<!--chrome:side-->.*?<!--/chrome:side-->", lambda m: SIDE, t, flags=re.S)
    else:
        t = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + SIDE, t, count=1)
    if re.search(r"<footer[\s>]", t):
        t = re.sub(r"<footer[\s>].*?</footer>", lambda m: footer, t, count=1, flags=re.S)
    else:
        t = t.replace("</body>", footer + "\n</body>", 1)
    if t != o:
        open(f, "w", encoding="utf-8").write(t); n += 1
print(f"site chrome synced to {n} page(s)")
