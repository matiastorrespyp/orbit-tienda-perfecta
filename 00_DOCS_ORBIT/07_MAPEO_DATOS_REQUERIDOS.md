# 07 — Mapeo de Datos Requeridos

## Inputs del pipeline

### ventas.csv

Exportado del sistema de facturación (GESCOM u otro). Procesado primero por `clean_venta.py`.

| Columna requerida | Tipo | Ejemplo | Notas |
|---|---|---|---|
| Fecha | string | `2026-05-14` o `14/05/2026` | `clean_venta.py` normaliza el formato |
| VendedorID | int | `2` | Debe ser entero, sin decimales |
| ClienteID | string | `C00123` | Clave única del cliente |
| Articulo | string | `LAC001` | Código de SKU |
| Cantidad | float | `12` | Unidades vendidas |
| Importe | float | `8400.50` | Moneda local |

Columnas opcionales reconocidas: `RazonSocial`, `Localidad`, `Zona`.

### gescom.xlsx

Padrón de clientes activos de la distribuidora.

| Columna requerida | Tipo | Ejemplo | Notas |
|---|---|---|---|
| ClienteID | string | `C00123` | Debe coincidir con ventas.csv |
| RazonSocial | string | `Almacén La Paz` | Nombre del cliente |
| Localidad | string | `Mar del Plata` | Ciudad o partido |
| Direccion | string | `Av. Colón 1234` | Dirección postal |
| VendedorID | int | `2` | Vendedor asignado |
| TAXONOMIA | string | `A` | Clasificación: P, A, B o C |
| TP_Sistema | string | `SI` / `NO` | Si el cliente tiene TP activo en sistema |
| TP_Aplica | string | `SI` / `NO` | Si el cliente aplica para TP |

### Portafolio Infaltable - Argentina.pptx

PowerPoint con los SKUs que componen Tienda Perfecta. El pipeline extrae de aquí la lista de productos obligatorios y su categoría.

Estructura esperada: cada slide o tabla lista un SKU con su código y descripción.

### lista_precios.xlsx

| Columna | Tipo | Descripción |
|---|---|---|
| Articulo | string | Código SKU (debe coincidir con ventas.csv) |
| Descripcion | string | Nombre del producto |
| Precio | float | Precio de venta unitario |

### objetivo_vendedor_tp.xlsx

| Columna | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| VendedorID | int | `2` | ID del vendedor |
| VendedorNombre | string | `Juliana` | Nombre (opcional) |
| Zona | string | `JU` | Código de día |
| Objetivo | int | `97` | Clientes TP objetivo para esa zona |

---

## Outputs del pipeline

### output/APPSHEET/pdf_index.csv

Índice de todos los PDFs generados. Usado por el portal para localizar PDFs en Drive.

| Columna | Descripción |
|---|---|
| Fecha | Fecha de generación (YYYY-MM-DD) |
| Dia | Código de zona (LU/MA/...) |
| TipoPDF | `vendedor` o `gerencial` |
| VendedorID | ID del vendedor (vacío para gerencial) |
| VendedorNombre | Nombre del vendedor |
| ArchivoPDF | Nombre del archivo (ej. `Vendedor_2_JU.pdf`) |
| RutaPDF | Ruta relativa local |
| RutaPDF_Relativa | Ruta relativa para Drive |
| Zona | Código de día |
| Rol | `vendedor` o `gerencia` |
| Visible | `SI` / `NO` |
| GeneradoEn | Timestamp |

### output/APPSHEET/clientes_oportunidad.csv

Un row por cliente, con KPIs de cumplimiento TP.

| Columna | Descripción |
|---|---|
| Fecha | Fecha del informe |
| Dia | Zona |
| VendedorID | ID del vendedor |
| VendedorNombre | Nombre del vendedor |
| ClienteID | ID del cliente |
| RazonSocial | Nombre del cliente |
| Localidad | Ciudad |
| Direccion | Dirección |
| PortafolioPct | % de SKUs TP comprados (0–100+) |
| Faltan80 | SKUs que faltan para llegar al 80% |
| Faltan100 | SKUs que faltan para llegar al 100% |
| SKUsFaltan80 | Lista de códigos separados por `;` |
| SKUsFaltan100 | Lista de códigos separados por `;` |
| TP_Sistema | Si tiene TP activo en sistema |
| TP_Aplica | Si aplica para TP |

### output/APPSHEET/foco_productos.csv

Top SKUs con mayor cantidad de clientes que los faltan.

| Columna | Descripción |
|---|---|
| Fecha | Fecha |
| Dia | Zona |
| Scope | `general`, `vendedor` |
| VendedorID | ID (vacío si Scope=general) |
| VendedorNombre | Nombre |
| Rank | Posición (1 = más urgente) |
| Articulo | Código SKU |
| CantClientes | Clientes que necesitan este SKU |

### output/APPSHEET/tp_objetivos_resumen.csv

Objetivos con cumplimiento actual. Tres niveles de agregación.

| Columna | Descripción |
|---|---|
| Scope | `general`, `vendedor`, `taxonomia` |
| VendedorID | ID (vacío si Scope≠vendedor) |
| VendedorNombre | Nombre / etiqueta taxonomía (P/A/B/C) |
| Zona | Código de día |
| Fecha | Fecha |
| Objetivo | Clientes TP objetivo |
| Acumulado | Clientes TP activos hoy |
| RealDia | Clientes TP activados en el día |
| Faltante | Objetivo - Acumulado (0 si ya cumplió) |
| CumplimientoPct | Acumulado / Objetivo × 100 |

---

## Google Sheets — hojas del Spreadsheet

| Hoja | Origen CSV | Modo | Descripción |
|---|---|---|---|
| `pdf_index` | `pdf_index.csv` | Desde B1 | Índice de PDFs |
| `clientes_oportunidad` | `clientes_oportunidad.csv` | Desde B1 | Clientes con KPIs |
| `foco_productos` | `foco_productos.csv` | Desde B1 | Productos foco |
| `tp_objetivos_resumen` | `tp_objetivos_resumen.csv` | Desde A1 | Objetivos |

**Desde B1**: la columna A tiene una fórmula de ID que AppSheet necesita. El sync no la toca.  
**Desde A1**: full overwrite, sin columna de ID extra.

---

## Mapeo entre distribuidoras

Al replicar en una nueva distribuidora, el único cambio estructural en los datos es:

1. **VendedorID**: los números deben coincidir entre todas las fuentes (ventas.csv, gescom.xlsx, objetivos, config_app.json)
2. **TAXONOMIA**: debe tener solo los valores `P`, `A`, `B`, `C`
3. **Zona**: debe ser uno de `LU`, `MA`, `MI`, `JU`, `VI`, `SA`
4. **Portafolio**: el SKU set puede variar por distribuidora — el archivo .pptx es la fuente de verdad

Los nombres de columnas deben ser idénticos o mapearse en `clean_venta.py`.
