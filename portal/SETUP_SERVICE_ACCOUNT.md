# Setup — Google Service Account para el Portal

El portal en Render/Railway necesita un **Service Account** de Google para leer
datos de Sheets y Drive sin intervención humana. Es distinto a las credenciales OAuth
que usa el pipeline local (`credenciales/`). Se crea una vez.

---

## Por qué Service Account y no OAuth

| | OAuth user (pipeline local) | Service Account (portal) |
|---|---|---|
| Auth | Requiere browser para el primer login | JSON de clave, sin interacción |
| Contexto | PC del usuario | Servidor remoto 24/7 |
| Permisos | Los del usuario propietario | Solo los explícitamente dados |
| Rotación | Token se renueva automáticamente | Clave válida hasta que se revoque |

---

## Paso 1 — Crear el proyecto en Google Cloud (si no existe)

1. Ir a [console.cloud.google.com](https://console.cloud.google.com)
2. Crear un proyecto nuevo → nombre sugerido: `orbit-tp-portal`
3. Activar las APIs necesarias en **APIs y servicios → Biblioteca**:
   - **Google Sheets API** → Activar
   - **Google Drive API** → Activar

---

## Paso 2 — Crear la cuenta de servicio

1. Ir a **IAM y administración → Cuentas de servicio**
2. Clic en **Crear cuenta de servicio**
3. Completar:
   - Nombre: `orbit-tp-portal`
   - ID (se genera solo): `orbit-tp-portal@<proyecto>.iam.gserviceaccount.com`
   - Descripción: `Portal Orbit Tienda Perfecta — solo lectura`
4. Clic en **Continuar** (sin asignar roles en el proyecto — no los necesita)
5. Clic en **Listo**

---

## Paso 3 — Descargar la clave JSON

1. En la lista de cuentas de servicio, clic en `orbit-tp-portal`
2. Ir a la pestaña **Claves**
3. **Agregar clave → Crear clave nueva → JSON**
4. Se descarga un archivo `.json` — guardarlo temporalmente en un lugar seguro
5. **Este archivo NUNCA va al repositorio GitHub**

El contenido del JSON se usará como valor de la variable de entorno
`GOOGLE_SERVICE_ACCOUNT_JSON` (todo el JSON en una sola línea).

---

## Paso 4 — Dar acceso al Google Spreadsheet

El Spreadsheet donde el pipeline sube los datos:

```
ID: 1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0
```

1. Abrir el Spreadsheet en Google Sheets
2. Clic en **Compartir** (botón superior derecho)
3. Agregar el email de la cuenta de servicio:
   `orbit-tp-portal@<proyecto>.iam.gserviceaccount.com`
4. Rol: **Lector** (solo lectura)
5. Desmarcar "Notificar a las personas" → **Compartir**

---

## Paso 5 — Dar acceso a las carpetas de Google Drive

Carpeta de PDFs de vendedores:
```
ID: 1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa
URL: https://drive.google.com/drive/folders/1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa
```

Carpeta de PDFs gerencial:
```
ID: 1tlBd2GrWuJAjYX0dwn6dsfbnDh6gM8PQ
URL: https://drive.google.com/drive/folders/1tlBd2GrWuJAjYX0dwn6dsfbnDh6gM8PQ
```

Para cada carpeta:
1. Abrir la carpeta en Google Drive
2. Clic derecho → **Compartir**
3. Agregar el email de la cuenta de servicio → rol **Lector**
4. **Compartir**

---

## Paso 6 — Configurar la variable de entorno

El valor de `GOOGLE_SERVICE_ACCOUNT_JSON` es el contenido completo del JSON descargado,
todo en una sola línea (los saltos de línea en `private_key` se representan como `\n`).

### En Render o Railway

Ir al dashboard del servicio → Environment Variables → agregar:

```
GOOGLE_SERVICE_ACCOUNT_JSON = {"type":"service_account","project_id":"orbit-tp-portal",...}
```

### Para prueba local

Crear `portal/.env` (gitignoreado) con:

```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

Ver `portal/.env.example` como plantilla.

---

## Paso 7 — Verificar acceso (opcional, antes de deploy)

Desde la PC local con el `.env` configurado, correr:

```bash
cd portal
node -e "
const { google } = require('googleapis');
const creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
const auth = new google.auth.GoogleAuth({ credentials: creds, scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'] });
auth.getClient().then(() => console.log('Auth OK')).catch(console.error);
" 
```

---

## Notas de seguridad

- La clave JSON es equivalente a una contraseña. No compartir por email o Slack.
- Si se compromete, revocarla en Google Cloud Console → IAM → Cuentas de servicio → Claves → Eliminar clave.
- El Service Account solo tiene acceso de **lectura** al Spreadsheet y a las carpetas de Drive. No puede modificar nada.
- Si se agrega un Spreadsheet nuevo o una carpeta nueva, hay que compartirlo explícitamente con el Service Account.
