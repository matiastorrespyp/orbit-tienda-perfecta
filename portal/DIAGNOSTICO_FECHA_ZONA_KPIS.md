# Diagnóstico: fecha, zona y KPI "Con TP en sistema"

Fecha: 2026-05-13  
Alcance: diagnóstico. Sin cambios de código, sin deploy, sin commit.

## 1. Fecha mostrada: 2026-05-07

La fecha sale de `clientes[0].Fecha`.

Archivos:
- `portal/src/components/GerenciaDashboard.tsx`
- `portal/src/components/VendedorDashboard.tsx`

Problema: el portal toma la fecha del primer registro de `clientes_oportunidad`, sin ordenar por fecha y sin buscar la última fecha disponible.

## 2. Zona mostrada: Zona VI

La zona sale de `clientes[0].Dia`.

Problema: el portal toma `Dia` del primer registro. Además, el campo se llama `Dia`, pero la UI lo muestra como `Zona`, lo que puede confundir.

## 3. Regla actual de fecha/zona

No existe una regla real.

Comportamiento actual:
- fecha = `clientes[0].Fecha`
- zona = `clientes[0].Dia`

Consecuencia: si la primera fila de Google Sheets es vieja, el portal muestra una fecha/zona vieja.

## 4. KPI "Con TP en sistema"

El cálculo es:

`clientes.filter(c => c.TP_Sistema === 'SI').length`

Significa: cantidad de clientes del conjunto `clientes_oportunidad` que tienen `TP_Sistema = SI`.

Problema: el texto no explica si se refiere a acuerdo TP, cliente censado, cliente con portafolio cargado o cliente que cumple TP.

## 5. Cambio mínimo recomendado

### Fecha/zona

Reemplazar `clientes[0]` por el registro con fecha más reciente.

Regla propuesta:
- tomar el cliente con mayor `Fecha`;
- usar su `Fecha`;
- usar su `Dia`.

### KPI

Cambiar:
- Antes: `Con TP en sistema`
- Después: `Con acuerdo TP`

Cambiar hint:
- Antes: `de N clientes`
- Después: `de N en zona oportunidad`

## 6. Validación obligatoria antes de deploy

- `npm.cmd run build`
- `npm.cmd run test:e2e`
- revisar portal local
- commit limpio
- push
- Render deploy
- prueba externa
