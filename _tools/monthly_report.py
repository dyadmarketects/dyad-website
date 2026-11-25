#!/usr/bin/env python3
"""
Monthly SEO report for dyadgrow.com (DYAD Marketects), built from free Google APIs.

  python3 _tools/monthly_report.py fetch  [--month YYYY-MM]  > data.json   # pulls GA4 + Search Console
  python3 _tools/monthly_report.py render data.json --out report.pdf       # builds the PDF

Run monthly by .github/workflows/monthly-report.yml (the PDF is a download on the workflow run).

Sources (all read only, all free):
  - Google Analytics 4 Data API (property GA4_PROPERTY, default 557555891)
  - Google Search Console API (property GSC_PROPERTY, default https://dyadgrow.com/)
  - Google Business Profile: numbers typed into gbp/YYYY-MM.json from the Business Profile
    Performance screen into _seo/gbp/YYYY-MM.json (the Business Profile API needs Google's approval first).
    See _seo/gbp/README.md.
  - SEO work log: _seo/changes.md and _blog/posts/.
  - Your own commentary: _seo/notes/YYYY-MM.md (optional, printed as written).

Rules this script follows: every number in the PDF comes straight from an API response or from a
file you wrote. Nothing is estimated. Where data is missing, the PDF says so.

Auth: GOOGLE_SERVICE_ACCOUNT_JSON (falls back to GSC_SERVICE_ACCOUNT_JSON) = the service account JSON key.
The service account needs Viewer on the GA4 property and Restricted access in Search Console. If GA4 access
is missing, the Search Console pages are still built and the GA4 pages say why they are empty.
"""
import argparse, base64, calendar, datetime, html, json, os, re, sys
from urllib.parse import quote

GA4_PROPERTY = os.environ.get("GA4_PROPERTY", "557555891")
GSC_PROPERTY = os.environ.get("GSC_PROPERTY", "https://dyadgrow.com/")
# GA4 sections are limited to this country (GA4's English country name). Empty = every country.
GA4_COUNTRY = os.environ.get("GA4_COUNTRY", "United States")
# Search Console country filter (ISO 3166-1 alpha-3, lower case). Empty = every country.
GSC_COUNTRY = os.environ.get("GSC_COUNTRY", "usa")
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE_REPO_DIR", os.path.dirname(HERE))
GBP_DIR = os.environ.get("GBP_DIR", os.path.join(SITE, "_seo", "gbp"))
NOTES_DIR = os.environ.get("NOTES_DIR", os.path.join(SITE, "_seo", "notes"))
TZ_NAME = "America/Denver"

AI_SOURCES = r"chatgpt|openai|perplexity|claude\.ai|anthropic|gemini\.google|bard\.google|copilot|deepseek|you\.com|phind|meta\.ai|grok|mistral"
LEAD_EVENTS = [  # (GA4 event name, label) as sent by the site's own tracking code in index.html
    ("generate_lead", "Contact form submissions"),
    ("cta_click", "Clicks on links to the contact form (Book a call, Start my project, nav, footer)"),
    ("click_email", "Email link clicks"),
    ("click_to_call", "Phone link clicks"),
]
SOCIAL = [  # outbound link hosts counted as social / review / map clicks (GA4 enhanced measurement "click")
    ("instagram.com", "Instagram"), ("linkedin.com", "LinkedIn"), ("facebook.com", "Facebook"),
    ("tiktok.com", "TikTok"), ("youtube.com", "YouTube"), ("x.com", "X"), ("twitter.com", "X"),
    ("g.page", "Google review link"), ("maps.google.com", "Google Maps"), ("maps.app.goo.gl", "Google Maps"),
]
SOCIAL_EXCLUDE = ("about.instagram.com",)  # help/press pages cited in blog posts, not DYAD's profiles


# ----------------------------------------------------------------------------------------- dates
def month_bounds(ym):
    y, m = map(int, ym.split("-"))
    last = calendar.monthrange(y, m)[1]
    return datetime.date(y, m, 1), datetime.date(y, m, last)


def prev_month(ym):
    y, m = map(int, ym.split("-"))
    return "%04d-%02d" % ((y, m - 1) if m > 1 else (y - 1, 12))


def default_month():
    try:
        from zoneinfo import ZoneInfo
        today = datetime.datetime.now(ZoneInfo(TZ_NAME)).date()
    except Exception:
        today = datetime.date.today()
    return prev_month("%04d-%02d" % (today.year, today.month))


def month_name(ym):
    y, m = map(int, ym.split("-"))
    return "%s %d" % (calendar.month_name[m], y)


# ----------------------------------------------------------------------------------------- fetch
def session():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise SystemExit("Missing the GOOGLE_SERVICE_ACCOUNT_JSON secret (service account JSON key).")
    creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=[
        "https://www.googleapis.com/auth/analytics.readonly",
        "https://www.googleapis.com/auth/webmasters.readonly"])
    return AuthorizedSession(creds)


class GA4Error(Exception):
    pass


def f_str(field, value, match="EXACT"):
    return {"filter": {"fieldName": field, "stringFilter": {"matchType": match, "value": value, "caseSensitive": False}}}


def f_and(*exprs):
    exprs = [e for e in exprs if e]
    if not exprs:
        return None
    return exprs[0] if len(exprs) == 1 else {"andGroup": {"expressions": exprs}}


def ga(s, start, end, dims, mets, filt=None, limit=10000):
    """One GA4 runReport call. Returns a list of {dimension: value, metric: number}."""
    body = {"dateRanges": [{"startDate": str(start), "endDate": str(end)}],
            "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets],
            "limit": limit, "keepEmptyRows": False}
    country = f_str("country", GA4_COUNTRY) if GA4_COUNTRY else None
    f = f_and(country, filt)
    if f:
        body["dimensionFilter"] = f
    r = s.post("https://analyticsdata.googleapis.com/v1beta/properties/%s:runReport" % GA4_PROPERTY, json=body)
    if r.status_code != 200:
        try:
            msg = r.json()["error"]["message"]
        except Exception:
            msg = r.text[:400]
        raise GA4Error("GA4 API error %s: %s" % (r.status_code, msg))
    j = r.json()
    if len(j.get("rows", [])) < int(j.get("rowCount", 0) or 0):
        print("warning: GA4 returned %d of %s rows for %s" % (len(j["rows"]), j["rowCount"], dims), file=sys.stderr)
    dn = [h["name"] for h in j.get("dimensionHeaders", [])]
    mn = [h["name"] for h in j.get("metricHeaders", [])]
    out = []
    for row in j.get("rows", []):
        d = {k: v["value"] for k, v in zip(dn, row.get("dimensionValues", []))}
        for k, v in zip(mn, row.get("metricValues", [])):
            d[k] = float(v["value"])
        out.append(d)
    if not dims:  # totals: always return one row so missing data reads as zero, not as an error
        out = out or [{m: 0.0 for m in mets}]
    return out


def gsc(s, start, end, dims, limit=25000):
    body = {"startDate": str(start), "endDate": str(end), "dimensions": dims, "rowLimit": limit, "dataState": "final"}
    if GSC_COUNTRY:
        body["dimensionFilterGroups"] = [{"filters": [{"dimension": "country", "operator": "equals", "expression": GSC_COUNTRY}]}]
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query" % quote(GSC_PROPERTY, safe="")
    r = s.post(url, json=body)
    if r.status_code != 200:
        raise SystemExit("Search Console API error %s: %s" % (r.status_code, r.text[:500]))
    rows = []
    for x in r.json().get("rows", []):
        d = dict(zip(dims, x.get("keys", [])))
        d.update({k: x[k] for k in ("clicks", "impressions", "ctr", "position")})
        rows.append(d)
    if not dims:
        rows = rows or [{"clicks": 0, "impressions": 0, "ctr": 0, "position": None}]
    return rows


KPI = ["newUsers", "sessions", "screenPageViews", "userEngagementDuration", "activeUsers", "engagedSessions", "keyEvents"]
ORGANIC = f_str("sessionDefaultChannelGroup", "Organic Search")


def fetch_period(s, ym):
    a, b = month_bounds(ym)
    p = {"month": ym, "start": str(a), "end": str(b)}
    try:
        fetch_ga4(s, a, b, p)
    except GA4Error as e:
        p["ga4_error"] = str(e)
        print("warning: %s" % e, file=sys.stderr)
    p["gsc_totals"] = gsc(s, a, b, [])[0]
    p["gsc_daily"] = gsc(s, a, b, ["date"])
    p["gsc_queries"] = gsc(s, a, b, ["query"])
    p["gsc_pages"] = gsc(s, a, b, ["page"])
    return p


def fetch_ga4(s, a, b, p):
    p["all_totals"] = ga(s, a, b, [], KPI)[0]
    p["org_totals"] = ga(s, a, b, [], KPI, ORGANIC)[0]
    p["all_daily"] = ga(s, a, b, ["date"], ["sessions"])
    p["org_daily"] = ga(s, a, b, ["date"], ["sessions"], ORGANIC)
    p["org_source"] = ga(s, a, b, ["sessionSourceMedium"], ["sessions"], ORGANIC)
    p["org_pages"] = ga(s, a, b, ["pagePath"], ["newUsers", "sessions", "screenPageViews", "userEngagementDuration"], ORGANIC)
    p["org_devices"] = ga(s, a, b, ["deviceCategory"], ["newUsers", "sessions", "screenPageViews", "userEngagementDuration", "activeUsers"], ORGANIC)
    p["all_sources"] = ga(s, a, b, ["sessionSourceMedium"], ["newUsers", "sessions", "screenPageViews", "userEngagementDuration"])
    p["all_channels"] = ga(s, a, b, ["sessionDefaultChannelGroup"], ["newUsers", "sessions", "screenPageViews", "userEngagementDuration", "activeUsers"])
    p["events_all"] = ga(s, a, b, ["eventName"], ["eventCount", "keyEvents"])
    p["events_org"] = ga(s, a, b, ["eventName"], ["eventCount", "keyEvents"], ORGANIC)
    p["lead_by_page"] = ga(s, a, b, ["eventName", "pagePath"], ["eventCount"],
                           f_str("eventName", "|".join(e for e, _ in LEAD_EVENTS), "FULL_REGEXP"))
    p["clicks_all"] = ga(s, a, b, ["linkUrl"], ["eventCount"], f_str("eventName", "click"))
    p["clicks_org"] = ga(s, a, b, ["linkUrl"], ["eventCount"], f_and(f_str("eventName", "click"), ORGANIC))
    p["ai"] = ga(s, a, b, ["sessionSource", "landingPage"], ["screenPageViews", "sessions", "engagedSessions", "keyEvents"],
                 f_str("sessionSource", AI_SOURCES, "PARTIAL_REGEXP"))


def cmd_fetch(args):
    ym = args.month or default_month()
    s = session()
    data = {"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "config": {"ga4_property": GA4_PROPERTY, "gsc_property": GSC_PROPERTY,
                       "ga4_country": GA4_COUNTRY, "gsc_country": GSC_COUNTRY},
            "cur": fetch_period(s, ym), "prev": fetch_period(s, prev_month(ym))}
    json.dump(data, sys.stdout, indent=1)


# ----------------------------------------------------------------------------------------- local files
def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return None


def load_gbp(ym):
    t = read(os.path.join(GBP_DIR, ym + ".json"))
    return json.loads(t) if t else None


def tracked_keywords():
    t = read(os.path.join(SITE, "_seo", "keywords.md")) or ""
    out = []
    for line in t.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(c) == 3 and c[0] and c[0] != "Search" and not c[0].startswith("---"):
            out.append((c[0].lower(), c[1], c[2]))
    return out


def seo_changes(ym):
    t = read(os.path.join(SITE, "_seo", "changes.md")) or ""
    rows = []
    for line in t.splitlines():
        c = [x.strip().replace("\\|", "|") for x in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if line.startswith("|") and len(c) >= 5 and c[0].startswith(ym):
            rows.append({"date": c[0], "page": c[1], "change": c[2], "why": c[4]})
    return rows


def blog_posts(ym):
    d = os.path.join(SITE, "_blog", "posts")
    out = []
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return out
    for n in names:
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.post$", n)
        if m and m.group(1).startswith(ym):
            t = read(os.path.join(d, n)) or ""
            title = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', t)
            out.append({"date": m.group(1), "slug": m.group(2),
                        "title": json.loads('"%s"' % title.group(1)) if title else m.group(2)})
    return out


def notes(ym):
    return read(os.path.join(NOTES_DIR, ym + ".md"))


# ----------------------------------------------------------------------------------------- math + formatting
def num(x):
    return 0.0 if x is None else float(x)


def pct(cur, prev):
    """Percent change, or None when there is no previous value to compare with."""
    cur, prev = num(cur), num(prev)
    if prev == 0:
        return None
    return (cur - prev) / prev * 100


def fmt_int(x):
    return "{:,}".format(int(round(num(x))))


def fmt_dur(sec):
    sec = int(round(num(sec)))
    return "%02d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


def ratio(a, b):
    return num(a) / num(b) if num(b) else 0.0


def esc(s):
    return html.escape(str(s))


def chip(cur, prev, invert=False, as_points=False):
    """Change badge. invert=True for metrics where lower is better (search position)."""
    if prev is None or (not as_points and num(prev) == 0 and num(cur) == 0):
        return '<span class="chip flat">0%</span>' if prev is not None else '<span class="chip flat">n/a</span>'
    if as_points:
        d = num(cur) - num(prev)
        good = d < 0 if invert else d > 0
        if abs(d) < 0.05:
            return '<span class="chip flat">0</span>'
        return '<span class="chip %s">%s%.1f</span>' % ("up" if good else "down", "+" if d > 0 else "", d)
    p = pct(cur, prev)
    if p is None:
        return '<span class="chip flat">was 0</span>'
    if abs(p) < 0.005:
        return '<span class="chip flat">0%</span>'
    good = p < 0 if invert else p > 0
    arrow = "&#9650;" if p > 0 else "&#9660;"
    return '<span class="chip %s">%s %s%%</span>' % ("up" if good else "down", arrow, ("%.0f" if abs(p) >= 10 else "%.1f") % abs(p))


def index(rows, key):
    return {r[key]: r for r in rows}


def diff_word(cur, prev, unit="", decimals=0):
    d = num(cur) - num(prev)
    f = ("{:,.%df}" % decimals)
    if abs(d) < (0.5 if decimals == 0 else 0.05):
        return "no change"
    return ("+" if d > 0 else "-") + f.format(abs(d)) + unit


# ----------------------------------------------------------------------------------------- charts (inline SVG)
PINK, LIME, LAV, MAG, INK, PAPER = "#f51153", "#b6fd29", "#b697fc", "#bd6ec9", "#0a0a0a", "#eeeeee"
SERIES = [PINK, LAV, LIME, MAG, "#5a5a5a", "#f7a1b8", "#d9c9fe"]


def line_chart(cur_pts, prev_pts, labels, w=520, h=190):
    """cur_pts/prev_pts: values per day of month (prev aligned by day number)."""
    pad_l, pad_b, pad_t, pad_r = 30, 26, 10, 8
    vmax = max([1] + cur_pts + prev_pts)
    step = max(1, (vmax + 4) // 5)
    top = step * 5
    n = max(len(cur_pts), len(prev_pts), 2)
    X = lambda i: pad_l + i * (w - pad_l - pad_r) / (n - 1)
    Y = lambda v: pad_t + (h - pad_t - pad_b) * (1 - v / top)
    g = []
    for k in range(6):
        y = Y(k * step)
        g.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e3e3e3"/><text x="%d" y="%.1f" class="ax" text-anchor="end">%d</text>' % (pad_l, y, w - pad_r, y, pad_l - 5, y + 3, k * step))
    for i, lab in enumerate(labels):
        if i % 4 == 0:
            g.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>' % (X(i), h - 8, esc(lab)))

    def path(pts, color, width, dash=""):
        if not pts:
            return ""
        d = " ".join(("M" if i == 0 else "L") + "%.1f,%.1f" % (X(i), Y(v)) for i, v in enumerate(pts))
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" %s/>' % (d, color, width, dash)
    g.append(path(prev_pts, LAV, 1.6, 'stroke-dasharray="4 3"'))
    g.append(path(cur_pts, PINK, 2.2))
    return '<svg viewBox="0 0 %d %d" width="100%%">%s</svg>' % (w, h, "".join(g))


def donut(parts, total_label, sub, total=None):
    """parts: [(label, value)]. When total is given and the parts add up to less, the rest is shown as "Other"."""
    import math
    if total is not None and total - sum(v for _, v in parts) > 0.5:
        parts = list(parts) + [("Other", total - sum(v for _, v in parts))]
    tot = sum(v for _, v in parts) or 1
    r, cx, cy, sw = 62, 80, 80, 26
    a0, segs = -math.pi / 2, []
    for i, (lab, v) in enumerate(parts):
        a1 = a0 + 2 * math.pi * v / tot
        if v > 0:
            if v == tot:
                segs.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d"/>' % (cx, cy, r, SERIES[i % len(SERIES)], sw))
            else:
                large = 1 if a1 - a0 > math.pi else 0
                segs.append('<path d="M%.2f,%.2f A%d,%d 0 %d 1 %.2f,%.2f" fill="none" stroke="%s" stroke-width="%d"/>' % (
                    cx + r * math.cos(a0), cy + r * math.sin(a0), r, r, large, cx + r * math.cos(a1), cy + r * math.sin(a1), SERIES[i % len(SERIES)], sw))
        a0 = a1
    legend = "".join('<div class="lg"><i style="background:%s"></i><span>%s</span><b>%s</b></div>' % (SERIES[i % len(SERIES)], esc(l), fmt_int(v)) for i, (l, v) in enumerate(parts))
    return ('<div class="donut"><svg viewBox="0 0 160 160" width="150" height="150">%s'
            '<text x="80" y="80" text-anchor="middle" class="dn">%s</text><text x="80" y="98" text-anchor="middle" class="ds">%s</text></svg>'
            '<div class="legend">%s</div></div>') % ("".join(segs), esc(total_label), esc(sub), legend)


def hbars(items, maxv=None):
    maxv = maxv or max([1] + [v for _, v in items])
    return "".join('<div class="hb"><div class="hbl"><span>%s</span><b>%s</b></div><div class="hbt"><i style="width:%.1f%%"></i></div></div>' % (
        esc(l), fmt_int(v), 100 * v / maxv) for l, v in items)


# ----------------------------------------------------------------------------------------- building blocks
def kpi(label, value, cur, prev, invert=False, as_points=False):
    return '<div class="kpi"><div class="kl">%s %s</div><div class="kv">%s</div></div>' % (esc(label), chip(cur, prev, invert, as_points), value)


def table(head, rows, cls=""):
    th = "".join("<th>%s</th>" % h for h in head)
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    return '<table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cls, th, tr)


def cell(value, cur, prev, invert=False, as_points=False):
    return '%s<br>%s' % (value, chip(cur, prev, invert, as_points))


def daily_series(rows, ym, key, metric):
    a, b = month_bounds(ym)
    # GA4 dates look like 20261001, Search Console dates like 2026-10-01: compare without dashes
    by = {r[key].replace("-", ""): num(r[metric]) for r in rows}
    out, d = [], a
    while d <= b:
        out.append(by.get(d.strftime("%Y%m%d"), 0.0))
        d += datetime.timedelta(days=1)
    return out


def day_labels(ym):
    a, b = month_bounds(ym)
    return ["%d %s" % (i, calendar.month_abbr[a.month]) for i in range(1, b.day + 1)]


def classify_click(url):
    """Label an outbound link by its host (exact host or a subdomain of it), so jerkyfixx.com is not X."""
    from urllib.parse import urlparse
    u = (url or "").strip().lower()
    host = urlparse(u if "://" in u else "https://" + u).hostname or ""
    if host in SOCIAL_EXCLUDE:
        return None
    for dom, label in SOCIAL:
        if host == dom or host.endswith("." + dom):
            return label
    if (host == "google.com" or host.endswith(".google.com")) and urlparse(u if "://" in u else "https://" + u).path.startswith("/maps"):
        return "Google Maps"
    return None


def conversions(p, scope):
    """Counts per conversion action for one period. scope 'all' or 'org'."""
    ev = index(p["events_" + scope], "eventName")
    out = {}
    for name, label in LEAD_EVENTS:
        out[label] = num(ev.get(name, {}).get("eventCount"))
    social = {}
    for r in p["clicks_" + scope]:
        lab = classify_click(r.get("linkUrl"))
        if lab:
            social[lab] = social.get(lab, 0) + num(r["eventCount"])
    out["Social, Google review and Google Maps link clicks"] = sum(social.values())
    return out, social, sum(num(r.get("keyEvents")) for r in p["events_" + scope])


def key_event_names(p):
    return sorted([(r["eventName"], num(r["keyEvents"])) for r in p["events_all"] if num(r.get("keyEvents")) > 0], key=lambda x: -x[1])


def gsc_buckets(rows):
    b = {"1-3": set(), "4-10": set(), "11+": set()}
    for r in rows:
        pos = round(num(r["position"]), 1)  # same rounding as the tables
        b["1-3" if pos <= 3 else "4-10" if pos <= 10 else "11+"].add(r["query"])
    return b


def path_of(url):
    p = re.sub(r"^https?://[^/]+", "", url or "") or "/"
    return p


# ----------------------------------------------------------------------------------------- report
def build_html(data):
    C, P = data["cur"], data["prev"]
    ym, pym = C["month"], P["month"]
    cfg = data["config"]
    geo = cfg["ga4_country"] or "all countries"
    sections = []  # (id, title, html)
    ga_err = C.get("ga4_error") or P.get("ga4_error")
    ga_ok = not ga_err
    if not ga_ok:  # keep the Search Console pages; GA4 figures are left empty, never guessed
        for X in (C, P):
            for k in ("all_totals", "org_totals"):
                X.setdefault(k, {m: 0.0 for m in KPI})
            for k in ("all_daily", "org_daily", "org_source", "org_pages", "org_devices", "all_sources", "all_channels",
                      "events_all", "events_org", "lead_by_page", "clicks_all", "clicks_org", "ai"):
                X.setdefault(k, [])
    ga_note = ('<p class="note">Google Analytics data could not be read for this report, so this part is empty. '
               'Google said: %s</p>' % esc((ga_err or "")[:300]))

    # ---------- figures used on several pages
    conv_c, soc_c, key_c = conversions(C, "all")
    conv_p, soc_p, key_p = conversions(P, "all")
    oconv_c, osoc_c, okey_c = conversions(C, "org")
    oconv_p, osoc_p, okey_p = conversions(P, "org")
    tot_conv_c, tot_conv_p = sum(conv_c.values()), sum(conv_p.values())
    tot_oconv_c, tot_oconv_p = sum(oconv_c.values()), sum(oconv_p.values())
    gt_c, gt_p = C["gsc_totals"], P["gsc_totals"]
    ch_c, ch_p = index(C["all_channels"], "sessionDefaultChannelGroup"), index(P["all_channels"], "sessionDefaultChannelGroup")
    at_c, at_p = C["all_totals"], P["all_totals"]
    ot_c, ot_p = C["org_totals"], P["org_totals"]
    ai_c = {"views": sum(num(r["screenPageViews"]) for r in C["ai"]), "sessions": sum(num(r["sessions"]) for r in C["ai"]), "engaged": sum(num(r["engagedSessions"]) for r in C["ai"]), "key": sum(num(r["keyEvents"]) for r in C["ai"])}
    ai_p = {"views": sum(num(r["screenPageViews"]) for r in P["ai"]), "sessions": sum(num(r["sessions"]) for r in P["ai"]), "engaged": sum(num(r["engagedSessions"]) for r in P["ai"]), "key": sum(num(r["keyEvents"]) for r in P["ai"])}
    qb_c, qb_p = gsc_buckets(C["gsc_queries"]), gsc_buckets(P["gsc_queries"])
    q_c, q_p = index(C["gsc_queries"], "query"), index(P["gsc_queries"], "query")
    both = [q for q in q_c if q in q_p]
    improved = sum(1 for q in both if round(num(q_c[q]["position"]), 1) < round(num(q_p[q]["position"]), 1))
    declined = sum(1 for q in both if round(num(q_c[q]["position"]), 1) > round(num(q_p[q]["position"]), 1))
    unchanged = len(both) - improved - declined

    # ---------- 1. overview
    def li(t):
        return "<li>%s</li>" % t

    if ga_ok:
        ov = ['<h3>1. Conversions (GA4, %s)</h3>' % esc(geo)]
        ov.append('<p>Tracked actions in %s, each counted separately (one visitor can trigger several, so they are not added up). In brackets: from organic search visits, and the change vs %s.</p>' % (month_name(ym), month_name(pym)))
        ov.append("<ul>" + "".join(li("<b>%s:</b> %s (organic %s; %s)" % (esc(k), fmt_int(v), fmt_int(oconv_c[k]), diff_word(v, conv_p[k]))) for k, v in conv_c.items()) + "</ul>")
        kn = key_event_names(C)
        ov.append("<p><b>GA4 key events:</b> %s in total, %s from organic search (%s)%s.</p>" % (
            fmt_int(key_c), fmt_int(okey_c), diff_word(key_c, key_p), (": " + ", ".join("%s %s" % (esc(n), fmt_int(v)) for n, v in kn)) if kn else ""))
        if tot_conv_c == 0 and key_c == 0:
            ov.append('<p class="note">GA4 recorded none of these actions this month. The counts come straight from GA4; an action that was not being tracked yet cannot appear here.</p>')
    else:
        ov = ['<h3>1. Conversions (GA4)</h3>', ga_note]

    ov.append('<h3>2. Performance on search results (Search Console%s)</h3>' % (", " + cfg["gsc_country"].upper() if cfg["gsc_country"] else ""))
    if not P["gsc_daily"]:
        ov.append('<p class="note">Search Console returned no data for %s, so every Search Console change in this report is against zero and none of them is a real comparison.%s</p>' % (
            month_name(pym), (" The first day with data in %s is %s." % (month_name(ym), esc(min(r["date"] for r in C["gsc_daily"])))) if C["gsc_daily"] else ""))
    ov.append("<ul>%s%s%s%s</ul>" % (
        li("<b>Clicks:</b> %s &rarr; <b>%s</b> (%s)" % (fmt_int(gt_p["clicks"]), fmt_int(gt_c["clicks"]), diff_word(gt_c["clicks"], gt_p["clicks"]))),
        li("<b>Impressions:</b> %s &rarr; <b>%s</b> (%s)" % (fmt_int(gt_p["impressions"]), fmt_int(gt_c["impressions"]), diff_word(gt_c["impressions"], gt_p["impressions"]))),
        li("<b>CTR:</b> %.1f%% &rarr; <b>%.1f%%</b> (%s)" % (num(gt_p["ctr"]) * 100, num(gt_c["ctr"]) * 100, diff_word(num(gt_c["ctr"]) * 100, num(gt_p["ctr"]) * 100, " percentage points", 1))),
        li("<b>Average position:</b> %s &rarr; <b>%s</b> (%s)" % (
            "%.1f" % num(gt_p["position"]) if gt_p["position"] is not None else "n/a",
            "%.1f" % num(gt_c["position"]) if gt_c["position"] is not None else "n/a",
            ("lower is better; " + diff_word(gt_c["position"], gt_p["position"], "", 1)) if gt_c["position"] is not None and gt_p["position"] is not None else "n/a"))))

    if ga_ok:
        ov.append('<h3>3. Traffic (GA4, %s)</h3>' % esc(geo))
        ov.append("<p><b>Total sessions:</b> %s (%s vs %s).</p>" % (fmt_int(at_c["sessions"]), diff_word(at_c["sessions"], at_p["sessions"]), month_name(pym)))
        tot_assigned = sum(num(r["sessions"]) for k, r in ch_c.items() if k != "Unassigned") or 1
        rows = sorted([(k, r) for k, r in ch_c.items() if k != "Unassigned"], key=lambda x: -num(x[1]["sessions"]))
        ov.append("<p class='small'>Share of sessions by channel (Unassigned left out):</p><ul>" + "".join(li("<b>%s:</b> %.1f%% of traffic, %s sessions (%s)" % (
            esc(k), 100 * num(r["sessions"]) / tot_assigned, fmt_int(r["sessions"]), diff_word(r["sessions"], ch_p.get(k, {}).get("sessions")))) for k, r in rows) + "</ul>")
        op_c, op_p = index(C["org_pages"], "pagePath"), index(P["org_pages"], "pagePath")
        moves = sorted(((pg, num(op_c.get(pg, {}).get("sessions")) - num(op_p.get(pg, {}).get("sessions"))) for pg in set(op_c) | set(op_p)), key=lambda x: x[1])
        downs = [m for m in moves if m[1] < 0][:3]
        ups = [m for m in reversed(moves) if m[1] > 0][:3]
        if ups or downs:
            ov.append("<p><b>Biggest organic session changes by page:</b> %s%s</p>" % (
                ("up: " + ", ".join("%s (+%s)" % (esc(p_), fmt_int(d)) for p_, d in ups)) if ups else "",
                ("; down: " if ups and downs else "down: " if downs else "") + ", ".join("%s (-%s)" % (esc(p_), fmt_int(-d)) for p_, d in downs) if downs else ""))

        ov.append('<h3>4. AI referrals (GA4, %s)</h3>' % esc(geo))
        ov.append("<ul>%s%s%s%s</ul>" % (li("<b>Sessions:</b> %s (%s)" % (fmt_int(ai_c["sessions"]), diff_word(ai_c["sessions"], ai_p["sessions"]))),
                                        li("<b>Views:</b> %s (%s)" % (fmt_int(ai_c["views"]), diff_word(ai_c["views"], ai_p["views"]))),
                                        li("<b>Engaged sessions:</b> %s (%s)" % (fmt_int(ai_c["engaged"]), diff_word(ai_c["engaged"], ai_p["engaged"]))),
                                        li("<b>Key events:</b> %s" % fmt_int(ai_c["key"]))))
        if C["ai"]:
            ov.append("<p class='small'>AI sources this month: %s.</p>" % ", ".join("%s to %s (%s session%s)" % (
                esc(r["sessionSource"]), esc(r["landingPage"]), fmt_int(r["sessions"]), "" if num(r["sessions"]) == 1 else "s") for r in sorted(C["ai"], key=lambda r: -num(r["sessions"]))))
    else:
        ov.extend(['<h3>3. Traffic (GA4)</h3>', ga_note, '<h3>4. AI referrals (GA4)</h3>', ga_note])

    ov.append('<h3>5. Keyword performance (Search Console queries)</h3>')
    ov.append("<ul>%s%s%s</ul>" % (
        li("<b>Keyword distribution:</b> %d queries at positions 1 to 3, %d at 4 to 10, %d beyond 10 (%s: %d, %d, %d)." % (
            len(qb_c["1-3"]), len(qb_c["4-10"]), len(qb_c["11+"]), month_name(pym), len(qb_p["1-3"]), len(qb_p["4-10"]), len(qb_p["11+"]))),
        li("<b>Position changes</b> (queries seen in both months, average position to one decimal): %d improved, %d declined, %d unchanged." % (improved, declined, unchanged)),
        li("<b>Queries:</b> %d with impressions this month, %d last month." % (len(q_c), len(q_p)))))
    ov.append('<p class="small">Search Console only lists queries that got impressions and hides rare (anonymized) ones, so these counts are not a full rank tracker.</p>')

    changes, posts = seo_changes(ym), blog_posts(ym)
    ov.append('<h3>6. SEO work in %s</h3>' % month_name(ym))
    if changes:
        ov.append("<p><b>On-site SEO changes</b> (from the SEO change log):</p><ul>" + "".join(li("%s, %s: %s" % (esc(c["date"]), esc(c["page"]), esc(c["change"]))) for c in changes) + "</ul>")
    else:
        ov.append("<p>No entries in the SEO change log for this month.</p>")
    if posts:
        ov.append("<p><b>Blog posts published (%d):</b></p><ul>" % len(posts) + "".join(li('%s: <a href="https://dyadgrow.com/blog/%s">%s</a>' % (esc(p_["date"]), esc(p_["slug"]), esc(p_["title"]))) for p_ in posts) + "</ul>")
    else:
        ov.append("<p>No blog posts were published this month.</p>")
    n = notes(ym)
    if n:
        ov.append('<h3>7. Notes and next steps</h3><div class="notes">%s</div>' % md_to_html(n))
    sections.append(("overview", "Monthly Performance Overview", "".join(ov)))

    # ---------- tracked keywords
    tk = tracked_keywords()
    trows = []
    for q, owner, typ in tk:
        c, p_ = q_c.get(q), q_p.get(q)
        trows.append([esc(q), esc(owner), esc(typ),
                      fmt_int(c["impressions"]) if c else "0", fmt_int(c["clicks"]) if c else "0",
                      ("%.1f" % num(c["position"])) if c else "not seen", ("%.1f" % num(p_["position"])) if p_ else "not seen",
                      chip(num(c["position"]), num(p_["position"]), invert=True, as_points=True) if c and p_ else ""])
    tk_html = ('<p class="small">Average Google position for each search in the keyword map (Search Console, %s). "Not seen" means the search got no impressions for dyadgrow.com that month.</p>' % esc(cfg["gsc_country"].upper() or "all countries")
               + table(["Search", "Owner page", "Type", "Impr.", "Clicks", month_name(ym), month_name(pym), "Change"], trows, "tight") if tk
               else '<p>The keyword map (_seo/keywords.md) could not be read.</p>')
    sections.append(("keywords", "Tracked Keyword Positions", tk_html))

    # ---------- organic GA4
    labels = day_labels(ym)
    org = ['<h2 class="sub">Organic search traffic to the website</h2><div class="kpis">']
    org.append(kpi("New users", fmt_int(ot_c["newUsers"]), ot_c["newUsers"], ot_p["newUsers"]))
    org.append(kpi("Sessions", fmt_int(ot_c["sessions"]), ot_c["sessions"], ot_p["sessions"]))
    org.append(kpi("Views", fmt_int(ot_c["screenPageViews"]), ot_c["screenPageViews"], ot_p["screenPageViews"]))
    eu_c, eu_p = ratio(ot_c["userEngagementDuration"], ot_c["activeUsers"]), ratio(ot_p["userEngagementDuration"], ot_p["activeUsers"])
    org.append(kpi("Engagement per user", fmt_dur(eu_c), eu_c, eu_p))
    org.append("</div>")
    src = sorted(C["org_source"], key=lambda r: -num(r["sessions"]))
    org.append('<div class="row"><div class="card w60"><div class="ct">Organic sessions per day <span class="lgd"><i class="c"></i>%s <i class="p"></i>%s</span></div>%s</div>' % (
        month_name(ym), month_name(pym), line_chart(daily_series(C["org_daily"], ym, "date", "sessions"), daily_series(P["org_daily"], pym, "date", "sessions"), labels)))
    org.append('<div class="card w40"><div class="ct">Type of search %s</div>%s</div></div>' % (
        chip(ot_c["sessions"], ot_p["sessions"]), donut([(r["sessionSourceMedium"], num(r["sessions"])) for r in src[:5]], fmt_int(ot_c["sessions"]), "sessions", num(ot_c["sessions"]))))
    pp = sorted(C["org_pages"], key=lambda r: -num(r["sessions"]))[:10]
    org.append('<div class="card"><div class="ct">Pages visited (top 10 by sessions)</div>' + table(
        ["Page", "New users", "Sessions", "Views", "Avg engagement per session"],
        [[esc(r["pagePath"]), cell(fmt_int(r["newUsers"]), r["newUsers"], op_p.get(r["pagePath"], {}).get("newUsers", 0)),
          cell(fmt_int(r["sessions"]), r["sessions"], op_p.get(r["pagePath"], {}).get("sessions", 0)),
          cell(fmt_int(r["screenPageViews"]), r["screenPageViews"], op_p.get(r["pagePath"], {}).get("screenPageViews", 0)),
          cell(fmt_dur(ratio(r["userEngagementDuration"], r["sessions"])), ratio(r["userEngagementDuration"], r["sessions"]),
               ratio(op_p.get(r["pagePath"], {}).get("userEngagementDuration"), op_p.get(r["pagePath"], {}).get("sessions")))] for r in pp]) + "</div>")
    dv_p = index(P["org_devices"], "deviceCategory")
    org.append('<div class="card"><div class="ct">Type of device</div>' + table(
        ["Device", "New users", "Sessions", "Views", "Engagement per user"],
        [[esc(r["deviceCategory"].title()), cell(fmt_int(r["newUsers"]), r["newUsers"], dv_p.get(r["deviceCategory"], {}).get("newUsers", 0)),
          cell(fmt_int(r["sessions"]), r["sessions"], dv_p.get(r["deviceCategory"], {}).get("sessions", 0)),
          cell(fmt_int(r["screenPageViews"]), r["screenPageViews"], dv_p.get(r["deviceCategory"], {}).get("screenPageViews", 0)),
          cell(fmt_dur(ratio(r["userEngagementDuration"], r["activeUsers"])), ratio(r["userEngagementDuration"], r["activeUsers"]),
               ratio(dv_p.get(r["deviceCategory"], {}).get("userEngagementDuration"), dv_p.get(r["deviceCategory"], {}).get("activeUsers")))]
         for r in sorted(C["org_devices"], key=lambda r: -num(r["sessions"]))]) + "</div>")
    oc = ['<div class="card"><div class="ct">Conversion actions from organic search (each counted separately)</div>' + table(
        ["Action", month_name(ym), month_name(pym)], [[esc(k), fmt_int(v), fmt_int(oconv_p[k])] for k, v in oconv_c.items()] +
        [["<b>GA4 key events</b>", fmt_int(okey_c), fmt_int(okey_p)]]) + "</div>"]
    org.extend(oc)
    sections.append(("organic", "Organic Search (%s) - Google Analytics 4" % esc(geo), ("".join(org) if ga_ok else ga_note)))

    # ---------- all channels GA4
    al = ['<h2 class="sub">All traffic to the website</h2><div class="kpis">']
    al.append(kpi("New users", fmt_int(at_c["newUsers"]), at_c["newUsers"], at_p["newUsers"]))
    al.append(kpi("Sessions", fmt_int(at_c["sessions"]), at_c["sessions"], at_p["sessions"]))
    al.append(kpi("Views", fmt_int(at_c["screenPageViews"]), at_c["screenPageViews"], at_p["screenPageViews"]))
    au_c, au_p = ratio(at_c["userEngagementDuration"], at_c["activeUsers"]), ratio(at_p["userEngagementDuration"], at_p["activeUsers"])
    al.append(kpi("Engagement per user", fmt_dur(au_c), au_c, au_p))
    al.append("</div>")
    chs = sorted(C["all_channels"], key=lambda r: -num(r["sessions"]))
    al.append('<div class="row"><div class="card w60"><div class="ct">Sessions per day <span class="lgd"><i class="c"></i>%s <i class="p"></i>%s</span></div>%s</div>' % (
        month_name(ym), month_name(pym), line_chart(daily_series(C["all_daily"], ym, "date", "sessions"), daily_series(P["all_daily"], pym, "date", "sessions"), labels)))
    al.append('<div class="card w40"><div class="ct">Source of traffic %s</div>%s</div></div>' % (
        chip(at_c["sessions"], at_p["sessions"]), donut([(r["sessionDefaultChannelGroup"], num(r["sessions"])) for r in chs[:5]], fmt_int(at_c["sessions"]), "sessions", num(at_c["sessions"]))))
    sp = index(P["all_sources"], "sessionSourceMedium")
    al.append('<div class="card"><div class="ct">Source / medium (top 10 by sessions)</div>' + table(
        ["Session source / medium", "New users", "Sessions", "Views", "Avg engagement per session"],
        [[esc(r["sessionSourceMedium"]), cell(fmt_int(r["newUsers"]), r["newUsers"], sp.get(r["sessionSourceMedium"], {}).get("newUsers", 0)),
          cell(fmt_int(r["sessions"]), r["sessions"], sp.get(r["sessionSourceMedium"], {}).get("sessions", 0)),
          cell(fmt_int(r["screenPageViews"]), r["screenPageViews"], sp.get(r["sessionSourceMedium"], {}).get("screenPageViews", 0)),
          cell(fmt_dur(ratio(r["userEngagementDuration"], r["sessions"])), ratio(r["userEngagementDuration"], r["sessions"]),
               ratio(sp.get(r["sessionSourceMedium"], {}).get("userEngagementDuration"), sp.get(r["sessionSourceMedium"], {}).get("sessions")))]
         for r in sorted(C["all_sources"], key=lambda r: -num(r["sessions"]))[:10]]) + "</div>")
    al.append('<div class="card"><div class="ct">Type of traffic (channel)</div>' + table(
        ["Channel", "New users", "Sessions", "Views", "Engagement per user"],
        [[esc(r["sessionDefaultChannelGroup"]), cell(fmt_int(r["newUsers"]), r["newUsers"], ch_p.get(r["sessionDefaultChannelGroup"], {}).get("newUsers", 0)),
          cell(fmt_int(r["sessions"]), r["sessions"], ch_p.get(r["sessionDefaultChannelGroup"], {}).get("sessions", 0)),
          cell(fmt_int(r["screenPageViews"]), r["screenPageViews"], ch_p.get(r["sessionDefaultChannelGroup"], {}).get("screenPageViews", 0)),
          cell(fmt_dur(ratio(r["userEngagementDuration"], r["activeUsers"])), ratio(r["userEngagementDuration"], r["activeUsers"]),
               ratio(ch_p.get(r["sessionDefaultChannelGroup"], {}).get("userEngagementDuration"), ch_p.get(r["sessionDefaultChannelGroup"], {}).get("activeUsers")))]
         for r in chs]) + "</div>")
    lead_rows = sorted(C["lead_by_page"], key=lambda r: -num(r["eventCount"]))
    al.append('<div class="card"><div class="ct">Conversion actions, all channels (each counted separately)</div>' + table(
        ["Action", month_name(ym), month_name(pym)], [[esc(k), fmt_int(v), fmt_int(conv_p[k])] for k, v in conv_c.items()] +
        [["<b>GA4 key events</b>", fmt_int(key_c), fmt_int(key_p)]]) +
        ("<p class='small'>Social, review and map clicks by site: %s.</p>" % ", ".join("%s %s" % (esc(k), fmt_int(v)) for k, v in sorted(soc_c.items(), key=lambda x: -x[1])) if soc_c else "") +
        ("<p class='small'>Where tracked actions happened: %s.</p>" % ", ".join("%s on %s (%s)" % (esc(dict(LEAD_EVENTS).get(r["eventName"], r["eventName"])), esc(r["pagePath"]), fmt_int(r["eventCount"])) for r in lead_rows[:12]) if lead_rows else "") + "</div>")
    sections.append(("channels", "All Channels (%s) - Google Analytics 4" % esc(geo), ("".join(al) if ga_ok else ga_note)))

    # ---------- GSC
    gs = ['<h2 class="sub">Search terms that brought people to the website</h2>']
    gs.append('<div class="row"><div class="card w60"><div class="ct">Clicks per day <b class="big">%s</b> %s <span class="lgd"><i class="c"></i>%s <i class="p"></i>%s</span></div>%s</div>' % (
        fmt_int(gt_c["clicks"]), chip(gt_c["clicks"], gt_p["clicks"]), month_name(ym), month_name(pym),
        line_chart(daily_series(C["gsc_daily"], ym, "date", "clicks"), daily_series(P["gsc_daily"], pym, "date", "clicks"), labels)))
    topq = sorted(C["gsc_queries"], key=lambda r: (-num(r["clicks"]), -num(r["impressions"])))
    gs.append('<div class="card w40"><div class="ct">Top search terms by clicks</div>%s</div></div>' % (
        hbars([(r["query"], num(r["clicks"])) for r in topq[:5] if num(r["clicks"]) > 0]) or "<p class='small'>No search term got a click this month.</p>"))
    gs.append('<div class="kpis">%s%s%s%s</div>' % (
        kpi("Clicks", fmt_int(gt_c["clicks"]), gt_c["clicks"], gt_p["clicks"]),
        kpi("Impressions", fmt_int(gt_c["impressions"]), gt_c["impressions"], gt_p["impressions"]),
        kpi("CTR", "%.1f%%" % (num(gt_c["ctr"]) * 100), num(gt_c["ctr"]) * 100, num(gt_p["ctr"]) * 100, as_points=True),
        kpi("Avg position", "%.1f" % num(gt_c["position"]) if gt_c["position"] is not None else "n/a",
            num(gt_c["position"]), num(gt_p["position"]) if (gt_p["position"] is not None and gt_c["position"] is not None) else None, invert=True, as_points=True)))
    gs.append('<div class="card"><div class="ct">Search terms by clicks (top 10)</div>' + table(
        ["Search term", "Clicks", "Impressions", "Position"],
        [[esc(r["query"]), cell(fmt_int(r["clicks"]), r["clicks"], q_p.get(r["query"], {}).get("clicks", 0)),
          cell(fmt_int(r["impressions"]), r["impressions"], q_p.get(r["query"], {}).get("impressions", 0)),
          cell("%.1f" % num(r["position"]), num(r["position"]), num(q_p[r["query"]]["position"]) if r["query"] in q_p else None, invert=True, as_points=True)]
         for r in topq[:10]]) + "</div>")
    pg_p = index(P["gsc_pages"], "page")
    gs.append('<div class="card"><div class="ct">Pages in Google search (top 10 by clicks, then impressions)</div>' + table(
        ["Page", "Clicks", "Impressions", "Position"],
        [[esc(path_of(r["page"])), cell(fmt_int(r["clicks"]), r["clicks"], pg_p.get(r["page"], {}).get("clicks", 0)),
          cell(fmt_int(r["impressions"]), r["impressions"], pg_p.get(r["page"], {}).get("impressions", 0)),
          cell("%.1f" % num(r["position"]), num(r["position"]), num(pg_p[r["page"]]["position"]) if r["page"] in pg_p else None, invert=True, as_points=True)]
         for r in sorted(C["gsc_pages"], key=lambda r: (-num(r["clicks"]), -num(r["impressions"])))[:10]]) + "</div>")
    sections.append(("gsc", "Organic Search Terms (%s) - Google Search Console" % esc(cfg["gsc_country"].upper() or "all countries"), "".join(gs)))

    # ---------- GBP
    g, gp = load_gbp(ym), load_gbp(pym)
    if g:
        imp = g.get("impressions", {})
        parts = [("Mobile Search", num(imp.get("mobile_search"))), ("Desktop Search", num(imp.get("desktop_search"))),
                 ("Mobile Maps", num(imp.get("mobile_maps"))), ("Desktop Maps", num(imp.get("desktop_maps")))]
        itot = sum(v for _, v in parts)
        pimp = (gp or {}).get("impressions", {})
        ptot = sum(num(pimp.get(k)) for k in ("mobile_search", "desktop_search", "mobile_maps", "desktop_maps")) if gp else None
        gb = ['<h2 class="sub">Insights</h2><div class="kpis">']
        gb.append(kpi("Website clicks", fmt_int(g.get("website_clicks")), g.get("website_clicks"), (gp or {}).get("website_clicks") if gp else None))
        gb.append(kpi("Calls", fmt_int(g.get("calls")), g.get("calls"), (gp or {}).get("calls") if gp else None))
        gb.append(kpi("Direction requests", fmt_int(g.get("directions")), g.get("directions"), (gp or {}).get("directions") if gp else None))
        gb.append(kpi("New reviews", fmt_int(g.get("new_reviews")), g.get("new_reviews"), (gp or {}).get("new_reviews") if gp else None))
        gb.append('</div><div class="row"><div class="card w50"><div class="ct">Profile views by type of search %s</div>%s</div>' % (
            chip(itot, ptot), donut(parts, fmt_int(itot), "views")))
        gb.append('<div class="card w50"><div class="ct">Views to actions</div>%s</div></div>' % hbars([
            ("Profile views", itot), ("Interactions", num(g.get("interactions"))), ("Website clicks", num(g.get("website_clicks"))),
            ("Calls", num(g.get("calls"))), ("Direction requests", num(g.get("directions")))]))
        if g.get("searches"):
            gb.append('<div class="card"><div class="ct">Searches that showed the profile</div>' + table(["Search", "Searches"], [[esc(k), fmt_int(v)] for k, v in g["searches"]]) + "</div>")
        gb.append('<p class="small">Typed in from the Business Profile Performance screen (gbp/%s.json)%s.</p>' % (ym, "" if gp else "; no file for %s, so there is no comparison" % month_name(pym)))
        sections.append(("gbp", "Google Business Profile", "".join(gb)))
    else:
        sections.append(("gbp", "Google Business Profile", '<p>No Business Profile numbers for %s yet. Add them to <code>gbp/%s.json</code> (see gbp/README.md) and run the report again.</p>' % (month_name(ym), ym)))

    return sections


def md_to_html(t):
    """Tiny Markdown subset for notes: paragraphs, - bullets, **bold**, ## headings."""
    out, ul = [], False
    for line in t.splitlines():
        s = line.strip()
        s_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))
        if s.startswith(("- ", "* ")):
            if not ul:
                out.append("<ul>"); ul = True
            out.append("<li>%s</li>" % s_html[2:])
            continue
        if ul:
            out.append("</ul>"); ul = False
        if s.startswith("#"):
            out.append("<h4>%s</h4>" % s_html.lstrip("#").strip())
        elif s:
            out.append("<p>%s</p>" % s_html)
    if ul:
        out.append("</ul>")
    return "".join(out)


def asset_uri(rel, mime):
    for base in (SITE, HERE):
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return "data:%s;base64,%s" % (mime, base64.b64encode(open(p, "rb").read()).decode())
    return ""


def page_html(data, sections, toc_pages=None):
    ym, pym = data["cur"]["month"], data["prev"]["month"]
    fonts = "".join("@font-face{font-family:'%s';src:url(%s) format('woff2');}" % (n, asset_uri("assets/fonts/" + f, "font/woff2")) for n, f in [
        ("Arian Bold", "arian-lt-bold.woff2"), ("Arian Heavy", "arian-lt-heavy.woff2"), ("Arian Light", "arian-lt-light.woff2"),
        ("Hyperwave", "hyperwave-one.woff2"), ("Mont", "mont-light.woff2"), ("Mont Heavy", "mont-heavy.woff2")])
    # Mont's own glyphs for / % | < > and arrows are broken; the site patches them with these files (same ranges as index.html)
    fix_range = ("U+23,U+25,U+2F,U+3C,U+3E,U+5C,U+5E,U+5F,U+7C,U+7E,U+A1,U+A4,U+A6,U+AA,U+AC,U+B0,U+B1,U+BA,U+BF,U+C6,U+DE,U+DF,"
                 "U+E6,U+F0,U+FE,U+2020,U+2021,U+2030,U+212E,U+2190-2199")
    fonts += "".join("@font-face{font-family:'%s';src:url(%s) format('woff2');unicode-range:%s;}" % (n, asset_uri("assets/fonts/" + f, "font/woff2"), fix_range)
                     for n, f in [("Mont", "mont-fix-light.woff2"), ("Mont Heavy", "mont-fix-heavy.woff2")])
    logo = asset_uri("assets/img/logo-header.webp", "image/webp")
    toc = "".join('<div class="toc"><span>%s</span><i></i><b>%s</b></div>' % (t, (toc_pages or {}).get(i, "")) for i, t, _ in sections)
    body = "".join('<section id="%s"><h1 class="title" data-marker="%s">%s</h1>%s</section>' % (i, i, t, h) for i, t, h in sections)
    css = """
    %s
    @page{size:Letter;margin:0.85in 0.45in 0.6in 0.45in}
    *{box-sizing:border-box}
    body{font-family:'Mont',Arial,sans-serif;color:#0a0a0a;font-size:9.6pt;line-height:1.45;margin:0;background:#fff}
    .cover{height:9.4in;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;break-after:page}
    .cover img{width:3.4in;height:auto}
    .cover h1{font-family:'Arian Heavy';font-size:25pt;margin:.6in 0 0}
    .cover .script{font-family:'Hyperwave';color:#f51153;font-size:50pt;line-height:1;margin:.05in 0 .15in}
    .cover .meta{font-family:'Arian Light';letter-spacing:.06em;text-transform:uppercase;font-size:10pt;color:#444}
    .cover .bar{width:2.2in;height:6px;margin:.35in auto;background:linear-gradient(90deg,#f51153 0 25%%,#b6fd29 25%% 50%%,#b697fc 50%% 75%%,#bd6ec9 75%%)}
    .tocp{break-after:page}
    .tocp h1,.title{font-family:'Arian Heavy';text-align:center;font-size:19pt;margin:0 0 .18in}
    .toc{display:flex;align-items:baseline;gap:6px;padding:7px 0;border-bottom:1px dotted #999;font-size:10.5pt}
    .toc i{flex:1}
    section{break-before:page}
    h2.sub{font-family:'Arian Bold';font-size:13pt;margin:0 0 8px;padding:8px 12px;border:1px solid #e6e6e6;border-radius:8px}
    h3{font-family:'Arian Bold';font-size:11.5pt;margin:14px 0 4px;text-decoration:underline;text-decoration-color:#f51153;text-underline-offset:3px}
    h4{font-family:'Arian Bold';font-size:10pt;margin:8px 0 2px}
    p{margin:4px 0}ul{margin:3px 0 6px;padding-left:18px}li{margin:1px 0}
    a{color:#bd6ec9;text-decoration:none}
    .small{font-size:8.4pt;color:#555}
    .note{background:#eeeeee;border-left:4px solid #b697fc;padding:6px 9px;font-size:8.8pt}
    .notes{border:1px solid #e6e6e6;border-radius:8px;padding:6px 12px}
    .kpis{display:flex;gap:8px;margin:8px 0}
    .kpi{flex:1;border:1px solid #e6e6e6;border-radius:8px;padding:8px 10px;break-inside:avoid}
    .kl{font-family:'Arian Light';font-size:8pt;display:flex;justify-content:space-between;align-items:center}
    .kv{font-family:'Arian Heavy';font-size:22pt;text-align:center;padding:10px 0 4px}
    .chip{display:inline-block;font-family:'Mont Heavy';font-size:7pt;padding:1px 6px;border-radius:10px;white-space:nowrap}
    .chip.up{background:#b6fd29;color:#0a0a0a}.chip.down{background:#fde3ea;color:#c40d43}.chip.flat{background:#eeeeee;color:#555}
    .row{display:flex;gap:8px;margin:8px 0}.w60{flex:6}.w40{flex:4}.w50{flex:5}
    .card{border:1px solid #e6e6e6;border-radius:8px;padding:8px 10px;margin:8px 0;break-inside:avoid}
    .row .card{margin:0}
    .ct{font-family:'Arian Bold';font-size:9pt;margin-bottom:6px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
    .ct .big{font-family:'Arian Heavy';font-size:13pt}
    .lgd{margin-left:auto;font-family:'Mont';font-size:7.5pt;color:#555}
    .lgd i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin:0 3px 0 8px}.lgd i.c{background:#f51153}.lgd i.p{background:#b697fc}
    svg .ax{font-size:8px;fill:#777;font-family:'Mont'}
    svg .dn{font-family:'Arian Heavy';font-size:22px}svg .ds{font-size:9px;fill:#777}
    .donut{display:flex;align-items:center;gap:10px}
    .legend{flex:1}.lg{display:flex;align-items:center;gap:6px;font-size:8pt;margin:3px 0}.lg i{width:9px;height:9px;border-radius:50%%;flex:none}.lg span{flex:1}
    .hb{margin:5px 0}.hbl{display:flex;justify-content:space-between;font-size:8.4pt}.hbt{height:7px;background:#eeeeee;border-radius:4px}.hbt i{display:block;height:7px;border-radius:4px;background:#f51153}
    table{width:100%%;border-collapse:collapse;font-size:8.4pt}
    th{font-family:'Arian Bold';font-size:7.8pt;text-align:center;padding:5px 4px;border-bottom:1.5px solid #0a0a0a}
    th:first-child,td:first-child{text-align:left}
    td{text-align:center;padding:4px;border-bottom:1px solid #e6e6e6;vertical-align:middle;word-break:break-word}
    tr{break-inside:avoid}
    table.tight td{padding:3px 4px}
    table.tight td:nth-child(3){white-space:nowrap}
    code{font-size:8.5pt;background:#eeeeee;padding:0 3px}
    """ % fonts
    cover = ('<div class="cover"><img src="%s" alt="DYAD Marketects">' % logo if logo else '<div class="cover">') + (
        '<h1>Monthly SEO Report</h1><div class="script">%s</div><div class="meta">dyadgrow.com &middot; compared with %s</div>'
        '<div class="bar"></div><div class="meta">DYAD Marketects &middot; Duality Yields Agile Development</div></div>') % (esc(month_name(ym)), esc(month_name(pym)))
    tocp = '<div class="tocp"><h1>Table of Contents</h1>%s<p class="small" style="margin-top:14px">Data pulled %s from the Google Analytics 4 Data API (property %s) and the Search Console API (%s). Every figure is taken directly from those APIs or from files listed on its page; nothing is estimated.</p></div>' % (
        toc, esc(data["generated"]), esc(data["config"]["ga4_property"]), esc(data["config"]["gsc_property"]))
    return "<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s%s%s</body></html>" % (css, cover, tocp, body)


def header_template(data):
    logo = asset_uri("assets/img/logo-header.webp", "image/webp")
    return ('<div style="width:100%%;font-family:Arial;font-size:7px;color:#888;padding:0 0.45in;display:flex;justify-content:space-between;align-items:center">'
            '%s<div style="text-align:right">DYAD Marketects<br>%s<br>Previous: %s</div></div>') % (
        ('<img src="%s" style="height:22px;width:auto">' % logo) if logo else "<b>DYAD</b>", esc(month_name(data["cur"]["month"])), esc(month_name(data["prev"]["month"])))


FOOTER = '<div style="width:100%;font-family:Arial;font-size:7px;color:#888;text-align:right;padding:0 0.45in"><span class="pageNumber"></span>/<span class="totalPages"></span></div>'


def render_pdf(html_text, data, out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.set_content(html_text, wait_until="load")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=out, format="Letter", print_background=True, display_header_footer=True,
               header_template=header_template(data), footer_template=FOOTER,
               margin={"top": "0.85in", "bottom": "0.6in", "left": "0.45in", "right": "0.45in"})
        b.close()


def find_pages(pdf_path, sections):
    from pypdf import PdfReader
    r = PdfReader(pdf_path)
    found = {}
    for n, page in enumerate(r.pages, 1):
        text = re.sub(r"\s+", " ", page.extract_text() or "")
        for i, t, _ in sections:
            plain = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", t)))
            if i not in found and n > 2 and plain in text:
                found[i] = n
    return found


def cmd_render(args):
    data = json.load(open(args.data, encoding="utf-8"))
    sections = build_html(data)
    tmp = args.out + ".tmp.pdf"
    render_pdf(page_html(data, sections), data, tmp)
    pages = find_pages(tmp, sections)
    os.remove(tmp)
    html_text = page_html(data, sections, pages)
    if args.html:
        open(args.html, "w", encoding="utf-8").write(html_text)
    render_pdf(html_text, data, args.out)
    missing = [i for i, _, _ in sections if i not in pages]
    if missing:
        print("warning: no page number found for sections: %s" % ", ".join(missing), file=sys.stderr)
    print(args.out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--month")
    r = sub.add_parser("render"); r.add_argument("data"); r.add_argument("--out", default="report.pdf"); r.add_argument("--html")
    a = ap.parse_args()
    (cmd_fetch if a.cmd == "fetch" else cmd_render)(a)


if __name__ == "__main__":
    main()
