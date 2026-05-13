# README — Deploy Apps Script Web App · Orbit TP

## Qué es esto

Una Web App hospedada en Google que permite a los vendedores ver su PDF del día,
clientes objetivo y focos desde el celular, sin necesitar la PC local encendida.

URL resultante: `https://script.google.com/macros/s/XXXXXX/exec`  
Estable, permanente, gratuita.

---

## Paso 1 — Abrir Google Sheets

Abrir el Spreadsheet del proyecto:

```
https://docs.google.com/spreadsheets/d/1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0
```

---

## Paso 2 — Abrir Apps Script

En el Spreadsheet: **Extensiones → Apps Script**

Se abre el editor de código en una nueva pestaña.

---

## Paso 3 — Crear los archivos del proyecto

El proyecto de Apps Script necesita 4 archivos.
Crearlos en este orden exacto:

### 3.1 — webapp.gs (reemplazar el código.gs existente)

1. Clic en el archivo `Código.gs` que aparece por defecto.
2. Borrar todo su contenido.
3. Pegar el contenido de `webapp.gs` (de esta carpeta).
4. Guardar con Ctrl+S.

### 3.2 — ui_main.html

1. Clic en el ícono **+** junto a "Archivos" → **HTML**.
2. Nombrar el archivo: `ui_main` (sin extensión, Apps Script la agrega solo).
3. Borrar el contenido que aparece por defecto.
4. Pegar el contenido de `ui_main.html` (de esta carpeta).
5. Guardar.

### 3.3 — ui_vendedor.html

1. Nuevo archivo HTML → nombre: `ui_vendedor`
2. Pegar contenido de `ui_vendedor.html`.
3. Guardar.

### 3.4 — ui_gerencia.html

1. Nuevo archivo HTML → nombre: `ui_gerencia`
2. Pegar contenido de `ui_gerencia.html`.
3. Guardar.

---

## Paso 4 — Configurar contraseñas (una vez)

En el editor de Apps Script:

1. Ir al menú **Proyecto** → clic en el ícono de configuración (engranaje ⚙️)
   o directamente al archivo `webapp.gs`.
2. Abrir la **Consola** (menú Ver → Registros, o Ctrl+Enter en un bloque vacío).
3. En el editor, crear una función temporal y ejecutarla **UNA SOLA VEZ**:

```javascript
function configurarContrasenas() {
  PropertiesService.getScriptProperties().setProperties({
    VENDOR_PASSWORD: 'tp2026',
    MGMT_PASSWORD:   'orbit2026'
  });
  Logger.log('Contraseñas configuradas.');
}
```

4. Seleccionar `configurarContrasenas` en el selector de función y clic en ▶ Ejecutar.
5. Autorizar los permisos que pida Google (es normal la primera vez).
6. Confirmar en los Registros que dice "Contraseñas configuradas."
7. **Eliminar** la función `configurarContrasenas` del código (ya no la necesitás).

> Para cambiar contraseñas en el futuro, repetir este proceso.

---

## Paso 5 — Publicar como Web App

1. En el editor de Apps Script, clic en **Implementar → Nueva implementación**.
2. Tipo: **Aplicación web**.
3. Configurar:
   - **Descripción:** `Orbit TP v1.0`
   - **Ejecutar como:** `Yo` (tu cuenta de Google)
   - **Quién tiene acceso:** `Cualquier persona` _(anyone, even anonymous)_
4. Clic en **Implementar**.
5. Autorizar los permisos que pida (Drive, Sheets).
6. Copiar la **URL de la aplicación web**.

La URL tiene este formato:
```
https://script.google.com/macros/s/AKfycb.../exec
```

---

## Paso 6 — Probar

1. Abrir la URL en el celular (o en modo incógnito en la PC).
2. Ingresar con número `2` y contraseña `tp2026`.
3. Verificar que carga el dashboard del vendedor.
4. Ingresar con `gerencia` y contraseña `orbit2026`.
5. Verificar que carga el dashboard de gerencia.

---

## Paso 7 — Distribuir el link

Compartir la URL con cada vendedor por WhatsApp.
Recomendación: que la guarden como **acceso directo en la pantalla de inicio** del celular.

En Chrome móvil: Menú (tres puntos) → "Agregar a pantalla de inicio".

---

## Paso extra — Habilitar vista Gerencia (objetivos + facturación)

La vista de gerencia requiere dos hojas adicionales en el Spreadsheet:
`tp_objetivos_resumen` y `tp_facturacion_comparativa`.

El `sync_tp_appsheet_drive.py` principal **no las sube** todavía.

Para habilitarlas, ejecutar `sync_extras.py` desde la carpeta raíz del proyecto:

```bat
cd C:\Users\usuario\OneDrive\Desktop\TP_PYP
python apps_script_webapp\sync_extras.py --config google_sync_config.json
```

Esto sube las dos hojas faltantes al mismo Spreadsheet.
Solo necesita correrse cuando haya datos nuevos (una vez por día, después del pipeline).

---

## Paso 8 — Integrar sync_extras al pipeline diario

Para que la vista gerencia se actualice automáticamente cada día,
agregar esta línea en `RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat`
**justo después del paso [3]** (después de la línea que llama a `sync_tp_appsheet_drive.py`):

### Dónde insertar

Buscar en el BAT este bloque (líneas ~115-120):

```bat
echo [3] Sincronizando Drive y Google Sheets...
...
python sync_tp_appsheet_drive.py --config "google_sync_config.json"
if errorlevel 1 (
    ...
)
```

### Línea a agregar después de ese bloque

```bat
echo.
echo ==========================================
echo [3b] Sincronizando hojas gerencia...
echo ==========================================
python apps_script_webapp\sync_extras.py --config "google_sync_config.json"
if errorlevel 1 (
    echo.
    echo AVISO: No se pudo sincronizar hojas de gerencia.
)
```

Insertar entre el `exit /b 1` del paso [3] y el bloque `echo [4]`.

---

## Qué hacer si el sync falla un día

- Los datos del día anterior siguen visibles (el Spreadsheet no se borra).
- El vendedor verá datos de la última corrida exitosa.
- La fecha visible en el dashboard indica de qué día son los datos.
- Al día siguiente, al correr el pipeline normalmente, se actualizan solos.

---

## Cómo revocar acceso

**Opción rápida — cambiar contraseña:**

Ejecutar en la consola de Apps Script:
```javascript
PropertiesService.getScriptProperties().setProperty('VENDOR_PASSWORD', 'nuevaclave');
```
El link no cambia. Los vendedores que intenten con la contraseña vieja verán "contraseña incorrecta".

**Opción de emergencia — deshabilitar la Web App:**

Ir a Apps Script → Implementar → Administrar implementaciones → clic en la implementación activa → Deshabilitar.
El link deja de funcionar para todos inmediatamente.

---

## Actualizar el código después del primer deploy

Si se modifica el código (webapp.gs o los HTML), hay que crear una **nueva implementación**:

1. Implementar → Nueva implementación.
2. La URL cambia. Hay que redistribuir el nuevo link.

Alternativa: usar "Implementar → Administrar implementaciones → Editar" para actualizar
la misma implementación. En ese caso la URL no cambia.

---

## Archivos en esta carpeta

| Archivo               | Propósito                                              |
|-----------------------|--------------------------------------------------------|
| `webapp.gs`           | Lógica server-side: auth, lectura de Sheets, Drive     |
| `ui_main.html`        | Shell principal: login + CSS + JS del dashboard        |
| `ui_vendedor.html`    | Fragmento HTML de la vista vendedor                    |
| `ui_gerencia.html`    | Fragmento HTML de la vista gerencia                    |
| `sync_extras.py`      | Sync de hojas adicionales para vista gerencia          |
| `README_DEPLOY.md`    | Este archivo                                           |

---

## Resumen de tiempos estimados

| Tarea                              | Tiempo estimado |
|------------------------------------|-----------------|
| Pasos 1-5 (setup y deploy inicial) | ~20 minutos     |
| Pruebas y distribución del link    | ~10 minutos     |
| Habilitar vista gerencia           | ~5 minutos      |
| Total                              | ~35 minutos     |

---

## Siguiente paso (Fase 2)

Cuando se quiera un portal propio con URL personalizada (ej: `orbit-tp.render.com`),
ver el prompt maestro:

`C:\Orbit\00_OBSIDIAN_ORBIT\04_PROMPTS_MAESTROS\PROMPT_TP_003_PORTAL_RENDER.md`

Eso implica modificar `portal/src/lib/data.ts` para leer de Google Sheets en lugar
de archivos locales, y deployar el portal Astro en Render.com.

---

*Orbit · Tienda Perfecta · PyP — 2026-05-12*
