import { initWork3D } from './work3d.js';
const p = document.getElementById('projects');
if (p && !p.classList.contains('w3d-on')) { try { if (!initWork3D(p)) p.classList.remove('w3d-on'); } catch (e) { p.classList.remove('w3d-on'); const s = p.querySelector('.w3d'); if (s) s.remove(); console.warn('work3d', e); } }
