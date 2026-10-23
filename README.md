# Proyecto AATD DC3 — Centro Digital de Ingeniería Aeronáutica

Plataforma web estática (GitHub Pages) del simulador terrestre de vuelo por
instrumentos del **Douglas DC-3 (XB-DPC)**. Interfaz en español, temas
claro/oscuro, reloj UTC/Zulu y acceso a la documentación técnica de los siete
equipos.

> La aeronave es un **simulador terrestre**; no vuela. Cabina virtual de
> referencia: **King Air 90** en **X-Plane 12**. No se declara certificación
> FAA/AFAC.

## Funcionalidades
- Apertura animada (7 s) con el globo terrestre de fondo.
- Navegación principal (8 módulos) y navegación auxiliar por iconos (5 módulos).
- EDT interactiva, cronograma (Gantt) con inicio 2026-11-16, plan de
  comunicación, riesgos/incidentes, acuerdos, reporte de avances y cierre.
- Biblioteca técnica con los documentos reales del proyecto (vista/descarga).
- Diagramas (wireframe DC-3, panel King Air 90, arquitectura), glosario y
  detalle de los siete equipos.

## Construcción y validación (Python)
```powershell
python construir.py   # genera datos.json, SVG y copia recursos autorizados
python validar.py     # valida estructura, referencias, JSON, SVG y duplicados
```

## Publicación en GitHub Pages (manual)
```powershell
git init
git remote add origin https://github.com/hanielfierros/dc3
git add .
git commit -m "Plataforma AATD DC3: refactor del centro digital"
git push -u origin main
```
En GitHub: `Settings → Pages → Source: Deploy from a branch → Branch: main / root`.
El archivo `.nojekyll` ya está incluido.

## Notas
- La información no confirmada se marca `Pendiente de verificación`,
  `Pendiente de estimación` o `Propuesto`.
- No se incluyen claves, datos personales ni archivos confidenciales no autorizados.
