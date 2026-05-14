# Checklist Nueva Distribuidora — Orbit TP

**Distribuidora:** ___________________________  
**Implementador:** ___________________________  
**Fecha inicio:** ___________________________  
**Fecha go-live objetivo:** ___________________________

---

## BLOQUE 1 — Recepción de datos

Verificar que la distribuidora entregó todos los archivos requeridos antes de avanzar.

- [ ] `ventas.csv` — exportación de ventas (mínimo 30 días)
- [ ] `gescom.xlsx` — padrón de clientes con columna TAXONOMIA (P/A/B/C)
- [ ] `Portafolio Infaltable - Argentina.pptx` — SKUs que componen TP
- [ ] `lista_precios.xlsx` — precios actualizados
- [ ] `objetivo_vendedor_tp.xlsx` — objetivos por vendedor y zona
- [ ] `logo_distrib.png` — logo PNG fondo transparente

**Datos adicionales a confirmar verbalmente:**
- [ ] Lista de vendedores activos con sus IDs numéricos
- [ ] Zonas activas (LU/MA/MI/JU/VI/SA) por vendedor
- [ ] Contraseñas deseadas para gerencia y vendedores
- [ ] Nombre corto de la distribuidora (para URL y archivos)

---

## BLOQUE 2 — Verificación de formato de datos

Correr las validaciones del archivo `VALIDADORES_REQUERIDOS.md` antes de configurar nada.

- [ ] ventas.csv: columnas correctas (`VendedorID`, `ClienteID`, `Articulo`, `Cantidad`, `Importe`, `Fecha`)
- [ ] ventas.csv: VendedorIDs son enteros (sin texto, sin decimales)
- [ ] ventas.csv: sin filas completamente vacías
- [ ] gescom.xlsx: columna `TAXONOMIA` presente con valores P/A/B/C únicamente
- [ ] gescom.xlsx: `ClienteID` coincide con los de ventas.csv (al menos 80% de match)
- [ ] objetivo_vendedor_tp.xlsx: sin celdas vacías en columnas `VendedorID`, `Zona`, `Objetivo`
- [ ] objetivo_vendedor_tp.xlsx: zonas son LU/MA/MI/JU/VI/SA (exactamente)
- [ ] lista_precios.xlsx: columna `Articulo` coincide con los de ventas.csv

---

## BLOQUE 3 — Configuración del archivo central

Completar `CONFIG_DISTRIBUIDORA_TEMPLATE.json` (guardar como `config_[nombre_distrib].json`):

- [ ] `distribuidora.nombre` y `distribuidora.nombre_corto` completados
- [ ] `distribuidora.logo_path` apunta a un archivo que existe
- [ ] `vendedores.lista` tiene todos los vendedores activos con IDs correctos
- [ ] `zonas.activas` tiene solo las zonas con actividad real
- [ ] `inputs.*` rutas existen en disco
- [ ] `portal.mgmt_password` y `portal.vendor_password` definidas (≥8 caracteres)
- [ ] `render.service_name` definido con nombre corto en minúsculas

---

## BLOQUE 4 — Google Cloud

- [ ] Proyecto Google Cloud creado o seleccionado
- [ ] Google Sheets API activada
- [ ] Google Drive API activada
- [ ] Spreadsheet vacío creado — ID copiado a `google.spreadsheet_id`
- [ ] Carpeta Drive `PDF_GERENCIAL_[DISTRIB]` creada — ID copiado
- [ ] Carpeta Drive `PDF_VENDEDORES_[DISTRIB]` creada — ID copiado
- [ ] Service Account `orbit-tp-[distrib]` creado
- [ ] JSON de clave descargado y guardado en lugar seguro (fuera del repo)
- [ ] Spreadsheet compartido con SA como Lector
- [ ] Carpeta PDF_GERENCIAL compartida con SA como Lector
- [ ] Carpeta PDF_VENDEDORES compartida con SA como Lector
- [ ] Credenciales OAuth configuradas para pipeline local (o copiadas de referencia)
- [ ] `google_sync_config.json` completo con los 3 IDs de Google

---

## BLOQUE 5 — Primer pipeline de prueba

- [ ] Archivos en `inputs/` correctamente nombrados
- [ ] Logo copiado a `assets/logo_distrib.png`
- [ ] `config_app.json` actualizado (contraseñas + vendor_names)
- [ ] Ejecutar `RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat` con zona de prueba
- [ ] Paso 1 (clean_venta.py): sin errores ✓
- [ ] Paso 2 (pipeline): sin errores ✓
- [ ] Paso 3 (Google sync): sin errores ✓
- [ ] Paso 4 (Streamlit sync): sin errores o warning aceptable ✓
- [ ] `output/PDF_VENDEDORES/[fecha]/`: archivos PDF generados, uno por vendedor
- [ ] `output/PDF_GERENCIAL/[fecha]/`: PDF gerencial generado
- [ ] `output/APPSHEET/`: 4 CSVs generados
- [ ] Google Sheets: 4 hojas con datos actualizados
- [ ] Google Drive: PDFs subidos a las carpetas correctas
- [ ] Abrir PDF de un vendedor — datos correctos, logo visible
- [ ] Abrir PDF gerencial — datos correctos

---

## BLOQUE 6 — Portal local

- [ ] Crear `portal/.env` con variables de la nueva distribuidora
- [ ] `cd portal && npm install` — sin errores
- [ ] `npm run build` — build OK ✓
- [ ] `npm run dev` — servidor iniciado en localhost:4321
- [ ] Login con contraseña de gerencia — acceso OK
- [ ] Dashboard gerencial: KPIs, objetivos, tabla de vendedores visibles
- [ ] PDFs de gerencia abren desde Drive (click → Google Drive view)
- [ ] Login con contraseña de vendedor — selección de vendedor funciona
- [ ] Dashboard vendedor: lista de clientes urgentes visible
- [ ] PDF del vendedor abre desde Drive
- [ ] Nombres de vendedores son los correctos (no "Vendedor 2")
- [ ] Datos de objetivos muestran Total + P/A/B/C + por vendedor
- [ ] `npm run test:e2e` — 7/7 tests pasando ✓

---

## BLOQUE 7 — Deploy en Render

- [ ] Código en repositorio GitHub (rama `main`)
- [ ] Render: nuevo Web Service creado y conectado al repo
- [ ] Root Directory: `portal`
- [ ] Build Command: `npm install && npm run build`
- [ ] Start Command: `node dist/server/entry.mjs`
- [ ] Variables de entorno cargadas en Render:
  - [ ] `GOOGLE_SERVICE_ACCOUNT_JSON`
  - [ ] `SPREADSHEET_ID`
  - [ ] `MGMT_PASSWORD`
  - [ ] `VENDOR_PASSWORD`
  - [ ] `VENDOR_NAMES`
  - [ ] `HOST=0.0.0.0`
- [ ] Deploy exitoso (log sin errores)
- [ ] URL pública cargada en `config_[distrib].json → render.url_publica`
- [ ] Login gerencia desde URL pública — OK
- [ ] Login vendedor desde URL pública — OK
- [ ] PDF abre desde celular — OK

---

## BLOQUE 8 — Capacitación y cierre

- [ ] Operador recibió instrucciones del `05_RUNBOOK_OPERATIVO_DIARIO.md`
- [ ] Operador ejecutó el BAT supervisado por primera vez
- [ ] Gerencia accede al portal y visualiza su dashboard
- [ ] Cada vendedor probó su acceso y vio sus datos
- [ ] URL del portal comunicada a todos los usuarios
- [ ] Contraseñas entregadas de forma segura
- [ ] Fecha de go-live registrada en `config_[distrib].json`
- [ ] Datos de la implementación registrados en tabla de cierre (abajo)

---

## Tabla de cierre

| Campo | Valor |
|---|---|
| Distribuidora | |
| Spreadsheet ID | |
| Drive gerencial ID | |
| Drive vendedores ID | |
| Service Account email | |
| URL portal Render | |
| Plan Render | |
| Fecha primer deploy | |
| Fecha go-live | |
| Vendedores configurados | |
| Zonas activas | |
| Observaciones | |
