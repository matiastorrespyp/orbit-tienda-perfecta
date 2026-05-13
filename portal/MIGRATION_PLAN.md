# Plan de migración — Portal Orbit: local/ngrok → Render + Google Sheets

## Estado anterior (antes de esta migración)

- Portal Astro corriendo en `localhost:4321` con ngrok para acceso externo
- Datos leídos desde archivos CSV locales (`output/`) con `fs.readFileSync` + PapaParse
- PDFs servidos directamente desde disco (`output/pdfs/`)
- Configuración (contraseñas, nombres) leída desde `config_app.json` local
- Dependencia total de la PC del usuario encendida y ngrok activo

## Estado objetivo (después de esta migración)

- Portal publicado en Render con URL permanente (24/7, sin PC local)
- Datos leídos desde Google Sheets vía Service Account (Google Sheets API v4)
- PDFs servidos como redirect a Google Drive (Google Drive API v3)
- Configuración leída desde variables de entorno
- Pipeline Python sigue corriendo local → sube a Sheets y Drive sin cambios

---

## Archivos modificados en el portal

| Archivo | Cambio |
|---|---|
| `src/lib/google.ts` | NUEVO — auth Service Account, `readSheet()`, `getDriveViewUrl()` |
| `src/lib/config.ts` | `fs.readFileSync config_app.json` → `process.env.*` |
| `src/lib/data.ts` | `readCsv()` local → `readSheet()` async (Google Sheets) |
| `src/pages/api/pdf.ts` | `fs.readFileSync` local → redirect 302 a Drive |
| `src/pages/vendedor.astro` | Agregado `await` en llamadas a data functions |
| `src/pages/gerencia.astro` | Agregado `await` en llamadas a data functions |
| `package.json` | Agregado `googleapis` en dependencies |

## Archivos documentales nuevos

| Archivo | Propósito |
|---|---|
| `.env.example` | Plantilla de variables de entorno (sin secretos) |
| `SETUP_SERVICE_ACCOUNT.md` | Instrucciones para crear el Service Account de Google |
| `DEPLOY_RENDER.md` | Instrucciones para publicar en Render |
| `MIGRATION_PLAN.md` | Este archivo |

## Archivos NO modificados

- Todo el pipeline Python (`sync_tp_appsheet_drive.py`, `sync_extras.py`, etc.)
- BATs operativos
- `credenciales/` (OAuth local del pipeline)
- `inputs/`, `output/`
- `config_app.json`, `google_sync_config.json`
- Componentes React del portal (`src/components/`)
- Estilos, assets, public/

---

## Checklist de deploy

### Paso 1 — Google Cloud
- [ ] Crear Service Account `orbit-tp-portal` (ver `SETUP_SERVICE_ACCOUNT.md`)
- [ ] Descargar clave JSON
- [ ] Compartir Spreadsheet con la cuenta de servicio (Lector)
- [ ] Compartir carpeta Drive vendedores con la cuenta de servicio (Lector)
- [ ] Compartir carpeta Drive gerencial con la cuenta de servicio (Lector)

### Paso 2 — GitHub
- [ ] Verificar que `portal/.env` y `credenciales/` estén en `.gitignore`
- [ ] Hacer `git push` del portal migrado a `main`

### Paso 3 — Render
- [ ] Crear Web Service conectado al repo (ver `DEPLOY_RENDER.md`)
- [ ] Cargar variables de entorno en Render dashboard
- [ ] Verificar build exitoso en el log de Render
- [ ] Verificar acceso a la URL pública

### Paso 4 — Validación funcional
- [ ] Login gerencia funciona
- [ ] Login vendedor funciona
- [ ] Datos de clientes se muestran correctamente
- [ ] PDFs abren vía redirect a Drive
- [ ] Objetivos y facturación comparativa se muestran en gerencia

---

## Flujo operativo post-migración

```
PC local
  └── pipeline Python corre normalmente
        ├── sync_tp_appsheet_drive.py → Google Sheets (datos) + Google Drive (PDFs)
        └── (sin cambios respecto al flujo anterior)

Render (24/7, sin PC local)
  └── portal Astro lee desde Google Sheets en cada request
        └── PDFs → redirect 302 a Google Drive
```

El pipeline no necesita saber que el portal existe. El portal no necesita saber cómo
se generan los datos. Ambos comparten únicamente el Spreadsheet y las carpetas de Drive.

---

## Rollback

Si el deploy en Render falla y se necesita volver al modo local:

1. Crear `portal/.env` con las variables (ver `.env.example`)
2. Correr `npm run dev` localmente
3. Usar ngrok como antes para acceso externo temporal
