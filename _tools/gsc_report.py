#!/usr/bin/env python3
"""
Weekly Google Search Console report for dyadgrow.com (run by .github/workflows/search-console.yml).

It reads the last 28 days of search data through the Search Console API and writes a Markdown report:
  - totals (clicks, impressions, average position) compared with the 28 days before
  - "striking distance" searches: average position 8 to 30, where a better title, a clearer
    section or a few internal links can move a page onto page one
  - local searches (Albuquerque, ABQ, New Mexico, NM, Rio Rancho, Santa Fe) and how they moved
  - pages, with their position change

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
BRAND = re.compile(r"\bdyad|marketects|dyadgrow\b", re.I)
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

    near = sorted([r for r in q if 8 <= r["position"] <= 30 and not BRAND.search(r["keys"][0])],
                  key=lambda r: -r["impressions"])[:25]
    out += ["## Striking distance (position 8 to 30, non-branded)", "",
            "These are closest to page one. Look at the page that ranks for each and tighten its title, headings and internal links.", ""]
    out += ["| Search | Impressions | Clicks | Position | Change |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in near
    ] if near else ["None yet."]
    out.append("")

    local = sorted([r for r in q if LOCAL.search(r["keys"][0]) and not BRAND.search(r["keys"][0])],
                   key=lambda r: -r["impressions"])[:30]
    out += ["## Local searches (non-branded)", "", "Change is in positions: positive means the page moved up.", ""]
    out += ["| Search | Impressions | Clicks | Position | Change |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in local
    ] if local else ["None yet."]
    out.append("")

    branded = sorted([r for r in q if BRAND.search(r["keys"][0]) or PERSON.search(r["keys"][0])], key=lambda r: -r["impressions"])[:20]
    out += ["## Branded searches (DYAD Marketects, DYAD Grow, DYAD NM, DYAD Marketing, Vincent King)", "",
            "These should stay at position 1 to 3. A drop here matters more than any other number in this report.", ""]
    out += ["| Search | Impressions | Clicks | Position | Change |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0]} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} | {move(r, pq.get(tuple(r['keys'])))} |" for r in branded
    ] if branded else ["None yet."]
    out.append("")

    qp = query(s, start, end, ["query", "page"], 1000)
    byq = {}
    for r in qp: byq.setdefault(r["keys"][0], []).append(r)
    pmap = {r["keys"][0].replace("https://dyadgrow.com", "") or "/": r for r in pg}
    out += ["## Key pages and their target searches", "", "| Page | Target search | Impressions | Clicks | Position |", "|---|---|---|---|---|"]
    for path, target in TARGETS:
        r = pmap.get(path)
        out.append(f"| {path} | {target} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} |" if r else f"| {path} | {target} | 0 | 0 | n/a |")
    out.append("")
    clash = sorted([(k, v) for k, v in byq.items() if len(v) > 1 and sum(x["impressions"] for x in v) >= 10], key=lambda kv: -sum(x["impressions"] for x in kv[1]))[:15]
    out += ["## Searches where two of our pages compete", "", "If one search keeps splitting between two pages, make one page clearly the better answer and link to it from the other.", ""]
    out += ["| Search | Pages (position) |", "|---|---|"] + [
        f"| {k} | " + ", ".join(f"{x['keys'][1].replace('https://dyadgrow.com', '') or '/'} ({x['position']:.1f})" for x in sorted(v, key=lambda x: x['position'])) + " |" for k, v in clash
    ] if clash else ["None."]
    out.append("")

    pages = sorted(pg, key=lambda r: -r["impressions"])[:30]
    out += ["## Pages", "", "| Page | Impressions | Clicks | Position | Change |", "|---|---|---|---|---|"] + [
        f"| {r['keys'][0].replace('https://dyadgrow.com', '') or '/'} | {r['impressions']:.0f} | {r['clicks']:.0f} | {r['position']:.1f} | {move(r, ppg.get(tuple(r['keys'])))} |"
        for r in pages]
    print("\n".join(out))


if __name__ == "__main__":
    if not os.environ.get("GSC_SERVICE_ACCOUNT_JSON"):
        sys.exit("GSC_SERVICE_ACCOUNT_JSON is not set; see the setup notes at the top of this file.")
    main()
