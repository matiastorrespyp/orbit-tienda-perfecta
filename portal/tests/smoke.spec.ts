import { test, expect } from '@playwright/test';
import fs from 'fs';

const MGMT_PASSWORD = 'smoke_mgmt';
const VENDOR_PASSWORD = 'smoke_vendor';
const SS = 'test-results/screenshots';

test.beforeAll(() => {
  fs.mkdirSync(SS, { recursive: true });
});

test('1 - landing carga y muestra formulario', async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  await page.goto('/');
  await page.locator('select[name="vendedor_id"] option[value="gerencia"]').waitFor({ state: 'attached' });

  await expect(page).toHaveTitle('Orbit · Tienda Perfecta');
  await expect(page.locator('select[name="vendedor_id"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();

  await page.screenshot({ path: `${SS}/01-landing.png`, fullPage: true });
  expect(consoleErrors).toEqual([]);
});

test('2 - login inválido muestra error en pantalla', async ({ page }) => {
  await page.goto('/');
  await page.locator('select[name="vendedor_id"] option[value="gerencia"]').waitFor({ state: 'attached' });

  await page.selectOption('select[name="vendedor_id"]', 'gerencia');
  await page.fill('input[name="password"]', 'clave_incorrecta');
  await page.screenshot({ path: `${SS}/02-login-invalido-antes.png` });

  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/error=1/);
  await expect(page.getByText('Contraseña incorrecta')).toBeVisible();
  await page.screenshot({ path: `${SS}/03-login-invalido-error.png` });
});

test('3 - perfil vacío muestra error antes de enviar', async ({ page }) => {
  await page.goto('/');
  await page.locator('select[name="vendedor_id"] option[value="gerencia"]').waitFor({ state: 'attached' });

  await page.fill('input[name="password"]', 'cualquier_clave');
  await page.click('button[type="submit"]');

  await expect(page.getByText('Seleccioná un perfil', { exact: true })).toBeVisible();
  await page.screenshot({ path: `${SS}/04-perfil-vacio-error.png` });
});

test('4 - login gerencia por UI redirige a /gerencia', async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  await page.route(/\/gerencia(\?.*)?$/, route =>
    route.fulfill({
      status: 200,
      contentType: 'text/html',
      body: '<html><head><title>Gerencia</title></head><body>mock-gerencia</body></html>',
    })
  );

  await page.goto('/');
  await page.locator('select[name="vendedor_id"] option[value="gerencia"]').waitFor({ state: 'attached' });

  await page.selectOption('select[name="vendedor_id"]', 'gerencia');
  await page.fill('input[name="password"]', MGMT_PASSWORD);
  await page.screenshot({ path: `${SS}/05-gerencia-formulario.png` });

  await page.click('button[type="submit"]');
  await page.waitForURL(/\/gerencia/, { timeout: 5000 });

  await page.screenshot({ path: `${SS}/06-gerencia-post-login.png` });
  expect(page.url()).toContain('/gerencia');
  expect(consoleErrors).toEqual([]);
});

test('5 - login vendedor por UI redirige a /vendedor', async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  await page.route(/\/vendedor(\?.*)?$/, route =>
    route.fulfill({
      status: 200,
      contentType: 'text/html',
      body: '<html><head><title>Vendedor</title></head><body>mock-vendedor</body></html>',
    })
  );

  await page.goto('/');
  await page.locator('select[name="vendedor_id"] option[value="2"]').waitFor({ state: 'attached' });

  await page.selectOption('select[name="vendedor_id"]', '2');
  await page.fill('input[name="password"]', VENDOR_PASSWORD);
  await page.screenshot({ path: `${SS}/07-vendedor-formulario.png` });

  await page.click('button[type="submit"]');
  await page.waitForURL(/\/vendedor/, { timeout: 5000 });

  await page.screenshot({ path: `${SS}/08-vendedor-post-login.png` });
  expect(page.url()).toContain('/vendedor');
  expect(consoleErrors).toEqual([]);
});

test('API - gerencia acepta credenciales correctas', async ({ request }) => {
  const resp = await request.post('/api/login', {
    form: { role: 'gerencia', password: MGMT_PASSWORD, vendedor_id: 'gerencia' },
  });

  expect(resp.url()).not.toContain('error=1');
  expect(resp.url()).toContain('/gerencia');
});

test('API - vendedor acepta credenciales correctas', async ({ request }) => {
  const resp = await request.post('/api/login', {
    form: { role: 'vendedor', password: VENDOR_PASSWORD, vendedor_id: '2' },
  });

  expect(resp.url()).not.toContain('error=1');
  expect(resp.url()).toContain('/vendedor');
});
