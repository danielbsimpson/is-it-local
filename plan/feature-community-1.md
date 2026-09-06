---
goal: Implement Phase 4 Community & Network Effect for Is It Local — accounts/auth, community submissions and corrections, moderation, contributor reputation, verified-vs-auto states, and abuse reporting
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: 'Planned'
tags: [feature, community, moderation, auth, backend, frontend]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan operationalizes **Phase 4 — Community & Network Effect** from [TODO.md](../TODO.md). It adds user accounts with lightweight authentication, community-submitted ownership classifications and corrections, a moderation/review workflow, a contributor reputation/weighting system, UI surfacing of "community verified" versus "auto-classified" states, and reporting of incorrect or abusive submissions. This plan extends the Phase 1 backend ([feature-backend-data-1.md](feature-backend-data-1.md)), the Phase 2 web app ([feature-web-app-1.md](feature-web-app-1.md)), and the Phase 3 mobile app ([feature-mobile-app-1.md](feature-mobile-app-1.md)), reusing the `CommunitySubmission` schema defined in Phase 0 ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).

## 1. Requirements & Constraints

- **REQ-001**: The backend MUST provide user accounts with lightweight authentication issuing signed JWT access tokens and supporting registration and login.
- **REQ-002**: Authenticated users MUST be able to submit a proposed ownership classification and corrections for a business via `POST /businesses/{id}/submissions`.
- **REQ-003**: Each `CommunitySubmission` MUST conform to the Phase 0 schema (`proposed_classification`, `evidence`, `submitter_id`, `status`) and MUST default to `status = pending`.
- **REQ-004**: A moderation workflow MUST allow a user with the `moderator` role to set a submission `status` to `approved` or `rejected` via `POST /submissions/{id}/moderate`.
- **REQ-005**: Approving a submission MUST update the business's effective ownership classification and MUST record provenance as `community` (versus `auto`).
- **REQ-006**: Each user MUST have a numeric `reputation` score; approved submissions MUST increase it and rejected submissions MUST decrease it by configurable amounts.
- **REQ-007**: When multiple community submissions conflict, resolution MUST weight submissions by submitter `reputation`.
- **REQ-008**: The web and mobile UIs MUST visibly distinguish "Community verified" from "Auto-classified" classification states.
- **REQ-009**: Authenticated users MUST be able to report a submission as incorrect or abusive via `POST /submissions/{id}/reports`.
- **REQ-010**: A submission that accumulates a configurable number of abuse reports (`REPORT_HIDE_THRESHOLD`) MUST be automatically hidden pending moderator review.
- **SEC-001**: Passwords MUST be stored using a salted, adaptive hash (`argon2` or `bcrypt`); plaintext passwords MUST NOT be stored or logged.
- **SEC-002**: All write endpoints (submissions, moderation, reports) MUST require a valid authenticated token; moderation endpoints MUST additionally require the `moderator` role.
- **SEC-003**: All submission and report inputs MUST be validated with Pydantic; free-text fields MUST be length-limited and sanitized before storage and display.
- **SEC-004**: Submission and report write endpoints MUST enforce per-user rate limiting to mitigate spam and abuse.
- **SEC-005**: JWT signing secrets MUST be read from environment variables (`JWT_SECRET`) and MUST NOT be hardcoded.
- **CON-001**: This plan MUST NOT implement photo lookup (Phase 5).
- **CON-002**: All data access MUST occur through the backend API; clients MUST NOT access the database directly.
- **GUD-001**: Backend code MUST follow the Phase 1 layering (`routers/`, `services/`, `repositories/`, `models/`, `schemas/`) and pass `ruff` checks.
- **GUD-002**: Frontend code MUST pass `tsc --noEmit`, ESLint, and Prettier checks.
- **PAT-001**: Authorization MUST be enforced via reusable FastAPI dependencies (`require_user`, `require_moderator`).
- **PAT-002**: Classification provenance MUST be represented by an enum `ClassificationSource` with values `auto` and `community`, defined once and reused across backend and clients.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Implement user accounts, lightweight authentication, roles, and reputation storage in the backend.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create ORM model `apps/api/app/models/user.py` (`User`) with fields `id` (uuid), `email` (unique), `password_hash`, `role` (enum: `user`, `moderator`), `reputation` (integer, default 0), `created_at`. | | |
| TASK-002 | Create Alembic migration `0003_create_users` creating the `users` table with a unique index on `email`. | | |
| TASK-003 | Create `apps/api/app/services/auth_service.py` implementing `register(email, password)`, `authenticate(email, password)`, password hashing (`argon2`), and JWT issuance/verification using `JWT_SECRET`. | | |
| TASK-004 | Add `JWT_SECRET`, `REPUTATION_APPROVE_DELTA`, `REPUTATION_REJECT_DELTA`, `REPORT_HIDE_THRESHOLD`, and `COMMUNITY_WRITE_RATE_LIMIT_PER_MIN` to `apps/api/app/config.py` `Settings`. | | |
| TASK-005 | Create `apps/api/app/deps/auth.py` exposing FastAPI dependencies `require_user` and `require_moderator` that decode the bearer token and enforce role. | | |
| TASK-006 | Create `apps/api/app/routers/auth.py` exposing `POST /auth/register` and `POST /auth/login` returning JWT access tokens. | | |
| TASK-007 | Create Pydantic schemas in `apps/api/app/schemas/auth.py` (`RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserPublic`). | | |
| TASK-008 | Create tests `apps/api/tests/test_auth.py` covering registration, login, invalid credentials, and role-protected access. | | |

### Implementation Phase 2

- GOAL-002: Implement community submissions, moderation workflow, reputation-weighted resolution, and abuse reporting in the backend.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-009 | Extend `apps/api/app/models/community_submission.py` to include `status` (enum: `pending`, `approved`, `rejected`, `hidden`), `created_at`, and a foreign key to `users`. | | |
| TASK-010 | Create ORM model `apps/api/app/models/report.py` (`SubmissionReport`) with fields `id`, `submission_id`, `reporter_id`, `reason` (enum: `incorrect`, `abusive`, `spam`), `created_at`. | | |
| TASK-011 | Add a `classification_source` column (enum `auto`/`community`) to `ownership_classifications` via Alembic migration `0004_add_classification_source_and_reports` and create the `submission_reports` table. | | |
| TASK-012 | Create `apps/api/app/repositories/submission_repository.py` with `create`, `get_by_id`, `list_for_business`, `set_status`, and `count_reports`. | | |
| TASK-013 | Create `apps/api/app/services/submission_service.py` implementing `submit`, `moderate(status)` (updates business classification and sets `classification_source = community` on approval, applies reputation deltas), and reputation-weighted conflict resolution `resolve_effective_classification(business_id)`. | | |
| TASK-014 | Create `apps/api/app/services/report_service.py` implementing `report(submission_id, reporter_id, reason)` and auto-hiding a submission when report count reaches `REPORT_HIDE_THRESHOLD`. | | |
| TASK-015 | Create `apps/api/app/routers/submissions.py` exposing `POST /businesses/{id}/submissions` (require_user), `GET /businesses/{id}/submissions`, `POST /submissions/{id}/moderate` (require_moderator), and `POST /submissions/{id}/reports` (require_user), all rate-limited. | | |
| TASK-016 | Update the business detail response schema/service to include `classification_source` and a `verified` boolean derived from it. | | |
| TASK-017 | Create tests `apps/api/tests/test_submissions.py`, `test_moderation.py`, `test_reputation_resolution.py`, and `test_reports.py`. | | |

### Implementation Phase 3

- GOAL-003: Surface community features and verified-vs-auto states in the web and mobile clients.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | Extend `apps/web/src/lib/api-client.ts` and `apps/mobile/src/lib/api-client.ts` with `register`, `login`, `submitClassification`, `listSubmissions`, `reportSubmission`, and token storage/attachment on requests. | | |
| TASK-019 | Add a shared `ClassificationSource` enum and a `VerifiedBadge` concept to `packages/shared/src/types.ts`; define labels "Community verified" and "Auto-classified". | | |
| TASK-020 | Create web components `apps/web/src/components/VerifiedBadge.tsx` and `apps/web/src/components/SubmissionForm.tsx`; render the verified/auto badge on the detail page and allow authenticated users to submit corrections. | | |
| TASK-021 | Create mobile components `apps/mobile/src/components/VerifiedBadge.tsx` and `apps/mobile/src/components/SubmissionForm.tsx`; render the badge on the detail screen and allow authenticated submissions. | | |
| TASK-022 | Add authentication screens/pages: `apps/web/src/app/(auth)/login/page.tsx` and `register/page.tsx`; `apps/mobile/src/app/login.tsx` and `register.tsx`; store the token securely (`expo-secure-store` on mobile). | | |
| TASK-023 | Add a report action (report incorrect/abusive) to submission displays in both web and mobile detail views. | | |
| TASK-024 | Create a minimal moderator review view `apps/web/src/app/moderate/page.tsx` listing pending/hidden submissions with approve/reject actions (visible only to `moderator` role). | | |
| TASK-025 | Add tests: web `apps/web/tests/submission.test.tsx` and `verified-badge.test.tsx`; mobile `apps/mobile/__tests__/submission.test.tsx` (mocked API client). | | |

## 3. Alternatives

- **ALT-001**: Third-party auth provider (OAuth/social login) instead of self-hosted JWT auth — deferred; the TODO specifies "lightweight auth," and self-hosted JWT minimizes external dependencies for the MVP. Social login can be added later.
- **ALT-002**: Fully automated moderation via ML content filters instead of human moderators — rejected for this phase; human moderation with abuse reporting is more accurate and auditable for community-driven classifications.
- **ALT-003**: Simple last-write-wins for conflicting submissions instead of reputation weighting — rejected; reputation weighting (REQ-007) better resists manipulation and rewards trusted contributors.
- **ALT-004**: Session cookies instead of JWT — JWT chosen for uniform use across web and mobile clients; cookie sessions complicate the native mobile flow.
- **ALT-005**: Soft-delete instead of a `hidden` status for reported submissions — `hidden` chosen so moderators can review and restore, preserving an audit trail.

## 4. Dependencies

- **DEP-001**: Completion of Phase 1 backend ([feature-backend-data-1.md](feature-backend-data-1.md)) including the businesses and classifications tables.
- **DEP-002**: Completion of Phase 0 `CommunitySubmission` schema and shared package ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).
- **DEP-003**: Completion of Phase 2 web app ([feature-web-app-1.md](feature-web-app-1.md)) and Phase 3 mobile app ([feature-mobile-app-1.md](feature-mobile-app-1.md)) for client integration.
- **DEP-004**: Python packages: `argon2-cffi` (or `passlib[bcrypt]`), `pyjwt`, plus existing Phase 1 dependencies.
- **DEP-005**: A rate-limiting mechanism (in-process token bucket or Redis-backed) for community write endpoints.
- **DEP-006**: Mobile secure token storage package `expo-secure-store`.

## 5. Files

- **FILE-001**: `apps/api/app/models/user.py` — User ORM model with role and reputation.
- **FILE-002**: `apps/api/app/models/community_submission.py` — extended submission model.
- **FILE-003**: `apps/api/app/models/report.py` — SubmissionReport ORM model.
- **FILE-004**: `apps/api/alembic/versions/0003_create_users`, `0004_add_classification_source_and_reports` — migrations.
- **FILE-005**: `apps/api/app/services/auth_service.py` — registration, login, hashing, JWT.
- **FILE-006**: `apps/api/app/services/submission_service.py` — submission, moderation, reputation-weighted resolution.
- **FILE-007**: `apps/api/app/services/report_service.py` — abuse reporting and auto-hide.
- **FILE-008**: `apps/api/app/deps/auth.py` — `require_user` / `require_moderator` dependencies.
- **FILE-009**: `apps/api/app/routers/auth.py`, `submissions.py` — auth and community endpoints.
- **FILE-010**: `apps/api/app/schemas/auth.py` and submission/report schemas.
- **FILE-011**: `apps/api/app/repositories/submission_repository.py` — submission data access.
- **FILE-012**: `apps/api/app/config.py` — new community/auth settings.
- **FILE-013**: `packages/shared/src/types.ts` — `ClassificationSource` enum and verified labels.
- **FILE-014**: `apps/web/src/components/VerifiedBadge.tsx`, `SubmissionForm.tsx` — web community UI.
- **FILE-015**: `apps/web/src/app/(auth)/login/page.tsx`, `register/page.tsx`, `apps/web/src/app/moderate/page.tsx` — web auth and moderation views.
- **FILE-016**: `apps/mobile/src/components/VerifiedBadge.tsx`, `SubmissionForm.tsx` — mobile community UI.
- **FILE-017**: `apps/mobile/src/app/login.tsx`, `register.tsx` — mobile auth screens.
- **FILE-018**: `apps/web/src/lib/api-client.ts`, `apps/mobile/src/lib/api-client.ts` — extended clients with auth/community calls.
- **FILE-019**: Backend and client test files enumerated in the tasks.

## 6. Testing

- **TEST-001**: Registration creates a user with a hashed (non-plaintext) password; login returns a valid JWT; invalid credentials return HTTP 401.
- **TEST-002**: `POST /businesses/{id}/submissions` requires authentication (HTTP 401 without token) and creates a `pending` submission conforming to the schema.
- **TEST-003**: `POST /submissions/{id}/moderate` requires the `moderator` role (HTTP 403 for regular users).
- **TEST-004**: Approving a submission updates the business classification and sets `classification_source = community`; the detail response reports `verified = true`.
- **TEST-005**: Approving a submission increases the submitter's reputation by `REPUTATION_APPROVE_DELTA`; rejecting decreases it by `REPUTATION_REJECT_DELTA`.
- **TEST-006**: With two conflicting approved submissions, `resolve_effective_classification` selects the one from the higher-reputation submitter.
- **TEST-007**: Submitting `REPORT_HIDE_THRESHOLD` reports for a submission sets its status to `hidden`.
- **TEST-008**: Community write endpoints enforce per-user rate limiting (requests beyond the limit return HTTP 429).
- **TEST-009**: Web and mobile detail views render "Community verified" when `classification_source = community` and "Auto-classified" otherwise.
- **TEST-010**: Free-text `evidence` exceeding the configured length limit is rejected with HTTP 422.
- **TEST-011**: Backend passes `ruff` checks; clients pass `tsc --noEmit`, ESLint, and Prettier checks.

## 7. Risks & Assumptions

- **RISK-001**: Coordinated abuse or vote manipulation could distort classifications; mitigated by reputation weighting (REQ-007), rate limiting (SEC-004), and abuse reporting with auto-hide (REQ-010).
- **RISK-002**: Storing user accounts introduces PII and security obligations; mitigated by adaptive password hashing (SEC-001), token secret management (SEC-005), and input sanitization (SEC-003).
- **RISK-003**: Moderator bottlenecks could delay review of hidden/pending submissions; mitigated by the moderator review view (TASK-024) and configurable thresholds.
- **RISK-004**: Reputation parameters may need tuning to avoid gaming; mitigated by making deltas and thresholds configurable (TASK-004).
- **RISK-005**: Conflicting provenance between auto and community classifications; mitigated by explicit `classification_source` provenance (PAT-002) and defined resolution rules.
- **ASSUMPTION-001**: The Phase 1–3 systems are deployed and integrable.
- **ASSUMPTION-002**: Moderator accounts are provisioned by an administrator (moderator onboarding process is out of scope).
- **ASSUMPTION-003**: The open question on moderation policy/thresholds is resolved to configurable numeric thresholds for this phase.
- **ASSUMPTION-004**: A rate-limiting backend (in-process or Redis) is available in the deployment environment.

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 4 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [infrastructure-foundations-1.md](infrastructure-foundations-1.md) — Phase 0 foundations (prerequisite).
- [feature-backend-data-1.md](feature-backend-data-1.md) — Phase 1 backend & data (prerequisite).
- [feature-web-app-1.md](feature-web-app-1.md) — Phase 2 web app (prerequisite).
- [feature-mobile-app-1.md](feature-mobile-app-1.md) — Phase 3 mobile app (prerequisite).
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JSON Web Token (JWT) — RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [Argon2 password hashing](https://github.com/P-H-C/phc-winner-argon2)
