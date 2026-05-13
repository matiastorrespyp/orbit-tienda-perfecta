import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ cookies, redirect }) => {
  cookies.delete('orbit_role', { path: '/' });
  return redirect('/');
};
