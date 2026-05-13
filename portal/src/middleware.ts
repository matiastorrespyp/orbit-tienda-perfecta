import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (ctx, next) => {
  const { pathname } = ctx.url;
  if (
    pathname === '/' ||
    pathname.startsWith('/api/login') ||
    pathname.startsWith('/api/logout') ||
    pathname.startsWith('/assets/') ||
    pathname === '/favicon.ico'
  ) return next();

  const role = ctx.cookies.get('orbit_role')?.value;
  if (!role) return ctx.redirect('/');
  return next();
});
