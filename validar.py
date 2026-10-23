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

    # 1) estructura plana
    subdirs = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))]
    check("Estructura plana (sin subcarpetas)", not subdirs, "subcarpetas: %s" % subdirs)

    # 2) archivos requeridos
    falt = [f for f in REQUERIDOS if not os.path.exists(os.path.join(ROOT, f))]
    check("Archivos requeridos", not falt, "faltantes: %s" % falt)

    # 3) datos.json
    try:
        datos = json.load(open(os.path.join(ROOT, "datos.json"), encoding="utf-8"))
        claves = ["proyecto", "responsables", "equipos", "edt", "cronograma",
                  "comunicacion", "fases", "riesgos", "incidentes", "acuerdos",
                  "avances", "biblioteca", "referencias_oficiales", "glosario"]
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

    # 8) duplicados de número de OI en equipos
    nums = {}
    for e in datos.get("equipos", []):
        for o in e.get("ois", []):
            nums[o.get("id")] = nums.get(o.get("id"), 0) + 1
    dups = [k for k, v in nums.items() if v > 1]
    check("Sin IDs duplicados de órdenes de trabajo", not dups, "duplicados: %s" % dups)

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
