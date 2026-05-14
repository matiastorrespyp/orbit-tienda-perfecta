# Setup Distribuidora — Plan del Script Automático

## Objetivo

`setup_distribuidora.py` es un script de configuración asistida que toma `CONFIG_DISTRIBUIDORA_TEMPLATE.json` completo y prepara el entorno de trabajo para una nueva distribuidora sin intervención manual en cada archivo.

Este documento define el diseño del script para cuando se implemente.

---

## Qué problema resuelve

Hoy, configurar una nueva distribuidora requiere editar manualmente:
- `config_app.json`
- `google_sync_config.json`
- `portal/.env` (o variables Render)
- Copiar y renombrar archivos de assets

El script automatiza esos pasos leyendo un único JSON de configuración.

---

## Invocación

```bash
python setup_distribuidora.py --config config_nueva_distrib.json [--dry-run] [--force]
```

| Flag | Descripción |
|---|---|
| `--config` | Ruta al JSON de configuración de la distribuidora (requerido) |
| `--dry-run` | Muestra qué haría sin escribir nada |
| `--force` | Sobreescribe archivos existentes sin preguntar |

---

## Pasos que ejecuta el script

### Paso 1 — Validar el JSON de configuración

Verificar que todos los campos `TODO` fueron reemplazados por valores reales.

```
✓ distribuidora.nombre completado
✓ vendedores.lista tiene al menos 1 vendedor
✓ google.spreadsheet_id no es TODO
✓ portal.mgmt_password tiene al menos 8 caracteres
✗ render.url_publica todavía es TODO (warning, no error — el deploy es posterior)
```

Cualquier campo requerido con valor `TODO` detiene la ejecución con mensaje claro.

### Paso 2 — Generar config_app.json

Construir el archivo a partir del JSON:

```python
config_app = {
    "mgmt_password":   cfg["portal"]["mgmt_password"],
    "vendor_password": cfg["portal"]["vendor_password"],
    "vendor_names": {
        str(v["id"]): v["nombre"]
        for v in cfg["vendedores"]["lista"]
    },
    "ngrok_token": ""
}
```

Escribir a `config_app.json`. Si ya existe, preguntar (o usar `--force`).

### Paso 3 — Generar google_sync_config.json

```python
google_sync = {
    "auth_mode": cfg["google"]["auth_mode"],
    "oauth_client_secrets_json": cfg["google"]["oauth_client_secrets_json"],
    "oauth_token_json": cfg["google"]["oauth_token_json"],
    "spreadsheet_id": cfg["google"]["spreadsheet_id"],
    "drive_pdf_gerencial_folder_id": cfg["google"]["drive_pdf_gerencial_folder_id"],
    "drive_pdf_vendedores_folder_id": cfg["google"]["drive_pdf_vendedores_folder_id"]
}
```

Escribir a `google_sync_config.json`.

### Paso 4 — Generar portal/.env

```python
vendor_names_json = json.dumps({
    str(v["id"]): v["nombre"]
    for v in cfg["vendedores"]["lista"]
}, ensure_ascii=False)

env_content = f"""GOOGLE_SERVICE_ACCOUNT_JSON=PENDIENTE_COMPLETAR_MANUALMENTE
SPREADSHEET_ID={cfg["google"]["spreadsheet_id"]}
MGMT_PASSWORD={cfg["portal"]["mgmt_password"]}
VENDOR_PASSWORD={cfg["portal"]["vendor_password"]}
VENDOR_NAMES={vendor_names_json}
HOST=0.0.0.0
"""
```

Escribir a `portal/.env`.  
El campo `GOOGLE_SERVICE_ACCOUNT_JSON` siempre queda como `PENDIENTE_COMPLETAR_MANUALMENTE` porque el JSON del Service Account no debe estar en el archivo de configuración de la distribuidora.

### Paso 5 — Copiar logo

Si `logo_path` apunta a un archivo que existe y no es el default de Orbit:
- Copiar a `assets/logo_distrib.png`
- Confirmar que el pipeline lo usará en el footer de PDFs

Si no existe el archivo del logo: warning (no error) — el pipeline usa el logo de Orbit como fallback.

### Paso 6 — Generar README de la instalación

Crear `ESTA_DISTRIBUIDORA.md` en la raíz con los datos de la distribuidora:

```markdown
# Orbit TP — [nombre distribuidora]

Generado automáticamente por setup_distribuidora.py

- Distribuidora: [nombre]
- Vendedores: [lista]
- Zonas activas: [lista]
- Spreadsheet ID: [id]
- Portal Render: [url o PENDIENTE]
- Generado: [timestamp]
```

### Paso 7 — Resumen de salida

```
=== SETUP DISTRIBUIDORA OK ===

Archivos generados:
  ✓ config_app.json
  ✓ google_sync_config.json
  ✓ portal/.env
  ✓ ESTA_DISTRIBUIDORA.md

Pendiente de completar manualmente:
  ! portal/.env → GOOGLE_SERVICE_ACCOUNT_JSON (requiere JSON de Service Account)
  ! render → URL pública (completar después del deploy)

Próximos pasos:
  1. Completar GOOGLE_SERVICE_ACCOUNT_JSON en portal/.env o en Render
  2. Correr: RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat
  3. Verificar outputs en output/PDF_VENDEDORES y Google Sheets
  4. Deploy en Render con las variables de portal/.env
```

---

## Qué NO hace el script

- No toca el código fuente (`tp_pyp_run_fast_ORBIT_appsheet.py`, portal, etc.)
- No sube nada a Google Cloud
- No crea el Spreadsheet ni las carpetas Drive
- No hace deploy en Render
- No valida que las credenciales de Google sean correctas
- No modifica `requirements.txt` ni dependencias

---

## Validaciones que incluye el script

Ver `VALIDADORES_REQUERIDOS.md` para el detalle.

El script corre automáticamente los validadores de formato de datos si los archivos de inputs ya están disponibles. Si alguno falla, lo reporta como warning sin detener el setup (los archivos de configuración se generan igual).

---

## Estructura de archivos generados

```
[raíz del proyecto]/
├── config_app.json                    ← generado por setup
├── google_sync_config.json            ← generado por setup
├── ESTA_DISTRIBUIDORA.md              ← generado por setup
├── assets/
│   └── logo_distrib.png               ← copiado si estaba en config
└── portal/
    └── .env                           ← generado por setup (sin SA JSON)
```

---

## Dependencias del script

```python
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
```

Sin dependencias externas. Solo stdlib de Python.

---

## Extensiones futuras

| Extensión | Descripción |
|---|---|
| `--validate-only` | Solo correr validadores sin generar archivos |
| `--render-deploy` | Disparar deploy en Render vía API |
| `--check-google` | Verificar acceso a Sheets y Drive con las credenciales |
| Multi-distribuidora | Modo `--list` para ver todas las distribuidoras configuradas |
| Git commit automático | Commitear los archivos generados con mensaje estándar |
