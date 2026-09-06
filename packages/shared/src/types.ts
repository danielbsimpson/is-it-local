/**
 * Canonical shared types for Is It Local.
 *
 * These types mirror the JSON Schemas in `packages/shared/schema/` and are the
 * single source of truth for the classification enum across web, mobile, and
 * backend clients. Keep them in sync with the schema files.
 */

/** The six canonical ownership categories. */
export enum OwnershipClassification {
  FamilyOwned = "family_owned",
  LocallyOwned = "locally_owned",
  Independent = "independent",
  Franchise = "franchise",
  CorporateOwned = "corporate_owned",
  Unknown = "unknown",
}

/** Review status for a community submission. */
export enum SubmissionStatus {
  Pending = "pending",
  Approved = "approved",
  Rejected = "rejected",
}

/** Postal address components for a business. */
export interface Address {
  street?: string;
  city?: string;
  region?: string;
  postal_code?: string;
  country?: string;
}

/** GeoJSON Point (RFC 7946) with [longitude, latitude]. */
export interface GeoPoint {
  type: "Point";
  coordinates: [number, number];
}

/** Public contact details for a business. */
export interface Contact {
  phone?: string;
  website?: string;
  email?: string;
}

/** A physical business or place that can be classified by ownership. */
export interface Business {
  id: string;
  name: string;
  address?: Address;
  location: GeoPoint;
  categories?: string[];
  contact?: Contact;
  brand?: string | null;
  parent_company?: string | null;
}

/** A piece of evidence supporting a classification. */
export interface Source {
  id: string;
  provider: string;
  url: string;
  retrieved_at: string;
  snippet?: string;
}

/** An ownership classification with confidence and cited source ids. */
export interface Classification {
  business_id: string;
  classification: OwnershipClassification;
  confidence: number;
  sources: string[];
  updated_at: string;
}

/** A user-submitted proposed classification pending review. */
export interface CommunitySubmission {
  id: string;
  business_id: string;
  proposed_classification: OwnershipClassification;
  evidence?: string;
  submitter_id: string;
  status: SubmissionStatus;
  created_at: string;
}
