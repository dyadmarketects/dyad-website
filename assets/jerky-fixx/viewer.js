/* Jerky Fixx case study: drag to spin the carne seca. Loads three.js only when the stage is near the screen. */
const stage = document.querySelector(".jx-view");
if (stage) {
  const boot = async () => {
    const THREE = await import("three");
    const { OrbitControls } = await import("three/addons/controls/OrbitControls.js");
    const { GLTFLoader } = await import("three/addons/loaders/GLTFLoader.js");
    const { MeshoptDecoder } = await import("three/addons/libs/meshopt_decoder.module.js");
    const canvas = stage.querySelector("canvas");
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(32, 1, 0.01, 100);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x5a0060, 1.6));
    const key = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(3, 4, 5); scene.add(key);
    const rim = new THREE.DirectionalLight(0xc9fb05, 1.2); rim.position.set(-4, 1, -3); scene.add(rim);
    const controls = new OrbitControls(cam, canvas);
    Object.assign(controls, { enableDamping: true, dampingFactor: 0.08, enablePan: false, enableZoom: false, autoRotate: true, autoRotateSpeed: 2.2, rotateSpeed: 0.9 });
    const hint = stage.querySelector(".lx-hint");
    controls.addEventListener("start", () => { controls.autoRotate = false; stage.classList.add("jx-held"); if (hint) hint.style.opacity = "0"; });
    controls.addEventListener("end", () => { stage.classList.remove("jx-held"); setTimeout(() => (controls.autoRotate = true), 4000); });
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    const gltf = await loader.loadAsync("/assets/jerky-fixx/jerky.glb");
    const m = gltf.scene, box = new THREE.Box3().setFromObject(m), c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
    m.position.sub(c); const g = new THREE.Group(); g.add(m); g.rotation.z = -0.25; scene.add(g);
    const r = Math.max(s.x, s.y, s.z);
    const fit = () => {
      const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false);
      cam.aspect = w / h; const d = (r * 0.8) / Math.tan((cam.fov * Math.PI) / 360) / Math.min(1, cam.aspect);
      cam.position.set(0, r * 0.1, d); cam.updateProjectionMatrix(); controls.update();
    };
    fit(); addEventListener("resize", fit);
    stage.classList.add("jx-ready");
    let on = true; new IntersectionObserver(e => (on = e[0].isIntersecting)).observe(stage);
    renderer.setAnimationLoop(t => { if (!on) return; g.position.y = r * 0.1 + Math.sin(t / 900) * r * 0.03; controls.update(); renderer.render(scene, cam); });
  };
  const io = new IntersectionObserver(es => { if (es[0].isIntersecting) { io.disconnect(); boot().catch(e => { console.warn(e); stage.classList.add("jx-fail"); }); } }, { rootMargin: "400px" });
  io.observe(stage);
}
