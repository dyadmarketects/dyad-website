# dyadgrow.com — DYAD Marketects website

Static site deployed to GitHub Pages by `.github/workflows/static.yml` on every push to `main`.
The workflow runs `python3 _tools/blog.py`, then publishes everything except `.github/`, `_blog/`, `_tools/` and this file.

URLs are extensionless (`/web-design` serves `web-design.html`). Blog posts live at `/blog/<slug>`.

## Hard rules for any edit
- Never touch the homepage loader or hero code in `index.html` (loading screen, hero video, sprite sheets). The owner has asked for this explicitly.
- Brand: pink `#f51153`, lime `#b6fd29`, lavender `#b697fc`, magenta `#bd6ec9`, ink `#0a0a0a`, paper `#eeeeee`. Fonts: Arian LT (headings), Hyperwave One (script accent, always 2x the adjacent Arian size), Mont (body), JetBrains Mono (kickers).
- DYAD stands for "Duality Yields Agile Development".
- Never invent facts: no prices, stats, client names, results, credentials, guarantees, "free" offers, addresses or phone numbers that aren't already on the site or in `_blog/FACTS.md`.

## Blog workflow (scheduled runs: Monday, Wednesday, Friday)
Each run writes ONE post and opens ONE pull request. The owner (Vince) reviews on his phone and merges to publish.

1. Make sure you're up to date with `main`. Read `_blog/TOPICS.md`, `_blog/FACTS.md` and the titles of existing posts in `_blog/posts/`.
2. If there's already an open PR from a `blog/` branch that hasn't been merged, still write the next post, but mention the waiting PR in the new PR description.
3. Pick the first topic in `_blog/TOPICS.md` marked `[ ]` whose slug isn't already used. Prefer rotating services so consecutive posts don't share a service.
4. Research the search intent if web search is available (what people in Albuquerque / New Mexico actually ask). Use reputable sources only, and link them in the post when you cite something.
5. Write the post as `_blog/posts/YYYY-MM-DD-<slug>.post` (today's date in America/Denver). Format is documented at the top of `_tools/blog.py`.
   - 900 to 1,500 words. Genuinely useful, specific, practical. Answer the question in the first 2 paragraphs.
   - `seo_title` 60 characters or fewer, includes the main keyword and a place (Albuquerque or New Mexico) when it fits naturally.
   - `description` 140 to 160 characters.
   - `summary`: 2 to 4 short takeaways (shown as "Quick answer", helps AI answers quote us).
   - `faq`: 2 to 4 real questions with direct answers that also appear in the visible FAQ (the builder renders them).
   - Use H2/H3 headings phrased the way people search. Use lists where they help.
   - Link to the matching service page at least once with descriptive anchor text, and to one or two related existing posts when relevant.
   - Ground it in DYAD's real work when relevant (portfolio projects and testimonials from `index.html`, quote testimonials exactly). Never invent a case study.
   - If a point needs a number or fact we don't have, write `<p class="note">NEEDS VINCE: ...</p>` instead of guessing. The PR description must list every NEEDS VINCE note.
   - `image`: reuse an existing relevant image from `images/*-card.webp` (800x500). Write a specific alt text.
   - Voice: conversational and warm, contractions, short-to-medium sentences, natural phrasing. Do not use em dashes or en dashes in the copy.
6. Mark the topic `[x]` in `_blog/TOPICS.md` with the date. If fewer than 9 `[ ]` topics remain, append 9 new, non-overlapping topics in the same format.
7. Run `python3 _tools/blog.py` and make sure it succeeds. Spot check the generated `blog/<slug>.html` (one H1, canonical, JSON-LD parses).
8. Commit on a new branch `blog/YYYY-MM-DD-<slug>`, push, and open a PR to `main` titled `Blog: <title>`. `gh pr create` doesn't work here (GraphQL is blocked); use REST: `gh api repos/dyadmarketects/dyad-website/pulls -f base=main -f head=<branch> -f title='Blog: <title>' -F body=@<file>`. PR body: one-line summary, target search query, word count, the service it supports, a list of NEEDS VINCE items (or "none"), and "Merge to publish."
9. Do not merge the PR yourself.
