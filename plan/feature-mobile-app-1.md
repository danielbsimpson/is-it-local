---
goal: Implement Phase 3 Mobile App (React Native / Expo) for Is It Local — search and detail screens, map with "near me" view, shared types, and iOS/Android builds
version: 1.0
date_created: 2026-09-06
last_updated: 2026-09-06
owner: Is It Local Core Team
status: 'Deferred (post-PoC)'
tags: [feature, mobile, react-native, expo]
---

# Introduction

![Status: Deferred (post-PoC)](https://img.shields.io/badge/status-Deferred-lightgrey)

> **Deferred until after the local-first PoC.** The PoC ships web-only (Phases 0–2). When mobile work begins, run the Expo app locally via Expo Go or a local dev build; **EAS cloud builds and app-store listings are out of scope for the PoC** and become relevant only when preparing a public release.

This implementation plan operationalizes **Phase 3 — Mobile App (React Native / Expo)** from [TODO.md](../TODO.md). It delivers a TypeScript Expo application in `apps/mobile` that lets users search businesses by name and location, view business detail with ownership classification, confidence, and cited sources, browse a map with a device-location "near me" view, reuse shared types from `packages/shared`, and produce buildable iOS and Android artifacts with prepared store listings. This plan consumes the REST API from Phase 1 ([feature-backend-data-1.md](feature-backend-data-1.md)) and the shared package from Phase 0 ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)), reusing patterns established by the Phase 2 web app ([feature-web-app-1.md](feature-web-app-1.md)).

## 1. Requirements & Constraints

- **REQ-001**: The mobile app MUST be implemented with Expo (managed workflow) and TypeScript in `apps/mobile`.
- **REQ-002**: The app MUST consume the Phase 1 REST endpoints `GET /businesses/search` and `GET /businesses/{id}`.
- **REQ-003**: The app MUST reuse shared types/enums from `@is-it-local/shared` (`OwnershipClassification`, `Business`, `Source`).
- **REQ-004**: Navigation MUST use Expo Router with at minimum a Search screen, a Map screen, and a Business Detail screen.
- **REQ-005**: The search screen MUST accept a `name` query and MUST support a "near me" search using device location (`lat`, `lon`, `radius_m`).
- **REQ-006**: The map screen MUST render the device location and business markers, each marker colored per its ownership classification.
- **REQ-007**: The business detail screen MUST display the classification badge, numeric confidence rendered as a percentage, and cited sources as tappable external links.
- **REQ-008**: The app MUST request foreground location permission at runtime and MUST degrade gracefully (fallback to manual location/name search) when permission is denied.
- **REQ-009**: The project MUST produce buildable iOS and Android artifacts via EAS Build with a documented build command.
- **REQ-010**: Store-listing assets (app icon, splash, screenshots, descriptions, privacy declarations) MUST be prepared under `apps/mobile/store/`.
- **SEC-001**: The API base URL and any client keys MUST be provided via Expo public environment variables (`EXPO_PUBLIC_*`); server-only secrets MUST NOT be embedded in the app bundle.
- **SEC-002**: All external source links MUST be opened via the platform-safe linking API (`expo-linking`/`Linking.openURL`) after URL validation.
- **SEC-003**: User-provided search input MUST be URL-encoded before insertion into API request URLs.
- **CON-001**: This plan MUST NOT implement authentication, community submissions, or photo lookup (Phase 4+).
- **CON-002**: The app MUST NOT access the database directly; all data access MUST go through the Phase 1 REST API.
- **GUD-001**: All TypeScript MUST pass `tsc --noEmit` and ESLint checks.
- **GUD-002**: Code MUST be organized as `app/` (Expo Router routes), `components/` (presentational), `lib/` (API client + utilities), and `types/` (local view models).
- **PAT-001**: All API access MUST route through a single typed API client module (`lib/api-client.ts`) mirroring the web app contract.
- **PAT-002**: The classification-to-color/label mapping MUST be defined once in `lib/classification.ts` and reused across all components.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Scaffold the Expo app, navigation, typed API client, shared type integration, and classification primitives.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Scaffold an Expo (TypeScript, Expo Router) app in `apps/mobile`; create `apps/mobile/package.json` with scripts `start`, `android`, `ios`, `lint`, `typecheck`. | | |
| TASK-002 | Add `apps/mobile/tsconfig.json` with a path alias `@is-it-local/shared` resolving to `packages/shared/src`, and register `apps/mobile` in the pnpm workspace. | | |
| TASK-003 | Create `apps/mobile/app.json` (Expo config) defining `name`, `slug`, `scheme`, iOS bundle identifier, Android package, and the foreground location permission usage strings. | | |
| TASK-004 | Create `apps/mobile/src/lib/config.ts` reading `EXPO_PUBLIC_API_BASE_URL` and `EXPO_PUBLIC_MAP_TILE_URL` from Expo public env vars. | | |
| TASK-005 | Create `apps/mobile/src/lib/api-client.ts` exporting typed `searchBusinesses(params)` and `getBusiness(id)` using `fetch`, returning `@is-it-local/shared` types; URL-encode all params. | | |
| TASK-006 | Create `apps/mobile/src/lib/classification.ts` exporting `CLASSIFICATION_COLORS` and `CLASSIFICATION_LABELS` for the six values (`family_owned`, `locally_owned`, `independent`, `franchise`, `corporate_owned`, `unknown`). | | |
| TASK-007 | Create `apps/mobile/src/components/ClassificationBadge.tsx` and `apps/mobile/src/components/ConfidenceMeter.tsx` rendering the badge and confidence percentage. | | |
| TASK-008 | Create `apps/mobile/src/app/_layout.tsx` defining the Expo Router tab/stack navigation for Search, Map, and Detail. | | |
| TASK-009 | Create `apps/mobile/.env.example` documenting `EXPO_PUBLIC_API_BASE_URL` and `EXPO_PUBLIC_MAP_TILE_URL`. | | |

### Implementation Phase 2

- GOAL-002: Implement search, business detail, and the map "near me" experience using device location.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Create `apps/mobile/src/lib/location.ts` wrapping `expo-location` to request foreground permission and return `{lat, lon}`, with a graceful denied-permission fallback. | | |
| TASK-011 | Create `apps/mobile/src/app/index.tsx` (Search screen) with a `name` input, a "near me" toggle, a radius selector, and a submit action calling `searchBusinesses`; handle loading, empty, and error states. | | |
| TASK-012 | Create `apps/mobile/src/components/BusinessListItem.tsx` showing name, address, distance, and a `ClassificationBadge`; tapping navigates to the detail route. | | |
| TASK-013 | Create `apps/mobile/src/app/business/[id].tsx` (Detail screen) calling `getBusiness(id)` and rendering name, address, `ClassificationBadge`, `ConfidenceMeter`, and a tappable cited-sources list opened via `expo-linking`. | | |
| TASK-014 | Create `apps/mobile/src/app/map.tsx` (Map screen) using `react-native-maps` to render the device location and business markers colored by classification; tapping a marker opens the detail route. | | |
| TASK-015 | Create `apps/mobile/src/components/ErrorState.tsx` and `apps/mobile/src/components/EmptyState.tsx` reused across screens. | | |
| TASK-016 | Wire the map screen to fetch "near me" businesses via `location.ts` + `searchBusinesses` when foreground permission is granted. | | |

### Implementation Phase 3

- GOAL-003: Add tests, configure iOS/Android EAS builds, and prepare store listings.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Add unit/component tests in `apps/mobile/__tests__/` using `jest-expo` + `@testing-library/react-native` for `ClassificationBadge`, `BusinessListItem`, and the search results rendering (mocked API client). | | |
| TASK-018 | Create `apps/mobile/eas.json` defining `development`, `preview`, and `production` build profiles for iOS and Android. | | |
| TASK-019 | Configure app icons and splash assets in `apps/mobile/assets/` and reference them in `app.json`. | | |
| TASK-020 | Produce Android (`.apk`/`.aab`) and iOS build artifacts via `eas build --profile preview --platform all`; document the command and outputs in `apps/mobile/README.md`. | | |
| TASK-021 | Create `apps/mobile/store/` containing screenshots, short/long descriptions, keywords, and a privacy declaration covering location usage. | | |
| TASK-022 | Create `apps/mobile/README.md` documenting local dev (`expo start`), environment variables, running on simulators/devices, and EAS build/submit steps. | | |

## 3. Alternatives

- **ALT-001**: Bare React Native workflow instead of Expo managed — rejected; Expo (managed) is specified in the README and simplifies iOS/Android builds via EAS.
- **ALT-002**: React Navigation instead of Expo Router — Expo Router chosen for file-based routing consistency with the Next.js web app; React Navigation remains available under the hood.
- **ALT-003**: `@rnmapbox/maps` instead of `react-native-maps` — `react-native-maps` chosen for first-class Expo support and native platform maps; tiles configurable where applicable.
- **ALT-004**: Sharing rendering components directly with the web app — rejected for this phase; web and native primitives differ, so only types/logic in `packages/shared` are reused (REQ-003).
- **ALT-005**: Manual Xcode/Gradle builds — rejected in favor of EAS Build for reproducible, cloud-based iOS/Android artifacts (REQ-009).

## 4. Dependencies

- **DEP-001**: Completion of Phase 1 API ([feature-backend-data-1.md](feature-backend-data-1.md)) providing search and detail endpoints.
- **DEP-002**: Completion of Phase 0 shared package `@is-it-local/shared` ([infrastructure-foundations-1.md](infrastructure-foundations-1.md)).
- **DEP-003**: Node.js 20+, pnpm workspace, and the Expo CLI/EAS CLI.
- **DEP-004**: npm packages: `expo`, `expo-router`, `expo-location`, `expo-linking`, `react-native-maps`, `jest-expo`, `@testing-library/react-native`.
- **DEP-005**: An Expo account and EAS Build access for iOS/Android builds.
- **DEP-006**: Apple Developer and Google Play Console accounts for store submission (submission itself is out of scope; listing preparation is in scope).
- **DEP-007**: A reachable Phase 1 API at `EXPO_PUBLIC_API_BASE_URL`.

## 5. Files

- **FILE-001**: `apps/mobile/package.json` — mobile app scripts and dependencies.
- **FILE-002**: `apps/mobile/tsconfig.json` — TypeScript config with shared path alias.
- **FILE-003**: `apps/mobile/app.json` — Expo config, identifiers, permissions.
- **FILE-004**: `apps/mobile/.env.example` — documented Expo public env vars.
- **FILE-005**: `apps/mobile/src/lib/config.ts` — environment configuration reader.
- **FILE-006**: `apps/mobile/src/lib/api-client.ts` — typed REST API client.
- **FILE-007**: `apps/mobile/src/lib/classification.ts` — classification color/label maps.
- **FILE-008**: `apps/mobile/src/lib/location.ts` — device-location utility.
- **FILE-009**: `apps/mobile/src/components/ClassificationBadge.tsx`, `ConfidenceMeter.tsx` — display components.
- **FILE-010**: `apps/mobile/src/components/BusinessListItem.tsx` — search result item.
- **FILE-011**: `apps/mobile/src/components/ErrorState.tsx`, `EmptyState.tsx` — shared state components.
- **FILE-012**: `apps/mobile/src/app/_layout.tsx` — navigation layout.
- **FILE-013**: `apps/mobile/src/app/index.tsx` — Search screen.
- **FILE-014**: `apps/mobile/src/app/map.tsx` — Map "near me" screen.
- **FILE-015**: `apps/mobile/src/app/business/[id].tsx` — Business Detail screen.
- **FILE-016**: `apps/mobile/eas.json` — EAS build profiles.
- **FILE-017**: `apps/mobile/assets/` — icons and splash assets.
- **FILE-018**: `apps/mobile/__tests__/*` — unit/component tests.
- **FILE-019**: `apps/mobile/store/` — store-listing assets and copy.
- **FILE-020**: `apps/mobile/README.md` — mobile app documentation.

## 6. Testing

- **TEST-001**: `ClassificationBadge` renders the correct label and color for each of the six classification values.
- **TEST-002**: `ConfidenceMeter` renders a 0.0–1.0 value as the correct percentage with an accessible label.
- **TEST-003**: The Search screen renders a `BusinessListItem` per result from a mocked `searchBusinesses` response and shows the empty-state component when the result set is empty.
- **TEST-004**: The Search screen renders the error-state component when the API client rejects.
- **TEST-005**: `location.ts` returns coordinates when permission is granted and invokes the fallback path when permission is denied (mocked `expo-location`).
- **TEST-006**: The Detail screen renders classification, confidence percentage, and each source as a tappable link that calls the linking API with a validated URL.
- **TEST-007**: Search input containing reserved URL characters is correctly URL-encoded in the API request (SEC-003).
- **TEST-008**: `tsc --noEmit` and ESLint pass for `apps/mobile`.
- **TEST-009**: `eas build --profile preview --platform all` completes and produces iOS and Android artifacts (validated in CI or documented manual run).

## 7. Risks & Assumptions

- **RISK-001**: Location permission denial degrades the "near me" experience; mitigated by graceful fallback to manual/name search (REQ-008, TASK-010).
- **RISK-002**: `react-native-maps` configuration differences across iOS/Android may cause build issues; mitigated by EAS build profiles and platform testing (TASK-018, TASK-020).
- **RISK-003**: API contract drift between phases; mitigated by consuming shared types (REQ-003) and a single typed client (PAT-001).
- **RISK-004**: Map/tile provider licensing or API-key requirements; mitigated by configurable `EXPO_PUBLIC_MAP_TILE_URL` and platform-native maps.
- **RISK-005**: EAS Build quota or account limits may block artifact generation; mitigated by using `preview` profiles and documenting manual runs.
- **ASSUMPTION-001**: The Phase 1 API is deployed and reachable at `EXPO_PUBLIC_API_BASE_URL`.
- **ASSUMPTION-002**: Search results include coordinates and/or a distance value usable for map markers and list display.
- **ASSUMPTION-003**: App store submission and review are handled outside this plan; only listing assets are prepared.
- **ASSUMPTION-004**: Expo and EAS accounts are available to the team.

## 8. Related Specifications / Further Reading

- [TODO.md](../TODO.md) — full phased roadmap (Phase 3 source).
- [README.md](../README.md) — project overview, architecture, and tech stack.
- [infrastructure-foundations-1.md](infrastructure-foundations-1.md) — Phase 0 foundations (prerequisite).
- [feature-backend-data-1.md](feature-backend-data-1.md) — Phase 1 backend & data (prerequisite).
- [feature-web-app-1.md](feature-web-app-1.md) — Phase 2 web app (pattern reference).
- [Expo documentation](https://docs.expo.dev/)
- [Expo Router documentation](https://docs.expo.dev/router/introduction/)
- [Expo Location documentation](https://docs.expo.dev/versions/latest/sdk/location/)
- [react-native-maps documentation](https://github.com/react-native-maps/react-native-maps)
- [EAS Build documentation](https://docs.expo.dev/build/introduction/)
