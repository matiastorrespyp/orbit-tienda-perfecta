# NEXT TASK — Tienda Perfecta

## Estado cerrado

Commit técnico realizado:

`7ffd1ac feat(tp): preparar portal publico con Google Sheets Drive y QA Playwright`

## Qué quedó listo

- Portal preparado para publicación externa 24/7.
- Migración de datos locales a Google Sheets API.
- PDFs migrados a Google Drive vía redirect.
- Configuración migrada a variables de entorno.
- Bug de login corregido en `Login.tsx`.
- Build OK.
- Playwright QA OK: 7/7 tests pasando.
- Screenshots QA: 8/8 generados.
- Documentación de deploy creada.
- Apps Script queda como plan B, no como solución principal.

## Próximo paso

Crear y configurar Service Account real de Google.

Luego:

1. Compartir Google Sheet con el email del Service Account.
2. Compartir carpetas Drive de PDFs con el Service Account.
3. Crear variables de entorno en Render/Railway.
4. Verificar o subir repo a GitHub.
5. Conectar Render/Railway al repo.
6. Deploy.
7. Probar link externo desde celular.
8. Ejecutar QA post-deploy.

## No tocar sin revisión

- `COMO_USAR_ORBIT_TP.txt`
- `GEN_BuenasPracticas_v5.py`
- `Tienda Perfecta/`

## Regla nueva Orbit

Todo portal, landing o dashboard Orbit debe pasar:

1. Build.
2. Playwright QA.
3. Capturas.
4. Revisión de consola.
5. Reporte QA.

Antes de commit importante o deploy.
