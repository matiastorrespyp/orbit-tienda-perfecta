# Playwright QA Report — Portal Orbit · Tienda Perfecta

Fecha: 2026-05-12
Entorno: Windows 10 · Node standalone (node dist/server/entry.mjs) · Chromium

---

## Build

npm run build → Completado en 9.04s

- Errores de compilación: 0
- Warning: imports no usados de lucide-react en GerenciaDashboard.tsx (no bloquea)

---

## Resultado Playwright

7 tests · 7 pasaron · 0 fallaron · Duración: 17.6s

| # | Test                                         | Tipo | Resultado |
|---|----------------------------------------------|------|-----------|
| 1 | landing carga y muestra formulario           | UI   | PASS      |
| 2 | login inválido muestra error en pantalla     | UI   | PASS      |
| 3 | perfil vacío muestra error antes de enviar   | UI   | PASS      |
| 4 | login gerencia por UI redirige a /gerencia   | UI   | PASS      |
| 5 | login vendedor por UI redirige a /vendedor   | UI   | PASS      |
| 6 | API — gerencia acepta credenciales correctas | API  | PASS      |
| 7 | API — vendedor acepta credenciales correctas | API  | PASS      |

---

## Bug corregido durante esta sesión

Archivo: portal/src/components/Login.tsx

El input type="hidden" name="role" usaba defaultValue="" (no controlado) y se
reseteaba a "" cuando setEntering(true) disparaba el re-render de React. Resultado:
form.submit() enviaba role="" y la API redirigía a /?error=1.

Fix aplicado (mínimo, sin cambios visuales):
- Eliminado useRef; agregado useState('') para role
- En handleSubmit: setRole('gerencia'|'vendedor') antes de setEntering(true)
- Hidden input: value={role} readOnly (controlado por React state)

---

## Screenshots generados

Ubicación: portal/test-results/screenshots/ — 8 de 8 generados

| Archivo                      | Descripción                                  |
|------------------------------|----------------------------------------------|
| 01-landing.png               | Landing inicial con formulario de login      |
| 02-login-invalido-antes.png  | Formulario con clave incorrecta completado   |
| 03-login-invalido-error.png  | Mensaje "Contraseña incorrecta" visible      |
| 04-perfil-vacio-error.png    | Error client-side "Seleccioná un perfil"     |
| 05-gerencia-formulario.png   | Formulario gerencia completo antes de submit |
| 06-gerencia-post-login.png   | Post-login gerencia (página mockeada)        |
| 07-vendedor-formulario.png   | Formulario vendedor completo antes de submit |
| 08-vendedor-post-login.png   | Post-login vendedor (página mockeada)        |

---

## Errores de consola

Browser (cliente): 0 errores en todos los tests.

Servidor (WebServer logs): errores de Google Auth esperados en entorno de test.
GOOGLE_SERVICE_ACCOUNT_JSON es un stub sin client_email. Son errores SSR, no
aparecen en el browser y no afectan los tests de landing ni login.

Ejemplo del error (esperado):
  [sheets] Error leyendo "pdf_index": The incoming JSON object does not
  contain a client_email field

Estos errores desaparecen cuando se configura el Service Account real en Render.

---

## Alcance de esta sesión

Realizado:
- Migración de data layer: fs.readFileSync -> Google Sheets API + Drive API
- config.ts: config_app.json -> variables de entorno
- api/pdf.ts: disco local -> redirect 302 a Google Drive
- vendedor.astro y gerencia.astro: await agregado en llamadas de datos
- Login.tsx: bug de hidden input corregido
- Archivos nuevos: google.ts, .env.example, SETUP_SERVICE_ACCOUNT.md,
  DEPLOY_RENDER.md, MIGRATION_PLAN.md, playwright.config.ts, tests/smoke.spec.ts

No tocado:
- Pipeline Python, BATs, credenciales, inputs, output
- config_app.json, google_sync_config.json
- Componentes React (GerenciaDashboard, VendedorDashboard)
- Diseño visual, estilos, assets

---

## git status --short

 M portal/package-lock.json
 M portal/package.json
 M portal/src/components/Login.tsx
 M portal/src/lib/config.ts
 M portal/src/lib/data.ts
 M portal/src/pages/api/pdf.ts
 M portal/src/pages/gerencia.astro
 M portal/src/pages/vendedor.astro
?? portal/.env.example
?? portal/DEPLOY_RENDER.md
?? portal/MIGRATION_PLAN.md
?? portal/PLAYWRIGHT_QA_REPORT.md
?? portal/SETUP_SERVICE_ACCOUNT.md
?? portal/playwright.config.ts
?? portal/src/lib/google.ts
?? portal/test-results/
?? portal/tests/

---

## Estado final

Build: OK — 0 errores
Playwright: 7/7 tests pasando
Screenshots: 8/8 generados
Browser console errors: 0
Login.tsx: bug de hidden input corregido

El portal esta listo para commit tecnico. Deploy pendiente de Service Account
real y variables de entorno configuradas en Render. Commit pendiente.
