"""
Case studies, built by blog.py into /work/<slug>.

Each entry needs: slug, client, title, seo_title (60 chars or fewer), description (140 to 160 chars),
service (a key of SERVICES), date, updated, image (an images/*-card.webp with a matching -share.jpg),
image_alt, live_url and live_label (optional: the client's live site), before/after (optional paths for the slider; the slider only shows
when both files exist), videos, and body (HTML). Never invent results, numbers or quotes.
Optional: mockup (multi-device render shown overlapping the hero) and screens (desktop and mobile
screenshot strips, stacked top to bottom; size the columns so both strips end at about the same height),
gallery (photos with captions). Video kinds: desktop (browser frame), phone (phone frame), film (plain rounded
frame; wide=True spans the full row) and tall (vertical rounded frame).
The newest case study goes first; /work lists them in this order.
"""

WORK = [
dict(
    slug="jerky-fixx",
    client="Jerky Fixx",
    title='Jerky Fixx: a jerky website that <span class="script">erupts</span>',
    plain_title="Jerky Fixx: a jerky website that erupts",
    seo_title="Jerky Fixx Website Design Case Study | DYAD Marketects",
    description="How DYAD Marketects replaced an AI-only first draft with a custom, immersive website for Albuquerque's Jerky Fixx, built with the owners' own 3D models and warning tape.",
    service="web-design",
    date="2026-10-29",
    updated="2026-10-29",
    image="images/jerky-fixx-card.webp",
    image_alt="The Jerky Fixx homepage hero with a lime Cure the Craving headline, yellow warning tape and floating 3D jerky on a magenta background",
    tags=["Website", "3D Models", "Scroll Motion", "Local SEO"],
    live_url="https://jerkyfixx.com/",
    live_label="Visit jerkyfixx.com",
    logo="images/work/jerky-fixx-mark.webp",
    top_cta="View the award winning jerky website",
    screens=dict(folder="images/work/jerky-fixx-screens",
                 desktop=[['desktop-01.webp', 1440, 900], ['desktop-02.webp', 1440, 900], ['desktop-03.webp', 1440, 900], ['desktop-04.webp', 1440, 900], ['desktop-05.webp', 1440, 900], ['desktop-06.webp', 1440, 900], ['desktop-07.webp', 1440, 900], ['desktop-08.webp', 1440, 900], ['desktop-09.webp', 1440, 900]],
                 mobile=[['mobile-01.webp', 780, 1688], ['mobile-02.webp', 780, 1688], ['mobile-03.webp', 780, 1688], ['mobile-04.webp', 780, 1688], ['mobile-05.webp', 780, 1688], ['mobile-06.webp', 780, 1688], ['mobile-07.webp', 780, 1688]],
                 lead="The Jerky Fixx homepage from the hero to the family photos, plus the cart page. Each layout was designed for its screen, not just shrunk to fit."),
    fx="jerky",   # co-branded Jerky Fixx x DYAD intro + tape, lightning and lime demo (assets/jerky-fixx/)
    before="images/work/jerky-fixx/first-draft-hero.webp",
    before_label="The AI-only first draft",
    after="images/work/jerky-fixx/final-hero.webp",
    after_label="The final site",
    compare_alt="Jerky Fixx homepage hero",
    videos=[],
    summary=[
        "Jerky Fixx's first draft was an AI-only site. DYAD replaced it with a custom, human-directed design.",
        "The homepage uses the owners' own 3D models, retopologized and baked into lightweight web models: jerky and ingredients that erupt, hover and orbit as you scroll.",
        "It also covers ordering (a multi-flavor form with door drop off delivery), local SEO and a blog the owners' daughter, Aaliyah, runs.",
    ],
    body="""
<h2>The client</h2>
<p>Jerky Fixx is a family run, small batch beef jerky and carne seca business in Albuquerque, New Mexico, owned by Joseph Garduno and Sabrina Penn Garduno. There are 25 flavors, sold in a Small bag for $7 or a Large for $20. The brand has won Most Exotic Flavor and Best Booth at New Mexico Jerky Fest, and they're vendors at the New Mexico Jerky Fest Halloween Edition on Saturday, October 31, 2026 at Isleta Resort &amp; Casino.</p>
<p>The new website launched on <a href="https://jerkyfixx.com/" target="_blank" rel="noopener">jerkyfixx.com</a> in late October 2026. Their daughter, Aaliyah Garduno, who is studying web design, manages and maintains it, so it was built for her to run.</p>

<h2>Where it started: an AI-only first draft</h2>
<p>The family's first draft of a website had been made with AI only. Here's a scroll through it. It's tidy and readable, with a retro sunset graphic, a neon grid and a card grid of flavors. It also looks like it could belong to any snack brand. There are no photos of the family, the booth or the jerky, and nothing in it says why Jerky Fixx is different.</p>
<figure class="cs-film" style="margin:28px 0"><video muted loop playsinline preload="none" poster="/images/work/jerky-fixx/first-draft-poster.webp" width="1280" height="696" data-autoplay aria-label="Scroll-through of the AI-only first draft of the Jerky Fixx website"><source src="/videos/jerky-fixx-first-draft.mp4" type="video/mp4"></video></figure>
<p>We replaced it with a custom design directed by a human, built around the brand's own ideas and the family's own assets. If you're weighing the two approaches yourself, we wrote up <a href="/blog/ai-generated-website-vs-custom-design">why AI-only websites all look the same</a>.</p>

<h2>What we built</h2>
<ul>
<li><strong>An immersive, scroll-driven homepage.</strong> The owners' own 3D models of the jerky and ingredients erupt, hover and orbit as you scroll. The 3D scans started as high-poly GLB files. Vince retopologized and baked them into lightweight web models so they run on a phone.</li>
<li><strong>The lime takeover.</strong> A lime fills the whole screen and carries you into the next section.</li>
<li><strong>Warning tape and lightning.</strong> A "Flavors may cause addiction" tape motif and lightning give the whole site its attitude.</li>
<li><strong>Top sellers turntable.</strong> A swipeable 3D turntable of the top sellers with a heat gauge.</li>
<li><strong>An award trophy.</strong> The trophy rises in 3D to show off the wins.</li>
<li><strong>A 25 flavor menu with a cart.</strong> Tap a flavor, pick a size and add it to the cart, with a dedicated cart page.</li>
<li><strong>The family story.</strong> A roadrunner video that reveals the logo, a family photo carousel, and a lab video with chapters.</li>
<li><strong>Finding and joining.</strong> A custom dealer map and a FIXX Fiends VIP Club waitlist.</li>
<li><strong>Ordering.</strong> A multi-flavor order form with door drop off delivery that feeds a Google Sheet and sends email notifications.</li>
<li><strong>Phone first details.</strong> A bottom tab bar on phones and bold legal pages in the brand's style.</li>
<li><strong>A branded loading screen.</strong> It sets the tone before the page appears.</li>
</ul>

<h2>Built to be found</h2>
<p>The site is built with local search in mind: structured data, an llms.txt file, a sitemap, Google Search Console and IndexNow. There's also an SEO blog written by Aaliyah that publishes twice a week automatically. For what goes into that kind of work, see our <a href="/blog/website-redesign-checklist-new-mexico">website redesign checklist</a>.</p>

<h2>Why it looks like nobody else</h2>
<p>Choosing a web designer is like picking your favorite artist. When you choose DYAD, you get Vincent King's bold, immersive style: premium, $10,000 level design at a cost a small business can afford, backed by SEO. No generic AI layouts. No basic templates. Just a site built around your brand and your real story.</p>
<p>If you want a website that makes people stop scrolling, <a href="/web-design">see how our web design works</a> or book a call below.</p>
""",
),
dict(
    slug="rio-rancho-events-center",
    client="Rio Rancho Events Center",
    title='Rio Rancho Events Center: show graphics for the <span class="script">big</span> screens',
    plain_title="Rio Rancho Events Center: show graphics for the big screens",
    seo_title="Arena Video Board Graphics Case Study | DYAD Marketects",
    description="How DYAD designed 11 video board and ribbon board graphics for Rio Rancho Events Center shows, delivered within a week alongside the venue's marketing team.",
    service="video-photo-production",
    date="2026-10-21",
    updated="2026-10-21",
    image="images/rrec-card.webp",
    image_alt="Rio Rancho Events Center's hanging in-bowl video board showing the Be Like Blippi Tour graphic in a 3D arena render",
    tags=["Video Board", "Ribbon Board", "Graphic Design", "Video Editing"],
    videos=[
        dict(kind="film", src="videos/rrec-video-board.mp4", poster="images/work/rrec/video-board-poster.webp", w=1280, h=720,
             label="3D render of the in-bowl video board cycling through the show graphics"),
        dict(kind="tall", src="videos/rrec-video-board-tall.mp4", poster="images/work/rrec/video-board-tall-poster.webp", w=540, h=960,
             label="Vertical cut of the video board render"),
        dict(kind="film", wide=True, src="videos/rrec-ribbon-board.mp4", poster="images/work/rrec/ribbon-board-poster.webp", w=1280, h=720,
             label="3D render of the ribbon board cycling through the show graphics"),
    ],
    gallery=[
        dict(src="images/work/rrec/blippi-ribbon.webp", w=676, h=840, alt="The Be Like Blippi Tour graphic on the arena video board with Harlem Globetrotters graphics on the ribbon board below",
             caption="Live in the arena: Blippi on the video board, the Harlem Globetrotters on the ribbon board."),
        dict(src="images/work/rrec/fantexter-jokoy.webp", w=715, h=840, alt="The FanTexter graphic on the arena video board above the Jo Koy ribbon board graphic",
             caption="The FanTexter graphic up top, Jo Koy on the ribbon board."),
        dict(src="images/work/rrec/ribbon-side.webp", w=900, h=1200, alt="The ribbon board glowing along the upper level of the Rio Rancho Events Center",
             caption="The ribbon board wraps the arena's upper level."),
        dict(src="images/work/rrec/control-room.webp", w=900, h=1200, alt="The arena's video production switcher and control screen",
             caption="The control room that runs the boards."),
    ],
    summary=[
        "11 graphics for the arena's in-bowl video board (1920 x 1080) and ribbon board (2512 x 24).",
        "Five touring shows plus a FanTexter promo, all delivered within a week of kickoff.",
        "DYAD worked alongside the venue's marketing coordinator, Crystal Hostler, to keep everything on schedule.",
    ],
    body="""
<h2>The ask</h2>
<p>Rio Rancho Events Center reached out with a quick question: did DYAD take on freelance graphic design, and was there time free the following week? A lineup of upcoming shows needed graphics for the arena's two biggest screens, the in-bowl video board and the stadium ribbon board.</p>
<p>Their marketing coordinator, Crystal Hostler, had a lot on her plate. So DYAD stepped in to work right alongside her and keep the whole run on schedule, with every graphic due within a week of kickoff.</p>

<h2>What we made</h2>
<ul>
<li><strong>In-bowl video board, 1920 x 1080.</strong> One graphic each for Hudson Westbrook, Sesame Street, Jo Koy, Blippi and the Harlem Globetrotters, plus a FanTexter graphic inviting fans to text in for discount codes.</li>
<li><strong>Ribbon board, 2512 x 24 pixels.</strong> One graphic each for the five shows.</li>
</ul>
<p>That's eleven pieces in all, combining graphic design and video editing so each one feels alive on the board.</p>

<h2>Designing for a screen that's 2512 pixels wide and 24 pixels tall</h2>
<p>The ribbon board is more than 100 times wider than it is tall. At that size every letter has to earn its place. Names need to read from across the arena in a split second, artwork has to repeat cleanly along the length of the board, and nothing important can hide where half the crowd can't see it.</p>
<p>The video board is the opposite challenge: big, bright and seen by everyone at once. Each graphic leads with what fans need to know, in type that holds up all the way to the top rows.</p>

<h2>Working in tandem with an in-house team</h2>
<p>Not every project needs an outside agency to take over. Sometimes a great in-house team just needs another set of hands for a busy stretch. DYAD can plug into your existing marketing team, match your brand and your process, and deliver on your timeline.</p>

<h2>What they said</h2>
<blockquote><p>&ldquo;Exceptional service, style and quality! We highly recommend DYAD for all your needs. We will use these services again and again!&rdquo;</p><cite>Rio Rancho Events Center, Google review</cite></blockquote>
<blockquote><p>&ldquo;Love it! Love it! Love it!!! Shout-out Vincent King 🚀 for the help with this INCREDIBLE show graphics for our in-house video boards. Vincent went above and beyond for us at the Rio Rancho Events Center. We are so happy with the final product!!&rdquo;</p><cite>Rio Rancho Events Center</cite></blockquote>
<p>Need graphics for a screen, a stage or a whole season of events? <a href="/video-photo-production">See our video and photo production services</a> or book a call below.</p>
""",
),
dict(
    slug="lumanta",
    client="Lumanta",
    title='Lumanta: an immersive website for a <span class="script">mindful</span> app',
    plain_title="Lumanta: an immersive website for a mindful app",
    seo_title="Lumanta Website Design Case Study | DYAD Marketects",
    description="How DYAD Marketects took Lumanta from a BRAND$TORM to a logo refresh and a custom, immersive website with 3D particle motion on desktop and phone.",
    service="web-design",
    date="2026-10-20",
    updated="2026-10-26",
    image="images/lumanta-card.webp",
    image_alt="New Lumanta homepage with the Rise Above the Static headline, a gradient logomark and a woman with arms open on a beach",
    tags=["Website", "Logo Refresh", "BRAND$TORM", "3D Motion", "SEO"],
    live_url="https://lumanta.co/",
    live_label="Visit lumanta.co",
    logo="images/work/lumanta-mark.webp",
    top_cta="View the luxury design website",
    mockup=dict(src="images/work/lumanta-devices.webp", src_small="images/work/lumanta-devices-1000.webp", w=2000, h=1303,
                alt="The new Lumanta website on a desktop monitor, a tablet and a phone"),
    screens=dict(folder="images/work/lumanta-screens",
                 desktop=[["desktop-01.webp", 1440, 900], ["desktop-02.webp", 1440, 812], ["desktop-03.webp", 1440, 812], ["desktop-04.webp", 1440, 812], ["desktop-05.webp", 1440, 812], ["desktop-06.webp", 1440, 812], ["desktop-07.webp", 1440, 812], ["desktop-08.webp", 1440, 812], ["desktop-09.webp", 1440, 812], ["desktop-10.webp", 1440, 812], ["desktop-11.webp", 1440, 812], ["desktop-12.webp", 1440, 812], ["desktop-13.webp", 1440, 812], ["desktop-14.webp", 1440, 812], ["desktop-15.webp", 1440, 812], ["desktop-16.webp", 1440, 812], ["desktop-17.webp", 1440, 812], ["desktop-18.webp", 1440, 812]],
                 mobile=[["mobile-01.webp", 780, 1328], ["mobile-02.webp", 780, 1328], ["mobile-03.webp", 780, 1328], ["mobile-04.webp", 780, 1328], ["mobile-05.webp", 780, 1328], ["mobile-06.webp", 780, 1328], ["mobile-07.webp", 780, 1328], ["mobile-08.webp", 780, 1328], ["mobile-09.webp", 780, 1328], ["mobile-10.webp", 780, 1328], ["mobile-11.webp", 780, 1328], ["mobile-12.webp", 780, 1328]],
                 lead="The Lumanta homepage plus the Catch, Shift and Rise pages, top to bottom. Each layout was designed for its screen, not just shrunk to fit."),
    fx=True,   # co-branded Lumanta x DYAD particle intro + hover particle simulator (assets/lumanta/)
    before="images/work/lumanta-before.webp",
    before_label="The old lumanta.co",
    after="images/work/lumanta-after.webp",
    after_label="The new site",
    compare_alt="Lumanta homepage",
    videos=[
        dict(kind="desktop", src="videos/lumanta-desktop.mp4", poster="images/work/lumanta-desktop-poster.webp", w=1280, h=720,
             label="Desktop scroll-through of the new Lumanta website"),
        dict(kind="phone", src="videos/lumanta-phone.mp4", poster="images/work/lumanta-phone-poster.webp", w=540, h=1202,
             label="Phone scroll-through of the new Lumanta website"),
    ],
    summary=[
        "Started with a BRAND$TORM with founder Julie McCord, then a logo refresh, then a fully custom website.",
        "The site is hand built, with no templates: a 72,000 particle logo intro, scroll-driven 3D motion and touch interaction on phones.",
        "It's built with search in mind, from titles and share cards to three new pages, Catch, Shift and Rise, written for people searching how to let go of negative thoughts.",
    ],
    body="""
<h2>The client</h2>
<p>Lumanta is a thought-awareness app from founder Julie McCord, built around three simple steps: Catch, Shift and Rise. You catch a negative, fearful or judgmental thought with a single tap, notice it without judgment and let it go. No journaling, no analyzing, no judging yourself. Its tagline says it best: rise above the static.</p>
<p>The new website is now live at <a href="https://lumanta.co/" target="_blank" rel="noopener">lumanta.co</a>, with the app coming soon. Julie needed a brand and a website that feel as calm, clear and uplifting as the experience itself.</p>

<h2>Step one: the BRAND$TORM</h2>
<p>Every DYAD project starts with a BRAND$TORM, our discovery consultation. We sat down with Julie to get to the heart of Lumanta: who it's for, how it should feel, and what makes it different from every other wellness app on the shelf. That conversation shaped every decision that came after it, from the colors to the way the site moves.</p>

<h2>Step two: a logo refresh</h2>
<p>Next we refreshed the logo. The logomark is a glowing ring that breaks into particles at the top, like a thought lifting away. It's set in a warm to cool gradient of ember orange, glow pink, lumen blue and aurora aqua, with Dazzle Unicase lettering that feels light and modern. That ring became the backbone of the whole website.</p>

<h2>Step three: a website you feel, not just read</h2>
<p>Most sites tell you what a brand is about. We wanted Lumanta's site to let you feel it. A few of the moments we built:</p>
<ul>
<li><strong>A particle intro.</strong> The logomark assembles from 72,000 particles, then the camera flies through the ring and into the site.</li>
<li><strong>A cinematic hero.</strong> A full-screen video with the Rise Above the Static headline, where the O in ABOVE is the logomark itself.</li>
<li><strong>Catch, Shift, Rise.</strong> Three color cards slide up over the hero, each with an icon that draws itself, and each opens its own page.</li>
<li><strong>The static.</strong> A scroll-driven 3D particle story where noise gathers into the logo and the night sky dawns into Lumanta's soft off white. Move your cursor, or your finger on a phone, and the particles move with you.</li>
<li><strong>The app walkthrough.</strong> A phone that stays pinned while you scroll through the app's three steps: one big Negative button, Judgmental and Fear below, in soft daylight colors with glowing particle rings behind it.</li>
</ul>
<p>Every section has its own entrance animation, and it all works on phones too, with touch built in rather than bolted on. Visitors who prefer reduced motion get a calm, still version automatically.</p>

<h2>Pages built to be found</h2>
<p>After launch we refreshed the brand around Julie's messaging and added three pages, one for each step of the method: <a href="https://lumanta.co/catch" target="_blank" rel="noopener">Catch</a>, <a href="https://lumanta.co/shift" target="_blank" rel="noopener">Shift</a> and <a href="https://lumanta.co/rise" target="_blank" rel="noopener">Rise</a>. Each one answers a real question people search, like how to let go of negative thoughts, with a full-bleed photo hero, a scroll story where the logo's particles act out the step, and a small demo you can tap.</p>
<p>The &ldquo;Become a founding member&rdquo; form saves every signup to a shared sheet and alerts both Julie and our team, with a privacy-friendly &ldquo;I'm not a robot&rdquo; check and a cookie notice that keeps visitors in control.</p>

<h2>Luxury design, backed by SEO</h2>
<p>This is a $10,000 level website at a cost a startup can actually afford. And it isn't just pretty. It's built with search in mind from day one: clear page titles and descriptions, social share cards, fast loading video sized for phones, and an llms.txt file that helps AI assistants describe Lumanta accurately. Now that it's live at lumanta.co, it's built to be found. Want to know what goes into that? Here's our <a href="/blog/website-redesign-checklist-new-mexico">website redesign checklist</a>.</p>

<h2>Why it looks like nobody else</h2>
<p>Choosing a web designer is like picking your favorite artist. When you choose DYAD, you get Vincent King's bold, immersive style. No boring AI layouts. No basic Wix or WordPress templates. Just a site built from scratch around your brand, so visitors feel it the moment it loads.</p>
<p>If you want a website that makes people stop scrolling, <a href="/web-design">see how our web design works</a> or book a call below.</p>
""",
)]
