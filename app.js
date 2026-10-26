/* app.js — Proyecto AATD DC3 */
(function () {
  "use strict";
  var D = window.DATOS || null;
  var $ = function (s) { return document.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); };

  function init() {
    if (!D) { return; }
    (D.responsables_color || []).forEach(function (rc) { colorResp[rc.nombre] = rc.color; });
    renderHome();
    renderEdt();
    renderDescargas();
    renderCronograma();
    renderComunicacion();
    renderRiesgos();
    renderAcuerdos();
    renderAvances();
    renderCierre();
    renderGrupos();
    renderPracticas();
    renderDiagramas();
    renderBiblioteca();
    renderGlosario();
    renderMateriales();
    renderResponsablesPage();
    configurarNav();
    configurarTema();
    configurarReloj();
    configurarIntro();
    configurarVisor();
    configurarModal();
    configurarLightbox();
  }

  /* ================= HOME ================= */
  var matrizFiltro = { equipo: "" };
  var colorResp = {};

  function riesgosFiltrados() {
    var eq = matrizFiltro.equipo;
    return D.riesgos.filter(function (r) { return !eq || r.equipo === eq; });
  }

  function renderHome() {
    var p = D.proyecto;
    $("#resumen-ejecutivo").innerHTML =
      "<h3>Resumen ejecutivo</h3>" +
      "<p>El <strong>" + esc(p.nombre) + "</strong> convierte la cabina del " + esc(p.aeronave) +
      " (registro <strong>" + esc(p.matricula) + "</strong>) en un simulador terrestre de vuelo por instrumentos. " +
      "Plataforma <strong>" + esc(p.plataforma) + "</strong>; cabina virtual de referencia <strong>" + esc(p.cabina_virtual) + "</strong>. " +
      esc(p.naturaleza) + "</p>" +
      "<p>Fecha de acceso: <strong>" + esc(p.fecha) + "</strong> · Presupuesto: <strong>" + esc(p.presupuesto) +
      "</strong> · Beneficios cuantitativos: <strong>" + esc(p.beneficios_cuantitativos) + "</strong></p>";

    renderObjetivosBeneficios();
    renderResponsables();
    renderKpis();
    renderMatrizRiesgos();
    renderEstadoEquipos();
    renderAccesosRapidos();
  }

  function renderObjetivosBeneficios() {
    var p = D.proyecto;
    var objetivos = [
      ["Objetivo principal", "Reutilizar los mandos originales mediante sensorización e integrar hardware y software con X-Plane 12."],
      ["Validación", "Validar procedimientos IFR simulados (sin vuelo real)."],
      ["Documentación", "Producir documentación técnica profesional conforme al sistema EEA."],
      ["Formación", "Disponer de una plataforma de entrenamiento por instrumentos de bajo costo y reparable."]
    ];
    $("#objetivos").innerHTML = objetivos.map(function (o) {
      return '<div class="card"><h4>' + esc(o[0]) + '</h4><p>' + esc(o[1]) + '</p></div>';
    }).join("");
    var beneficios = [
      ["Alcance", "Inspección, limpieza, mecánica, aviónica, software, documentación, pruebas y entrega."],
      ["Duración y entregables", "Plazo nominal y entregables de los siete equipos (por confirmar)."],
      ["Presupuesto", esc(p.presupuesto) + " — base de cálculo pendiente de confirmar."],
      ["Beneficios", "Beneficios cualitativos: entrenamiento IFR, trazabilidad y reutilización de la cabina real."]
    ];
    $("#beneficios").innerHTML = beneficios.map(function (b) {
      return '<div class="card"><h4>' + esc(b[0]) + '</h4><p>' + esc(b[1]) + '</p></div>';
    }).join("");
  }

  function renderResponsables() {
    $("#responsables-home").innerHTML = D.responsables.map(function (r) {
      return '<div class="card"><h4>' + esc(r.nombre) + '</h4><p><strong>' + esc(r.rol) + '</strong></p><p>' + esc(r.cargo) + '</p></div>';
    }).join("");
  }

  function renderKpis() {
    var totalOI = 0, totalEntregables = 0;
    D.equipos.forEach(function (e) { totalOI += (e.ois || []).length; totalEntregables += (e.entregables || 0); });
    var porNivel = { Alto: 0, Medio: 0, Bajo: 0 };
    D.riesgos.forEach(function (r) { var n = norm(r.nivel); porNivel[n] = (porNivel[n] || 0) + 1; });
    var kpis = [
      { v: "Pendiente", t: "Progreso general del proyecto", c: "info", d: "No hay datos de avance; el progreso real se registrará al ejecutar las actividades." },
      { v: "0%", t: "Progreso de los 7 equipos", c: "info", d: "Los siete equipos inician en 0%. Sin avances reales registrados." },
      { v: totalOI, t: "Órdenes de trabajo (OI/OT)", c: "acento", d: "Total de órdenes de ingeniería y de trabajo inventariadas de los equipos." },
      { v: D.riesgos.length, t: "Riesgos registrados", c: porNivel.Alto > 0 ? "peligro" : "medio", d: "Riesgos potenciales consolidados del proyecto (no son incidentes ocurridos)." },
      { v: porNivel.Alto, t: "Riesgos de nivel alto", c: "peligro", d: "Riesgos con nivel alto o crítico, según la matriz de probabilidad × impacto." },
      { v: D.incidentes.length, t: "Incidentes abiertos", c: "pendiente", d: "Incidentes reales ocurridos y registrados (aún sin registros)." },
      { v: "0 / " + totalEntregables, t: "Entregables completados / total", c: "pendiente", d: "Ningún entregable marcado como completado todavía." },
      { v: D.acuerdos.length, t: "Acuerdos pendientes", c: "pendiente", d: "Acuerdos registrados (aún sin registros)." }
    ];
    $("#kpis").innerHTML = kpis.map(function (k, i) {
      return '<button class="kpi kpi-' + k.c + '" type="button" data-kpi="' + i + '">' +
        '<span class="kpi-num">' + esc(String(k.v)) + '</span><span class="kpi-txt">' + esc(k.t) + '</span></button>';
    }).join("");
    window._kpis = kpis;
  }

  function renderEstadoEquipos() {
    $("#estado-equipos").innerHTML = D.equipos.map(function (e) {
      var tareas = (e.ois || []).length, ent = (e.entregables || 0), ri = (e.riesgos || []).length;
      return '<div class="estado-equipo" title="Tareas: ' + tareas + ' · Entregables: ' + ent + ' · Riesgos: ' + ri + '">' +
        '<div class="cab"><span class="nombre">' + e.numero + ". " + esc(e.nombre) + '</span><span class="pct">0%</span></div>' +
        '<div class="barra"><div class="relleno" style="width:0%"></div></div>' +
        '<div class="meta">Tareas: ' + tareas + ' · Entregables: ' + ent + ' · Riesgos: ' + ri + '</div></div>';
    }).join("");
  }

  function renderAccesosRapidos() {
    var accesos = [
      ["edt", "🧩", "EDT"], ["cronograma", "📅", "Cronograma"], ["riesgos", "⚠️", "Riesgos"],
      ["diagramas", "📐", "Diagramas"], ["biblioteca", "📚", "Biblioteca"], ["glosario", "📖", "Glosario"]
    ];
    $("#accesos-rapidos").innerHTML = accesos.map(function (a) {
      return '<a class="acceso" href="#' + a[0] + '" data-seccion="' + a[0] + '"><span class="ico">' + a[1] +
        '</span><span class="txt">' + a[2] + "</span></a>";
    }).join("");
  }

  /* Matriz de riesgos interactiva */
  function renderMatrizRiesgos() {
    var sel = $("#matriz-filtro-equipo");
    var equipos = {};
    D.riesgos.forEach(function (r) { if (r.equipo) equipos[r.equipo] = true; });
    sel.innerHTML = '<option value="">Todos los equipos</option>' +
      Object.keys(equipos).sort().map(function (e) { return '<option value="' + esc(e) + '">' + esc(e) + '</option>'; }).join("");

    function pintar() {
      var conteo = { "Alto,Bajo": 0, "Alto,Medio": 0, "Alto,Alto": 0, "Medio,Bajo": 0, "Medio,Medio": 0, "Medio,Alto": 0, "Bajo,Bajo": 0, "Bajo,Medio": 0, "Bajo,Alto": 0 };
      riesgosFiltrados().forEach(function (r) {
        var pr = norm(r.prob), im = norm(r.impacto);
        if (pr === "Pendiente" || im === "Pendiente") return;
        conteo[pr + "," + im] = (conteo[pr + "," + im] || 0) + 1;
      });
      var filasProb = ["Alto", "Medio", "Bajo"];
      var colsImp = ["Bajo", "Medio", "Alto"];
      var h = '<div class="matriz-riesgo">';
      h += '<div class="matriz-celda vacio">Prob \\ Impacto</div>';
      colsImp.forEach(function (c) { h += '<div class="matriz-celda eje">' + c + '</div>'; });
      filasProb.forEach(function (pr) {
        h += '<div class="matriz-celda eje">' + pr + '</div>';
        colsImp.forEach(function (im) {
          var n = conteo[pr + "," + im] || 0;
          var nivel = nivelDe(pr, im);
          h += '<button class="matriz-celda ' + (n ? nivel : "vacio") + '" type="button" data-celda="' + pr + ',' + im + '"' +
            (n ? ' aria-label="' + n + ' riesgos — probabilidad ' + pr + ', impacto ' + im + '"' : ' disabled') + '>' + n + '</button>';
        });
      });
      h += "</div>";
      h += '<div class="leyenda">' +
        '<span class="ly l-critico">Crítico</span><span class="ly l-alto">Alto</span><span class="ly l-medio">Medio</span>' +
        '<span class="ly l-bajo">Bajo</span><span class="ly l-vacio">Sin registros</span><span class="ly l-info">Información</span>' +
        "</div>";
      h += '<p class="nota">La matriz usa los riesgos <strong>potenciales</strong> con probabilidad e impacto ya evaluados; los que están <strong>pendientes de evaluación</strong> y los <strong>incidentes</strong> (ocurridos) se registran por separado. Pulse una celda con valor para ver sus riesgos.</p>';
      $("#matriz-riesgo-resumen").innerHTML = h;
    }
    sel.onchange = function () { matrizFiltro.equipo = sel.value; pintar(); };
    pintar();
  }

  function mostrarRiesgosCelda(pr, im) {
    var filas = riesgosFiltrados().filter(function (r) {
      return norm(r.prob) === pr && norm(r.impacto) === im;
    });
    var html = "<h3>Riesgos — Probabilidad " + esc(pr) + " · Impacto " + esc(im) + "</h3>" +
      "<p>Total: <strong>" + filas.length + "</strong> · pulse una fila para ver el detalle.</p>";
    html += '<div class="tabla-contenedor"><table class="tabla"><thead><tr><th>ID</th><th>Descripción</th><th>Prob.</th><th>Impacto</th><th>Nivel</th><th>Estado</th><th>Responsables</th></tr></thead><tbody>' +
      filas.map(function (r) {
        var idx = D.riesgos.indexOf(r);
        return "<tr data-riesgo='" + idx + "' tabindex='0' role='button'><td>" + esc(r.id) + "</td><td>" + esc(r.nombre || r.peligro || "") + "</td><td>" + esc(r.prob) + "</td><td>" + esc(r.impacto) +
          "</td><td><span class='etiqueta " + claseNivel(r.nivel) + "'>" + esc(r.nivel) + "</span></td><td>" + esc(r.estado) +
          "</td><td>" + chipsResponsables(r) + "</td></tr>";
      }).join("") + "</tbody></table></div>";
    abrirModal(html);
  }

  function norm(v) {
    var s = String(v || "").toLowerCase();
    if (s.indexOf("pendiente") >= 0 || s.indexOf("evaluacion") >= 0 || s.indexOf("evaluación") >= 0) return "Pendiente";
    if (s.indexOf("muy alta") >= 0 || s.indexOf("alto") >= 0) return "Alto";
    if (s.indexOf("muy bajo") >= 0 || s.indexOf("bajo") >= 0) return "Bajo";
    if (s.indexOf("medio") >= 0 || s.indexOf("media") >= 0) return "Medio";
    return "Medio";
  }
  function claseNivel(v) {
    var s = String(v || "").toLowerCase();
    if (s.indexOf("pendiente") >= 0 || s.indexOf("evaluacion") >= 0 || s.indexOf("evaluación") >= 0) return "pendiente";
    if (s.indexOf("critic") >= 0) return "critico";
    if (s.indexOf("alto") >= 0) return "alto";
    if (s.indexOf("medio") >= 0 || s.indexOf("media") >= 0) return "medio";
    if (s.indexOf("bajo") >= 0) return "bajo";
    return "pendiente";
  }
  function nivelDe(pr, im) {
    var n = { "Alto": 3, "Medio": 2, "Bajo": 1 };
    var v = n[pr] * n[im];
    if (v >= 9) return "critico"; if (v >= 6) return "alto"; if (v >= 3) return "medio"; return "bajo";
  }

  /* ================= EDT ================= */
  function renderEdt() {
    var cont = $("#edt-arbol");
    cont.innerHTML = "";
    cont.appendChild(nodoEdt(D.edt));
    $("#edt-expandir").addEventListener("click", edtExpandirTodo);
    $("#edt-contraer").addEventListener("click", edtContraerTodo);
  }

  function nodoEdt(nodo) {
    var li = document.createElement("li");
    var tieneHijos = nodo.hijos && nodo.hijos.length;
    var fila = document.createElement("div");
    fila.className = "edt-fila";

    var chev = document.createElement("button");
    chev.className = "edt-chevron" + (tieneHijos ? "" : " edt-chevron-vacio");
    chev.type = "button";
    chev.textContent = tieneHijos ? "▶" : "";
    chev.setAttribute("aria-label", "Expandir o contraer " + nodo.nombre);
    if (tieneHijos) {
      chev.addEventListener("click", function (ev) {
        ev.stopPropagation();
        var ul = li.querySelector(":scope > ul");
        if (ul) { ul.classList.toggle("oculto"); chev.classList.toggle("abierto"); }
      });
    }
    fila.appendChild(chev);

    var b = document.createElement("button");
    b.className = "edt-nodo edt-" + (nodo.tipo || "fase");
    b.type = "button";
    b.innerHTML = esc(nodo.nombre);
    var clicable = (nodo.tipo === "ceo" || nodo.tipo === "supervisor" || nodo.tipo === "equipo" || nodo.tipo === "oi");
    if (clicable) {
      b.addEventListener("click", function (ev) {
        ev.stopPropagation();
        if (nodo.tipo === "ceo") mostrarCeo(nodo);
        else if (nodo.tipo === "supervisor") mostrarSupervisor(nodo);
        else if (nodo.tipo === "equipo") mostrarEquipo(nodo);
        else if (nodo.tipo === "oi") {
          var titulo = nodo.nombre + (nodo.titulo ? " — " + nodo.titulo : "");
          abrirVisor(nodo.archivo, titulo);
        }
      });
    } else {
      b.classList.add("edt-no-accion");
      b.setAttribute("aria-disabled", "true");
    }
    fila.appendChild(b);
    li.appendChild(fila);

    if (tieneHijos) {
      var ul = document.createElement("ul");
      nodo.hijos.forEach(function (h) { ul.appendChild(nodoEdt(h)); });
      li.appendChild(ul);
    }
    return li;
  }

  function edtExpandirTodo() {
    $$("#edt-arbol ul").forEach(function (ul) { ul.classList.remove("oculto"); });
    $$("#edt-arbol .edt-chevron").forEach(function (c) { c.classList.add("abierto"); });
  }
  function edtContraerTodo() {
    $$("#edt-arbol ul").forEach(function (ul) { ul.classList.add("oculto"); });
    $$("#edt-arbol .edt-chevron").forEach(function (c) { c.classList.remove("abierto"); });
  }

  function mostrarCeo(n) {
    abrirModal(
      "<h3>" + esc(n.nombre) + "</h3>" +
      "<p><strong>Rol:</strong> " + esc(n.rol) + "</p>" +
      "<p><strong>Cargo:</strong> " + esc(n.cargo) + "</p>" +
      "<p><strong>Decisiones:</strong> " + esc(n.decisiones || "Pendiente de confirmación") + "</p>" +
      '<div class="recomendaciones"><h4>Recomendaciones del equipo</h4><ul>' +
      (n.recomendaciones || []).map(function (r) { return "<li>" + esc(r) + "</li>"; }).join("") +
      "</ul></div>");
  }

  function mostrarSupervisor(n) {
    abrirModal(
      "<h3>" + esc(n.nombre) + "</h3>" +
      "<p><strong>Rol:</strong> " + esc(n.rol) + "</p>" +
      "<p><strong>Cargo:</strong> " + esc(n.cargo) + "</p>" +
      '<div class="recomendaciones"><h4>Recomendaciones</h4><ul>' +
      (n.recomendaciones || []).map(function (r) { return "<li>" + esc(r) + "</li>"; }).join("") +
      "</ul></div>");
  }

  function mostrarEquipo(n) {
    abrirModal(
      "<h3>" + esc(n.nombre) + "</h3>" +
      "<p><strong>Objetivo:</strong> " + esc(n.objetivo || "Pendiente de confirmación") + "</p>" +
      "<p><strong>Límites de trabajo:</strong> " + esc(n.limites || "Pendiente de confirmación") + "</p>" +
      "<p><strong>Responsabilidades:</strong> " + (n.responsabilidades || []).map(esc).join("; ") + "</p>" +
      "<p><strong>Entregables:</strong> " + (n.entregables || 0) + "</p>" +
      '<div class="card-acciones"><button class="boton" type="button" data-ver-manual="' + esc(n.manual) +
      '" data-titulo="Manual — ' + esc(n.nombre) + '">VER MANUAL DEL EQUIPO</button></div>');
  }

  function renderDescargas() {
    var cont = $("#descargas-contenido");
    var html = "";
    (D.descargas || []).forEach(function (g) {
      html += "<h4>" + esc(g.grupo) + "</h4><div class='grilla-cards'>" +
        g.archivos.map(function (a) {
          return '<div class="card"><h4>' + esc(a.nombre) + '</h4><p>Formato: ' + esc((a.tipo || "").toUpperCase()) + '</p>' +
            '<div class="card-acciones"><a class="boton boton-sec" href="' + esc(a.archivo) + '" download>Descargar</a>' +
            '<a class="boton" href="' + esc(a.archivo) + '" target="_blank" rel="noopener">Abrir</a></div></div>';
        }).join("") + "</div>";
    });
    cont.innerHTML = html || '<p class="nota">Sin archivos de descarga.</p>';
  }

  /* ================= CRONOGRAMA ================= */
  function renderCronograma() {
    var c = D.cronograma;
    $("#cronograma-inicio").textContent = c.inicio + " (" + c.inicio_marca + ")";
    $("#cronograma-escala").textContent = c.escala;

    var colapsados = new Set();
    var zoom = 1;

    var NOMBRE_MES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
    var ETIQUETAS = {};
    (c.categorias || []).forEach(function (cat) { ETIQUETAS[cat.id] = cat.etiqueta; });

    function nodoSinHijos(n) {
      return { tipo: n.tipo, nombre: n.nombre, rol: n.rol, cargo: n.cargo,
               decisiones: n.decisiones, recomendaciones: n.recomendaciones, hijos: [] };
    }
    // Nivel superior estricto: 9 elementos hermanos.
    var top = [nodoSinHijos(D.edt), nodoSinHijos(D.edt.hijos[0])].concat(D.edt.hijos[0].hijos);

    function diaW() { return 14 * zoom; }
    function dias(iso) {
      var d = new Date(iso + "T00:00:00");
      var i = new Date(c.inicio + "T00:00:00");
      return Math.round((d - i) / 86400000);
    }
    function recoger(nodo, nivel, equipo, out) {
      out.push({ nodo: nodo, nivel: nivel, equipo: equipo });
      if (colapsados.has(nodo)) return;
      var eq = nodo.tipo === "equipo" ? nodo.nombre : equipo;
      (nodo.hijos || []).forEach(function (h) { recoger(h, nivel + 1, eq, out); });
    }

    function clickLabel(nodo, equipo) {
      if (nodo.tipo === "ceo") mostrarCeo(nodo);
      else if (nodo.tipo === "supervisor") mostrarSupervisor(nodo);
      else if (nodo.tipo === "equipo") mostrarEquipo(nodo);
      else if (nodo.tipo === "oi") mostrarOi(nodo, equipo);
    }

    function pintar() {
      var cont = $("#gantt-contenedor");
      cont.innerHTML = "";
      var filas = [];
      top.forEach(function (n) { recoger(n, 0, "", filas); });
      var dw = diaW();
      var anchoTotal = c.span * dw;
      var altoFila = 30;

      var inner = document.createElement("div");
      inner.className = "gantt-inner";
      inner.style.minWidth = (280 + anchoTotal + 60) + "px";

      var izq = document.createElement("div");
      izq.className = "gantt-izq";
      var filaIzq = document.createElement("div");
      filaIzq.className = "gantt-izq-cab"; filaIzq.textContent = "Jerarquía";
      izq.appendChild(filaIzq);
      filas.forEach(function (f) {
        var r = document.createElement("div");
        r.className = "gantt-izq-fila gantt-" + f.nodo.tipo;
        r.style.height = altoFila + "px";
        var tiene = f.nodo.hijos && f.nodo.hijos.length;
        var chev = document.createElement("button");
        chev.className = "gantt-chev" + (tiene ? "" : " gantt-chev-vacio");
        chev.type = "button";
        chev.textContent = tiene ? (colapsados.has(f.nodo) ? "▶" : "▼") : "";
        if (tiene) {
          chev.addEventListener("click", function (ev) {
            ev.stopPropagation();
            if (colapsados.has(f.nodo)) colapsados.delete(f.nodo);
            else colapsados.add(f.nodo);
            pintar();
          });
        }
        var lbl = document.createElement("button");
        lbl.className = "gantt-lbl gantt-lbl-" + f.nodo.tipo;
        lbl.type = "button";
        lbl.style.paddingLeft = (f.nivel * 14 + 4) + "px";
        lbl.textContent = f.nodo.nombre;
        if (f.nodo.tipo === "fase") lbl.classList.add("gantt-lbl-noaccion");
        else lbl.addEventListener("click", function () { clickLabel(f.nodo, f.equipo); });
        r.appendChild(chev);
        r.appendChild(lbl);
        izq.appendChild(r);
      });

      var der = document.createElement("div");
      der.className = "gantt-der";
      der.style.width = anchoTotal + "px";
      var cab = document.createElement("div");
      cab.className = "gantt-cab";
      cab.style.width = anchoTotal + "px";
      cab.style.height = altoFila + "px";
      var dIni = new Date(c.inicio + "T00:00:00");
      for (var d = 0; d < c.span; d++) {
        var fecha = new Date(dIni.getTime() + d * 86400000);
        var x = d * dw;
        var diaEl = document.createElement("div");
        diaEl.className = "gantt-dia";
        diaEl.style.left = x + "px";
        diaEl.style.width = dw + "px";
        diaEl.textContent = fecha.getDate();
        cab.appendChild(diaEl);
        if (fecha.getDate() === 1) {
          var mes = document.createElement("div");
          mes.className = "gantt-mes";
          mes.style.left = x + "px";
          mes.textContent = NOMBRE_MES[fecha.getMonth()] + " " + fecha.getFullYear();
          cab.appendChild(mes);
        }
      }
      der.appendChild(cab);

      filas.forEach(function (f) {
        var r = document.createElement("div");
        r.className = "gantt-fila";
        r.style.height = altoFila + "px";
        var pista = document.createElement("div");
        pista.className = "gantt-pista";
        pista.style.width = anchoTotal + "px";
        if (f.nodo.tipo === "oi") {
          var ini = dias(f.nodo.inicio || c.inicio);
          var dur = Math.max(1, f.nodo.duracion || 1);
          var barra = document.createElement("button");
          barra.type = "button";
          barra.className = "gantt-barra gantt-c-" + (f.nodo.complejidad || "general");
          barra.style.left = (ini * dw) + "px";
          barra.style.width = (dur * dw - 3) + "px";
          barra.title = f.nodo.nombre + (f.nodo.titulo ? " — " + f.nodo.titulo : "");
          barra.textContent = f.nodo.nombre;
          barra.addEventListener("click", function () { mostrarOi(f.nodo, f.equipo); });
          pista.appendChild(barra);
        } else {
          var strip = document.createElement("div");
          strip.className = "gantt-strip gantt-" + f.nodo.tipo;
          pista.appendChild(strip);
        }
        r.appendChild(pista);
        der.appendChild(r);
      });

      var hoy = new Date();
      var hoyDias = Math.round((hoy - dIni) / 86400000);
      var linea = document.createElement("div");
      linea.className = "gantt-hoy";
      linea.style.left = (hoyDias * dw) + "px";
      linea.style.height = (filas.length * altoFila + altoFila) + "px";
      linea.title = "Hoy";
      der.appendChild(linea);

      inner.appendChild(izq);
      inner.appendChild(der);
      cont.appendChild(inner);

      var leg = $("#gantt-leyenda");
      leg.innerHTML = (c.categorias || []).map(function (cat) {
        return '<span class="gantt-leyenda-item"><span class="gantt-caja" style="background:' + cat.color + '"></span>' + esc(cat.etiqueta) + "</span>";
      }).join("");
    }

    function mostrarOi(nodo, equipo) {
      abrirModal(
        "<h3>" + esc(nodo.nombre) + "</h3>" +
        (nodo.titulo ? "<p><strong>Título:</strong> " + esc(nodo.titulo) + "</p>" : "") +
        "<p><strong>Equipo:</strong> " + esc(equipo || "—") + "</p>" +
        "<p><strong>Inicio:</strong> " + esc(nodo.inicio || "Pendiente de confirmación") +
        " · <strong>Fin:</strong> " + esc(nodo.fin || "Pendiente de confirmación") + "</p>" +
        "<p><strong>Duración:</strong> " + (nodo.duracion ? nodo.duracion + " días" : "Pendiente de confirmación") + "</p>" +
        "<p><strong>Complejidad:</strong> " + esc(ETIQUETAS[nodo.complejidad] || nodo.complejidad || "Pendiente de confirmación") + "</p>" +
        "<p><strong>Dependencias:</strong> " + ((nodo.dependencias && nodo.dependencias.length) ? esc(nodo.dependencias.join(", ")) : "Pendiente de confirmación") + "</p>" +
        "<p><strong>Estado:</strong> " + esc(nodo.estado || "Pendiente de confirmación") + "</p>" +
        '<div class="card-acciones"><button class="boton" type="button" data-ver-pdf="' + esc(nodo.archivo) +
        '" data-titulo="' + esc(nodo.nombre) + '">VER ORDEN DE INGENIERÍA PDF</button></div>');
    }

    $("#crono-expandir").onclick = function () { colapsados.clear(); pintar(); };
    $("#crono-contraer").onclick = function () {
      colapsados.clear();
      top.forEach(function (n) { if (n.tipo === "equipo") colapsados.add(n); });
      pintar();
    };
    $("#crono-zoom-in").onclick = function () { zoom = Math.min(4, zoom * 1.25); pintar(); };
    $("#crono-zoom-out").onclick = function () { zoom = Math.max(0.4, zoom / 1.25); pintar(); };
    $("#crono-ajustar").onclick = function () {
      var cont = $("#gantt-contenedor");
      var ancho = cont.clientWidth - 290;
      zoom = Math.max(0.2, ancho / (c.span * 14));
      pintar();
    };

    // Arrastre para desplazar (mouse + táctil)
    var cont = $("#gantt-contenedor");
    var arrastre = { activo: false, x: 0, y: 0, sl: 0, st: 0 };
    function iniciar(px, py) {
      arrastre.activo = true;
      arrastre.x = px; arrastre.y = py;
      arrastre.sl = cont.scrollLeft; arrastre.st = cont.scrollTop;
      cont.classList.add("gantt-arrastrando");
    }
    function mover(px, py) {
      if (!arrastre.activo) return;
      cont.scrollLeft = arrastre.sl - (px - arrastre.x);
      cont.scrollTop = arrastre.st - (py - arrastre.y);
    }
    function terminar() { arrastre.activo = false; cont.classList.remove("gantt-arrastrando"); }

    cont.addEventListener("mousedown", function (ev) {
      if (ev.target.closest(".gantt-barra, .gantt-chev, .gantt-lbl")) return;
      iniciar(ev.clientX, ev.clientY);
      ev.preventDefault();
    });
    document.addEventListener("mousemove", function (ev) { mover(ev.clientX, ev.clientY); });
    document.addEventListener("mouseup", terminar);
    cont.addEventListener("touchstart", function (ev) {
      var t = ev.touches[0];
      iniciar(t.clientX, t.clientY);
    }, { passive: true });
    cont.addEventListener("touchmove", function (ev) {
      if (!arrastre.activo) return;
      var t = ev.touches[0];
      mover(t.clientX, t.clientY);
    }, { passive: true });
    cont.addEventListener("touchend", terminar);

    // Zoom con rueda del ratón, centrado en el puntero
    cont.addEventListener("wheel", function (ev) {
      ev.preventDefault();
      var rect = cont.getBoundingClientRect();
      var pxRel = ev.clientX - rect.left + cont.scrollLeft;
      var diasAntes = pxRel / diaW();
      var nuevo = zoom * (ev.deltaY < 0 ? 1.1 : 0.9);
      zoom = Math.min(4, Math.max(0.4, nuevo));
      pintar();
      var pxNuevo = diasAntes * diaW();
      cont.scrollLeft = pxNuevo - (ev.clientX - rect.left);
    }, { passive: false });

    pintar();
  }

  /* ================= COMUNICACIÓN ================= */
  function renderComunicacion() {
    $("#comunicacion-lista").innerHTML = D.comunicacion.map(function (c) {
      return '<div class="card"><h4>' + esc(c.frecuencia) + '</h4>' +
        '<p><strong>Medio:</strong> ' + esc(c.medio) + '</p>' +
        '<p><strong>Participantes:</strong> ' + esc(c.participantes) + '</p>' +
        '<p><strong>Temas:</strong> ' + esc(c.temas) + '</p>' +
        '<p><strong>Registro:</strong> ' + esc(c.minuta) + '</p></div>';
    }).join("");
    $("#comunicacion-observaciones").innerHTML =
      '<div class="info-box" id="observaciones-juntas">' +
      '<h3>Observaciones, notas y comunicados de las juntas</h3>' +
      '<ul>' +
      '<li>Aquí se concentran las observaciones importantes generadas en las juntas.</li>' +
      '<li>Incluye notas, comentarios, decisiones e información que todo el equipo debe conocer.</li>' +
      '<li>Incluye coordinación entre equipos, asuntos pendientes de confirmar y recordatorios importantes.</li>' +
      '<li>La información se presenta por tema, para que todos los participantes la lean con rapidez.</li>' +
      '</ul>' +
      '<div class="estado-vacio"><div class="icono">📝</div><h3>Sin comunicados confirmados</h3>' +
      '<p>Esta es una zona de consulta estática. Mientras no existan actas de junta verificadas, se muestra este estado vacío; no se inventan minutas, acuerdos ni comentarios.</p></div>' +
      "</div>";
  }

  /* ================= RIESGOS ================= */
  var ordenNivel = { "pendiente": 0, "bajo": 1, "medio": 2, "alto": 3, "critico": 4 };
  var nivelEtiqueta = { "alto": "Alto", "medio": "Medio", "bajo": "Bajo", "pendiente": "Pendiente de evaluación" };

  function chipsResponsables(r) {
    var resp = (r.responsables && r.responsables.length) ? r.responsables : ["Aplicabilidad pendiente de validación"];
    return resp.map(function (nombre) {
      var color = colorResp[nombre];
      if (color) {
        return '<span class="chip-resp" title="Responsable: ' + esc(nombre) + '"><span class="chip-resp-punto" style="background:' + color + '"></span>' + esc(nombre) + "</span>";
      }
      return '<span class="chip-resp chip-resp-pendiente" title="Aplicabilidad pendiente de validación"><span class="chip-resp-punto"></span>' + esc(nombre) + "</span>";
    }).join("");
  }

  function seccionLista(titulo, items, numerada) {
    items = items || [];
    var tag = numerada ? "ol" : "ul";
    if (!items.length) return "<h5>" + esc(titulo) + '</h5><p class="nota">Pendiente de definición.</p>';
    return "<h5>" + esc(titulo) + "</h5><" + tag + ">" +
      items.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</" + tag + ">";
  }

  function mostrarRiesgoDetalle(r) {
    var nombre = r.nombre || r.peligro || "";
    var desc = r.descripcion || "";
    var html = "<h3>" + esc(r.id) + "</h3>" +
      '<p class="modal-sub"><span class="etiqueta-tipo ' + (r.tipo === "Incidente real" ? "incidente" : "riesgo") + '">' +
      esc(r.tipo === "Incidente real" ? "Incidente real" : "Riesgo potencial") + "</span>" +
      (r.categoria ? " <span class='modal-cat'>" + esc(r.categoria) + "</span>" : "") + "</p>" +
      "<h4>" + esc(nombre) + "</h4>" +
      (desc && desc !== nombre ? "<p>" + esc(desc) + "</p>" : "");

    html += "<h5>Responsables aplicables</h5><p>" + chipsResponsables(r) + "</p>";

    html += '<div class="modal-meta">' +
      "<div><strong>Probabilidad</strong><br>" + esc(r.prob || "Pendiente de evaluación") + "</div>" +
      "<div><strong>Impacto</strong><br>" + esc(r.impacto || "Pendiente de evaluación") + "</div>" +
      '<div><strong>Nivel de riesgo</strong><br><span class="etiqueta ' + claseNivel(r.nivel) + '">' + esc(r.nivel || "Pendiente de evaluación") + "</span></div>" +
      "<div><strong>Estado</strong><br>" + esc(r.estado || "Pendiente de evaluación") + "</div>" +
      "</div>";

    html += seccionLista("Posibles causas", r.causas);
    html += seccionLista("Condiciones disparadoras", r.disparadores);
    html += seccionLista("Consecuencias potenciales", r.consecuencias);
    html += seccionLista("Medidas preventivas", r.medidas_preventivas);
    html += seccionLista("Qué hacer si ocurre", r.que_hacer, true);
    html += seccionLista("Inspección y verificación", r.inspeccion);

    if (r.referencias && r.referencias.length) {
      html += '<h5>Referencias técnicas</h5><ul class="ref-lista">' +
        r.referencias.map(function (ref) {
          if (typeof ref === "string") return "<li>" + esc(ref) + "</li>";
          var li = "<li>";
          var titulo = ref.titulo || "Referencia";
          li += ref.url
            ? '<a href="' + esc(ref.url) + '" target="_blank" rel="noopener">' + esc(titulo) + "</a>"
            : "<span>" + esc(titulo) + "</span>";
          if (ref.org) li += " · <span class='ref-org'>" + esc(ref.org) + "</span>";
          if (ref.documento) li += " · " + esc(ref.documento);
          if (ref.seccion) li += " · <span class='ref-seccion'>" + esc(ref.seccion) + "</span>";
          if (ref.conclusion) li += '<br><span class="ref-concl">' + esc(ref.conclusion) + "</span>";
          li += "</li>";
          return li;
        }).join("") + "</ul>";
    } else {
      html += '<h5>Referencias técnicas</h5><p class="nota">Referencia específica pendiente de verificación.</p>';
    }

    abrirModal(html);
  }

  function renderRiesgos() {
    var selNivel = $("#riesgo-nivel");
    var niveles = {};
    D.riesgos.forEach(function (r) { niveles[claseNivel(r.nivel)] = true; });
    selNivel.innerHTML = '<option value="">Todos los niveles</option>' +
      ["alto", "medio", "bajo", "pendiente"].filter(function (k) { return niveles[k]; }).map(function (k) {
        return '<option value="' + k + '">' + nivelEtiqueta[k] + "</option>";
      }).join("");

    var leg = $("#riesgos-leyenda-responsables");
    if (leg) {
      leg.innerHTML = (D.responsables_color || []).map(function (rc) {
        return '<span class="chip-resp chip-resp-leyenda"><span class="chip-resp-punto" style="background:' + rc.color + '"></span>' + esc(rc.nombre) + "</span>";
      }).join("") + '<span class="leyenda-nota">El color identifica al responsable, no la severidad del riesgo.</span>';
    }

    var ascendente = false;
    function pintar() {
      var q = ($("#riesgo-busqueda").value || "").toLowerCase();
      var nv = selNivel.value;
      var filas = D.riesgos.filter(function (r) {
        var texto = (r.id + " " + (r.nombre || "") + " " + (r.descripcion || "") + " " + (r.peligro || "") + " " + (r.categoria || "")).toLowerCase();
        var okQ = !q || texto.indexOf(q) >= 0;
        var okN = !nv || claseNivel(r.nivel) === nv;
        return okQ && okN;
      }).sort(function (a, b) {
        var d = (ordenNivel[claseNivel(a.nivel)] || 0) - (ordenNivel[claseNivel(b.nivel)] || 0);
        return ascendente ? d : -d;
      });
      var tb = $("#tabla-riesgos tbody");
      tb.innerHTML = filas.map(function (r) {
        var idx = D.riesgos.indexOf(r);
        var tipo = r.tipo === "Incidente real" ? "Incidente real" : "Riesgo potencial";
        return '<tr data-riesgo="' + idx + '" tabindex="0" role="button" aria-label="Abrir detalle de ' + esc(r.id) + '">' +
          "<td>" + esc(r.id) + "</td>" +
          '<td><span class="etiqueta-tipo ' + (r.tipo === "Incidente real" ? "incidente" : "riesgo") + '">' + esc(tipo) + "</span></td>" +
          '<td><strong>' + esc(r.nombre || r.peligro || "") + "</strong></td>" +
          "<td>" + chipsResponsables(r) + "</td>" +
          "<td>" + esc(r.prob) + "</td>" +
          "<td>" + esc(r.impacto) + "</td>" +
          '<td><span class="etiqueta ' + claseNivel(r.nivel) + '">' + esc(r.nivel) + "</span></td>" +
          "<td>" + esc(r.estado) + "</td>" +
          "</tr>";
      }).join("");
    }
    $("#riesgo-busqueda").addEventListener("input", pintar);
    selNivel.addEventListener("change", pintar);
    $("#riesgo-orden").addEventListener("click", function () { ascendente = !ascendente; pintar(); });
    pintar();
  }

  /* ================= ACUERDOS / PRÁCTICAS ================= */
  function renderAcuerdos() {
    $("#acuerdos-contenido").innerHTML =
      '<div class="icono">🤝</div><h3>Sin acuerdos registrados</h3>' +
      "<p>No se han registrado acuerdos. No se muestran acuerdos ficticios.</p>";
  }
  function renderPracticas() {
    var ps = D.practicas || [];
    if (!ps.length) {
      $("#practicas-contenido").innerHTML =
        '<div class="estado-vacio"><div class="icono">🧪</div><h3>Prácticas — sin contenido</h3>' +
        "<p>Esta sección está reservada para las prácticas del proyecto; aún no hay registros.</p></div>";
      return;
    }
    $("#practicas-contenido").innerHTML = ps.map(function (p) {
      var num = ("0" + p.numero).slice(-2);
      var sub = p.codigo + (p.nivel ? " · " + p.nivel : "");
      return '<div class="card practica-card">' +
        '<div class="practica-cab">' +
          '<span class="practica-numero">' + num + "</span>" +
          '<div class="practica-titulos">' +
            '<span class="practica-codigo">' + esc(sub) + "</span>" +
            "<h4>" + esc(p.nombre) + "</h4>" +
          "</div>" +
        "</div>" +
        '<p class="practica-objetivo"><strong>Objetivo:</strong> ' + esc(p.objetivo) + "</p>" +
        '<div class="card-acciones">' +
          '<button class="boton" type="button" data-ver-pdf="' + esc(p.archivo) +
            '" data-titulo="' + esc(p.codigo + " — " + p.nombre) + '">Ver PDF</button>' +
        "</div>" +
        "</div>";
    }).join("");
  }

  /* ================= AVANCES ================= */
  function renderAvances() {
    var html = D.equipos.map(function (e) {
      return '<div class="progreso-item"><div class="fila"><span>' + esc(e.nombre) + '</span><span>0%</span></div>' +
        '<div class="progreso-barra"><div class="progreso-relleno" style="width:0%"></div></div></div>';
    }).join("");
    html += '<p class="nota">Sin datos de avance. El progreso de los siete equipos es 0% (sin registros reales).</p>';
    $("#avances-contenido").innerHTML = html;
  }

  /* ================= CIERRE ================= */
  function renderCierre() {
    var items = [
      ["Aceptación", "Verificación de entregables y criterios de aceptación.", "Pendiente"],
      ["Entrega", "Transferencia del expediente técnico final al Equipo Lógico.", "Pendiente"],
      ["Pendientes", "Lista de asuntos no cerrados.", "Pendiente"],
      ["Lecciones aprendidas", "Registro de experiencias del proyecto.", "Pendiente"],
      ["Checklist de cierre", "Verificación de actividades completadas.", "Pendiente"]
    ];
    $("#cierre-contenido").innerHTML = items.map(function (i) {
      return '<div class="card"><h4>' + esc(i[0]) + '</h4><p>' + esc(i[1]) + '</p>' +
        '<span class="etiqueta pendiente">' + esc(i[2]) + "</span></div>";
    }).join("");
  }

  /* ================= GRUPOS ================= */
  var PRIORIDAD_CLASE = { "Crítica": "critica", "Alta": "alta", "Media": "media", "Baja": "baja" };

  function panelEquipo(titulo, cuerpo) {
    return '<div class="acordeon"><button class="acordeon-cabecera" type="button" data-acordeon>' +
      "<span>" + esc(titulo) + "</span><span class='acordeon-flecha'>▶</span></button>" +
      '<div class="acordeon-cuerpo">' + cuerpo + "</div></div>";
  }

  function filaOi(o) {
    var prioClase = PRIORIDAD_CLASE[o.prioridad] || "media";
    var accion = o.archivo
      ? '<button class="boton boton-sec boton-oi" type="button" data-ver-pdf="' + esc(o.archivo) +
        '" data-titulo="' + esc(o.id + " — " + (o.titulo || "")) + '">' + esc(o.id) + " · " + esc(o.titulo || "") + " · Abrir PDF</button>"
      : '<span class="nota">Documento pendiente de incorporación</span>';
    return '<div class="oi-fila">' +
      '<div class="oi-info">' +
      '<code class="oi-id">' + esc(o.id) + "</code>" +
      '<div class="oi-titulo">' + esc(o.titulo || "") + "</div>" +
      '<div class="oi-meta">' +
      '<span class="oi-fase">Fase: ' + esc(o.fase_nombre || o.fase || "—") + "</span>" +
      '<span class="prioridad prioridad-' + prioClase + '" title="' + esc(o.prioridad_basis || "") + '">' + esc(o.prioridad || "Media") + "</span>" +
      "</div></div>" +
      '<div class="oi-accion">' + accion + "</div>" +
      "</div>";
  }

  function vistaEquipo(e) {
    var riesgos = e.riesgos || [];
    var ois = e.ois || [];
    var html = "";

    html += '<button class="boton boton-sec grupo-volver" id="grupo-volver" type="button">← Volver a equipos</button>';

    html += '<div class="equipo-cabecera">' +
      '<span class="equipo-punto equipo-punto-lg" style="background:' + esc(e.color) + '"></span>' +
      '<div><p class="equipo-kicker">Equipo ' + e.numero + "</p><h3>" + esc(e.nombre) + "</h3>" +
      '<p class="equipo-rol">' + esc(e.rol || "") + "</p></div></div>";

    html += '<div class="grilla-cards equipo-resumen">' +
      '<div class="card"><h4>Objetivo</h4><p>' + esc(e.objetivo) + "</p></div>" +
      '<div class="card"><h4>Responsabilidades</h4><ul class="lista-resumen">' +
      e.responsabilidades.map(function (r) { return "<li>" + esc(r) + "</li>"; }).join("") + "</ul></div>" +
      '<div class="card"><h4>Resumen</h4>' +
      "<p><strong>Órdenes de trabajo:</strong> " + ois.length + "</p>" +
      "<p><strong>Entregables:</strong> " + (e.entregables || 0) + "</p>" +
      "<p><strong>Riesgos registrados:</strong> " + riesgos.length + "</p>" +
      "<p><strong>Responsable:</strong> Pendiente de confirmación</p></div></div>";

    html += '<div class="equipo-manual">' +
      '<button class="boton" type="button" data-ver-manual="' + esc(e.manual) +
      '" data-titulo="Manual principal del equipo — ' + esc(e.nombre) + '">Manual principal del equipo · Abrir PDF</button></div>';

    var fases = e.fases || [];
    var actividades = fases.length
      ? "<ul>" + fases.map(function (f) {
          var n = ois.filter(function (o) { return String(o.fase) === String(f.id); }).length;
          return "<li><strong>" + esc(f.nombre) + "</strong> — " + n + " orden(es) de trabajo</li>";
        }).join("") + "</ul>"
      : '<p class="nota">Fases por definir.</p>';

    var seguridad = riesgos.length
      ? "<ul>" + riesgos.map(function (r) { return "<li>" + esc(r.peligro || r.nombre || "") + "</li>"; }).join("") +
        '</ul><p class="nota">El detalle completo (causas, medidas preventivas, qué hacer) está en el módulo Incidentes y Riesgos.</p>'
      : '<p class="nota">Sin riesgos registrados.</p>';

    html += '<div class="equipo-paneles">' +
      panelEquipo("Objetivo y alcance", "<p>" + esc(e.objetivo) + '</p><p><strong>Límites de trabajo:</strong> ' + esc(e.limites || "Pendiente de confirmación") + "</p>") +
      panelEquipo("Responsabilidades", "<ul>" + e.responsabilidades.map(function (r) { return "<li>" + esc(r) + "</li>"; }).join("") + "</ul>") +
      panelEquipo("Actividades y procedimientos", actividades) +
      panelEquipo("Entregables", "<p>Entregables registrados: <strong>" + (e.entregables || 0) + "</strong>.</p><p class='nota'>El detalle de cada entregable se define en los documentos del equipo.</p>") +
      panelEquipo("Seguridad y prevención de riesgos", seguridad) +
      panelEquipo("Coordinación con otros equipos", "<p><strong>Límites de trabajo:</strong> " + esc(e.limites || "Pendiente de confirmación") + '</p><p class="nota">Las dependencias específicas entre equipos se marcarán al confirmarse en el cronograma.</p>') +
      panelEquipo("Criterios de inspección y aceptación", '<p class="nota">Pendiente de definición: los criterios se establecerán con la evidencia de los documentos del equipo.</p>') +
      "</div>";

    html += "<h4>Órdenes de trabajo (" + ois.length + ")</h4>";
    html += '<div class="leyenda leyenda-prioridad">' +
      '<span class="ly p-critica">Crítica</span><span class="ly p-alta">Alta</span>' +
      '<span class="ly p-media">Media</span><span class="ly p-baja">Baja</span>' +
      '<span class="leyenda-nota">La prioridad deriva de la complejidad y fase del cronograma, no de la severidad de riesgos.</span></div>';
    html += '<div class="ois-lista">' + ois.map(filaOi).join("") + "</div>";

    html += "<h4>Coordinación y dependencias</h4>" +
      '<div class="acordeon"><button class="acordeon-cabecera" type="button" data-acordeon>' +
      "<span>Dependencias confirmadas</span><span class='acordeon-flecha'>▶</span></button>" +
      '<div class="acordeon-cuerpo"><p class="nota">Pendiente de confirmación: no hay dependencias entre equipos verificadas en los documentos actuales.</p></div></div>';

    html += '<div class="pizarra"><div class="pizarra-titulo">Pizarra del equipo · ' + esc(e.nombre) + "</div>" +
      '<p class="pizarra-msg">Aquí aparecerán las notas, solicitudes, observaciones y recomendaciones que el administrador publique para este equipo.</p></div>';

    return html;
  }

  function renderGrupos() {
    var cont = $("#grupos-contenido");

    function lista() {
      cont.innerHTML = '<div class="equipos-lista">' + D.equipos.map(function (e, idx) {
        return '<button class="equipo-tarjeta" type="button" data-equipo="' + idx + '" aria-label="Abrir equipo ' + esc(e.nombre) + '">' +
          '<span class="equipo-punto" style="background:' + esc(e.color) + '"></span>' +
          '<span class="equipo-info"><strong>' + e.numero + ". " + esc(e.nombre) + "</strong>" +
          "<small>" + esc(e.rol || "") + "</small></span>" +
          '<span class="equipo-flecha">›</span></button>';
      }).join("") + "</div>";
      $$("[data-equipo]").forEach(function (b) {
        b.addEventListener("click", function () { detalle(+b.getAttribute("data-equipo")); });
      });
    }

    function detalle(idx) {
      var e = D.equipos[idx];
      if (!e) { lista(); return; }
      cont.innerHTML = vistaEquipo(e);
      $$("#grupos-contenido [data-acordeon]").forEach(function (b) {
        b.addEventListener("click", function () { b.parentElement.classList.toggle("abierto"); });
      });
      $("#grupo-volver").addEventListener("click", lista);
    }

    lista();
  }

  /* ================= DIAGRAMAS ================= */
  var DIAGRAMAS_ARQ = [
    { src: "diagrama_arquitectura.svg", titulo: "A · Arquitectura general del simulador" },
    { src: "arq-mandos.svg", titulo: "B · Mandos y sensorización" },
    { src: "arq-avionica.svg", titulo: "C · Aviónica y visualización" },
    { src: "arq-software.svg", titulo: "D · Software y comunicaciones" },
    { src: "arq-electrica.svg", titulo: "E · Eléctrica y distribución de energía" },
    { src: "arq-flujo.svg", titulo: "F · Flujo funcional de una sesión" },
    { src: "arq-integracion.svg", titulo: "G · Integración y pruebas" }
  ];

  function construirGaleria(items, titulo, nota) {
    var wrap = document.createElement("div");
    var h3 = document.createElement("h3");
    h3.textContent = titulo;
    wrap.appendChild(h3);
    var p = document.createElement("p");
    p.className = "nota";
    p.textContent = nota;
    wrap.appendChild(p);
    var grid = document.createElement("div");
    grid.className = "galeria";
    items.forEach(function (it, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "galeria-item";
      var img = document.createElement("img");
      img.src = it.src; img.alt = it.titulo; img.loading = "lazy";
      var cap = document.createElement("span");
      cap.className = "galeria-caption";
      cap.innerHTML = esc(it.titulo) + (it.nota ? "<small>" + esc(it.nota) + "</small>" : "");
      b.appendChild(img); b.appendChild(cap);
      b.addEventListener("click", function () { abrirLightbox(items, i); });
      grid.appendChild(b);
    });
    wrap.appendChild(grid);
    return wrap;
  }

  function renderDiagramas() {
    function activar(nombre) {
      if (window.DC3Viewer) window.DC3Viewer.dispose();
      $$("#pestanas-diagramas .pestana").forEach(function (p) {
        p.classList.toggle("activa", p.getAttribute("data-pestana") === nombre);
      });
      var v = $("#visor-diagrama");
      v.innerHTML = "";
      if (nombre === "dc3") {
        var cont = document.createElement("div");
        cont.id = "dc3-visores";
        v.appendChild(cont);
        var nota = document.createElement("p");
        nota.className = "nota";
        nota.textContent = "Vista exterior del Douglas DC-3 (modelo FlightGear real) en malla wireframe. Arrastrar = rotar · rueda = zoom · botón derecho = desplazar.";
        v.appendChild(nota);
        if (window.DC3Viewer) window.DC3Viewer.init(cont);
      } else {
        v.appendChild(construirGaleria(DIAGRAMAS_ARQ, "Arquitectura del proyecto",
          "Siete diagramas complementarios. Pulse uno para ampliarlo con zoom, desplazamiento y navegación."));
      }
    }
    $$("#pestanas-diagramas .pestana").forEach(function (p) {
      p.addEventListener("click", function () { activar(p.getAttribute("data-pestana")); });
    });
    activar("dc3");
  }

  /* ---- Visor de imágenes (lightbox) ---- */
  var _lightboxItems = [], _lightboxIdx = 0, _lbZoom = 1, _lbPanX = 0, _lbPanY = 0;

  function _aplicarLightboxTransform() {
    var img = $("#lightbox-img");
    if (img) img.style.transform = "translate(" + _lbPanX + "px," + _lbPanY + "px) scale(" + _lbZoom + ")";
  }
  function _mostrarLightboxItem() {
    var it = _lightboxItems[_lightboxIdx];
    var img = $("#lightbox-img");
    img.src = it.src; img.alt = it.titulo;
    $("#lightbox-titulo").textContent = it.titulo + " (" + (_lightboxIdx + 1) + " / " + _lightboxItems.length + ")";
    _lbZoom = 1; _lbPanX = 0; _lbPanY = 0;
    _aplicarLightboxTransform();
  }
  function abrirLightbox(items, idx) {
    _lightboxItems = items || [];
    _lightboxIdx = Math.max(0, Math.min(_lightboxItems.length - 1, idx || 0));
    var lb = $("#lightbox");
    _mostrarLightboxItem();
    lb.classList.remove("oculto");
    lb.setAttribute("aria-hidden", "false");
    $("#lb-cerrar").focus();
  }
  function cerrarLightbox() {
    var lb = $("#lightbox");
    lb.classList.add("oculto");
    lb.setAttribute("aria-hidden", "true");
  }

  function configurarLightbox() {
    var lb = $("#lightbox"), escenario = $("#lightbox-escenario");
    var arrastre = null;
    function iniciar(x, y) { arrastre = { x: x, y: y, px: _lbPanX, py: _lbPanY }; }
    function mover(x, y) {
      if (!arrastre) return;
      _lbPanX = arrastre.px + (x - arrastre.x);
      _lbPanY = arrastre.py + (y - arrastre.y);
      _aplicarLightboxTransform();
    }
    escenario.addEventListener("mousedown", function (ev) { iniciar(ev.clientX, ev.clientY); ev.preventDefault(); });
    window.addEventListener("mousemove", function (ev) { mover(ev.clientX, ev.clientY); });
    window.addEventListener("mouseup", function () { arrastre = null; });
    escenario.addEventListener("wheel", function (ev) {
      ev.preventDefault();
      _lbZoom = Math.max(0.5, Math.min(6, _lbZoom * (ev.deltaY < 0 ? 1.15 : 0.87)));
      _aplicarLightboxTransform();
    }, { passive: false });
    $("#lb-zoom-in").addEventListener("click", function () { _lbZoom = Math.min(6, _lbZoom * 1.2); _aplicarLightboxTransform(); });
    $("#lb-zoom-out").addEventListener("click", function () { _lbZoom = Math.max(0.5, _lbZoom / 1.2); _aplicarLightboxTransform(); });
    $("#lb-ajustar").addEventListener("click", function () { _lbZoom = 1; _lbPanX = 0; _lbPanY = 0; _aplicarLightboxTransform(); });
    $("#lb-prev").addEventListener("click", function () { _lightboxIdx = (_lightboxIdx - 1 + _lightboxItems.length) % _lightboxItems.length; _mostrarLightboxItem(); });
    $("#lb-next").addEventListener("click", function () { _lightboxIdx = (_lightboxIdx + 1) % _lightboxItems.length; _mostrarLightboxItem(); });
    $("#lb-cerrar").addEventListener("click", cerrarLightbox);
    lb.addEventListener("click", function (ev) { if (ev.target === lb) cerrarLightbox(); });
    document.addEventListener("keydown", function (ev) {
      if (lb.classList.contains("oculto")) return;
      if (ev.key === "Escape") cerrarLightbox();
      else if (ev.key === "ArrowLeft") { _lightboxIdx = (_lightboxIdx - 1 + _lightboxItems.length) % _lightboxItems.length; _mostrarLightboxItem(); }
      else if (ev.key === "ArrowRight") { _lightboxIdx = (_lightboxIdx + 1) % _lightboxItems.length; _mostrarLightboxItem(); }
    });
  }

  /* ================= BIBLIOTECA ================= */
  function renderBiblioteca() {
    $("#biblioteca-lista").innerHTML = D.biblioteca.map(function (b) {
      var disp = b.estado === "Disponible";
      return '<div class="card"><h4>' + esc(b.titulo) + '</h4>' +
        "<p>Tamaño: " + b.mb + " MB</p>" +
        '<p><span class="etiqueta ' + (disp ? "bajo" : "pendiente") + '">' + esc(b.estado) + "</span></p>" +
        '<div class="card-acciones">' +
        (disp
          ? '<a href="' + esc(b.archivo) + '" class="boton" data-pdf="' + esc(b.titulo) + '">Ver</a>' +
            '<a href="' + esc(b.archivo) + '" class="boton boton-sec" download>Descargar</a>'
          : '<span class="nota">Archivo en revisión (excede el límite de publicación).</span>') +
        "</div></div>";
    }).join("");
    $("#referencias-oficiales").innerHTML = D.referencias_oficiales.map(function (r) {
      return '<div class="card"><h4>' + esc(r.nombre) + '</h4><p>' + esc(r.tipo) + '</p>' +
        '<p><a href="' + esc(r.enlace) + '" target="_blank" rel="noopener">' + esc(r.enlace) + "</a></p>" +
        '<p><span class="etiqueta pendiente">' + esc(r.estado) + "</span> — " + esc(r.nota) + "</p></div>";
    }).join("");
  }

  /* ================= GLOSARIO ================= */
  function renderGlosario() {
    function pintar() {
      var q = ($("#glosario-busqueda").value || "").toLowerCase();
      var filas = D.glosario.filter(function (g) {
        return !q || (g.termino + " " + g.definicion).toLowerCase().indexOf(q) >= 0;
      });
      $("#glosario-lista").innerHTML = '<dl class="glosario">' + filas.map(function (g) {
        return '<div class="glosario-term"><dt>' + esc(g.termino) + "</dt><dd>" + esc(g.definicion) + "</dd></div>";
      }).join("") + "</dl>";
    }
    $("#glosario-busqueda").addEventListener("input", pintar);
    pintar();
  }

  /* ================= MATERIALES ================= */
  var MAT_STORAGE_KEY = "aatd-materiales";
  var EST_MAT_CLASE = {
    "Existente": "existente",
    "Recuperable": "recuperable",
    "Por reparar": "reparar",
    "Por comprar": "comprar",
    "Pendiente de verificar": "pendiente"
  };

  function materialesLeer() {
    var datos = {};
    try { datos = JSON.parse(localStorage.getItem(MAT_STORAGE_KEY) || "{}") || {}; } catch (e) { datos = {}; }
    return datos;
  }
  function materialesGuardar(datos) {
    try { localStorage.setItem(MAT_STORAGE_KEY, JSON.stringify(datos)); } catch (e) {}
  }

  function renderMateriales() {
    var mods = D.materiales || [];
    var estados = D.estados_material || [];
    var marcados = materialesLeer();
    var cont = $("#materiales-contenido");
    if (!cont) return;

    var leyenda = $("#materiales-leyenda");
    if (leyenda) {
      leyenda.innerHTML = '<span class="leyenda-nota">Estado de cada material:</span>' +
        estados.map(function (e) {
          return '<span class="chip-resp chip-resp-leyenda"><span class="mat-punto ' +
            (EST_MAT_CLASE[e] || "pendiente") + '"></span>' + esc(e) + "</span>";
        }).join("");
    }

    function cantTexto(it) {
      var c = it.cantidad;
      if (c === null || c === undefined || c === "") return "Pendiente de verificar";
      return c;
    }

    function filaItem(it) {
      var marcado = !!marcados[it.id];
      var cls = EST_MAT_CLASE[it.estado] || "pendiente";
      return '<div class="mat-item' + (marcado ? " marcado" : "") + '">' +
        '<label class="mat-check">' +
        '<input type="checkbox" data-item="' + esc(it.id) + '"' + (marcado ? " checked" : "") +
        ' aria-label="Marcar ' + esc(it.nombre) + '">' +
        '<span class="mat-checkbox" aria-hidden="true"></span>' +
        "</label>" +
        '<div class="mat-cant"><span class="mat-cant-val">' + esc(String(cantTexto(it))) +
        '</span><span class="mat-cant-unidad">' + esc(it.unidad) + "</span></div>" +
        '<div class="mat-datos">' +
        '<div class="mat-nombre">' + esc(it.nombre) + "</div>" +
        (it.especificacion ? '<div class="mat-spec">' + esc(it.especificacion) + "</div>" : "") +
        (it.observacion ? '<div class="mat-obs">' + esc(it.observacion) + "</div>" : "") +
        "</div>" +
        '<span class="mat-estado mat-est-' + cls + '">' + esc(it.estado) + "</span>" +
        "</div>";
    }

    function pintarModulo(m) {
      var items = m.items || [];
      var grupos = {}, orden = [];
      items.forEach(function (it) {
        var g = it.grupo || "General";
        if (!grupos[g]) { grupos[g] = []; orden.push(g); }
        grupos[g].push(it);
      });
      var body = orden.map(function (g) {
        return '<div class="mat-grupo"><div class="mat-grupo-titulo">' + esc(g) + "</div>" +
          grupos[g].map(filaItem).join("") + "</div>";
      }).join("");
      var marcadosMod = items.filter(function (it) { return !!marcados[it.id]; }).length;
      var pct = items.length ? Math.round(100 * marcadosMod / items.length) : 0;
      return '<div class="acordeon mat-modulo' + (pct === 100 ? " completo" : "") +
        '" data-modulo="' + esc(m.id) + '">' +
        '<button class="acordeon-cabecera" type="button" data-acordeon>' +
        '<span class="mat-mod-titulo"><span class="mat-mod-codigo">' + esc(m.id) + "</span> " + esc(m.nombre) + "</span>" +
        '<span class="mat-mod-meta"><span class="mat-mod-cont">' + marcadosMod + " / " + items.length +
        '</span><span class="mat-mod-pct">' + pct + '%</span><span class="acordeon-flecha">▶</span></span>' +
        "</button>" +
        '<div class="acordeon-cuerpo">' +
        '<p class="mat-mod-desc">' + esc(m.descripcion) + "</p>" +
        '<div class="mat-progreso"><div class="mat-progreso-relleno" style="width:' + pct + '%"></div></div>' +
        body +
        "</div></div>";
    }

    cont.innerHTML = mods.map(pintarModulo).join("");

    function actualizarTotales() {
      $$("#materiales-contenido .mat-modulo").forEach(function (mod) {
        var mid = mod.getAttribute("data-modulo");
        var m = null;
        for (var i = 0; i < mods.length; i++) { if (mods[i].id === mid) { m = mods[i]; break; } }
        if (!m) return;
        var n = (m.items || []).length;
        var c = (m.items || []).filter(function (it) { return !!marcados[it.id]; }).length;
        var p = n ? Math.round(100 * c / n) : 0;
        mod.classList.toggle("completo", p === 100);
        var contEl = mod.querySelector(".mat-mod-cont"); if (contEl) contEl.textContent = c + " / " + n;
        var pctEl = mod.querySelector(".mat-mod-pct"); if (pctEl) pctEl.textContent = p + "%";
        var barra = mod.querySelector(".mat-progreso-relleno"); if (barra) barra.style.width = p + "%";
        Array.prototype.slice.call(mod.querySelectorAll(".mat-item")).forEach(function (row) {
          var cb = row.querySelector("input[data-item]");
          if (cb) row.classList.toggle("marcado", !!marcados[cb.getAttribute("data-item")]);
        });
      });
    }

    cont.addEventListener("change", function (ev) {
      var cb = ev.target.closest("input[data-item]");
      if (!cb) return;
      var id = cb.getAttribute("data-item");
      if (cb.checked) marcados[id] = true; else delete marcados[id];
      materialesGuardar(marcados);
      actualizarTotales();
    });

    cont.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-acordeon]");
      if (b) b.parentElement.classList.toggle("abierto");
    });

    $("#mat-expandir").addEventListener("click", function () {
      $$("#materiales-contenido .mat-modulo").forEach(function (m) { m.classList.add("abierto"); });
    });
    $("#mat-contraer").addEventListener("click", function () {
      $$("#materiales-contenido .mat-modulo").forEach(function (m) { m.classList.remove("abierto"); });
    });
    $("#mat-restablecer").addEventListener("click", function () {
      marcados = {};
      materialesGuardar(marcados);
      $$("#materiales-contenido input[data-item]").forEach(function (cb) { cb.checked = false; });
      actualizarTotales();
    });
  }

  /* ================= RESPONSABLES (gobernanza) ================= */
  function renderResponsablesPage() {
    var gob = D.gobernanza;
    var cont = $("#responsables-contenido");
    if (!cont || !gob) return;

    function lista(titulo, items) {
      if (!items || !items.length) return "";
      return "<h5>" + esc(titulo) + "</h5><ul>" +
        items.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    }

    var est = gob.estructura || {};
    var html = '<div class="resp-bloque">' +
      "<h3>" + esc(est.titulo || "Estructura de responsabilidades") + "</h3>" +
      '<div class="estructura">' +
      (est.niveles || []).map(function (n, i) {
        var miembros = n.miembros.map(function (m) {
          return '<span class="estructura-chip">' +
            (m.nombre ? "<strong>" + esc(m.nombre) + "</strong> · " : "") + esc(m.cargo) + "</span>";
        }).join("");
        var flecha = i < (est.niveles || []).length - 1 ? '<div class="estructura-flecha">↓</div>' : "";
        return '<div class="estructura-nivel"><div class="estructura-nivel-titulo">' + esc(n.nivel) + "</div>" +
          '<div class="estructura-miembros">' + miembros + "</div></div>" + flecha;
      }).join("") +
      (est.apoyo ? '<div class="estructura-apoyo"><div class="estructura-nivel-titulo">' + esc(est.apoyo.titulo) + "</div>" +
        '<div class="estructura-miembros">' + est.apoyo.miembros.map(function (m) {
          return '<span class="estructura-chip apoyo">' +
            (m.nombre ? "<strong>" + esc(m.nombre) + "</strong> · " : "") + esc(m.cargo) + "</span>";
        }).join("") + "</div></div>" : "") +
      "</div></div>";

    html += '<div class="resp-bloque"><h3>Perfiles y funciones</h3><div class="roles-lista">' +
      (gob.roles || []).map(function (r) {
        var entregables = (r.entregables && r.entregables.length)
          ? "<ul>" + r.entregables.map(function (e) { return "<li>" + esc(e) + "</li>"; }).join("") + "</ul>"
          : '<p class="nota">—</p>';
        var comunica = (r.comunica_con && r.comunica_con.length)
          ? r.comunica_con.map(function (c) { return '<span class="rol-chip">' + esc(c) + "</span>"; }).join("")
          : '<span class="nota">—</span>';
        return '<div class="acordeon rol-card">' +
          '<button class="acordeon-cabecera rol-cabecera" type="button" data-acordeon>' +
          '<span class="rol-icono">' + esc(r.icono) + "</span>" +
          '<span class="rol-titulos">' +
          '<span class="rol-cargo">' + esc(r.cargo) + "</span>" +
          (r.nombre ? '<span class="rol-nombre">' + esc(r.nombre) + "</span>" : "") +
          '<span class="rol-resumen">' + esc(r.resumen) + "</span>" +
          "</span>" +
          '<span class="acordeon-flecha">▶</span>' +
          "</button>" +
          '<div class="acordeon-cuerpo">' +
          '<div class="rol-meta">' +
          "<div><strong>Rol</strong><br>" + esc(r.rol) + "</div>" +
          "<div><strong>Reporta a</strong><br>" + esc(r.reporta_a) + "</div>" +
          "<div><strong>Organización</strong><br>" + esc(r.organizacion || "—") + "</div>" +
          "</div>" +
          lista("Responsabilidades", r.responsabilidades) +
          "<h5>Entregables</h5>" + entregables +
          "<h5>Comunica con</h5><div class='rol-chips'>" + comunica + "</div>" +
          '<div class="rol-limite"><strong>Límites y alcance:</strong> ' + esc(r.limite) + "</div>" +
          "</div></div>";
      }).join("") + "</div></div>";

    // Equipos de trabajo
    var et = gob.equipos_trabajo || {};
    html += '<div class="resp-bloque"><h3>' + esc(et.titulo || "Equipos de trabajo") + "</h3>" +
      (et.intro ? '<p class="seccion-intro">' + esc(et.intro) + "</p>" : "") +
      '<div class="equipos-trabajo">' +
      (et.equipos || []).map(function (e) {
        var resumen = (e.responsabilidades && e.responsabilidades.length) ? e.responsabilidades[0] : "";
        return '<div class="acordeon rol-card eq-card">' +
          '<button class="acordeon-cabecera rol-cabecera" type="button" data-acordeon>' +
          '<span class="rol-icono">' + esc(e.icono) + "</span>" +
          '<span class="rol-titulos">' +
          '<span class="rol-cargo">' + esc(e.nombre) + "</span>" +
          '<span class="rol-resumen">' + esc(resumen) + "</span>" +
          "</span>" +
          '<span class="acordeon-flecha">▶</span>' +
          "</button>" +
          '<div class="acordeon-cuerpo">' +
          lista("Responsabilidades", e.responsabilidades) +
          lista("Actividades principales", e.actividades) +
          lista("Entregables", e.entregables) +
          lista("Dependencias y colaboración", e.dependencias) +
          lista("Perfil recomendado del líder", e.perfil_lider) +
          (e.nota ? '<div class="eq-nota">' + esc(e.nota) + "</div>" : "") +
          "</div></div>";
      }).join("") +
      "</div>" +
      (et.nota ? '<p class="nota">' + esc(et.nota) + "</p>" : "") +
      "</div>";

    if (et.relaciones && et.relaciones.length) {
      html += '<div class="resp-bloque"><h3>' + esc(et.relaciones_titulo || "Relaciones y colaboración principal") + "</h3>" +
        '<div class="relaciones">' + et.relaciones.map(function (r) {
          return '<div class="relacion">' +
            '<span class="relacion-de">' + esc(r.de) + "</span>" +
            '<span class="relacion-flecha">→</span>' +
            '<span class="relacion-a">' + esc(r.a) + "</span>" +
            '<span class="relacion-tipo">' + esc(r.tipo) + "</span>" +
            "</div>";
        }).join("") + "</div>" +
        (et.relaciones_nota ? '<p class="nota">' + esc(et.relaciones_nota) + "</p>" : "") +
        "</div>";
    }

    var pl = gob.perfil_lider || {};
    html += '<div class="resp-bloque"><h3>' + esc(pl.titulo || "Perfil del líder de equipo") + "</h3>" +
      (pl.descripcion ? '<p class="seccion-intro">' + esc(pl.descripcion) + "</p>" : "") +
      '<div class="perfil-lider">' +
      '<ul class="perfil-criterios">' + (pl.criterios || []).map(function (c) { return "<li>" + esc(c) + "</li>"; }).join("") + "</ul>" +
      '<blockquote class="perfil-frase">' + esc(pl.frase || "") + "</blockquote>" +
      "</div></div>";

    var re = gob.reglas_equipos || {};
    html += '<div class="resp-bloque"><h3>' + esc(re.titulo || "Reglas para conformar equipos") + "</h3>" +
      '<div class="reglas-equipos">' +
      '<ol class="reglas-lista">' + (re.reglas || []).map(function (r2) { return "<li>" + esc(r2) + "</li>"; }).join("") + "</ol>" +
      (re.nota ? '<div class="reglas-nota">' + esc(re.nota) + "</div>" : "") +
      "</div></div>";

    var com = gob.comunicacion || {};
    html += '<div class="resp-bloque"><h3>' + esc(com.titulo || "Comunicación, reportes y escalamiento") + "</h3>" +
      '<div class="flujo">' + (com.flujo || []).map(function (f) {
        return '<div class="flujo-paso">' +
          '<div class="flujo-caja flujo-de">' + esc(f.de) + "</div>" +
          '<div class="flujo-flecha">→</div>' +
          '<div class="flujo-caja flujo-a">' + esc(f.a) + "</div>" +
          '<div class="flujo-nota">' + esc(f.nota) + "</div>" +
          "</div>";
      }).join("") + "</div>" +
      '<div class="canales-especiales">' + (com.canales_especiales || []).map(function (c) {
        return '<div class="canal"><strong>' + esc(c.titulo) + ":</strong> " + esc(c.responsable) + "</div>";
      }).join("") + "</div>" +
      "<h5>Reglas complementarias</h5>" +
      '<ul class="com-reglas">' + (com.reglas || []).map(function (r3) { return "<li>" + esc(r3) + "</li>"; }).join("") + "</ul>" +
      "</div>";

    cont.innerHTML = html;

    cont.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-acordeon]");
      if (b) b.parentElement.classList.toggle("abierto");
    });
  }

  /* ================= NAVEGACIÓN ================= */
  function configurarNav() {
    var enlaces = $$(".navegacion a, .navegacion-iconos a");
    var titulos = { home: "Home", edt: "EDT", cronograma: "Cronograma", comunicacion: "Plan de Comunicación",
      riesgos: "Incidentes y Riesgos", acuerdos: "Acuerdos", avances: "Reporte de Avances", cierre: "Cierre de Proyecto",
      grupos: "Grupos de trabajo", practicas: "Prácticas", diagramas: "Diagramas", biblioteca: "Biblioteca Técnica", glosario: "Glosario", materiales: "Materiales", responsables: "Responsables" };
    function activar(id) {
      $$(".seccion").forEach(function (s) { s.classList.toggle("activa", s.id === id); });
      enlaces.forEach(function (a) { a.classList.toggle("nav-activo", a.getAttribute("data-seccion") === id); });
      var tb = $("#barra-titulo");
      if (tb) tb.textContent = titulos[id] || "Home";
      window.scrollTo({ top: 0 });
    }
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest("[data-seccion]");
      if (!a) return;
      ev.preventDefault();
      activar(a.getAttribute("data-seccion"));
      var lat = $("#lateral"); if (lat) lat.classList.remove("abierta");
    });
    $("#btn-menu").addEventListener("click", function () { $("#lateral").classList.toggle("abierta"); });
    // Colapsar/expandir barra lateral
    $("#btn-lateral").addEventListener("click", function () {
      var colapsada = document.body.classList.toggle("lateral-colapsada");
      this.textContent = colapsada ? "»" : "«";
      this.title = colapsada ? "Expandir barra lateral" : "Contraer barra lateral";
      this.setAttribute("aria-expanded", colapsada ? "false" : "true");
    });
    var hash = (window.location.hash || "").replace("#", "");
    var secs = ["home", "edt", "cronograma", "comunicacion", "riesgos", "acuerdos", "avances", "cierre",
                "grupos", "practicas", "diagramas", "biblioteca", "glosario", "materiales", "responsables"];
    activar(secs.indexOf(hash) >= 0 ? hash : "home");
  }

  /* ================= TEMA ================= */
  function configurarTema() {
    var guardado = null; try { guardado = localStorage.getItem("aatd-tema"); } catch (e) {}
    var tema = (guardado === "oscuro" || guardado === "claro") ? guardado : "oscuro";
    function aplicar(t) {
      document.documentElement.setAttribute("data-tema", t);
      $("#btn-tema").textContent = t === "oscuro" ? "☀" : "☾";
    }
    $("#btn-tema").addEventListener("click", function () {
      var actual = document.documentElement.getAttribute("data-tema") || "oscuro";
      var nuevo = actual === "oscuro" ? "claro" : "oscuro";
      try { localStorage.setItem("aatd-tema", nuevo); } catch (e) {}
      aplicar(nuevo);
    });
    aplicar(tema);
  }

  /* ================= RELOJ ================= */
  function configurarReloj() {
    function tic() {
      var n = new Date(), p = function (x) { return (x < 10 ? "0" : "") + x; };
      var h = p(n.getUTCHours()), m = p(n.getUTCMinutes()), s = p(n.getUTCSeconds());
      var el = $("#reloj"); if (el) el.textContent = h + ":" + m + ":" + s + "Z";
      var el2 = $("#reloj-home"); if (el2) el2.innerHTML = h + ":" + m + ":" + s + "<span>Z</span>";
    }
    tic(); setInterval(tic, 1000);
  }

  /* ================= INTRO ================= */
  function configurarIntro() {
    var intro = $("#intro");
    var cerrar = function () { intro.classList.add("oculto"); };
    var reducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var t = setTimeout(cerrar, reducido ? 300 : 7000);
    $("#intro-saltar").addEventListener("click", function () { clearTimeout(t); cerrar(); });
  }

  /* ================= VISOR PDF ================= */
  var visorZoom = 1;

  function abrirVisor(url, titulo) {
    var visor = $("#visor"), frame = $("#visor-frame");
    $("#visor-titulo").textContent = titulo;
    $("#visor-descargar").href = url;
    visorZoom = 1;
    aplicarVisorZoom();
    $("#visor-carga").classList.remove("oculto");
    $("#visor-error").classList.add("oculto");
    frame.onload = function () { $("#visor-carga").classList.add("oculto"); };
    frame.src = url;
    visor.classList.remove("oculto");
    document.body.classList.add("sin-scroll");
  }

  function cerrarVisor() {
    var visor = $("#visor"), frame = $("#visor-frame");
    visor.classList.add("oculto");
    frame.src = "about:blank";
    $("#visor-carga").classList.remove("oculto");
    document.body.classList.remove("sin-scroll");
  }

  function aplicarVisorZoom() {
    var frame = $("#visor-frame");
    frame.style.transform = "scale(" + visorZoom + ")";
  }

  function configurarVisor() {
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest("a[data-pdf]");
      if (a) {
        ev.preventDefault();
        abrirVisor(a.getAttribute("href"), a.getAttribute("data-pdf"));
        return;
      }
      if (ev.target.closest("#ver-plan-maestro")) {
        abrirVisor("Plan_Maestro_DC3_Eben_Ezer_Aviation.pdf", "Plan Maestro del Proyecto");
      }
    });
    $("#visor-cerrar").addEventListener("click", cerrarVisor);
    $("#visor").addEventListener("click", function (ev) { if (ev.target === this) cerrarVisor(); });
    $("#pdf-zoom-in").addEventListener("click", function () { visorZoom = Math.min(2.5, visorZoom + 0.25); aplicarVisorZoom(); });
    $("#pdf-zoom-out").addEventListener("click", function () { visorZoom = Math.max(0.5, visorZoom - 0.25); aplicarVisorZoom(); });
    $("#pdf-ajustar").addEventListener("click", function () { visorZoom = 1; aplicarVisorZoom(); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !$("#visor").classList.contains("oculto")) cerrarVisor();
    });
  }

  /* ================= MODAL ================= */
  var modalUltimoFoco = null;
  function abrirModal(html) {
    if (html !== undefined && html !== null) $("#modal-contenido").innerHTML = html;
    var modal = $("#modal");
    modalUltimoFoco = document.activeElement;
    modal.classList.remove("oculto");
    modal.setAttribute("aria-hidden", "false");
    var c = $("#modal-cerrar");
    if (c) c.focus();
  }
  function cerrarModal() {
    var modal = $("#modal");
    modal.classList.add("oculto");
    modal.setAttribute("aria-hidden", "true");
    if (modalUltimoFoco && modalUltimoFoco.focus) {
      try { modalUltimoFoco.focus(); } catch (e) {}
    }
  }

  function configurarModal() {
    var modal = $("#modal");
    document.addEventListener("click", function (ev) {
      var rk = ev.target.closest("[data-riesgo]");
      if (rk) {
        var r = D.riesgos[+rk.getAttribute("data-riesgo")];
        if (r) mostrarRiesgoDetalle(r);
        return;
      }
      var celda = ev.target.closest("[data-celda]");
      if (celda) {
        var par = celda.getAttribute("data-celda").split(",");
        mostrarRiesgosCelda(par[0], par[1]);
        return;
      }
      var kpi = ev.target.closest("[data-kpi]");
      if (kpi) {
        var k = window._kpis && window._kpis[+kpi.getAttribute("data-kpi")];
        if (k) {
          abrirModal("<h3>" + esc(k.t) + "</h3><p><strong>Valor:</strong> " + esc(String(k.v)) + "</p><p>" + esc(k.d) + "</p>");
        }
        return;
      }
      var bm = ev.target.closest("[data-ver-manual]");
      if (bm) {
        var manual = bm.getAttribute("data-ver-manual");
        var mTitulo = bm.getAttribute("data-titulo") || "Manual del equipo";
        if (manual) {
          cerrarModal();
          abrirVisor(manual, mTitulo);
        }
        return;
      }
      var bp = ev.target.closest("[data-ver-pdf]");
      if (bp) {
        var pdf = bp.getAttribute("data-ver-pdf");
        var pTitulo = bp.getAttribute("data-titulo") || "Orden de ingeniería";
        if (pdf) {
          cerrarModal();
          abrirVisor(pdf, pTitulo);
        }
        return;
      }
    });
    $("#modal-cerrar").addEventListener("click", cerrarModal);
    modal.addEventListener("click", function (ev) { if (ev.target === modal) cerrarModal(); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        if (!$("#visor").classList.contains("oculto")) cerrarVisor();
        if (!modal.classList.contains("oculto")) cerrarModal();
        return;
      }
      if ((ev.key === "Enter" || ev.key === " ") && ev.target && ev.target.closest) {
        var rk = ev.target.closest("[data-riesgo]");
        if (rk) {
          ev.preventDefault();
          var r = D.riesgos[+rk.getAttribute("data-riesgo")];
          if (r) mostrarRiesgoDetalle(r);
        }
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
