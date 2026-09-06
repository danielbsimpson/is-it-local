---
goal: Establish Phase 0 Foundations for the Is It Local project (monorepo, tooling, data model, and ownership classification schema)
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: 'Completed'
tags: [infrastructure, architecture, foundations, chore, data]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-green)

This implementation plan operationalizes **Phase 0 — Foundations** from [TODO.md](../TODO.md). It establishes the monorepo structure, root tooling, licensing, environment configuration, continuous integration, contribution guidelines, and the core data model and ownership classification schema for the **Is It Local** project. Completion of this plan yields a fully scaffolded repository ready for Phase 1 (Backend & Data) development.

## 1. Requirements & Constraints

- **REQ-001**: Repository MUST use a monorepo layout with top-level directories `apps/`, `packages/`, `infra/`, and `docs/`.
- **REQ-002**: JavaScript/TypeScript packages MUST be managed with `pnpm` workspaces via a root `pnpm-workspace.yaml`.
- **REQ-003**: Python code MUST be managed with a per-package `pyproject.toml` using `ruff` for lint/format.
- **REQ-004**: A `LICENSE` file containing the MIT License MUST exist at the repository root.
- **REQ-005**: A `.env.example` file MUST document all required environment variables with placeholder values and comments.
- **REQ-006**: The ownership classification schema MUST include exactly these six values: `family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`.
- **REQ-007**: Every classification record MUST include a numeric `confidence` field and a list of `sources`.
- **SEC-001**: No real secrets, API keys, or credentials MAY be committed; `.env` MUST be listed in `.gitignore`.
- **SEC-002**: CI dependency installation MUST use lockfiles (`pnpm-lock.yaml`, `uv.lock` or `poetry.lock`) to ensure reproducible builds.
- **CON-001**: This plan produces NO application business logic; it produces structure, configuration, and schema definitions only.
- **CON-002**: All shared type definitions MUST live in `packages/shared` and be consumable by both `apps/web` and `apps/mobile`.
- **GUD-001**: Markdown files MUST pass a markdown linter with no errors.
- **GUD-002**: All identifiers, file paths, and configuration keys MUST use lowercase-kebab-case for files and snake_case for schema fields.
- **PAT-001**: The classification schema MUST be defined once as a canonical source (JSON Schema) and referenced by language-specific type definitions.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Establish repository structure, root tooling, licensing, environment configuration, CI, and contribution guidelines.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create top-level directories with `.gitkeep` placeholders: `apps/api/`, `apps/web/`, `apps/mobile/`, `packages/enrichment/`, `packages/shared/`, `infra/`, `docs/`. | ✅ | 2026-09-06 |
| TASK-002 | Create root `pnpm-workspace.yaml` declaring `packages: ["apps/*", "packages/*"]`. | ✅ | 2026-09-06 |
| TASK-003 | Create root `package.json` with fields `name: "is-it-local"`, `private: true`, `packageManager: "pnpm@9"`, and workspace scripts `lint`, `format`, `test`, `build`. | ✅ | 2026-09-06 |
| TASK-004 | Create root `.gitignore` including `.env`, `node_modules/`, `__pycache__/`, `.venv/`, `dist/`, `.next/`, `*.log`. | ✅ | 2026-09-06 |
| TASK-005 | Create `LICENSE` at repository root containing the MIT License text with copyright line `Copyright (c) 2026 Is It Local`. | ✅ | 2026-09-06 |
| TASK-006 | Create `.env.example` documenting `DATABASE_URL`, `LLM_BASE_URL`, `LLM_MODEL`, `SEARXNG_BASE_URL` with commented placeholder values (local-first PoC; no paid API keys). | ✅ | 2026-09-06 |
| TASK-007 | Create `.prettierrc.json` (root) and `prettier.config` ignore file `.prettierignore` for TypeScript/Markdown formatting. | ✅ | 2026-09-06 |
| TASK-008 | Create root `ruff.toml` configuring `ruff` lint + format rules for Python packages (`apps/api`, `packages/enrichment`). | ✅ | 2026-09-06 |
| TASK-009 | Create `.pre-commit-config.yaml` with hooks: `ruff`, `ruff-format`, `prettier`, and `end-of-file-fixer`. | ✅ | 2026-09-06 |
| TASK-010 | Create `.github/workflows/ci.yml` running jobs: `lint`, `test`, `build` on `push` and `pull_request` to `main`, using `pnpm/action-setup` and `actions/setup-python`. | ✅ | 2026-09-06 |
| TASK-011 | Create `CONTRIBUTING.md` at repository root describing branch strategy, commit conventions, and PR process. | ✅ | 2026-09-06 |
| TASK-012 | Create `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, and `.github/pull_request_template.md`. | ✅ | 2026-09-06 |

### Implementation Phase 2

- GOAL-002: Define the canonical data model and ownership classification schema, and document them.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Create `packages/shared/schema/business.schema.json` (JSON Schema draft 2020-12) defining the **Business** entity: `id` (uuid), `name` (string), `address` (object), `location` (GeoJSON Point), `categories` (string[]), `contact` (object), `brand` (string, nullable), `parent_company` (string, nullable). | ✅ | 2026-09-06 |
| TASK-014 | Create `packages/shared/schema/classification.schema.json` defining the **Ownership Classification**: `business_id` (uuid), `classification` (enum: `family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`), `confidence` (number, 0.0–1.0), `sources` (array of Source references), `updated_at` (date-time). | ✅ | 2026-09-06 |
| TASK-015 | Create `packages/shared/schema/source.schema.json` defining the **Source** entity: `id` (uuid), `provider` (string), `url` (uri), `retrieved_at` (date-time), `snippet` (string). | ✅ | 2026-09-06 |
| TASK-016 | Create `packages/shared/schema/community-submission.schema.json` defining the **Community Submission** entity: `id` (uuid), `business_id` (uuid), `proposed_classification` (enum, same values as TASK-014), `evidence` (string), `submitter_id` (uuid), `status` (enum: `pending`, `approved`, `rejected`), `created_at` (date-time). | ✅ | 2026-09-06 |
| TASK-017 | Create `packages/shared/src/types.ts` exporting TypeScript types/enums generated from the JSON Schemas (`OwnershipClassification`, `Business`, `Source`, `CommunitySubmission`). | ✅ | 2026-09-06 |
| TASK-018 | Create `packages/shared/package.json` (`name: "@is-it-local/shared"`, `private: true`, `main`/`types` pointing to `src/types.ts`) and `packages/shared/tsconfig.json`. | ✅ | 2026-09-06 |
| TASK-019 | Create `docs/data-model.md` documenting all four entities, field definitions, relationships, and the six classification values with confidence + sources semantics. | ✅ | 2026-09-06 |
| TASK-020 | Create `docs/classification-schema.md` documenting the definition and boundaries of each ownership category, including the distinction between `locally_owned` and `independent`. | ✅ | 2026-09-06 |

## 3. Alternatives

- **ALT-001**: Polyrepo (separate repositories per app) — rejected because it complicates sharing the classification schema and types across web, mobile, and backend.
- **ALT-002**: `npm`/`yarn` workspaces instead of `pnpm` — rejected; `pnpm` provides stricter dependency isolation and faster installs, matching the README tech stack.
- **ALT-003**: Defining types separately per language without a canonical schema — rejected in favor of PAT-001 (single JSON Schema source of truth) to prevent drift between backend and clients.
- **ALT-004**: Using Poetry for Python — acceptable but `ruff` + `pyproject.toml` with `uv` is preferred for speed; final tool selection deferred to Phase 1 (see DEP-002).

## 4. Dependencies

- **DEP-001**: `pnpm@9` installed in the CI and developer environments.
- **DEP-002**: Python 3.11+ and `ruff` available for Python linting/formatting.
- **DEP-003**: `pre-commit` framework for local git hooks.
- **DEP-004**: GitHub Actions runners with `pnpm/action-setup` and `actions/setup-python`.
- **DEP-005**: A JSON Schema draft 2020-12 validator (e.g., `ajv`) for validating schema files in CI.

## 5. Files

- **FILE-001**: `pnpm-workspace.yaml` — declares pnpm workspace package globs.
- **FILE-002**: `package.json` (root) — workspace metadata and top-level scripts.
- **FILE-003**: `.gitignore` — ignores secrets, build outputs, and dependency directories.
- **FILE-004**: `LICENSE` — MIT License text.
- **FILE-005**: `.env.example` — documented environment variable placeholders.
- **FILE-006**: `.prettierrc.json` and `.prettierignore` — formatting configuration.
- **FILE-007**: `ruff.toml` — Python lint/format configuration.
- **FILE-008**: `.pre-commit-config.yaml` — local git hook definitions.
- **FILE-009**: `.github/workflows/ci.yml` — CI pipeline (lint, test, build).
- **FILE-010**: `CONTRIBUTING.md` — contribution guidelines.
- **FILE-011**: `.github/ISSUE_TEMPLATE/*.md` and `.github/pull_request_template.md` — issue/PR templates.
- **FILE-012**: `packages/shared/schema/business.schema.json` — Business entity schema.
- **FILE-013**: `packages/shared/schema/classification.schema.json` — Ownership Classification schema.
- **FILE-014**: `packages/shared/schema/source.schema.json` — Source entity schema.
- **FILE-015**: `packages/shared/schema/community-submission.schema.json` — Community Submission schema.
- **FILE-016**: `packages/shared/src/types.ts` — TypeScript types/enums.
- **FILE-017**: `packages/shared/package.json` and `packages/shared/tsconfig.json` — shared package configuration.
- **FILE-018**: `docs/data-model.md` — data model documentation.
- **FILE-019**: `docs/classification-schema.md` — classification category documentation.

## 6. Testing

- **TEST-001**: Validate all four JSON Schema files parse as valid JSON Schema draft 2020-12 using `ajv` (or equivalent) in CI; build fails on invalid schema.
- **TEST-002**: Assert `packages/shared/src/types.ts` compiles with `tsc --noEmit` and exports the `OwnershipClassification` enum containing exactly the six required values.
- **TEST-003**: Assert `pnpm install --frozen-lockfile` succeeds at the repository root using the committed lockfile.
- **TEST-004**: Assert `ruff check` and `ruff format --check` pass on all Python files.
- **TEST-005**: Assert `.gitignore` contains `.env` and that no `.env` file is tracked by git (`git ls-files | grep -x .env` returns nothing).
- **TEST-006**: Assert the CI workflow file is valid YAML and defines `lint`, `test`, and `build` jobs.
- **TEST-007**: Assert all Markdown files pass a markdown linter (`markdownlint`) with no errors.

## 7. Risks & Assumptions

- **RISK-001**: Divergence between JSON Schema definitions and language-specific types if type generation is manual; mitigated by TEST-002 and PAT-001.
- **RISK-002**: Tooling version drift across contributors may cause inconsistent lint/format results; mitigated by pinning versions in config and CI.
- **RISK-003**: The `locally_owned` vs `independent` boundary may remain ambiguous, affecting downstream classification accuracy; mitigated by explicit documentation in TASK-020.
- **ASSUMPTION-001**: The tech stack from [README.md](../README.md) (FastAPI, PostgreSQL/PostGIS, Next.js, React Native/Expo, pnpm) is confirmed and stable for Phase 0.
- **ASSUMPTION-002**: GitHub is the hosting platform, so `.github/` workflows and templates apply.
- **ASSUMPTION-003**: No database is provisioned in Phase 0; schemas are definition-only artifacts consumed in Phase 1.

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 0 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [JSON Schema draft 2020-12 specification](https://json-schema.org/specification)
- [pnpm workspaces documentation](https://pnpm.io/workspaces)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [GeoJSON specification (RFC 7946)](https://datatracker.ietf.org/doc/html/rfc7946)
