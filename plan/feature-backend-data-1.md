---
goal: Implement Phase 1 Backend & Data (API-first) for Is It Local — FastAPI service, PostgreSQL/PostGIS database, data ingestion, and LLM enrichment pipeline
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: "Planned"
tags: [feature, backend, data, infrastructure, api]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan operationalizes **Phase 1 — Backend & Data (API-first)** from [TODO.md](../TODO.md). It delivers a FastAPI backend, a PostgreSQL + PostGIS database with migrations, read/search/detail endpoints, data ingestion from OpenStreetMap and Overture (free/open data), and a local enrichment pipeline (self-hosted SearXNG + llama.cpp) that classifies business ownership with confidence scores and cited sources. Everything runs locally for the PoC — no paid API keys or hosted services are required. Completion of this plan produces a running, tested API that serves classified business data, enabling Phase 2 (Web App) development. This plan depends on the completion of Phase 0 ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).

## 1. Requirements & Constraints

- **REQ-001**: The backend API MUST be implemented with FastAPI in `apps/api` using Python 3.11+.
- **REQ-002**: The database MUST be PostgreSQL 16+ with the PostGIS extension enabled for geospatial queries.
- **REQ-003**: Database schema changes MUST be managed exclusively through Alembic migrations in `apps/api/alembic/`.
- **REQ-004**: The API MUST expose a search endpoint supporting query by `name` (partial match) and `location` (latitude, longitude, radius) using PostGIS `ST_DWithin`.
- **REQ-005**: The API MUST expose a business detail endpoint returning the business record, its ownership classification, `confidence` score, and `sources`.
- **REQ-006**: The ownership `classification` field MUST be constrained to exactly: `family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`.
- **REQ-007**: The enrichment pipeline MUST persist an `OwnershipClassification` record with a `confidence` value in the range 0.0–1.0 and at least one linked `Source` when confidence is greater than 0.0.
- **REQ-008**: Data ingestion MUST be idempotent; re-running a seed job MUST NOT create duplicate `Business` records for the same external provider identity.
- **REQ-009**: The API MUST auto-generate OpenAPI documentation served at `/docs` and `/openapi.json`.
- **SEC-001**: All service endpoints and connection strings (`DATABASE_URL`, `LLM_BASE_URL`, `LLM_MODEL`, `SEARXNG_BASE_URL`) MUST be read from environment variables and MUST NOT be hardcoded. The PoC requires no paid API keys.
- **SEC-002**: All API request inputs MUST be validated with Pydantic models; invalid input MUST return HTTP 422.
- **SEC-003**: Database access MUST use parameterized queries via SQLAlchemy ORM to prevent SQL injection.
- **SEC-004**: The enrichment pipeline MUST enforce a per-service rate limit and response caching to avoid overloading the local llama.cpp and SearXNG instances (there is no external spend to guard in the PoC).
- **CON-001**: This plan MUST NOT implement authentication, community submissions, web UI, or mobile UI (those are Phase 2+).
- **CON-002**: The public API contract MUST default to REST (per README); GraphQL is out of scope for this plan.
- **CON-003**: All services (database, API, SearXNG, llama.cpp) MUST run locally for the PoC; no paid third-party APIs or hosted services may be required.
- **GUD-001**: All Python code MUST pass `ruff check` and `ruff format --check`.
- **GUD-002**: Business and enrichment logic MUST be organized into layers: `routers/` (HTTP), `services/` (logic), `repositories/` (data access), `models/` (ORM), `schemas/` (Pydantic).
- **PAT-001**: Persisted entity structures MUST conform to the canonical JSON Schemas defined in `packages/shared/schema/` from Phase 0.
- **PAT-002**: External provider integrations MUST implement a shared `PlaceProvider` interface to allow adding providers without changing ingestion orchestration.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Stand up the FastAPI application, PostgreSQL/PostGIS database, ORM models, migrations, and read/search/detail endpoints with tests.

| Task     | Description                                                                                                                                                                                                                                                                                   | Completed | Date |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Create `apps/api/pyproject.toml` declaring dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2`, `geoalchemy2`, `alembic`, `psycopg[binary]`, `pydantic>=2`, `pydantic-settings`, `httpx`, `pytest`, `pytest-asyncio`.                                                               |           |      |
| TASK-002 | Create `apps/api/app/config.py` defining a `Settings` class (pydantic-settings) reading `DATABASE_URL`, `LLM_BASE_URL`, `LLM_MODEL`, `SEARXNG_BASE_URL`, `PROVIDER_RATE_LIMIT_PER_MIN`.                                                                                                       |           |      |
| TASK-003 | Create `apps/api/app/db.py` configuring the SQLAlchemy engine, `SessionLocal`, and a `get_db` FastAPI dependency.                                                                                                                                                                             |           |      |
| TASK-004 | Create ORM models in `apps/api/app/models/`: `business.py` (`Business`), `classification.py` (`OwnershipClassification`), `source.py` (`Source`), `community_submission.py` (`CommunitySubmission`), matching Phase 0 schemas; `Business.location` uses `geoalchemy2.Geography(POINT, 4326)`. |           |      |
| TASK-005 | Create Pydantic schemas in `apps/api/app/schemas/` mirroring the ORM models for request/response serialization, including a `ClassificationEnum` with the six required values.                                                                                                                |           |      |
| TASK-006 | Initialize Alembic in `apps/api/alembic/`; create migration `0001_enable_postgis` executing `CREATE EXTENSION IF NOT EXISTS postgis`.                                                                                                                                                         |           |      |
| TASK-007 | Create Alembic migration `0002_create_core_tables` creating tables `businesses`, `ownership_classifications`, `sources`, `community_submissions` with a GIST index on `businesses.location` and a unique constraint on `(provider, provider_place_id)` in `businesses`.                       |           |      |
| TASK-008 | Create `apps/api/app/repositories/business_repository.py` with functions `get_by_id`, `search(name, lat, lon, radius_m)` using `ST_DWithin`, and `upsert_by_provider_identity`.                                                                                                               |           |      |
| TASK-009 | Create `apps/api/app/routers/businesses.py` exposing `GET /businesses/{id}` (detail with classification + sources) and `GET /businesses/search` (query params `name`, `lat`, `lon`, `radius_m`).                                                                                              |           |      |
| TASK-010 | Create `apps/api/app/main.py` instantiating the FastAPI app, including the businesses router, enabling OpenAPI at `/docs` and `/openapi.json`, and a `GET /health` endpoint.                                                                                                                  |           |      |
| TASK-011 | Create `infra/docker-compose.yml` defining services `db` (image `postgis/postgis:16-3.4`, healthcheck), `api` (builds `apps/api`, depends_on `db`), and `searxng` (image `searxng/searxng`, JSON output format enabled) with named volume `pgdata`.                                           |           |      |
| TASK-012 | Create `apps/api/Dockerfile` (python:3.11-slim base) installing dependencies and running `uvicorn app.main:app`.                                                                                                                                                                              |           |      |
| TASK-013 | Create tests in `apps/api/tests/`: `test_health.py`, `test_business_detail.py`, `test_business_search.py` using `pytest` + `httpx` against a test database.                                                                                                                                   |           |      |

### Implementation Phase 2

- GOAL-002: Implement idempotent data ingestion from OpenStreetMap and Overture with de-duplication and a repeatable seed job.

| Task     | Description                                                                                                                                                                                                               | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-014 | Create `apps/api/app/providers/base.py` defining the `PlaceProvider` abstract interface with method `fetch_places(bbox: BoundingBox) -> list[NormalizedPlace]`.                                                           |           |      |
| TASK-015 | Create `apps/api/app/providers/openstreetmap.py` implementing `PlaceProvider` against the OpenStreetMap Overpass API, mapping elements to `NormalizedPlace` (name, address, lat, lon, categories, provider_place_id).     |           |      |
| TASK-016 | Create `apps/api/app/providers/overture.py` implementing `PlaceProvider` reading OpenStreetMap/Overture place data and mapping to `NormalizedPlace`.                                                                      |           |      |
| TASK-017 | Create `apps/api/app/services/ingestion_service.py` orchestrating provider fetches and calling `business_repository.upsert_by_provider_identity` for idempotent writes.                                                   |           |      |
| TASK-018 | Implement de-duplication in `apps/api/app/services/dedup_service.py` matching records across providers by normalized name + geospatial proximity (`ST_DWithin` within 50 meters) and merging into a canonical `Business`. |           |      |
| TASK-019 | Create CLI seed script `apps/api/app/cli/seed.py` (invocable via `python -m app.cli.seed --provider <name> --bbox <coords>`) that runs ingestion and de-duplication.                                                      |           |      |
| TASK-020 | Create `docs/data-sources-compliance.md` documenting OpenStreetMap (ODbL) and Overture license and terms-of-use compliance for ingestion and redistribution.                                                              |           |      |
| TASK-021 | Create tests `apps/api/tests/test_ingestion_idempotent.py` (asserts re-running seed does not duplicate records) and `apps/api/tests/test_dedup.py`.                                                                       |           |      |

### Implementation Phase 3

- GOAL-003: Implement the LLM + web-search enrichment pipeline that classifies ownership, produces confidence scores and cited sources, and persists results with cost/rate guardrails.

| Task     | Description                                                                                                                                                                                                                                                                                                  | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---- |
| TASK-022 | Create `packages/enrichment/pyproject.toml` declaring dependencies: `httpx`, `pydantic>=2`, `tenacity`, `openai` (used against the local llama.cpp OpenAI-compatible endpoint), and a shared DB access layer or client to the API.                                                                           |           |      |
| TASK-023 | Create `packages/enrichment/enrichment/search_client.py` implementing ownership-signal retrieval via the self-hosted SearXNG JSON API (`SEARXNG_BASE_URL`), returning candidate `Source` objects (url, snippet, retrieved_at).                                                                               |           |      |
| TASK-024 | Create `packages/enrichment/enrichment/llm_classifier.py` implementing a function `classify(business, sources) -> ClassificationResult` that calls the local llama.cpp server (`LLM_BASE_URL`, `LLM_MODEL`) and returns `{classification, confidence, cited_source_ids}` constrained to the six enum values. |           |      |
| TASK-025 | Create `packages/enrichment/enrichment/guardrails.py` implementing a token-bucket rate limiter (`PROVIDER_RATE_LIMIT_PER_MIN`) for the local services, retries via `tenacity`, and an on-disk/DB response cache.                                                                                             |           |      |
| TASK-026 | Create `packages/enrichment/enrichment/pipeline.py` orchestrating: fetch business → search sources → classify → persist `Source` rows and one `OwnershipClassification` row (with confidence + linked sources).                                                                                              |           |      |
| TASK-027 | Create CLI `packages/enrichment/enrichment/cli.py` (`python -m enrichment.cli --limit N`) enriching businesses lacking a classification.                                                                                                                                                                     |           |      |
| TASK-028 | Create an evaluation harness `packages/enrichment/eval/` with a labeled fixture set `eval/fixtures.jsonl` and `eval/run_eval.py` computing accuracy/precision/recall against known classifications.                                                                                                          |           |      |
| TASK-029 | Create tests `packages/enrichment/tests/test_classifier.py`, `test_guardrails.py`, and `test_pipeline.py` using mocked LLM/search clients.                                                                                                                                                                   |           |      |

## 3. Alternatives

- **ALT-001**: GraphQL public API instead of REST — deferred; README specifies REST as the default and the open question remains unresolved in TODO.md.
- **ALT-002**: MongoDB/document store instead of PostgreSQL — rejected; PostGIS geospatial querying and relational integrity for classifications/sources are core requirements.
- **ALT-006**: Hosted LLM/search APIs (e.g. OpenAI, paid search) instead of local llama.cpp + SearXNG — rejected for the PoC to keep cost at zero and everything local; can be revisited when scaling beyond a single machine.
- **ALT-003**: Django + GeoDjango instead of FastAPI — rejected; FastAPI is specified in the README and offers lighter async APIs and automatic OpenAPI generation.
- **ALT-004**: Real-time synchronous enrichment on each API request — rejected; enrichment is expensive and rate-limited, so it runs as an offline/batch pipeline persisting results.
- **ALT-005**: Direct DB writes from the enrichment package versus calling the API — DB writes chosen for batch efficiency; interface kept behind a client module (TASK-022) to allow switching later.

## 4. Dependencies

- **DEP-001**: Completion of Phase 0 foundations, including canonical schemas in `packages/shared/schema/` ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).
- **DEP-002**: PostgreSQL 16 with PostGIS 3.4 (via `postgis/postgis:16-3.4` Docker image).
- **DEP-003**: Python packages: `fastapi`, `uvicorn`, `sqlalchemy>=2`, `geoalchemy2`, `alembic`, `psycopg`, `pydantic>=2`, `pydantic-settings`, `httpx`, `tenacity`, `pytest`, `pytest-asyncio`.
- **DEP-004**: Network access to the OpenStreetMap Overpass API and Overture data distribution (no API key required).
- **DEP-005**: A local llama.cpp server exposing an OpenAI-compatible endpoint at `LLM_BASE_URL` with an open-weight model.
- **DEP-006**: A self-hosted SearXNG instance reachable at `SEARXNG_BASE_URL` (run via Docker Compose).
- **DEP-007**: Docker and Docker Compose for local database and API orchestration.

## 5. Files

- **FILE-001**: `apps/api/pyproject.toml` — API package definition and dependencies.
- **FILE-002**: `apps/api/app/config.py` — environment-driven settings.
- **FILE-003**: `apps/api/app/db.py` — SQLAlchemy engine, session, `get_db` dependency.
- **FILE-004**: `apps/api/app/models/*.py` — ORM models for Business, OwnershipClassification, Source, CommunitySubmission.
- **FILE-005**: `apps/api/app/schemas/*.py` — Pydantic request/response schemas and `ClassificationEnum`.
- **FILE-006**: `apps/api/alembic/` and versions `0001_enable_postgis`, `0002_create_core_tables` — migrations.
- **FILE-007**: `apps/api/app/repositories/business_repository.py` — data access including geospatial search and upsert.
- **FILE-008**: `apps/api/app/routers/businesses.py` — detail and search endpoints.
- **FILE-009**: `apps/api/app/main.py` — FastAPI app, router registration, health, OpenAPI.
- **FILE-010**: `infra/docker-compose.yml` — `db` and `api` services.
- **FILE-011**: `apps/api/Dockerfile` — API container image.
- **FILE-012**: `apps/api/app/providers/base.py`, `openstreetmap.py`, `overture.py` — provider integrations.
- **FILE-013**: `apps/api/app/services/ingestion_service.py`, `dedup_service.py` — ingestion and de-duplication logic.
- **FILE-014**: `apps/api/app/cli/seed.py` — repeatable seed CLI.
- **FILE-015**: `packages/enrichment/enrichment/search_client.py`, `llm_classifier.py`, `guardrails.py`, `pipeline.py`, `cli.py` — enrichment pipeline modules.
- **FILE-016**: `packages/enrichment/eval/fixtures.jsonl`, `eval/run_eval.py` — enrichment evaluation harness.
- **FILE-017**: `apps/api/tests/*.py` and `packages/enrichment/tests/*.py` — automated tests.
- **FILE-018**: `docs/data-sources-compliance.md` — provider license/terms documentation.

## 6. Testing

- **TEST-001**: `GET /health` returns HTTP 200 with body `{"status": "ok"}`.
- **TEST-002**: `GET /businesses/{id}` returns the business plus its classification, `confidence`, and `sources`; returns HTTP 404 for unknown id.
- **TEST-003**: `GET /businesses/search?name=...&lat=...&lon=...&radius_m=...` returns only businesses within the radius, validated against known PostGIS fixtures.
- **TEST-004**: Search endpoint returns HTTP 422 when required numeric params are non-numeric (input validation).
- **TEST-005**: Running the seed job twice for the same provider bbox results in the same number of `Business` rows (idempotency).
- **TEST-006**: De-duplication merges two provider records within 50 meters with matching normalized names into one canonical `Business`.
- **TEST-007**: `llm_classifier.classify` (mocked LLM) returns a `classification` within the six enum values and a `confidence` in 0.0–1.0.
- **TEST-008**: Enrichment persists at least one `Source` when `confidence > 0.0` (REQ-007) verified against the database.
- **TEST-009**: Guardrails enforce the per-minute rate limit and serve cached responses on repeated identical requests.
- **TEST-010**: `eval/run_eval.py` produces accuracy/precision/recall metrics against `eval/fixtures.jsonl` and exits non-zero if accuracy is below a configured threshold.
- **TEST-011**: All Python files pass `ruff check` and `ruff format --check` in CI.

## 7. Risks & Assumptions

- **RISK-001**: LLM classification may be inaccurate or hallucinate sources; mitigated by requiring cited sources (REQ-007), confidence scoring, and the evaluation harness (TASK-028).
- **RISK-002**: Provider API rate limits or terms may restrict bulk ingestion; mitigated by rate limiting (SEC-004) and compliance documentation (TASK-020).
- **RISK-003**: Heavy local LLM/search usage could exhaust machine resources; mitigated by the rate limiter and response cache in `guardrails.py` (TASK-025).
- **RISK-004**: Cross-provider de-duplication may produce false merges; mitigated by combining name normalization with a strict 50-meter proximity threshold and tests (TASK-021).
- **RISK-005**: PostGIS geospatial queries may be slow without proper indexing; mitigated by the GIST index on `businesses.location` (TASK-007).
- **ASSUMPTION-001**: Phase 0 canonical schemas exist and are stable.
- **ASSUMPTION-002**: The REST-vs-GraphQL open question resolves to REST for this phase.
- **ASSUMPTION-003**: The local llama.cpp server and SearXNG instance expose HTTP APIs usable via `httpx`/`openai`.
- **ASSUMPTION-004**: OpenStreetMap (ODbL) and Overture licenses permit ingestion and redistribution of derived classification data (to be confirmed in TASK-020).

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 1 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [infrastructure-foundations-1.md](infrastructure-foundations-1.md) — Phase 0 foundations (prerequisite).
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [PostGIS documentation](https://postgis.net/documentation/)
- [GeoAlchemy2 documentation](https://geoalchemy-2.readthedocs.io/)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [Overture Maps documentation](https://docs.overturemaps.org/)
- [OpenStreetMap Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [SearXNG documentation](https://docs.searxng.org/)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
