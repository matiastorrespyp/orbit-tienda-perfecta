# 04 — Checklist de Replicación

Checklist para implementar Orbit TP en una nueva distribuidora.
Completar en orden. Marcar cada ítem antes de avanzar al siguiente.

---

## FASE 1 — Datos fuente

- [ ] Obtener exportación de ventas del sistema de facturación (GESCOM u otro)
- [ ] Verificar que ventas.csv tiene: Fecha, VendedorID, ClienteID, Articulo, Cantidad, Importe
- [ ] Obtener padrón de clientes (gescom.xlsx): ClienteID, RazonSocial, VendedorID, TAXONOMIA (P/A/B/C)
- [ ] Obtener lista de precios (lista_precios.xlsx)
- [ ] Obtener o crear objetivos mensuales por vendedor (objetivo_vendedor_tp.xlsx)
- [ ] Verificar que el Portafolio Infaltable .pptx está disponible y actualizado
- [ ] Confirmar IDs de vendedores (números enteros únicos)
- [ ] Confirmar cantidad de vendedores activos y sus zonas (LU/MA/MI/JU/VI/SA)

---

## FASE 2 — Google Cloud

- [ ] Crear proyecto en Google Cloud Console (o reutilizar existente)
- [ ] Activar Google Sheets API
- [ ] Activar Google Drive API
- [ ] Crear Google Spreadsheet vacío — anotar ID
- [ ] Crear carpeta Drive `PDF_GERENCIAL_[DISTRIB]` — anotar ID
- [ ] Crear carpeta Drive `PDF_VENDEDORES_[DISTRIB]` — anotar ID
- [ ] Crear Service Account `orbit-tp-[distrib]` — descargar JSON
- [ ] Compartir Spreadsheet con Service Account (rol: Lector)
- [ ] Compartir carpeta PDF_GERENCIAL con Service Account (rol: Lector)
- [ ] Compartir carpeta PDF_VENDEDORES con Service Account (rol: Lector)
- [ ] Configurar credenciales OAuth para pipeline local (o copiar de referencia)

---

## FASE 3 — Configuración local

- [ ] Copiar estructura del proyecto base a nueva carpeta
- [ ] Colocar inputs en `inputs/`
- [ ] Editar `google_sync_config.json`:
  - [ ] `spreadsheet_id` actualizado
  - [ ] `drive_pdf_gerencial_folder_id` actualizado
  - [ ] `drive_pdf_vendedores_folder_id` actualizado
- [ ] Editar `config_app.json`:
  - [ ] `mgmt_password` definida
  - [ ] `vendor_password` definida
  - [ ] `vendor_names` con todos los IDs y nombres correctos
- [ ] Verificar que `credenciales/google-oauth-client.json` existe

---

## FASE 4 — Validación pipeline

- [ ] Ejecutar `RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat` con una zona de prueba
- [ ] Verificar que `clean_venta.py` no reporta errores
- [ ] Verificar que `tp_pyp_run_fast_ORBIT_appsheet.py` termina sin errores
- [ ] Verificar PDFs generados en `output/PDF_VENDEDORES/`
- [ ] Verificar PDFs generados en `output/PDF_GERENCIAL/`
- [ ] Verificar 4 CSVs en `output/APPSHEET/`
- [ ] Verificar sync: hojas actualizadas en Google Sheets
- [ ] Verificar sync: PDFs subidos a Google Drive
- [ ] Abrir un PDF de vendedor y confirmar que los datos son correctos
- [ ] Abrir un PDF gerencial y confirmar que los datos son correctos

---

## FASE 5 — Portal local

- [ ] Crear `portal/.env` con las variables de la nueva distribuidora
- [ ] Ejecutar `cd portal && npm install`
- [ ] Ejecutar `npm run build`
- [ ] Ejecutar `npm run dev` y abrir `http://localhost:4321`
- [ ] Ingresar con contraseña de gerencia — verificar dashboard
- [ ] Verificar KPIs: Inscriptos TP, En zona, cumplimiento
- [ ] Verificar bloque de objetivos: total, por taxonomía, por vendedor
- [ ] Verificar tabla de vendedores: Clientes posibilidad, TP activos, PDFs
- [ ] Ingresar con contraseña de vendedor — seleccionar vendedor
- [ ] Verificar lista de clientes urgentes
- [ ] Verificar acceso a PDF propio
- [ ] Ejecutar `npm run test:e2e` — deben pasar 7/7 tests

---

## FASE 6 — Deploy en Render

- [ ] Código en repositorio GitHub (rama `main`)
- [ ] Crear Web Service en Render → conectar repo
- [ ] Configurar Root Directory: `portal`
- [ ] Configurar Build Command: `npm install && npm run build`
- [ ] Configurar Start Command: `node dist/server/entry.mjs`
- [ ] Agregar todas las variables de entorno en Render
- [ ] Hacer deploy y esperar que el build complete sin errores
- [ ] Abrir URL pública y verificar login de gerencia
- [ ] Verificar login de vendedor
- [ ] Verificar que los PDFs abren desde Drive (redirect funciona)
- [ ] Probar desde celular

---

## FASE 7 — Operación diaria

- [ ] Confirmar con el equipo el horario de actualización diaria
- [ ] Documentar quién corre el BAT cada día (persona responsable)
- [ ] Comunicar URL del portal y contraseñas a gerencia y vendedores
- [ ] Correr el pipeline el primer día hábil de operación real
- [ ] Verificar que gerencia puede ver el dashboard actualizado
- [ ] Verificar que cada vendedor puede ver su panel

---

## Notas por distribuidora

| Campo | Valor |
|---|---|
| Nombre distribuidora | |
| Spreadsheet ID | |
| Drive gerencial ID | |
| Drive vendedores ID | |
| Service Account email | |
| URL portal Render | |
| Fecha primer deploy | |
| Contacto técnico | |
