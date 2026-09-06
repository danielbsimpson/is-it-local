# Is It Local — TODO

A phased roadmap from an empty repository to a community-driven, photo-enabled app. Check items off as they're completed. Phases are ordered, but items within a phase can often run in parallel.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

Each phase has a detailed, machine-readable implementation plan in the [plan/](plan/) directory, linked from its heading below.

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
- [ ] Scaffold FastAPI app in `apps/api`.
- [ ] Set up PostgreSQL + PostGIS via Docker Compose.
- [ ] Add database migrations (Alembic).
- [ ] Implement business CRUD/read endpoints.
- [ ] Implement search endpoint (by name + location, geospatial "near me").
- [ ] Implement business detail endpoint (classification, confidence, sources).
- [ ] Auto-generate OpenAPI docs.
- [ ] Add API tests.

### Data ingestion (seeding)
- [ ] Integrate **Foursquare Places** to seed businesses.
- [ ] Integrate **OpenStreetMap / Overture** to broaden coverage.
- [ ] Build a de-duplication/merge strategy for overlapping records.
- [ ] Create a repeatable seed script/job.
- [ ] Document each provider's license/terms compliance.

### Enrichment pipeline (LLM + web search)
- [ ] Build enrichment worker in `packages/enrichment`.
- [ ] Implement web-search retrieval for ownership signals.
- [ ] Implement LLM classification producing category + confidence + cited sources.
- [ ] Persist enrichment results and sources to the database.
- [ ] Add guardrails: rate limiting, cost controls, retries, caching.
- [ ] Add evaluation set to measure classification accuracy.

---

## Phase 2 — Web App (Next.js)

> Implementation plan: [plan/feature-web-app-1.md](plan/feature-web-app-1.md)

- [ ] Scaffold Next.js app in `apps/web` (TypeScript).
- [ ] Build search UI (name + location).
- [ ] Build results list with classification badges.
- [ ] Build business detail page (classification, confidence, sources, map).
- [ ] Add responsive/mobile-friendly layout.
- [ ] Add basic analytics and error monitoring.
- [ ] Deploy a public web preview.

---

## Phase 3 — Mobile App (React Native / Expo)

> Implementation plan: [plan/feature-mobile-app-1.md](plan/feature-mobile-app-1.md)

- [ ] Scaffold Expo app in `apps/mobile` (TypeScript).
- [ ] Implement search and business detail screens.
- [ ] Add map + "near me" view using device location.
- [ ] Share types/classification schema via `packages/shared`.
- [ ] Set up iOS and Android builds.
- [ ] Prepare store listings (screenshots, descriptions, privacy).

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

## Phase 5 — Photo Lookup

> Implementation plan: [plan/feature-photo-lookup-1.md](plan/feature-photo-lookup-1.md)

- [ ] Add image upload/capture in mobile (and web).
- [ ] Implement storefront/logo matching to existing businesses.
- [ ] Integrate OCR and/or visual search for sign/logo recognition.
- [ ] Fall back to location + text search when image match is uncertain.
- [ ] Evaluate accuracy and iterate.

---

## Cross-Cutting (ongoing)
- [ ] Security: secrets management, input validation, rate limiting, dependency scanning.
- [ ] Privacy: clear data-use policy; respect provider terms; handle user data responsibly.
- [ ] Observability: logging, metrics, error tracking across services.
- [ ] Cost monitoring for LLM/search/API usage.
- [ ] Accessibility (a11y) on web and mobile.
- [ ] Documentation kept current in `docs/`.

---

## Open Questions / Decisions to Revisit
- [ ] REST vs GraphQL for the public API.
- [ ] Which LLM + web-search providers to standardize on.
- [ ] Data licensing constraints for redistributing enriched data.
- [ ] Moderation policy and thresholds for community-driven classifications.
- [ ] Definition boundaries between "locally owned" and "independent."
