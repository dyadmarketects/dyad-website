"""Vincent King's journey: one entry per timeline item.

This file is the single source for BOTH timelines:
  * the homepage timeline cards (year, title, summary, and an "Immerse" link), written into index.html
    between <!--journey:cards--> markers by _tools/blog.py
  * the in-depth timeline on /about (id anchor, full story, photos, YouTube videos, sources)

To add or change a milestone, edit this file only and run `python3 _tools/blog.py`.
Images live in assets/img/journey/<name>.webp (plus <name>-700.webp); sizes come from _tools/journey_dims.json.
Keep copy conversational and in Vince's first person voice, no em or en dashes, and only facts Vince has given.
"""

# Bump this when you change the timeline content, so Google sees /about as updated (sitemap lastmod).
UPDATED = "2026-10-18"

J = [
dict(id="born-1990", year="'90", title="Two worlds, one house",
  summary="Born in 1990 and raised by an electrical engineer father and an artist mother who homeschooled us to think critically. Logic and creativity were never separate rooms in that house.",
  story="""<p>I was born at the end of 1990 and raised by an electrical engineer father and an artist mother who homeschooled us to think critically. Logic and creativity were never separate rooms in that house.</p>"""),

dict(id="arrow-to-the-sun", year="'03", title="Animating a planetarium dome at 12",
  summary="I took my passion for graphic design, immersive media, and 2D/3D animation and started applying it on purpose. I joined the UNM LodeStar Astronomy Production Team as a 3D model designer and animator on Arrow to the Sun, a full dome 360 production based on Gerald McDermott's Caldecott Medal winning book.",
  story="""<p>At 12, I joined the UNM LodeStar Astronomy production team as a 3D model designer and animator on <em>Arrow to the Sun</em>, a fulldome 360 production for the planetarium at the New Mexico Museum of Natural History and Science. It&rsquo;s based on Gerald McDermott&rsquo;s Caldecott Medal winning children&rsquo;s book, and it grew into a co-venture between McDermott and UNM&rsquo;s ARTS Lab.</p>
<p>The timing was special. Fulldome theaters had gone from a handful to more than 200 worldwide, with new ones opening almost weekly, and UNM was a leader in exploring what domes could do beyond planetarium shows. <em>Arrow to the Sun</em> was UNM&rsquo;s first fulldome production, made as the book was released in a 30th anniversary edition. It pairs a Native American tale with a first introduction to the solar system, and the team made a point of developing dome content with members of traditionally underrepresented groups.</p>
<p>The reel below is a 2.5 minute collection of clips from the production while it was in progress, showing the book&rsquo;s world coming to life on the dome.</p>""",
  videos=[("vKI05gGzwNM", "Arrow to the Sun fulldome production, work in progress")],
  media=[("arrow-storyboard-wall", "Storyboards and concept art for the production, stitched into one long panorama"),
         ("arrow-dome-frame", "A fulldome frame. Domes are rendered as a circle that wraps over the audience")]),

dict(id="fulldome-course", year="'04", title="First of its kind at UNM",
  summary="At 13, I enrolled as a student and teaching assistant in UNM's college level Full Dome Production course, the world's first full semester course of its kind when it launched in spring 2004.",
  story="""<p>At 13, I enrolled as a student and teaching assistant in a college level course most adults had never heard of. In spring 2004, UNM began offering the world&rsquo;s first full semester course in Full Dome Production.</p>
<p>Students from fine arts, science and engineering backgrounds worked in collaborative teams to create 1 to 3 minute films for an immersive dome. Frames were built as 3200 x 3200 pixel images at 30 frames per second, through a pipeline of specialized software that was barely documented. Almost everyone walked in with one piece of the skill set and quickly hit parts of the process that were completely new. The team approach was the point: pool your skills, split the work, and spend your energy on the story instead of the software.</p>
<p>The class pushed us to think about what makes a dome different. What does it mean when something enters from behind you instead of in front? How does peripheral vision change motion, scale and time? The big thrill came at the end of the semester, when our work played on LodeStar&rsquo;s 55 foot dome at a public screening. LodeStar, built in 2000 at the New Mexico Museum of Natural History and Science, was only the second digital dome theater of its kind in the world.</p>""",
  media=[("course-stomped", "&ldquo;Stomped&rdquo; by Thomas Keegan and Vincent King, featured as Figure 3 in the course paper")],
  sources=[("Hue Walker, &ldquo;Inventing a Collaborative Full Dome Production Course,&rdquo; ARTS Lab, University of New Mexico", None)]),

dict(id="maya-skies", year="'09", title="Maya Skies, then architecture",
  summary="Graduated from Albuquerque Academy, then took my senior project to the UNM ARTS Lab as a 3D modeler and animator on the full dome production Tales of the Maya Skies, where my animations were shown worldwide. After that I studied architecture at UNM.",
  story="""<p>I graduated from Albuquerque Academy in 2009 and took my senior project to the UNM ARTS Lab. As the lab&rsquo;s Advanced Multimedia Assistant, I was part of the team responsible for <a href="http://www.mayaskies.org/" target="_blank" rel="noopener"><em>Tales of the Maya Skies</em></a>, an educational, immersive 360 degree animated film about ancient Maya astronomy that has been shown around the globe.</p>
<p>ARTS Lab supports experimental artistic research and production at UNM in emerging technologies. It&rsquo;s an interdisciplinary center connecting art, science, business and technology, with a vision of becoming a key catalyst for the education and research that grows an advanced media industry in New Mexico. It lives in the Digital Garage, a black box space built for performance, experimentation and research in digital graphics, sound and real time immersive projection. The Garage&rsquo;s major resources include a 15 foot hemispheric dome built in partnership with the LodeStar Astronomy Center, a large motion capture system and a sizable green screen environment.</p>
<p>The ARTS Lab trained me in Maya, Rhino 3D and Final Cut Pro. In my free time I taught myself Photoshop, After Effects and Premiere Pro.</p>
<h4>Then architecture</h4>
<p>After Maya Skies I studied architecture at UNM. In my second year, an assignment asked us to illustrate the transformation between organic and mechanical, and to make it symmetrical. I said no. Living things aren&rsquo;t perfectly symmetrical; our hearts sit off to the left. I tried to draw the conversation between organic asymmetry and our idea of fabricated, precise symmetry. Every imperfection in each evolutionary iteration creates a reason to grow.</p>""",
  videos=[("_2zCQmMOKCo", "Tales of the Maya Skies: the Hero Twins, the birth of corn and the creation of the Sun and the Moon")],
  media=[("maya-skies-screening", "Guests at a screening in the ARTS Lab&rsquo;s Digital Garage"),
         ("maya-skies-guests", "Visitors taking in the dome"),
         ("garage-dome-spheres", "Testing content on the Digital Garage&rsquo;s 15 foot dome"),
         ("garage-dome-shoot", "A shoot in front of the dome"),
         ("mocap-markers", "Suited up with motion capture markers"),
         ("dome-audience", "A full house waiting for a dome screening"),
         ("arch-organic-mechanical", "Organic vs. Mechanical, pencil, second year of architecture school"),
         ("arch-mirrored-sky", "Mirrored Sky gazebo: modeled in Rhino 3D, drafted in pencil and pen, then fabricated in wood. Inspired by a fictional city built on a river, each side is a parallel dimension")]),

dict(id="skateboard-simulation", year="'10", title="The DYAD within, validated",
  summary="At the ARTS Lab I worked on full dome animation, CNC routing, and a 360 degree immersive skateboarding video game. It aired on Discovery Channel Canada, was unveiled at Mesa del Sol in front of the governor, and made Albuquerque Business First. The rebel and the nerd, creating in unison.",
  story="""<p>This is where three of my passions collided: skateboarding, immersive media and science. At the ARTS Lab I worked on fulldome animation, CNC routing and a futuristic skateboard simulation, a 360 degree immersive skateboarding game you ride on a real deck in front of the dome.</p>
<p>I was blessed with the opportunity to be featured in a Discovery Channel Canada episode about that exact mix, which documented our production of the simulation. The work was unveiled at Mesa del Sol in front of the governor and made Albuquerque Business First. The rebel and the nerd, creating in unison.</p>
<p>The lab&rsquo;s interactive dome work also included HexDex, a six sided motion platform designed by UNM computer science professor Joe Kniss for &ldquo;the feel and fun of skateboarding without the road rash.&rdquo; Two HexDexes sit inside a larger rotating platform, and in the asteroids game shifting your weight steers the view.</p>""",
  media=[("hexdex-crouch", "Dropping in on the skateboard simulation under the dome"),
         ("hexdex-two-riders", "Testing the board in front of the dome"),
         ("hexdex-board-closeup", "The deck, trucks and springs that make the board feel real"),
         ("hexdex-rider-dome", "Riding through a sea of spheres"),
         ("hexdex-spheres-sky", "Talking through a scene on the dome"),
         ("immersive-room-1", "HexDex motion platforms running the asteroids game"),
         ("immersive-room-2", "The asteroids game wraps around the room"),
         ("immersive-room-3", "Navigating the asteroid field"),
         ("immersive-asteroids-dome", "The asteroid field on the dome"),
         ("hexdex-hexapod", "Testing a HexDex platform"),
         ("immersive-room-logos", "The immersive room, a collaboration between UNM Computer Science, the School of Architecture and ARTS Lab"),
         ("build-empty-space", "The space before the build"),
         ("build-platform-floor", "Laying out the rotating platform floor"),
         ("build-dome-collage", "Building a portable dome"),
         ("build-dome-shell", "Raising the portable dome shell"),
         ("demo-dome-spiral", "Guests at a portable dome demo"),
         ("demo-dome-nebula", "A demo on the portable dome"),
         ("opening-crowd", "A packed house at the unveiling")],
  sources=[("UNM School of Engineering, &ldquo;HexDex takes gaming to new dimensions&rdquo; (2011)", "https://engineering-dev.unm.edu/news-archive/news/2011/11/hexdex-takes-gaming-to-new-dimensions.html")]),

dict(id="summer-majik", year="'11 &amp; '12", title="Giving back",
  summary="Lead Instructor for Summer Majik, a STEM initiative of the UNM Summer Enrichment camp run by the late Debra Johns, a longtime Albuquerque educator. Across two semesters, in 2011 and 2012, I taught middle school students production basics with professional software, and they animated the stories of influential African American figures in New Mexico history.",
  story="""<p>I was Lead Instructor for Summer Majik, a STEM initiative of the UNM Summer Enrichment camp run by the late Debra Johns, a longtime Albuquerque educator. I taught it for two semesters, in 2011 and 2012.</p>
<p>Across an intensive two week program, I taught middle school students production basics with professional software: After Effects animation, Photoshop, GarageBand audio and chroma key compositing. They researched influential African American figures in New Mexico history and animated their stories with original audio and voiceover, then presented them to families and faculty.</p>
<p>Two of my 2012 class&rsquo;s films are below, telling the stories of the Buffalo Soldiers and Estevanico the Explorer.</p>""",
  videos=[("cF3Vq4MJGVE", "Summer Majik 2012 student animation"), ("oP_dXcxMBB0", "Summer Majik 2012 student animation")],
  media=[("majik-high-five", "Celebrating a finished scene"),
         ("majik-gathered", "Students gathered around a project in progress"),
         ("majik-kneeling", "Working through an After Effects timeline with a student"),
         ("majik-pointing", "Walking a student through his edit")]),

dict(id="film-internship", year="'12", title="Architecture major, film intern",
  summary="Earned a spot in the exclusive UNM IFDM (Interdisciplinary Film and Digital Media) summer internship, even as an architecture major. I created a full dome short film with 360 HDR photography, stitching, After Effects, and Autodesk Maya.",
  story="""<p>In 2012 I earned a spot in UNM&rsquo;s intensive IFDM (Interdisciplinary Film and Digital Media) summer internship at the ARTS Lab, even as an architecture major.</p>
<p>The internship produced <em>Chaco Canyon: Earth, Time, People</em>, a fulldome film built from 360 degree HDR photography. That meant shooting bracketed panoramas on location, stitching them so they sit correctly on a dome, then bringing them into After Effects and Autodesk Maya, where a flat photo becomes a space you can move through.</p>""",
  videos=[("pCSQT8CY68E", "Chaco Canyon: Earth, Time, People (ARTS Lab summer internship)")],
  media=[("ifdm-chaco-wall", "A 360 degree HDR panorama of the ruins at Chaco Canyon"),
         ("ifdm-chaco-night-rig", "A night shoot at Chaco with the panoramic camera rig"),
         ("ifdm-camera-rig", "Setting up the panoramic rig"),
         ("ifdm-chaco-maya", "A Chaco panorama mapped onto 3D geometry in Autodesk Maya"),
         ("ifdm-tent-rocks", "Another stitched HDR panorama from New Mexico")]),

dict(id="explore-media-kunm", year="'12 &amp; '13", title="Recalibrating into marketing",
  summary="Architecture tickled the fascination but didn't scratch the itch, so I recalibrated. I joined ExploreMedia360, a New Mexico marketing agency start-up focused on graphic design, web design, and 360 tours in partnership with Google Maps, and designed for KUNM, Albuquerque's public radio station.",
  story="""<p>Architecture tickled the fascination but didn&rsquo;t scratch the itch, so I recalibrated toward marketing.</p>
<h4>ExploreMedia360</h4>
<p>Working for ExploreMedia, one of my tasks was moderating Google tours for our clients, giving their customers an immersive experience of our clients&rsquo; establishments through Google Maps. 360&deg; images were sent to me and I stitched the panoramas to one another so they were oriented correctly, giving the viewer a clear, easily navigable virtual space to explore. By contract, I also scrubbed through every pano and blurred all human faces and license plates. A couple of those clients were DriveTime Used Cars, a nationwide company, and Art Gone Wild Galleries in Santa Fe, NM and Key West, FL.</p>
<p>As ExploreMedia&rsquo;s graphic designer, I created book covers and multiple iterations of website mockups in Photoshop and After Effects. Some of my clients were Trend Magazine (Santa Fe), Art Gone Wild (Santa Fe), Bon Marche (Santa Fe) and Al&rsquo;s Upholstery (Albuquerque).</p>
<h4>KUNM</h4>
<p>I also worked as the Graphic Designer for the KUNM Development Department, designing a monthly electronic newsletter, web buttons and icons, direct mail pieces from response cards to envelopes, advertising specialties, print ads, bumper stickers and more. I&rsquo;d help with bulk mailings and other clerical and customer service work too.</p>
<p>Designing for a nonprofit taught me to multitask and prioritize, because I had to produce multiple iterations of ads and articles quickly, on tight schedules, to bring in essential donations.</p>""",
  media=[("kunm-zounds", "Zounds, KUNM&rsquo;s monthly web and print newsletter. As the station&rsquo;s sole graphic designer I proofread articles, built layouts in InDesign and created ads, logos and campaign videos"),
         ("kunm-auction-flyer", "KUNM&rsquo;s 2012 Gift of Community Auction")]),

dict(id="cnm", year="'17", title="Architecture meets marketing",
  summary="After the business sold, I went back to school at CNM and studied both disciplines side by side, graduating Phi Theta Kappa in Digital Marketing &amp; Communications. Structure and story, same toolkit.",
  story="""<p>After the business sold, I went back to school at CNM (Central New Mexico Community College) and studied both disciplines side by side. My studies covered graphic design and digital communications, and I graduated Phi Theta Kappa in Digital Marketing &amp; Communications. Structure and story, same toolkit.</p>
<p>Some of the class projects got delightfully whimsical. Here are two of them, including <em>Xplode</em>.</p>""",
  videos=[("ROCbPvl6z3I", "CNM class project"), ("dp6cxqxc_gk", "CNM class project")]),

dict(id="century-sign-builders", year="'19", title="Design grounded by gravity",
  summary="As an Environmental Graphic Designer and Production Artist at Century Sign Builders, I took signage from concept to design to production to installation, building ADA compliant wayfinding from site surveys and architectural plans.",
  story="""<p>In 2019 I worked as an Environmental Graphic Designer and Production Artist at Century Sign Builders, a local sign design and manufacturing company.</p>
<p>Every team had three roles. A project manager assessed the customer&rsquo;s needs, ran site surveys and met with contractors and architects. An environmental graphic designer created visually dynamic, ADA compliant, branded wayfinding based on the customer&rsquo;s needs and the environment, along with full production specs and installation guides. A production artist took approved designs and formatted them for production.</p>
<p>The unique thing about my team was that it was just me and a project manager, so I had to learn everything quickly, from concept to design to production to installation. When my project manager was out on an extended leave, I worked directly with clients like Utah Navajo Health System, Inc. to take the entire project from start to finish.</p>
<p>I used architectural plans and site visit assessments to create to scale renderings, not only for the client to see, but for our production team to fabricate the signage in house and our installation team to mount it. Every specification had to be spelled out, from quantities, messages and locations to substrates, sizes, hardware and mounting technique. That&rsquo;s how the client and every department stayed on the same page.</p>
<p>This role was a great combination of data and design. Architecture and engineering. Form and function.</p>""",
  media=[("century-signage-package", "Signage packages assembled in InDesign with master pages, styles and page numbering, so each client got a package catered to their environment"),
         ("century-storefront-vinyl", "To scale storefront rendering for the Navajo Regional Behavioral Health Authority"),
         ("century-vinyl-specs", "Privacy vinyl with a Navajo decorative print lets natural light in while keeping the interior confidential"),
         ("century-unhs-sign", "A custom wall mounted sign designed to join Utah Navajo Health System&rsquo;s existing sign family"),
         ("century-unhs-hardware", "Hardware and mounting details, rendered and specified for approval"),
         ("century-dental-clinic", "A suspended sign from the Utah Navajo Health System sign family, installed")]),

dict(id="dsi", year="'20", title="Building marketing at DSI",
  summary="Started as a Graphic Designer, grew into Marketing Manager &amp; Senior Graphic Designer, and built and now lead an entire marketing department running campaigns across web, print, social, email, events, and video for six plus years.",
  story="""<p>In 2020, COVID layoffs moved me on from Century Sign Builders, and I dove even further into the digital side of design as a Graphic Designer at DSI, Document Solutions, Inc. Rather than designs grounded by gravity, my designs were now grounded by customer connection, both external and internal: driving sales, supporting technical teams and making internal operations run better.</p>
<p>I grew into Marketing Manager &amp; Senior Graphic Designer, and built and now lead an entire marketing department running campaigns across web, print, social, email, events and video. That includes a full redesign of <a href="https://www.dsinm.com" target="_blank" rel="noopener">DSI&rsquo;s website</a>, rebuilt page by page around customer and employee experience with real team photos and SEO copy, and the March to the Madness lead generation event, where a $400 budget turned into $1.9M in profit.</p>
<p>I was one of the first non-sales employees to receive DSI&rsquo;s Presidential Trip (President&rsquo;s Club), earned for revenue-generating work, brand visibility campaigns, a comprehensive website rebrand and embodying DSI&rsquo;s core values.</p>""",
  media=[("@/images/dsi-website.jpg", "DSI&rsquo;s redesigned website")]),

dict(id="rebel-meets-professional", year="'22", title="Rebel meets professional",
  summary="Stopped treating the skateboarder and the strategist as different people. Channeled the same resourcefulness into client work, and it started showing.",
  story="""<p>I stopped treating the skateboarder and the strategist as different people. I channeled the same resourcefulness into client work, and it started showing.</p>"""),

dict(id="classroom-to-career", year="'23", title="Classroom to career",
  summary="I volunteer my time presenting to and mentoring students on the jump from classroom to career, from hosting Junior Achievement students at DSI to speaking to CNM's Advanced Adobe Creative Suite class.",
  story="""<p>I continue to volunteer my time presenting to and mentoring students on transitioning from classroom to career.</p>
<h4>eCademy Junior Achievement at DSI, 2023</h4>
<p>On April 18, 2023, about 40 students from <a href="https://ecademy.aps.edu/" target="_blank" rel="noopener">eCademy High School</a> visited DSI&rsquo;s Albuquerque headquarters with Junior Achievement. One of the best ways for students to learn about the world of work is to spend time on site with a business, get a feel for a professional workplace and ask questions about a field they&rsquo;re interested in.</p>
<p>I presented &ldquo;Net-iquette,&rdquo; a topic I coined for best practices on social media so you present your best self to potential employers. I also talked about the importance of identifying your passions and finding a job where you can do just that.</p>
<p>Our team ran a series of hands on activities on career research and preparation, job hunting tools, professionalism and ethics in the workplace, and professional action plans. Students were able to:</p>
<ul>
<li>Recognize career clusters and potential jobs that align with their passions</li>
<li>Professionally problem solve workplace scenarios</li>
<li>Understand why researching the requirements for a position matters</li>
<li>Develop job hunting tools like networking, resumes and interviewing skills</li>
<li>Identify the next steps in their own career preparation</li>
</ul>
<p>It was a great opportunity to show Vincent King&rsquo;s shared value with DSI of Selfless Service.</p>
<h4>CNM Advanced Adobe Creative Suite, 2024</h4>
<p>In 2024 I presented to Sonia Crawford&rsquo;s Advanced Adobe Creative Suite class at CNM, sharing my college experience and how to best prepare yourself for a smooth transition from the classroom to a career.</p>""",
  media=[("ja-presenting", "Presenting &ldquo;Net-iquette&rdquo; to eCademy students at DSI"),
         ("ja-room", "About 40 eCademy students working through career activities at DSI"),
         ("ja-mentoring", "Talking careers with students at the table"),
         ("ja-students", "Students working on their professional action plans"),
         ("ja-warehouse-tour", "A behind the scenes tour of DSI&rsquo;s warehouse"),
         ("ja-presenting-2", "On finding a job that lets you do what you&rsquo;re passionate about")]),

dict(id="houser-raspberry-ranch", year="'24", title="Growing a ranch brand",
  summary="I partnered with Houser Raspberry Ranch as their Marketing Specialist, leading PR, social media, email, web, branding and event planning, plus the full logo design and brand strategy for their Rusty Nail Saloon.",
  story="""<p>In 2024 I also partnered with Houser Raspberry Ranch in the Mora Valley as their Marketing Specialist. I lead their PR initiatives, social media content and management, email campaigns and website management.</p>
<p>The branding work covers business cards, menus, documentation, email signatures, flyers, a recruiting initiative, event planning, app development and more, plus comprehensive logo design and brand strategy for their Rusty Nail Saloon. Two years of consistent, on brand social content took the ranch&rsquo;s profile from 0 to 2.7K followers.</p>""",
  media=[("@/images/houser-cards.jpg", "Houser Raspberry Ranch business cards"),
         ("@/images/houser-instagram.jpg", "On brand social content for Houser Raspberry Ranch"),
         ("@/images/rusty-nail.jpg", "The Rusty Nail Saloon logo, rebuilt by hand in Illustrator")]),

dict(id="dyad-marketects", year="'26", title="DYAD Marketects is born",
  summary="Two forces, one system. A studio built on the belief that creativity and analytics were never actually competing, they just needed the right bridge. Based in Albuquerque, New Mexico.",
  story="""<p>Two forces, one system. DYAD Marketects is a studio built on the belief that creativity and analytics were never actually competing, they just needed the right bridge. DYAD stands for Duality Yields Agile Development.</p>
<p>Today I work across DSI, Houser Raspberry Ranch and DYAD Marketects, helping local businesses in Albuquerque and across New Mexico grow.</p>"""),
]
