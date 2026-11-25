# Google Business Profile numbers

Google's Business Profile API needs an approval request before it can be used, so until that is granted
the report reads these numbers from a small file you fill in once a month.

1. Open your Business Profile (search "DYAD Marketects" on Google while signed in, or business.google.com) and choose **Performance**.
2. Set the date range to the full month.
3. Copy the numbers into `_seo/gbp/YYYY-MM.json` (copy `TEMPLATE.json`), using exactly what Google shows. Leave a number out if Google doesn't show it; never guess.
4. Rerun the "Monthly SEO report" workflow (Actions tab, Run workflow, enter the month) for that month from the Actions tab.

Fields:
- `impressions`: profile views split by platform and device (Google Search mobile/desktop, Google Maps mobile/desktop)
- `interactions`: total interactions
- `website_clicks`, `calls`, `directions` (direction requests), `new_reviews`
- `searches`: optional list of `["search term", count]` pairs from "Searches used to find your Business Profile"
