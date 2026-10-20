"""
Case studies, built by blog.py into /work/<slug>.

Each entry needs: slug, client, title, seo_title (60 chars or fewer), description (140 to 160 chars),
service (a key of SERVICES), date, updated, image (an images/*-card.webp with a matching -share.jpg),
image_alt, live_url, live_label, before/after (optional paths for the slider; the slider only shows
when both files exist), videos, and body (HTML). Never invent results, numbers or quotes.
"""

WORK = [dict(
    slug="lumanta",
    client="Lumanta",
    title='Lumanta: an immersive website for a <span class="script">mindful</span> app',
    plain_title="Lumanta: an immersive website for a mindful app",
    seo_title="Lumanta Website Design Case Study | DYAD Marketects",
    description="How DYAD Marketects took Lumanta from a BRAND$TORM to a logo refresh and a custom, immersive website with 3D particle motion on desktop and phone.",
    service="web-design",
    date="2026-10-20",
    updated="2026-10-20",
    image="images/lumanta-card.webp",
    image_alt="New Lumanta homepage with the Rise Above the Static headline, a gradient logomark and a woman with arms open on a beach",
    tags=["Website", "Logo Refresh", "BRAND$TORM", "3D Motion"],
    live_url="https://dyadmarketects.github.io/lumanta-website/",
    live_label="See the new site",
    logo="images/work/lumanta-mark.webp",
    before="images/work/lumanta-before.webp",
    before_label="lumanta.co today",
    after="images/work/lumanta-after.webp",
    after_label="The new site",
    compare_alt="Lumanta homepage",
    videos=[
        dict(kind="desktop", src="videos/lumanta-desktop.mp4", poster="images/work/lumanta-desktop-poster.webp", w=1120, h=700,
             label="Desktop scroll-through of the new Lumanta site, sped up"),
        dict(kind="phone", src="videos/lumanta-phone.mp4", poster="images/work/lumanta-phone-poster.webp", w=390, h=844,
             label="Phone scroll-through of the new Lumanta site, sped up"),
    ],
    summary=[
        "Started with a BRAND$TORM with founder Julie McCord, then a logo refresh, then a fully custom website.",
        "The site is hand built, with no templates: a 72,000 particle logo intro, scroll-driven 3D motion and touch interaction on phones.",
        "It's built with search in mind from day one, with titles, descriptions, social share cards and an llms.txt file ready for launch.",
    ],
    body="""
<h2>The client</h2>
<p>Lumanta is a simple thought-awareness app from founder Julie McCord. You catch a negative, fear-based or judgmental thought with a single tap, then watch your patterns come into view over time. No journaling, no analyzing, no judging yourself. Its tagline says it best: rise above the static.</p>
<p>The app is getting ready to launch, and Julie needed a brand and a website that feel as calm, clear and uplifting as the experience itself.</p>

<h2>Step one: the BRAND$TORM</h2>
<p>Every DYAD project starts with a BRAND$TORM, our discovery consultation. We sat down with Julie to get to the heart of Lumanta: who it's for, how it should feel, and what makes it different from every other wellness app on the shelf. That conversation shaped every decision that came after it, from the colors to the way the site moves.</p>

<h2>Step two: a logo refresh</h2>
<p>Next we refreshed the logo. The logomark is a glowing ring that breaks into particles at the top, like a thought lifting away. It's set in a warm to cool gradient of ember orange, glow pink, lumen blue and aurora aqua, with Dazzle Unicase lettering that feels light and modern. That ring became the backbone of the whole website.</p>

<h2>Step three: a website you feel, not just read</h2>
<p>Most sites tell you what a brand is about. We wanted Lumanta's site to let you feel it. A few of the moments we built:</p>
<ul>
<li><strong>A particle intro.</strong> The logomark assembles from 72,000 particles, then the camera flies through the ring and into the site.</li>
<li><strong>A cinematic hero.</strong> A full-screen video with the Rise Above the Static headline, where the O in ABOVE is the logomark itself.</li>
<li><strong>Catch, Shift, Rise, Repeat.</strong> Four color cards slide up over the hero, each with an icon that draws itself.</li>
<li><strong>The static.</strong> A scroll-driven 3D particle story where noise gathers into the logo and the night sky dawns into Lumanta's soft off white. Move your cursor, or your finger on a phone, and the particles move with you.</li>
<li><strong>The app walkthrough.</strong> A phone that stays pinned while you scroll through the app's four steps, with glowing color and particle rings behind it.</li>
</ul>
<p>Every section has its own entrance and exit animation, and it all works on phones too, with touch built in rather than bolted on. Visitors who prefer reduced motion get a calm, still version automatically.</p>

<h2>Luxury design, backed by SEO</h2>
<p>This is a $10,000 level website at a cost a startup can actually afford. And it isn't just pretty. It's built with search in mind from day one: clear page titles and descriptions, social share cards, fast loading video sized for phones, and an llms.txt file that helps AI assistants describe Lumanta accurately. When the site launches at lumanta.co, it's ready to be found. Want to know what goes into that? Here's our <a href="/blog/website-redesign-checklist-new-mexico">website redesign checklist</a>.</p>

<h2>Why it looks like nobody else</h2>
<p>Choosing a web designer is like picking your favorite artist. When you choose DYAD, you get Vincent King's bold, immersive style. No boring AI layouts. No basic Wix or WordPress templates. Just a site built from scratch around your brand, so visitors feel it the moment it loads.</p>
<p>If you want a website that makes people stop scrolling, <a href="/web-design">see how our web design works</a> or book a call below.</p>
""",
)]
