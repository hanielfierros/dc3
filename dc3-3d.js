/* dc3-3d.js — Visor 3D wireframe del Douglas DC-3 (WebGL, sin dependencias externas).
   Expone window.DC3_3D.init(contenedor). Autocontenido y compatible con GitHub Pages. */
(function () {
  "use strict";
  var _ultimaLimpieza = null;

  function identidad() { return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]); }
  function multiplicar(a, b) {
    var out = new Float32Array(16);
    for (var c = 0; c < 4; c++) for (var r = 0; r < 4; r++) {
      var s = 0;
      for (var k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k];
      out[c * 4 + r] = s;
    }
    return out;
  }
  function trasladar(x, y, z) {
    var m = identidad(); m[12] = x; m[13] = y; m[14] = z; return m;
  }
  function rotarX(a) {
    var c = Math.cos(a), s = Math.sin(a);
    return new Float32Array([1,0,0,0, 0,c,s,0, 0,-s,c,0, 0,0,0,1]);
  }
  function rotarY(a) {
    var c = Math.cos(a), s = Math.sin(a);
    return new Float32Array([c,0,-s,0, 0,1,0,0, s,0,c,0, 0,0,0,1]);
  }
  function perspectiva(fovGrados, aspecto, cerca, lejos) {
    var f = 1 / Math.tan(fovGrados * Math.PI / 360);
    var nf = 1 / (cerca - lejos);
    return new Float32Array([
      f / aspecto, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (lejos + cerca) * nf, -1,
      0, 0, 2 * lejos * cerca * nf, 0
    ]);
  }

  /* ---- Geometría wireframe del DC-3 (puntos + líneas) ---- */
  function radioFuselaje(t) {
    if (t < 0.16) return 0.34 + 0.66 * Math.sin(t / 0.16 * Math.PI / 2);
    if (t > 0.84) return 0.34 + 0.66 * Math.cos((t - 0.84) / 0.16 * Math.PI / 2);
    return 1.0;
  }

  function construirGeometria() {
    var pts = [], lns = [];
    function L(x1, y1, z1, x2, y2, z2) { lns.push(x1, y1, z1, x2, y2, z2); }
    function P(x, y, z) { pts.push(x, y, z); }
    function linea(a, b) { L(a[0], a[1], a[2], b[0], b[1], b[2]); }
    function punto(a) { P(a[0], a[1], a[2]); }

    // Fuselaje (tubo ahusado con secciones circulares)
    var S = 26, R = 16, anillos = [];
    for (var i = 0; i <= S; i++) {
      var t = i / S, x = -6 + t * 12, r = radioFuselaje(t);
      var anillo = [];
      for (var j = 0; j < R; j++) {
        var a = j / R * Math.PI * 2;
        anillo.push([x, Math.cos(a) * r, Math.sin(a) * r]);
      }
      anillos.push(anillo);
    }
    for (i = 0; i < S; i++) for (j = 0; j < R; j++) linea(anillos[i][j], anillos[i + 1][j]);
    for (i = 0; i <= S; i++) for (j = 0; j < R; j++) linea(anillos[i][j], anillos[i][(j + 1) % R]);
    for (i = 0; i <= S; i++) for (j = 0; j < R; j++) punto(anillos[i][j]);

    // Alas (planos ahusados, uno por lado)
    var raizLE = -1.2, raizTE = 2.2, puntaLE = 0.2, puntaTE = 1.6, raizZ = 1.1, puntaZ = 7.2;
    [-1, 1].forEach(function (lado) {
      var zr = raizZ * lado, zt = puntaZ * lado;
      L(raizLE, 0.05, zr, puntaLE, 0.35, zt);
      L(raizTE, 0.05, zr, puntaTE, 0.35, zt);
      L(raizLE, 0.05, zr, raizTE, 0.05, zr);
      L(puntaLE, 0.35, zt, puntaTE, 0.35, zt);
      L(raizLE, -0.05, zr, puntaLE, 0.25, zt);
      L(raizTE, -0.05, zr, puntaTE, 0.25, zt);
      for (var k = 0; k <= 6; k++) {
        var u = k / 6, xx = raizLE + (puntaLE - raizLE) * u, zz = zr + (zt - zr) * u, yy = 0.05 + 0.30 * u;
        P(xx, yy, zz); P(xx, -0.05 + 0.25 * u, zz);
      }
    });

    // Góndolas de motor (cilindros) + hélices
    [-1, 1].forEach(function (lado) {
      var z = 2.6 * lado, ex = 0.4, r = 0.5, exf = 1.6, exb = -0.4, nr = 12;
      var a1 = [], a2 = [];
      for (var j = 0; j < nr; j++) {
        var a = j / nr * Math.PI * 2, cy = Math.cos(a) * r, cz = Math.sin(a) * r;
        a1.push([exf, cy, z + cz]); a2.push([exb, cy, z + cz]);
      }
      for (j = 0; j < nr; j++) { linea(a1[j], a2[j]); linea(a1[j], a1[(j + 1) % nr]); linea(a2[j], a2[(j + 1) % nr]); }
      for (j = 0; j < nr; j++) { punto(a1[j]); punto(a2[j]); }
      // hélice (disco en el plano YZ)
      for (j = 0; j < nr; j++) {
        var a = j / nr * Math.PI * 2;
        L(exf + 0.15, Math.cos(a) * 0.85, z + Math.sin(a) * 0.85,
          exf + 0.15, Math.cos(a + Math.PI * 2 / nr) * 0.85, z + Math.sin(a + Math.PI * 2 / nr) * 0.85);
        P(exf + 0.15, Math.cos(a) * 0.85, z + Math.sin(a) * 0.85);
      }
    });

    // Empenaje: deriva vertical + estabilizador horizontal
    var tx = 5.2;
    L(tx, 0, 0, tx + 1.1, 1.9, 0);
    L(tx, 0, 0, tx, 1.4, 0);
    L(tx + 1.1, 0, 0, tx + 1.1, 1.0, 0);
    L(tx, 1.4, 0, tx + 1.1, 1.0, 0);
    L(tx + 0.1, 0, 0, tx + 0.1, 1.3, 0);
    [-2.8, 2.8].forEach(function (z) {
      L(tx, 0.1, 0, tx + 0.6, 0.3, z);
      L(tx, 0.0, 0, tx + 0.6, 0.15, z);
    });
    L(tx + 0.6, 0.3, -2.8, tx + 0.6, 0.3, 2.8);
    L(tx + 0.6, 0.15, -2.8, tx + 0.6, 0.15, 2.8);
    P(tx, 1.9, 0); P(tx + 1.1, 1.9, 0); P(tx + 0.6, 0.3, -2.8); P(tx + 0.6, 0.3, 2.8);

    // Tren de aterrizaje (dos patas principales + rueda de cola)
    [-1, 1].forEach(function (lado) {
      var z = 1.6 * lado;
      L(0.6, -0.9, z, 0.8, -1.9, z + 0.5);
      L(0.6, -0.9, z, 0.3, -1.9, z + 0.1);
      L(0.8, -1.9, z + 0.5, 0.3, -1.9, z + 0.1);
      P(0.8, -1.9, z + 0.5); P(0.3, -1.9, z + 0.1);
    });
    L(5.3, -0.35, 0, 5.3, -0.85, 0);
    P(5.3, -0.85, 0);

    return { puntos: new Float32Array(pts), lineas: new Float32Array(lns) };
  }

  function compilar(gl, tipo, src) {
    var sh = gl.createShader(tipo);
    gl.shaderSource(sh, src);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(sh) || "Error de compilación de shader");
    }
    return sh;
  }

  function init(contenedor) {
    if (!contenedor) return;
    contenedor.innerHTML = "";

    var lienzo = document.createElement("canvas");
    lienzo.style.cssText = "display:block;width:100%;height:100%;touch-action:none;cursor:grab;";
    lienzo.setAttribute("aria-label", "Modelo 3D interactivo del Douglas DC-3 (wireframe)");
    contenedor.appendChild(lienzo);

    var gl = null;
    try {
      gl = lienzo.getContext("webgl", { antialias: true, alpha: true }) ||
           lienzo.getContext("experimental-webgl", { antialias: true, alpha: true });
    } catch (e) { gl = null; }

    if (!gl) {
      contenedor.innerHTML = '<div class="dc3-fallback"><div class="icono">⚠️</div>' +
        '<h3>No se pudo iniciar el visor 3D</h3>' +
        "<p>Su navegador no soporta WebGL. Puede revisar los diagramas de arquitectura en la pestaña correspondiente.</p></div>";
      return;
    }

    var geo = construirGeometria();

    var vSrc = "attribute vec3 aPos;uniform mat4 uMVP;void main(){gl_Position=uMVP*vec4(aPos,1.0);gl_PointSize=2.2;}";
    var fSrc = "precision mediump float;uniform vec4 uColor;void main(){gl_FragColor=uColor;}";
    var prog = gl.createProgram();
    gl.attachShader(prog, compilar(gl, gl.VERTEX_SHADER, vSrc));
    gl.attachShader(prog, compilar(gl, gl.FRAGMENT_SHADER, fSrc));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(prog) || "Error al enlazar programa WebGL");
    }
    gl.useProgram(prog);

    var locPos = gl.getAttribLocation(prog, "aPos");
    var locMVP = gl.getUniformLocation(prog, "uMVP");
    var locColor = gl.getUniformLocation(prog, "uColor");

    function crearBuffer(data) {
      var b = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, b);
      gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
      return b;
    }
    var bufLineas = crearBuffer(geo.lineas);
    var bufPuntos = crearBuffer(geo.puntos);
    var nLineas = geo.lineas.length / 3;
    var nPuntos = geo.puntos.length / 3;

    // Estado de cámara
    var yaw = -0.62, pitch = 0.42, dist = 17, panX = 0, panY = 0;
    var DIST_MIN = 7.5, DIST_MAX = 34, PITCH_MAX = 1.45;
    var INICIO = { yaw: -0.62, pitch: 0.42, dist: 17, panX: 0, panY: 0 };

    function mvp() {
      var view = trasladar(panX, panY, 0);
      view = multiplicar(view, trasladar(0, 0, -dist));
      view = multiplicar(view, rotarX(pitch));
      view = multiplicar(view, rotarY(yaw));
      return multiplicar(perspectiva(45, lienzo.width / Math.max(1, lienzo.height), 0.1, 200), view);
    }

    function dibujar() {
      gl.viewport(0, 0, lienzo.width, lienzo.height);
      gl.clearColor(0, 0, 0, 0);
      gl.enable(gl.DEPTH_TEST);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      var m = mvp();
      gl.uniformMatrix4fv(locMVP, false, m);
      gl.enableVertexAttribArray(locPos);
      gl.bindBuffer(gl.ARRAY_BUFFER, bufLineas);
      gl.vertexAttribPointer(locPos, 3, gl.FLOAT, false, 0, 0);
      gl.uniform4fv(locColor, new Float32Array([0.22, 0.53, 0.79, 0.9]));
      gl.drawArrays(gl.LINES, 0, nLineas);
      gl.bindBuffer(gl.ARRAY_BUFFER, bufPuntos);
      gl.vertexAttribPointer(locPos, 3, gl.FLOAT, false, 0, 0);
      gl.uniform4fv(locColor, new Float32Array([0.45, 0.80, 1.0, 1.0]));
      gl.drawArrays(gl.POINTS, 0, nPuntos);
      gl.disableVertexAttribArray(locPos);
    }

    function ajustar() {
      var dpr = window.devicePixelRatio || 1;
      var w = Math.max(1, contenedor.clientWidth);
      var h = Math.max(1, contenedor.clientHeight || 460);
      lienzo.width = Math.round(w * dpr);
      lienzo.height = Math.round(h * dpr);
      dibujar();
    }

    // Interacción (mouse + táctil)
    var agarre = null; // {tipo:'rotar'|'mover', x, y, ...}
    var pinch = null;  // {dist0, distBase}

    function puntero(ev) {
      if (ev.touches && ev.touches.length) {
        return { x: ev.touches[0].clientX, y: ev.touches[0].clientY };
      }
      return { x: ev.clientX, y: ev.clientY };
    }

    lienzo.addEventListener("mousedown", function (ev) {
      if (ev.button === 0 || ev.button === 2) {
        agarre = { tipo: ev.button === 2 ? "mover" : "rotar", x: ev.clientX, y: ev.clientY, yaw: yaw, pitch: pitch, panX: panX, panY: panY };
        lienzo.style.cursor = "grabbing";
        ev.preventDefault();
      }
    });
    _ultimaLimpieza = [];
    function _onMove(ev) {
      if (!agarre) return;
      var dx = ev.clientX - agarre.x, dy = ev.clientY - agarre.y;
      if (agarre.tipo === "rotar") {
        yaw = agarre.yaw + dx * 0.008;
        pitch = Math.max(-PITCH_MAX, Math.min(PITCH_MAX, agarre.pitch + dy * 0.008));
      } else {
        panX = agarre.panX + dx * 0.02;
        panY = agarre.panY - dy * 0.02;
      }
      dibujar();
    }
    function _onUp() {
      if (agarre) { agarre = null; lienzo.style.cursor = "grab"; }
    }
    function _onResize() { ajustar(); }
    window.addEventListener("mousemove", _onMove);
    window.addEventListener("mouseup", _onUp);
    window.addEventListener("resize", _onResize);
    _ultimaLimpieza.push(function () {
      window.removeEventListener("mousemove", _onMove);
      window.removeEventListener("mouseup", _onUp);
      window.removeEventListener("resize", _onResize);
    });
    lienzo.addEventListener("contextmenu", function (ev) { ev.preventDefault(); });
    lienzo.addEventListener("wheel", function (ev) {
      ev.preventDefault();
      dist = Math.max(DIST_MIN, Math.min(DIST_MAX, dist * (ev.deltaY > 0 ? 1.1 : 0.9)));
      dibujar();
    }, { passive: false });
    lienzo.addEventListener("dblclick", function () {
      yaw = INICIO.yaw; pitch = INICIO.pitch; dist = INICIO.dist; panX = 0; panY = 0;
      dibujar();
    });

    lienzo.addEventListener("touchstart", function (ev) {
      if (ev.touches.length === 1) {
        agarre = { tipo: "rotar", x: ev.touches[0].clientX, y: ev.touches[0].clientY, yaw: yaw, pitch: pitch, panX: panX, panY: panY };
      } else if (ev.touches.length === 2) {
        agarre = { tipo: "mover", x: (ev.touches[0].clientX + ev.touches[1].clientX) / 2, y: (ev.touches[0].clientY + ev.touches[1].clientY) / 2, panX: panX, panY: panY };
        pinch = { d0: Math.hypot(ev.touches[0].clientX - ev.touches[1].clientX, ev.touches[0].clientY - ev.touches[1].clientY), dist: dist };
      }
    }, { passive: true });
    lienzo.addEventListener("touchmove", function (ev) {
      if (agarre && ev.touches.length === 1 && agarre.tipo === "rotar") {
        var dx = ev.touches[0].clientX - agarre.x, dy = ev.touches[0].clientY - agarre.y;
        yaw = agarre.yaw + dx * 0.008;
        pitch = Math.max(-PITCH_MAX, Math.min(PITCH_MAX, agarre.pitch + dy * 0.008));
        dibujar();
      } else if (agarre && ev.touches.length === 2) {
        var cx = (ev.touches[0].clientX + ev.touches[1].clientX) / 2;
        var cy = (ev.touches[0].clientY + ev.touches[1].clientY) / 2;
        panX = agarre.panX + (cx - agarre.x) * 0.02;
        panY = agarre.panY - (cy - agarre.y) * 0.02;
        if (pinch) {
          var d = Math.hypot(ev.touches[0].clientX - ev.touches[1].clientX, ev.touches[0].clientY - ev.touches[1].clientY);
          dist = Math.max(DIST_MIN, Math.min(DIST_MAX, pinch.dist * pinch.d0 / Math.max(1, d)));
        }
        dibujar();
      }
    }, { passive: true });
    lienzo.addEventListener("touchend", function () { agarre = null; pinch = null; });

    // Indicador de ejes + leyenda (overlay HTML)
    var overlay = document.createElement("div");
    overlay.className = "dc3-overlay";
    overlay.innerHTML =
      '<span class="dc3-ejes"><b style="color:#f87171">X</b> <b style="color:#34d399">Y</b> <b style="color:#38bdf8">Z</b></span>' +
      '<span class="dc3-leyenda">Arrastrar = rotar · Rueda = zoom · Botón derecho = desplazar · Doble clic = centrar</span>';
    contenedor.appendChild(overlay);

    _ultimaLimpieza.push(function () {
      var cnv = contenedor.querySelector("canvas");
      if (cnv && cnv.parentNode) cnv.parentNode.removeChild(cnv);
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    });

    ajustar();
    dibujar();
  }

  function dispose() {
    if (_ultimaLimpieza) {
      var fns = _ultimaLimpieza;
      _ultimaLimpieza = null;
      fns.forEach(function (f) { try { f(); } catch (e) {} });
    }
  }

  window.DC3_3D = { init: init, dispose: dispose };
})();
