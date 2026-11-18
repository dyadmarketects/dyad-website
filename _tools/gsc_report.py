#!/usr/bin/env python3
"""
Weekly Google Search Console report for dyadgrow.com (run by .github/workflows/search-console.yml).

It reads the last 28 days of search data through the Search Console API and writes a Markdown report:
  - totals (clicks, impressions, average position) compared with the 28 days before
  - "striking distance" searches: average position 8 to 30, where a better title, a clearer
    section or a few internal links can move a page onto page one
  - local searches (Albuquerque, ABQ, New Mexico, NM, Rio Rancho, Santa Fe) and how they moved
  - pages, with their position change
  - tracked searches from _seo/keywords.md: the real position of each search (not the page average),
    clicks, CTR and whether the owner page is the one ranking
  - Google Business Profile traffic (the homepage URL tagged utm_campaign=gbp) as its own local row
  - index coverage of every sitemap URL (URL Inspection API, same service account)
  - a JSON snapshot at the end, so the weekly SEO audit can compare week over week

Setup (one time, done by the site owner):
  1. In Google Cloud, create a project, enable the "Google Search Console API" and create a
     service account. Create a JSON key for it.
  2. In Search Console > Settings > Users and permissions for https://dyadgrow.com/, add the service
     account's email with "Restricted" permission (read only).
  3. In GitHub > repo Settings > Secrets and variables > Actions, add the JSON key as the secret
     GSC_SERVICE_ACCOUNT_JSON.
Until the secret exists the workflow skips quietly.

Usage: python3 _tools/gsc_report.py > report.md   (needs: pip install google-auth requests)
"""
import datetime, json, os, re, sys

PROPERTY = os.environ.get("GSC_PROPERTY", "https://dyadgrow.com/")
LOCAL = re.compile(r"\b(albuquerque|abq|new mexico|nm|rio rancho|santa fe|los lunas|bernalillo|corrales|mora|el paso)\b", re.I)
BRAND = re.compile(r"\b(dyad|diad|dyadgrow|marketects|marketeks|markitects|marketechs|marketecs)\b", re.I)
# searches we don't chase (services DYAD doesn't sell, other brands): kept out of the opportunity lists
EXCLUDE = re.compile(r"google ads|adwords|\bppc\b|pay per click|ad management|website builder|fragrance|hemispheric", re.I)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSON = re.compile(r"\b(vincent|vince)\s+(inkosi\s+)?king\b", re.I)
# each key page and the search it is built to win 
TARGETS = [("/", "marketing agency Albuquerque"), ("/about", "Vincent King"),
           ("/work/", "DYAD Marketects case studies"), ("/branding-logo-design", "logo design Albuquerque"),
           ("/web-design", "web design Albuquerque"), ("/video-photo-production", "video production Albuquerque"), ("/social-media-marketing", "social media marketing Albuquerque")]


def session():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    info = json.loads(os.environ["GSC_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return AuthorizedSession(creds)


def query(s, start, end, dims, limit=500):
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query" % (
        __import__("urllib.parse").parse.quote(PROPERTY, safe=""))
    r = s.post(url, json={"startDate": str(start), "endDate": str(end), "dimensions": dims, "rowLimit": limit})
    r.raise_for_status()
    return r.json().get("rows", [])


def keyed(rows):
    return {tuple(r["keys"]): r for r in rows}


def tracked():
    """(search, owner page, type) rows from the table in _seo/keywords.md."""
    out = []
    try:
        for line in open(os.path.join(ROOT, "_seo", "keywords.md"), encoding="utf-8"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(c) == 3 and c[0] and c[0] != "Search" and not c[0].startswith("---"):
                out.append((c[0].lower(), c[1], c[2]))
    except FileNotFoundError:
        pass
    return out


def path_of(url):
    p = url.replace("https://dyadgrow.com", "") or "/"
    return ("/ (Google Business Profile)" if "utm_campaign=gbp" in p else p.split("?")[0] or "/")


def ctr(r):
    return f"{100 * r['clicks'] / r['impressions']:.1f}%" if r.get("impressions") else "0%"


def inspect_index(s):
    """Coverage state of every sitemap URL through the URL Inspection API (read only)."""
    import requests
    try:
        xml = requests.get("https://dyadgrow.com/sitemap.xml", timeout=30).text
    except Exception as e:
        return None, f"could not read the sitemap ({e})"
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)[:150]
    res, err = [], None
    for u in urls:
        try:
            r = s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                       json={"inspectionUrl": u, "siteUrl": PROPERTY}, timeout=60)
            if r.status_code != 200:
                err = f"URL Inspection returned {r.status_code}: {r.text[:200]}"
                break
            st = r.json().get("inspectionResult", {}).get("indexStatusResult", {})
            res.append({"url": u, "verdict": st.get("verdict", ""), "coverage": st.get("coverageState", ""),
                        "google_canonical": st.get("googleCanonical", ""), "last_crawl": st.get("lastCrawlTime", "")})
        except Exception as e:
            err = str(e)
            break
    return res, err


def main():
    s = session()
    end = datetime.date.today() - datetime.timedelta(days=3)          # Search Console data lags ~2-3 days
    start = end - datetime.timedelta(days=27)
    pend, pstart = start - datetime.timedelta(days=1), start - datetime.timedelta(days=28)

    tot, ptot = query(s, start, end, []), query(s, pstart, pend, [])
    q, pq = query(s, start, end, ["query"]), keyed(query(s, pstart, pend, ["query"]))
    pg, ppg = query(s, start, end, ["page"]), keyed(query(s, pstart, pend, ["page"]))

    def t(rows, k): return rows[0][k] if rows else 0
    prev_pos = f"{t(ptot, 'position'):.1f}" if ptot else "n/a"
    out = [f"# Search Console report: {start} to {end}", "",
           f"Property: {PROPERTY}. Compared with {pstart} to {pend}.", "",
           "| | Last 28 days | Previous 28 days |", "|---|---|---|",
           f"| Clicks | {t(tot,'clicks'):.0f} | {t(ptot,'clicks'):.0f} |",
           f"| Impressions | {t(tot,'impressions'):.0f} | {t(ptot,'impressions'):.0f} |",
           f"| Average position | {t(tot,'position'):.1f} | {prev_pos} |", ""]

    def move(row, prev):
        if not prev: return "new"
        d = prev["position"] - row["position"]
        return f"{'+' if d >= 0 else ''}{d:.1f}"

    near = sorted([r for r in q if 8 <= r["position"] <= 30 and not BRAND.search(r["keys"][0]) and not EXCLUDE.search(r["keys"][0])],
                  key=lambda r: -r["impressions"])[:25]
    out += ["## Striking distance (position 8 to 30, non-branded)", "",
            "These are closest to page one. Look at the page that ranks for each and tighten its title, headings and internal links.", ""]
    out += ["| Search | Impressions | Clicks | CTR | Position | Change |", "|---|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {ctr(r)} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in near
    ] if near else ["None yet."]
    out.append("")

    local = sorted([r for r in q if LOCAL.search(r["keys"][0]) and not BRAND.search(r["keys"][0]) and not EXCLUDE.search(r["keys"][0])],
                   key=lambda r: -r["impressions"])[:30]
    out += ["## Local searches (non-branded)", "", "Change is in positions: positive means the page moved up.", ""]
    out += ["| Search | Impressions | Clicks | CTR | Position | Change |", "|---|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {ctr(r)} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in local
    ] if local else ["None yet."]
    out.append("")

    branded = sorted([r for r in q if BRAND.search(r["keys"][0]) or PERSON.search(r["keys"][0])], key=lambda r: -r["impressions"])[:20]
    out += ["## Branded searches (DYAD Marketects, DYAD Grow, DYAD NM, DYAD Marketing, Vincent King)", "",
            "These should stay at position 1 to 3. A drop here matters more than any other number in this report.", ""]
    out += ["| Search | Impressions | Clicks | CTR | Position | Change |", "|---|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {ctr(r)} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in branded
    ] if branded else ["None yet."]
    out.append("")

    qp = query(s, start, end, ["query", "page"], 5000)
    pqp = query(s, pstart, pend, ["query", "page"], 5000)
    byq, pbyq = {}, {}
    for r in qp: byq.setdefault(r["keys"][0].lower(), []).append(r)
    for r in pqp: pbyq.setdefault(r["keys"][0].lower(), []).append(r)

    def agg(rows):
        if not rows: return None
        im = sum(r["impressions"] for r in rows); cl = sum(r["clicks"] for r in rows)
        pos = sum(r["position"] * r["impressions"] for r in rows) / im if im else 0
        top = max(rows, key=lambda r: r["impressions"])
        return {"impressions": im, "clicks": cl, "position": pos, "page": path_of(top["keys"][1])}

    snap = []
    out += ["## Tracked searches (from _seo/keywords.md)", "",
            "The real position for each search, not a page average. Owner ranking = the page that gets most of the impressions is the page meant to own it.", "",
            "| Search | Type | Owner page | Impressions | Clicks | CTR | Position | Change | Ranking page | Owner ranking |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for kw, owner, typ in tracked():
        a, b = agg(byq.get(kw, [])), agg(pbyq.get(kw, []))
        if not a:
            out.append(f"| {kw} | {typ} | {owner} | 0 | 0 | 0% | not seen | | | |")
            snap.append({"search": kw, "owner": owner, "type": typ, "impressions": 0})
            continue
        ch = f"{b['position'] - a['position']:+.1f}" if b else "new"
        ok = "yes" if a["page"].split(" ")[0] == owner else "no"
        out.append(f"| {kw} | {typ} | {owner} | {a['impressions']:.0f} | {a['clicks']:.0f} | {ctr(a)} | {a['position']:.1f} | {ch} | {a['page']} | {ok} |")
        snap.append({"search": kw, "owner": owner, "type": typ, "impressions": a["impressions"], "clicks": a["clicks"],
                     "position": round(a["position"], 1), "prev_position": round(b["position"], 1) if b else None, "ranking_page": a["page"]})
    out.append("")

    gbp = sorted([r for r in qp if "utm_campaign=gbp" in r["keys"][1]], key=lambda r: -r["impressions"])[:20]
    out += ["## Google Business Profile (local pack and Maps)", "",
            "Searches that reached the homepage through the Google Business Profile link. This is the local pack, our strongest local signal.", ""]
    out += ["| Search | Impressions | Clicks | CTR | Position |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {ctr(r)} | {r['position']:.1f} |" for r in gbp
    ] if gbp else ["None yet."]
    out.append("")

    pmap = {r["keys"][0].replace("https://dyadgrow.com", "") or "/": r for r in pg}
    out += ["## Key pages (page averages across all their searches)", "", "| Page | Impressions | Clicks | CTR | Average position |", "|---|---|---|---|---|"]
    for path, target in TARGETS:
        r = pmap.get(path)
        out.append(f"| {path} | {r['impressions']:.0f} | {r['clicks']:.0f} | {ctr(r)} | {r['position']:.1f} |" if r else f"| {path} | 0 | 0 | 0% | n/a |")
    out.append("")

    # two different pages (the Google Business Profile link counts as the homepage) splitting one search
    clash = []
    for k, v in byq.items():
        paths = {path_of(x["keys"][1]).split(" ")[0] for x in v}
        if len(paths) > 1 and sum(x["impressions"] for x in v) >= 10 and not BRAND.search(k) and not EXCLUDE.search(k):
            clash.append((k, v))
    clash = sorted(clash, key=lambda kv: -sum(x["impressions"] for x in kv[1]))[:15]
    out += ["## Searches where two of our pages compete", "", "If one search keeps splitting between two pages, make one page clearly the better answer and link to it from the other.", ""]
    out += ["| Search | Pages (position) |", "|---|---|"] + [
        f"| {k} | " + ", ".join(f"{path_of(x['keys'][1])} ({x['position']:.1f})" for x in sorted(v, key=lambda x: x['position'])) + " |" for k, v in clash
    ] if clash else ["None."]
    out.append("")

    pages = sorted(pg, key=lambda r: -r["impressions"])[:30]
    out += ["## Pages", "", "| Page | Impressions | Clicks | Position | Change |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0].replace('https://dyadgrow.com', '') or '/'} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} | {move(r, ppg.get(tuple(r['keys'])))} |"
        for r in pages]
    out.append("")

    idx, err = inspect_index(s)
    out += ["## Index coverage (every sitemap URL)", ""]
    if idx is None or (err and not idx):
        out.append(f"Couldn't check this week: {err}")
    else:
        bad = [x for x in idx if x["verdict"] != "PASS"]
        out.append(f"{len(idx) - len(bad)} of {len(idx)} sitemap URLs are indexed." + (f" Stopped early: {err}" if err else ""))
        if bad:
            out += ["", "| URL | Coverage | Google's canonical | Last crawl |", "|---|---|---|---|"] + [
                f"| {x['url'].replace('https://dyadgrow.com', '') or '/'} | {x['coverage']} | {x['google_canonical'].replace('https://dyadgrow.com', '')} | {x['last_crawl'][:10]} |" for x in bad]
    out.append("")

    data = {"period": [str(start), str(end)], "previous": [str(pstart), str(pend)],
            "totals": {"clicks": t(tot, "clicks"), "impressions": t(tot, "impressions"), "position": round(t(tot, "position"), 1)},
            "tracked": snap, "index": idx or [], "index_error": err}
    out += ["<details><summary>Data snapshot for the weekly SEO audit</summary>", "", "```json", json.dumps(data, indent=1), "```", "", "</details>"]
    print("\n".join(out))


if __name__ == "__main__":
    if not os.environ.get("GSC_SERVICE_ACCOUNT_JSON"):
        sys.exit("GSC_SERVICE_ACCOUNT_JSON is not set; see the setup notes at the top of this file.")
    main()
