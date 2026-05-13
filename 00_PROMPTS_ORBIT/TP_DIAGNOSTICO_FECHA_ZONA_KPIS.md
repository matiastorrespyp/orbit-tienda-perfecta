# Diagnóstico fecha, zona y KPIs — Portal Tienda Perfecta

Repo operativo: C:\Orbit\TP_PYP_CLEAN

El portal ya está deployado, pero muestra mal fecha/zona: aparece "Zona VI · 2026-05-07" y no entiendo el KPI "Con TP en sistema".

Hacer solo diagnóstico, sin tocar código ni deploy.

Revisar:
- portal/src/lib/data.ts
- portal/src/pages/vendedor.astro
- portal/src/pages/gerencia.astro
- portal/src/components/*
- hojas Google: pdf_index, clientes_oportunidad, foco_productos, tp_objetivos_resumen, tp_facturacion_comparativa

Crear el diagnóstico en:
portal/DIAGNOSTICO_FECHA_ZONA_KPIS.md

El diagnóstico debe responder:
1. De dónde sale la fecha 2026-05-07.
2. De dónde sale Zona VI.
3. Qué regla usa el portal para elegir fecha/zona por default.
4. Qué significa y cómo calcula “Con TP en sistema”.
5. Qué cambio mínimo propone para que sea claro y correcto.

No hacer cambios de código.
No deploy.
No commit.
Primero diagnóstico.
