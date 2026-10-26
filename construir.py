# -*- coding: utf-8 -*-
"""
construir.py — Motor de construcción del Proyecto AATD DC3 (GitHub Pages).

Genera desde los datos reales del proyecto:
  - datos.json / datos.js  (responsables, equipos, EDT, cronograma, comunicación,
                            riesgos/incidentes, biblioteca, glosario)
  - SVG (wireframe DC-3, panel King Air 90, arquitectura)
  - Copia los PDF autorizados de la Biblioteca Técnica y earth.jpg a la raíz
  - README.md, .nojekyll, .gitignore, dependencias.txt, informe_archivos.txt

No modifica archivos de otros equipos. Todo se escribe en la raíz de Plataforma DC3.
"""
import os
import re
import json
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.dirname(ROOT)  # Simulador DC3
DPC = os.path.join(PROYECTO, "Proyecto DPC DC3")
BT = os.path.join(PROYECTO, "Biblioteca Técnica")
FIG = os.path.join(PROYECTO, "Figuras y diagramas")
PE = os.path.join(PROYECTO, "Programas de Estudio")

PEND = "Pendiente de verificación"
PEND_EST = "Pendiente de estimación"
PROPUESTO = "Propuesto"

LIMITE_COPIA_MB = 100  # Límite real por archivo de GitHub Pages (100 MB); 50–100 MB solo genera aviso

# ---------------------------------------------------------------------------
# Datos estáticos
# ---------------------------------------------------------------------------
RESPONSABLES = [
    {"nombre": "Haniel Fierros", "rol": "CEO Eben Ezer Aviation", "cargo": "Director de Proyecto · Patrocinador principal"},
    {"nombre": "Roxana Mendez", "rol": "Supervisor", "cargo": "Supervisa a los equipos y el cumplimiento de objetivos"},
]

EQUIPOS = [
    {"id": "T1", "numero": 1, "nombre": "Limpieza", "carpeta": "Limpieza",
     "rol": "Preparación y saneamiento de la cabina",
     "objetivo": "Preparar la cabina y el fuselaje mediante diagnóstico, desmontaje controlado, limpieza profunda y protección temporal.",
     "responsabilidades": ["Diagnóstico de riesgos biológicos/químicos", "Desmontaje controlado de cabina", "Limpieza profunda y sanitización", "Protección temporal y transferencia"]},
    {"id": "T2", "numero": 2, "nombre": "Supervisión y Planeación", "carpeta": "Supervision_y_Planeacion",
     "rol": "Planeación, coordinación y control del proyecto",
     "objetivo": "Planear, coordinar y controlar el avance del proyecto y sus puertas de enlace.",
     "responsabilidades": ["Plan maestro y cronograma", "RACI y entregables", "Gestión de riesgos y presupuesto", "Coordinación diaria y puertas de enlace"]},
    {"id": "T3", "numero": 3, "nombre": "Avionica", "carpeta": "Avionica",
     "rol": "Electrónica, control e integración con X-Plane 12",
     "objetivo": "Implementar controles, sensores, indicadores e interfaces electrónicas entre la cabina y X-Plane 12.",
     "responsabilidades": ["Infraestructura eléctrica", "Módulos de control (14)", "Integración X-Plane (DataRefs/Commands)", "Compatibilidad de software"]},
    {"id": "T4", "numero": 4, "nombre": "Mecánica", "carpeta": "Mecanica",
     "rol": "Estructura, soportes y adaptación de mandos",
     "objetivo": "Proveer la base física de instalación: soportes, paneles, estructuras y adaptación de mandos.",
     "responsabilidades": ["Levantamiento y medición", "Fabricación de estructuras", "Adaptación de mandos e instrumentos", "Integración y aceptación conjunta"]},
    {"id": "T5", "numero": 5, "nombre": "Software", "carpeta": "Software",
     "rol": "Sistema, simulación, aplicaciones y firmware",
     "objetivo": "Instalar, configurar e integrar el sistema operativo, X-Plane 12, aplicaciones y firmware.",
     "responsabilidades": ["Sistema operativo y entorno", "Simulación y aplicaciones", "Firmware y control", "Mantenimiento informático"]},
    {"id": "T6", "numero": 6, "nombre": "Lógico", "carpeta": "Logico",
     "rol": "Control documental y trazabilidad",
     "objetivo": "Administrar el control documental, el archivo, la trazabilidad y la auditoría de documentos.",
     "responsabilidades": ["Control documental", "Archivo físico y digital", "Auditorías internas", "Expediente técnico final"]},
    {"id": "T7", "numero": 7, "nombre": "Vuelo", "carpeta": "Vuelo",
     "rol": "Validación y pruebas del simulador",
     "objetivo": "Validar el desempeño técnico del simulador mediante pruebas estáticas, VFR/IFR y rutas completas.",
     "responsabilidades": ["Pruebas estáticas y de mandos", "Motor, instrumentos y aviónica", "Vuelo VFR/IFR simulado", "Rutas IFR SLW-MTY y TLC-MEX"]},
]

FASES = [
    {"id": "A", "nombre": "Inspección estática y arranque", "semana": 1},
    {"id": "B", "nombre": "Mandos, sensores y entradas físicas", "semana": 1},
    {"id": "C", "nombre": "Motor, instrumentos y aviónica", "semana": 2},
    {"id": "D", "nombre": "Rodaje simulado y vuelo básico", "semana": 3},
    {"id": "E", "nombre": "IFR — entrenamiento y validación", "semana": 4},
    {"id": "F", "nombre": "Ruta IFR SLW–MTY", "semana": 5},
    {"id": "G", "nombre": "Ruta IFR TLC–MEX", "semana": 6},
    {"id": "H", "nombre": "Integración y regresión", "semana": 7},
]

COMUNICACION = [
    {"frecuencia": "Diaria", "medio": "Reunión breve / Zoom", "participantes": "Líderes de equipo",
     "temas": "Avance del día anterior, plan del día, bloqueos, responsables", "minuta": "Acta de reunión diaria"},
    {"frecuencia": "Semanal", "medio": "Reunión de seguimiento", "participantes": "Supervisor y líderes de equipo",
     "temas": "Avance vs plan, riesgos, decisiones, próximos pasos", "minuta": "Minuta semanal"},
    {"frecuencia": "Mensual", "medio": "Revisión de proyecto", "participantes": "CEO, supervisor y líderes",
     "temas": "Hitos, presupuesto, calidad, riesgos estratégicos", "minuta": "Informe mensual"},
    {"frecuencia": "Cierre de proyecto", "medio": "Reunión presencial / Zoom", "participantes": "CEO, supervisor y equipos",
     "temas": "Aceptación, entrega, lecciones aprendidas, cierre", "minuta": "Acta de cierre"},
]

GLOSARIO = [
    ("AATD", "Advanced Aviation Training Device; término descriptivo del dispositivo de entrenamiento."),
    ("DataRef", "Variable interna de X-Plane que expone estado o parámetro (lectura/escritura según aplique)."),
    ("Command", "Comando de X-Plane que ejecuta una acción."),
    ("Teensy", "Microcontrolador usado para adquisición de entradas y control de salidas."),
    ("GTN 750", "Unidad de navegación táctil (referencia Garmin) mostrada en el monitor central."),
    ("IFR / VFR", "Reglas de vuelo por instrumentos / visual; en este proyecto solo simulación."),
    ("OI / OT", "Orden de Ingeniería / Orden de Trabajo: documento ejecutable por actividad."),
    ("BOM", "Lista de materiales."),
    ("EDT / WBS", "Estructura de desglose del trabajo (Work Breakdown Structure)."),
    ("As-Built", "Documentación de la configuración real construida."),
    ("FAT/SAT", "Pruebas de aceptación en fábrica / en sitio (internas, sin certificación externa)."),
    ("SID / STAR", "Salida / llegada normalizada por instrumentos; solo con datos verificados (AIP)."),
]

PEND_EVAL = "Pendiente de evaluación"

# Color fijo de los 9 responsables (el color identifica al responsable, NO a la severidad).
# Se evitan verde/amarillo/rojo/azul porque están reservados para la matriz de severidad.
RESPONSABLES_COLOR = [
    {"nombre": "Haniel Fierros", "color": "#7C3AED", "descripcion": "CEO · Director de proyecto"},
    {"nombre": "Roxana Mendez", "color": "#EC4899", "descripcion": "Supervisora principal"},
    {"nombre": "Limpieza", "color": "#F97316", "descripcion": "Equipo 1"},
    {"nombre": "Supervisión y Planeación", "color": "#64748B", "descripcion": "Equipo 2"},
    {"nombre": "Avionica", "color": "#06B6D4", "descripcion": "Equipo 3"},
    {"nombre": "Mecánica", "color": "#A16207", "descripcion": "Equipo 4"},
    {"nombre": "Software", "color": "#E879F9", "descripcion": "Equipo 5"},
    {"nombre": "Lógico", "color": "#14B8A6", "descripcion": "Equipo 6"},
    {"nombre": "Vuelo", "color": "#A3A3A3", "descripcion": "Equipo 7"},
]

_NOMBRES_RESP = {r["nombre"] for r in RESPONSABLES_COLOR}


def _riesgo(rid, categoria, nombre, descripcion, responsables, causas, consecuencias,
            preventivas, que_hacer, inspeccion, referencias=None, disparadores=None):
    """Registro unificado de riesgo potencial (sin inventar prob/impacto/estado)."""
    resp = [r for r in responsables if r in _NOMBRES_RESP]
    if not resp:
        resp = ["Aplicabilidad pendiente de validación"]
    return {
        "id": rid,
        "tipo": "Riesgo potencial",
        "categoria": categoria,
        "nombre": nombre,
        "descripcion": descripcion,
        "causas": causas,
        "disparadores": disparadores or [],
        "consecuencias": consecuencias,
        "responsables": resp,
        "prob": PEND_EVAL,
        "impacto": PEND_EVAL,
        "nivel": PEND_EVAL,
        "estado": "Abierto",
        "medidas_preventivas": preventivas,
        "que_hacer": que_hacer,
        "inspeccion": inspeccion,
        "referencias": referencias or [],
        "equipo": None,
    }


RIESGOS_AMPLIADOS = [
    # ===== A. Eléctrico y electrónico =====
    _riesgo("R-EL-01", "Eléctrico y electrónico", "Cortocircuito en cableado o tarjetas",
            "Contacto accidental entre conductores con distinto potencial que puede dañar componentes y generar calor excesivo.",
            ["Avionica", "Software"],
            ["Aislamiento dañado o retirado de forma incorrecta", "Hilos sueltos que se tocan entre sí", "Restos de soldadura o virutas metálicas sobre la placa"],
            ["Daño de CPU/Arduino Mega, fuentes o actuadores", "Calentamiento anómalo", "Interrupción del sistema durante una prueba"],
            ["Verificar el aislamiento y la separación de conductores antes de energizar", "Retirar residuos metálicos y revisar las soldaduras", "Usar protecciones (fusibles/breakers) adecuadas"],
            ["Desenergizar de inmediato", "Inspeccionar el punto de contacto y sustituir el conductor o componente dañado", "Reparar y repetir la prueba sin carga"],
            ["Continuidad y aislamiento entre pistas", "Ausencia de restos metálicos", "Valor de protección conforme al diseño"],
            ["Manual del equipo de Avionica"],
            ["Calor excesivo, olor a quemado o chispa visible", "Disparo de la protección"]),
    _riesgo("R-EL-02", "Eléctrico y electrónico", "Sobrecorriente o sobrecarga",
            "Consumo de corriente por encima de la capacidad de la fuente, los conductores o los módulos.",
            ["Avionica"],
            ["Demasiadas cargas conectadas a una misma salida", "Dimensionamiento incorrecto de la fuente", "Actuador con carga mecánica excesiva"],
            ["Sobrecalentamiento y daño de la fuente", "Caída de tensión que apaga módulos", "Daño progresivo de conductores"],
            ["Dimensionar la fuente con margen y balancear las cargas", "Proteger cada ramal con su fusible/breaker", "No conectar más cargas de las previstas"],
            ["Desconectar la carga", "Medir la corriente real y compararla con el diseño", "Corregir el dimensionamiento antes de volver a energizar"],
            ["Corriente por ramal dentro de límites", "Temperatura de fuente y cables normal", "Protecciones sin disparos repetidos"],
            ["Manual del equipo de Avionica"],
            ["Fusible o breaker que se dispara", "Cables o fuente calientes al tacto"]),
    _riesgo("R-EL-03", "Eléctrico y electrónico", "Inversión de polaridad",
            "Conexión de positivo y negativo invertidos en la alimentación de un módulo o placa.",
            ["Avionica"],
            ["Código de colores no respetado", "Conector sin llave que permite invertirse", "Prisa durante el armado"],
            ["Daño inmediato de semiconductores y reguladores", "Funcionamiento errático", "Destrucción de la placa"],
            ["Marcar claramente la polaridad y usar conectores con llave", "Verificar con multímetro antes de conectar", "Revisar el diagrama de conexión antes de energizar"],
            ["Desconectar la alimentación", "Verificar y corregir la polaridad", "Probar el módulo de forma aislada antes de reintegrarlo"],
            ["Polaridad correcta en cada conector", "Código de colores respetado", "Módulo responde tras la corrección"],
            ["Manual del equipo de Avionica"],
            ["No enciende o se reinicia", "Componente caliente al energizar"]),
    _riesgo("R-EL-04", "Eléctrico y electrónico", "Sobretensión o subtensión",
            "Tensión de alimentación fuera del rango admisible para los módulos y sensores.",
            ["Avionica"],
            ["Fuente mal regulada", "Variación de la red eléctrica", "Regulador dañado o mal configurado"],
            ["Daño de microcontroladores y sensores", "Lecturas erróneas de los instrumentos", "Reinicios aleatorios"],
            ["Medir la tensión de salida antes de conectar la carga", "Usar fuentes reguladas y estables", "Ajustar los reguladores al valor de diseño"],
            ["Desenergizar y verificar la fuente", "Comparar la tensión medida con el rango admisible", "Sustituir la fuente o el regulador si está fuera de rango"],
            ["Tensión dentro del rango en vacío y con carga", "Ausencia de variaciones bruscas", "Reguladores sin calentamiento anómalo"],
            ["Manual del equipo de Avionica"],
            ["Lecturas fuera de lo esperado", "Reinicios o apagados intermitentes"]),
    _riesgo("R-EL-05", "Eléctrico y electrónico", "Cableado incorrecto o conexiones cruzadas",
            "Conexión de señales o alimentación a terminales equivocados del controlador.",
            ["Avionica", "Software"],
            ["Diagrama desactualizado o mal interpretado", "Etiquetado insuficiente", "Reconexión apresurada tras un cambio"],
            ["Señal errónea hacia X-Plane 12", "Entradas/salidas sobrecargadas", "Comportamiento impredecible de los mandos"],
            ["Etiquetar cada conductor y respetar el diagrama", "Verificar continuidad punto a punto antes de energizar", "Trabajar con el esquema vigente aprobado"],
            ["Desenergizar", "Comparar cada conexión con el diagrama", "Corregir el cableado y repetir la verificación"],
            ["Continuidad punto a punto conforme al diagrama", "Sin cortos entre señales adyacentes", "Respuesta correcta en la prueba funcional"],
            ["Manual del equipo de Avionica"],
            ["Mandos que no responden o responden invertidos", "Error de lectura de entradas"]),
    _riesgo("R-EL-06", "Eléctrico y electrónico", "Daño del aislamiento de conductores",
            "Aislamiento cortado, quemado o desgastado que deja el conductor expuesto.",
            ["Avionica", "Mecánica"],
            ["Paso de cables por bordes filosos", "Calor cercano a los conductores", "Desgaste por fricción o manipulación"],
            ["Contacto con masa y cortocircuito", "Descarga o falla intermitente", "Deterioro progresivo del arnés"],
            ["Proteger los pasos de cable con grommets o canaleta", "Alejar los conductores de fuentes de calor", "Revisar el arnés tras cada instalación"],
            ["Desenergizar", "Localizar y aislar el tramo dañado", "Reparar o sustituir el conductor afectado"],
            ["Aislamiento íntegro en todo el recorrido", "Sin conductor expuesto", "Pasos de cable protegidos"],
            ["Manual del equipo de Avionica"],
            ["Inspección visual con conductor al descubierto", "Falla intermitente al mover el arnés"]),
    _riesgo("R-EL-07", "Eléctrico y electrónico", "Terminales sueltos o conexiones flojas",
            "Conexiones que no aseguran el contacto eléctrico estable, con resistencia variable.",
            ["Avionica"],
            ["Tornillería sin apretar", "Terminal sin crimpar correctamente", "Vibración del entorno"],
            ["Caídas de señal intermitentes", "Calentamiento en el punto de conexión", "Falsos contactos difíciles de reproducir"],
            ["Apretar la tornillería al par adecuado", "Crimpar y verificar cada terminal", "Asegurar los conectores contra vibración"],
            ["Desenergizar", "Apretar o recrimpar el terminal", "Verificar continuidad con el cable en reposo y en movimiento"],
            ["Terminales firmes y sin juego", "Continuidad estable", "Sin calentamiento en conexiones"],
            ["Manual del equipo de Avionica"],
            ["Señal que se pierde al tocar o mover el cable", "Terminal caliente"]),
    _riesgo("R-EL-08", "Eléctrico y electrónico", "Capacidad de fuente insuficiente",
            "La fuente no entrega la potencia total que demandan los módulos y actuadores.",
            ["Avionica"],
            ["Subestimar el consumo total", "Añadir cargas sin recalcular", "Fuente degradada"],
            ["Apagados al activar varios actuadores", "Servos con respuesta débil", "Reinicios del controlador"],
            ["Calcular el consumo total con margen", "Medir la corriente real en operación", "Dimensionar la fuente por encima del consumo pico"],
            ["Desconectar cargas", "Medir el consumo y compararlo con la capacidad", "Sustituir o reforzar la fuente si es insuficiente"],
            ["Consumo pico dentro de la capacidad de la fuente", "Tensión estable con carga plena", "Fuente sin sobrecalentamiento"],
            ["Manual del equipo de Avionica"],
            ["Tensión que cae al activar cargas", "Reinicios bajo demanda"]),
    _riesgo("R-EL-09", "Eléctrico y electrónico", "Protección de distribución inadecuada",
            "Ausencia o mala selección de fusibles/breakers por ramal de distribución.",
            ["Avionica"],
            ["No colocar protección por ramal", "Valor de protección mayor al del conductor", "Protección puenteada"],
            ["Daño extenso ante una falla", "Riesgo de incendio del cableado", "Imposibilidad de aislar una falla puntual"],
            ["Proteger cada ramal con el valor correcto", "No puentear protecciones", "Documentar el valor de cada protección"],
            ["Desenergizar", "Instalar o corregir la protección del ramal", "Verificar que la protección abre antes de dañar el conductor"],
            ["Cada ramal con su protección", "Valores conforme al diseño", "Protecciones operativas y accesibles"],
            ["Manual del equipo de Avionica"],
            ["Protección ausente o puenteada", "Conductor con signos de calentamiento"]),
    _riesgo("R-EL-10", "Eléctrico y electrónico", "Problemas de puesta a tierra",
            "Tierra inexistente, deficiente o con lazos que generan ruido y diferencias de potencial.",
            ["Avionica"],
            ["Punto de tierra mal elegido", "Tierras múltiples con distinta referencia", "Conexión de tierra floja o corroída"],
            ["Ruido en señales analógicas", "Interferencia en la comunicación", "Riesgo de descarga en el chasis"],
            ["Definir un único punto de referencia de tierra", "Apretar y limpiar las conexiones de tierra", "Separar tierra de potencia y de señal según el diseño"],
            ["Desenergizar", "Revisar y consolidar las conexiones de tierra", "Medir continuidad entre chasis y punto de tierra"],
            ["Continuidad de tierra correcta", "Sin lazos de tierra no deseados", "Señales sin ruido evidente"],
            ["Manual del equipo de Avionica"],
            ["Ruido o zumbido en instrumentos", "Diferencias de potencial entre puntos metálicos"]),
    _riesgo("R-EL-11", "Eléctrico y electrónico", "Interferencia electromagnética (EMI)",
            "Ruido electromagnético que perturba señales, comunicaciones o displays.",
            ["Avionica", "Software"],
            ["Cables de señal cerca de líneas de potencia", "Blindaje ausente o mal conectado", "Actuadores con conmutación ruidosa"],
            ["Lecturas de sensores erráticas", "Comunicación USB/serial con errores", "Parpadeo o falla de displays"],
            ["Trenzar y blindar los cables de señal", "Separar potencia y señal", "Conectar el blindaje correctamente a tierra"],
            ["Identificar la fuente de ruido", "Reordenar o blindar el cableado", "Verificar que la comunicación se estabiliza"],
            ["Señales estables con los actuadores operando", "Comunicación sin errores", "Blindajes conectados a tierra"],
            ["Manual del equipo de Avionica"],
            ["Valores de sensor que saltan al activar motores", "Errores de comunicación"]),
    _riesgo("R-EL-12", "Eléctrico y electrónico", "Descarga electrostática (ESD)",
            "Descarga estática que daña componentes electrónicos sensibles durante la manipulación.",
            ["Avionica", "Software"],
            ["Manipular tarjetas sin protección ESD", "Ambiente seco con acumulación de carga", "Ausencia de pulsera o superficie antiestática"],
            ["Daño latente o inmediato de microcontroladores", "Fallas intermitentes difíciles de diagnosticar", "Reducción de vida útil del componente"],
            ["Usar pulsera y superficie antiestática", "Manipular las tarjetas por los bordes", "Almacenar en bolsas antiestáticas"],
            ["Detener la manipulación", "Sustituir el componente sospechoso", "Documentar la falla y reforzar el protocolo ESD"],
            ["Zona de trabajo con protección ESD", "Personal con pulsera conectada", "Componentes sin daño tras la manipulación"],
            ["Manual del equipo de Avionica"],
            ["Falla que aparece tras manipular la tarjeta", "Ambiente seco y sin protección ESD"]),
    _riesgo("R-EL-13", "Eléctrico y electrónico", "Daño de componentes de control y actuadores",
            "CPU, Arduino Mega, microcontrolador, LED, botones, switches, sensores, potenciómetros, servos u otros actuadores dañados.",
            ["Avionica", "Software", "Mecánica"],
            ["Sobretensión o polaridad invertida", "Carga mecánica o térmica excesiva", "Manipulación inadecuada o ESD"],
            ["Pérdida de función de un mando o indicador", "Lecturas incorrectas", "Retrabajo y retraso del cronograma"],
            ["Respetar rangos de tensión y corriente", "Montar los actuadores sin forzar su recorrido", "Proteger los componentes contra ESD y sobretensión"],
            ["Aislar el componente dañado", "Verificar la causa antes de sustituir", "Reemplazar y validar la función en banco"],
            ["Componente dentro de sus especificaciones", "Respuesta correcta tras la sustitución", "Sin recurrencia de la causa"],
            ["Manual del equipo de Avionica"],
            ["Componente sin respuesta", "Olor a quemado o carcasa deformada"]),
    _riesgo("R-EL-14", "Eléctrico y electrónico", "Daño de interfaces y saturación de entradas/salidas",
            "Puertos USB/serial dañados, conflictos de señal, sobrecarga de E/S, bloqueo de servos o calentamiento anómalo.",
            ["Avionica", "Software"],
            ["Conectar/desconectar con energía", "Sobrepasar la corriente de salida del pin", "Servo con tope mecánico que lo mantiene en esfuerzo"],
            ["Pérdida de comunicación con X-Plane 12", "Salida de control sin respuesta", "Sobrecalentamiento y daño del controlador"],
            ["Respetar la corriente máxima por pin", "Limitar el recorrido de los servos en software y mecánica", "Conectar interfaces con el sistema apagado"],
            ["Desenergizar", "Identificar la salida o puerto afectado", "Corregir la carga o el límite de recorrido y validar"],
            ["E/S dentro de límites de corriente", "Servos sin esfuerzo en los topes", "Comunicación estable"],
            ["Manual del equipo de Avionica", "Manual del equipo de Software"],
            ["Servo que zumba o se calienta en el tope", "Puerto USB que deja de responder"]),
    _riesgo("R-EL-15", "Eléctrico y electrónico", "Riesgos en depuración y primera energización",
            "Peligros durante la medición con energía, la revisión previa, el aislamiento y la primera puesta en marcha.",
            ["Avionica", "Roxana Mendez"],
            ["Medir con el equipo energizado sin procedimiento", "No aislar el circuito antes de intervenir", "Primera energización sin revisión previa"],
            ["Descarga eléctrica al operador", "Daño del equipo por falla no detectada", "Falsa sensación de conformidad"],
            ["Aplicar LOTO o aislamiento antes de intervenir", "Revisar voltaje, polaridad, cableado y protecciones antes de energizar", "Hacer la primera energización por pasos y con carga mínima"],
            ["Desenergizar y aislar de inmediato", "Atender cualquier lesión y reportar", "Investigar la causa antes de volver a energizar"],
            ["Circuito confirmado sin tensión antes de intervenir", "Lista de revisión previa completada", "Primera energización sin incidentes"],
            ["Manual del equipo de Avionica"],
            ["Intervención sin verificar ausencia de tensión", "Primera energización sin revisión documentada"]),

    # ===== B. Estructura y mecánica =====
    _riesgo("R-MC-01", "Estructura y mecánica", "Error de medición dimensional de cabina",
            "Dimensiones de la cabina tomadas incorrectamente, que no corresponden a la estructura real.",
            ["Mecánica", "Supervisión y Planeación"],
            ["Instrumento de medición mal calibrado", "Puntos de referencia mal elegidos", "Lectura o registro erróneo"],
            ["Soportes y paneles que no ajustan", "Retrabajo de piezas fabricadas", "Retraso y costo adicional"],
            ["Calibrar los instrumentos antes de medir", "Definir y documentar los puntos de referencia", "Verificar cada medida por duplicado"],
            ["Detener la fabricación afectada", "Re-medir y corregir el plano", "Ajustar o rehacer la pieza según la medida verificada"],
            ["Medidas verificadas contra el plano", "Instrumentos calibrados", "Pieza que ajusta en el montaje de prueba"],
            ["Manual del equipo de Mecánica"],
            ["Pieza que no ajusta al montar", "Discrepancia entre medida y plano"]),
    _riesgo("R-MC-02", "Estructura y mecánica", "Inconsistencia de referencias (datum)",
            "Distintos equipos usan planos o referencias de origen no coincidentes.",
            ["Mecánica", "Supervisión y Planeación"],
            ["Planos con distinto origen de coordenadas", "Actualización no comunicada", "Mezcla de versiones de dibujo"],
            ["Piezas incompatibles entre equipos", "Errores de alineación acumulados", "Rechazo en la integración"],
            ["Fijar un único sistema de referencia", "Versionar y comunicar los planos vigentes", "Revisar la referencia antes de cada fabricación"],
            ["Detener el trabajo en conflicto", "Confrontar versiones y definir el plano vigente", "Repetir el trabajo conforme a la referencia única"],
            ["Todos los equipos usan la misma referencia", "Planos con versión y fecha vigente", "Sin desalineación en la integración"],
            ["Manual del equipo de Mecánica"],
            ["Dos equipos con medidas que no coinciden", "Plano sin versión o fecha"]),
    _riesgo("R-MC-03", "Estructura y mecánica", "Discrepancia entre plano y estructura real",
            "La geometría real del fuselaje difiere del plano o modelo usado para fabricar.",
            ["Mecánica", "Supervisión y Planeación"],
            ["Plano histórico o genérico del DC-3", "Deformación previa de la estructura", "Falta de levantamiento real"],
            ["Soportes que no asientan", "Modificaciones forzadas en sitio", "Daño por ajuste indebido"],
            ["Levantar la estructura real antes de diseñar", "Validar el plano contra la cabina", "Prever margen de ajuste en los soportes"],
            ["Detener la instalación", "Levantar y comparar plano contra estructura", "Ajustar el diseño antes de fabricar de nuevo"],
            ["Plano validado contra la estructura real", "Soportes que asientan sin forzar", "Sin modificaciones improvisadas"],
            ["Manual del equipo de Mecánica"],
            ["Soporte que no asienta o requiere forzarse", "Diferencia visible entre plano y cabina"]),
    _riesgo("R-MC-04", "Estructura y mecánica", "Interferencia con mandos y piezas móviles",
            "Los nuevos componentes obstruyen el recorrido de mandos, pedales, palancas, cables o partes móviles.",
            ["Mecánica", "Avionica", "Vuelo"],
            ["No considerar el movimiento de los mandos", "Instalar componentes en el recorrido", "Falta de análisis de interferencia"],
            ["Mandos con recorrido limitado", "Desgaste o rotura de cables y piezas", "Comportamiento de vuelo simulado incorrecto"],
            ["Analizar el movimiento completo de cada mando", "Respetar el recorrido y dejar holgura", "Verificar con el mando en todo su rango"],
            ["Detener el uso del mando afectado", "Reubicar el componente que interfiere", "Verificar el recorrido completo antes de usar"],
            ["Recorrido completo sin contacto", "Holgura suficiente en todo el rango", "Sin desgaste en cables y piezas"],
            ["Manual del equipo de Mecánica"],
            ["Mando que roza o no llega al tope", "Desgaste visible en cables"]),
    _riesgo("R-MC-05", "Estructura y mecánica", "Virutas, bordes filosos, polvo y daño local",
            "Residuos y bordes generados por taladrado, corte o esmerilado que dañan componentes o personas.",
            ["Mecánica", "Limpieza"],
            ["Taladrar o cortar cerca de equipos sin protegerlos", "No desbarbar los bordes", "No aspirar los residuos"],
            ["Cortes en el personal", "Virutas que caen en equipos electrónicos", "Daño local de la estructura"],
            ["Proteger equipos y cableado cercano", "Desbarbar los bordes tras mecanizar", "Aspirar y limpiar la zona al terminar"],
            ["Detener el trabajo", "Atender cualquier corte y reportar", "Limpiar y desbarbar antes de continuar"],
            ["Sin virutas en equipos ni cableado", "Bordes sin filos", "Zona limpia tras el trabajo"],
            ["Manual del equipo de Mecánica"],
            ["Virutas cerca de placas o conectores", "Borde cortante sin desbarbar"]),
    _riesgo("R-MC-06", "Estructura y mecánica", "Resistencia insuficiente de soportes y montajes",
            "Soportes, pantallas, instrumentos, asientos o consolas con resistencia o rigidez insuficiente.",
            ["Mecánica"],
            ["Material o espesor inadecuado", "Fijación subdimensionada", "Cargas mal estimadas"],
            ["Deformación o falla del soporte", "Caída del componente montado", "Riesgo para el usuario"],
            ["Dimensionar el soporte con margen", "Usar materiales y fijaciones adecuados", "Probar la carga antes del uso regular"],
            ["Retirar la carga del soporte", "Reforzar o rediseñar la pieza", "Validar con la carga prevista"],
            ["Soporte rígido y estable", "Fijaciones completas y apretadas", "Sin deformación tras la prueba"],
            ["Manual del equipo de Mecánica"],
            ["Soporte que flexiona o cruje", "Fijación incompleta o suelta"]),
    _riesgo("R-MC-07", "Estructura y mecánica", "Falla de fijación, vibración o desalineación",
            "Piezas que se aflojan, vibran o quedan desalineadas durante el montaje.",
            ["Mecánica"],
            ["Tornillería sin fijador o sin apretar", "Vibración del entorno", "Montaje sin plantilla de alineación"],
            ["Aflojamiento progresivo", "Ruido y vibración", "Desalineación que afecta la función"],
            ["Apretar y asegurar la tornillería", "Usar fijadores de rosca cuando aplique", "Montar con plantilla y verificar alineación"],
            ["Detener el uso", "Reapretar y verificar alineación", "Revisar si hubo daño por la vibración"],
            ["Tornillería firme", "Sin vibración ni juego", "Alineación dentro de tolerancia"],
            ["Manual del equipo de Mecánica"],
            ["Tornillos que se aflojan tras el uso", "Vibración o juego perceptible"]),
    _riesgo("R-MC-08", "Estructura y mecánica", "Ruteo de mazos de cable inadecuado",
            "Mazos de cables mal tendidos, pellizcados, desgastados, doblados en exceso o que obstruyen la operación.",
            ["Mecánica", "Avionica"],
            ["Cable pasado por bordes o entre paneles", "Radio de doblez excesivo", "Cable que cruza zonas de movimiento"],
            ["Cortocircuito por aislamiento dañado", "Señal intermitente", "Obstrucción de mandos"],
            ["Tender los cables por canaletas o pasos protegidos", "Respetar radios de doblez", "Alejar los cables de zonas móviles"],
            ["Desenergizar", "Reubicar el mazo por la ruta correcta", "Sustituir el tramo dañado"],
            ["Mazos fijados y protegidos", "Sin pellizcos ni dobleces excesivos", "Sin interferencia con mandos"],
            ["Manual del equipo de Mecánica", "Manual del equipo de Avionica"],
            ["Cable aplastado entre paneles", "Doblez marcado en el arnés"]),
    _riesgo("R-MC-09", "Estructura y mecánica", "Riesgos en maquinado, montaje de prueba e instalación",
            "Peligros durante la fabricación, la prueba de ajuste, la re-verificación y la verificación funcional.",
            ["Mecánica", "Supervisión y Planeación"],
            ["Trabajar sin equipo de protección", "No verificar el ajuste antes de fijar", "Instalar sin validar la función"],
            ["Lesiones por herramientas", "Pieza mal ajustada que se daña", "Instalación que falla en operación"],
            ["Usar equipo de protección adecuado", "Probar el ajuste antes de la fijación final", "Validar la función tras cada instalación"],
            ["Detener la tarea", "Atender cualquier lesión y reportar", "Corregir el ajuste o la instalación y validar"],
            ["EPP disponible y en uso", "Ajuste verificado antes de fijar", "Función validada tras instalar"],
            ["Manual del equipo de Mecánica"],
            ["Montaje sin prueba de ajuste previa", "Instalación sin validación funcional"]),

    # ===== C. Software, integración y pruebas =====
    _riesgo("R-SW-01", "Software, integración y pruebas", "Error de mapeo de entradas",
            "Asignación incorrecta de las entradas físicas a los mandos y funciones de X-Plane 12.",
            ["Software", "Avionica"],
            ["DataRef o comando equivocado", "Entrada conectada al pin incorrecto", "Configuración desactualizada"],
            ["Mando que no responde o lo hace invertido", "Funciones cruzadas", "Entrenamiento con controles erróneos"],
            ["Documentar el mapeo de cada entrada", "Verificar cada DataRef/Command antes de asignar", "Probar cada mando tras configurar"],
            ["Identificar la entrada mal mapeada", "Corregir la asignación", "Repetir la prueba funcional del mando"],
            ["Mapeo documentado y verificado", "Cada mando responde a su función", "Sin funciones cruzadas"],
            ["Manual del equipo de Software"],
            ["Mando que activa otra función", "Entrada sin respuesta"]),
    _riesgo("R-SW-02", "Software, integración y pruebas", "Falla de calibración de sensores",
            "Sensores sin calibrar o mal calibrados que entregan valores incorrectos al simulador.",
            ["Software", "Avionica"],
            ["Calibración omitida", "Rango mal configurado", "Deriva del sensor"],
            ["Instrumentos que indican mal", "Mandos con respuesta imprecisa", "Entrenamiento con datos falsos"],
            ["Calibrar cada sensor según el procedimiento", "Verificar el rango y el cero", "Re-calibrar tras cambios de montaje"],
            ["Repetir la calibración del sensor afectado", "Comparar contra una referencia conocida", "Validar la lectura en pantalla"],
            ["Sensor calibrado y verificado", "Lectura acorde a la referencia", "Rango correcto en los extremos"],
            ["Manual del equipo de Software"],
            ["Lectura que no corresponde a la posición real", "Sensor con deriva"]),
    _riesgo("R-SW-03", "Software, integración y pruebas", "Recorrido de servo fuera de límites",
            "Servo que intenta superar su recorrido mecánico y se esfuerza contra el tope.",
            ["Software", "Avionica", "Mecánica"],
            ["Límite de software mal configurado", "Tope mecánico desalineado", "Orden de salida fuera de rango"],
            ["Servo que zumba y se calienta", "Desgaste o rotura del servo", "Mando atascado"],
            ["Limitar el recorrido en software y mecánica", "Alinear los topes mecánicos", "Verificar la salida máxima del servo"],
            ["Desenergizar", "Corregir el límite de recorrido", "Validar el movimiento completo sin esfuerzo"],
            ["Servo sin esfuerzo en los extremos", "Recorrido dentro de los límites", "Sin calentamiento"],
            ["Manual del equipo de Software"],
            ["Servo que zumba en el tope", "Salida que intenta pasar del límite"]),
    _riesgo("R-SW-04", "Software, integración y pruebas", "Falla de integración con X-Plane 12",
            "Falla de integración entre X-Plane 12, el hardware de control, la interfaz de comunicación y los displays.",
            ["Software", "Avionica"],
            ["Versión incompatible de X-Plane o plugins", "Puerto o protocolo mal configurado", "DataRef/Command inexistente"],
            ["Simulador sin respuesta a los mandos", "Displays sin información", "Imposibilidad de entrenar"],
            ["Verificar compatibilidad de versiones", "Configurar el puerto y protocolo correctamente", "Probar la integración de forma incremental"],
            ["Registrar el error y aislar el componente", "Corregir la configuración o el plugin", "Repetir la prueba de integración"],
            ["Comunicación estable entre hardware y X-Plane", "Displays actualizados", "Mandos con respuesta correcta"],
            ["Manual del equipo de Software"],
            ["X-Plane que no recibe datos", "Display congelado o sin datos"]),
    _riesgo("R-SW-05", "Software, integración y pruebas", "Interacción entre fallas eléctricas y mecánicas",
            "Una falla eléctrica y una mecánica se combinan y producen un efecto mayor o distinto.",
            ["Avionica", "Mecánica", "Software"],
            ["Servo atascado que sobrecarga la electrónica", "Cable dañado que mueve mal un mando", "Falla que oculta otra falla"],
            ["Efecto combinado difícil de diagnosticar", "Daño en cadena", "Falsa lectura del estado real"],
            ["Analizar las interfaces entre sistemas", "Probar de forma integrada, no solo por partes", "Registrar fallas y su secuencia"],
            ["Aislar el sistema completo", "Investigar la secuencia de fallas", "Corregir ambas causas y validar en conjunto"],
            ["Sistema integrado sin fallas combinadas", "Interfaces revisadas", "Prueba conjunta satisfactoria"],
            ["Manual del equipo de Avionica", "Manual del equipo de Mecánica"],
            ["Falla que reaparece al probar en conjunto", "Síntomas que no corresponden a una sola causa"]),
    _riesgo("R-SW-06", "Software, integración y pruebas", "Retroalimentación de estado errónea",
            "El sistema informa un estado que no corresponde a la condición real del equipo.",
            ["Software", "Avionica"],
            ["Sensor o indicador descalibrado", "Lógica de estado mal programada", "Señal invertida"],
            ["Operador confía en un estado falso", "Decisiones equivocadas", "Pérdida de confianza en el sistema"],
            ["Verificar la lógica de estado", "Calibrar los sensores que alimentan el estado", "Probar los estados con condiciones conocidas"],
            ["Registrar el estado erróneo", "Corregir la lógica o el sensor", "Validar con la condición real"],
            ["Estados que reflejan la condición real", "Indicadores coherentes", "Sin señales invertidas"],
            ["Manual del equipo de Software"],
            ["Indicador que muestra un estado imposible", "Estado que cambia sin causa"]),
    _riesgo("R-SW-07", "Software, integración y pruebas", "Pruebas repetitivas sin criterio de aceptación",
            "Pruebas que se repiten sin criterios claros o sin verificación de aceptación.",
            ["Software", "Vuelo", "Supervisión y Planeación"],
            ["Criterio de aceptación no definido", "Repetir pruebas sin registrar resultados", "Falta de revisión de aceptación"],
            ["Defectos que pasan desapercibidos", "Retrabajo al final del proyecto", "Aceptación sin evidencia"],
            ["Definir criterios de aceptación por prueba", "Registrar los resultados de cada prueba", "Revisar y firmar la aceptación"],
            ["Detener la repetición sin sentido", "Definir el criterio y el resultado esperado", "Documentar y validar la aceptación"],
            ["Criterios de aceptación definidos", "Resultados registrados", "Aceptación documentada"],
            ["Manual del equipo de Software"],
            ["Pruebas sin criterio ni registro", "Resultado no documentado"]),
]


# ---------------------------------------------------------------------------
# Referencias técnicas verificables (biblioteca compartida de fuentes oficiales)
# ---------------------------------------------------------------------------
REF_ARDUINO_MEGA = {
    "org": "Arduino",
    "titulo": "Arduino Mega 2560 Rev3 — Documentación y especificaciones técnicas",
    "documento": "Mega 2560 Rev3 (A000067)",
    "seccion": "Tech Specs — ATmega2560 · 54 pines digitales (15 PWM) · 16 entradas analógicas · 4 UART",
    "url": "https://docs.arduino.cc/hardware/mega-2560/",
    "conclusion": "Placa basada en ATmega2560. La corriente por pin de E/S es limitada (típicamente 20 mA recomendado, 40 mA máximo); las cargas mayores requieren driver o fuente externa con masa común.",
}
REF_ARDUINO_MEGA_STORE = {
    "org": "Arduino",
    "titulo": "Arduino Mega 2560 Rev3 — Página oficial del producto",
    "documento": "Mega 2560 Rev3 (A000067)",
    "seccion": "Especificaciones del producto (voltaje de operación, corriente por pin)",
    "url": "https://store.arduino.cc/products/arduino-mega-2560-rev3",
    "conclusion": "Fuente oficial para confirmar voltaje de alimentación y límites de corriente de los pines antes de conectar cargas.",
}
REF_FAA_AC_25_26 = {
    "org": "FAA (Federal Aviation Administration)",
    "titulo": "AC 25-26 — Development of standard wiring practices documentation",
    "documento": "Advisory Circular AC 25-26",
    "seccion": "Prácticas estándar de cableado: protección, fijación, rutado e inspección del arnés",
    "url": "https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25-26.pdf",
    "conclusion": "Orienta sobre prácticas de cableado (sujeción, protección, separación e inspección). Se usa como referencia de buenas prácticas; el proyecto es un simulador terrestre y no exige certificación de aeronave.",
}
REF_FAA_AC_120_94 = {
    "org": "FAA (Federal Aviation Administration)",
    "titulo": "AC 120-94 — Aircraft Electrical Wiring Interconnection Systems (EWIS) training",
    "documento": "Advisory Circular AC 120-94",
    "seccion": "Criterios de inspección y mantenimiento de EWIS: contaminación, daño del aislamiento, fijación y rutado",
    "url": "https://www.faa.gov/documentLibrary/media/Advisory_Circular/120-94.pdf",
    "conclusion": "Describe criterios para inspeccionar el sistema de interconexión de cableado (contaminación, aislamiento dañado, terminales y alivio de esfuerzo).",
}
REF_OSHA_1910_147 = {
    "org": "OSHA (Occupational Safety and Health Administration)",
    "titulo": "1910.147 — The control of hazardous energy (lockout/tagout)",
    "documento": "29 CFR 1910.147",
    "seccion": "Requisitos de aislamiento y control de energía peligrosa en mantenimiento",
    "url": "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147",
    "conclusion": "Establece aislar y bloquear/etiquetar las fuentes de energía antes del mantenimiento para evitar la energización inesperada.",
}
REF_OSHA_MG = {
    "org": "OSHA (Occupational Safety and Health Administration)",
    "titulo": "Machine Guarding eTool — General Requirements",
    "documento": "OSHA eTool — Machine Guarding",
    "seccion": "Requisitos generales de resguardo de máquinas y protección frente a puntos de operación",
    "url": "https://www.osha.gov/etools/machine-guarding/introduction/general-requirements",
    "conclusion": "Orienta sobre la protección del personal frente a piezas móviles, virutas y puntos de operación durante el mecanizado.",
}

PEND_REF = {"org": None, "titulo": "Referencia específica pendiente de verificación", "documento": None,
            "seccion": None, "url": None,
            "conclusion": "No se localizó una fuente oficial verificable para este punto; se deberá confirmar antes de considerarla respaldada."}

# ---------------------------------------------------------------------------
# Enriquecimiento de contenido por registro de riesgo (fuente única de verdad).
# Se aplica en construir_riesgos() para rellenar los 7 campos con texto específico.
# ---------------------------------------------------------------------------
ENRIQUECIMIENTO = {}

ENRIQUECIMIENTO.update({
    # ===== Limpieza =====
    "EEA-DC3-XBDPC-LIM-RSG-001": {
        "causas": ["Restos orgánicos acumulados en la cabina (moho, esporas, excretas de animales)", "Falta de limpieza previa o de ventilación en la zona", "Manipulación de superficies contaminadas sin equipo de protección"],
        "disparadores": ["Remover paneles y tapicería que liberan partículas", "Aspirar o barrer material seco contaminado", "Trabajar en zonas cerradas sin ventilación"],
        "consecuencias": ["Irritación respiratoria o cutánea del personal", "Contaminación cruzada de herramientas y zonas limpias", "Pausa del trabajo por limpieza y desinfección adicional"],
        "medidas_preventivas": ["Usar mascarilla, guantes y protección ocular al manipular material contaminado", "Humedecer el material antes de removerlo para evitar suspender partículas", "Ventilar la cabina y delimitar la zona de trabajo"],
        "que_hacer": ["Detener la tarea y retirar al personal de la zona", "Ventilar el área y aplicar el procedimiento de limpieza/desinfección", "Reportar la exposición y registrar los hechos", "Reanudar solo con el equipo de protección completo"],
        "inspeccion": ["Zona ventilada y material contaminado confinado", "Personal con EPP adecuado y en buen estado", "Superficies limpias antes de continuar"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-002": {
        "causas": ["Chapas y bordes metálicos cortantes sin desbarbar", "Perfiles dañados o con rebabas tras el desmontaje", "Manipulación sin guantes resistentes al corte"],
        "disparadores": ["Desmontar paneles y piezas con bordes expuestos", "Introducir las manos en zonas ocultas o entre chapas", "Mover piezas cortantes sin asegurar el agarre"],
        "consecuencias": ["Cortes en manos y brazos", "Daño de cables o componentes al rozar un borde", "Retraso por atención médica y limpieza"],
        "medidas_preventivas": ["Usar guantes resistentes al corte", "Desbarbar o cubrir los bordes expuestos", "Manipular las chapas por zonas seguras y con agarre firme"],
        "que_hacer": ["Detener la manipulación", "Atender la herida según el protocolo de primeros auxilios", "Identificar y cubrir o desbarbar el borde causante", "Registrar el incidente antes de continuar"],
        "inspeccion": ["Bordes expuestos desbarbados o cubiertos", "Personal con guantes adecuados", "Zona libre de chapas cortantes sueltas"],
        "referencias": [REF_OSHA_MG],
    },
    "EEA-DC3-XBDPC-LIM-RSG-003": {
        "causas": ["Residuos químicos no identificados en la cabina", "Envases sin etiqueta o deteriorados", "Mezcla accidental de productos incompatibles"],
        "disparadores": ["Aplicar un producto sobre una superficie sin conocer su naturaleza", "Abrir un envase sin etiqueta", "Mezclar limpiadores de distinto tipo"],
        "consecuencias": ["Quemaduras o irritación de piel y vías respiratorias", "Reacción química que daña materiales de la cabina", "Contaminación del área de trabajo"],
        "medidas_preventivas": ["Identificar el producto antes de usarlo y leer la etiqueta", "No mezclar productos de distinto tipo", "Usar guantes, gafas y ventilación adecuadas"],
        "que_hacer": ["Detener la aplicación y ventilar la zona", "Retirar el producto derramado con el método adecuado", "Atender cualquier contacto con piel u ojos", "Etiquetar y reportar el producto no identificado"],
        "inspeccion": ["Productos etiquetados y almacenados correctamente", "Sin mezclas de productos incompatibles", "Personal con protección química adecuada"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-004": {
        "causas": ["Retiro de cableado sin autorización del equipo de Avionica", "Corte o desconexión de conductores que se creían sin energía", "Falta de identificación de circuitos activos"],
        "disparadores": ["Manipular o cortar cables durante la limpieza", "Desconectar conectores sin verificar el estado de energía", "Trabajar cerca de cableado no identificado"],
        "consecuencias": ["Descarga eléctrica al personal", "Daño de circuitos del simulador", "Retrabajo de cableado y retraso"],
        "medidas_preventivas": ["No retirar ni cortar cableado sin autorización de Avionica", "Aislar y verificar ausencia de tensión antes de intervenir", "Identificar y proteger el cableado cercano a la zona de trabajo"],
        "que_hacer": ["Detener la manipulación eléctrica", "Aislar la zona y verificar ausencia de tensión", "Reportar a Avionica y no reconectar sin autorización", "Registrar lo ocurrido y las acciones realizadas"],
        "inspeccion": ["Cableado identificado y protegido", "Sin intervención eléctrica no autorizada", "Ausencia de tensión verificada antes de trabajar"],
        "referencias": [REF_OSHA_1910_147, REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-LIM-RSG-005": {
        "causas": ["Uso de productos corrosivos o abrasivos sobre superficies delicadas", "Concentración o tiempo de contacto excesivo", "Aplicación sobre materiales incompatibles"],
        "disparadores": ["Frotar con estropajo o producto abrasivo una superficie pintada o un instrumento", "Dejar actuar un producto corrosivo más tiempo del indicado", "Usar el producto sin diluir"],
        "consecuencias": ["Daño del acabado o de los instrumentos", "Corrosión localizada", "Rechazo del componente y retrabajo"],
        "medidas_preventivas": ["Usar el producto indicado para cada superficie", "Respetar dilución y tiempo de contacto", "Probar en una zona poco visible antes de aplicar"],
        "que_hacer": ["Detener la aplicación y enjuagar la superficie según el producto", "Evaluar el daño causado", "Reportar y definir la corrección con el responsable", "Registrar el producto y la superficie afectada"],
        "inspeccion": ["Producto correcto para el material", "Dilución y tiempo respetados", "Sin daño visible en superficies tratadas"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-006": {
        "causas": ["Paneles o elementos sueltos por fijación incompleta o corroída", "Apilamiento inestable de piezas desmontadas", "Manipulación sin asegurar la pieza"],
        "disparadores": ["Mover una pieza suelta durante la limpieza", "Retirar el último tornillo de un panel sin soporte", "Trabajar debajo de elementos mal sujetos"],
        "consecuencias": ["Caída de la pieza sobre el personal o el equipo", "Daño de la pieza y de componentes cercanos", "Lesiones por golpe"],
        "medidas_preventivas": ["Asegurar o retirar los paneles sueltos antes de limpiar", "Apilar las piezas de forma estable y fuera de paso", "No trabajar debajo de elementos sin asegurar"],
        "que_hacer": ["Detener el trabajo y asegurar la zona", "Atender cualquier lesión", "Retirar o sujetar la pieza suelta", "Reportar y corregir la causa de la caída"],
        "inspeccion": ["Piezas aseguradas o retiradas", "Apilamiento estable", "Zona de trabajo despejada"],
        "referencias": [REF_OSHA_MG],
    },
    "EEA-DC3-XBDPC-LIM-RSG-007": {
        "causas": ["Corrosión avanzada en estructura o fijaciones", "Daño estructural no detectado", "Piezas debilitadas por la corrosión"],
        "disparadores": ["Aplicar carga o apalancar sobre una zona corroída", "Retirar una fijación muy oxidada", "Detectar grietas o adelgazamiento durante la limpieza"],
        "consecuencias": ["Falla estructural local", "Caída o rotura de la pieza", "Pérdida de integridad de la cabina"],
        "medidas_preventivas": ["Inspeccionar visualmente antes de intervenir", "No apalancar ni cargar zonas corroídas", "Reportar la corrosión severa antes de continuar"],
        "que_hacer": ["Detener la intervención sobre la zona", "Delimitar y no cargar la estructura afectada", "Reportar a Mecánica y Supervisión", "Definir la reparación antes de continuar"],
        "inspeccion": ["Zonas corroídas identificadas y señaladas", "Sin carga sobre estructura debilitada", "Reporte emitido a los responsables"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-008": {
        "causas": ["Descartar componentes reutilizables o con valor", "Falta de criterio sobre qué conservar", "Mezcla de piezas aprovechables con residuos"],
        "disparadores": ["Separar material durante la limpieza sin inventario", "Tirar piezas retiradas sin autorización", "No etiquetar las piezas conservadas"],
        "consecuencias": ["Pérdida de componentes necesarios", "Costo y retraso por reposición", "Incumplimiento del control documental"],
        "medidas_preventivas": ["Clasificar y etiquetar las piezas antes de desechar", "Consultar antes de descartar componentes", "Llevar inventario de lo retirado"],
        "que_hacer": ["Detener el descarte", "Recuperar y clasificar las piezas si es posible", "Reportar lo descartado indebidamente", "Actualizar el inventario"],
        "inspeccion": ["Piezas clasificadas y etiquetadas", "Sin descarte sin autorización", "Inventario actualizado"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-009": {
        "causas": ["Suspensión de polvo y partículas al aspirar o barrer", "Falta de extracción o filtración adecuada", "Limpieza en seco de zonas muy polvorientas"],
        "disparadores": ["Aspirar sin filtro HEPA o con el equipo saturado", "Barrer material seco en la cabina", "Limpieza prolongada sin mascarilla"],
        "consecuencias": ["Irritación respiratoria", "Contaminación de instrumentos y conectores", "Pausa por limpieza adicional"],
        "medidas_preventivas": ["Usar aspiración con filtro adecuado", "Humedecer antes de barrer", "Usar mascarilla y ventilar la zona"],
        "que_hacer": ["Detener la tarea y ventilar", "Retirar el polvo suspendido con aspiración húmeda", "Revisar el estado del equipo de aspiración", "Reanudar con protección adecuada"],
        "inspeccion": ["Equipo de aspiración con filtro operativo", "Zona ventilada y sin polvo suspendido", "Personal con mascarilla"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LIM-RSG-010": {
        "causas": ["Derrames de agua o producto sobre el piso", "Superficies mojadas sin señalizar", "Falta de drenaje o secado"],
        "disparadores": ["Caminar sobre una zona mojada", "Verter agua o limpiador sin controlar el derrame", "Trabajar en una zona con pendiente resbaladiza"],
        "consecuencias": ["Caídas y resbalones del personal", "Daño por caída de herramientas o equipos", "Lesiones y retraso"],
        "medidas_preventivas": ["Contener y secar los derrames de inmediato", "Señalizar las zonas mojadas", "Usar calzado antideslizante"],
        "que_hacer": ["Señalizar y delimitar la zona resbaladiza", "Secar el derrame con material absorbente", "Atender cualquier caída y reportar", "Verificar el piso antes de reanudar"],
        "inspeccion": ["Piso seco y sin derrames", "Zonas mojadas señalizadas", "Calzado antideslizante disponible"],
        "referencias": [PEND_REF],
    },
})

ENRIQUECIMIENTO.update({
    # ===== Supervisión y Planeación =====
    "EEA-DC3-XBDPC-SYP-RSG-001": {
        "causas": ["Dependencias entre equipos no resueltas a tiempo", "Entregables previos no concluidos", "Fechas del cronograma sin margen de holgura"],
        "disparadores": ["Un equipo espera un insumo de otro equipo", "Una puerta de enlace no se completa en la fecha", "Acumulación de tareas pendientes en una semana"],
        "consecuencias": ["Desplazamiento del cronograma", "Trabajo en paralelo desordenado", "Presión para recortar verificaciones"],
        "medidas_preventivas": ["Revisar semanalmente las dependencias y sus fechas", "Definir responsables y fecha de cada insumo", "Alertar con anticipación cuando una dependencia se atrasa"],
        "que_hacer": ["Registrar la dependencia bloqueada", "Replanificar con los responsables involucrados", "Comunicar el impacto al cronograma", "Dar seguimiento hasta cerrar la dependencia"],
        "inspeccion": ["Dependencias identificadas y fechadas", "Alertas emitidas con anticipación", "Cronograma actualizado"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-002": {
        "causas": ["Compras sin aprobación de la dirección", "Solicitud de compra incompleta", "Proveedor sin confirmación"],
        "disparadores": ["Iniciar una actividad que requiere material no adquirido", "Requerir un componente crítico sin orden de compra", "Esperar autorización de la dirección"],
        "consecuencias": ["Paro de actividades por falta de material", "Retraso del cronograma", "Compras de emergencia con mayor costo"],
        "medidas_preventivas": ["Preparar la solicitud con especificaciones y justificación", "Gestionar la aprobación con anticipación", "Confirmar proveedor y tiempo de entrega"],
        "que_hacer": ["Registrar la falta de aprobación", "Escalar la solicitud a la dirección", "Buscar alternativa aprobada mientras tanto", "Actualizar el cronograma"],
        "inspeccion": ["Solicitudes completas y aprobadas", "Proveedor confirmado", "Sin actividades detenidas por compras"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-003": {
        "causas": ["Dos o más equipos ocupan la misma zona de la cabina", "Falta de plan de ocupación por turnos", "Dimensiones del espacio mal estimadas"],
        "disparadores": ["Coincidir dos equipos en la cabina al mismo tiempo", "Instalar un componente donde otro ya trabaja", "Cambio de alcance que ocupa espacio"],
        "consecuencias": ["Bloqueo de actividades", "Riesgo de daños por interferencia", "Retrabajo por reubicación"],
        "medidas_preventivas": ["Planificar la ocupación de la cabina por turnos", "Coordinar los espacios antes de instalar", "Verificar dimensiones con Mecánica y Avionica"],
        "que_hacer": ["Suspender la actividad en conflicto", "Coordinar la liberación del espacio", "Reasignar turnos o ubicación", "Registrar el conflicto y la solución"],
        "inspeccion": ["Plan de ocupación vigente", "Sin dos equipos en conflicto", "Espacio suficiente verificado"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-004": {
        "causas": ["Presencia de polvo, solventes y bordes afilados en el área", "Falta de EPP o de ventilación", "Trabajo simultáneo de equipos con distintos riesgos"],
        "disparadores": ["Exposición a solventes sin ventilación", "Manipular bordes afilados sin guantes", "Acumulación de polvo sin extracción"],
        "consecuencias": ["Lesiones o afecciones del personal", "Paro de actividades por incidente HSE", "Incumplimiento de condiciones de trabajo seguras"],
        "medidas_preventivas": ["Asegurar EPP y ventilación antes de iniciar", "Limitar el uso de solventes a zonas ventiladas", "Desbarbar y limpiar la zona de trabajo"],
        "que_hacer": ["Detener la actividad y retirar al personal expuesto", "Aplicar primeros auxilios si corresponde", "Ventilar y limpiar la zona", "Reportar y corregir la causa"],
        "inspeccion": ["EPP disponible y en uso", "Ventilación operativa", "Zona sin acumulación de polvo ni solventes"],
        "referencias": [REF_OSHA_MG],
    },
    "EEA-DC3-XBDPC-SYP-RSG-005": {
        "causas": ["Cambios de alcance sin control de cambios", "Nuevos requisitos no documentados", "Aceptación informal de modificaciones"],
        "disparadores": ["Un interesado pide una modificación no prevista", "Se agrega una función sin actualizar el plan", "Se cambia un requisito sin aprobación"],
        "consecuencias": ["Desviación del alcance y del presupuesto", "Retrabajo e inconsistencias", "Difícil trazabilidad del entregable"],
        "medidas_preventivas": ["Aplicar control de cambios formal", "Documentar y aprobar cada modificación", "Comunicar el cambio a todos los equipos"],
        "que_hacer": ["Detener el trabajo afectado", "Registrar la solicitud de cambio", "Evaluar impacto y obtener aprobación", "Actualizar plan y documentación"],
        "inspeccion": ["Cambios registrados y aprobados", "Plan y documentos actualizados", "Sin modificaciones informales"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-006": {
        "causas": ["Integración de hardware y software sin pruebas conjuntas", "Interfaces no acordadas entre Avionica y Software", "Configuración inconsistente de versiones"],
        "disparadores": ["Conectar un módulo al simulador sin prueba de integración", "Actualizar firmware sin verificar el software", "Detectar un error solo en la integración final"],
        "consecuencias": ["Fallas en la operación del simulador", "Retraso por diagnóstico tardío", "Retrabajo de hardware o software"],
        "medidas_preventivas": ["Definir las interfaces entre equipos por escrito", "Probar de forma incremental la integración", "Mantener versiones compatibles documentadas"],
        "que_hacer": ["Registrar la falla de integración", "Aislar el componente que falla", "Corregir la interfaz o versión", "Repetir la prueba de integración"],
        "inspeccion": ["Interfaces documentadas", "Versiones compatibles", "Prueba de integración satisfactoria"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-SYP-RSG-007": {
        "causas": ["Documentación As-Built incompleta", "Registros inconsistentes entre equipos", "Cambios no reflejados en los planos"],
        "disparadores": ["Entregar un documento sin reflejar la construcción real", "Detectar una diferencia entre plano y equipo", "Faltar un registro de cambio"],
        "consecuencias": ["Trazabilidad deficiente", "Dificultad de mantenimiento futuro", "Rechazo del expediente técnico"],
        "medidas_preventivas": ["Actualizar el As-Built tras cada cambio", "Verificar que el documento refleja lo construido", "Controlar versiones de los planos"],
        "que_hacer": ["Registrar la inconsistencia", "Corregir el documento con el dato real", "Comunicar la actualización a los equipos", "Verificar la versión final"],
        "inspeccion": ["As-Built actualizado y versionado", "Plano coherente con lo construido", "Sin diferencias pendientes"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-008": {
        "causas": ["Desviación en la calibración de los mandos", "Sensores o potenciómetros con deriva", "Calibración inicial mal realizada"],
        "disparadores": ["Mando que no coincide con el valor mostrado en pantalla", "Repetir una calibración sin éxito", "Cambiar un sensor sin recalibrar"],
        "consecuencias": ["Respuesta incorrecta de los mandos", "Entrenamiento con datos imprecisos", "Retrabajo de calibración"],
        "medidas_preventivas": ["Calibrar siguiendo el procedimiento del equipo", "Verificar rango y cero de cada sensor", "Recalibrar tras cualquier cambio de montaje"],
        "que_hacer": ["Registrar la desviación", "Repetir la calibración del mando afectado", "Comparar contra una referencia conocida", "Validar la lectura en pantalla"],
        "inspeccion": ["Calibración documentada", "Lecturas coherentes con la posición", "Sin deriva tras la prueba"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-SYP-RSG-009": {
        "causas": ["Firmas técnicas realizadas por personal no autorizado", "Roles de aprobación no definidos", "Documentos firmados sin revisión técnica"],
        "disparadores": ["Firmar un documento sin tener la facultad", "Aprobar un resultado sin revisión", "Falta de matriz de responsabilidades"],
        "consecuencias": ["Documentos sin validez técnica", "Responsabilidad mal asignada", "Rechazo en auditoría"],
        "medidas_preventivas": ["Definir la matriz de firmas autorizadas", "Verificar la facultad antes de firmar", "Revisar técnicamente antes de aprobar"],
        "que_hacer": ["Detener la firma no autorizada", "Informar al responsable correcto", "Corregir el documento con la firma válida", "Registrar la incidencia"],
        "inspeccion": ["Matriz de firmas vigente", "Firmas conforme a la facultad", "Sin documentos con firma indebida"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SYP-RSG-010": {
        "causas": ["Aceptación final sin evidencia suficiente", "Criterios de aceptación no definidos", "Pruebas incompletas o no documentadas"],
        "disparadores": ["Cerrar una fase sin verificar los entregables", "Aprobar sin revisar los resultados", "Faltar registros de prueba"],
        "consecuencias": ["Entregable defectuoso aceptado", "Retrabajo después del cierre", "Pérdida de trazabilidad"],
        "medidas_preventivas": ["Definir criterios de aceptación por entregable", "Revisar la evidencia antes de aceptar", "Documentar las pruebas y sus resultados"],
        "que_hacer": ["Suspender la aceptación", "Reunir y revisar la evidencia faltante", "Ejecutar las pruebas pendientes", "Aceptar solo con evidencia completa"],
        "inspeccion": ["Criterios de aceptación definidos", "Evidencia completa y revisada", "Aceptación documentada"],
        "referencias": [PEND_REF],
    },
})


ENRIQUECIMIENTO.update({
    # ===== Avionica =====
    "EEA-DC3-XBDPC-AVI-RSG-001": {
        "causas": ["Conexión de positivo y negativo invertidos", "Contacto entre conductores con distinto potencial", "Aislamiento dañado o restos metálicos sobre la placa"],
        "disparadores": ["Primera energización sin revisión previa", "Reconexión apresurada de un conector", "Presencia de virutas sobre la tarjeta"],
        "consecuencias": ["Daño de fuentes, microcontrolador o actuadores", "Calentamiento anómalo", "Interrupción del sistema en prueba"],
        "medidas_preventivas": ["Verificar polaridad y aislamiento antes de energizar", "Limpiar restos metálicos de las tarjetas", "Proteger cada ramal con fusible/breaker adecuado"],
        "que_hacer": ["Desenergizar de inmediato", "Inspeccionar el punto de falla y sustituir el componente dañado", "Corregir la causa antes de reconectar", "Repetir la prueba sin carga"],
        "inspeccion": ["Polaridad correcta en cada conector", "Sin restos metálicos", "Protección conforme al diseño"],
        "referencias": [REF_ARDUINO_MEGA, REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-AVI-RSG-002": {
        "causas": ["Carga conectada directamente a un pin GPIO sin driver", "Consumo de la carga mayor que la corriente del pin", "Ausencia de fuente externa y masa común"],
        "disparadores": ["Conectar un LED, relé o motor directo al pin", "Encender varias cargas a la vez desde la placa", "Medir corriente por pin por encima del límite"],
        "consecuencias": ["Daño del pin o del microcontrolador", "Caída de tensión y funcionamiento errático", "Sobrecalentamiento de la placa"],
        "medidas_preventivas": ["Consultar la corriente máxima por pin en la hoja de datos", "Usar driver o fuente externa para cargas mayores", "Asegurar masa común entre placa y fuente externa"],
        "que_hacer": ["Desenergizar la placa", "Retirar la carga directa del pin", "Instalar el driver o fuente externa adecuada", "Verificar la corriente y repetir la prueba"],
        "inspeccion": ["Ninguna carga mayor conectada directo al pin", "Driver o fuente externa instalado", "Corriente por pin dentro del límite"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-AVI-RSG-003": {
        "causas": ["DataRef o Command de X-Plane no verificado", "Nombre del DataRef mal escrito o inexistente", "Uso de un comando sin confirmar su función"],
        "disparadores": ["Asignar un DataRef sin probarlo", "Actualizar X-Plane y que cambie un DataRef", "Detectar que un mando no responde"],
        "consecuencias": ["Mandos que no responden o lo hacen mal", "Funciones cruzadas entre controles", "Entrenamiento con mandos erróneos"],
        "medidas_preventivas": ["Verificar cada DataRef/Command antes de usarlo", "Documentar el mapeo de cada control", "Probar cada mando tras la asignación"],
        "que_hacer": ["Registrar el DataRef no verificado", "Consultar la referencia de X-Plane para confirmar el nombre", "Corregir la asignación", "Repetir la prueba del mando"],
        "inspeccion": ["Mapeo documentado y verificado", "Cada mando responde a su función", "Sin funciones cruzadas"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-AVI-RSG-004": {
        "causas": ["Manipular tarjetas sin protección antiestática", "Ambiente seco que acumula carga", "Ausencia de pulsera o superficie antiestática"],
        "disparadores": ["Tocar un microcontrolador sin pulsera antiestática", "Guardar tarjetas fuera de bolsa antiestática", "Manipular en un ambiente seco"],
        "consecuencias": ["Daño latente o inmediato de componentes", "Fallas intermitentes difíciles de diagnosticar", "Reducción de vida útil"],
        "medidas_preventivas": ["Usar pulsera y superficie antiestática", "Manipular las tarjetas por los bordes", "Almacenar en bolsas antiestáticas"],
        "que_hacer": ["Detener la manipulación", "Sustituir el componente sospechoso", "Reforzar el protocolo ESD", "Documentar la falla"],
        "inspeccion": ["Zona de trabajo con protección ESD", "Personal con pulsera conectada", "Componentes sin daño tras la manipulación"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-AVI-RSG-005": {
        "causas": ["Bucles de tierra con referencias distintas", "Cables de señal cerca de líneas de potencia", "Blindaje ausente o mal conectado"],
        "disparadores": ["Ruido en instrumentos al activar motores", "Comunicación serial con errores", "Valores de sensor que saltan"],
        "consecuencias": ["Lecturas erráticas", "Comunicación inestable", "Parpadeo o falla de displays"],
        "medidas_preventivas": ["Definir un único punto de referencia de tierra", "Separar cableado de potencia y de señal", "Trenzar y blindar los cables de señal"],
        "que_hacer": ["Identificar la fuente de ruido", "Reordenar o blindar el cableado", "Conectar el blindaje a tierra correctamente", "Verificar que la comunicación se estabiliza"],
        "inspeccion": ["Sin bucles de tierra", "Potencia y señal separadas", "Blindajes conectados a tierra"],
        "referencias": [REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-AVI-RSG-006": {
        "causas": ["Tensión de las lámparas no verificada contra la fuente", "Lámpara con tensión distinta a la alimentación", "Mezcla de lámparas de distinto voltaje en un circuito"],
        "disparadores": ["Conectar una lámpara a una tensión mayor", "Encender el circuito de iluminación sin verificar", "Sustituir una lámpara por otra de distinto voltaje"],
        "consecuencias": ["Quemado inmediato de la lámpara", "Daño del circuito de alimentación", "Iluminación de cabina inoperante"],
        "medidas_preventivas": ["Verificar la tensión nominal de cada lámpara", "Comprobar la tensión de la fuente antes de conectar", "No mezclar lámparas de distinto voltaje"],
        "que_hacer": ["Desenergizar el circuito", "Reemplazar la lámpara por la de voltaje correcto", "Verificar la fuente", "Probar el circuito de iluminación"],
        "inspeccion": ["Tensión de lámpara y fuente coincidentes", "Sin mezcla de voltajes", "Iluminación operativa"],
        "referencias": [REF_ARDUINO_MEGA_STORE],
    },
    "EEA-DC3-XBDPC-AVI-RSG-007": {
        "causas": ["Cableado móvil sin alivio de esfuerzo", "Conectores que soportan el peso del cable", "Cables que se doblan en el punto de conexión"],
        "disparadores": ["Mover un mando y tensar el cable", "Doblar el cable repetidamente en el conector", "Vibrar el equipo con el cable fijo"],
        "consecuencias": ["Rotura del conductor en el punto de conexión", "Falsa conexión intermitente", "Daño del conector"],
        "medidas_preventivas": ["Fijar el cable con alivio de esfuerzo", "Dejar holgura suficiente en zonas móviles", "Usar conectores y prensacables adecuados"],
        "que_hacer": ["Detener el movimiento que tensa el cable", "Inspeccionar y reparar el punto de conexión", "Instalar alivio de esfuerzo", "Verificar la conexión en movimiento"],
        "inspeccion": ["Alivio de esfuerzo en cada conector móvil", "Holgura suficiente", "Sin desgaste en el punto de conexión"],
        "referencias": [REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-AVI-RSG-008": {
        "causas": ["Incompatibilidad de la aplicación Garmin 750 con la versión del simulador", "Configuración incorrecta de la app", "Falta de actualización de la interfaz de la app"],
        "disparadores": ["Lanzar la app Garmin 750 en el monitor central", "Actualizar el simulador o la app", "Detectar que la app no responde o no se muestra"],
        "consecuencias": ["Monitor central sin la app de navegación", "Pérdida de la referencia de navegación", "Entrenamiento incompleto"],
        "medidas_preventivas": ["Verificar compatibilidad de versiones", "Configurar la app según el procedimiento", "Probar la app antes de la sesión de entrenamiento"],
        "que_hacer": ["Registrar el error de la app", "Revisar configuración y versión", "Reinstalar o actualizar la app si aplica", "Validar la app en el monitor"],
        "inspeccion": ["Versión compatible", "App operativa en el monitor", "Configuración correcta"],
        "referencias": [PEND_REF],
    },
})

ENRIQUECIMIENTO.update({
    # ===== Mecánica =====
    "EEA-DC3-XBDPC-MEC-RSG-001": {
        "causas": ["Bordes afilados tras cortar metal", "Rebabas sin desbarbar", "Manipulación de piezas recién cortadas sin guantes"],
        "disparadores": ["Tocar una pieza recién cortada", "Pasar la mano por un borde sin desbarbar", "Montar una pieza con rebabas"],
        "consecuencias": ["Cortes en el personal", "Daño del cableado al rozar el borde", "Retrabajo por desbarbado posterior"],
        "medidas_preventivas": ["Desbarbar y pulir los bordes tras cada corte", "Usar guantes resistentes al corte", "Revisar los bordes antes del montaje"],
        "que_hacer": ["Detener el trabajo y atender la herida", "Desbarbar el borde causante", "Proteger los cables cercanos", "Registrar el incidente"],
        "inspeccion": ["Bordes desbarbados", "Sin rebabas en piezas montadas", "Personal con guantes"],
        "referencias": [REF_OSHA_MG],
    },
    "EEA-DC3-XBDPC-MEC-RSG-002": {
        "causas": ["Perforar o cortar sin aprobación conjunta", "No verificar el espacio trasero de la zona a perforar", "Desconocer cables o estructuras ocultas"],
        "disparadores": ["Taladrar sin revisar el reverso", "Cortar una zona con cableado oculto", "Perforar sin coordinación con Avionica"],
        "consecuencias": ["Daño de cableado o estructura", "Perforación en zona indebida", "Retrabajo y retraso"],
        "medidas_preventivas": ["Obtener aprobación antes de perforar o cortar", "Revisar el reverso y la cercanía de cables", "Marcar y verificar la zona de corte"],
        "que_hacer": ["Detener la perforación o corte", "Inspeccionar el daño causado", "Reparar el cableado o estructura afectada", "Coordinar la nueva zona con los responsables"],
        "inspeccion": ["Aprobación registrada", "Reverso verificado", "Sin daño en cables ni estructura"],
        "referencias": [REF_OSHA_MG, REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-MEC-RSG-003": {
        "causas": ["Intervenir estructura primaria sin aprobación escrita", "Modificar una pieza estructural sin evaluación", "Desconocer la clasificación de la estructura"],
        "disparadores": ["Cortar o taladrar una pieza primaria", "Retirar una fijación estructural", "Modificar una pieza sin autorización"],
        "consecuencias": ["Pérdida de integridad estructural", "Riesgo para la seguridad del montaje", "Rechazo de la modificación"],
        "medidas_preventivas": ["No intervenir estructura primaria sin aprobación escrita", "Identificar y clasificar la estructura antes de intervenir", "Consultar a Supervisión y Mecánica"],
        "que_hacer": ["Detener la intervención", "Reportar la modificación no autorizada", "Evaluar el daño con los responsables", "Definir la corrección antes de continuar"],
        "inspeccion": ["Sin intervención no autorizada", "Estructura primaria identificada", "Aprobación escrita disponible"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-MEC-RSG-004": {
        "causas": ["Cortar o taladrar cerca del cableado de Avionica", "No proteger los mazos durante el trabajo", "Desplazar cables sin coordinación"],
        "disparadores": ["Pasar una herramienta cerca de un mazo", "Generar virutas sobre el cableado", "Mover un mazo para acceder a la zona"],
        "consecuencias": ["Daño del aislamiento del cable", "Cortocircuito o señal intermitente", "Retrabajo de cableado"],
        "medidas_preventivas": ["Proteger los mazos antes de mecanizar", "Coordinar con Avionica las zonas de trabajo", "Aspirar las virutas de inmediato"],
        "que_hacer": ["Detener el mecanizado", "Inspeccionar el cableado afectado", "Reparar o sustituir el tramo dañado", "Coordinar con Avionica la reanudación"],
        "inspeccion": ["Mazos protegidos", "Sin virutas sobre el cableado", "Cableado íntegro tras el trabajo"],
        "referencias": [REF_FAA_AC_120_94],
    },
    "EEA-DC3-XBDPC-MEC-RSG-005": {
        "causas": ["Fabricar con dimensiones no confirmadas de Avionica", "Montaje previo a la confirmación de medidas", "Cambios de diseño no comunicados"],
        "disparadores": ["Fabricar un soporte sin las medidas finales", "Recibir una medida distinta a la usada", "Instalar sin verificar contra el componente real"],
        "consecuencias": ["Soporte que no ajusta", "Retrabajo de piezas", "Retraso y costo adicional"],
        "medidas_preventivas": ["Confirmar las dimensiones con Avionica antes de fabricar", "Verificar contra el componente real", "Congelar la versión del diseño"],
        "que_hacer": ["Detener la fabricación afectada", "Confirmar la medida correcta", "Ajustar o rehacer la pieza", "Documentar la medida final"],
        "inspeccion": ["Medidas confirmadas", "Pieza que ajusta", "Versión de diseño vigente"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-MEC-RSG-006": {
        "causas": ["Fijaciones sin apretar o sin fijador de rosca", "Vibración del entorno", "Montaje sin verificación de torque"],
        "disparadores": ["Vibrar el equipo durante una prueba", "Detectar tornillos flojos tras el uso", "Reapretar repetidamente una fijación"],
        "consecuencias": ["Aflojamiento progresivo", "Ruido y vibración", "Desalineación o caída del componente"],
        "medidas_preventivas": ["Apretar la tornillería al torque adecuado", "Usar fijador de rosca cuando aplique", "Verificar el apriete tras el montaje"],
        "que_hacer": ["Detener el uso", "Reapretar y verificar la alineación", "Revisar si hubo daño por vibración", "Documentar la fijación corregida"],
        "inspeccion": ["Tornillería firme", "Sin vibración ni juego", "Alineación dentro de tolerancia"],
        "referencias": [PEND_REF],
    },
})

ENRIQUECIMIENTO.update({
    # ===== Software =====
    "EEA-DC3-XBDPC-SW-RSG-001": {
        "causas": ["Versiones incompatibles entre sistema operativo, X-Plane 12 y aplicaciones", "Drivers o plugins desactualizados", "Mezcla de versiones sin control"],
        "disparadores": ["Actualizar un componente sin verificar compatibilidad", "Instalar un plugin que requiere otra versión", "Detectar un error solo al arrancar el simulador"],
        "consecuencias": ["Simulador que no arranca o falla", "Displays o mandos sin respuesta", "Retraso por reinstalación"],
        "medidas_preventivas": ["Registrar las versiones instaladas", "Verificar compatibilidad antes de actualizar", "Mantener un entorno base conocido"],
        "que_hacer": ["Registrar el error y la versión", "Revisar la matriz de compatibilidad", "Reinstalar o revertir la versión incompatible", "Probar el arranque completo"],
        "inspeccion": ["Versiones documentadas y compatibles", "Arranque correcto", "Sin conflictos de plugins"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SW-RSG-002": {
        "causas": ["Actualización sin respaldo previo", "Sin plan de rollback", "Actualización que corrompe la configuración"],
        "disparadores": ["Actualizar sin crear un punto de restauración", "Aplicar una actualización destructiva", "Perder la configuración tras actualizar"],
        "consecuencias": ["Pérdida de la configuración", "Simulador inoperante", "Tiempo de recuperación prolongado"],
        "medidas_preventivas": ["Crear respaldo antes de actualizar", "Documentar el procedimiento de rollback", "Probar la actualización en un entorno de prueba"],
        "que_hacer": ["Detener la actualización", "Restaurar el respaldo previo", "Verificar la configuración", "Reintentar con el procedimiento documentado"],
        "inspeccion": ["Respaldo realizado antes de actualizar", "Procedimiento de rollback documentado", "Configuración restaurada"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SW-RSG-003": {
        "causas": ["Software de fuente no oficial o sin licencia", "Licencia no verificada", "Descarga de sitios no confiables"],
        "disparadores": ["Instalar una aplicación sin verificar la fuente", "Usar una licencia dudosa", "Descargar un plugin de un sitio no oficial"],
        "consecuencias": ["Software con fallas o malware", "Problemas de cumplimiento", "Simulador comprometido"],
        "medidas_preventivas": ["Usar solo fuentes oficiales", "Verificar la licencia antes de instalar", "Mantener inventario de licencias"],
        "que_hacer": ["Desinstalar el software no verificado", "Obtener la versión oficial o licencia válida", "Revisar el sistema por seguridad", "Documentar la licencia"],
        "inspeccion": ["Software de fuentes oficiales", "Licencias verificadas", "Sin aplicaciones no autorizadas"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-SW-RSG-004": {
        "causas": ["Cable USB suelto o dañado", "Controlador Teensy mal instalado", "Puerto USB con interferencia o conflicto"],
        "disparadores": ["Mover el cable y perder la comunicación", "Desconectar y reconectar el USB", "Actualizar el driver de Teensy"],
        "consecuencias": ["Pérdida de comunicación con el hardware", "Mandos sin respuesta", "Interrupción del entrenamiento"],
        "medidas_preventivas": ["Asegurar el cable USB y su alivio de esfuerzo", "Instalar el driver correcto de Teensy", "Probar la comunicación antes de la sesión"],
        "que_hacer": ["Verificar el cable y el puerto USB", "Reinstalar el driver de Teensy", "Reconectar y probar la comunicación", "Registrar el error si persiste"],
        "inspeccion": ["Cable USB fijo y en buen estado", "Driver correcto", "Comunicación estable"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-SW-RSG-005": {
        "causas": ["Ventilación insuficiente del equipo", "Acumulación de polvo en disipadores", "Carga sostenida del sistema"],
        "disparadores": ["Ejecutar el simulador por tiempo prolongado", "Obstruir las rejillas de ventilación", "Detectar apagados por temperatura"],
        "consecuencias": ["Apagado o reinicio del equipo", "Daño térmico de componentes", "Interrupción del entrenamiento"],
        "medidas_preventivas": ["Mantener limpias las rejillas y ventiladores", "Asegurar espacio de ventilación", "Vigilar la temperatura durante sesiones largas"],
        "que_hacer": ["Apagar y dejar enfriar el equipo", "Limpiar disipadores y ventiladores", "Mejorar la ventilación", "Reanudar vigilando la temperatura"],
        "inspeccion": ["Ventilación despejada", "Ventiladores operativos", "Temperatura dentro de rango"],
        "referencias": [PEND_REF],
    },
})

ENRIQUECIMIENTO.update({
    # ===== Lógico =====
    "EEA-DC3-XBDPC-LOG-RSG-001": {
        "causas": ["Documentos no registrados al crearse", "Cambios sin actualizar el índice", "Versiones mezcladas sin control"],
        "disparadores": ["Buscar un documento y no encontrarlo", "Detectar dos versiones distintas del mismo documento", "Faltar un registro en el índice"],
        "consecuencias": ["Pérdida de trazabilidad", "Uso de documentos desactualizados", "Rechazo del expediente"],
        "medidas_preventivas": ["Registrar cada documento en el índice", "Versionar y fechar cada cambio", "Auditar el índice periódicamente"],
        "que_hacer": ["Registrar el documento faltante", "Corregir el índice", "Conciliar las versiones", "Verificar la trazabilidad"],
        "inspeccion": ["Índice completo y actualizado", "Versiones controladas", "Sin documentos sin registrar"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LOG-RSG-002": {
        "causas": ["Documento firmado o aprobado sin verificar", "Firma dudosa o no trazable", "Aprobación sin revisión"],
        "disparadores": ["Recibir un documento con firma dudosa", "Detectar una aprobación sin registro", "Faltar la firma del responsable"],
        "consecuencias": ["Documento sin validez", "Responsabilidad no trazable", "Rechazo en auditoría"],
        "medidas_preventivas": ["Verificar la firma y la facultad de quien aprueba", "Registrar la aprobación en el control documental", "Rechazar documentos sin firma válida"],
        "que_hacer": ["Retener el documento dudoso", "Solicitar la firma o aprobación válida", "Registrar la incidencia", "Actualizar el control documental"],
        "inspeccion": ["Firmas verificadas", "Aprobaciones registradas", "Sin documentos dudosos"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LOG-RSG-003": {
        "causas": ["Evidencia digital sin respaldo", "Almacenamiento en un solo dispositivo", "Archivos borrados o dañados"],
        "disparadores": ["Falla del dispositivo de almacenamiento", "Borrado accidental de un archivo", "No encontrar una evidencia digital"],
        "consecuencias": ["Pérdida de evidencia", "Trazabilidad incompleta", "Retrabajo de documentación"],
        "medidas_preventivas": ["Respaldar la evidencia en al menos dos ubicaciones", "Usar almacenamiento con integridad", "Verificar la recuperación de respaldos"],
        "que_hacer": ["Detener la escritura en el dispositivo afectado", "Intentar recuperar el respaldo", "Registrar la pérdida", "Reforzar el procedimiento de respaldo"],
        "inspeccion": ["Respaldos actualizados", "Recuperación verificada", "Evidencia íntegra"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-LOG-RSG-004": {
        "causas": ["Archivo físico sin sujeción antivuelco", "Estantería sin fijar", "Carpetas apiladas de forma inestable"],
        "disparadores": ["Volcar un estante por sobrepeso o empuje", "Mover una carpeta pesada de una zona alta", "Detectar estantes sin fijar a la pared"],
        "consecuencias": ["Caída de documentos y lesiones", "Daño del archivo físico", "Pérdida de expedientes"],
        "medidas_preventivas": ["Fijar los estantes con sujeción antivuelco", "Distribuir el peso en los niveles bajos", "No sobrecargar las repisas"],
        "que_hacer": ["Asegurar la zona y atender cualquier lesión", "Fijar o retirar el estante inestable", "Reorganizar el archivo", "Registrar el incidente"],
        "inspeccion": ["Estantes fijados", "Peso distribuido", "Sin riesgo de vuelco"],
        "referencias": [PEND_REF],
    },
})

ENRIQUECIMIENTO.update({
    # ===== Vuelo =====
    "EEA-DC3-XBDPC-VUE-RSG-001": {
        "causas": ["Mapeo de mandos incorrecto en el software", "Entrada conectada al pin equivocado", "DataRef asignado a la función incorrecta"],
        "disparadores": ["Mover un mando y observar otra respuesta", "Detectar un mando sin respuesta", "Reconfigurar sin verificar el mapeo"],
        "consecuencias": ["Control incorrecto durante la prueba", "Entrenamiento con mandos erróneos", "Resultados de prueba inválidos"],
        "medidas_preventivas": ["Verificar el mapeo antes de cada prueba", "Documentar la asignación de cada mando", "Probar cada control de forma individual"],
        "que_hacer": ["Registrar el mapeo incorrecto", "Corregir la asignación del mando", "Repetir la prueba del control", "Documentar el resultado"],
        "inspeccion": ["Mapeo verificado", "Cada mando responde a su función", "Sin funciones cruzadas"],
        "referencias": [REF_ARDUINO_MEGA],
    },
    "EEA-DC3-XBDPC-VUE-RSG-002": {
        "causas": ["Falla de un instrumento crítico durante la prueba", "Instrumento sin calibrar o dañado", "Señal del instrumento perdida"],
        "disparadores": ["Detectar un instrumento sin lectura en vuelo", "Observar una lectura errática", "Perder un instrumento durante una fase crítica"],
        "consecuencias": ["Prueba interrumpida", "Datos de prueba no confiables", "Retraso de la validación"],
        "medidas_preventivas": ["Verificar los instrumentos antes de la prueba", "Calibrar y probar cada instrumento", "Definir el procedimiento ante falla de instrumento"],
        "que_hacer": ["Registrar el instrumento y la fase de falla", "Interrumpir la prueba si es crítico", "Diagnosticar y reparar el instrumento", "Repetir la prueba"],
        "inspeccion": ["Instrumentos operativos antes de la prueba", "Lecturas estables", "Procedimiento de falla definido"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-VUE-RSG-003": {
        "causas": ["Datos de navegación no verificados", "Cartas o rutas desactualizadas", "Fuente de datos no confirmada"],
        "disparadores": ["Usar una ruta sin verificar la fuente", "Detectar una discrepancia en la navegación", "Cargar datos de navegación sin validar"],
        "consecuencias": ["Ruta simulada incorrecta", "Entrenamiento con datos falsos", "Resultados de prueba inválidos"],
        "medidas_preventivas": ["Verificar los datos de navegación antes de usarlos", "Usar solo fuentes confirmadas (AIP)", "Documentar la fuente de cada ruta"],
        "que_hacer": ["Detener la prueba con datos no verificados", "Confirmar la fuente correcta", "Corregir los datos de navegación", "Repetir la prueba"],
        "inspeccion": ["Datos de navegación verificados", "Fuente documentada", "Ruta coherente con la referencia"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-VUE-RSG-004": {
        "causas": ["Confundir la habilidad del piloto con el desempeño del equipo", "No aislar variables en la prueba", "Usar el desempeño humano como único criterio de aprobación"],
        "disparadores": ["Aprobar un equipo porque el piloto compensó un defecto", "No registrar datos objetivos de la prueba", "Evaluar solo la impresión del piloto"],
        "consecuencias": ["Defectos del equipo no detectados", "Aprobación sin evidencia técnica", "Resultados no reproducibles"],
        "medidas_preventivas": ["Definir criterios objetivos de aceptación", "Registrar datos del equipo, no solo del piloto", "Separar la evaluación del piloto de la del equipo"],
        "que_hacer": ["Registrar los datos objetivos de la prueba", "Revisar los criterios de aceptación", "Repetir la prueba con instrumentación adecuada", "Documentar el resultado técnico"],
        "inspeccion": ["Criterios objetivos definidos", "Datos del equipo registrados", "Evaluación técnica independiente"],
        "referencias": [PEND_REF],
    },
    "EEA-DC3-XBDPC-VUE-RSG-005": {
        "causas": ["Defectos críticos sin corregir que bloquean pruebas avanzadas", "Aceptar un defecto y avanzar de fase", "Falta de verificación de los prerequisitos"],
        "disparadores": ["Avanzar a una fase sin cerrar los defectos", "Detectar un defecto crítico en una prueba avanzada", "Repetir una prueba por un defecto previo"],
        "consecuencias": ["Pruebas avanzadas inválidas", "Acumulación de defectos", "Retraso en la validación"],
        "medidas_preventivas": ["Cerrar los defectos críticos antes de avanzar", "Verificar los prerequisitos de cada fase", "Registrar y priorizar los defectos"],
        "que_hacer": ["Detener las pruebas avanzadas", "Registrar y priorizar el defecto crítico", "Corregir y verificar el defecto", "Repetir la fase bloqueada"],
        "inspeccion": ["Defectos críticos cerrados", "Prerequisitos verificados", "Pruebas avanzadas válidas"],
        "referencias": [PEND_REF],
    },
})


# Referencias estructuradas para los 31 riesgos ampliados (R-*)
ENRIQUECIMIENTO.update({
    "R-EL-01": {"referencias": [REF_ARDUINO_MEGA, REF_FAA_AC_120_94]},
    "R-EL-02": {"referencias": [REF_ARDUINO_MEGA, REF_FAA_AC_120_94]},
    "R-EL-03": {"referencias": [REF_ARDUINO_MEGA]},
    "R-EL-04": {"referencias": [REF_ARDUINO_MEGA_STORE]},
    "R-EL-05": {"referencias": [REF_FAA_AC_120_94]},
    "R-EL-06": {"referencias": [REF_FAA_AC_120_94, REF_FAA_AC_25_26]},
    "R-EL-07": {"referencias": [REF_FAA_AC_120_94]},
    "R-EL-08": {"referencias": [REF_ARDUINO_MEGA_STORE]},
    "R-EL-09": {"referencias": [REF_OSHA_1910_147]},
    "R-EL-10": {"referencias": [REF_FAA_AC_120_94]},
    "R-EL-11": {"referencias": [REF_FAA_AC_120_94]},
    "R-EL-12": {"referencias": [REF_ARDUINO_MEGA]},
    "R-EL-13": {"referencias": [REF_ARDUINO_MEGA, REF_ARDUINO_MEGA_STORE]},
    "R-EL-14": {"referencias": [REF_ARDUINO_MEGA]},
    "R-EL-15": {"referencias": [REF_OSHA_1910_147]},
    "R-MC-01": {"referencias": [PEND_REF]},
    "R-MC-02": {"referencias": [PEND_REF]},
    "R-MC-03": {"referencias": [PEND_REF]},
    "R-MC-04": {"referencias": [REF_OSHA_MG]},
    "R-MC-05": {"referencias": [REF_OSHA_MG]},
    "R-MC-06": {"referencias": [PEND_REF]},
    "R-MC-07": {"referencias": [PEND_REF]},
    "R-MC-08": {"referencias": [REF_FAA_AC_120_94]},
    "R-MC-09": {"referencias": [REF_OSHA_MG]},
    "R-SW-01": {"referencias": [REF_ARDUINO_MEGA]},
    "R-SW-02": {"referencias": [REF_ARDUINO_MEGA]},
    "R-SW-03": {"referencias": [REF_ARDUINO_MEGA]},
    "R-SW-04": {"referencias": [PEND_REF]},
    "R-SW-05": {"referencias": [REF_ARDUINO_MEGA]},
    "R-SW-06": {"referencias": [REF_ARDUINO_MEGA]},
    "R-SW-07": {"referencias": [PEND_REF]},
})


# ---------------------------------------------------------------------------
# Materiales (listas de material por módulo M01–M05)
# ---------------------------------------------------------------------------
# Estados permitidos para cada material (campo "estado"):
#   Existente · Recuperable · Por reparar · Por comprar · Pendiente de verificar
#
# Regla de veracidad: no se inventan existencias, cantidades, longitudes,
# calibres ni especificaciones. Los valores no confirmados se marcan con
# cantidad=None (la interfaz muestra "Pendiente de verificar") y el estado
# "Pendiente de verificar" cuando no se conoce la situación de compra.
# ---------------------------------------------------------------------------
ESTADOS_MATERIAL = ["Existente", "Recuperable", "Por reparar", "Por comprar",
                    "Pendiente de verificar"]


def _m(id_, nombre, grupo, cantidad, unidad, especificacion, estado, observacion=""):
    """Crea un ítem de material de forma compacta y estructurada."""
    return {
        "id": id_, "nombre": nombre, "grupo": grupo,
        "cantidad": cantidad,  # int/float cuando está confirmado; None = Pendiente de verificar
        "unidad": unidad, "especificacion": especificacion,
        "estado": estado, "observacion": observacion,
    }


MATERIALES = [
    {
        "id": "M01", "nombre": "Cabina, estructura física y mandos de vuelo",
        "descripcion": ("Inventario y recuperación de la cabina existente y de los mandos "
                        "originales reutilizables, con los materiales, herramientas y consumibles "
                        "para limpiar, desoxidar, reparar, pintar e instalar."),
        "items": [
            # --- Estructura y cabina ---
            _m("M01-001", "Fuselaje Douglas DC-3 (XB-DPC)", "Estructura y cabina", 1, "unidad",
               "Cabina y estructura original del avión; objeto del proyecto.", "Existente",
               "Incluye toda la estructura a inspeccionar, limpiar y recuperar."),
            _m("M01-002", "Paneles de cabina (chapas y carenados)", "Estructura y cabina", None, "unidad",
               "Paneles desmontables originales.", "Recuperable",
               "Verificar el estado de cada panel; conservar los reutilizables."),
            _m("M01-003", "Asiento del piloto", "Estructura y cabina", None, "unidad",
               "Asiento original de la cabina.", "Recuperable",
               "Reutilizar si el estado estructural lo permite."),
            _m("M01-004", "Asiento del copiloto", "Estructura y cabina", None, "unidad",
               "Asiento original de la cabina.", "Recuperable",
               "Reutilizar si el estado estructural lo permite."),
            _m("M01-005", "Consola o pedestal central", "Estructura y cabina", None, "unidad",
               "Pedestal central de la cabina.", "Pendiente de verificar",
               "Confirmar si existe en cabina y su estado."),
            # --- Mandos de vuelo ---
            _m("M01-006", "Volante (yoke) original", "Mandos de vuelo", None, "unidad",
               "Mando de control de alabeo y cabeceo.", "Recuperable",
               "Verificar cuántos volantes hay y su estado de conservación."),
            _m("M01-007", "Columna de control", "Mandos de vuelo", None, "unidad",
               "Columna que transmite el movimiento del volante.", "Recuperable",
               "Inspeccionar articulaciones y herrajes."),
            _m("M01-008", "Pedales de timón (rudder)", "Mandos de vuelo", None, "unidad",
               "Pedales originales del timón de dirección.", "Recuperable",
               "Revisar mecanismo, cables y resortes."),
            _m("M01-009", "Palanca o actuador de flaps", "Mandos de vuelo", None, "unidad",
               "Mando de los flaps.", "Pendiente de verificar",
               "Confirmar presencia y estado; puede requerir reparación."),
            _m("M01-010", "Mecanismo de tren de aterrizaje", "Mandos de vuelo", None, "unidad",
               "Palanca o mecanismo de tren.", "Pendiente de verificar",
               "Confirmar si se reutiliza el mecanismo original."),
            _m("M01-011", "Cables y mecanismos de transmisión de mandos", "Mandos de vuelo", None, "unidad",
               "Cables, poleas y soportes de transmisión.", "Recuperable",
               "Verificar estado, corrosión y tensión de cada tramo."),
            _m("M01-012", "Soportes y herrajes de montaje de mandos", "Mandos de vuelo", None, "unidad",
               "Herrajes y soportes de fijación.", "Pendiente de verificar",
               "Inventariar piezas presentes y faltantes."),
            # --- Herramientas ---
            _m("M01-013", "Juego de llaves (boca, corona y cubo)", "Herramientas", None, "juego",
               "Medidas métricas y estándar.", "Por comprar",
               "Adquirir conforme a la tornillería encontrada."),
            _m("M01-014", "Destornilladores (plano, Phillips y Torx)", "Herramientas", None, "juego",
               "Varios tamaños.", "Por comprar", ""),
            _m("M01-015", "Alicates (punta, corte y presión)", "Herramientas", None, "juego",
               "Para sujeción y corte de cables y chapa.", "Por comprar", ""),
            _m("M01-016", "Cepillo de alambre / cepillo metálico", "Herramientas", None, "unidad",
               "Para remoción de óxido superficial.", "Por comprar", ""),
            _m("M01-017", "Lijas de varios granos (80 a 400)", "Herramientas", None, "paquete",
               "Granos para desbastar y preparar superficie.", "Por comprar",
               "Grano a confirmar según el acabado requerido."),
            _m("M01-018", "Taladro y brocas para metal", "Herramientas", None, "unidad",
               "Brocas para metal de medidas por definir.", "Por comprar", ""),
            # --- Consumibles y restauración ---
            _m("M01-019", "Trapos / paños de limpieza", "Consumibles", None, "paquete",
               "Paños sin pelusa.", "Por comprar", ""),
            _m("M01-020", "Desengrasante / limpiador industrial", "Consumibles", None, "litro",
               "Producto por definir según la superficie a limpiar.", "Por comprar",
               "Verificar compatibilidad con el material."),
            _m("M01-021", "Removedor o convertidor de óxido", "Consumibles", None, "litro",
               "Producto para tratamiento anticorrosivo.", "Por comprar",
               "Seleccionar según el grado de corrosión."),
            _m("M01-022", "WD-40 / lubricante penetrante", "Consumibles", None, "unidad",
               "Aflojar tornillería y proteger temporalmente.", "Por comprar", ""),
            _m("M01-023", "Masilla o epóxico de relleno para metal", "Consumibles", None, "unidad",
               "Relleno de picaduras y pequeñas imperfecciones.", "Por comprar", ""),
            # --- Pintura y protección ---
            _m("M01-024", "Imprimación anticorrosiva", "Pintura y protección", None, "litro",
               "Base anticorrosiva para metal.", "Por comprar",
               "Tipo y color por confirmar."),
            _m("M01-025", "Pintura de acabado", "Pintura y protección", None, "litro",
               "Acabado para cabina y mandos.", "Por comprar",
               "Color y acabado por confirmar."),
            _m("M01-026", "Thinner / diluyente", "Pintura y protección", None, "litro",
               "Diluyente compatible con la pintura elegida.", "Por comprar", ""),
            _m("M01-027", "Protección anticorrosiva temporal", "Pintura y protección", None, "unidad",
               "Para zonas no pintadas durante el montaje.", "Por comprar", ""),
        ],
    },
    {
        "id": "M02", "nombre": "Panel e instrumentación",
        "descripcion": ("Instrumentación principalmente virtual. Considera dos monitores "
                        "ordinarios y un monitor táctil, con sus conexiones, alimentación, "
                        "soportes y materiales de prueba pantalla por pantalla."),
        "items": [
            _m("M02-001", "Monitor de instrumentos 1", "Pantallas", 1, "unidad",
               "Monitor ordinario para instrumentación.", "Por comprar",
               "Tamaño y resolución por confirmar."),
            _m("M02-002", "Monitor de instrumentos 2", "Pantallas", 1, "unidad",
               "Monitor ordinario para instrumentación.", "Por comprar",
               "Tamaño y resolución por confirmar."),
            _m("M02-003", "Monitor táctil", "Pantallas", 1, "unidad",
               "Monitor con pantalla táctil (por ejemplo, para GTN 750).", "Por comprar",
               "Compatibilidad táctil por confirmar."),
            _m("M02-004", "Cable de video por monitor", "Conexiones", 3, "unidad",
               "Interfaz por confirmar (HDMI, DisplayPort, DVI o VGA) según puertos de PC y monitores.",
               "Por comprar",
               "No asumir el tipo de conector sin verificar los puertos."),
            _m("M02-005", "Cable de alimentación por monitor", "Conexiones", 3, "unidad",
               "Cable de energía de cada monitor.", "Por comprar", ""),
            _m("M02-006", "Multicontacto / regleta eléctrica", "Conexiones", None, "unidad",
               "Distribución de alimentación para monitores y equipos.", "Por comprar",
               "Capacidad y número de salidas por confirmar."),
            _m("M02-007", "Extensión eléctrica", "Conexiones", None, "unidad",
               "Extensión hacia la zona de la cabina.", "Por comprar",
               "Longitud y calibre por confirmar."),
            _m("M02-008", "Soporte o brazo de montaje de monitores", "Soporte y fijación", None, "unidad",
               "Soporte para fijar los tres monitores al panel.", "Por comprar",
               "Diseño según la estructura de la cabina."),
            _m("M02-009", "Tornillería y anclaje para soportes", "Soporte y fijación", None, "juego",
               "Tornillos, tuercas y anclajes.", "Por comprar",
               "Medidas por definir según el soporte."),
            _m("M02-010", "Adaptador de video", "Conexiones", None, "unidad",
               "Convertidor entre interfaces si los puertos no coinciden.", "Pendiente de verificar",
               "Comprar solo si se confirma la necesidad."),
            _m("M02-011", "Carta / patrón de prueba de color y grilla", "Pruebas", None, "unidad",
               "Imagen de prueba para verificar cada pantalla.", "Pendiente de verificar",
               "Puede ser una imagen o software; por confirmar."),
            _m("M02-012", "Multímetro digital", "Herramientas", 1, "unidad",
               "Para verificar alimentación y continuidad.", "Por comprar", ""),
            _m("M02-013", "Cinta aislante y bridas", "Herramientas", None, "paquete",
               "Para organización del cableado.", "Por comprar", ""),
        ],
    },
    {
        "id": "M03", "nombre": "Electrónica, control, sensorización, distribución eléctrica y cableado",
        "descripcion": ("Electrónica de control y sensores: Arduino Mega, Teensy (opcional), "
                        "sensores, potenciómetros, interruptores, botones, displays de 7 segmentos, "
                        "componentes pasivos y activos, alimentación, protecciones, cableado y "
                        "herramientas. Los valores se determinan por el diseño eléctrico, no por estimación."),
        "items": [
            # --- Microcontroladores y módulos ---
            _m("M03-001", "Arduino Mega 2560", "Microcontroladores", 1, "unidad",
               "ATmega2560 · 54 pines digitales (15 PWM) · 16 analógicas · 4 UART.", "Por comprar",
               "Corriente por pin ~20 mA recomendado / 40 mA máx.; cargas mayores requieren driver o fuente externa."),
            _m("M03-002", "Teensy (placa opcional)", "Microcontroladores", None, "unidad",
               "Modelo por definir; se evalúa solo si Arduino Mega no cubre las necesidades.", "Pendiente de verificar",
               "No se da por requerido; decidir tras el diseño de entradas/salidas."),
            _m("M03-003", "Módulo shield / expansión", "Microcontroladores", None, "unidad",
               "Tarjeta de expansión si las conexiones lo exigen.", "Pendiente de verificar", ""),
            # --- Sensores y entradas ---
            _m("M03-004", "Potenciómetro rotativo (ejes de mandos)", "Sensores y entradas", None, "unidad",
               "Valor y tipo (p. ej. 10 kΩ lineal) por confirmar según el mando.", "Por comprar",
               "Confirmar recorrido y valor por mando."),
            _m("M03-005", "Potenciómetro deslizante (palancas)", "Sensores y entradas", None, "unidad",
               "Valor y recorrido por confirmar.", "Por comprar", ""),
            _m("M03-006", "Sensor de posición / encoder", "Sensores y entradas", None, "unidad",
               "Tipo por definir según la señal requerida.", "Pendiente de verificar", ""),
            _m("M03-007", "Final de carrera / microinterruptor", "Sensores y entradas", None, "unidad",
               "Para detección de posición de tren, flaps o topes.", "Por comprar", ""),
            _m("M03-008", "Interruptores de palanca (toggle)", "Sensores y entradas", None, "unidad",
               "Cantidad y número de posiciones por definir.", "Por comprar", ""),
            _m("M03-009", "Botones pulsadores", "Sensores y entradas", None, "unidad",
               "Cantidad por definir.", "Por comprar", ""),
            _m("M03-010", "Interruptor rotativo / selector", "Sensores y entradas", None, "unidad",
               "Si se requiere para modos; por confirmar.", "Pendiente de verificar", ""),
            # --- Componentes pasivos ---
            _m("M03-011", "Resistencias (surtido)", "Componentes pasivos", None, "paquete",
               "Valores y potencia por calcular según cada circuito.", "Por comprar",
               "No asignar valores sin el cálculo del circuito."),
            _m("M03-012", "Condensadores cerámicos", "Componentes pasivos", None, "paquete",
               "Valores por calcular (desacople y filtrado).", "Por comprar", ""),
            _m("M03-013", "Condensadores electrolíticos", "Componentes pasivos", None, "paquete",
               "Valores por calcular (alimentación y filtrado).", "Por comprar", ""),
            # --- Componentes activos ---
            _m("M03-014", "Diodos de protección / rectificadores", "Componentes activos", None, "paquete",
               "Tipo (p. ej. 1N4007) y cantidad por calcular.", "Por comprar", ""),
            _m("M03-015", "Transistores de conmutación / driver", "Componentes activos", None, "paquete",
               "Tipo (p. ej. 2N2222 u otro driver) por calcular según la carga.", "Por comprar",
               "Seleccionar conforme a corriente y tensión de carga."),
            _m("M03-016", "Regulador de voltaje / convertidor DC-DC", "Componentes activos", None, "unidad",
               "Tensión de entrada/salida por confirmar.", "Por comprar",
               "Dimensionar según fuentes y consumo."),
            # --- Indicadores y actuadores ---
            _m("M03-017", "Display de 7 segmentos", "Indicadores y actuadores", None, "unidad",
               "Cantidad, tamaño y driver por definir.", "Por comprar", ""),
            _m("M03-018", "LED indicadores", "Indicadores y actuadores", None, "paquete",
               "Colores y corriente por definir.", "Por comprar", ""),
            _m("M03-019", "Servo / actuador", "Indicadores y actuadores", None, "unidad",
               "Solo si un mando lo requiere; por confirmar.", "Pendiente de verificar", ""),
            # --- Alimentación y distribución ---
            _m("M03-020", "Fuente de alimentación regulada", "Alimentación", None, "unidad",
               "Tensión y corriente por calcular según la carga total.", "Por comprar",
               "Dimensionar con margen; balancear las cargas."),
            _m("M03-021", "Fuente o conversor USB para Arduino", "Alimentación", 1, "unidad",
               "Alimentación de la placa; tipo por confirmar.", "Por comprar", ""),
            _m("M03-022", "Regleta de distribución (bornes)", "Alimentación", None, "unidad",
               "Para repartir alimentación a los ramales.", "Por comprar", ""),
            _m("M03-023", "Barra o borne de tierra común", "Alimentación", None, "unidad",
               "Punto único de referencia de tierra.", "Por comprar", ""),
            # --- Protecciones ---
            _m("M03-024", "Fusibles (surtido de valores)", "Protecciones", None, "paquete",
               "Valor por ramal por calcular.", "Por comprar",
               "No usar un valor mayor al que soporta el conductor."),
            _m("M03-025", "Portafusibles", "Protecciones", None, "unidad",
               "Soportes para los fusibles.", "Por comprar", ""),
            _m("M03-026", "Breaker / interruptor de protección", "Protecciones", None, "unidad",
               "Si se requiere protección rearmable; por confirmar.", "Pendiente de verificar", ""),
            # --- Cableado ---
            _m("M03-027", "Cable Ethernet (p. ej. Steren) para señales de control", "Cableado", None, "unidad",
               "Conductores internos para señales de control de baja corriente.", "Por comprar",
               "No usar los hilos para cargas de potencia sin el cálculo correspondiente."),
            _m("M03-028", "Cable de alimentación (potencia)", "Cableado", None, "metro",
               "Calibre AWG por calcular según carga, corriente y longitud.", "Por comprar",
               "Registrar AWG y longitud estimada por tramo."),
            _m("M03-029", "Cable de señal blindado", "Cableado", None, "metro",
               "Blindaje y conexión a tierra por definir.", "Pendiente de verificar", ""),
            # --- Conectores y terminales ---
            _m("M03-030", "Terminales de crimpado", "Conectores y terminales", None, "paquete",
               "Tipo (hembra/macho, ojal) por definir.", "Por comprar", ""),
            _m("M03-031", "Conectores desmontables", "Conectores y terminales", None, "unidad",
               "Para puntos que requieren mantenimiento o reemplazo.", "Por comprar",
               "Señales soldadas salvo donde se requiera desconectar."),
            _m("M03-032", "Bornera / clemas de conexión", "Conectores y terminales", None, "unidad",
               "Conexión de cableado en tablero.", "Por comprar", ""),
            # --- Herramientas de soldadura ---
            _m("M03-033", "Cautín / soldador de estaño", "Herramientas de soldadura", 1, "unidad",
               "Soldador de punta fina.", "Por comprar", ""),
            _m("M03-034", "Estaño para soldar (carrete)", "Herramientas de soldadura", None, "unidad",
               "Aleación y diámetro por confirmar.", "Por comprar", ""),
            _m("M03-035", "Flux / pasta para soldar", "Herramientas de soldadura", None, "unidad",
               "Fundente para mejorar la soldadura.", "Por comprar", ""),
            _m("M03-036", "Malla desoldadora / extractor de estaño", "Herramientas de soldadura", None, "unidad",
               "Para correcciones y retrabajo.", "Por comprar", ""),
            # --- Herramientas de medición ---
            _m("M03-037", "Multímetro digital", "Herramientas de medición", 1, "unidad",
               "Medición de tensión, corriente, continuidad y resistencia.", "Por comprar", ""),
            _m("M03-038", "Pinza amperimétrica", "Herramientas de medición", None, "unidad",
               "Solo si se requiere medir corriente sin abrir el circuito.", "Pendiente de verificar", ""),
            # --- Prototipado ---
            _m("M03-039", "Protoboard (breadboard)", "Prototipado", None, "unidad",
               "Para prototipos antes del armado definitivo.", "Por comprar", ""),
            _m("M03-040", "Cables puente (jumpers)", "Prototipado", None, "paquete",
               "Para conexiones temporales en protoboard.", "Por comprar", ""),
            # --- Consumibles ---
            _m("M03-041", "Cinta aislante", "Consumibles", None, "unidad",
               "Aislamiento de conexiones.", "Por comprar", ""),
            _m("M03-042", "Tubo termocontráctil (heat shrink)", "Consumibles", None, "paquete",
               "Diversos diámetros.", "Por comprar", ""),
            _m("M03-043", "Bridas / abrazaderas para cables", "Consumibles", None, "paquete",
               "Organización y fijación del arnés.", "Por comprar", ""),
            _m("M03-044", "Grommets / pasacables de protección", "Consumibles", None, "paquete",
               "Protección del cableado en bordes y paneles.", "Por comprar", ""),
        ],
    },
    {
        "id": "M04", "nombre": "Computación, simulación, aviónica virtual e interfaces",
        "descripcion": ("Computadora, software, licencias, integración con X-Plane 12, joystick y "
                        "hardware de interfaz, panel de autopiloto (CRS, HDG, FD, AP, ALT, VS, ILS, BC), "
                        "arranque de dos motores, iluminación LED de cabina y audio del simulador. "
                        "Las herramientas se verifican antes de fijarse como arquitectura definitiva."),
        "items": [
            _m("M04-001", "Computadora de simulación (PC)", "Computación", 1, "unidad",
               "Especificaciones por definir según requisitos de X-Plane 12.", "Por comprar",
               "Verificar requisitos mínimos/recomendados de X-Plane 12."),
            _m("M04-002", "Tarjeta gráfica / salida multi-monitor", "Computación", None, "unidad",
               "Capacidad de tres salidas de video por confirmar.", "Pendiente de verificar",
               "Confirmar si la PC admite los tres monitores o requiere adaptador."),
            _m("M04-003", "X-Plane 12", "Software y licencias", 1, "licencia",
               "Versión, requisitos y licencia por verificar.", "Por comprar",
               "Confirmar versión y términos de licencia antes de adquirir."),
            _m("M04-004", "Arduino IDE", "Software y licencias", 1, "unidad",
               "Herramienta gratuita de programación; versión por confirmar.", "Pendiente de verificar",
               "Verificar versión compatible con las placas."),
            _m("M04-005", "MobiFlight", "Software y licencias", None, "unidad",
               "Herramienta de interfaz; compatibilidad y necesidad por verificar.", "Pendiente de verificar",
               "No se asume requerido ni compatible sin verificación."),
            _m("M04-006", "XPLDirect / XPL Pro", "Software y licencias", None, "unidad",
               "Puente de comunicación con X-Plane; usar uno según lo verificado.", "Pendiente de verificar",
               "No duplicar software sin confirmar la arquitectura."),
            _m("M04-007", "Joystick / yoke USB", "Interfaces y control", None, "unidad",
               "Mando de vuelo; modelo y compatibilidad por confirmar.", "Por comprar", ""),
            _m("M04-008", "Pedales USB", "Interfaces y control", None, "unidad",
               "Pedales adicionales si los mandos originales no se sensorizan.", "Pendiente de verificar", ""),
            _m("M04-009", "Hub USB", "Interfaces y control", None, "unidad",
               "Para concentrar los mandos y controladores.", "Por comprar",
               "Con alimentación si las cargas lo requieren."),
            _m("M04-010", "Cables USB", "Interfaces y control", None, "unidad",
               "Conexión de mandos y controladores a la PC.", "Por comprar", ""),
            _m("M04-011", "Panel de autopiloto (físico)", "Autopiloto", 1, "unidad",
               "Controles CRS, HDG, FD, AP, ALT, VS, ILS, BC.", "Por comprar",
               "Puede construirse con interruptores, encoders y displays."),
            _m("M04-012", "Encoders / potenciómetros de autopiloto", "Autopiloto", None, "unidad",
               "Para CRS, HDG, ALT y VS; tipo por definir.", "Por comprar", ""),
            _m("M04-013", "Botones de modo de autopiloto", "Autopiloto", None, "unidad",
               "FD, AP, ALT, VS, ILS, BC.", "Por comprar", ""),
            _m("M04-014", "Display de 7 segmentos para autopiloto", "Autopiloto", None, "unidad",
               "Para mostrar CRS, HDG y ALT; cantidad por definir.", "Por comprar", ""),
            _m("M04-015", "Interruptores de 2/3 posiciones (arranque de motores)", "Encendido de motores", None, "unidad",
               "Para simular el arranque de dos motores.", "Por comprar", ""),
            _m("M04-016", "Botones de arranque de motor", "Encendido de motores", None, "unidad",
               "Pulsadores del proceso de arranque.", "Por comprar", ""),
            _m("M04-017", "Luces LED de cabina", "Audio e iluminación", None, "unidad",
               "Iluminación LED independiente de la cabina.", "Por comprar",
               "Tensión y consumo por confirmar."),
            _m("M04-018", "Driver / dimmer de LED", "Audio e iluminación", None, "unidad",
               "Control de intensidad si se requiere.", "Pendiente de verificar", ""),
            _m("M04-019", "Altavoces (bocinas) del simulador", "Audio e iluminación", None, "unidad",
               "Sonido claro y con volumen suficiente.", "Por comprar", ""),
            _m("M04-020", "Amplificador de audio", "Audio e iluminación", None, "unidad",
               "Solo si los altavoces lo requieren.", "Pendiente de verificar", ""),
            _m("M04-021", "Cables y conectores de audio", "Audio e iluminación", None, "unidad",
               "Conexión de audio entre PC y altavoces.", "Por comprar", ""),
            _m("M04-022", "Interfaz de comunicación con X-Plane", "Interfaces y control", None, "unidad",
               "Protocolo y DataRefs/Commands por verificar.", "Pendiente de verificar",
               "Diseñar según lo que X-Plane 12 soporta realmente."),
            _m("M04-023", "Licencia / activación de software adicional", "Software y licencias", None, "unidad",
               "Software complementario solo si se confirma necesario.", "Pendiente de verificar", ""),
            _m("M04-024", "Destornilladores y herramientas menores", "Herramientas", None, "juego",
               "Para montaje de la PC y los mandos.", "Por comprar", ""),
        ],
    },
    {
        "id": "M05", "nombre": "Visualización e iluminación exterior",
        "descripcion": ("Solo la luz de baliza (beacon) exterior y los materiales para su "
                        "alimentación, control, instalación, cableado, protección y prueba. "
                        "No se declaran requisitos de aeronavegabilidad; es un simulador terrestre."),
        "items": [
            _m("M05-001", "Luz de baliza exterior (beacon)", "Iluminación exterior", 1, "unidad",
               "Baliza roja para simulador terrestre (sin certificación).", "Por comprar",
               "Tensión y tipo por confirmar."),
            _m("M05-002", "Fuente / adaptador de la baliza", "Alimentación", None, "unidad",
               "Tensión y corriente por confirmar según la lámpara.", "Por comprar", ""),
            _m("M05-003", "Interruptor / control de encendido de la baliza", "Control", None, "unidad",
               "Encendido y apagado de la baliza.", "Por comprar", ""),
            _m("M05-004", "Cableado de alimentación de la baliza", "Cableado", None, "metro",
               "Calibre por calcular según carga y distancia.", "Por comprar",
               "Registrar AWG y longitud estimada."),
            _m("M05-005", "Fusible de protección del circuito", "Protección", None, "unidad",
               "Valor por calcular según la carga.", "Por comprar", ""),
            _m("M05-006", "Soporte y fijación de la baliza", "Instalación", None, "unidad",
               "Fijación a la estructura exterior.", "Por comprar",
               "Diseño según la ubicación de montaje."),
            _m("M05-007", "Sello / junta contra intemperie", "Instalación", None, "unidad",
               "Protección de la instalación exterior.", "Por comprar", ""),
            _m("M05-008", "Conectores y terminales", "Instalación", None, "paquete",
               "Conexión del circuito de la baliza.", "Por comprar", ""),
            _m("M05-009", "Multímetro digital", "Herramientas", 1, "unidad",
               "Verificación del circuito de la baliza.", "Por comprar", ""),
            _m("M05-010", "Cinta aislante y termocontráctil", "Herramientas", None, "paquete",
               "Aislamiento y protección de conexiones.", "Por comprar", ""),
        ],
    },
]


# ---------------------------------------------------------------------------
# Gobernanza y responsabilidades (estructura de roles, perfiles y reglas)
# ---------------------------------------------------------------------------
# Regla de veracidad: no se inventan credenciales, grados académicos ni
# certificaciones. Solo se muestran nombres y cargos confirmados.
# ---------------------------------------------------------------------------
GOBERNANZA = {
    "titulo": "Responsables",
    "intro": ("Estructura de responsabilidades, roles, perfil de liderazgo y reglas "
              "para conformar equipos del Proyecto AATD DC3."),
    "estructura": {
        "titulo": "Estructura de responsabilidades",
        "niveles": [
            {"nivel": "Dirección", "miembros": [
                {"nombre": "Haniel Fierros", "cargo": "CEO Eben Ezer Aviation"}]},
            {"nivel": "Gestión y revisión", "miembros": [
                {"nombre": "Misael Ramos", "cargo": "Ingeniería de Operaciones"},
                {"nombre": "Roxana Méndez", "cargo": "Supervisor de Planeación"}]},
            {"nivel": "Ejecución", "miembros": [
                {"nombre": "", "cargo": "Líderes de equipo"}]},
        ],
        "apoyo": {
            "titulo": "Apoyo técnico",
            "miembros": [{"nombre": "", "cargo": "Profesores del IPN"}],
        },
    },
    "roles": [
        {
            "id": "ceo", "icono": "👔", "nombre": "Haniel Fierros",
            "cargo": "CEO Eben Ezer Aviation", "organizacion": "Eben Ezer Aviation",
            "rol": "Patrocinador principal y responsable general del proyecto",
            "resumen": "Dirige la dirección general del proyecto, la coordinación de recursos y la autorización; es el enlace principal entre EEA y el IPN.",
            "responsabilidades": [
                "Dirigir la dirección general del proyecto, la coordinación de recursos y la autorización del proyecto.",
                "Actuar como enlace principal entre EEA y el IPN.",
                "Coordinar a las partes participantes y resolver los asuntos que requieran decisión de la dirección.",
                "Aprobar la ejecución general del proyecto y los asuntos relevantes.",
                "Revisar y tomar las decisiones finales de aceptación/aprobación.",
            ],
            "limite": "Aprobación final de la entrega general del proyecto. El trabajo técnico específico recibe el apoyo profesional de los responsables correspondientes y de los profesores del IPN.",
            "entregables": ["Decisión final de aceptación/aprobación del proyecto."],
            "reporta_a": "— (máxima autoridad del proyecto)",
            "comunica_con": ["EEA", "IPN", "Equipos del proyecto"],
        },
        {
            "id": "ingenieria-operaciones", "icono": "🔎", "nombre": "Misael Ramos",
            "cargo": "Ingeniería de Operaciones", "organizacion": "Eben Ezer Aviation",
            "rol": "Responsable de calidad, documentación técnica y revisión de entregables; principal colaborador del CEO",
            "resumen": "Revisa los resultados, manuales, documentos de entrega y expedientes; audita la evidencia y da seguimiento a las correcciones.",
            "responsabilidades": [
                "Revisar los resultados finales del proyecto, los manuales, los documentos de entrega y los expedientes de responsabilidades del personal.",
                "Revisar los registros del proyecto, la evidencia de ejecución y las auditorías relacionadas.",
                "Verificar la integridad, consistencia y trazabilidad de los entregables.",
                "Cuando se detecten defectos, plantear requisitos de corrección y dar seguimiento hasta su cierre.",
                "Reportar al CEO los resultados de la revisión y los asuntos relevantes.",
            ],
            "limite": "No sustituye la autoridad de aprobación final del proyecto del CEO.",
            "entregables": ["Informe de revisión/auditoría.", "Requisitos de corrección con seguimiento."],
            "reporta_a": "CEO (Haniel Fierros)",
            "comunica_con": ["CEO", "Supervisor de Planeación", "Líderes de equipo"],
        },
        {
            "id": "supervisor-planeacion", "icono": "📋", "nombre": "Roxana Méndez",
            "cargo": "Supervisor de Planeación", "organizacion": "Eben Ezer Aviation",
            "rol": "Responsable de la planeación, el avance y la coordinación entre equipos del proyecto",
            "resumen": "Supervisa la ejecución, mantiene el cronograma Gantt y coordina las prioridades y el trabajo entre equipos.",
            "responsabilidades": [
                "Supervisar que los equipos ejecuten conforme a objetivos, tiempos y plan.",
                "Mantener y actualizar el cronograma Gantt del proyecto.",
                "Recibir de todos los líderes de equipo los reportes de avance, el estado de las tareas, las necesidades de recursos, los riesgos y las fechas estimadas de término.",
                "Identificar desviaciones de avance, dependencias entre tareas y riesgos de retraso.",
                "Coordinar prioridades y la organización del trabajo entre equipos.",
                "Reportar periódicamente al CEO el avance general y plantear los asuntos que requieran decisión.",
            ],
            "limite": "Los líderes de equipo deben entregarle oportunamente información de avance veraz y verificable.",
            "entregables": ["Cronograma Gantt actualizado.", "Reporte de avance general para el CEO."],
            "reporta_a": "CEO (Haniel Fierros)",
            "comunica_con": ["Líderes de equipo", "CEO", "Ingeniería de Operaciones"],
        },
        {
            "id": "profesores-ipn", "icono": "🎓", "nombre": "",
            "cargo": "Profesores del IPN", "organizacion": "IPN",
            "rol": "Orientación profesional y supervisión técnica",
            "resumen": "Brindan orientación técnica en sus áreas de especialidad y apoyan la confirmación de métodos, estándares y pruebas.",
            "responsabilidades": [
                "Brindar orientación a los estudiantes en sus respectivas áreas de especialidad.",
                "Colaborar en la confirmación de métodos de trabajo, estándares técnicos, pasos de operación y seguridad técnica.",
                "Revisar, cuando sea necesario, el diseño, el plan de implementación, los métodos de prueba y los resultados.",
                "Orientar a los estudiantes para detectar, analizar y corregir problemas técnicos.",
                "Aportar recomendaciones profesionales; los asuntos de alcance del proyecto, recursos o aprobación final se escalan según el proceso de gestión.",
            ],
            "limite": "No se asume que los profesores asuman la gestión de planeación interna de EEA ni la responsabilidad de aprobación final del proyecto.",
            "entregables": ["Orientación y recomendaciones técnicas."],
            "reporta_a": "— (asesoría técnica; sin línea de mando del proyecto)",
            "comunica_con": ["Estudiantes", "Líderes de equipo"],
        },
        {
            "id": "lideres-equipo", "icono": "🧑‍💼", "nombre": "",
            "cargo": "Líderes de equipo", "organizacion": "Equipos del proyecto",
            "rol": "Responsables de la ejecución de cada grupo de trabajo",
            "resumen": "Responsables de las tareas, calidad, avance y entregables del equipo; coordinan a sus integrantes y reportan a Planeación.",
            "responsabilidades": [
                "Ser responsable de las tareas, la calidad, el avance y los entregables asignados al equipo.",
                "Organizar la descomposición de tareas y definir los pasos de ejecución y los objetivos por etapa.",
                "Seleccionar a los integrantes del equipo; el equipo tiene un máximo de cinco personas en total, incluyendo al líder.",
                "Distribuir el trabajo de forma razonable, dar seguimiento a las tareas de los integrantes y revisar los resultados.",
                "Investigar y confirmar, antes de ejecutar, los métodos técnicos, las herramientas, los materiales y el proceso de implementación correctos.",
                "Elaborar y presentar reportes de avance, registros de trabajo, listas de problemas, necesidades de recursos y fechas estimadas de término.",
                "Presentar al Supervisor de Planeación el avance, las necesidades, los riesgos y las alertas de retraso, para actualizar el Gantt.",
                "Comunicarse con los profesores del IPN ante problemas técnicos.",
                "Comunicarse con Roxana, Misael y el CEO según la naturaleza del asunto; escalar los cambios relevantes de alcance, recursos críticos, conflictos o aprobación final.",
                "Garantizar la continuidad del trabajo del equipo, la integridad de la información y la transferencia de conocimiento.",
                "Asegurar que las necesidades de materiales, herramientas y recursos se identifiquen con anticipación; no ocultar faltantes ni comprometer compras por cuenta propia sin autorización.",
                "Dirigir al equipo con buen liderazgo, colaboración justa, sentido de responsabilidad y comunicación efectiva.",
            ],
            "limite": "No tienen autorización para gastar ni para comprometer compras por cuenta propia; las necesidades se identifican, estiman y coordinan según el proceso de EEA.",
            "entregables": ["Reportes de avance y registros de trabajo.", "Listas de problemas y necesidades de recursos.", "Fechas estimadas de término."],
            "reporta_a": "Supervisor de Planeación (Roxana Méndez)",
            "comunica_con": ["Supervisor de Planeación", "Profesores del IPN", "Ingeniería de Operaciones", "CEO"],
        },
    ],
    "perfil_lider": {
        "titulo": "Perfil del líder de equipo",
        "descripcion": "Criterios de selección del líder de cada equipo.",
        "criterios": [
            "Liderazgo y responsabilidad.",
            "Comunicación clara y respetuosa.",
            "Planeación, organización y seguimiento.",
            "Delegación y coordinación de personas.",
            "Resolución de problemas y toma de decisiones.",
            "Capacidad para investigar y aprender procedimientos técnicos.",
            "Trabajo en equipo y colaboración interdisciplinaria.",
            "Cumplimiento de plazos y documentación.",
            "Gestión de recursos, materiales y riesgos.",
            "Continuidad operativa y transferencia de conocimientos.",
        ],
        "frase": "Un líder no necesita saber hacerlo todo; debe saber organizar, investigar, consultar a los especialistas, delegar y asegurar que el trabajo se complete correctamente.",
    },
    "reglas_equipos": {
        "titulo": "Reglas para conformar equipos",
        "reglas": [
            "Cada equipo debe contar con un líder cuyo perfil sea adecuado para las responsabilidades asignadas.",
            "Cada equipo debe tener acceso a por lo menos una laptop funcional para sus actividades.",
            "Cada líder seleccionará su equipo, con un máximo de cinco integrantes en total, incluyendo al líder: cuatro integrantes adicionales como máximo.",
            "Un líder puede participar también como integrante de un equipo dirigido por otro líder, siempre que se mantengan claras sus responsabilidades y no se comprometa el cumplimiento de sus funciones principales.",
            "Cada equipo debe garantizar la continuidad de sus actividades durante todo el proyecto, incluyendo documentación, respaldos y transferencia de conocimientos.",
            "Cada líder debe identificar y justificar los recursos financieros necesarios para las actividades asignadas, elaborar estimaciones y coordinar las necesidades de recursos. No implica autorización para gastar ni obligación de financiar personalmente el proyecto.",
            "El IPN podrá aportar parte de los materiales. La disponibilidad real debe verificarse y coordinarse con el CEO antes de decidir qué materiales se comprarán. Se debe consultar el inventario existente y evitar compras duplicadas.",
        ],
        "nota": "La regla 6 no debe interpretarse como que el líder debe pagar de su bolsillo. Su responsabilidad es planear, estimar, declarar y coordinar las necesidades de fondos y materiales; la aprobación real de fondos se ejecuta según el proceso de gestión del proyecto de EEA.",
    },
    "comunicacion": {
        "titulo": "Comunicación, reportes y escalamiento",
        "flujo": [
            {"de": "Líderes de equipo", "a": "Supervisor de Planeación (Roxana)", "nota": "Avance, fechas estimadas y necesidades de recursos."},
            {"de": "Supervisor de Planeación (Roxana)", "a": "CEO (Haniel)", "nota": "Reporte de avance general y asuntos que requieren decisión."},
        ],
        "canales_especiales": [
            {"titulo": "Revisión de ingeniería, calidad, manuales y entrega", "responsable": "Ingeniería de Operaciones (Misael)"},
            {"titulo": "Consulta técnica especializada", "responsable": "Profesores del IPN"},
        ],
        "reglas": [
            "Los líderes de equipo pueden plantear preguntas directamente a los profesores, a Roxana o al CEO, según la naturaleza del asunto.",
            "El avance diario, las fechas estimadas de término y las necesidades de recursos se reportan de forma unificada a Roxana, para mantener el Gantt.",
            "Los problemas técnicos se consultan de manera prioritaria con el profesor correspondiente del IPN.",
            "La revisión de entregables, manuales, auditorías y asuntos de calidad se presentan a Misael.",
            "El alcance del proyecto, los recursos relevantes, los conflictos entre equipos y la aprobación final se presentan al CEO.",
            "Los riesgos de seguridad o técnicos relevantes y urgentes deben reportarse de inmediato, sin esperar el reporte rutinario.",
            "La comunicación directa no sustituye el registro formal de avance; las decisiones importantes deben registrarse y notificarse a las personas correspondientes.",
        ],
    },
    "equipos_trabajo": {
        "titulo": "Equipos de trabajo",
        "intro": ("Siete equipos iniciales del proyecto. Esta estructura es editable y puede "
                  "ajustarse si la inspección real o el avance del proyecto lo requiere."),
        "nota": ("Los entregables deben verificarse mediante documentos, registros, pruebas o "
                 "evidencias; no se declaran como ya existentes."),
        "relaciones_titulo": "Relaciones y colaboración principal",
        "relaciones_nota": ("Relaciones principales de colaboración. Las dependencias específicas y sus "
                            "fechas se confirmarán durante la planeación con el Supervisor de Planeación."),
        "relaciones": [
            {"de": "Supervisión y Planeación", "a": "Todos los equipos", "tipo": "Coordinación y seguimiento"},
            {"de": "Limpieza y acondicionamiento", "a": "Mecánica y mandos físicos", "tipo": "Cabina preparada"},
            {"de": "Limpieza y acondicionamiento", "a": "Aviónica e instrumentación", "tipo": "Zona limpia"},
            {"de": "Mecánica y mandos físicos", "a": "Electrónica y sensorización", "tipo": "Mandos físicos adaptados"},
            {"de": "Electrónica y sensorización", "a": "Software e integración", "tipo": "Señales y cableado"},
            {"de": "Aviónica e instrumentación", "a": "Software e integración", "tipo": "Instrumentos e interfaces"},
            {"de": "Software e integración", "a": "Simulación y validación operativa", "tipo": "Integración lista para pruebas"},
        ],
        "equipos": [
            {
                "id": "limpieza", "icono": "🧹",
                "nombre": "Limpieza y acondicionamiento",
                "responsabilidades": [
                    "Inspección inicial de la cabina.",
                    "Limpieza profunda de la cabina.",
                    "Retiro controlado de residuos.",
                    "Limpieza de superficies.",
                    "Identificación de corrosión.",
                    "Preparación de la cabina para trabajos posteriores.",
                ],
                "actividades": [
                    "Realizar la inspección inicial y el diagnóstico de riesgos (biológicos/químicos).",
                    "Desmontar de forma controlada los elementos que lo requieran.",
                    "Limpiar y sanitizar las superficies de la cabina.",
                    "Retirar y clasificar los residuos de forma controlada.",
                    "Identificar y reportar las zonas con corrosión.",
                    "Preparar y proteger la cabina para las siguientes etapas.",
                ],
                "entregables": [
                    "Registro fotográfico inicial y final.",
                    "Lista de daños y faltantes.",
                    "Registro de limpieza.",
                    "Reporte de condiciones y necesidades de reparación.",
                ],
                "dependencias": [
                    "Entrega la cabina preparada a Mecánica y mandos físicos y a Aviónica e instrumentación.",
                    "Recibe lineamientos y prioridades de Supervisión y Planeación.",
                ],
                "perfil_lider": [
                    "Organización del trabajo en sitio y manejo de residuos.",
                    "Atención al detalle y documentación (registros fotográficos y listas).",
                ],
                "nota": "",
            },
            {
                "id": "supervision-planeacion", "icono": "🗓️",
                "nombre": "Supervisión y Planeación",
                "responsabilidades": [
                    "Coordinación de actividades.",
                    "Seguimiento de avances.",
                    "Recopilación de estimados de entrega.",
                    "Identificación de dependencias, riesgos y necesidades de recursos.",
                    "Actualización del Gantt bajo la dirección de Roxana Méndez.",
                ],
                "actividades": [
                    "Coordinar las actividades entre los equipos.",
                    "Dar seguimiento a los avances y recopilar estimados de entrega.",
                    "Identificar dependencias, riesgos y necesidades de recursos.",
                    "Mantener actualizado el cronograma Gantt.",
                ],
                "entregables": [
                    "Cronograma actualizado.",
                    "Reportes de avance.",
                    "Registro de riesgos.",
                    "Lista de pendientes.",
                    "Solicitudes de recursos.",
                    "Seguimiento de acuerdos.",
                ],
                "dependencias": [
                    "Coordina y da seguimiento a todos los equipos.",
                    "Reporta a Roxana Méndez, Supervisor de Planeación.",
                ],
                "perfil_lider": [
                    "Planeación, organización y seguimiento.",
                    "Comunicación clara y manejo de cronograma y riesgos.",
                ],
                "nota": "Este equipo apoya la planeación; no sustituye la responsabilidad de Roxana como Supervisor de Planeación.",
            },
            {
                "id": "avionica-instrumentacion", "icono": "🖥️",
                "nombre": "Aviónica e instrumentación",
                "responsabilidades": [
                    "Definición e integración de instrumentos virtuales.",
                    "Panel de control y pantallas.",
                    "Controles de navegación y panel de piloto automático.",
                    "Todo según las funciones realmente compatibles con X-Plane 12.",
                ],
                "actividades": [
                    "Definir los instrumentos virtuales y su distribución.",
                    "Integrar el panel de control y las pantallas.",
                    "Configurar los controles de navegación y el panel de piloto automático.",
                    "Verificar las funciones realmente compatibles con X-Plane 12.",
                ],
                "entregables": [
                    "Inventario de instrumentos e interfaces.",
                    "Mapa de controles.",
                    "Especificación funcional.",
                    "Pruebas de operación.",
                    "Documentación de integración.",
                ],
                "dependencias": [
                    "Colabora con Software e integración para conectarse a X-Plane 12.",
                    "Coordina con Electrónica y sensorización el cableado de los controles.",
                ],
                "perfil_lider": [
                    "Conocimiento de instrumentación y de integración con simulador.",
                    "Verificación de compatibilidad antes de asumir funciones.",
                ],
                "nota": "",
            },
            {
                "id": "mecanica-mandos", "icono": "🔧",
                "nombre": "Mecánica y mandos físicos",
                "responsabilidades": [
                    "Inspección, recuperación, reparación y adaptación de mandos originales.",
                    "Volante/columna, pedales, timón, palancas, mecanismos y soportes físicos.",
                ],
                "actividades": [
                    "Inspeccionar y recuperar los mandos originales.",
                    "Reparar los componentes dañados.",
                    "Adaptar los mandos y soportes físicos para la sensorización.",
                    "Documentar reparaciones y piezas faltantes.",
                ],
                "entregables": [
                    "Inventario de componentes recuperables.",
                    "Registro de reparaciones.",
                    "Relación de piezas faltantes.",
                    "Evidencia de funcionamiento.",
                    "Reporte de aceptación mecánica.",
                ],
                "dependencias": [
                    "Recibe la cabina preparada de Limpieza y acondicionamiento.",
                    "Entrega los mandos funcionales a Electrónica y sensorización.",
                ],
                "perfil_lider": [
                    "Conocimientos de mecánica y fabricación.",
                    "Cuidado con estructuras y documentación de reparaciones.",
                ],
                "nota": "",
            },
            {
                "id": "software-integracion", "icono": "💻",
                "nombre": "Software e integración",
                "responsabilidades": [
                    "Integración de X-Plane 12 con los microcontroladores, interfaces y controles físicos.",
                    "Configuración de software, desarrollo de lógica, pruebas de comunicación y gestión de versiones locales.",
                ],
                "actividades": [
                    "Integrar X-Plane 12 con microcontroladores e interfaces.",
                    "Configurar el software y desarrollar la lógica.",
                    "Ejecutar pruebas de comunicación.",
                    "Gestionar las versiones locales del software.",
                ],
                "entregables": [
                    "Arquitectura de software.",
                    "Configuración documentada.",
                    "Código fuente desarrollado.",
                    "Matriz de asignación de controles.",
                    "Resultados de pruebas.",
                    "Guía de recuperación.",
                ],
                "dependencias": [
                    "Recibe mapas y hardware de Electrónica y de Aviónica.",
                    "Entrega la integración lista para Simulación y validación operativa.",
                ],
                "perfil_lider": [
                    "Capacidad para investigar y verificar compatibilidad de herramientas.",
                    "Documentación y control de versiones.",
                ],
                "nota": "No asumir compatibilidad entre herramientas sin verificarla.",
            },
            {
                "id": "electronica-sensorizacion", "icono": "⚡",
                "nombre": "Electrónica y sensorización",
                "responsabilidades": [
                    "Diseño y montaje de circuitos con Arduino Mega y Teensy cuando proceda.",
                    "Selección de sensores, potenciómetros, interruptores, cableado, alimentación independiente, filtros y acondicionamiento de señales.",
                ],
                "actividades": [
                    "Diseñar y montar los circuitos con Arduino Mega y, cuando proceda, Teensy.",
                    "Seleccionar sensores, potenciómetros e interruptores.",
                    "Tender el cableado y la alimentación independiente.",
                    "Implementar filtros y acondicionamiento de señales.",
                ],
                "entregables": [
                    "Diagramas de conexión.",
                    "Lista de materiales validada.",
                    "Mapa de entradas/salidas.",
                    "Registro de calibración.",
                    "Pruebas eléctricas.",
                    "Documentación de cableado.",
                ],
                "dependencias": [
                    "Recibe los mandos de Mecánica y mandos físicos.",
                    "Entrega señales y cableado a Software e integración.",
                ],
                "perfil_lider": [
                    "Conocimientos de electrónica y seguridad eléctrica.",
                    "Validación de la lista de materiales sin asumir componentes no confirmados.",
                ],
                "nota": "Priorizar protoboards y conexiones soldadas funcionales; no exigir fabricación de PCB.",
            },
            {
                "id": "simulacion-validacion", "icono": "🛬",
                "nombre": "Simulación y validación operativa",
                "responsabilidades": [
                    "Ejecutar pruebas integrales en el simulador terrestre.",
                    "Comprobar respuesta de mandos, flaps, tren de aterrizaje, motores simulados, piloto automático, indicaciones, audio y visualización, según el alcance implementado.",
                ],
                "actividades": [
                    "Ejecutar las pruebas integrales del simulador.",
                    "Comprobar la respuesta de mandos, flaps y tren de aterrizaje.",
                    "Verificar motores simulados, piloto automático e indicaciones.",
                    "Probar audio y visualización.",
                ],
                "entregables": [
                    "Plan y protocolos de pruebas.",
                    "Listas de verificación.",
                    "Resultados reproducibles.",
                    "Registro de defectos.",
                    "Evidencias.",
                    "Reporte de aceptación funcional.",
                ],
                "dependencias": [
                    "Recibe la integración de Software y Aviónica.",
                    "Reporta defectos a los equipos correspondientes.",
                ],
                "perfil_lider": [
                    "Pruebas sistemáticas con criterios objetivos.",
                    "Registro de resultados y reporte de defectos.",
                ],
                "nota": "Las pruebas se realizan en simulación terrestre; la aeronave real no volverá a volar.",
            },
        ],
    },
}


REFERENCIAS_OFICIALES = [
    {"nombre": "AFAC — Agencia Federal de Aviación Civil (México)", "tipo": "Referencia regulatoria",
     "enlace": "https://www.gob.mx/afac", "estado": "Fuente oficial (dominio confirmado)",
     "nota": "El dominio gob.mx es oficial; el contenido específico se verifica en el sitio (pendiente de confirmación de cada documento)."},
    {"nombre": "FAA — Advisory Circulars (AC)", "tipo": "Referencia técnica",
     "enlace": "https://www.faa.gov/regulations_policies/advisory_circulars", "estado": "Verificada (fuente oficial)",
     "nota": "Fuente pública oficial de la FAA; la AC aplicable se selecciona tras verificar el contenido."},
]

PAT = re.compile(r"EEA[A-Z0-9\-]*\d{3}")

LIMITES_EQUIPOS = {
    "Limpieza": "No realiza cortes ni reparaciones estructurales ni retiro eléctrico sin autorización.",
    "Supervision_y_Planeacion": "No aprueba gastos ni compras y no sustituye firmas técnicas de otros equipos.",
    "Avionica": "No declara certificación FAA/AFAC; verifica DataRefs/Commands antes de usarlos.",
    "Mecanica": "No interviene estructuras primarias sin aprobación escrita.",
    "Software": "No ejecuta cambios de sistema sin autorización del responsable.",
    "Logico": "No decide el diseño técnico ni aprueba resultados técnicos de otros equipos.",
    "Vuelo": "No ejecuta vuelo real; no usa el desempeño del piloto como único criterio de aprobación.",
}

MANUALES_EQUIPOS = {
    "Limpieza": "manual-limpieza.pdf",
    "Supervision_y_Planeacion": "manual-supervision-planeacion.pdf",
    "Avionica": "manual-avionica.pdf",
    "Mecanica": "manual-mecanica.pdf",
    "Software": "manual-software.pdf",
    "Logico": "manual-logico.pdf",
    "Vuelo": "manual-vuelo.pdf",
}

MANUALES_FUENTES = {
    "Limpieza": "Proyecto DPC DC3/Limpieza/00_Manual/Manual_del_Equipo_de_Limpieza.pdf",
    "Supervision_y_Planeacion": "Proyecto DPC DC3/Supervision_y_Planeacion/00_Manual/Manual_del_Equipo_de_Supervision_y_Planeacion.pdf",
    "Avionica": "Proyecto DPC DC3/Avionica/00_Manual/Manual_del_Equipo_de_Avionica.pdf",
    "Mecanica": "Proyecto DPC DC3/Mecanica/00_Manual/Manual_del_Equipo_de_Mecanica.pdf",
    "Software": "Proyecto DPC DC3/Software/00_Manual/Manual_del_Equipo_de_Software.pdf",
    "Logico": "Proyecto DPC DC3/Logico/00_Manual/Manual_del_Equipo_Logico.pdf",
    "Vuelo": "Proyecto DPC DC3/Vuelo/01_Manual/Manual_del_Equipo_de_Vuelo.pdf",
}

CEO = {
    "nombre": "Haniel Fierros", "rol": "CEO Eben Ezer Aviation",
    "cargo": "Director de Proyecto · Patrocinador principal",
    "decisiones": "Decisiones estratégicas y de dirección del proyecto.",
    "recomendaciones": [
        "Mantener la colaboración entre equipos y la coordinación multidisciplinaria, compartiendo información oportunamente.",
        "Ejecutar según el plan y los hitos acordados, reportando oportunamente las desviaciones.",
        "Comunicar de inmediato los riesgos o bloqueos, sin ocultarlos ni retrasarlos.",
    ],
}

SUPERVISOR = {
    "nombre": "Roxana Mendez", "rol": "Supervisora principal",
    "cargo": "Supervisa a los equipos y el cumplimiento de objetivos; reporta al CEO.",
    "recomendaciones": [
        "Seguir estrictamente el plan, los plazos y los hitos confirmados.",
        "Preguntar de inmediato ante requisitos técnicos poco claros; no ejecutar por suposición.",
        "Revisar periódicamente el avance, los entregables y las dependencias de cada equipo.",
        "Registrar y escalar oportunamente retrasos, conflictos de recursos o riesgos.",
        "En cada reunión de coordinación, definir responsables, acciones y fechas, y dar seguimiento al cierre.",
    ],
}

DIRS_DESCARGAS = [
    ("Bitácora y seguimiento", "Proyecto DPC DC3/Limpieza/02_Bitacora_y_Seguimiento", "dl-bitacora-"),
    ("Formatos y anexos", "Proyecto DPC DC3/Limpieza/03_Formatos_y_Anexos", "dl-formato-"),
]


# ---------------------------------------------------------------------------
# Escaneo de equipos (OI/OT, riesgos, entregables, fases)
# ---------------------------------------------------------------------------
def _cargar_oi_data(base):
    """Carga actividades.json/ois.json/ots.json y devuelve {oi_id: {fase, titulo}}."""
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "render_check") and not d.startswith("backup_")]
        for nombre in ("actividades.json", "ois.json", "ots.json"):
            if nombre in files:
                try:
                    data = json.load(open(os.path.join(root, nombre), encoding="utf-8"))
                    mapa = {}
                    for it in data:
                        oid = it.get("oi_id") or it.get("ot_id")
                        if oid:
                            mapa[oid] = {"fase": it.get("fase"),
                                         "titulo": it.get("titulo_corto") or it.get("titulo", "")}
                    if mapa:
                        return mapa
                except Exception:
                    pass
    return {}


def escanear_equipo(equipo):
    base = os.path.join(DPC, equipo["carpeta"])
    oi_data = _cargar_oi_data(base)
    ois = []
    riesgos = []
    entregables = 0
    fases_equipo = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "render_check") and not d.startswith("backup_")]
        for f in files:
            if f.lower().endswith(".pdf") and re.search(r"(OI|OT)-\d{3}", f):
                num = PAT.findall(f)
                oid = num[0] if num else f.replace(".pdf", "")
                info = oi_data.get(oid, {})
                ois.append({"id": oid, "archivo": f,
                            "fase": info.get("fase"),
                            "titulo": info.get("titulo", "")})
        if "riesgos.json" in files:
            try:
                data = json.load(open(os.path.join(root, "riesgos.json"), encoding="utf-8"))
                for r in data:
                    riesgos.append({
                        "id": r.get("id", PEND),
                        "tipo": "riesgo",
                        "equipo": equipo["nombre"],
                        "peligro": r.get("peligro", ""),
                        "prob": r.get("prob") or r.get("prob_inicial") or PEND,
                        "impacto": r.get("impacto") or r.get("impacto_inicial") or PEND,
                        "nivel": r.get("nivel") or r.get("riesgo_inicial") or PEND,
                        "mitigacion": r.get("mitigacion", ""),
                        "responsable": r.get("responsable", PEND),
                        "estado": r.get("estado", "Abierto"),
                    })
            except Exception:
                pass
        if "entregables.json" in files:
            try:
                entregables = len(json.load(open(os.path.join(root, "entregables.json"), encoding="utf-8")))
            except Exception:
                pass
        if "config.json" in files:
            try:
                cfg = json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
                fases_equipo = [{"id": f.get("id"), "nombre": f.get("nombre", "")}
                                for f in cfg.get("fases", [])]
            except Exception:
                pass
    return ois, riesgos, entregables, fases_equipo


def construir_equipos():
    equipos = []
    for e in EQUIPOS:
        ois, riesgos, entregables, fases_equipo = escanear_equipo(e)
        e2 = dict(e)
        e2["ois"] = ois
        e2["riesgos"] = riesgos
        e2["entregables"] = entregables
        e2["fases"] = fases_equipo
        e2["limites"] = LIMITES_EQUIPOS.get(e["carpeta"], "Pendiente de confirmación")
        e2["manual"] = MANUALES_EQUIPOS.get(e["carpeta"], "")
        e2["progreso"] = 0
        equipos.append(e2)
    return equipos


def _nodo_oi(o, mapa):
    nodo = {"tipo": "oi", "nombre": o["id"], "titulo": o.get("titulo", ""), "archivo": o["archivo"]}
    t = mapa.get(o["id"], {})
    for k in ("inicio", "fin", "duracion", "complejidad", "estado", "dependencias"):
        nodo[k] = t.get(k, "")
    return nodo


def _nodo_equipo(e, mapa):
    asignados = set()
    fases = e.get("fases") or []
    hijos = []
    for f in fases:
        fid = str(f["id"])
        ois_fase = [o for o in e["ois"] if str(o.get("fase")) == fid and o["id"] not in asignados]
        for o in ois_fase:
            asignados.add(o["id"])
        hijos.append({"tipo": "fase", "nombre": f["nombre"], "hijos": [_nodo_oi(o, mapa) for o in ois_fase]})
    restantes = [o for o in e["ois"] if o["id"] not in asignados]
    if restantes:
        hijos.append({"tipo": "fase", "nombre": "Sin fase asignada", "hijos": [_nodo_oi(o, mapa) for o in restantes]})
    return {
        "tipo": "equipo", "nombre": e["nombre"], "manual": e.get("manual", ""),
        "objetivo": e.get("objetivo", ""), "limites": e.get("limites", ""),
        "responsabilidades": e.get("responsabilidades", []),
        "entregables": e.get("entregables", 0), "hijos": hijos,
    }


def construir_edt(equipos, mapa):
    arbol = {
        "tipo": "ceo", "nombre": CEO["nombre"], "rol": CEO["rol"], "cargo": CEO["cargo"],
        "decisiones": CEO["decisiones"], "recomendaciones": CEO["recomendaciones"],
        "hijos": [{
            "tipo": "supervisor", "nombre": SUPERVISOR["nombre"], "rol": SUPERVISOR["rol"],
            "cargo": SUPERVISOR["cargo"], "recomendaciones": SUPERVISOR["recomendaciones"],
            "hijos": [_nodo_equipo(e, mapa) for e in equipos],
        }],
    }
    return arbol


def construir_cronograma(equipos):
    """Cronograma estimado: asignación determinista de tiempo y complejidad por OI.

    La fecha de inicio (2026-11-16) y la ventana nominal de 8 semanas son de
    referencia. Las duraciones y fechas resultantes son estimaciones de
    ingeniería marcadas como 'Estimación pendiente de validación'.
    """
    import datetime as _dt
    inicio = _dt.date(2026, 11, 16)
    span = 56  # 8 semanas calendario

    CATEGORIAS = [
        {"id": "baja", "etiqueta": "Baja complejidad / corta duración", "color": "#34d399", "duracion": 1},
        {"id": "general", "etiqueta": "Complejidad general", "color": "#38bdf8", "duracion": 2},
        {"id": "media-alta", "etiqueta": "Complejidad media-alta", "color": "#fbbf24", "duracion": 3},
        {"id": "alta", "etiqueta": "Alta complejidad / larga duración", "color": "#f97316", "duracion": 4},
        {"id": "critica", "etiqueta": "Integración, validación o aceptación", "color": "#ef4444", "duracion": 3},
    ]
    CAT = {c["id"]: c for c in CATEGORIAS}

    # Regla de clasificación (documentada): según la fase del proyecto.
    COMPLEJIDAD_POR_FASE = {
        "1": "general", "A": "general", "B": "general",
        "2": "media-alta", "C": "media-alta", "D": "media-alta",
        "3": "alta", "E": "alta", "F": "alta", "G": "alta",
        "4": "critica", "H": "critica",
    }

    # Ventana de trabajo por equipo (días desde el inicio), nominal.
    VENTANAS = {
        "Limpieza": (0, 12),
        "Supervision_y_Planeacion": (0, span),
        "Avionica": (8, 28),
        "Mecanica": (8, 28),
        "Software": (18, 36),
        "Logico": (0, span),
        "Vuelo": (30, span),
    }
    CONTINUOS = {"Supervision_y_Planeacion", "Logico"}

    def fecha(delta):
        return (inicio + _dt.timedelta(days=delta)).isoformat()

    mapa = {}
    equipos_crono = []
    for e in equipos:
        carpeta = e["carpeta"]
        w0, w1 = VENTANAS.get(carpeta, (0, span))
        ois = e.get("ois", [])
        n = len(ois)
        tareas = []
        if carpeta in CONTINUOS and n > 1:
            for i, o in enumerate(ois):
                cat = COMPLEJIDAD_POR_FASE.get(str(o.get("fase", "")), "general")
                dur = CAT[cat]["duracion"]
                ini = w0 + round(i * (w1 - w0 - dur) / (n - 1))
                fin = min(ini + dur, w1)
                t = {"id": o["id"], "titulo": o.get("titulo", ""), "archivo": o["archivo"],
                     "inicio": fecha(ini), "fin": fecha(fin), "duracion": dur,
                     "complejidad": cat, "estado": "Estimación pendiente de validación",
                     "dependencias": []}
                tareas.append(t)
        else:
            cursor = w0
            for o in ois:
                cat = COMPLEJIDAD_POR_FASE.get(str(o.get("fase", "")), "general")
                dur = CAT[cat]["duracion"]
                ini = min(cursor, w1 - 1)
                fin = min(ini + dur, w1)
                cursor = fin
                t = {"id": o["id"], "titulo": o.get("titulo", ""), "archivo": o["archivo"],
                     "inicio": fecha(ini), "fin": fecha(fin), "duracion": dur,
                     "complejidad": cat, "estado": "Estimación pendiente de validación",
                     "dependencias": []}
                tareas.append(t)
        for t in tareas:
            mapa[t["id"]] = {k: t[k] for k in ("inicio", "fin", "duracion", "complejidad", "estado", "dependencias")}
        equipos_crono.append({"nombre": e["nombre"], "inicio": w0, "fin": w1, "tareas": tareas})

    return {
        "inicio": fecha(0), "inicio_marca": "Propuesto",
        "fin": fecha(span), "span": span,
        "escala": "Estimación pendiente de validación",
        "categorias": CATEGORIAS,
        "mapa": mapa,
        "equipos": equipos_crono,
    }


def construir_biblioteca():
    if not os.path.isdir(BT):
        return [], []
    docs = []
    copiados = []
    sobre = []
    for f in sorted(os.listdir(BT)):
        fp = os.path.join(BT, f)
        if not os.path.isfile(fp):
            continue
        mb = os.path.getsize(fp) / (1024 * 1024)
        nombre = os.path.splitext(f)[0]
        seguro = re.sub(r"[^a-zA-Z0-9]+", "-", nombre).strip("-").lower() or "doc"
        destino = "bt-" + seguro + ".pdf"
        docs.append({"titulo": nombre, "archivo": destino, "origen": f,
                     "mb": round(mb, 1), "estado": "Disponible" if mb <= LIMITE_COPIA_MB else "Bajo revisión"})
        if mb <= LIMITE_COPIA_MB:
            shutil.copyfile(fp, os.path.join(ROOT, destino))
            copiados.append(destino)
        else:
            sobre.append({"archivo": f, "mb": round(mb, 1),
                          "motivo": "Supera el límite de %d MB para la web" % LIMITE_COPIA_MB})
    return docs, sobre


def _objetivo_general(j):
    """Extrae el objetivo general del programa desde cualquiera de los dos
    esquemas de programa.json presentes en la serie EEA-IFR."""
    gd = j.get("guia_didactica")
    if isinstance(gd, dict):
        og = gd.get("objetivo_general")
        if isinstance(og, dict) and isinstance(og.get("texto"), str) and og["texto"].strip():
            return og["texto"].strip()
    ident = j.get("identificacion")
    if isinstance(ident, dict):
        for ss in ident.get("subsecciones", []):
            if isinstance(ss, dict) and (ss.get("titulo") or "").strip().lower() == "objetivo general":
                for clave in ("parrafos", "items"):
                    vals = ss.get(clave)
                    if isinstance(vals, list) and vals and isinstance(vals[0], str) and vals[0].strip():
                        return vals[0].strip()
    return ""


def construir_practicas():
    """Escanea los PDF numerados de la serie EEA-IFR en `Programas de Estudio`,
    extrae nombre/objetivo del programa.json correspondiente, verifica el texto
    del PDF y copia cada PDF a la raíz (nombre original, sin depender de la
    ruta de Windows). Devuelve (practicas, pendientes)."""
    if not os.path.isdir(PE):
        return [], []
    practicas = []
    pendientes = []
    try:
        from pypdf import PdfReader
        tiene_pypdf = True
    except Exception:
        tiene_pypdf = False
    for f in sorted(os.listdir(PE)):
        if not re.match(r"^EEA-IFR-\d{2}-.+\.pdf$", f, re.I):
            continue
        fp = os.path.join(PE, f)
        if not os.path.isfile(fp):
            continue
        base = os.path.splitext(f)[0]
        num = int(re.match(r"^EEA-IFR-(\d{2})", base, re.I).group(1))
        codigo = "EEA-IFR-%02d" % num
        nombre = nivel = objetivo = ""
        pend_razones = []
        pj = os.path.join(PE, base, "data", "programa.json")
        if os.path.exists(pj):
            try:
                j = json.load(open(pj, encoding="utf-8"))
                pr = j.get("programa", {})
                nombre = (pr.get("nombre") or "").strip()
                nivel = (pr.get("nivel") or "").strip()
                codigo = (pr.get("codigo") or codigo).strip()
                objetivo = _objetivo_general(j)
            except Exception as ex:
                pend_razones.append("programa.json no legible (%s)" % ex)
        else:
            pend_razones.append("falta data/programa.json")
        if not nombre:
            pend_razones.append("nombre no identificado")
        if not objetivo:
            pend_razones.append("objetivo no identificado")
        # Verificación del texto del PDF (preferente a OCR solo si no extrae texto)
        texto_pdf = ""
        if tiene_pypdf:
            try:
                lector = PdfReader(fp)
                texto_pdf = "\n".join((pg.extract_text() or "") for pg in lector.pages)
            except Exception as ex:
                pend_razones.append("PDF no legible (%s)" % ex)
        if not texto_pdf.strip():
            pend_razones.append("PDF sin texto extraíble (posible escaneado)")
        destino = f
        shutil.copyfile(fp, os.path.join(ROOT, destino))
        practicas.append({
            "numero": num, "codigo": codigo, "nombre": nombre,
            "nivel": nivel, "objetivo": objetivo, "archivo": destino,
        })
        if pend_razones:
            pendientes.append({"codigo": codigo, "archivo": destino,
                               "motivo": "; ".join(pend_razones)})
    practicas.sort(key=lambda p: p["numero"])
    return practicas, pendientes


def generar_svg():
    def _escribir(nombre, contenido):
        open(os.path.join(ROOT, nombre), "w", encoding="utf-8").write(contenido)

    # Wireframe DC-3 (referencia, se conserva por compatibilidad; el visor 3D usa WebGL)
    dc3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-label="Wireframe DC-3">
  <g fill="none" stroke="#1686c9" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">
    <path d="M80 150 L120 130 L400 120 L500 110 L620 118 L760 130 L840 140 L820 155 L760 160 L620 160 L500 150 L400 150 L120 160 L80 150 Z"/>
    <path d="M120 130 L110 150 L80 150"/>
    <path d="M400 120 L420 100 L560 100 L580 118"/>
    <path d="M120 160 L100 200 L80 210"/>
    <path d="M700 160 L720 210 L760 220"/>
    <path d="M620 118 L640 96 L760 96 L780 130"/>
    <line x1="180" y1="125" x2="180" y2="155"/>
    <line x1="240" y1="123" x2="240" y2="155"/>
    <line x1="300" y1="122" x2="300" y2="155"/>
    <circle cx="560" cy="104" r="22"/>
    <path d="M700 96 L700 104 L760 104"/>
  </g>
  <text x="450" y="260" fill="#5a6b7b" font-family="sans-serif" font-size="14" text-anchor="middle">DC-3 — perfil de referencia (línea; no a escala)</text>
</svg>
"""
    _escribir("wireframe-dc3.svg", dc3)

    # ===== Paneles King Air 90 (esquemas de referencia; fotografía verificable pendiente) =====
    def _panel(archivo, titulo, config, instrumentos, nota):
        panel = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" role="img" aria-label="%s">'
                 '<rect x="10" y="10" width="1180" height="400" rx="14" fill="#0b1622"/>'
                 '<text x="600" y="40" fill="#e6edf4" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle">%s</text>'
                 '<text x="600" y="60" fill="#8ea3ba" font-family="sans-serif" font-size="12" text-anchor="middle">%s</text>'
                 '%s'
                 '<text x="600" y="405" fill="#9fb2c6" font-family="sans-serif" font-size="11" text-anchor="middle">%s</text></svg>'
                 % (titulo, titulo, config, instrumentos, nota))
        _escribir(archivo, panel)

    _panel("panel-kingair90-convencional.svg",
           "King Air 90 — Panel convencional (instrumentos analógicos)",
           "Configuración convencional · referencia esquemática",
           '<g fill="#0e1c2a" stroke="#1686c9">'
           '<rect x="40" y="90" width="260" height="180" rx="8"/><text x="170" y="120" fill="#bfd8e8" font-family="sans-serif" font-size="14" text-anchor="middle">Instrumentos de vuelo</text>'
           '<circle cx="130" cy="180" r="40" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<circle cx="210" cy="180" r="40" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<circle cx="170" cy="240" r="32" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<rect x="330" y="90" width="540" height="180" rx="8"/><text x="600" y="120" fill="#bfd8e8" font-family="sans-serif" font-size="14" text-anchor="middle">Panel central — instrumentos de motor</text>'
           '<circle cx="450" cy="185" r="42" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<circle cx="750" cy="185" r="42" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<rect x="900" y="90" width="260" height="180" rx="8"/><text x="1030" y="120" fill="#bfd8e8" font-family="sans-serif" font-size="14" text-anchor="middle">Navegación</text>'
           '<circle cx="1030" cy="185" r="40" fill="none" stroke="#1686c9" stroke-width="2"/></g>'
           '<g fill="#2f7d4f"><rect x="40" y="300" width="200" height="30" rx="5"/><text x="140" y="320" fill="#fff" font-family="sans-serif" font-size="12" text-anchor="middle">Autopiloto</text>'
           '<rect x="260" y="300" width="200" height="30" rx="5"/><text x="360" y="320" fill="#fff" font-family="sans-serif" font-size="12" text-anchor="middle">Mandos</text></g>',
           "Esquema de referencia — fotografía verificable pendiente de incorporación")

    _panel("panel-kingair90-gtn750.svg",
           "King Air 90 — Panel con Garmin GTN 750",
           "Configuración GTN 750 · referencia esquemática",
           '<rect x="30" y="90" width="300" height="200" rx="8" fill="#0e1c2a" stroke="#1686c9"/>'
           '<text x="180" y="122" fill="#bfd8e8" font-family="sans-serif" font-size="15" text-anchor="middle">PFD — Capitán</text>'
           '<circle cx="180" cy="195" r="60" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<rect x="360" y="90" width="440" height="200" rx="8" fill="#0e1c2a" stroke="#ff9800" stroke-width="3"/>'
           '<text x="580" y="122" fill="#ffc107" font-family="sans-serif" font-size="17" text-anchor="middle">Garmin GTN 750</text>'
           '<rect x="390" y="145" width="380" height="110" rx="6" fill="none" stroke="#ff9800" stroke-dasharray="6 4"/>'
           '<text x="580" y="205" fill="#ffc107" font-family="sans-serif" font-size="13" text-anchor="middle">Navegación táctil central</text>'
           '<rect x="830" y="90" width="300" height="200" rx="8" fill="#0e1c2a" stroke="#1686c9"/>'
           '<text x="980" y="122" fill="#bfd8e8" font-family="sans-serif" font-size="15" text-anchor="middle">PFD — Copiloto</text>'
           '<circle cx="980" cy="195" r="60" fill="none" stroke="#1686c9" stroke-width="2"/>'
           '<g fill="#2f7d4f"><rect x="40" y="315" width="260" height="30" rx="5"/><text x="170" y="335" fill="#fff" font-family="sans-serif" font-size="12" text-anchor="middle">Autopiloto</text></g>',
           "Esquema de referencia — fotografía verificable pendiente de incorporación")

    _panel("panel-kingair90-g1000.svg",
           "King Air 90 — Panel con Garmin G1000",
           "Configuración G1000 · referencia esquemática",
           '<rect x="40" y="90" width="420" height="210" rx="8" fill="#0e1c2a" stroke="#1686c9" stroke-width="3"/>'
           '<text x="250" y="122" fill="#bfd8e8" font-family="sans-serif" font-size="15" text-anchor="middle">PFD — Garmin G1000</text>'
           '<rect x="60" y="140" width="380" height="140" rx="6" fill="none" stroke="#38bdf8" stroke-dasharray="5 3"/>'
           '<text x="250" y="215" fill="#8ea3ba" font-family="sans-serif" font-size="12" text-anchor="middle">Pantalla primaria de vuelo</text>'
           '<rect x="740" y="90" width="420" height="210" rx="8" fill="#0e1c2a" stroke="#1686c9" stroke-width="3"/>'
           '<text x="950" y="122" fill="#bfd8e8" font-family="sans-serif" font-size="15" text-anchor="middle">MFD — Garmin G1000</text>'
           '<rect x="760" y="140" width="380" height="140" rx="6" fill="none" stroke="#38bdf8" stroke-dasharray="5 3"/>'
           '<text x="950" y="215" fill="#8ea3ba" font-family="sans-serif" font-size="12" text-anchor="middle">Pantalla multifunción</text>'
           '<text x="600" y="205" fill="#5a6b7b" font-family="sans-serif" font-size="24" text-anchor="middle">PFD · MFD</text>'
           '<g fill="#2f7d4f"><rect x="40" y="325" width="260" height="30" rx="5"/><text x="170" y="345" fill="#fff" font-family="sans-serif" font-size="12" text-anchor="middle">Panel de audio / AP</text></g>',
           "Esquema de referencia — fotografía verificable pendiente de incorporación")

    # ===== Diagramas de arquitectura (A–G) =====
    ESTILOS = {"doc": "#1686c9", "prev": "#ff9800", "pend": "#5a6b7b", "opt": "#2f7d4f"}

    def _caja(titulo, sub, x, y, w, h, estilo):
        c = ESTILOS.get(estilo, "#1686c9")
        dash = ' stroke-dasharray="6 4"' if estilo == "pend" else (' stroke-dasharray="3 3"' if estilo == "opt" else "")
        s = '<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="#0c1622" stroke="%s" stroke-width="2"%s/>' % (x, y, w, h, c, dash)
        if sub:
            s += '<text x="%d" y="%d" fill="#e6edf4" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">%s</text>' % (x + w // 2, y + h // 2 - 2, titulo)
            s += '<text x="%d" y="%d" fill="#8ea3ba" font-family="sans-serif" font-size="10" text-anchor="middle">%s</text>' % (x + w // 2, y + h // 2 + 14, sub)
        else:
            s += '<text x="%d" y="%d" fill="#e6edf4" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">%s</text>' % (x + w // 2, y + h // 2 + 4, titulo)
        return s

    def _flecha(x1, y1, x2, y2):
        return '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#5a6b7b" stroke-width="2" marker-end="url(#f)"/>' % (x1, y1, x2, y2)

    def _diagrama(archivo, titulo, objetivo, cajas, flechas, notas, alto=560):
        cab = '<text x="40" y="34" fill="#e6edf4" font-family="sans-serif" font-size="18" font-weight="bold">%s</text>' % titulo
        obj = '<text x="40" y="58" fill="#8ea3ba" font-family="sans-serif" font-size="12">%s</text>' % objetivo
        cuerpo = "".join(_caja(*c) for c in cajas) + "".join(_flecha(*f) for f in flechas)
        ley = ('<text x="40" y="%d" fill="#8ea3ba" font-family="sans-serif" font-size="11">Leyenda: '
               '<tspan fill="#1686c9">Documentado</tspan> · <tspan fill="#ff9800">Previsto</tspan> · '
               '<tspan fill="#5a6b7b">Pendiente de confirmar</tspan> · <tspan fill="#2f7d4f">Opcional</tspan></text>') % (alto - 20)
        notatxt = '<text x="40" y="%d" fill="#5f7487" font-family="sans-serif" font-size="11">%s</text>' % (alto - 42, notas)
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 %d" role="img" aria-label="%s">'
               '<rect width="1200" height="%d" fill="#0a111f"/>'
               '<defs><marker id="f" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
               '<path d="M0,0 L0,6 L9,3 z" fill="#5a6b7b"/></marker></defs>'
               '%s%s%s%s%s</svg>') % (alto, titulo, alto, cab, obj, cuerpo, ley, notatxt)
        _escribir(archivo, svg)

    # A. Arquitectura general
    _diagrama("diagrama_arquitectura.svg",
              "A · Arquitectura general del simulador",
              "Flujo de señal desde la cabina física hasta la visualización; se distinguen elementos documentados, previstos y pendientes.",
              [("Cabina DC-3 XB-DPC", "Aeronave en tierra", 20, 140, 190, 70, "doc"),
               ("Mandos físicos y sensores", "", 20, 280, 190, 70, "doc"),
               ("Microcontroladores", "Arduino Mega / Teensy", 300, 200, 210, 70, "prev"),
               ("PC de simulación", "", 610, 200, 190, 70, "doc"),
               ("X-Plane 12", "", 880, 140, 170, 70, "prev"),
               ("Modelo virtual", "King Air 90", 880, 260, 170, 70, "prev"),
               ("Pantallas de visualización", "3 monitores", 620, 350, 200, 70, "prev")],
              [(210, 175, 210, 280), (210, 315, 300, 245), (510, 235, 610, 235), (800, 235, 880, 175),
               (800, 235, 880, 295), (965, 295, 720, 370)],
              "Los flujos de retroalimentación (X-Plane → microcontroladores) se representan en el diagrama F.",
              alto=440)

    # B. Mandos y sensorización
    _diagrama("arq-mandos.svg",
              "B · Arquitectura de mandos y sensorización",
              "Entradas y salidas físicas vinculadas a los microcontroladores. Los elementos pendientes no se asumen instalados.",
              [("Volante / yoke", "", 20, 120, 190, 60, "doc"),
               ("Pedales de timón", "", 20, 210, 190, 60, "prev"),
               ("Palancas (flaps, tren)", "", 20, 300, 190, 60, "pend"),
               ("Interruptores y botones", "", 250, 120, 190, 60, "prev"),
               ("Potenciómetros", "", 250, 210, 190, 60, "pend"),
               ("Sensores", "", 250, 300, 190, 60, "prev"),
               ("Arduino Mega", "Entradas/salidas", 560, 200, 220, 80, "prev"),
               ("Servos y actuadores", "", 850, 120, 200, 60, "prev"),
               ("Luces e indicadores", "", 850, 220, 200, 60, "pend"),
               ("Interfaces", "USB / serie", 850, 320, 200, 60, "pend")],
              [(210, 150, 250, 150), (210, 240, 250, 240), (210, 330, 250, 330),
               (440, 150, 560, 210), (440, 240, 560, 230), (440, 330, 560, 250),
               (780, 230, 850, 150), (780, 240, 850, 250), (780, 250, 850, 350)],
              "La asignación exacta de cada mando a cada pin está sujeta a verificación en la ingeniería de detalle.",
              alto=430)

    # C. Aviónica y visualización
    _diagrama("arq-avionica.svg",
              "C · Arquitectura de aviónica y visualización",
              "Relación entre el panel físico, las pantallas y los componentes previstos. No se asume que todos estén instalados.",
              [("Panel físico", "", 20, 150, 180, 70, "doc"),
               ("Pantallas detrás del panel", "", 20, 280, 180, 70, "prev"),
               ("Garmin GTN 750", "Previsto", 300, 150, 210, 70, "prev"),
               ("Autopiloto", "", 300, 280, 210, 70, "pend"),
               ("Componentes descritos", "en documentación", 610, 150, 210, 70, "doc"),
               ("Instrumentos y LEDs", "", 610, 280, 210, 70, "prev"),
               ("Opcionales", "por definir", 880, 210, 190, 70, "opt")],
              [(200, 185, 300, 185), (200, 315, 300, 315), (510, 185, 610, 185), (510, 315, 610, 315),
               (820, 185, 880, 230), (820, 315, 880, 255)],
              "Los componentes reales frente a los simulados se confirmarán con la documentación de cada equipo.",
              alto=420)

    # D. Software y comunicaciones
    _diagrama("arq-software.svg",
              "D · Arquitectura de software y comunicaciones",
              "Cadena de herramientas y puentes de comunicación. La dirección de los datos solo se marca cuando está verificada.",
              [("Arduino IDE", "Programación", 20, 150, 180, 70, "doc"),
               ("Firmware", "", 250, 150, 170, 70, "prev"),
               ("XPLDirect / XPL Pro", "", 250, 280, 170, 70, "pend"),
               ("MobiFlight", "", 470, 280, 170, 70, "opt"),
               ("X-Plane 12", "", 470, 150, 170, 70, "prev"),
               ("Puente de comunicación", "por verificar", 700, 150, 210, 70, "pend"),
               ("Aplicaciones", "GTN 750 / G1000", 700, 280, 210, 70, "prev")],
              [(200, 185, 250, 185), (420, 185, 470, 185), (640, 185, 700, 185),
               (420, 315, 470, 315), (640, 315, 700, 315)],
              "No se declara compatibilidad entre herramientas hasta verificarla; MobiFlight figura como opcional.",
              alto=430)

    # E. Eléctrica y distribución
    _diagrama("arq-electrica.svg",
              "E · Arquitectura eléctrica y distribución de energía",
              "Distribución conceptual de energía. No se especifican tensiones, corrientes ni calibres por no estar verificados.",
              [("Fuentes de alimentación", "", 20, 150, 200, 70, "pend"),
               ("Protecciones", "fusibles / breakers", 20, 280, 200, 70, "pend"),
               ("Distribución", "", 300, 200, 200, 70, "pend"),
               ("Alimentación de PC", "", 580, 130, 200, 70, "prev"),
               ("Alimentación electrónica", "", 580, 260, 200, 70, "prev"),
               ("Tierras", "", 860, 130, 190, 70, "pend"),
               ("Cableado", "", 860, 260, 190, 70, "pend")],
              [(220, 185, 300, 220), (220, 315, 300, 245), (500, 225, 580, 165), (500, 225, 580, 295),
               (780, 165, 860, 165), (780, 295, 860, 295)],
              "Especificaciones (tensión, corriente, calibre, fusibles) quedan como Pendiente de ingeniería/verificación.",
              alto=430)

    # F. Flujo funcional de una sesión
    _diagrama("arq-flujo.svg",
              "F · Flujo funcional de una sesión",
              "Secuencia de interacción de una sesión de simulación, con retroalimentación al usuario.",
              [("Acción del usuario", "", 20, 200, 180, 70, "doc"),
               ("Captación del mando", "", 240, 200, 180, 70, "prev"),
               ("Lectura electrónica", "", 460, 200, 180, 70, "prev"),
               ("Envío de datos", "", 680, 200, 180, 70, "prev"),
               ("Respuesta de X-Plane", "", 900, 200, 190, 70, "prev"),
               ("Visualización", "", 900, 340, 190, 70, "prev"),
               ("Retroalimentación al usuario", "", 240, 340, 210, 70, "prev")],
              [(200, 235, 240, 235), (420, 235, 460, 235), (640, 235, 680, 235), (860, 235, 900, 235),
               (995, 270, 995, 340), (995, 375, 450, 375)],
              "Los tramos de captación y envío requieren integración y pruebas antes de confirmarse.",
              alto=440)

    # G. Integración y pruebas
    _diagrama("arq-integracion.svg",
              "G · Integración y pruebas",
              "Relación entre los siete equipos según la EDT y el cronograma. Las dependencias específicas no se dan por confirmadas.",
              [("Limpieza", "Preparación", 20, 130, 190, 70, "doc"),
               ("Supervisión y Planeación", "Coordinación", 20, 260, 190, 70, "doc"),
               ("Aviónica", "Electrónica", 250, 130, 190, 70, "doc"),
               ("Mecánica", "Estructura", 250, 260, 190, 70, "doc"),
               ("Software", "Sistema", 480, 130, 190, 70, "doc"),
               ("Lógico", "Documentación", 480, 260, 190, 70, "doc"),
               ("Vuelo", "Validación", 710, 195, 190, 70, "doc"),
               ("Dependencias", "por confirmar", 940, 195, 210, 70, "pend")],
              [(210, 165, 250, 165), (440, 165, 480, 165), (670, 165, 710, 200),
               (210, 295, 250, 295), (440, 295, 480, 295), (670, 295, 710, 235),
               (900, 230, 940, 230)],
              "El orden y las dependencias entre equipos se reflejarán al confirmarse en la EDT y el cronograma.",
              alto=440)


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------
def _normalizar_riesgo(r):
    """Convierte un riesgo escaneado de un equipo al esquema unificado."""
    equipo = r.get("equipo")
    responsables = [equipo] if equipo in _NOMBRES_RESP else []
    if not responsables:
        responsables = ["Aplicabilidad pendiente de validación"]
    mitigacion = (r.get("mitigacion") or "").strip()
    return {
        "id": r.get("id", PEND),
        "tipo": "Riesgo potencial",
        "categoria": "Por equipo (registro del equipo)",
        "nombre": r.get("peligro", ""),
        "descripcion": r.get("peligro", ""),
        "causas": [],
        "disparadores": [],
        "consecuencias": [],
        "responsables": responsables,
        "prob": r.get("prob") or PEND_EVAL,
        "impacto": r.get("impacto") or PEND_EVAL,
        "nivel": r.get("nivel") or PEND_EVAL,
        "estado": r.get("estado") or "Abierto",
        "medidas_preventivas": [mitigacion] if mitigacion else ["Pendiente de definición"],
        "que_hacer": ["Pendiente de definición"],
        "inspeccion": ["Pendiente de definición"],
        "referencias": [],
        "equipo": equipo,
    }


def construir_riesgos(equipos):
    """Riesgos existentes (de equipos) + biblioteca ampliada de riesgos potenciales."""
    existentes = [_normalizar_riesgo(r) for e in equipos for r in e["riesgos"]]
    ids = set()
    unicos = []
    for r in existentes + RIESGOS_AMPLIADOS:
        rid = r["id"]
        if rid in ids:
            continue
        ids.add(rid)
        enr = ENRIQUECIMIENTO.get(rid)
        if enr:
            for campo in ("causas", "disparadores", "consecuencias", "medidas_preventivas",
                          "que_hacer", "inspeccion", "referencias"):
                if campo in enr:
                    r[campo] = enr[campo]
        unicos.append(r)
    return unicos


def _prioridad_complejidad(cat):
    """Prioridad de la OI derivada de la categoría de complejidad del cronograma."""
    if cat == "critica":
        return "Crítica", "Integración, validación o aceptación (categoría 'critica' del cronograma)"
    if cat == "alta":
        return "Alta", "Alta complejidad / larga duración (categoría 'alta' del cronograma)"
    if cat == "media-alta":
        return "Media", "Complejidad media-alta (categoría 'media-alta' del cronograma)"
    if cat == "baja":
        return "Baja", "Baja complejidad / corta duración (categoría 'baja' del cronograma)"
    return "Media", "Complejidad general (categoría 'general' del cronograma)"


def _enriquecer_equipos(equipos, cronograma):
    """Agrega color, rol y el detalle por OI (fase, complejidad, prioridad, dependencias)."""
    mapa = cronograma.get("mapa", {})
    color_por_nombre = {r["nombre"]: r["color"] for r in RESPONSABLES_COLOR}
    result = []
    for e in equipos:
        e2 = dict(e)
        e2["color"] = color_por_nombre.get(e["nombre"], "#64748B")
        fases_nombre = {str(f["id"]): f["nombre"] for f in (e.get("fases") or [])}
        ois = []
        for o in e.get("ois", []):
            o2 = dict(o)
            t = mapa.get(o["id"], {})
            cat = t.get("complejidad") or "general"
            prio, basis = _prioridad_complejidad(cat)
            o2["complejidad"] = cat
            o2["prioridad"] = prio
            o2["prioridad_basis"] = basis
            o2["fase_nombre"] = fases_nombre.get(str(o.get("fase", "")), "Sin fase asignada")
            o2["duracion"] = t.get("duracion", "")
            o2["dependencias"] = t.get("dependencias") or []
            ois.append(o2)
        e2["ois"] = ois
        result.append(e2)
    return result


def generar_datos(equipos, arbol, cronograma, biblioteca, sobre, descargas, practicas):
    crono_publico = {k: cronograma[k] for k in
                     ("inicio", "inicio_marca", "fin", "span", "escala", "categorias")}
    equipos_enriquecidos = _enriquecer_equipos(equipos, cronograma)
    datos = {
        "proyecto": {
            "nombre": "Proyecto AATD DC3",
            "aeronave": "Douglas DC-3", "matricula": "XB-DPC",
            "plataforma": "X-Plane 12", "cabina_virtual": "King Air 90",
            "naturaleza": "Simulador terrestre de vuelo por instrumentos; la aeronave no vuela.",
            "eslogan": "A la altura de Nuestra Identidad. Ingeniería Aeronáutica.",
            "departamento": "Departamento de Ingeniería Aeronáutica Aplicada",
            "empresa": "Eben Ezer Aviation",
            "fecha": date.today().isoformat(),
            "presupuesto": PEND_EST,
            "beneficios_cuantitativos": PEND_EST,
        },
        "responsables": RESPONSABLES,
        "equipos": equipos_enriquecidos,
        "edt": arbol,
        "cronograma": crono_publico,
        "comunicacion": COMUNICACION,
        "fases": FASES,
        "riesgos": construir_riesgos(equipos),
        "incidentes": [],
        "responsables_color": RESPONSABLES_COLOR,
        "acuerdos": [],
        "avances": [],
        "biblioteca": biblioteca,
        "referencias_oficiales": REFERENCIAS_OFICIALES,
        "practicas": practicas,
        "sobre_limite": sobre,
        "descargas": descargas,
        "glosario": [{"termino": t, "definicion": d} for t, d in GLOSARIO],
        "materiales": MATERIALES,
        "estados_material": ESTADOS_MATERIAL,
        "gobernanza": GOBERNANZA,
    }
    with open(os.path.join(ROOT, "datos.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, "datos.js"), "w", encoding="utf-8") as f:
        f.write("window.DATOS = " + json.dumps(datos, ensure_ascii=False) + ";\n")
    return datos


def escribir_meta(sobre):
    readme = """# Proyecto AATD DC3 — Centro Digital de Ingeniería Aeronáutica

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
"""
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
    open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8").write("")
    open(os.path.join(ROOT, ".gitignore"), "w", encoding="utf-8").write(
        "__pycache__/\n*.pyc\n*.log\ninforme_archivos.txt\n")
    open(os.path.join(ROOT, "dependencias.txt"), "w", encoding="utf-8").write(
        "Dependencias (solo desarrollo local):\n\n  Python 3.12 (biblioteca estándar; sin paquetes externos)\n\n"
        "El sitio desplegado es estático (HTML/CSS/JS/SVG/JSON/PNG).\n")

    lineas = ["Informe de archivos de la Biblioteca Técnica",
              "Fecha: %s" % date.today().isoformat(), "=" * 60, ""]
    if sobre:
        lineas.append("ARCHIVOS SOBRE EL LÍMITE (%d MB) — bajo revisión:" % LIMITE_COPIA_MB)
        for s in sobre:
            lineas.append("  - %s (%.1f MB) — %s" % (s["archivo"], s["mb"], s["motivo"]))
    else:
        lineas.append("Sin archivos sobre el límite.")
    lineas.append("")
    lineas.append("Los archivos dentro del límite se copiaron a la raíz para su publicación.")
    open(os.path.join(ROOT, "informe_archivos.txt"), "w", encoding="utf-8").write("\n".join(lineas))


def copiar_earth():
    origen = os.path.join(FIG, "earth.jpg")
    destino = os.path.join(ROOT, "earth.jpg")
    if os.path.exists(origen):
        shutil.copyfile(origen, destino)
        return True
    return False


def copiar_plan_maestro():
    origen = os.path.join(PROYECTO, "Plan_Maestro_DC3_Eben_Ezer_Aviation.pdf")
    destino = os.path.join(ROOT, "Plan_Maestro_DC3_Eben_Ezer_Aviation.pdf")
    if os.path.exists(origen):
        shutil.copyfile(origen, destino)
        return True
    return False


def copiar_ois(equipos):
    """Copia todos los PDF de órdenes de trabajo (OI/OT) a la raíz (nombres únicos)."""
    n = 0
    for e in equipos:
        base = os.path.join(DPC, e["carpeta"])
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", "render_check") and not d.startswith("backup_")]
            for f in files:
                if f.lower().endswith(".pdf") and re.search(r"(OI|OT)-\d{3}", f):
                    src = os.path.join(root, f)
                    dst = os.path.join(ROOT, f)
                    if not os.path.exists(dst):
                        try:
                            shutil.copyfile(src, dst)
                            n += 1
                        except Exception:
                            pass
    return n


def copiar_manuales():
    n = 0
    for carpeta, destino in MANUALES_EQUIPOS.items():
        src = os.path.join(PROYECTO, MANUALES_FUENTES[carpeta])
        dst = os.path.join(ROOT, destino)
        if os.path.exists(src):
            try:
                shutil.copyfile(src, dst)
                n += 1
            except Exception:
                pass
    return n


def escanear_descargas():
    grupos = []
    for grupo, rel, prefijo in DIRS_DESCARGAS:
        d = os.path.join(PROYECTO, rel)
        archivos = []
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                fp = os.path.join(d, f)
                if not os.path.isfile(fp):
                    continue
                ext = os.path.splitext(f)[1].lower()
                seguro = re.sub(r"[^A-Za-z0-9]+", "-", f).strip("-")
                destino = prefijo + seguro
                try:
                    shutil.copyfile(fp, os.path.join(ROOT, destino))
                except Exception:
                    continue
                archivos.append({"nombre": f, "archivo": destino, "tipo": ext.lstrip(".")})
        grupos.append({"grupo": grupo, "archivos": archivos})
    return grupos


def main():
    equipos = construir_equipos()
    cronograma = construir_cronograma(equipos)
    arbol = construir_edt(equipos, cronograma["mapa"])
    biblioteca, sobre = construir_biblioteca()
    descargas = escanear_descargas()
    practicas, practicas_pend = construir_practicas()
    datos = generar_datos(equipos, arbol, cronograma, biblioteca, sobre, descargas, practicas)
    generar_svg()
    escribir_meta(sobre)
    earth = copiar_earth()
    pm = copiar_plan_maestro()
    n_oi = copiar_ois(equipos)
    n_man = copiar_manuales()
    print("Equipos:", len(datos["equipos"]))
    print("Riesgos:", len(datos["riesgos"]))
    print("Biblioteca (disponibles):", sum(1 for b in biblioteca if b["estado"] == "Disponible"))
    print("Biblioteca (bajo revisión):", len(sobre))
    print("Prácticas:", len(practicas))
    if practicas_pend:
        print("Prácticas pendientes de verificación:", len(practicas_pend))
    print("earth.jpg:", "copiado" if earth else "no encontrado")
    print("Plan Maestro PDF:", "copiado" if pm else "no encontrado")
    print("Órdenes de trabajo (PDF) copiadas:", n_oi)
    print("Manuales de equipo copiados:", n_man)
    print("Descargas:", sum(len(g["archivos"]) for g in descargas))
    print("Construcción completa en:", ROOT)


if __name__ == "__main__":
    main()
