// config.ts — Lee configuración desde variables de entorno.
// En producción (Render/Railway): definir en el dashboard de la plataforma.
// En local: crear portal/.env con los valores reales (ver portal/.env.example).

export interface AppConfig {
  mgmt_password: string;
  vendor_password: string;
  vendor_names: Record<string, string>;
}

export function getConfig(): AppConfig {
  const mgmt_password   = process.env.MGMT_PASSWORD   ?? '';
  const vendor_password = process.env.VENDOR_PASSWORD ?? '';

  let vendor_names: Record<string, string> = {};
  try {
    vendor_names = JSON.parse(process.env.VENDOR_NAMES ?? '{}');
  } catch {
    console.warn('[config] VENDOR_NAMES no es JSON válido — verificá la variable de entorno');
  }

  if (!mgmt_password || !vendor_password)
    console.warn('[config] MGMT_PASSWORD o VENDOR_PASSWORD no están definidas');

  return { mgmt_password, vendor_password, vendor_names };
}
