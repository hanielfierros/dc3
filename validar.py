# -*- coding: utf-8 -*-
"""
validar.py — Valida el sitio estático del Proyecto AATD DC3 y genera
informe_pruebas.txt.

Comprueba: estructura plana, archivos requeridos, validez de datos.json/datos.js,
referencias de index.html, anclas de navegación, SVG, recursos de la biblioteca
y duplicados de número.
"""
import os
import re
import json
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

REQUERIDOS = [
    "index.html", "estilos.css", "app.js", "datos.json", "datos.js",
    "construir.py", "validar.py", "README.md", ".nojekyll", ".gitignore",
    "dependencias.txt", "informe_archivos.txt",
    "eea-logo-light.png", "eea-logo-dark.png", "dpc-logo.png", "earth.jpg",
    "wireframe-dc3.svg", "panel-kingair90.svg", "diagrama_arquitectura.svg",
    "Plan_Maestro_DC3_Eben_Ezer_Aviation.pdf",
]


def main():
    resultados = []

    def check(desc, cond, detalle=""):
        resultados.append((cond, desc + ((" - " + detalle) if detalle else "")))

    # 1) estructura plana (el directorio de metadatos .git no se publica)
    subdirs = [d for d in os.listdir(ROOT)
               if os.path.isdir(os.path.join(ROOT, d)) and d != ".git"]
    check("Estructura plana (sin subcarpetas)", not subdirs, "subcarpetas: %s" % subdirs)

    # 2) archivos requeridos
    falt = [f for f in REQUERIDOS if not os.path.exists(os.path.join(ROOT, f))]
    check("Archivos requeridos", not falt, "faltantes: %s" % falt)

    # 3) datos.json
    try:
        datos = json.load(open(os.path.join(ROOT, "datos.json"), encoding="utf-8"))
        claves = ["proyecto", "responsables", "equipos", "edt", "cronograma",
                  "comunicacion", "fases", "riesgos", "incidentes", "acuerdos",
                  "avances", "biblioteca", "referencias_oficiales", "glosario",
                  "practicas", "materiales", "estados_material", "gobernanza"]
        ok = all(k in datos for k in claves)
        check("datos.json válido y con claves", ok,
              "equipos=%d riesgos=%d biblioteca=%d" % (len(datos.get("equipos", [])),
              len(datos.get("riesgos", [])), len(datos.get("biblioteca", []))))
    except Exception as ex:
        check("datos.json válido", False, str(ex))
        datos = {}

    # 4) datos.js
    try:
        js = open(os.path.join(ROOT, "datos.js"), encoding="utf-8").read()
        check("datos.js define window.DATOS", js.lstrip().startswith("window.DATOS"))
    except Exception as ex:
        check("datos.js legible", False, str(ex))

    # 5) referencias en index.html
    try:
        html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        refs = re.findall(r'(?:src|href)="([^"#][^"]*)"', html)
        rotas = []
        for r in refs:
            if r.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            ruta = r.split("?")[0].split("#")[0]
            if ruta and not os.path.exists(os.path.join(ROOT, ruta)):
                rotas.append(r)
        check("Referencias de index.html resueltas", not rotas, "rotas: %s" % rotas)
        ids = set(re.findall(r'id="([^"]+)"', html))
        anclas = set(re.findall(r'href="#([^"]+)"', html))
        check("Anclas de navegación válidas", all(a in ids for a in anclas),
              "sin sección: %s" % [a for a in anclas if a not in ids])
        # enlaces de secciones data-seccion
        secs = set(re.findall(r'data-seccion="([^"]+)"', html))
        falt_sec = [s for s in secs if ('id="%s"' % s) not in html]
        check("Secciones data-seccion existentes", not falt_sec, "faltantes: %s" % falt_sec)
    except Exception as ex:
        check("index.html analizado", False, str(ex))

    # 6) SVG bien formados
    for svg in ("wireframe-dc3.svg", "panel-kingair90.svg", "diagrama_arquitectura.svg"):
        try:
            t = open(os.path.join(ROOT, svg), encoding="utf-8").read()
            check("SVG %s legible" % svg, "<svg" in t and "</svg>" in t)
        except Exception as ex:
            check("SVG %s legible" % svg, False, str(ex))

    # 7) biblioteca: archivos disponibles existen
    bib = datos.get("biblioteca", [])
    falt_bib = [b["archivo"] for b in bib
                if b.get("estado") == "Disponible" and not os.path.exists(os.path.join(ROOT, b["archivo"]))]
    check("Archivos de biblioteca disponibles existen", not falt_bib, "faltantes: %s" % falt_bib)

    # 7b) prácticas (serie EEA-IFR): 10, ordenadas, con nombre/objetivo y PDF presente
    pracs = datos.get("practicas", [])
    nums = [p.get("numero") for p in pracs]
    check("Prácticas: exactamente 10", len(pracs) == 10, "cantidad: %d" % len(pracs))
    check("Prácticas: numeración 1..10 en orden", nums == list(range(1, 11)),
          "numeración: %s" % nums)
    sin_nombre = [p["codigo"] for p in pracs if not p.get("nombre")]
    check("Prácticas: nombre presente en todas", not sin_nombre, "sin nombre: %s" % sin_nombre)
    sin_obj = [p["codigo"] for p in pracs if not p.get("objetivo")]
    check("Prácticas: objetivo presente en todas", not sin_obj, "sin objetivo: %s" % sin_obj)
    falt_pdf = [p["archivo"] for p in pracs
                if not os.path.exists(os.path.join(ROOT, p.get("archivo", "")))]
    check("Prácticas: PDF de cada práctica presente", not falt_pdf, "faltantes: %s" % falt_pdf)

    # 8) duplicados de número de OI en equipos
    nums = {}
    for e in datos.get("equipos", []):
        for o in e.get("ois", []):
            nums[o.get("id")] = nums.get(o.get("id"), 0) + 1
    dups = [k for k, v in nums.items() if v > 1]
    check("Sin IDs duplicados de órdenes de trabajo", not dups, "duplicados: %s" % dups)

    # 8b) materiales: estructura, módulos M01..M05, ítems válidos y sin duplicados
    mats = datos.get("materiales", [])
    estados_ok = set(datos.get("estados_material", []))
    mods_ok = [m.get("id") for m in mats] == ["M01", "M02", "M03", "M04", "M05"]
    check("Materiales: exactamente M01..M05 en orden", mods_ok,
          "módulos: %s" % [m.get("id") for m in mats])
    ids_mat = {}
    items_invalidos = []
    for m in mats:
        for it in m.get("items", []):
            iid = it.get("id")
            ids_mat[iid] = ids_mat.get(iid, 0) + 1
            if not all(k in it for k in ("id", "nombre", "grupo", "cantidad", "unidad",
                                         "especificacion", "estado", "observacion")):
                items_invalidos.append(iid)
            if it.get("estado") not in estados_ok:
                items_invalidos.append("%s (estado)" % iid)
            if it.get("cantidad") is not None and not isinstance(it.get("cantidad"), (int, float)):
                items_invalidos.append("%s (cantidad)" % iid)
    dups_mat = [k for k, v in ids_mat.items() if v > 1]
    check("Materiales: ítems con campos completos y estado válido", not items_invalidos,
          "inválidos: %s" % items_invalidos[:10])
    check("Materiales: sin IDs duplicados de ítem", not dups_mat, "duplicados: %s" % dups_mat)

    # 8c) gobernanza: roles, perfil del líder, reglas de equipo y comunicación
    gob = datos.get("gobernanza", {})
    roles = gob.get("roles", [])
    ids_roles = [r.get("id") for r in roles]
    check("Gobernanza: exactamente 5 roles", ids_roles ==
          ["ceo", "ingenieria-operaciones", "supervisor-planeacion", "profesores-ipn", "lideres-equipo"],
          "roles: %s" % ids_roles)
    roles_inv = []
    for r in roles:
        if not all(k in r for k in ("id", "icono", "nombre", "cargo", "rol", "resumen",
                                    "responsabilidades", "limite", "entregables",
                                    "reporta_a", "comunica_con")):
            roles_inv.append(r.get("id"))
        if not isinstance(r.get("responsabilidades"), list) or not r.get("responsabilidades"):
            roles_inv.append(r.get("id") + " (responsabilidades)")
        if not r.get("limite"):
            roles_inv.append(r.get("id") + " (limite)")
    check("Gobernanza: roles con campos completos", not roles_inv, "inválidos: %s" % roles_inv)
    check("Gobernanza: 10 criterios del perfil del líder",
          len(gob.get("perfil_lider", {}).get("criterios", [])) == 10)
    check("Gobernanza: frase del perfil presente",
          bool(gob.get("perfil_lider", {}).get("frase")))
    check("Gobernanza: 7 reglas para conformar equipos",
          len(gob.get("reglas_equipos", {}).get("reglas", [])) == 7)
    check("Gobernanza: reglas de comunicación presentes",
          bool(gob.get("comunicacion", {}).get("reglas")))

    # 8d) gobernanza: equipos de trabajo (7, con campos completos)
    et = gob.get("equipos_trabajo", {})
    eqs = et.get("equipos", [])
    eq_ids = [e.get("id") for e in eqs]
    check("Equipos de trabajo: exactamente 7 en orden", eq_ids ==
          ["limpieza", "supervision-planeacion", "avionica-instrumentacion",
           "mecanica-mandos", "software-integracion", "electronica-sensorizacion",
           "simulacion-validacion"], "ids: %s" % eq_ids)
    eq_inv = []
    for e in eqs:
        for campo in ("id", "icono", "nombre", "responsabilidades", "actividades",
                      "entregables", "dependencias", "perfil_lider"):
            if campo not in e:
                eq_inv.append(e.get("id", "?") + " (" + campo + ")")
        for campo in ("responsabilidades", "actividades", "entregables", "dependencias", "perfil_lider"):
            if not isinstance(e.get(campo), list) or not e.get(campo):
                eq_inv.append(e.get("id", "?") + " (" + campo + " vacío)")
    check("Equipos de trabajo: campos completos", not eq_inv, "inválidos: %s" % eq_inv)
    check("Equipos de trabajo: relaciones de colaboración presentes",
          bool(et.get("relaciones")))

    # 9) PDF del Plan Maestro (firma y legibilidad)
    pm = os.path.join(ROOT, "Plan_Maestro_DC3_Eben_Ezer_Aviation.pdf")
    try:
        firma = open(pm, "rb").read(5)
        check("PDF Plan Maestro con firma válida", firma == b"%PDF-", "firma: %r" % firma)
    except Exception as ex:
        check("PDF Plan Maestro legible", False, str(ex))

    # 10) codificación UTF-8 sin BOM y sin mojibake
    exts = (".html", ".css", ".js", ".json", ".md", ".py", ".txt", ".svg")
    web = (".html", ".css", ".js", ".json", ".svg", ".md", ".txt")
    malos = []
    for f in os.listdir(ROOT):
        if not f.lower().endswith(exts):
            continue
        raw = open(os.path.join(ROOT, f), "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"):
            malos.append(f + " (BOM)")
            continue
        try:
            s = raw.decode("utf-8")
        except UnicodeDecodeError:
            malos.append(f + " (no UTF-8)")
            continue
        if f.lower().endswith(web) and ("Ã" in s or "Â" in s):
            malos.append(f + " (mojibake)")
    check("Codificación UTF-8 sin BOM ni mojibake", not malos, "afectados: %s" % malos)

    # 11) EDT: manuales y PDF de órdenes de trabajo
    equipos_d = datos.get("equipos", [])
    manuales_ok = all(e.get("manual") and os.path.exists(os.path.join(ROOT, e["manual"]))
                      for e in equipos_d)
    check("Manuales de equipo copiados (7)", manuales_ok)
    oi_nodos = []

    def _recolectar(n):
        if n.get("tipo") == "oi":
            oi_nodos.append(n)
        for h in n.get("hijos", []):
            _recolectar(h)
    if datos.get("edt"):
        _recolectar(datos["edt"])
    falt_oi = [n["archivo"] for n in oi_nodos
               if not os.path.exists(os.path.join(ROOT, n["archivo"]))]
    check("PDF de órdenes de trabajo existentes (%d nodos OI)" % len(oi_nodos),
          not falt_oi, "faltantes: %d" % len(falt_oi))

    # 12) descargas
    falt_dl = [a["archivo"] for g in datos.get("descargas", [])
               for a in g.get("archivos", [])
               if not os.path.exists(os.path.join(ROOT, a["archivo"]))]
    total_dl = sum(len(g.get("archivos", [])) for g in datos.get("descargas", []))
    check("Archivos de descarga existentes (%d)" % total_dl, not falt_dl,
          "faltantes: %s" % falt_dl)

    # 13) cronograma: categorías y asignación de tiempo de las OI
    crono = datos.get("cronograma", {})
    cats = crono.get("categorias", [])
    check("Cronograma con 5+ categorías de complejidad", len(cats) >= 5,
          "categorías: %d" % len(cats))
    sin_tiempo = [n["nombre"] for n in oi_nodos
                  if not (n.get("inicio") and n.get("fin") and n.get("complejidad"))]
    check("Todas las OI tienen fecha y complejidad asignada", not sin_tiempo,
          "sin asignación: %d" % len(sin_tiempo))

    # informe
    lineas = ["Informe de pruebas - Plataforma AATD DC3",
              "Fecha: %s" % datetime.datetime.now().isoformat(), "=" * 70, ""]
    ok_n = sum(1 for c, _ in resultados if c)
    err_n = sum(1 for c, _ in resultados if not c)
    for c, desc in resultados:
        lineas.append(("  [OK]   " if c else "  [ERROR] ") + desc)
    lineas.append("")
    lineas.append("RESULTADO: %d verificaciones, %d OK, %d errores -> %s" %
                  (len(resultados), ok_n, err_n, "CONFORME" if err_n == 0 else "CON NO CONFORMIDADES"))
    texto = "\n".join(lineas)
    with open(os.path.join(ROOT, "informe_pruebas.txt"), "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
    return 0 if err_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
