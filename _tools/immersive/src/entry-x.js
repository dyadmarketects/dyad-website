import { initXScroll } from './xscroll.js';
function boot(){ const x = document.querySelector('.divider-section'); if (x && !x.classList.contains('xs-on')) { try { initXScroll(x); } catch (e) { console.warn('xscroll', e); } } }
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
