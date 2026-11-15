// DYAD Selected Work: an immersive 3D ring of project panels orbiting the DYAD logo.
// Progressive enhancement: reads the existing .port-card markup; if WebGL is missing the old carousel stays.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Color, FogExp2, Vector2, Vector3, Raycaster,
  CylinderGeometry, CircleGeometry, ExtrudeGeometry, Shape, Path, MeshBasicMaterial, MeshPhysicalMaterial,
  CanvasTexture, TextureLoader, PMREMGenerator, PointLight, AmbientLight, RepeatWrapping, SRGBColorSpace,
  FrontSide, BackSide, DoubleSide, MathUtils, AdditiveBlending,
} from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { LOGO } from './logo-paths.js';

const PINK = 0xf51153, LIME = 0xb6fd29, LAV = 0xb697fc, MAG = 0xbd6ec9, INK = 0x0a0a0a;
const R = 5;                       // ring radius
const BOX_W = 2.5, BOX_H = 2.0;    // each panel fits inside this box, keeping its image's proportions

function logoGeometry() {
  // Extrude the official logo outline. One uniform scale for x and y, so the logo is never stretched.
  const s = 1 / LOGO.w, cx = LOGO.w / 2, cy = LOGO.h / 2;
  const P = (p) => [(p[0] - cx) * s, -(p[1] - cy) * s];
  const shapes = [];
  LOGO.contours.filter((c) => !c.hole).forEach((c) => {
    const sh = new Shape(); c.pts.forEach((p, i) => { const [x, y] = P(p); i ? sh.lineTo(x, y) : sh.moveTo(x, y); }); sh.closePath();
    LOGO.contours.filter((h) => h.hole && h.bbox[0] > c.bbox[0] && h.bbox[2] < c.bbox[2]).forEach((h) => {
      const hp = new Path(); h.pts.forEach((p, i) => { const [x, y] = P(p); i ? hp.lineTo(x, y) : hp.moveTo(x, y); }); hp.closePath(); sh.holes.push(hp);
    });
    shapes.push(sh);
  });
  const depth = 0.1;   // same depth-to-width ratio as Vince's 3D logo file
  const g = new ExtrudeGeometry(shapes, { depth, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.004, bevelOffset: -0.004, bevelSegments: 3, curveSegments: 4 });
  g.translate(0, 0, -depth / 2);
  return g;
}

function gridTexture(cells, lit) {
  const c = document.createElement('canvas'); c.width = c.height = 1024; const x = c.getContext('2d');
  x.fillStyle = '#0a0a0a'; x.fillRect(0, 0, 1024, 1024);
  const n = cells, s = 1024 / n, cols = ['245,17,83', '182,151,252', '182,253,41', '189,110,201'];
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    const r = rnd();
    if (r < lit) { x.fillStyle = `rgba(${cols[(i * 3 + j) % 4]},${0.05 + rnd() * 0.16})`; x.fillRect(i * s, j * s, s, s); }
    else if (r < lit * 3) { x.fillStyle = `rgba(255,255,255,${0.012 + rnd() * 0.03})`; x.fillRect(i * s, j * s, s, s); }
  }
  x.strokeStyle = 'rgba(182,151,252,.34)'; x.lineWidth = 2;
  for (let i = 0; i <= n; i++) { x.beginPath(); x.moveTo(i * s, 0); x.lineTo(i * s, 1024); x.moveTo(0, i * s); x.lineTo(1024, i * s); x.stroke(); }
  x.fillStyle = 'rgba(255,255,255,.5)';
  for (let i = 0; i <= n; i++) for (let j = 0; j <= n; j++) { x.fillRect(i * s - 7, j * s - 1, 14, 2); x.fillRect(i * s - 1, j * s - 7, 2, 14); }
  const t = new CanvasTexture(c); t.wrapS = t.wrapT = RepeatWrapping; t.colorSpace = SRGBColorSpace; t.anisotropy = 4; return t;
}

function radialAlpha() {
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d');
  const g = x.createRadialGradient(128, 128, 10, 128, 128, 128); g.addColorStop(0, '#fff'); g.addColorStop(0.55, '#777'); g.addColorStop(1, '#000');
  x.fillStyle = g; x.fillRect(0, 0, 256, 256); return new CanvasTexture(c);
}

export function initWork3D(section) {
  const cards = [...section.querySelectorAll('.port-card')];
  if (!cards.length) return null;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let renderer;   // powerPreference 'default' avoids a GPU switch that can stutter the hero video on dual-GPU laptops
  try { renderer = new WebGLRenderer({ antialias: (devicePixelRatio || 1) < 1.5, alpha: false, powerPreference: 'default' }); } catch (e) { return null; }
  if (!renderer.getContext()) return null;

  // ---------- data from the existing markup ----------
  const items = cards.map((c) => {
    const a = c.querySelector('.port-immerse');
    return {
      img: c.dataset.bg || (c.style.backgroundImage.match(/url\(["']?(.*?)["']?\)/) || [])[1] || '', alt: c.getAttribute('aria-label') || '',
      tags: [...c.querySelectorAll('.port-tags span')].map((s) => s.textContent),
      client: (c.querySelector('.port-client') || {}).textContent || '',
      title: (c.querySelector('h5') || {}).innerHTML || '', desc: (c.querySelector('.port-expand p') || {}).innerHTML || '',
      stat: (c.querySelector('.port-stat') || {}).innerHTML || '', href: a ? a.getAttribute('href') : '', blank: a ? a.target === '_blank' : false,
      isNew: !!c.querySelector('.port-new'),
    };
  });
  const N = items.length, STEP = (Math.PI * 2) / N;

  // ---------- DOM ----------
  section.classList.add('w3d-on');
  const stage = document.createElement('div'); stage.className = 'w3d';
  stage.innerHTML = `
    <div class="w3d-canvas" aria-hidden="true"></div>
    <div class="w3d-vig" aria-hidden="true"></div>
    <div class="w3d-hud" aria-hidden="true"><span>DYAD / SELECTED WORK</span><span class="w3d-coord"></span></div>
    <div class="w3d-cap" aria-live="polite">
      <div class="w3d-count"><b class="w3d-i">01</b><i></i><span>${String(N).padStart(2, '0')}</span></div>
      <div class="w3d-tags"></div>
      <div class="w3d-client"></div>
      <h3 class="w3d-title"></h3>
      <p class="w3d-desc"></p>
      <div class="w3d-stat"></div>
      <div class="w3d-row">
        <a class="w3d-go" href="#">Immerse <span aria-hidden="true">&#8599;</span></a>
        <button type="button" class="w3d-btn" data-d="-1" aria-label="Previous project"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
        <button type="button" class="w3d-btn" data-d="1" aria-label="Next project"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
      </div>
    </div>
    <div class="w3d-dots" role="tablist" aria-label="Projects"></div>
    <div class="w3d-hint" aria-hidden="true">Drag to explore</div>`;
  const shell = section.querySelector('.sc-shell');
  shell.parentNode.insertBefore(stage, shell);
  const q = (s) => stage.querySelector(s);
  const holder = q('.w3d-canvas'), cap = q('.w3d-cap'), dots = q('.w3d-dots');
  items.forEach((it, i) => { const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('aria-label', it.client); b.onclick = () => goTo(i, true); dots.appendChild(b); });
  holder.appendChild(renderer.domElement);

  // ---------- scene ----------
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
  renderer.outputColorSpace = SRGBColorSpace;
  const scene = new Scene(); scene.background = new Color(INK); scene.fog = new FogExp2(INK, 0.034);
  const pm = new PMREMGenerator(renderer); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; pm.dispose();
  const camera = new PerspectiveCamera(30, 1, 0.1, 80);

  // room: gridded cylinder wall, floor and ceiling
  const room = new Group(); scene.add(room);
  const wallTex = gridTexture(8, 0.07); wallTex.repeat.set(14, 2);
  const wall = new Mesh(new CylinderGeometry(17, 17, 15, 64, 1, true), new MeshBasicMaterial({ map: wallTex, side: BackSide, fog: true })); wall.position.y = 2.2; room.add(wall);
  const flTex = gridTexture(8, 0.05); flTex.repeat.set(6, 6);
  const alpha = radialAlpha();
  const floor = new Mesh(new CircleGeometry(17, 64), new MeshBasicMaterial({ map: flTex, alphaMap: alpha, transparent: true, opacity: 0.9 })); floor.rotation.x = -Math.PI / 2; floor.position.y = -1.75; room.add(floor);
  const ceil = new Mesh(new CircleGeometry(17, 64), new MeshBasicMaterial({ map: flTex, alphaMap: alpha, transparent: true, opacity: 0.5 })); ceil.rotation.x = Math.PI / 2; ceil.position.y = 6.2; room.add(ceil);
  // soft pink pool of light on the floor under the logo
  const glowC = document.createElement('canvas'); glowC.width = glowC.height = 256; { const x = glowC.getContext('2d'); const g = x.createRadialGradient(128, 128, 0, 128, 128, 128); g.addColorStop(0, 'rgba(245,17,83,.55)'); g.addColorStop(0.5, 'rgba(189,110,201,.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, 256, 256); }
  const glow = new Mesh(new CircleGeometry(7.5, 48), new MeshBasicMaterial({ map: new CanvasTexture(glowC), transparent: true, blending: AdditiveBlending, depthWrite: false })); glow.rotation.x = -Math.PI / 2; glow.position.y = -1.74; room.add(glow);

  // logo
  const logoMat = new MeshPhysicalMaterial({ color: PINK, emissive: PINK, emissiveIntensity: 0.32, metalness: 0.55, roughness: 0.24, clearcoat: 1, clearcoatRoughness: 0.12, envMapIntensity: 1.5 });
  const logo = new Mesh(logoGeometry(), logoMat);
  const logoPivot = new Group(); logoPivot.add(logo); scene.add(logoPivot);
  scene.add(new AmbientLight(0xffffff, 0.35));
  const l1 = new PointLight(LIME, 60, 30), l2 = new PointLight(LAV, 70, 30), l3 = new PointLight(0xffffff, 40, 30);
  scene.add(l1, l2, l3);

  // panels
  const ring = new Group(); scene.add(ring);
  const loader = new TextureLoader(), panels = [], hitMeshes = [];
  const backMat = new MeshBasicMaterial({ color: 0x141214, side: BackSide });
  items.forEach((it, i) => {
    const pivot = new Group(); pivot.rotation.y = i * STEP; ring.add(pivot);
    const mat = new MeshBasicMaterial({ color: 0x222222, side: FrontSide });
    const mesh = new Mesh(new CylinderGeometry(R, R, BOX_H, 24, 1, true, -BOX_W / R / 2, BOX_W / R), mat); mesh.userData.i = i;
    const back = new Mesh(mesh.geometry, backMat);
    const edge = new Mesh(new CylinderGeometry(R - 0.015, R - 0.015, BOX_H + 0.07, 24, 1, true, -(BOX_W + 0.07) / R / 2, (BOX_W + 0.07) / R), new MeshBasicMaterial({ color: PINK, side: DoubleSide, transparent: true, opacity: 0 })); 
    pivot.add(edge, back, mesh); panels.push({ pivot, mesh, back, edge, mat, lum: 0.3 }); hitMeshes.push(mesh);
    loader.load(it.img, (t) => {
      t.colorSpace = SRGBColorSpace; t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      const ar = t.image.width / t.image.height; let w = BOX_W, h = BOX_W / ar; if (h > BOX_H) { h = BOX_H; w = BOX_H * ar; }
      const g = new CylinderGeometry(R, R, h, 24, 1, true, -w / R / 2, w / R);
      mesh.geometry.dispose(); edge.geometry.dispose(); mesh.geometry = g; back.geometry = g; edge.geometry = new CylinderGeometry(R - 0.015, R - 0.015, h + 0.07, 24, 1, true, -(w + 0.07) / R / 2, (w + 0.07) / R);
      mat.map = t; mat.color.set(0xffffff); mat.needsUpdate = true; dirty = true;
    });
  });

  // ---------- state ----------
  let pos = reduce ? 0 : -1.6, target = 0, vel = 0, active = -1, dirty = true, inView = false, hover = false, dragging = false, lastInteract = 0, intro = reduce ? 1 : 0;
  let W = 1, H = 1, portrait = false, logoW = 6.4, logoY = 2.05, camZ = 16, lookY = 0.75, shiftX = 0;
  const mouse = new Vector2(), mouseS = new Vector2(), ray = new Raycaster(), ndc = new Vector2();
  const mod = (a, n) => ((a % n) + n) % n;

  function layout() {
    W = holder.clientWidth; H = holder.clientHeight; if (!W || !H) return;
    portrait = W / H < 0.9;
    renderer.setSize(W, H, false); camera.aspect = W / H;
    logoW = portrait ? 3.5 : Math.min(5.4, 2.9 + (W / H) * 1.5);
    const logoH = logoW * (LOGO.h / LOGO.w);
    logoY = BOX_H / 2 + (portrait ? 0.42 : 0.2) + logoH / 2;
    const wide = !portrait && W > 820;
    shiftX = wide ? 1.35 : 0;
    const top = logoY + logoH / 2 + (portrait ? 0.3 : 0.42), bottom = portrait ? -1.45 : -2.0;
    lookY = (top + bottom) / 2;
    const needH = top - bottom, needW = Math.max(logoW * 1.1, BOX_W * 1.5) + shiftX * 2;
    const t = Math.tan(MathUtils.degToRad(camera.fov / 2));
    camZ = R + Math.max(needH / (2 * t), needW / (2 * t * camera.aspect));
    if (portrait) { const visH = 2 * t * (camZ - R); lookY = top + visH * 0.15 - visH / 2; }   // phones: scene sits in the upper part, details overlay the floor
    camera.updateProjectionMatrix(); dirty = true;
  }

  function setCaption(i) {
    if (i === active) return; active = i; const it = items[i];
    cap.classList.remove('in'); void cap.offsetWidth; cap.classList.add('in');
    q('.w3d-i').textContent = String(i + 1).padStart(2, '0');
    q('.w3d-tags').innerHTML = (it.isNew ? '<span class="new">New</span>' : '') + it.tags.map((t) => `<span>${t}</span>`).join('');
    q('.w3d-client').textContent = it.client; q('.w3d-title').innerHTML = it.title; q('.w3d-desc').innerHTML = it.desc; q('.w3d-stat').innerHTML = it.stat;
    const go = q('.w3d-go'); go.href = it.href; if (it.blank) { go.target = '_blank'; go.rel = 'noopener'; } else { go.removeAttribute('target'); go.removeAttribute('rel'); }
    go.setAttribute('aria-label', 'Immerse: ' + it.client);
    [...dots.children].forEach((d, k) => { d.classList.toggle('on', k === i); d.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
  }
  function goTo(i, user) { const cur = Math.round(target); let d = mod(i - cur, N); if (d > N / 2) d -= N; target = cur + d; if (user) lastInteract = performance.now(); }
  function step(d, user) { target = Math.round(target) + d; if (user) lastInteract = performance.now(); }

  stage.querySelectorAll('.w3d-btn').forEach((b) => b.addEventListener('click', () => step(+b.dataset.d, true)));
  stage.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') { step(1, true); e.preventDefault(); } if (e.key === 'ArrowLeft') { step(-1, true); e.preventDefault(); } });

  // drag, click and hover
  const el = renderer.domElement; let sx = 0, sp = 0, moved = 0, lx = 0, lt = 0;
  const pick = (e) => { const r = el.getBoundingClientRect(); ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(ndc, camera); const h = ray.intersectObjects(hitMeshes, false)[0]; return h ? h.object.userData.i : -1; };
  el.addEventListener('pointerdown', (e) => { if (e.button) return; dragging = true; moved = 0; sx = lx = e.clientX; sp = pos; lt = performance.now(); vel = 0; try { el.setPointerCapture(e.pointerId); } catch (_) {} stage.classList.add('drag'); });
  el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect(); mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, ((e.clientY - r.top) / r.height) * 2 - 1);
    if (dragging) { const dx = e.clientX - sx; moved = Math.max(moved, Math.abs(dx)); const per = Math.max(240, W * 0.24); pos = sp - dx / per; target = pos; const now = performance.now(); if (now > lt) vel = (-(e.clientX - lx) / per) / ((now - lt) / 1000); lx = e.clientX; lt = now; lastInteract = now; }
    else if (e.pointerType === 'mouse') { const i = pick(e); el.style.cursor = i >= 0 ? 'pointer' : 'grab'; }
  });
  const up = (e) => {
    if (!dragging) return; dragging = false; stage.classList.remove('drag');
    if (moved < 6) { const i = pick(e); if (i >= 0) { if (i === mod(Math.round(pos), N)) q('.w3d-go').click(); else goTo(i, true); } target = Math.round(target); }
    else target = Math.round(pos + MathUtils.clamp(vel * 0.22, -2.4, 2.4));
    stage.classList.add('used');
  };
  el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  stage.addEventListener('pointerenter', () => { hover = true; }); stage.addEventListener('pointerleave', () => { hover = false; mouse.set(0, 0); });
  stage.addEventListener('focusin', () => { hover = true; }); stage.addEventListener('focusout', () => { hover = false; });

  // ---------- loop ----------
  let raf = 0, last = 0, clock = 0;
  function frame(now) {
    raf = 0; if (!inView) return;
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now; clock += dt;
    if (!reduce && !dragging && !hover && !window.__w3dNoAuto && now - lastInteract > 6500 && intro >= 1 && document.visibilityState === 'visible') { step(1); lastInteract = now; }
    if (!dragging) { const k = 1 - Math.exp(-dt * 5.2); pos += (target - pos) * k; if (Math.abs(target - pos) < 0.0004) pos = target; }
    if (intro < 1) intro = Math.min(1, intro + dt / 1.6);
    const ease = 1 - Math.pow(1 - intro, 3);
    setCaption(mod(Math.round(pos), N));
    ring.rotation.y = -pos * STEP;
    panels.forEach((p, i) => {
      let d = mod(i - pos, N); if (d > N / 2) d -= N; const a = Math.abs(d);
      const lum = a < 0.5 ? 1 : MathUtils.clamp(0.62 - a * 0.09, 0.2, 0.62); p.lum += (lum - p.lum) * Math.min(1, dt * 8);
      if (p.mat.map) p.mat.color.setScalar(p.lum);
      p.edge.material.opacity += ((a < 0.5 ? 0.95 : 0) - p.edge.material.opacity) * Math.min(1, dt * 8);
      const pop = Math.max(0, 1 - a) * 0.35; p.mesh.position.set(0, 0, 0); p.pivot.scale.setScalar((1 + pop * 0.12) * (0.6 + 0.4 * ease));
      p.pivot.position.y = Math.sin(clock * 0.7 + i * 1.7) * 0.035 + (1 - ease) * -1.2;
    });
    // logo: one full turn per project so it always settles facing forward, with a slow sway at rest
    logoPivot.position.set(0, logoY + Math.sin(clock * 0.8) * 0.06, 0);
    logoPivot.scale.setScalar(logoW * (0.2 + 0.8 * ease));
    logoPivot.rotation.y = -pos * Math.PI * 2 + (reduce ? 0 : Math.sin(clock * 0.45) * 0.3) + (1 - ease) * 2.4;
    logoPivot.rotation.x = reduce ? 0 : Math.sin(clock * 0.33) * 0.05;
    l1.position.set(Math.cos(clock * 0.5) * 6, logoY + 1.5, Math.sin(clock * 0.5) * 6 + 2);
    l2.position.set(Math.cos(clock * 0.37 + 2.4) * 7, logoY - 1, Math.sin(clock * 0.37 + 2.4) * 7 + 2);
    l3.position.set(0, logoY + 2.5, 7);
    room.rotation.y = -pos * STEP * 0.35 + clock * 0.012;
    mouseS.lerp(mouse, Math.min(1, dt * 3));
    camera.position.set(mouseS.x * 0.55 - shiftX, lookY + 0.55 - mouseS.y * 0.3, camZ);
    camera.lookAt(mouseS.x * 0.12 - shiftX, lookY, 0);
    renderer.render(scene, camera);
    const c = q('.w3d-coord'); if (c) c.textContent = 'ROT ' + String(Math.round(mod(pos * (360 / N), 360))).padStart(3, '0') + '°';
    if (!reduce || dirty || Math.abs(target - pos) > 0.0004 || dragging) { dirty = false; raf = requestAnimationFrame(frame); }
  }
  const kick = () => { if (!raf && inView) { last = 0; raf = requestAnimationFrame(frame); } };
  new IntersectionObserver((es) => { inView = es[0].isIntersecting; if (inView) { lastInteract = performance.now(); kick(); } }, { rootMargin: '120px' }).observe(stage);
  new ResizeObserver(() => { layout(); kick(); }).observe(holder);
  if (reduce) ['pointerdown', 'pointermove', 'click', 'keydown'].forEach((t) => stage.addEventListener(t, () => setTimeout(kick, 0)));
  layout(); setCaption(0);
  return { goTo, step };
}
