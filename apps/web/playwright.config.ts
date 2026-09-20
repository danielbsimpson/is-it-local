import { defineConfig, devices } from "@playwright/test";

/**
 * Smoke-test configuration. Runtime execution is deferred until the full stack
 * (API + web) is available; run with `pnpm --filter @is-it-local/web e2e`.
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
