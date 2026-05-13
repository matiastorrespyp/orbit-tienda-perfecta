# Deploy — Portal Orbit en Render

Arquitectura objetivo:

- **GitHub** → código fuente.
- **Render** → hosting 24/7 conectado a GitHub.
- **Google Sheets** → datos leídos por el portal vía Service Account.
- **Google Drive** → PDFs abiertos desde links de visualización.

---

## Por qué no GitHub Pages

GitHub Pages solo sirve sitios estáticos. Este portal usa:

- `output: 'server'` con Astro Node adapter.
- Rutas API: `/api/pdf`, `/api/login`, `/api/logout`.
- Cookies `httpOnly` para autenticación.

Por eso el camino correcto es GitHub + Render/Railway, no GitHub Pages.

---

## Prerrequisitos

- [ ] Repositorio en GitHub con rama `main`.
- [ ] Service Account de Google creado.
- [ ] Spreadsheet compartido con Service Account como Viewer.
- [ ] Carpetas Drive compartidas con Service Account como Viewer.
- [ ] Contraseñas definidas en variables de entorno.

---

## Paso 1 — Crear Web Service en Render

1. Entrar a Render.
2. Crear **New → Web Service**.
3. Conectar el repositorio GitHub.
4. Configurar:

| Campo | Valor |
|---|---|
| Name | `orbit-tp-portal` |
| Branch | `main` |
| Root Directory | `portal` |
| Runtime | Node |
| Build Command | `npm install && npm run build` |
| Start Command | `node dist/server/entry.mjs` |

---

## Paso 2 — Variables de entorno

Agregar en Render:

```text
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
SPREADSHEET_ID=1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0
MGMT_PASSWORD=definir_clave_gerencia
VENDOR_PASSWORD=definir_clave_vendedores
VENDOR_NAMES={"2":"Juliana","3":"Nadia","4":"Ángel","5":"Majo","6":"Andrea"}
HOST=0.0.0.0

```

`PORT` normalmente lo inyecta Render. Si el servidor no arranca, revisar el log y agregar el `PORT` que indique Render.

---

## Paso 3 — Deploy

1. Click en **Create Web Service**.
2. Render clona el repo.
3. Ejecuta build.
4. Arranca el server.
5. Entrega una URL pública similar a:

```text
https://orbit-tp-portal.onrender.com
```

---

## Actualización de datos

El portal no requiere redeploy cuando cambian los datos.

1. `sync_tp_appsheet_drive.py` corre en la PC local y sube datos a Google Sheets y PDFs a Google Drive.
2. El portal en Render lee los datos desde Sheets en cada request con cache de 5 minutos.
3. Vendedores y gerencia ven los datos actualizados sin tocar Render.

---

## Plan B — Railway

Railway es alternativa directa:

- Deploy from GitHub.
- Root Directory: `portal`.
- Build Command: `npm install && npm run build`.
- Start Command: `node dist/server/entry.mjs`.
- Mismas variables de entorno.

---

## Verificación post-deploy

```bash
curl -I https://orbit-tp-portal.onrender.com

curl -X POST https://orbit-tp-portal.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"role":"gerencia","password":"TU_PASSWORD"}'
```

---

## Notas de seguridad

- Las variables de entorno en Render quedan fuera del repositorio.
- El Service Account debe tener solo lectura.
- `portal/.env` nunca debe subirse a GitHub.
- Si se rota una clave, se actualiza en Render y se redeploya.
