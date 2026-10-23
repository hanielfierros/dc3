# AGENTS.md — Reglas de trabajo del Proyecto AATD DC3

Reglas de larga duración para agentes que trabajen en la plataforma.

## Identidad
- Proyecto AATD DC3: simulador terrestre del fuselaje Douglas DC-3 (XB-DPC); no volverá a volar.
- Cabina virtual: King Air 90 en X-Plane 12. Sin certificación FAA/AFAC.
- Empresa: Eben Ezer Aviation · Departamento de Ingeniería Aeronáutica Aplicada.
- Director/patrocinador: Haniel Fierros (CEO). Supervisión: Roxana Mendez.
- Eslogan: "A la altura de Nuestra Identidad. Ingeniería Aeronáutica."

## Estructura y despliegue
- Todos los archivos publicables en la raíz de `Plataforma DC3`, sin subcarpetas.
- Sitio estático (HTML/CSS/JS/SVG/JSON/PNG) compatible con GitHub Pages; sin backend.
- Rutas relativas. Backups fuera del directorio de despliegue (no publicar backups).

## Generación
- Python es el motor de generación: `construir.py` (datos, SVG, copia de recursos) y `validar.py` (verificación).
- Datos estructurados en `datos.json` (también `datos.js` para el navegador). JS solo para interacción.
- No crear botones inertes ni enlaces falsos; todo control debe tener función real.

## Veracidad
- No inventar progreso, presupuesto, plazos, personal, riesgos, conexiones, pruebas, aprobaciones ni certificaciones.
- Lo no confirmado se marca "Pendiente de verificación", "Pendiente de estimación" o "Propuesto".
- Los documentos se exponen solo si existen en la fuente (`Biblioteca Técnica`, equipos).

## Calidad
- Auditar antes de modificar. Preferir correcciones puntuales a reescrituras completas.
- Ejecutar `python construir.py` y `python validar.py` tras cada cambio.
- Sin git local (aún no inicializado): documentar comandos en README; no hacer push sin autorización.
- Pruebas de navegador automatizadas (Playwright) no disponibles en el entorno: indicar la limitación.
