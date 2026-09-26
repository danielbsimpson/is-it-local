# Is It Local — TODO

A phased roadmap from an empty repository to a community-driven, photo-enabled app. Check items off as they're completed. Phases are ordered, but items within a phase can often run in parallel.

> **Local-first PoC:** The current goal is to run everything on one machine at zero cost — a local LLM via **llama.cpp**, a self-hosted **SearXNG** search, a local **PostgreSQL + PostGIS** database, free/open data from **OpenStreetMap + Overture**, and the **web app served locally**. The PoC scope is **Phases 0–2**. Mobile (Phase 3), community (Phase 4), and photo lookup (Phase 5) come after the concept is validated, and use local/open-source tools where possible.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

Each phase has a detailed, machine-readable implementation plan in the [plan/](plan/) directory, linked from its heading below.

> **Runtime validation (2026-09-26):** Phases 0–2 were exercised end-to-end on a local machine — Postgres/PostGIS + SearXNG via Docker Compose, Alembic migrations, seeding ~350 businesses from OpenStreetMap, the enrichment DB round-trip against live SearXNG, all FastAPI endpoints (`/health`, `/businesses/search`, `/businesses/{id}`), and the Next.js home/search/detail pages with passing Playwright smoke tests. Two bugs were found and fixed in the process:
>
> - **Overpass `406`** — the OSM provider now sends an explicit `User-Agent` (public Overpass rejects the default httpx one). Note: `overpass-api.de` is often overloaded (`504`); use a mirror such as `https://overpass.kumi.systems/api/interpreter`.
> - **Address schema mismatch** — the OSM and Overture providers emitted `state`/`postcode`/`house_number`, which the `Address` schema (`extra="forbid"`) rejected, causing `500`s on any business with an address. Both providers now emit the canonical `street`/`city`/`region`/`postal_code`/`country` keys, covered by a new regression test.
>
> Still requires manual setup: a running **llama.cpp** server for real LLM classification (enrichment was validated with a stub classifier over live search results).

---

## Phase 0 — Foundations

> Implementation plan: [plan/infrastructure-foundations-1.md](plan/infrastructure-foundations-1.md)

### Repository & tooling

- [x] Initialize monorepo structure (`apps/`, `packages/`, `infra/`, `docs/`).
- [x] Add root tooling: package manager (pnpm), linting, formatting (Prettier/Ruff), pre-commit hooks.
- [x] Add `LICENSE` (MIT).
- [x] Add `.env.example` documenting all required environment variables.
- [x] Set up CI (lint, test, build) via GitHub Actions.
- [x] Add `CONTRIBUTING.md` and issue/PR templates.

### Data model & classification

- [x] Define the core **Business** entity (id, name, address, geolocation, categories, contact, brand/parent).
- [x] Define the **Ownership Classification** schema: `family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`.
- [x] Add fields for **confidence score** and **source citations** on every classification.
- [x] Define a **Source** entity (provider, URL, retrieved date, snippet).
- [x] Define a **Community Submission** entity (proposed classification, evidence, submitter, status).
- [x] Document the data model in `docs/`.

---

## Phase 1 — Backend & Data (API-first)

> Implementation plan: [plan/feature-backend-data-1.md](plan/feature-backend-data-1.md)

### Backend API (FastAPI)

- [x] Scaffold FastAPI app in `apps/api`.
- [x] Set up PostgreSQL + PostGIS via Docker Compose.
- [x] Add database migrations (Alembic).
- [x] Implement business CRUD/read endpoints.
- [x] Implement search endpoint (by name + location, geospatial "near me").
- [x] Implement business detail endpoint (classification, confidence, sources).
- [x] Auto-generate OpenAPI docs.
- [x] Add API tests.

### Data ingestion (seeding)

- [x] Integrate **OpenStreetMap** (Overpass / extracts) to seed businesses — free and open, no API key.
- [x] Integrate **Overture Maps** to broaden coverage.
- [x] Build a de-duplication/merge strategy for overlapping records.
- [x] Create a repeatable seed script/job.
- [x] Document each provider's license/terms compliance.

### Enrichment pipeline (local LLM + self-hosted search)

- [x] Build enrichment worker in `packages/enrichment`.
- [x] Stand up a self-hosted **SearXNG** instance (Docker) for ownership-signal retrieval.
- [x] Implement search retrieval against the local SearXNG instance.
- [x] Run a local **llama.cpp** OpenAI-compatible server and implement LLM classification producing category + confidence + cited sources.
- [x] Persist enrichment results and sources to the database.
- [x] Add guardrails: rate limiting, retries, caching (no external spend to control in the PoC).
- [x] Add evaluation set to measure classification accuracy.

---

## Phase 2 — Web App (Next.js)

> Implementation plan: [plan/feature-web-app-1.md](plan/feature-web-app-1.md)

- [x] Scaffold Next.js app in `apps/web` (TypeScript).
- [x] Build search UI (name + location).
- [x] Build results list with classification badges.
- [x] Build business detail page (classification, confidence, sources, map).
- [x] Add responsive/mobile-friendly layout.
- [x] Use free/open map tiles (OpenStreetMap) and local geocoding (Nominatim).
- [x] Run the web app locally (`pnpm dev`); no hosted deployment for the PoC.

---

## Phase 3 — Mobile App (React Native / Expo) — _deferred (post-PoC)_

> Implementation plan: [plan/feature-mobile-app-1.md](plan/feature-mobile-app-1.md)

- [ ] Scaffold Expo app in `apps/mobile` (TypeScript).
- [ ] Implement search and business detail screens.
- [ ] Add map + "near me" view using device location.
- [ ] Share types/classification schema via `packages/shared`.
- [ ] Run locally via Expo Go / local dev build (defer EAS cloud builds and store listings).

---

## Phase 4 — Community & Network Effect

> Implementation plan: [plan/feature-community-1.md](plan/feature-community-1.md)

- [ ] Add user accounts / lightweight auth.
- [ ] Implement community submissions and corrections.
- [ ] Add moderation/review workflow for submissions.
- [ ] Add contributor reputation/weighting to prioritize trusted input.
- [ ] Surface "community verified" vs "auto-classified" states in the UI.
- [ ] Add reporting for incorrect or abusive submissions.

---

## Phase 5 — Photo Lookup — _deferred (post-PoC)_

> Implementation plan: [plan/feature-photo-lookup-1.md](plan/feature-photo-lookup-1.md)

- [ ] Add image upload/capture in web (and later mobile).
- [ ] Implement storefront/logo matching to existing businesses.
- [ ] Integrate local OCR (**Tesseract**) and open-source image embeddings (**CLIP**) with **pgvector** for visual search.
- [ ] Fall back to location + text search when image match is uncertain.
- [ ] Evaluate accuracy and iterate.

---

## Cross-Cutting (ongoing)

- [ ] Security: secrets management, input validation, rate limiting, dependency scanning.
- [ ] Privacy: clear data-use policy; respect provider terms; handle user data responsibly.
- [ ] Observability: local logging and metrics across services.
- [ ] Resource monitoring for local LLM/search (latency, memory) rather than cloud cost.
- [ ] Accessibility (a11y) on web.
- [ ] Documentation kept current in `docs/`.

---

## Open Questions / Decisions to Revisit

- [ ] REST vs GraphQL for the public API.
- [ ] Which open-weight model to standardize on for llama.cpp.
- [ ] Data licensing constraints for redistributing enriched data.
- [ ] Moderation policy and thresholds for community-driven classifications.
- [ ] Definition boundaries between "locally owned" and "independent."
