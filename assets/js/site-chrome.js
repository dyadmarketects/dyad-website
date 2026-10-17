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
  /* Contrast-aware color: read the background under the pointer. Grays (white to black) keep DYAD pink;
     on colored backgrounds pink is kept only if it stands out, otherwise the most contrasting brand color is used. */
  var PINK=[245,17,83], CHOICES=[[10,10,10],[255,255,255],[182,253,41]], lastBg='', pending=false;
  function rgb(str){ var m=str.match(/[\d.]+/g); return m ? m.map(Number) : null; }
  function bgAt(x,y){
    var el=document.elementFromPoint(x,y);
    while(el && el.nodeType===1){
      var c=rgb(getComputedStyle(el).backgroundColor);
      if(c && (c.length<4 || c[3]>0.5)) return c.slice(0,3);
      el=el.parentElement;
    }
    return [255,255,255];
  }
  function lum(c){ return c.map(function(v){ v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }).reduce(function(a,v,i){ return a+v*[0.2126,0.7152,0.0722][i]; },0); }
  function contrast(a,b){ var l1=lum(a), l2=lum(b); return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05); }
  function hue(c){ var r=c[0]/255,g=c[1]/255,b=c[2]/255, mx=Math.max(r,g,b), mn=Math.min(r,g,b), d=mx-mn; if(!d) return 0;
    var h = mx===r ? ((g-b)/d)%6 : mx===g ? (b-r)/d+2 : (r-g)/d+4; return (h*60+360)%360; }
  function sat(c){ var mx=Math.max.apply(null,c), mn=Math.min.apply(null,c); return mx ? (mx-mn)/mx : 0; }
  function pick(bg){
    if(sat(bg) < 0.18) return PINK;                                   // white, black and grays
    var hd=Math.abs(hue(bg)-hue(PINK)); hd=Math.min(hd,360-hd);
    if(hd >= 50 && contrast(PINK,bg) >= 2.2) return PINK;
    var LIME=CHOICES[2], hl=Math.abs(hue(bg)-hue(LIME)); hl=Math.min(hl,360-hl);
    if(hl >= 60 && contrast(LIME,bg) >= 2.5) return LIME;                 // DYAD lime on pinks and magentas
    return CHOICES.reduce(function(best,c){ return contrast(c,bg) > contrast(best,bg) ? c : best; });
  }
  function recolor(){
    pending=false;
    var bg=bgAt(mouse.x, mouse.y), key=bg.join(',');
    if(key===lastBg) return; lastBg=key;
    var c=pick(bg); root.style.setProperty('--cur','rgb('+c.join(',')+')');
  }
  function queueRecolor(){ if(!pending){ pending=true; requestAnimationFrame(recolor); } }
  document.addEventListener('mousemove', queueRecolor, {passive:true});
  window.addEventListener('scroll', queueRecolor, {passive:true});

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

/* Contact form (same behavior as the homepage) */
(function(){
  var form = document.getElementById('ctaForm');
  if(!form) return;
  var successBox = document.getElementById('ctaFormSuccess');
  var errBox = document.getElementById('ctaFormError');
  var another = document.getElementById('ctaAnother');
  var fallback = document.getElementById('ctaFormEmailFallback');
  var openedAt = Date.now();
  var human = form.querySelector('.cta-human-cb'), humanTrusted = false;
  if(human) human.addEventListener('change', function(e){ humanTrusted = !!(e.isTrusted && human.checked && Date.now() - openedAt > 1200); if(human.checked) clearError(); });
  function showError(msg){ if(errBox){ errBox.textContent = msg; errBox.hidden = false; } }
  function clearError(){ if(errBox){ errBox.textContent = ''; errBox.hidden = true; } }
  form.addEventListener('submit', function(e){
    e.preventDefault();
    clearError();
    var btn = form.querySelector('button[type="submit"]');
    // bot traps: hidden honeypot box, and forms filled faster than a human could
    var honey = form.querySelector('input[name="botcheck"]');
    if((honey && honey.checked) || Date.now() - openedAt < 3000){ showError('Please take a moment and try again.'); return; }
    // one-click human check: the box has to be ticked by a real click or key press, not by a script
    if(!human || !human.checked || !humanTrusted){ showError('Please check the box to confirm you are a real person.'); return; }
    var originalText = btn.textContent;
    btn.textContent = 'Sending...';
    btn.disabled = true;
    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    }).then(function(res){ return res.json(); }).then(function(json){
      btn.textContent = originalText; btn.disabled = false;
      if(json && json.success){
        form.style.display = 'none';
        if(fallback) fallback.style.display = 'none';
        if(successBox){ successBox.hidden = false; successBox.scrollIntoView({behavior:'smooth', block:'center'}); }
      } else {
        showError('Something went wrong sending your message. Please try again or email dyadmarketects@gmail.com.');
        if(human){ human.checked = false; humanTrusted = false; }
      }
    }).catch(function(){
      btn.textContent = originalText; btn.disabled = false;
      showError('Something went wrong sending your message. Please try again or email dyadmarketects@gmail.com.');
    });
  });
  if(another) another.addEventListener('click', function(){
    form.reset(); clearError(); openedAt = Date.now(); humanTrusted = false;
    if(successBox) successBox.hidden = true;
    form.style.display = '';
    if(fallback) fallback.style.display = '';
    var first = form.querySelector('input[name="Name"]'); if(first) first.focus();
  });
})();
