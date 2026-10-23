/* dc3-viewer.js — Visor 3D de la malla exterior del DC-3 (Three.js UMD).
   Expone window.DC3Viewer = { init, dispose }. */
(function () {
  "use strict";
  var THREE = window.THREE;
  var vistas = [];

  function _b64a(b64) {
    var bin = atob(b64);
    var n = bin.length;
    var bytes = new Uint8Array(n);
    for (var i = 0; i < n; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  function crearVisor(contenedor, modeloKey, cfg) {
    var renderer;
    try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); }
    catch (e) { renderer = null; }
    if (!renderer) { return null; }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputEncoding = THREE.sRGBEncoding;

    var escena = new THREE.Scene();
    escena.background = new THREE.Color(0x0a111f);

    var camara = new THREE.PerspectiveCamera(50, 1, 0.05, 400);
    camara.position.copy(cfg.pos);

    escena.add(new THREE.AmbientLight(0xffffff, 0.8));
    var dir = new THREE.DirectionalLight(0xffffff, 0.9);
    dir.position.set(5, 8, 4);
    escena.add(dir);
    escena.add(new THREE.HemisphereLight(0xdfe8f0, 0x101826, 0.35));

    var controles = new THREE.OrbitControls(camara, renderer.domElement);
    controles.target.copy(cfg.target);
    controles.enableDamping = true;
    controles.dampingFactor = 0.08;
    controles.minDistance = cfg.minDist || 0.3;
    controles.maxDistance = cfg.maxDist || 60;
    controles.maxPolarAngle = Math.PI * 0.95;
    controles.update();

    var carga = document.createElement("div");
    carga.className = "dc3v-carga";
    carga.textContent = "Cargando…";
    contenedor.appendChild(carga);

    var info = document.createElement("div");
    info.className = "dc3v-info";
    contenedor.appendChild(info);

    var raycaster = new THREE.Raycaster();
    var mouse = new THREE.Vector2();
    var sel = null;   // objeto seleccionado
    var downPos = null;

    var b64 = (window.DC3_MODELS || {})[modeloKey];
    if (!b64) { info.textContent = "Modelo no disponible."; return; }
    var glb = _b64a(b64).buffer;

    new THREE.GLTFLoader().parse(glb, '', function (gltf) {
      if (carga.parentNode) carga.parentNode.removeChild(carga);
      var modelo = gltf.scene;
      if (cfg.wireframe) {
        modelo.traverse(function (o) {
          if (o.isMesh) {
            o.material = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.9 });
          }
        });
      }
      var box = new THREE.Box3().setFromObject(modelo);
      var c = box.getCenter(new THREE.Vector3());
      var sz = box.getSize(new THREE.Vector3());
      var radio = Math.max(sz.x, sz.y, sz.z) || 1;
      if (!cfg.camaraManual) {
        var dir0 = cfg.pos.clone().sub(cfg.target).normalize();
        camara.position.copy(c).addScaledVector(dir0, radio * cfg.distancia);
        controles.target.copy(c);
      }
      controles.minDistance = Math.max(0.05, radio * 0.02);
      controles.maxDistance = radio * 4;
      controles.update();
      escena.add(modelo);
    }, function () {
      if (carga.parentNode) carga.parentNode.removeChild(carga);
      info.textContent = "No se pudo cargar el modelo 3D.";
    });

    function ajustar() {
      var w = contenedor.clientWidth || 1, h = contenedor.clientHeight || 1;
      camara.aspect = w / h; camara.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    function onPointerDown(ev) {
      var r = contenedor.getBoundingClientRect();
      downPos = { x: ev.clientX, y: ev.clientY };
    }
    function onPointerUp(ev) {
      if (!downPos) return;
      var dx = ev.clientX - downPos.x, dy = ev.clientY - downPos.y;
      downPos = null;
      if (dx * dx + dy * dy > 36) return;  // fue arrastre, no clic
      var r = contenedor.getBoundingClientRect();
      mouse.x = ((ev.clientX - r.left) / r.width) * 2 - 1;
      mouse.y = -((ev.clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camara);
      var hits = raycaster.intersectObjects(escena.children, true);
      if (sel && sel.object) { if (sel.object.material) sel.object.material.emissive.setHex(sel.origEmissive); sel = null; }
      if (hits.length) {
        var o = hits[0].object;
        if (o.isMesh && o.material) {
          var orig = o.material.emissive ? o.material.emissive.getHex() : 0;
          o.material.emissive = o.material.emissive || new THREE.Color(0);
          o.material.emissive.setHex(0x224466);
          sel = { object: o, origEmissive: orig };
          info.textContent = o.name || "Componente";
          return;
        }
      }
      info.textContent = "";
    }

    renderer.domElement.style.cssText = "display:block;width:100%;height:100%;touch-action:none;cursor:grab;";
    contenedor.appendChild(renderer.domElement);
    renderer.domElement.addEventListener("pointerdown", onPointerDown);
    renderer.domElement.addEventListener("pointerup", onPointerUp);

    ajustar();
    renderer.render(escena, camara);
    vistas.push({ renderer: renderer, escena: escena, camara: camara, controles: controles,
                  contenedor: contenedor, raycaster: raycaster, mouse: mouse, sel: sel, info: info,
                  _ajustar: ajustar });
    window.addEventListener("resize", ajustar);
    return true;
  }

  function init(contenedor) {
    dispose();
    contenedor.classList.add("dc3v-contenedor");
    contenedor.innerHTML =
      '<div class="dc3v-item"><div class="dc3v-titulo">A · Exterior — malla wireframe</div><div class="dc3v-lienzo" data-v="a"></div></div>';

    var a = contenedor.querySelector('[data-v="a"]');
    crearVisor(a, "exterior", { wireframe: true, pos: new THREE.Vector3(20, 10, 20), target: new THREE.Vector3(0, 0, 0), distancia: 1.3, minDist: 5, maxDist: 80 });

    iniciarBucle();
  }

  function iniciarBucle() {
    function bucle() {
      vistas.forEach(function (v) {
        v.controles.update();
        v.renderer.render(v.escena, v.camara);
      });
      if (vistas.length) requestAnimationFrame(bucle);
    }
    bucle();
  }

  function dispose() {
    vistas.forEach(function (v) {
      if (v._ajustar) window.removeEventListener("resize", v._ajustar);
      if (v.controles) v.controles.dispose();
      if (v.escena) {
        v.escena.traverse(function (o) {
          if (o.isMesh || o.isPoints) {
            if (o.geometry) o.geometry.dispose();
            if (o.material) {
              var m = Array.isArray(o.material) ? o.material : [o.material];
              m.forEach(function (mm) { if (mm.map) mm.map.dispose(); mm.dispose(); });
            }
          }
        });
      }
      if (v.renderer) {
        v.renderer.dispose();
        if (v.renderer.domElement && v.renderer.domElement.parentNode) v.renderer.domElement.parentNode.removeChild(v.renderer.domElement);
      }
    });
    vistas = [];
  }

  window.DC3Viewer = { init: init, dispose: dispose };
})();
