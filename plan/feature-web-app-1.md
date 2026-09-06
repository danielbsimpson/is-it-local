---
goal: Implement Phase 2 Web App (Next.js) for Is It Local — search UI, results with classification badges, business detail with map, analytics, and a public preview deployment
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: "Planned"
tags: [feature, frontend, web, nextjs]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan operationalizes **Phase 2 — Web App (Next.js)** from [TODO.md](../TODO.md). It delivers a TypeScript Next.js application in `apps/web` that lets users search businesses by name and location, view results with ownership classification badges, open a business detail page showing classification, confidence, cited sources, and a map, and provides a responsive layout. For the local-first PoC the app runs entirely on your machine (`pnpm dev`) against the local API, uses free OpenStreetMap map tiles and a Nominatim geocoder, and does not integrate any third-party analytics, error-monitoring, or hosted deployment. This plan consumes the REST API and shared types produced in Phase 1 ([feature-backend-data-1.md](feature-backend-data-1.md)) and Phase 0 ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).

## 1. Requirements & Constraints

- **REQ-001**: The web app MUST be implemented with Next.js (App Router) and TypeScript in `apps/web`.
- **REQ-002**: The web app MUST consume the Phase 1 REST API endpoints `GET /businesses/search` and `GET /businesses/{id}`.
- **REQ-003**: The web app MUST reuse shared types/enums from `@is-it-local/shared` (`OwnershipClassification`, `Business`, `Source`).
- **REQ-004**: The search UI MUST accept a `name` query and a `location` input (free-text geocoded to lat/lon, or browser geolocation) and MUST call the search endpoint with `name`, `lat`, `lon`, and `radius_m`.
- **REQ-005**: The results list MUST render an ownership classification badge for each business using a fixed color mapping for the six classification values.
- **REQ-006**: The business detail page MUST display the classification badge, numeric confidence (rendered as a percentage), a list of cited sources as external links, and a map marker at the business location.
- **REQ-007**: The layout MUST be responsive and usable at viewport widths of 360px, 768px, and 1280px.
- **REQ-008**: The app MUST run without any third-party analytics or error-monitoring services; client errors MUST be surfaced via an in-app error boundary and the browser console.
- **REQ-009**: The app MUST run locally via `pnpm dev` against the local API, with a documented dev workflow; no hosted deployment is required for the PoC.
- **SEC-001**: The API base URL and all third-party keys MUST be provided via environment variables prefixed `NEXT_PUBLIC_` only when client-exposed; server-only secrets MUST NOT use the `NEXT_PUBLIC_` prefix.
- **SEC-002**: All external source links MUST render with `rel="noopener noreferrer"` and `target="_blank"`.
- **SEC-003**: User-provided search input MUST be encoded before insertion into API request URLs to prevent injection.
- **CON-001**: This plan MUST NOT implement authentication, community submissions, or photo lookup (Phase 4+).
- **CON-002**: The web app MUST NOT write to the database directly; all data access MUST go through the Phase 1 REST API.
- **CON-003**: The web app MUST run fully locally for the PoC and MUST NOT depend on any hosted third-party service (analytics, monitoring, or deployment).
- **GUD-001**: All TypeScript MUST pass `tsc --noEmit`, `eslint`, and Prettier formatting checks.
- **GUD-002**: Components MUST be organized as `app/` routes, `components/` (presentational), `lib/` (API client + utilities), and `types/` (local view models).
- **PAT-001**: All API access MUST route through a single typed API client module (`lib/api-client.ts`).
- **PAT-002**: The classification-to-color mapping MUST be defined once in a single module and reused across all components.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Scaffold the Next.js app, typed API client, shared design primitives, and the classification badge system.

| Task     | Description                                                                                                                                                                                                                         | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Scaffold Next.js (App Router, TypeScript, ESLint) in `apps/web`; create `apps/web/package.json` with scripts `dev`, `build`, `start`, `lint`, `typecheck`.                                                                          |           |      |
| TASK-002 | Add `apps/web/tsconfig.json` with a path alias `@is-it-local/shared` resolving to `packages/shared/src`, and register `apps/web` in the pnpm workspace.                                                                             |           |      |
| TASK-003 | Create `apps/web/src/lib/config.ts` reading `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_MAP_TILE_URL` (OpenStreetMap tiles), and `NEXT_PUBLIC_GEOCODE_URL` (Nominatim) from environment variables.                                     |           |      |
| TASK-004 | Create `apps/web/src/lib/api-client.ts` exporting typed functions `searchBusinesses(params)` and `getBusiness(id)` using `fetch`, returning types from `@is-it-local/shared`; encode all query params.                              |           |      |
| TASK-005 | Create `apps/web/src/lib/classification.ts` exporting a `CLASSIFICATION_COLORS` map and `CLASSIFICATION_LABELS` map for the six values (`family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`). |           |      |
| TASK-006 | Create `apps/web/src/components/ClassificationBadge.tsx` rendering the label and color for a given classification value.                                                                                                            |           |      |
| TASK-007 | Create `apps/web/src/components/ConfidenceMeter.tsx` rendering a 0.0–1.0 confidence value as a percentage with an accessible label.                                                                                                 |           |      |
| TASK-008 | Create `apps/web/src/app/layout.tsx` and `apps/web/src/app/globals.css` establishing the responsive base layout, header, and theme tokens.                                                                                          |           |      |
| TASK-009 | Create `apps/web/.env.example` documenting `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_MAP_TILE_URL`, `NEXT_PUBLIC_GEOCODE_URL`.                                                                                                       |           |      |

### Implementation Phase 2

- GOAL-002: Implement the search experience, results list, and business detail page with a map.

| Task     | Description                                                                                                                                                                                                                       | Completed | Date |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-010 | Create `apps/web/src/components/SearchForm.tsx` with a `name` text input, a `location` input, a "use my location" button (browser Geolocation API), and a radius selector; on submit it navigates to `/search` with query params. |           |      |
| TASK-011 | Create `apps/web/src/lib/geocode.ts` exporting `geocode(query) -> {lat, lon}` using a Nominatim (OpenStreetMap) endpoint at `NEXT_PUBLIC_GEOCODE_URL`, with graceful fallback when geolocation/geocoding fails.                   |           |      |
| TASK-012 | Create `apps/web/src/app/page.tsx` (home) rendering the `SearchForm` and a short product explanation.                                                                                                                             |           |      |
| TASK-013 | Create `apps/web/src/app/search/page.tsx` reading query params, calling `searchBusinesses`, and rendering a results list; handle loading, empty, and error states.                                                                |           |      |
| TASK-014 | Create `apps/web/src/components/BusinessCard.tsx` showing name, address, distance, and a `ClassificationBadge`; link to the detail page `/business/[id]`.                                                                         |           |      |
| TASK-015 | Create `apps/web/src/app/business/[id]/page.tsx` calling `getBusiness(id)` and rendering name, address, `ClassificationBadge`, `ConfidenceMeter`, and a cited-sources list with external links (`rel="noopener noreferrer"`).     |           |      |
| TASK-016 | Create `apps/web/src/components/BusinessMap.tsx` rendering a map with a marker at the business location using an OSS map library (`react-leaflet`) and `NEXT_PUBLIC_MAP_TILE_URL`.                                                |           |      |
| TASK-017 | Create `apps/web/src/app/not-found.tsx` and `apps/web/src/app/error.tsx` for 404 and runtime error boundaries.                                                                                                                    |           |      |

### Implementation Phase 3

- GOAL-003: Add responsiveness verification, lightweight local logging, tests, and a documented local run workflow.

| Task     | Description                                                                                                                                                                                       | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-018 | Verify and adjust responsive layout for 360px, 768px, and 1280px breakpoints across home, search, and detail pages.                                                                               |           |      |
| TASK-019 | Create `apps/web/src/lib/logger.ts` exposing a `logEvent(name, props)` function that writes page-view and search events to the browser console (no third-party analytics).                        |           |      |
| TASK-020 | Wire the error boundary (`app/error.tsx`) to the local `logger` and verify the app makes no requests to third-party analytics/monitoring endpoints — only the local API, map tiles, and geocoder. |           |      |
| TASK-021 | Add component/integration tests in `apps/web/tests/` using `vitest` + `@testing-library/react` for `ClassificationBadge`, `SearchForm`, and the search results rendering (mocked API client).     |           |      |
| TASK-022 | Add an end-to-end smoke test with Playwright in `apps/web/e2e/` covering search → results → detail navigation against a mocked or seeded API.                                                     |           |      |
| TASK-023 | Create `apps/web/README.md` documenting local dev, environment variables, build, and preview deployment steps.                                                                                    |           |      |
| TASK-024 | Document the local run workflow (`pnpm --filter web dev`) and required env vars in `apps/web/README.md`; no hosted deployment is configured for the PoC.                                          |           |      |

## 3. Alternatives

- **ALT-001**: Vite + React SPA instead of Next.js — rejected; the README specifies Next.js for SEO-friendly server rendering and shared React patterns with mobile.
- **ALT-002**: Google Maps for the map component — deferred in favor of `react-leaflet` with configurable OSS tiles to avoid mandatory paid keys; can be swapped later via `NEXT_PUBLIC_MAP_TILE_URL`.
- **ALT-003**: Client-side-only data fetching everywhere — partially rejected; detail and search pages MAY use server components for initial data to improve performance and SEO.
- **ALT-004**: Tailwind vs CSS Modules — either is acceptable; the plan uses theme tokens in `globals.css` and does not mandate a specific utility framework, leaving it to `apps/web` scaffold defaults.
- **ALT-005**: Integrating third-party analytics/monitoring providers — rejected for the local-first PoC to avoid external services and keep everything on your machine; console logging and an error boundary suffice.

## 4. Dependencies

- **DEP-001**: Completion of Phase 1 API ([feature-backend-data-1.md](feature-backend-data-1.md)) providing `GET /businesses/search` and `GET /businesses/{id}`.
- **DEP-002**: Completion of Phase 0 shared package `@is-it-local/shared` ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).
- **DEP-003**: Node.js 20+ and pnpm workspace configured at the repository root.
- **DEP-004**: npm packages: `next`, `react`, `react-dom`, `react-leaflet`, `leaflet`, `vitest`, `@testing-library/react`, `@playwright/test`.
- **DEP-005**: A Nominatim (OpenStreetMap) geocoding endpoint reachable from the app for free-text location resolution (public instance or self-hosted).
- **DEP-006**: _(none)_ No analytics or error-monitoring provider is used in the PoC.
- **DEP-007**: _(none)_ No hosting platform is required; the app runs locally via `pnpm dev`.

## 5. Files

- **FILE-001**: `apps/web/package.json` — web app scripts and dependencies.
- **FILE-002**: `apps/web/tsconfig.json` — TypeScript config with shared path alias.
- **FILE-003**: `apps/web/.env.example` — documented client environment variables.
- **FILE-004**: `apps/web/src/lib/config.ts` — environment configuration reader.
- **FILE-005**: `apps/web/src/lib/api-client.ts` — typed REST API client.
- **FILE-006**: `apps/web/src/lib/classification.ts` — classification color/label maps.
- **FILE-007**: `apps/web/src/lib/geocode.ts` — location geocoding utility.
- **FILE-008**: `apps/web/src/lib/logger.ts` — lightweight console logging and event tracking.
- **FILE-009**: _(removed)_ No third-party error-monitoring module; client errors are handled by the error boundary and console logger.
- **FILE-010**: `apps/web/src/components/ClassificationBadge.tsx` — classification badge component.
- **FILE-011**: `apps/web/src/components/ConfidenceMeter.tsx` — confidence display component.
- **FILE-012**: `apps/web/src/components/SearchForm.tsx` — search input form.
- **FILE-013**: `apps/web/src/components/BusinessCard.tsx` — result list item.
- **FILE-014**: `apps/web/src/components/BusinessMap.tsx` — map with marker.
- **FILE-015**: `apps/web/src/app/layout.tsx`, `globals.css` — base layout and theme.
- **FILE-016**: `apps/web/src/app/page.tsx` — home page.
- **FILE-017**: `apps/web/src/app/search/page.tsx` — search results page.
- **FILE-018**: `apps/web/src/app/business/[id]/page.tsx` — business detail page.
- **FILE-019**: `apps/web/src/app/not-found.tsx`, `error.tsx` — error/404 boundaries.
- **FILE-020**: `apps/web/tests/*` and `apps/web/e2e/*` — unit/integration and E2E tests.
- **FILE-021**: `apps/web/README.md` — web app documentation.

## 6. Testing

- **TEST-001**: `ClassificationBadge` renders the correct label and color for each of the six classification values.
- **TEST-002**: `ConfidenceMeter` renders a 0.0–1.0 value as the correct percentage and exposes an accessible label.
- **TEST-003**: `SearchForm` submission navigates to `/search` with correctly encoded `name`, `lat`, `lon`, and `radius_m` query params.
- **TEST-004**: The search page renders a `BusinessCard` per result from a mocked `searchBusinesses` response and shows an empty-state message when the result set is empty.
- **TEST-005**: The search page renders an error state when the API client rejects.
- **TEST-006**: The business detail page renders classification, confidence percentage, and each source as an external link with `rel="noopener noreferrer"`.
- **TEST-007**: Playwright E2E: from the home page, performing a search navigates to results and clicking a result opens the detail page.
- **TEST-008**: Layout has no horizontal overflow at 360px, 768px, and 1280px viewport widths.
- **TEST-009**: `tsc --noEmit`, `eslint`, and Prettier checks pass for `apps/web`.

## 7. Risks & Assumptions

- **RISK-001**: API contract drift between Phase 1 and the web client; mitigated by consuming shared types from `@is-it-local/shared` (REQ-003) and typed API client (PAT-001).
- **RISK-002**: Geocoding provider rate limits or inaccuracies may degrade location search; mitigated by browser geolocation fallback and graceful error handling (TASK-011).
- **RISK-003**: Map tile provider usage limits or licensing; mitigated by configurable tile URL (`NEXT_PUBLIC_MAP_TILE_URL`).
- **RISK-004**: Exposing secrets via `NEXT_PUBLIC_` variables; mitigated by SEC-001 restricting the prefix to client-safe values only.
- **ASSUMPTION-001**: The Phase 1 API is running locally and reachable at `NEXT_PUBLIC_API_BASE_URL`.
- **ASSUMPTION-002**: Search results include a distance value or the coordinates needed to compute one client-side.
- **ASSUMPTION-003**: A Nominatim geocoding endpoint is available for free-text location input.
- **ASSUMPTION-004**: The local environment has Node 20+ and pnpm to run the dev server.

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 2 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [infrastructure-foundations-1.md](infrastructure-foundations-1.md) — Phase 0 foundations (prerequisite).
- [feature-backend-data-1.md](feature-backend-data-1.md) — Phase 1 backend & data (prerequisite).
- [Next.js App Router documentation](https://nextjs.org/docs/app)
- [React Leaflet documentation](https://react-leaflet.js.org/)
- [Vitest documentation](https://vitest.dev/)
- [Playwright documentation](https://playwright.dev/)
