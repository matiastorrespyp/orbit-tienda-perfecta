import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:4321',
  },
  webServer: {
    command: 'node dist/server/entry.mjs',
    url: 'http://localhost:4321',
    reuseExistingServer: false,
    env: {
      HOST: '0.0.0.0',
      PORT: '4321',
      // Credenciales de prueba — sin acceso real a Google
      MGMT_PASSWORD:               'smoke_mgmt',
      VENDOR_PASSWORD:             'smoke_vendor',
      VENDOR_NAMES:                '{"2":"Test"}',
      SPREADSHEET_ID:              'fake_id',
      GOOGLE_SERVICE_ACCOUNT_JSON: '{"type":"service_account"}',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
