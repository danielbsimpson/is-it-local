---
goal: Implement Phase 5 Photo Lookup for Is It Local — image upload/capture, storefront/logo matching, OCR/visual search recognition, and graceful fallback to location/text search
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: 'Deferred (post-PoC)'
tags: [feature, computer-vision, ocr, mobile, web, backend]
---

# Introduction

![Status: Deferred (post-PoC)](https://img.shields.io/badge/status-Deferred-lightgrey)

> **Deferred until after the local-first PoC.** When built, photo lookup uses local tools only — **Tesseract OCR** and an **open-source CLIP** embedding model with **pgvector** — so the entire pipeline runs on your machine with no third-party vision APIs.

This implementation plan operationalizes **Phase 5 — Photo Lookup** from [TODO.md](../TODO.md). It enables users to upload or capture a storefront/logo image and receive a matched business with its ownership classification. It adds a backend image-matching service combining OCR text extraction and visual embedding similarity search, mobile and web capture/upload flows, a graceful fallback to location + text search when a confident match is not found, and an accuracy evaluation harness. This plan extends the Phase 1 backend ([feature-backend-data-1.md](feature-backend-data-1.md)), the Phase 2 web app ([feature-web-app-1.md](feature-web-app-1.md)), and the Phase 3 mobile app ([feature-mobile-app-1.md](feature-mobile-app-1.md)), reusing the `Business` schema from Phase 0 ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).

## 1. Requirements & Constraints

- **REQ-001**: The backend MUST expose `POST /lookup/photo` accepting a multipart image upload and returning ranked candidate businesses with a per-candidate `match_confidence` in the range 0.0–1.0.
- **REQ-002**: The photo-lookup pipeline MUST extract text from the image via OCR and MUST compute a visual embedding for similarity search.
- **REQ-003**: Candidate ranking MUST combine OCR-derived name/text matching against the `businesses` table with visual embedding similarity, producing a single normalized `match_confidence` per candidate.
- **REQ-004**: When the top candidate `match_confidence` is greater than or equal to `PHOTO_MATCH_CONFIDENCE_THRESHOLD`, the API MUST return that candidate as `matched = true`; otherwise it MUST return `matched = false` with fallback suggestions.
- **REQ-005**: When `matched = false`, clients MUST fall back to the existing location + text search flow using any OCR-extracted text and available device location.
- **REQ-006**: Visual embeddings for businesses MUST be stored in a vector index supporting nearest-neighbor search (`pgvector` extension on the existing PostgreSQL database).
- **REQ-007**: The mobile app MUST support capturing a photo with the camera and selecting an image from the library; the web app MUST support file upload and (where available) camera capture.
- **REQ-008**: The system MUST provide an evaluation harness measuring top-1 and top-5 match accuracy against a labeled image fixture set.
- **SEC-001**: Uploaded images MUST be validated for MIME type (`image/jpeg`, `image/png`, `image/webp`) and MUST enforce a maximum size (`PHOTO_MAX_UPLOAD_BYTES`); invalid uploads MUST return HTTP 422.
- **SEC-002**: Uploaded images MUST NOT be executed or stored in a web-served static path; processing MUST occur in an isolated code path and temporary files MUST be deleted after processing.
- **SEC-003**: EXIF metadata (including GPS) MUST be stripped from uploaded images before any persistence or logging unless the user explicitly consents to using location from the photo.
- **SEC-004**: The photo-lookup endpoint MUST enforce per-user/per-IP rate limiting to prevent abuse and cost overrun.
- **SEC-005**: OCR and embedding inference MUST run locally (Tesseract + open-source CLIP); the PoC MUST NOT require any third-party vision/OCR API keys.
- **CON-001**: This plan MUST NOT alter the ownership classification methodology; it only maps an image to an existing `Business` whose classification is served by Phase 1.
- **CON-002**: Image processing MUST NOT block the API event loop; heavy inference MUST run in a worker/threadpool or dedicated service.
- **GUD-001**: Backend code MUST follow the Phase 1 layering (`routers/`, `services/`, `repositories/`, `models/`, `schemas/`) and pass `ruff` checks.
- **GUD-002**: Client code MUST pass `tsc --noEmit`, ESLint, and Prettier checks.
- **PAT-001**: OCR and embedding providers MUST be abstracted behind interfaces (`OcrProvider`, `EmbeddingProvider`) to allow swapping implementations without changing the pipeline.
- **PAT-002**: The combined ranking function MUST be a single pure function `rank_candidates(ocr_text, embedding, candidates)` for deterministic testing.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Add vector storage, OCR/embedding provider abstractions, and business embedding backfill in the backend.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create Alembic migration `0005_enable_pgvector_and_embeddings` executing `CREATE EXTENSION IF NOT EXISTS vector` and adding a `logo_embedding vector(512)` column plus an IVFFlat/HNSW index to a new `business_images` table. | | |
| TASK-002 | Create ORM model `apps/api/app/models/business_image.py` (`BusinessImage`) with fields `id`, `business_id`, `image_url` (nullable), `logo_embedding`, `source` (enum: `provider`, `community`), `created_at`. | | |
| TASK-003 | Add `PHOTO_MATCH_CONFIDENCE_THRESHOLD`, `PHOTO_MAX_UPLOAD_BYTES`, `PHOTO_LOOKUP_RATE_LIMIT_PER_MIN`, `OCR_ENGINE` (default `tesseract`), and `EMBEDDING_MODEL` (default an open-source CLIP model) to `apps/api/app/config.py` `Settings` — all run locally, no API keys. | | |
| TASK-004 | Create `apps/api/app/vision/base.py` defining `OcrProvider.extract_text(image_bytes) -> list[TextSpan]` and `EmbeddingProvider.embed(image_bytes) -> list[float]` abstract interfaces. | | |
| TASK-005 | Create `apps/api/app/vision/ocr_provider.py` (local Tesseract via `pytesseract`) and `apps/api/app/vision/embedding_provider.py` (open-source CLIP via `open_clip`/`torch`) implementing the interfaces — models run locally, no API keys. | | |
| TASK-006 | Create `apps/api/app/vision/image_utils.py` implementing MIME/size validation and EXIF stripping (`strip_exif(image_bytes)`). | | |
| TASK-007 | Create a backfill CLI `apps/api/app/cli/backfill_embeddings.py` (`python -m app.cli.backfill_embeddings`) that computes and stores `logo_embedding` for businesses with available images. | | |
| TASK-008 | Create tests `apps/api/tests/test_image_utils.py` (validation + EXIF stripping) and `apps/api/tests/test_vision_providers.py` (mocked providers). | | |

### Implementation Phase 2

- GOAL-002: Implement the photo-lookup matching pipeline, ranking, endpoint, and fallback contract.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-009 | Create `apps/api/app/repositories/image_repository.py` with `nearest_by_embedding(embedding, k)` using pgvector similarity and `search_by_text(tokens)` reusing the businesses name index. | | |
| TASK-010 | Create `apps/api/app/services/photo_lookup_service.py` implementing `lookup(image_bytes) -> LookupResult`: validate → strip EXIF → OCR → embed → fetch candidates (text + vector) → `rank_candidates` → apply `PHOTO_MATCH_CONFIDENCE_THRESHOLD`. | | |
| TASK-011 | Implement the pure ranking function `rank_candidates(ocr_text, embedding, candidates)` in `apps/api/app/services/ranking.py` combining normalized text similarity and vector similarity into a single `match_confidence`. | | |
| TASK-012 | Create Pydantic schemas in `apps/api/app/schemas/lookup.py` (`PhotoLookupResponse` with `matched: bool`, `candidates: list[CandidateMatch]`, `ocr_text: str`). | | |
| TASK-013 | Create `apps/api/app/routers/lookup.py` exposing `POST /lookup/photo` (multipart) running the service in a threadpool/worker, rate-limited per SEC-004, returning `PhotoLookupResponse`. | | |
| TASK-014 | Ensure temporary files/buffers are deleted after processing and no image is written to a web-served static path (SEC-002). | | |
| TASK-015 | Create tests `apps/api/tests/test_ranking.py` (deterministic ranking), `test_photo_lookup.py` (matched + unmatched paths, mocked providers), and `test_lookup_validation.py` (invalid MIME/size → 422). | | |

### Implementation Phase 3

- GOAL-003: Implement client capture/upload flows, result handling with fallback, and an accuracy evaluation harness.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-016 | Extend `apps/mobile/src/lib/api-client.ts` and `apps/web/src/lib/api-client.ts` with `photoLookup(imageFile) -> PhotoLookupResponse` sending multipart form data. | | |
| TASK-017 | Create mobile capture flow `apps/mobile/src/app/scan.tsx` using `expo-camera`/`expo-image-picker` to capture or select an image, call `photoLookup`, and navigate to the matched business detail on `matched = true`. | | |
| TASK-018 | Create web upload flow `apps/web/src/app/scan/page.tsx` with a file input and (where supported) `getUserMedia` camera capture, calling `photoLookup`. | | |
| TASK-019 | Implement fallback UI in both clients: when `matched = false`, pre-fill the existing search with `ocr_text` and device location and navigate to the search results (REQ-005). | | |
| TASK-020 | Create shared result types for `PhotoLookupResponse` and `CandidateMatch` in `packages/shared/src/types.ts`. | | |
| TASK-021 | Add client tests: `apps/web/tests/scan.test.tsx` and `apps/mobile/__tests__/scan.test.tsx` covering matched-navigation and unmatched-fallback (mocked API client). | | |
| TASK-022 | Create an evaluation harness `packages/enrichment/eval/photo/` (or `apps/api/eval/photo/`) with a labeled fixture set `fixtures/` (image → expected business id) and `run_photo_eval.py` computing top-1 and top-5 accuracy. | | |
| TASK-023 | Create `docs/photo-lookup.md` documenting the pipeline, thresholds, privacy handling (EXIF stripping/consent), and evaluation results. | | |

## 3. Alternatives

- **ALT-001**: A dedicated external image-recognition SaaS for end-to-end storefront identification — rejected for the local-first PoC; a local Tesseract + open-source CLIP approach keeps everything on-machine at zero cost and reuses the existing database via pgvector.
- **ALT-002**: A separate vector database (e.g., Milvus, Pinecone) instead of pgvector — rejected for this phase to avoid new infrastructure; pgvector reuses the existing PostgreSQL instance. Can be revisited at scale.
- **ALT-003**: OCR-only matching without visual embeddings — rejected; many storefronts have stylized logos with little machine-readable text, so visual similarity materially improves recall.
- **ALT-004**: On-device inference in the mobile app — deferred; server-side inference centralizes model updates and keeps the app lightweight, at the cost of requiring connectivity.
- **ALT-005**: Storing raw uploaded images long-term for retraining — rejected by default for privacy (SEC-002/SEC-003); only derived embeddings are retained unless the user consents.

## 4. Dependencies

- **DEP-001**: Completion of Phase 1 backend ([feature-backend-data-1.md](feature-backend-data-1.md)) including the businesses table and search index.
- **DEP-002**: Completion of Phase 0 `Business` schema and shared package ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).
- **DEP-003**: Completion of Phase 2 web app ([feature-web-app-1.md](feature-web-app-1.md)) and Phase 3 mobile app ([feature-mobile-app-1.md](feature-mobile-app-1.md)) for client flows.
- **DEP-004**: PostgreSQL `pgvector` extension available on the database instance.
- **DEP-005**: Python packages: `pillow` (image handling/EXIF), `numpy`, `pytesseract` (with the Tesseract binary installed), and `open_clip_torch` + `torch` for local CLIP embeddings.
- **DEP-006**: Mobile packages: `expo-camera`, `expo-image-picker`.
- **DEP-007**: The Tesseract OCR binary installed locally and an open-source CLIP model available on-disk (downloaded once); no external API access required.

## 5. Files

- **FILE-001**: `apps/api/alembic/versions/0005_enable_pgvector_and_embeddings` — pgvector extension, `business_images` table, vector index.
- **FILE-002**: `apps/api/app/models/business_image.py` — BusinessImage ORM model with embedding column.
- **FILE-003**: `apps/api/app/config.py` — photo-lookup thresholds, limits, and provider settings.
- **FILE-004**: `apps/api/app/vision/base.py` — `OcrProvider` and `EmbeddingProvider` interfaces.
- **FILE-005**: `apps/api/app/vision/ocr_provider.py`, `embedding_provider.py` — provider implementations.
- **FILE-006**: `apps/api/app/vision/image_utils.py` — validation and EXIF stripping.
- **FILE-007**: `apps/api/app/repositories/image_repository.py` — vector and text candidate retrieval.
- **FILE-008**: `apps/api/app/services/photo_lookup_service.py` — end-to-end lookup pipeline.
- **FILE-009**: `apps/api/app/services/ranking.py` — pure `rank_candidates` function.
- **FILE-010**: `apps/api/app/schemas/lookup.py` — request/response schemas.
- **FILE-011**: `apps/api/app/routers/lookup.py` — `POST /lookup/photo` endpoint.
- **FILE-012**: `apps/api/app/cli/backfill_embeddings.py` — business embedding backfill CLI.
- **FILE-013**: `apps/mobile/src/app/scan.tsx` — mobile capture/upload flow.
- **FILE-014**: `apps/web/src/app/scan/page.tsx` — web upload/capture flow.
- **FILE-015**: `apps/mobile/src/lib/api-client.ts`, `apps/web/src/lib/api-client.ts` — `photoLookup` client method.
- **FILE-016**: `packages/shared/src/types.ts` — `PhotoLookupResponse` and `CandidateMatch` types.
- **FILE-017**: Photo evaluation harness (`run_photo_eval.py` + `fixtures/`).
- **FILE-018**: `docs/photo-lookup.md` — pipeline, privacy, and evaluation documentation.
- **FILE-019**: Backend and client test files enumerated in the tasks.

## 6. Testing

- **TEST-001**: `POST /lookup/photo` with a valid image returns HTTP 200 with `candidates` ranked by descending `match_confidence`.
- **TEST-002**: `POST /lookup/photo` with an unsupported MIME type or an oversized file returns HTTP 422 (SEC-001).
- **TEST-003**: `strip_exif` removes GPS/EXIF metadata from an image containing it (SEC-003).
- **TEST-004**: When the top candidate confidence is `>= PHOTO_MATCH_CONFIDENCE_THRESHOLD`, the response has `matched = true` and the correct business id (mocked providers/fixtures).
- **TEST-005**: When no candidate meets the threshold, the response has `matched = false` and includes `ocr_text` for fallback.
- **TEST-006**: `rank_candidates` is deterministic and returns identical ordering for identical inputs.
- **TEST-007**: Vector similarity retrieval returns the nearest business embeddings for a known query embedding (pgvector fixture).
- **TEST-008**: Clients navigate to the matched business detail on `matched = true` and to pre-filled search on `matched = false` (mocked API client).
- **TEST-009**: The photo-lookup endpoint enforces rate limiting (requests beyond the limit return HTTP 429).
- **TEST-010**: `run_photo_eval.py` computes top-1 and top-5 accuracy over the fixture set and exits non-zero if top-1 accuracy is below a configured threshold.
- **TEST-011**: Backend passes `ruff`; clients pass `tsc --noEmit`, ESLint, and Prettier checks.

## 7. Risks & Assumptions

- **RISK-001**: Low match accuracy for visually similar or generic storefronts; mitigated by combining OCR + embeddings (REQ-002/REQ-003) and the evaluation harness (REQ-008) to tune the threshold.
- **RISK-002**: Privacy exposure via image EXIF/GPS or retained uploads; mitigated by mandatory EXIF stripping (SEC-003), no static storage, and temp-file deletion (SEC-002).
- **RISK-003**: Inference cost and latency for OCR/embeddings; mitigated by rate limiting (SEC-004), threadpool/worker execution (CON-002), and provider abstraction for cheaper backends (PAT-001).
- **RISK-004**: Sparse business image coverage limits vector matching recall; mitigated by the backfill CLI (TASK-007) and text-based candidate fallback (REQ-005).
- **RISK-005**: pgvector performance at scale; mitigated by an appropriate ANN index (IVFFlat/HNSW) and the option to migrate to a dedicated vector DB later (ALT-002).
- **ASSUMPTION-001**: The Phase 1–3 systems are deployed and integrable, and the database supports the `pgvector` extension.
- **ASSUMPTION-002**: A labeled set of storefront/logo images mapped to business ids is available for evaluation.
- **ASSUMPTION-003**: The local Tesseract binary and the open-source CLIP model are installed and runnable server-side.
- **ASSUMPTION-004**: Users grant camera/photo-library permission on mobile for the capture flow.

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 5 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [infrastructure-foundations-1.md](infrastructure-foundations-1.md) — Phase 0 foundations (prerequisite).
- [feature-backend-data-1.md](feature-backend-data-1.md) — Phase 1 backend & data (prerequisite).
- [feature-web-app-1.md](feature-web-app-1.md) — Phase 2 web app (prerequisite).
- [feature-mobile-app-1.md](feature-mobile-app-1.md) — Phase 3 mobile app (prerequisite).
- [pgvector documentation](https://github.com/pgvector/pgvector)
- [Pillow documentation](https://pillow.readthedocs.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenCLIP](https://github.com/mlfoundations/open_clip)
- [Expo Camera documentation](https://docs.expo.dev/versions/latest/sdk/camera/)
- [Expo ImagePicker documentation](https://docs.expo.dev/versions/latest/sdk/imagepicker/)
- [MDN MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
