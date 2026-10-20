/* Lumanta case study extras (dyadgrow.com/work/lumanta)
   1. Co-branded Lumanta x DYAD intro: the real Lumanta particle loader (72,000 points form the logomark,
      then fly through the ring). Plays on every load; skipped for reduced motion or no WebGL.
   2. "Try it yourself": the hover/touch particle simulator from the Lumanta site.
   3. Keeps the "View the luxury design website" bar pinned just under the site header.
   Uses assets/lumanta/particles.js (LumantaParticles + loadParticleData), copied from the lumanta-website repo. */
(function () {
  "use strict";
  var DATA = "/assets/lumanta/lumanta-particles.bin";
  var root = document.documentElement;
  var mobile = matchMedia("(max-width: 800px)").matches;
  var finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches;
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* tiny tween helpers (no GSAP on this site) */
  var ease = {
    out3: function (t) { return 1 - Math.pow(1 - t, 3); },
    inOut2: function (t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; },
    in2: function (t) { return t * t; },
    in3: function (t) { return t * t * t; }
  };
  function tween(obj, key, to, dur, delay, fn) {
    var from = null, t0 = performance.now() + delay * 1000;
    return function (now) {
      if (now < t0) return false;
      if (from === null) from = obj[key];
      var p = Math.min(1, (now - t0) / (dur * 1000));
      obj[key] = from + (to - from) * fn(p);
      return p >= 1;
    };
  }

  /* ---------- 3. sticky "view the site" bar sits under the sticky header ---------- */
  var bar = document.querySelector(".lx-bar"), head = document.querySelector("header.top");
  function placeBar() { if (bar && head) bar.style.top = head.offsetHeight + "px"; }
  placeBar(); addEventListener("resize", placeBar);

  if (typeof LumantaParticles !== "function") return;

  /* ---------- 1. intro loader ---------- */
  var loader = document.querySelector(".lx-loader");
  window.scrollTo(0, 0);   // the intro always opens at the top of the page
  if (loader && root.classList.contains("lx-intro")) runLoader();
  function runLoader() {
    var eng = new LumantaParticles(loader.querySelector("canvas"), { count: mobile ? 36000 : 72000, dprMax: mobile ? 1.5 : 2 });
    var tweens = [], hole = { r: -4 }, exiting = false, finished = false;
    document.body.style.overflow = "hidden";
    var pctEl = loader.querySelector(".lx-pct"), barEl = loader.querySelector(".lx-progress i");
    var t0 = performance.now(), shown = 0, dataOk = 0;
    loader.classList.add("lx-show");

    function tick(now) {
      if (finished) return;
      var target = Math.min(1, dataOk * 0.7 + 0.3) * Math.min(1, (now - t0) / 2600);
      shown += (target - shown) * 0.08;
      barEl.style.transform = "scaleX(" + shown.toFixed(4) + ")";
      pctEl.textContent = String(Math.round(shown * 100)).padStart(2, "0");
      tweens = tweens.filter(function (f) { return !f(now); });
      loader.style.setProperty("--hole", hole.r.toFixed(2) + "vmax");
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    var ready = loadParticleData(DATA).then(function (d) {
      dataOk = 1;
      if (!eng.ok) return;
      eng.setData(d); eng.resize();
      var zFit = eng.fitZ(mobile ? 0.62 : 0.46);
      eng.cam.y = 0.6; eng.u.alpha = 0.62; eng.u.size = 0.92;
      eng.cam.z = zFit + 6; eng.cam.ry = -1.1;
      tweens.push(tween(eng.u, "burst", 1, 0.9, 0, ease.out3), tween(eng.u, "form", 1, 1.9, 0.35, ease.inOut2),
                  tween(eng.cam, "z", zFit, 2.4, 0, ease.out3), tween(eng.cam, "ry", 0, 2.6, 0, ease.out3));
      eng.start(function (e) { e.cam.rx = Math.sin(e.u.time * 0.6) * 0.06; });
      return new Promise(function (r) { setTimeout(r, 2500); });   // let the logomark finish forming
    }).catch(function () { dataOk = 1; });

    var minWait = new Promise(function (r) { setTimeout(r, 2900); });
    var maxWait = new Promise(function (r) { setTimeout(r, 8000); });
    Promise.race([Promise.all([ready, minWait]), maxWait]).then(function () { setTimeout(exit, 250); });
    loader.addEventListener("click", exit);
    addEventListener("keydown", function (e) { if (e.key === "Escape") exit(); });

    function exit() {
      if (exiting) return; exiting = true;
      loader.classList.add("lx-leaving");
      if (eng.ok && eng.n) {
        tweens.push(tween(eng.u, "explode", 1, 1.2, 0.05, ease.in2), tween(eng.cam, "z", 1.2, 1.2, 0.05, ease.in3),
                    tween(eng.u, "alpha", 0, 0.45, 0.8, ease.in2));
      }
      tweens.push(tween(hole, "r", 160, 1, 0.35, ease.in2));
      setTimeout(done, 1450);
    }
    function done() {
      finished = true; eng.destroy && eng.destroy();
      loader.remove(); root.classList.remove("lx-intro");
      document.body.style.overflow = "";
    }
  }

  /* ---------- 2. particle simulator ---------- */
  var stage = document.querySelector(".lx-sim");
  if (stage) {
    var canvas = stage.querySelector("canvas"), sim = null, visible = false, loaded = false, pulse = 0, releaseT = 0;
    var hint = stage.querySelector(".lx-hint");
    if (hint) hint.textContent = finePointer ? "Move your cursor through the light" : "Touch the light";
    function build() {
      if (sim) return;
      sim = new LumantaParticles(canvas, { count: mobile ? 24000 : 72000, dprMax: mobile ? 1.25 : 2 });
      if (!sim.ok) { stage.classList.add("lx-nogl"); return; }
      Object.assign(sim.u, { burst: 1, form: 1, useStatic: 0, staticAmt: 0, additive: 1, light: 0, mouseOn: 1, alpha: 0.55, size: mobile ? 1.0 : 0.85 });
      loadParticleData(DATA).then(function (d) {
        sim.setData(d); sim.resize();
        sim.cam.z = sim.fitZ(mobile ? 0.66 : 0.52); sim.cam.y = 0.25; loaded = true;
        if (visible) go();
      });
    }
    function go() {
      if (!loaded) return;
      sim.start(function (e) {
        pulse *= 0.94; e.u.mouseOn = 1 + pulse;
        e.cam.ry = Math.sin(e.u.time * 0.25) * 0.18; e.cam.rx = Math.sin(e.u.time * 0.4) * 0.06;
      });
    }
    if (finePointer) {
      stage.addEventListener("pointermove", function (e) { if (sim) sim.setMouse(e.clientX, e.clientY); });
      stage.addEventListener("pointerleave", function () { if (sim) sim.mouse.has = false; });
      stage.addEventListener("pointerdown", function () { pulse = 0.9; });
    }
    var touchAt = function (e) { var t = e.touches && e.touches[0]; if (!t || !sim) return; clearTimeout(releaseT); sim.setMouse(t.clientX, t.clientY); };
    stage.addEventListener("touchstart", function (e) { touchAt(e); pulse = 0.9; }, { passive: true });
    stage.addEventListener("touchmove", touchAt, { passive: true });
    var release = function () { releaseT = setTimeout(function () { if (sim) sim.mouse.has = false; }, 350); };
    stage.addEventListener("touchend", release, { passive: true });
    stage.addEventListener("touchcancel", release, { passive: true });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          visible = en.isIntersecting;
          if (visible) { build(); go(); } else if (sim && sim.ok) sim.stop();
        });
      }, { rootMargin: "300px" }).observe(stage);
    } else { visible = true; build(); }
  }
})();
