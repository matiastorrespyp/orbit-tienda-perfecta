/**
 * google.ts — Auth compartida y acceso a Google Sheets y Drive.
 * Service Account via GOOGLE_SERVICE_ACCOUNT_JSON env var.
 */

import { google } from 'googleapis';

const CACHE_TTL_MS = 5 * 60 * 1000;

// ─── Auth ─────────────────────────────────────────────────────────────────────

function getAuth() {
  const raw = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;
  if (!raw) throw new Error('[google] GOOGLE_SERVICE_ACCOUNT_JSON no está definida');
  return new google.auth.GoogleAuth({
    credentials: JSON.parse(raw),
    scopes: [
      'https://www.googleapis.com/auth/spreadsheets.readonly',
      'https://www.googleapis.com/auth/drive.readonly',
    ],
  });
}

// ─── Sheets ───────────────────────────────────────────────────────────────────

interface SheetCache { rows: Record<string, string>[]; ts: number; }
const _sheetCache = new Map<string, SheetCache>();

export async function readSheet(sheetName: string): Promise<Record<string, string>[]> {
  const ssId = process.env.SPREADSHEET_ID ?? '1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0';
  const now = Date.now();
  const hit = _sheetCache.get(sheetName);
  if (hit && now - hit.ts < CACHE_TTL_MS) return hit.rows;

  try {
    const sheets = google.sheets({ version: 'v4', auth: getAuth() });
    const res = await sheets.spreadsheets.values.get({ spreadsheetId: ssId, range: sheetName });
    const raw = res.data.values ?? [];
    if (raw.length < 2) {
      _sheetCache.set(sheetName, { rows: [], ts: now });
      return [];
    }
    const headers = raw[0].map(String);
    const rows = raw.slice(1).map(row => {
      const obj: Record<string, string> = {};
      headers.forEach((h, i) => { obj[h] = row[i] != null ? String(row[i]) : ''; });
      return obj;
    });
    _sheetCache.set(sheetName, { rows, ts: now });
    return rows;
  } catch (err) {
    console.error(`[sheets] Error leyendo "${sheetName}":`, err);
    return hit?.rows ?? [];
  }
}

// ─── Drive ────────────────────────────────────────────────────────────────────

interface DriveCache { url: string | null; ts: number; }
const _driveCache = new Map<string, DriveCache>();

/**
 * Devuelve la URL de vista de Google Drive para un PDF.
 * Drive API v3 no soporta búsqueda recursiva nativa ('in ancestors' no existe).
 * Estrategia: buscar en subcarpeta por fecha → fallback en carpeta raíz.
 * @param filename     Nombre del archivo, ej. 'Vendedor_2_VI.pdf'
 * @param rootFolderId ID de la carpeta raíz en Drive
 * @param dateSub      Subcarpeta de fecha, ej. '2026-05-12' (opcional)
 */
export async function getDriveViewUrl(
  filename: string,
  rootFolderId: string,
  dateSub?: string,
): Promise<string | null> {
  if (!filename || !rootFolderId) return null;

  const key = `${rootFolderId}::${dateSub ?? ''}::${filename}`;
  const now = Date.now();
  const hit = _driveCache.get(key);
  if (hit && now - hit.ts < CACHE_TTL_MS) return hit.url;

  try {
    const safe = (s: string) => s.replace(/\\/g, '').replace(/'/g, "\\'");
    const drive = google.drive({ version: 'v3', auth: getAuth() });

    // Paso 1: buscar en subcarpeta de fecha si se indicó
    if (dateSub) {
      const subRes = await drive.files.list({
        q: `name = '${safe(dateSub)}' and '${rootFolderId}' in parents`
          + ` and mimeType = 'application/vnd.google-apps.folder' and trashed = false`,
        fields: 'files(id)',
        pageSize: 1,
      });
      const subId = subRes.data.files?.[0]?.id;
      if (subId) {
        const fileRes = await drive.files.list({
          q: `name = '${safe(filename)}' and '${subId}' in parents and trashed = false`,
          fields: 'files(id)',
          pageSize: 1,
        });
        const fileId = fileRes.data.files?.[0]?.id;
        if (fileId) {
          const url = `https://drive.google.com/file/d/${fileId}/view`;
          _driveCache.set(key, { url, ts: now });
          return url;
        }
      }
    }

    // Paso 2 (fallback): buscar directamente en carpeta raíz
    const rootRes = await drive.files.list({
      q: `name = '${safe(filename)}' and '${rootFolderId}' in parents and trashed = false`,
      fields: 'files(id)',
      pageSize: 1,
    });
    const fileId = rootRes.data.files?.[0]?.id ?? null;
    const url = fileId ? `https://drive.google.com/file/d/${fileId}/view` : null;
    _driveCache.set(key, { url, ts: now });
    return url;
  } catch (err) {
    console.error(`[drive] Error buscando "${filename}":`, err);
    return hit?.url ?? null;
  }
}
