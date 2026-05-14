# 03 — Guía de Implementación en Nueva Distribuidora

## Resumen del proceso

Implementar Orbit TP en una nueva distribuidora requiere:
1. Preparar los datos fuente en el formato correcto
2. Configurar las credenciales de Google
3. Adaptar los 3 archivos de configuración
4. Correr el pipeline una vez para validar
5. Deployar el portal con las variables de la nueva distribuidora

Tiempo estimado: 1–2 días hábiles si los datos fuente ya están disponibles.

---

## Paso 1 — Preparar los datos fuente

### 1.1 Estructura de carpeta

Crear la carpeta del proyecto (ej. `C:\Orbit\TP_NUEVA_DISTRIB`) copiando la estructura base:

```
inputs/
├── ventas.csv              → exportado de GESCOM / sistema de facturación
├── gescom.xlsx             → padrón de clientes
├── Portafolio Infaltable - Argentina.pptx  → catálogo de SKUs TP
├── lista_precios.xlsx      → precios por producto
└── objetivo_vendedor_tp.xlsx → objetivos mensuales por vendedor
```

### 1.2 Formato ventas.csv

Columnas mínimas requeridas (nombres exactos o se adaptan en `clean_venta.py`):

| Columna | Descripción |
|---|---|
| Fecha | `YYYY-MM-DD` o `DD/MM/YYYY` |
| VendedorID | Número entero (ej. `2`, `3`, `4`) |
| ClienteID | Código único del cliente |
| Articulo | Código de SKU |
| Cantidad | Unidades vendidas |
| Importe | Valor en moneda local |

### 1.3 Formato gescom.xlsx

Columnas mínimas requeridas:

| Columna | Descripción |
|---|---|
| ClienteID | Código único (debe coincidir con ventas.csv) |
| RazonSocial | Nombre del cliente |
| Localidad | Ciudad o zona |
| Direccion | Dirección postal |
| VendedorID | Vendedor asignado |
| TAXONOMIA | Clasificación: P, A, B o C |

### 1.4 Formato objetivo_vendedor_tp.xlsx

| Columna | Descripción |
|---|---|
| VendedorID | ID del vendedor |
| Zona | Código de día (LU, MA, MI, JU, VI, SA) |
| Objetivo | Cantidad de clientes TP objetivo |

---

## Paso 2 — Crear recursos en Google Cloud

### 2.1 Crear Spreadsheet

1. Crear un Google Spreadsheet vacío en Google Drive
2. Copiar el ID de la URL: `https://docs.google.com/spreadsheets/d/**ID**/edit`
3. El pipeline creará las hojas automáticamente en el primer sync

### 2.2 Crear carpetas en Drive

Crear dos carpetas en Google Drive:
- `PDF_GERENCIAL_[NOMBRE_DISTRIB]`
- `PDF_VENDEDORES_[NOMBRE_DISTRIB]`

Copiar los IDs de las URLs de cada carpeta.

### 2.3 Crear Service Account (portal)

Ver instrucciones completas en `portal/SETUP_SERVICE_ACCOUNT.md`.

Resumen:
1. Google Cloud Console → nuevo proyecto → activar Sheets API + Drive API
2. IAM → Cuentas de servicio → Crear → descargar JSON
3. Compartir el Spreadsheet con el email del SA como Lector
4. Compartir las carpetas de Drive con el email del SA como Lector

### 2.4 Credenciales OAuth (pipeline local)

1. Copiar `credenciales/google-oauth-client.json` de la instalación de referencia
2. O crear nuevas credenciales OAuth 2.0 en Google Cloud → Credenciales → OAuth 2.0
3. En el primer `sync_tp_appsheet_drive.py --config ...` se abrirá el browser para autorizar

---

## Paso 3 — Configurar los 3 archivos de configuración

### 3.1 `google_sync_config.json`

```json
{
  "auth_mode": "oauth_user",
  "oauth_client_secrets_json": "credenciales/google-oauth-client.json",
  "oauth_token_json": "credenciales/google-oauth-token.json",
  "spreadsheet_id": "ID_DEL_NUEVO_SPREADSHEET",
  "drive_pdf_gerencial_folder_id": "ID_CARPETA_GERENCIAL",
  "drive_pdf_vendedores_folder_id": "ID_CARPETA_VENDEDORES"
}
```

### 3.2 `config_app.json`

```json
{
  "mgmt_password": "clave_gerencia_nueva_distrib",
  "vendor_password": "clave_vendedores_nueva_distrib",
  "vendor_names": {
    "2": "Nombre Vendedor 2",
    "3": "Nombre Vendedor 3",
    "4": "Nombre Vendedor 4"
  },
  "ngrok_token": ""
}
```

Los IDs de vendedor deben coincidir exactamente con los que aparecen en `ventas.csv`.

### 3.3 Variables de entorno del portal (`portal/.env` para local o Render para producción)

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
SPREADSHEET_ID=ID_DEL_NUEVO_SPREADSHEET
MGMT_PASSWORD=clave_gerencia_nueva_distrib
VENDOR_PASSWORD=clave_vendedores_nueva_distrib
VENDOR_NAMES={"2":"Nombre Vendedor 2","3":"Nombre Vendedor 3"}
HOST=0.0.0.0
```

---

## Paso 4 — Primer pipeline de prueba

```
1. Colocar los inputs en inputs/
2. Ejecutar: RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat
3. Ingresar zona a procesar (ej. JU)
4. Verificar:
   - output/PDF_VENDEDORES/ → archivos PDF generados
   - output/PDF_GERENCIAL/  → archivos PDF generados
   - output/APPSHEET/       → 4 archivos CSV generados
   - Google Sheets          → hojas actualizadas con datos
   - Google Drive           → PDFs subidos a las carpetas
```

Si hay errores, ver `08_PLAN_EXPORTABLE_V2.md` sección "Errores comunes".

---

## Paso 5 — Deploy del portal

Ver `portal/DEPLOY_RENDER.md` para el proceso completo.

Puntos clave por distribuidora:
- Nombre del Web Service en Render: `orbit-tp-[nombre-distrib]`
- Usar las variables de entorno de la nueva distribuidora (no las de PyP)
- Cada distribuidora tiene su propio Spreadsheet ID
- Las contraseñas deben ser distintas por distribuidora

---

## Checklist rápido de adaptación

| Qué cambiar | Dónde |
|---|---|
| IDs de Spreadsheet y Drive | `google_sync_config.json` |
| Contraseñas | `config_app.json` + variables Render |
| Nombres de vendedores | `config_app.json` + `VENDOR_NAMES` en Render |
| IDs de vendedores | Deben coincidir con los datos fuente |
| Objetivos | `inputs/objetivo_vendedor_tp.xlsx` |
| Service Account | Compartir con el nuevo Spreadsheet y Drive |

---

## Lo que NO cambia entre distribuidoras

- Todo el código fuente (pipeline, portal, sync)
- La estructura de hojas en Google Sheets
- El formato de los PDFs
- El diseño del portal
- Los tests Playwright
