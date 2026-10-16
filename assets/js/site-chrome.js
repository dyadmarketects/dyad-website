/* Shared site chrome behavior (President's Club slide-out, custom cursor). Generated from the homepage by _tools/site_chrome.py. */
/* ===== President's Club slide-out: hover on desktop, tap/click anywhere ===== */
(function(){
  var pc = document.getElementById('presClub'); if(!pc) return;
  var tab = pc.querySelector('.side-tab'), close = pc.querySelector('.pc-close');
  var pinned = false, t = 0;
  var canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  function set(open){ pc.classList.toggle('open', open); tab.setAttribute('aria-expanded', open ? 'true' : 'false'); }
  if(canHover){
    pc.addEventListener('mouseenter', function(){ clearTimeout(t); set(true); });
    pc.addEventListener('mouseleave', function(){ if(pinned) return; t = setTimeout(function(){ set(false); }, 260); });
  }
  tab.addEventListener('click', function(){
    var open = !pc.classList.contains('open') || (canHover && !pinned);
    pinned = open; set(open);
  });
  close.addEventListener('click', function(){ pinned = false; set(false); });
  document.addEventListener('click', function(e){ if(pc.classList.contains('open') && !pc.contains(e.target)){ pinned = false; set(false); } });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && pc.classList.contains('open')){ pinned = false; set(false); } });
})();

(function(){
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  if(!fine.matches) return;                       // touch devices keep the normal cursor
  var root = document.documentElement;
  var dot = document.querySelector('.cursor-dot');
  var ring = document.querySelector('.cursor-ring');
  if(!dot || !ring) return;

  var HOVER_SEL = 'a, button, [role="button"], label, summary, .faq-q, [data-cursor="hover"]';
  var TEXT_SEL = 'input, textarea, select, [contenteditable="true"]';
  var mouse = {x: innerWidth/2, y: innerHeight/2};
  var ringPos = {x: mouse.x, y: mouse.y};
  var magnet = null, raf = null;
  var EASE = reduce.matches ? 1 : 0.16;           // lerp factor: lower = more lag
  var PULL = 0.35;                                 // how far the ring snaps toward a .magnetic center

  root.classList.add('has-custom-cursor');

  function onMove(e){
    mouse.x = e.clientX; mouse.y = e.clientY;
    dot.style.transform = 'translate3d(' + mouse.x + 'px,' + mouse.y + 'px,0)';
    root.classList.add('cursor-visible');
  }
  function onOver(e){
    var t = e.target;
    if(!(t instanceof Element)) return;
    root.classList.toggle('cursor-text', !!t.closest(TEXT_SEL));
    root.classList.toggle('cursor-hover', !!t.closest(HOVER_SEL) && !t.closest(TEXT_SEL));
    magnet = t.closest('.magnetic');
  }
  function onOut(e){
    if(!e.relatedTarget){ root.classList.remove('cursor-visible'); } // left the window
  }
  function onDown(){ root.classList.add('cursor-down'); }
  function onUp(){ root.classList.remove('cursor-down'); }

  function loop(){
    var tx = mouse.x, ty = mouse.y;
    if(magnet && magnet.isConnected){
      var r = magnet.getBoundingClientRect();
      tx += ((r.left + r.width/2) - tx) * PULL;
      ty += ((r.top + r.height/2) - ty) * PULL;
    }
    ringPos.x += (tx - ringPos.x) * EASE;
    ringPos.y += (ty - ringPos.y) * EASE;
    ring.style.transform = 'translate3d(' + ringPos.x + 'px,' + ringPos.y + 'px,0)';
    raf = requestAnimationFrame(loop);
  }

  document.addEventListener('mousemove', onMove, {passive:true});
  document.addEventListener('mouseover', onOver, {passive:true});
  document.addEventListener('mouseout', onOut, {passive:true});
  document.addEventListener('mousedown', onDown);
  document.addEventListener('mouseup', onUp);
  raf = requestAnimationFrame(loop);

  // Full cleanup, e.g. window.dyadCursor.destroy()
  function destroy(){
    cancelAnimationFrame(raf);
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseover', onOver);
    document.removeEventListener('mouseout', onOut);
    document.removeEventListener('mousedown', onDown);
    document.removeEventListener('mouseup', onUp);
    root.classList.remove('has-custom-cursor','cursor-visible','cursor-hover','cursor-down','cursor-text');
    dot.remove(); ring.remove();
  }
  window.dyadCursor = { destroy: destroy };
  window.addEventListener('pagehide', destroy, {once:true});
})();
