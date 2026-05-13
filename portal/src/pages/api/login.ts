import type { APIRoute } from 'astro';
import { getConfig } from '../../lib/config';

export const POST: APIRoute = async ({ request, cookies, redirect }) => {
  const data = await request.formData();
  const role        = data.get('role')?.toString()        ?? '';
  const password    = data.get('password')?.toString()    ?? '';
  const vendedor_id = data.get('vendedor_id')?.toString() ?? '';

  const cfg = getConfig();

  if (role === 'gerencia' && password === cfg.mgmt_password) {
    cookies.set('orbit_role', 'gerencia', { path: '/', maxAge: 86400, httpOnly: true });
    return redirect('/gerencia');
  }
  if (role === 'vendedor' && password === cfg.vendor_password && vendedor_id) {
    cookies.set('orbit_role', `vendedor_${vendedor_id}`, { path: '/', maxAge: 86400, httpOnly: true });
    return redirect(`/vendedor?id=${vendedor_id}`);
  }
  return redirect('/?error=1');
};
