# 06 — Configuración Google y Render

## Google Cloud — Visión general

El sistema usa dos tipos de credenciales de Google con propósitos distintos:

| Credencial | Uso | Dónde vive |
|---|---|---|
| OAuth 2.0 (user) | Pipeline local — escribe en Sheets y Drive | `credenciales/` en PC local |
| Service Account | Portal en Render — lee Sheets y Drive | Variable de entorno `GOOGLE_SERVICE_ACCOUNT_JSON` |

---

## Credenciales OAuth (pipeline local)

### Archivos

```
credenciales/
├── google-oauth-client.json   → client_id y client_secret de Google Cloud
└── google-oauth-token.json    → token de acceso (generado en primer uso)
```

### Primer uso

Al correr `sync_tp_appsheet_drive.py` por primera vez:
1. Se abre el browser automáticamente
2. El usuario hace login con la cuenta de Google que tiene acceso al Spreadsheet y al Drive
3. Se genera `google-oauth-token.json` — se reutiliza en ejecuciones siguientes

### Token vencido

Si el token vence (raro con refresh_token activo), borrarlo y correr el sync de nuevo para regenerarlo:
```
del credenciales\google-oauth-token.json
python sync_tp_appsheet_drive.py --config google_sync_config.json
```

---

## Service Account (portal en Render)

### Crear desde cero

1. Ir a [console.cloud.google.com](https://console.cloud.google.com)
2. Seleccionar el proyecto (o crear uno: `orbit-tp-portal`)
3. APIs y servicios → Biblioteca:
   - Activar **Google Sheets API**
   - Activar **Google Drive API**
4. IAM y administración → Cuentas de servicio → Crear cuenta de servicio:
   - Nombre: `orbit-tp-portal`
   - Sin rol en el proyecto (no necesita)
5. Pestaña Claves → Agregar clave → JSON → Descargar

### Dar acceso

El Service Account tiene su propio email: `orbit-tp-portal@<proyecto>.iam.gserviceaccount.com`

Compartir con ese email como **Lector**:
- El Spreadsheet de datos
- La carpeta de Drive PDF_GERENCIAL
- La carpeta de Drive PDF_VENDEDORES

### Configurar en Render

Ir al dashboard de Render → Web Service → Environment:

```
GOOGLE_SERVICE_ACCOUNT_JSON = {"type":"service_account","project_id":"orbit-tp-portal",...}
```

El JSON completo va en una sola línea. Los saltos de línea del campo `private_key` son literales `\n`.

**Truco para generar el valor correcto:**
```python
import json
with open("service-account.json") as f:
    data = json.load(f)
print(json.dumps(data))  # imprime en una sola línea
```

---

## google_sync_config.json

```json
{
  "auth_mode": "oauth_user",
  "oauth_client_secrets_json": "credenciales/google-oauth-client.json",
  "oauth_token_json": "credenciales/google-oauth-token.json",
  "spreadsheet_id": "ID_DEL_SPREADSHEET",
  "drive_pdf_gerencial_folder_id": "ID_CARPETA_GERENCIAL",
  "drive_pdf_vendedores_folder_id": "ID_CARPETA_VENDEDORES"
}
```

### Cómo obtener los IDs

**Spreadsheet ID**: parte de la URL de Google Sheets
```
https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit
```

**Drive folder ID**: parte de la URL de la carpeta en Drive
```
https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
```

---

## Render — Configuración del Web Service

### Parámetros de build

| Campo | Valor |
|---|---|
| Name | `orbit-tp-[distrib]` |
| Region | Oregon (US West) — o el más cercano |
| Branch | `main` |
| Root Directory | `portal` |
| Runtime | Node |
| Build Command | `npm install && npm run build` |
| Start Command | `node dist/server/entry.mjs` |

### Variables de entorno completas

```
GOOGLE_SERVICE_ACCOUNT_JSON = {...JSON completo en una línea...}
SPREADSHEET_ID              = 1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0
MGMT_PASSWORD               = clave_gerencia
VENDOR_PASSWORD             = clave_vendedores
VENDOR_NAMES                = {"2":"Juliana","3":"Nadia","4":"Ángel","5":"Majo","6":"Andrea"}
HOST                        = 0.0.0.0
```

`PORT` es inyectado automáticamente por Render.

### Plan de Render

- **Free tier**: duerme después de 15 minutos de inactividad. El primer request tarda ~30 segundos en despertar.
- **Starter ($7/mes)**: siempre activo. Recomendado para uso diario.

### Actualización de datos

El portal **no requiere redeploy** cuando cambian los datos. El pipeline sube a Sheets/Drive y el portal los lee con cache de 5 minutos.

Un redeploy solo es necesario cuando:
- Cambia el código del portal
- Cambian las variables de entorno (contraseñas, IDs)

---

## Verificación post-configuración

### Verificar Service Account local

```bash
cd portal
node -e "
const { google } = require('googleapis');
const creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
const auth = new google.auth.GoogleAuth({
  credentials: creds,
  scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly']
});
auth.getClient().then(() => console.log('Auth OK')).catch(console.error);
"
```

### Verificar portal en Render

```bash
curl -I https://orbit-tp-portal.onrender.com

curl -X POST https://orbit-tp-portal.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"role":"gerencia","password":"TU_PASSWORD"}'
```

Respuesta esperada: `{"ok":true}`

---

## Seguridad

- El JSON de Service Account es equivalente a una contraseña. No compartir por email.
- Si se compromete: Google Cloud → IAM → Cuentas de servicio → Claves → Eliminar clave.
- El Service Account tiene solo lectura — no puede modificar Sheets ni Drive.
- Las contraseñas del portal viven solo en las variables de entorno de Render, no en el repo.
- `portal/.env` está en `.gitignore` — nunca subir al repositorio.
