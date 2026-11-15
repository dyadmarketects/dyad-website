// DYAD logomark scroll animation: blueprint guides draw, the pink X outline traces itself, fills,
// then the two D's slide in to complete the DYAD logo. Driven by scroll position inside a pinned section.
import { LOGO } from './logo-paths.js';

const NS = 'http://www.w3.org/2000/svg';
const el = (n, a) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); return e; };
const clamp = (v) => Math.max(0, Math.min(1, v));
const seg = (p, a, b) => clamp((p - a) / (b - a));
const eio = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const eo = (t) => 1 - Math.pow(1 - t, 3);

export function initXScroll(section) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const W = LOGO.w, H = LOGO.h, cx = W / 2, cy = H / 2;
  const d = (c) => 'M' + c.pts.map((p) => p[0] + ' ' + p[1]).join('L') + 'Z';
  const outers = LOGO.contours.filter((c) => !c.hole).sort((a, b) => a.bbox[0] - b.bbox[0]);
  const holes = LOGO.contours.filter((c) => c.hole).sort((a, b) => a.bbox[0] - b.bbox[0]);
  const [DL, X, DR] = outers;
  const VB = { x: -260, y: -520, w: W + 520, h: H + 1040 };

  section.classList.add('xs-on');
  section.innerHTML = `<div class="xs-pin"><div class="xs-grid" aria-hidden="true"></div>
    <div class="xs-hud" aria-hidden="true"><span>DYAD / LOGOMARK</span><span class="xs-pct">000</span></div>
    <div class="xs-words" aria-hidden="true"><span>Duality</span><span>Yields</span><span>Agile</span><span>Development</span></div></div>`;
  const pin = section.firstElementChild;
  const svg = el('svg', { viewBox: `${VB.x} ${VB.y} ${VB.w} ${VB.h}`, class: 'xs-svg', role: 'img', 'aria-label': 'DYAD Marketects logomark and logo', preserveAspectRatio: 'xMidYMid meet' });
  pin.insertBefore(svg, pin.children[1]);

  // ----- blueprint guides: lines along the X's long edges, circles and ticks -----
  const guides = el('g', { class: 'xs-guides' }); svg.appendChild(guides);
  const zoom = el('g', {}); svg.appendChild(zoom);          // everything in here scales together (uniformly)
  const gl = [];
  const addLine = (x1, y1, x2, y2) => { const l = el('line', { x1, y1, x2, y2, pathLength: 1 }); guides.appendChild(l); gl.push(l); };
  const pts = X.pts, long = [];
  for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length], len = Math.hypot(b[0] - a[0], b[1] - a[1]); if (len > 150) long.push([a, b, len]); }
  long.sort((a, b) => b[2] - a[2]);
  const SC0 = 1.9;   // the X starts large, then settles to its place in the full logo
  const T = (p) => [cx + (p[0] - cx) * SC0, cy + (p[1] - cy) * SC0];
  long.slice(0, 10).forEach(([a, b]) => {
    const A = T(a), B = T(b), dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, ext = 2600;
    addLine(A[0] - ux * ext, A[1] - uy * ext, B[0] + ux * ext, B[1] + uy * ext);
  });
  const xb = X.bbox, top = T([0, xb[1]])[1], bot = T([0, xb[3]])[1], lft = T([xb[0], 0])[0], rgt = T([xb[2], 0])[0];
  [top, cy, bot].forEach((y) => addLine(VB.x, y, VB.x + VB.w, y));
  [lft, cx, rgt].forEach((x) => addLine(x, VB.y, x, VB.y + VB.h));
  const circles = [150, 330, 560].map((r) => { const c = el('circle', { cx, cy, r, pathLength: 1 }); guides.appendChild(c); return c; });
  const ticks = el('g', { class: 'xs-ticks' }); guides.appendChild(ticks);
  [[lft, top], [rgt, top], [lft, bot], [rgt, bot], [cx, cy]].forEach(([x, y]) => { ticks.appendChild(el('path', { d: `M${x - 26} ${y}H${x + 26}M${x} ${y - 26}V${y + 26}` })); });
  [['X ' + Math.round(xb[2] - xb[0]), lft + 14, top - 16], ['Y ' + Math.round(xb[3] - xb[1]), rgt + 14, bot + 34], ['DYAD.01', lft + 14, bot + 34], ['45.0°', rgt - 150, top - 16]].forEach(([t, x, y]) => { const e = el('text', { x, y }); e.textContent = t; ticks.appendChild(e); });

  // ----- the logo -----
  const ghost = el('path', { d: d(X), class: 'xs-ghost' }); zoom.appendChild(ghost);
  const gDL = el('g', { class: 'xs-d' }), gDR = el('g', { class: 'xs-d' }); zoom.appendChild(gDL); zoom.appendChild(gDR);
  const mk = (g, outer, hole) => { const dd = d(outer) + (hole ? d(hole) : ''); const f = el('path', { d: dd, class: 'xs-fill', 'fill-rule': 'evenodd' }); const s = el('path', { d: dd, class: 'xs-stroke', pathLength: 1 }); g.appendChild(f); g.appendChild(s); return { f, s }; };
  const pDL = mk(gDL, DL, holes[0]), pDR = mk(gDR, DR, holes[1]);
  const gX = el('g', {}); zoom.appendChild(gX); const pX = mk(gX, X, null);
  const glowP = el('path', { d: d(X), class: 'xs-glow', pathLength: 1 }); gX.insertBefore(glowP, pX.s);

  const words = [...pin.querySelectorAll('.xs-words span')], pct = pin.querySelector('.xs-pct'), grid = pin.querySelector('.xs-grid');
  const dash = (e, t) => { e.style.strokeDasharray = '1 1'; e.style.strokeDashoffset = String(1 - t); };

  function draw(p) {
    // 1. guides draw in, then fade
    const gOut = 1 - seg(p, 0.5, 0.66);
    gl.forEach((l, i) => { dash(l, eio(seg(p, 0.0 + i * 0.012, 0.2 + i * 0.012))); });
    circles.forEach((c, i) => dash(c, eio(seg(p, 0.06 + i * 0.04, 0.3 + i * 0.04))));
    guides.style.opacity = String(gOut * 0.9); ticks.style.opacity = String(seg(p, 0.14, 0.24));
    // 2. X outline traces itself
    const tr = eio(seg(p, 0.16, 0.5)); dash(pX.s, tr); dash(glowP, tr);
    glowP.style.opacity = String(tr > 0 ? 0.55 * (1 - seg(p, 0.56, 0.7)) : 0);
    // 3. fill
    const fill = eo(seg(p, 0.52, 0.66)); pX.f.style.fillOpacity = String(fill);
    ghost.style.opacity = String(0.1 * seg(p, 0.02, 0.2) * (1 - seg(p, 0.55, 0.7)));
    // 4. settle to logo scale while the D's arrive from each side
    const z = eio(seg(p, 0.6, 0.86)), sc = SC0 + (1 - SC0) * z;
    zoom.setAttribute('transform', `translate(${cx} ${cy}) scale(${sc}) translate(${-cx} ${-cy})`);
    ghost.setAttribute('transform', `translate(${cx} ${cy}) scale(${1.9 - z * 0.6}) translate(${-cx} ${-cy})`);
    const dIn = eo(seg(p, 0.64, 0.88)), off = (1 - dIn) * 620;
    gDL.setAttribute('transform', `translate(${-off} 0)`); gDR.setAttribute('transform', `translate(${off} 0)`);
    gDL.style.opacity = gDR.style.opacity = String(seg(p, 0.64, 0.74));
    const dTr = eio(seg(p, 0.66, 0.86)); dash(pDL.s, dTr); dash(pDR.s, dTr);
    const dFill = eo(seg(p, 0.8, 0.92)); pDL.f.style.fillOpacity = pDR.f.style.fillOpacity = String(dFill);
    // 5. what DYAD stands for
    words.forEach((w, i) => { const t = eo(seg(p, 0.84 + i * 0.03, 0.92 + i * 0.03)); w.style.opacity = String(t); w.style.transform = `translateY(${(1 - t) * 18}px)`; });
    grid.style.opacity = String(0.25 + 0.75 * seg(p, 0.5, 0.9));
    pct.textContent = String(Math.round(p * 100)).padStart(3, '0');
  }

  if (reduce) { section.classList.add('xs-static'); draw(1); return; }
  let cur = -1, want = 0, raf = 0;
  const measure = () => { const r = section.getBoundingClientRect(), span = r.height - innerHeight; want = span > 0 ? clamp(-r.top / span) : (r.top < innerHeight * 0.4 ? 1 : 0); };
  const tick = () => { raf = 0; cur = cur < 0 ? want : cur + (want - cur) * 0.16; if (Math.abs(want - cur) < 0.0005) cur = want; draw(cur); if (cur !== want) raf = requestAnimationFrame(tick); };
  const on = () => { measure(); if (!raf) raf = requestAnimationFrame(tick); };
  addEventListener('scroll', on, { passive: true }); addEventListener('resize', on); on();
}
