/* Shared site chrome behavior (President's Club slide-out). Generated from the homepage by _tools/site_chrome.py. */
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
