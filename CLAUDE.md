# dyadgrow.com — DYAD Marketects website

Static site deployed to GitHub Pages by `.github/workflows/static.yml` on every push to `main`.
The workflow runs `python3 _tools/blog.py`, then publishes everything except `.github/`, `_blog/`, `_tools/` and this file.

URLs are extensionless (`/web-design` serves `web-design.html`). Blog posts live at `/blog/<slug>`.

## Hard rules for any edit
- Never touch the homepage loader or hero code in `index.html` (loading screen, hero video, sprite sheets). The owner has asked for this explicitly.
- Brand: pink `#f51153`, lime `#b6fd29`, lavender `#b697fc`, magenta `#bd6ec9`, ink `#0a0a0a`, paper `#eeeeee`. Fonts: Arian LT (headings), Hyperwave One (script accent, always 2x the adjacent Arian size), Mont (body), JetBrains Mono (kickers).
- DYAD stands for "Duality Yields Agile Development".
- Every page shares the homepage's President's Club tab, social bar, custom cursor, contact form (#contact) and footer. `_tools/site_chrome.py` copies them from `index.html` into all other pages (it runs on every deploy). To change them, edit `index.html` only. New pages just need a normal `<head>`, `<body>` and any `<footer>` (it gets replaced); "Book a call" links should point to `#contact` (the script rewrites `/#contact` automatically). Contact section colors per page live in `CTA_BG` in that script.
- Refreshing any page starts at the top: an inline `/*top-on-reload*/` script in each `<head>` (in `index.html` by hand, added to every other page by `site_chrome.py`).
- Never invent facts: no prices, stats, client names, results, credentials, guarantees, "free" offers, addresses or phone numbers that aren't already on the site or in `_blog/FACTS.md`.

## SEO tooling (runs on every deploy)
- `_tools/seo_check.py` runs after the builders and prints warnings for broken internal links, missing canonicals, bad JSON-LD and sitemap problems. It never fails a deploy or the blog "build" check (it runs as a separate `seo` job on PRs). Run it locally after building and fix anything it reports.
- `_tools/indexnow.py` runs after each deploy and sends Bing (IndexNow) every sitemap URL that is new or has a new `<lastmod>`. The key file `4e5ef9bac0f06f4a6a1645f34ab17671.txt` in the root must stay. Keep sitemap lastmod dates honest so only real changes get submitted.
- Each `images/*-card.webp` (800x500) has an `images/*-share.jpg` (1200x630) used as the post's og:image and schema image. When adding a new card image, add its 1200x630 share version too (the builder falls back to the card if it's missing).
- The footer's "Leave us a Google review" link is https://g.page/r/CZzRBWB4hoeyEAE/review (Google Business review link). Never offer anything in exchange for reviews.

## Case studies (`/work/<slug>`)
- Defined in `_tools/work.py`, built by `build_work()` in `_tools/blog.py` (sitemap entries included). Never invent results, numbers or quotes.
- Lumanta (`/work/lumanta`) also loads `assets/lumanta/` (particle engine and data copied from the lumanta-website repo, plus `case.js`): a co-branded Lumanta x DYAD intro (every load, skipped for reduced motion), a hover/touch particle demo, and a pinned "View the luxury design website" bar. When Lumanta launches on lumanta.co, change `live_url` in `_tools/work.py` from the github.io preview to https://lumanta.co/.

## Promos (`/promos`)
- `promos.html` holds one `<article class="pm" data-ends="...">` per promo. When `data-ends` passes, the page marks it ended, removes its entry form and moves it to "Past promos" on its own; with nothing live it shows "No promos running right now".
- The homepage popup (between `<!--promo` and `<!--/promo-->` in `index.html`) has its own `data-ends` and hides itself after that time.
- Entries are emailed through FormSubmit (form activated for dyadmarketects@gmail.com). Never put a promo's offer anywhere else on the site unless Vince wrote it.

## Blog workflow (scheduled runs: Monday, Wednesday, Friday)
Each run writes ONE post, opens ONE pull request, and merges it automatically once the "Blog build check" passes. Publishing does not wait for Vince. He gets the run's notification and can revert any post on GitHub.

1. Start clean from the latest main: `git fetch origin && git checkout -B post origin/main`. If `CLAUDE.md`, `_tools/blog.py` or `_blog/TOPICS.md` is missing on main, stop without writing anything and report "Skipped: the blog setup isn't merged into main yet."
   Today's date: `TZ=America/Denver date +%F`.
2. Read `_blog/TOPICS.md`, `_blog/FACTS.md`, and the metadata of every existing post in `_blog/posts/`.
   Posts waiting in open PRs:
   `gh api 'repos/dyadmarketects/dyad-website/pulls?state=open&per_page=100' --jq '.[].number' | while read n; do gh api "repos/dyadmarketects/dyad-website/pulls/$n/files" --jq '.[].filename'; done | grep '^_blog/posts/'`
   Mention any waiting PRs in the new PR description.
3. Choose the topic. A slug is taken if `_blog/posts/*-<slug>.post` exists on main or appears in the open-PR list above (ignore the TOPICS checkboxes; post PRs can't update them). Take the first untaken topic whose service differs from the newest post's service (main plus open PRs); if none, the first untaken topic. If every topic is taken, pick a new useful local topic that doesn't overlap existing posts or a service page, and list 9 suggested topic lines in the PR description.
4. Research search intent if web search is available (what people in Albuquerque / New Mexico actually ask). Use reputable sources only, and link them in the post when you cite something.
5. Write the post as `_blog/posts/<date>-<slug>.post` (the builder rejects any other filename). Format is documented at the top of `_tools/blog.py`.
   - As long as it takes to fully answer the question, usually 800 to 1,500 words. Never pad. Genuinely useful, specific, practical. Answer the question in the first 2 paragraphs.
   - Add `"target_query"` to the metadata (the main informational search the post answers). The builder rejects two posts with the same target_query. Service pages own commercial searches ([service] + Albuquerque / agency / company / cost / near me); posts target informational questions only.
   - First-hand experience: if `## Field notes (unused)` in `_blog/FACTS.md` has a line that fits, use it and name it in the PR description. If none fit, write the post without one. Never block or wait on Vince.
   - A portfolio case study may anchor at most 2 posts in total, and don't feature a case that was featured in any of the last 3 posts. Mentioning it in one line with a link is fine.
   - `seo_title` 60 characters or fewer, includes the main keyword and a place (Albuquerque or New Mexico) when it fits naturally. `description` 140 to 160 characters.
   - `summary`: 2 to 4 short takeaways (shown as "Quick answer", helps AI answers quote us).
   - `faq`: 2 to 4 real questions with direct, plain-text answers (no HTML). They're rendered visibly on the page.
   - No `<h1>` in the body. Use H2/H3 headings phrased the way people search. Use lists where they help.
   - Link to the matching service page at least once with descriptive anchor text, and to one or two related existing posts when relevant. Don't target the same main keyword as a service page or an existing post.
   - Ground it in DYAD's real work when relevant, using only `_blog/FACTS.md` and the site. Quote testimonials exactly. Never invent a case study, client, number or result. Remember the DSI work was done by Vince as DSI's Marketing Manager, not as a DYAD client.
   - If a point needs a number or fact we don't have, don't guess and don't leave placeholders: give general guidance instead, or cite a reputable source with a link. Posts publish automatically, so they must never contain notes to Vince, TODOs or placeholders.
   - `image`: reuse an existing relevant image from `images/*-card.webp` (800x500). Write a specific alt text.
   - If a field note names before/after images, show them with the `[[compare ...]]` slider (syntax at the top of `_tools/blog.py`) where it supports the point.
   - Voice: conversational and warm, contractions, short-to-medium sentences, natural phrasing. Do not use em dashes or en dashes in your own copy (quotes and names keep their original punctuation).
6. Do NOT edit `_blog/TOPICS.md` in a post PR (parallel PRs would conflict).
7. Run `python3 _tools/blog.py && python3 _tools/site_chrome.py && python3 _tools/seo_check.py` and make sure the builders succeed and the check reports no warnings for the new post. Spot check the generated `blog/<slug>.html` (one H1, canonical, JSON-LD parses). Then discard the generated files: `git reset -q && git checkout -- . && git clean -fd blog/`. The deploy workflow rebuilds every page on merge.
8. Commit only the post: `git checkout -b blog/<date>-<slug> && git add _blog/posts/<date>-<slug>.post`, and confirm `git diff --cached --name-only` prints exactly that one path. Commit, push, and open a PR to `main`. `gh pr create` doesn't work here (GraphQL is blocked); use REST with the title in double quotes so apostrophes are safe:
   `gh api repos/dyadmarketects/dyad-website/pulls -f base=main -f head=blog/<date>-<slug> -f "title=Blog: $TITLE" -F body=@<file>`
   PR body: one-line summary, target search query, word count, the service it supports, and any field note used.
9. Publish: wait for the "build" check on the PR's head commit to finish (poll every 30 seconds, up to 10 minutes):
   `gh api repos/dyadmarketects/dyad-website/commits/<sha>/check-runs --jq '.check_runs[] | select(.name=="build") | .status+" "+(.conclusion//"")'`
   If it succeeds, merge: `gh api -X PUT repos/dyadmarketects/dyad-website/pulls/<number>/merge -f merge_method=squash`. If it fails, fix the post, push, and wait again. If it still fails, leave the PR open and say so in the final message. If an older auto post PR from a previous run is still open with a passing check, merge it too.
10. Only bump `updated` in an existing post for a substantive edit (it changes the sitemap lastmod Google trusts).

## Blog structure (built by `_tools/blog.py`)
- `/llms.txt` is generated by `_tools/blog.py` from `_tools/llms_template.md` (facts and official profiles there, the blog list fills in automatically). Edit the template, not `llms.txt`.
- `/blog/` (24 posts per page, then `/blog/page/2`, ...), `/blog/topic/<service>` crawlable topic pages, `/blog/<slug>` posts, `/about` author page for Vincent King (bio and timeline pulled from the homepage), `/feed.xml`.
- Each post shows an AI assistance note under the byline (`AI_NOTE` in `_tools/blog.py`; set it to "" to hide).
- The builder also refreshes "From the blog" on the service pages and the homepage (between `<!--blog:...-->` markers, just above the FAQ).
