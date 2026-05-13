/**
 * Orbit · Tienda Perfecta — Apps Script Web App
 * Datos para vendedores sin depender de PC local.
 *
 * Primer uso — configurar contraseñas UNA VEZ en la consola Apps Script:
 *   PropertiesService.getScriptProperties().setProperties({
 *     VENDOR_PASSWORD: 'tp2026',
 *     MGMT_PASSWORD:   'orbit2026'
 *   });
 */

// ─── Configuración ────────────────────────────────────────────────────────────

const SS_ID             = '1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0';
const FOLDER_VENDEDORES = '1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa';

const VENDOR_NAMES = {
  '2': 'Juliana',
  '3': 'Nadia',
  '4': 'Ángel',
  '5': 'Majo',
  '6': 'Andrea'
};

// ─── Entry point ──────────────────────────────────────────────────────────────

function doGet() {
  return HtmlService
    .createTemplateFromFile('ui_main')
    .evaluate()
    .setTitle('Orbit · Tienda Perfecta')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// Permite usar <?!= include('archivo') ?> en las plantillas HTML
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

// ─── Autenticación ────────────────────────────────────────────────────────────

function autenticar(id, password) {
  try {
    const props = PropertiesService.getScriptProperties();
    const vPass = props.getProperty('VENDOR_PASSWORD');
    const mPass = props.getProperty('MGMT_PASSWORD');

    if (!vPass || !mPass)
      return { ok: false, error: 'Contraseñas no configuradas. Ejecutá configurarContrasenas() según el README Paso 4.' };

    if (id === 'gerencia' && password === mPass)
      return { ok: true, rol: 'gerencia', nombre: 'Gerencia' };

    if (VENDOR_NAMES[id] && password === vPass)
      return { ok: true, rol: 'vendedor', id, nombre: VENDOR_NAMES[id] };

    return { ok: false };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// ─── Setup (ejecutar una sola vez desde el editor de Apps Script) ─────────────

function configurarContrasenas() {
  PropertiesService.getScriptProperties().setProperties({
    VENDOR_PASSWORD: 'tp2026',
    MGMT_PASSWORD:   'orbit2026'
  });
  Logger.log('Contraseñas guardadas en PropertiesService.');
}

// ─── Datos vendedor ───────────────────────────────────────────────────────────

function getDatosVendedor(vendedorId) {
  try {
    const ss      = SpreadsheetApp.openById(SS_ID);
    const pdfRows = sheetToArray(ss, 'pdf_index');
    const cRows   = sheetToArray(ss, 'clientes_oportunidad');
    const fRows   = sheetToArray(ss, 'foco_productos');

    // PDF más reciente del vendedor
    const pdfsV = pdfRows
      .filter(r => String(r.VendedorID) === String(vendedorId) && r.TipoPDF === 'vendedor')
      .sort((a, b) => b.Fecha.localeCompare(a.Fecha));

    let pdfUrl = null, pdfFecha = null;
    if (pdfsV.length) {
      pdfFecha = pdfsV[0].Fecha;
      pdfUrl   = buscarPdfEnDrive(pdfsV[0].ArchivoPDF, FOLDER_VENDEDORES, pdfFecha);
    }

    // Clientes del día más reciente disponible
    const cV = cRows
      .filter(r => String(r.VendedorID) === String(vendedorId))
      .sort((a, b) => b.Fecha.localeCompare(a.Fecha));
    const fechaC      = cV.length ? cV[0].Fecha : '';
    const clientesHoy = cV.filter(r => r.Fecha === fechaC);

    // Focos del día más reciente
    const fV = fRows
      .filter(r => String(r.VendedorID) === String(vendedorId))
      .sort((a, b) => b.Fecha.localeCompare(a.Fecha) || Number(a.Rank) - Number(b.Rank));
    const fechaF   = fV.length ? fV[0].Fecha : '';
    const focosHoy = fV.filter(r => r.Fecha === fechaF);

    return {
      ok:       true,
      nombre:   VENDOR_NAMES[vendedorId] || `Vendedor ${vendedorId}`,
      fecha:    fechaC || pdfFecha || '',
      pdfUrl,
      pdfFecha,
      clientes: clientesHoy,
      focos:    focosHoy
    };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// ─── Datos gerencia ───────────────────────────────────────────────────────────

function getDatosGerencia() {
  try {
    const ss = SpreadsheetApp.openById(SS_ID);

    const objRows = sheetToArray(ss, 'tp_objetivos_resumen')
      .sort((a, b) => b.Fecha.localeCompare(a.Fecha));
    const fechaO       = objRows.length ? objRows[0].Fecha : '';
    const objetivosHoy = objRows.filter(r => r.Fecha === fechaO);

    const facRows = sheetToArray(ss, 'tp_facturacion_comparativa')
      .sort((a, b) => b.PeriodoDesde.localeCompare(a.PeriodoDesde));

    return { ok: true, fecha: fechaO, objetivos: objetivosHoy, facturacion: facRows };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// ─── Helpers internos ─────────────────────────────────────────────────────────

function sheetToArray(ss, sheetName) {
  const sh = ss.getSheetByName(sheetName);
  if (!sh) return [];
  const vals = sh.getDataRange().getValues();
  if (vals.length < 2) return [];
  const headers = vals[0].map(String);
  return vals.slice(1).map(row => {
    const obj = {};
    headers.forEach((h, i) => { obj[h] = (row[i] != null) ? String(row[i]) : ''; });
    return obj;
  });
}

function buscarPdfEnDrive(filename, folderId, fecha) {
  if (!filename || !folderId) return null;
  try {
    const root = DriveApp.getFolderById(folderId);

    // Buscar en subcarpeta con nombre igual a la fecha (YYYY-MM-DD)
    if (fecha) {
      const subs = root.getFoldersByName(fecha);
      if (subs.hasNext()) {
        const archivos = subs.next().getFilesByName(filename);
        if (archivos.hasNext()) return archivos.next().getUrl();
      }
    }

    // Fallback: raíz de la carpeta
    const archivos = root.getFilesByName(filename);
    if (archivos.hasNext()) return archivos.next().getUrl();

    return null;
  } catch (e) {
    return null;
  }
}
