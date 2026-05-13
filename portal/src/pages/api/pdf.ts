// api/pdf.ts — Resuelve PDFs vía redirect 302 a Google Drive.
// Antes: fs.readFileSync desde disco local.
// Ahora: extrae filename y subcarpeta de fecha del parámetro ruta,
//        busca el archivo en Drive y redirige.

import type { APIRoute } from 'astro';
import { getDriveViewUrl } from '../../lib/google';

const FOLDER_VENDEDORES = '1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa';
const FOLDER_GERENCIAL  = '1tlBd2GrWuJAjYX0dwn6dsfbnDh6gM8PQ';

export const GET: APIRoute = async ({ url }) => {
  const ruta = url.searchParams.get('ruta');
  if (!ruta) return new Response('Missing ruta', { status: 400 });

  // Normalizar separadores y dividir en partes
  // Ej: "PDF_VENDEDORES/2026-05-12/Vendedor_2_VI.pdf"
  const parts    = ruta.replace(/\\/g, '/').split('/');
  const filename = parts.at(-1) ?? '';
  // dateSub = '2026-05-12' si el path tiene al menos 3 segmentos, undefined si es plano
  const dateSub  = parts.length >= 3 ? parts.at(-2) : undefined;

  if (!filename.toLowerCase().endsWith('.pdf'))
    return new Response('Ruta inválida', { status: 400 });

  const folderId = ruta.toUpperCase().includes('GERENCIAL')
    ? FOLDER_GERENCIAL
    : FOLDER_VENDEDORES;

  const driveUrl = await getDriveViewUrl(filename, folderId, dateSub);
  if (!driveUrl)
    return new Response('PDF no encontrado en Google Drive', { status: 404 });

  return new Response(null, {
    status: 302,
    headers: { Location: driveUrl },
  });
};
