# Validadores Requeridos — Orbit TP

Verificaciones que deben pasar antes de correr el pipeline con datos de una nueva distribuidora.

Cada validador indica: **qué chequear**, **cómo chequearlo** y **qué hacer si falla**.

---

## V01 — ventas.csv: columnas requeridas

**Qué chequear:** el archivo tiene las columnas mínimas necesarias.

```python
import pandas as pd
df = pd.read_csv("inputs/ventas.csv", nrows=1)
required = {"Fecha", "VendedorID", "ClienteID", "Articulo", "Cantidad", "Importe"}
missing = required - set(df.columns)
assert not missing, f"Columnas faltantes en ventas.csv: {missing}"
```

**Si falla:** revisar los nombres exactos de columnas en el sistema de origen. Adaptar `clean_venta.py` para renombrar si es necesario.

---

## V02 — ventas.csv: VendedorID es entero

**Qué chequear:** la columna VendedorID no tiene texto, NaN ni decimales.

```python
df = pd.read_csv("inputs/ventas.csv")
df["VendedorID"] = pd.to_numeric(df["VendedorID"], errors="coerce")
assert df["VendedorID"].notna().all(), "VendedorID tiene valores no numéricos"
assert (df["VendedorID"] == df["VendedorID"].astype(int)).all(), "VendedorID tiene decimales"
```

**Si falla:** el sistema de origen puede exportar IDs como `2.0` o `"V02"`. Corregir en `clean_venta.py`.

---

## V03 — ventas.csv: IDs de vendedores coinciden con config

**Qué chequear:** todos los VendedorIDs en ventas.csv aparecen en `config_app.json → vendor_names`.

```python
import json
with open("config_app.json") as f:
    cfg = json.load(f)
vendor_ids_config = set(cfg["vendor_names"].keys())

df = pd.read_csv("inputs/ventas.csv")
vendor_ids_ventas = set(df["VendedorID"].dropna().astype(int).astype(str).unique())

sin_nombre = vendor_ids_ventas - vendor_ids_config
if sin_nombre:
    print(f"AVISO: vendedores en ventas sin nombre en config: {sin_nombre}")
```

**Si falla:** agregar el VendedorID faltante a `vendor_names` en `config_app.json`.

---

## V04 — gescom.xlsx: columnas requeridas

**Qué chequear:** el padrón tiene las columnas mínimas.

```python
df = pd.read_excel("inputs/gescom.xlsx", nrows=1)
required = {"ClienteID", "RazonSocial", "VendedorID", "TAXONOMIA"}
missing = required - set(df.columns)
assert not missing, f"Columnas faltantes en gescom.xlsx: {missing}"
```

**Si falla:** verificar el nombre exacto de la columna de taxonomía. Puede llamarse `Taxonomia`, `CLASE`, `SEGMENTO`. Adaptar en el pipeline.

---

## V05 — gescom.xlsx: TAXONOMIA tiene solo valores P/A/B/C

**Qué chequear:** no hay valores inesperados en la columna de taxonomía.

```python
df = pd.read_excel("inputs/gescom.xlsx")
valores = set(df["TAXONOMIA"].dropna().str.strip().str.upper().unique())
validos = {"P", "A", "B", "C"}
invalidos = valores - validos
if invalidos:
    print(f"AVISO: valores inesperados en TAXONOMIA: {invalidos}")
    print(f"Registros afectados: {df[~df['TAXONOMIA'].isin(validos)].shape[0]}")
```

**Si falla:** mapear los valores del cliente a P/A/B/C en `clean_venta.py` o en el gescom directamente.

---

## V06 — gescom.xlsx: ClienteID coincide con ventas.csv

**Qué chequear:** la mayoría de los clientes en ventas existen en el padrón.

```python
df_ventas = pd.read_csv("inputs/ventas.csv")
df_gescom = pd.read_excel("inputs/gescom.xlsx")

ids_ventas = set(df_ventas["ClienteID"].astype(str).unique())
ids_gescom = set(df_gescom["ClienteID"].astype(str).unique())

en_ventas_sin_gescom = ids_ventas - ids_gescom
pct_sin_padron = len(en_ventas_sin_gescom) / len(ids_ventas) * 100

print(f"Clientes en ventas: {len(ids_ventas)}")
print(f"Sin padrón: {len(en_ventas_sin_gescom)} ({pct_sin_padron:.1f}%)")
assert pct_sin_padron < 20, "Más del 20% de clientes en ventas no está en gescom"
```

**Si falla:** los IDs de cliente pueden tener formato distinto (con/sin ceros, mayúsculas). Normalizar en `clean_venta.py`.

---

## V07 — objetivo_vendedor_tp.xlsx: sin celdas vacías

**Qué chequear:** todas las filas de objetivos tienen VendedorID, Zona y Objetivo completos.

```python
df = pd.read_excel("inputs/objetivo_vendedor_tp.xlsx")
for col in ["VendedorID", "Zona", "Objetivo"]:
    nulls = df[col].isna().sum()
    assert nulls == 0, f"Columna {col} en objetivos tiene {nulls} valores vacíos"
```

**Si falla:** completar el archivo de objetivos con todos los valores.

---

## V08 — objetivo_vendedor_tp.xlsx: zonas válidas

**Qué chequear:** las zonas en el archivo de objetivos son LU/MA/MI/JU/VI/SA exactamente.

```python
df = pd.read_excel("inputs/objetivo_vendedor_tp.xlsx")
zonas_validas = {"LU", "MA", "MI", "JU", "VI", "SA"}
zonas_en_archivo = set(df["Zona"].str.strip().str.upper().unique())
invalidas = zonas_en_archivo - zonas_validas
assert not invalidas, f"Zonas inválidas en objetivos: {invalidas}"
```

**Si falla:** reemplazar por los códigos correctos en el Excel.

---

## V09 — lista_precios.xlsx: columna Articulo coincide con ventas

**Qué chequear:** al menos el 50% de los SKUs en ventas tienen precio definido.

```python
df_ventas = pd.read_csv("inputs/ventas.csv")
df_precios = pd.read_excel("inputs/lista_precios.xlsx")

skus_ventas = set(df_ventas["Articulo"].astype(str).unique())
skus_precios = set(df_precios["Articulo"].astype(str).unique())

sin_precio = skus_ventas - skus_precios
pct_sin_precio = len(sin_precio) / len(skus_ventas) * 100
print(f"SKUs sin precio: {len(sin_precio)} ({pct_sin_precio:.1f}%)")
if pct_sin_precio > 50:
    print("ALERTA: más del 50% de SKUs sin precio — verificar formato de Articulo")
```

**Si falla:** los códigos de SKU pueden tener formato distinto. Normalizar antes de la comparación.

---

## V10 — Google Sheets: hojas requeridas existen

**Qué chequear:** después del primer sync, las 4 hojas existen en el Spreadsheet.

Verificar en la UI de Google Sheets que existen las pestañas:
- `pdf_index`
- `clientes_oportunidad`
- `foco_productos`
- `tp_objetivos_resumen`

O via API:
```python
from googleapiclient.discovery import build
# ... auth ...
meta = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
hojas = {s["properties"]["title"] for s in meta["sheets"]}
requeridas = {"pdf_index", "clientes_oportunidad", "foco_productos", "tp_objetivos_resumen"}
faltantes = requeridas - hojas
assert not faltantes, f"Hojas faltantes en Sheets: {faltantes}"
```

**Si falla:** correr el sync completo una vez para que el pipeline cree las hojas.

---

## V11 — Portal: variables de entorno definidas

**Qué chequear:** antes del deploy, todas las variables están en `portal/.env` o en Render.

```bash
# Variables requeridas:
GOOGLE_SERVICE_ACCOUNT_JSON  → no debe ser PENDIENTE ni vacío
SPREADSHEET_ID               → debe ser el ID real (no TODO)
MGMT_PASSWORD                → mínimo 8 caracteres
VENDOR_PASSWORD              → mínimo 8 caracteres
VENDOR_NAMES                 → JSON válido con al menos 1 vendedor
HOST                         → debe ser 0.0.0.0
```

**Si falla:** completar las variables antes del deploy. Ver `06_CONFIGURACION_GOOGLE_RENDER.md`.

---

## V12 — Tests E2E del portal

**Qué chequear:** los 7 smoke tests pasan con la configuración de la nueva distribuidora.

```bash
cd portal
npm run test:e2e
```

Resultado esperado: `7 passed`

**Si falla:** revisar el log de Playwright para identificar qué test falló. Los tests más comunes que fallan en nuevas configuraciones son los de login (contraseñas incorrectas en `.env`).

---

## Resumen de validadores

| ID | Archivo | Qué chequea | Severidad |
|---|---|---|---|
| V01 | ventas.csv | Columnas requeridas | Error |
| V02 | ventas.csv | VendedorID es entero | Error |
| V03 | ventas.csv + config | IDs coinciden | Warning |
| V04 | gescom.xlsx | Columnas requeridas | Error |
| V05 | gescom.xlsx | TAXONOMIA = P/A/B/C | Warning |
| V06 | gescom + ventas | ClienteID coincide (≥80%) | Error |
| V07 | objetivos.xlsx | Sin celdas vacías | Error |
| V08 | objetivos.xlsx | Zonas válidas | Error |
| V09 | precios + ventas | SKUs con precio (≥50%) | Warning |
| V10 | Google Sheets | Hojas requeridas existen | Post-sync |
| V11 | portal/.env | Variables definidas | Pre-deploy |
| V12 | portal | Tests E2E 7/7 | Pre-deploy |

**Error**: detiene la implementación hasta corregir.  
**Warning**: puede avanzar pero registrar para revisión posterior.  
**Post-sync**: verificar después del primer sync.  
**Pre-deploy**: verificar antes del deploy en Render.
