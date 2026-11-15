import { initWork3D } from './work3d.js';
import { initXScroll } from './xscroll.js';
function boot(){
  const p = document.getElementById('projects'); if (p && !p.classList.contains('w3d-on')) { try { initWork3D(p); } catch (e) { p.classList.remove('w3d-on'); console.warn('work3d', e); } }
  const x = document.querySelector('.divider-section'); if (x && !x.classList.contains('xs-on')) { try { initXScroll(x); } catch (e) { console.warn('xscroll', e); } }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
