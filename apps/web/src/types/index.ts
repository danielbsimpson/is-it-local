/**
 * Local view models mirroring the Phase 1 REST API responses.
 *
 * These reuse the canonical shared types where the shapes match and add the
 * detail-endpoint composite that the API returns.
 */

import type { Business, OwnershipClassification, Source } from "@is-it-local/shared";

export type { Business, Source } from "@is-it-local/shared";
export { OwnershipClassification } from "@is-it-local/shared";

/** The classification block returned by `GET /businesses/{id}`. */
export interface DetailClassification {
  classification: OwnershipClassification;
  confidence: number;
  updated_at: string;
  source_ids: string[];
}

/** Composite response from `GET /businesses/{id}`. */
export interface BusinessDetail {
  business: Business;
  classification: DetailClassification | null;
  sources: Source[];
}

/** Parameters accepted by the business search endpoint. */
export interface SearchParams {
  name?: string;
  lat?: number;
  lon?: number;
  radiusM?: number;
}

/** A geographic center used to compute result distances. */
export interface Center {
  lat: number;
  lon: number;
}
