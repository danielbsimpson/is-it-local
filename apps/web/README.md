# Is It Local — Web App

Next.js 14 (App Router) frontend for searching businesses and viewing ownership
classifications produced by the Phase 1 API and enrichment pipeline.

## Prerequisites

- Node 20+ and pnpm
- The Phase 1 API running (default `http://localhost:8000`)

## Setup

From the repository root:

```powershell
pnpm install
```

Copy the example environment file and adjust as needed:

```powershell
Copy-Item apps/web/.env.example apps/web/.env.local
```

| Variable                   | Purpose                      | Default                 |
| -------------------------- | ---------------------------- | ----------------------- |
| `NEXT_PUBLIC_API_BASE_URL` | Base URL of the Phase 1 API  | `http://localhost:8000` |
| `NEXT_PUBLIC_MAP_TILE_URL` | Leaflet raster tile template | OpenStreetMap tiles     |
| `NEXT_PUBLIC_GEOCODE_URL`  | Nominatim search endpoint    | OpenStreetMap Nominatim |

## Scripts

```powershell
pnpm --filter @is-it-local/web dev        # start dev server on :3000
pnpm --filter @is-it-local/web build      # production build
pnpm --filter @is-it-local/web typecheck  # tsc --noEmit
pnpm --filter @is-it-local/web lint        # next lint
pnpm --filter @is-it-local/web test        # vitest unit/component tests
pnpm --filter @is-it-local/web e2e         # Playwright smoke tests (needs stack running)
```

## Structure

```
src/
  app/                 App Router routes (home, search, business/[id], error, not-found)
  components/          Presentational + client components
  lib/                 api-client, classification map, distance, geocode, logger, config
  types/               Local view models re-exporting @is-it-local/shared
tests/                 Vitest component tests
e2e/                   Playwright smoke tests (deferred)
```

### Conventions

- All backend access goes through `src/lib/api-client.ts` (single API client).
- Classification colors/labels live only in `src/lib/classification.ts`.
- Ownership types are reused from `@is-it-local/shared`.
- External links use `target="_blank" rel="noopener noreferrer"`.
- No third-party analytics or monitoring; events log to the console via `src/lib/logger.ts`.
- The map (`BusinessMap`) is client-only and loaded with `next/dynamic` (`ssr: false`).
