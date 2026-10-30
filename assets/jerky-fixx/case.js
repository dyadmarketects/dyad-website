/* Jerky Fixx case study extras (dyadgrow.com/work/jerky-fixx)
   1. Co-branded Jerky Fixx x DYAD intro: warning tape fills as the percent climbs, then the lime floods the screen.
      Plays on every load; skipped for reduced motion (the inline script in the page never adds .jx-intro).
   2. "Try it yourself": warning tape, lightning that follows your cursor or finger, and press and hold to fill with lime.
   3. Keeps the "View the award winning jerky website" bar pinned just under the site header. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches;
  var TAPE = "WARNING! FLAVORS MAY CAUSE ADDICTION";

  function fillTracks(scope) {
    var spans = "";
    for (var i = 0; i < 10; i++) spans += "<span>" + TAPE + "</span>";
    (scope || document).querySelectorAll(".jx-track").forEach(function (t) { t.innerHTML = spans; });
  }
  fillTracks();

  /* ---------- 3. pinned bar ---------- */
  var bar = document.querySelector(".lx-bar"), head = document.querySelector("header.top");
  function placeBar() { if (bar && head) bar.style.top = head.offsetHeight + "px"; }
  placeBar(); addEventListener("resize", placeBar);

  /* ---------- 1. intro loader ---------- */
  var loader = document.querySelector(".jx-loader");
  window.scrollTo(0, 0);
  if (loader && root.classList.contains("jx-intro")) runLoader();
  function runLoader() {
    document.body.style.overflow = "hidden";
    var pctEl = loader.querySelector(".jx-pct span"), fill = loader.querySelector(".jx-fill");
    var icons = loader.querySelectorAll(".jx-icons img");
    var t0 = performance.now(), dur = 2800, exiting = false, raf;
    loader.classList.add("jx-show");
    function tick(now) {
      var p = Math.min(1, (now - t0) / dur);
      p = 1 - Math.pow(1 - p, 2.2);
      fill.style.width = (p * 100).toFixed(1) + "%";
      pctEl.textContent = Math.round(p * 100);
      icons.forEach(function (im, i) { im.classList.toggle("on", p > (i + 1) / 4); });
      if (p < 1) raf = requestAnimationFrame(tick); else setTimeout(exit, 280);
    }
    raf = requestAnimationFrame(tick);
    loader.addEventListener("click", exit);
    addEventListener("keydown", function (e) { if (e.key === "Escape") exit(); });
    function exit() {
      if (exiting) return; exiting = true; cancelAnimationFrame(raf);
      pctEl.textContent = "100"; fill.style.width = "100%";
      loader.classList.add("jx-leaving");
      setTimeout(function () { loader.classList.add("jx-fade"); }, 900);
      setTimeout(function () {
        loader.remove(); root.classList.remove("jx-intro"); document.body.style.overflow = "";
      }, 1500);
    }
  }

  /* ---------- 2. tape, lightning and lime demo ---------- */
  var stage = document.querySelector(".jx-sim");
  if (!stage) return;
  var canvas = stage.querySelector("canvas"), ctx = canvas.getContext("2d");
  var limeEl = stage.querySelector(".jx-lime2"), hint = stage.querySelector(".lx-hint");
  var dpr = 1, w = 0, h = 0, bolts = [], running = false, visible = false, lastBolt = 0, lastAuto = 0;
  var px = 0.5, py = 0.5;
  var lime = { r: 0, target: 0, x: 0.5, y: 0.5 };
  if (hint) hint.textContent = reduced ? "Press and hold to fill with lime"
    : (finePointer ? "Move for lightning. Press and hold for lime" : "Touch for lightning. Hold for lime");

  function size() {
    var r = stage.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    w = r.width; h = r.height;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  size(); addEventListener("resize", size);

  function jag(ax, ay, bx, by, d, out) {
    var dx = bx - ax, dy = by - ay, len = Math.sqrt(dx * dx + dy * dy);
    if (len < 9) { out.push([bx, by]); return; }
    var mx = (ax + bx) / 2 + (-dy / len) * (Math.random() - 0.5) * d;
    var my = (ay + by) / 2 + (dx / len) * (Math.random() - 0.5) * d;
    jag(ax, ay, mx, my, d / 2, out); jag(mx, my, bx, by, d / 2, out);
  }
  function makeBolt(x, y) {
    var sx = x + (Math.random() - 0.5) * w * 0.3, pts = [[sx, 0]];
    jag(sx, 0, x, y, Math.max(40, y * 0.35), pts);
    var branches = [], n = 1 + Math.floor(Math.random() * 3);
    for (var i = 0; i < n; i++) {
      var k = pts[Math.floor(pts.length * (0.25 + Math.random() * 0.5))];
      var ex = k[0] + (Math.random() - 0.5) * w * 0.35, ey = k[1] + h * (0.1 + Math.random() * 0.2);
      var bp = [k]; jag(k[0], k[1], ex, ey, 40, bp); branches.push(bp);
    }
    bolts.push({ t: performance.now(), life: 700, main: pts, branches: branches });
    start();
  }
  function stroke(pts, a, wd) {
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    for (var i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.globalAlpha = a; ctx.lineWidth = wd; ctx.stroke();
  }
  function frame(now) {
    ctx.clearRect(0, 0, w, h);
    ctx.lineJoin = "round"; ctx.lineCap = "round";
    bolts = bolts.filter(function (b) { return now - b.t < b.life; });
    bolts.forEach(function (b) {
      var age = (now - b.t) / b.life, a = (1 - age) * (0.75 + Math.random() * 0.25);
      ctx.shadowColor = "#ff66c4"; ctx.shadowBlur = 18;
      ctx.strokeStyle = "#ff66c4"; stroke(b.main, a * 0.6, 10);
      b.branches.forEach(function (br) { stroke(br, a * 0.45, 6); });
      ctx.shadowBlur = 0; ctx.strokeStyle = "#ffffff";
      stroke(b.main, a, 3.4);
      b.branches.forEach(function (br) { stroke(br, a * 0.85, 2); });
    });
    ctx.globalAlpha = 1;
    /* lime fill eases toward its target, from wherever you pressed */
    lime.r += (lime.target - lime.r) * (lime.target > lime.r ? 0.045 : 0.12);
    if (Math.abs(lime.target - lime.r) < 0.002) lime.r = lime.target;
    limeEl.style.setProperty("--r", (lime.r * 150).toFixed(2) + "%");
    limeEl.style.setProperty("--x", (lime.x * 100).toFixed(1) + "%");
    limeEl.style.setProperty("--y", (lime.y * 100).toFixed(1) + "%");
    stage.classList.toggle("jx-full", lime.r > 0.92);
    if (!reduced && visible && now - lastAuto > 3200 && !bolts.length && !pressing) {
      lastAuto = now; makeBolt(w * (0.15 + Math.random() * 0.7), h * (0.35 + Math.random() * 0.3));
    }
    if (visible && (bolts.length || lime.r !== lime.target || !reduced)) raf2 = requestAnimationFrame(frame);
    else running = false;
  }
  var raf2 = 0;
  function start() { if (running || !visible) return; running = true; raf2 = requestAnimationFrame(frame); }

  var pressing = false;
  function pos(e) {
    var r = stage.getBoundingClientRect();
    return [Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)), Math.max(0, Math.min(1, (e.clientY - r.top) / r.height))];
  }
  function strike(e, force) {
    if (reduced) return;
    var now = performance.now();
    if (!force && now - lastBolt < 150) return;
    lastBolt = now; var p = pos(e); makeBolt(p[0] * w, p[1] * h);
  }
  function press(e) {
    var p = pos(e); lime.x = p[0]; lime.y = p[1]; lime.target = 1; pressing = true;
    strike(e, true); start();
  }
  function release() { pressing = false; lime.target = 0; start(); }
  stage.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse" || pressing) strike(e); });
  stage.addEventListener("pointerdown", press);
  stage.addEventListener("pointerup", release);
  stage.addEventListener("pointercancel", release);
  stage.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") release(); });
  stage.addEventListener("keydown", function (e) {
    if ((e.key === " " || e.key === "Enter") && !pressing) { e.preventDefault(); lime.x = 0.5; lime.y = 0.5; lime.target = 1; pressing = true; if (!reduced) makeBolt(w / 2, h / 2); start(); }
  });
  stage.addEventListener("keyup", function (e) { if (e.key === " " || e.key === "Enter") release(); });
  stage.addEventListener("blur", release);

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (en) { visible = en.isIntersecting; if (visible) { size(); start(); } });
    }, { rootMargin: "100px" }).observe(stage);
  } else { visible = true; start(); }
})();
