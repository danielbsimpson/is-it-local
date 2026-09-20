/**
 * The single source of truth for classification presentation: colors and labels.
 * Reused across the badge, detail page, and any future components (PAT-002).
 */

import { OwnershipClassification } from "@is-it-local/shared";

export const CLASSIFICATION_COLORS: Record<OwnershipClassification, string> = {
  [OwnershipClassification.FamilyOwned]: "#2e7d32",
  [OwnershipClassification.LocallyOwned]: "#1565c0",
  [OwnershipClassification.Independent]: "#00838f",
  [OwnershipClassification.Franchise]: "#ef6c00",
  [OwnershipClassification.CorporateOwned]: "#c62828",
  [OwnershipClassification.Unknown]: "#546e7a",
};

export const CLASSIFICATION_LABELS: Record<OwnershipClassification, string> = {
  [OwnershipClassification.FamilyOwned]: "Family owned",
  [OwnershipClassification.LocallyOwned]: "Locally owned",
  [OwnershipClassification.Independent]: "Independent",
  [OwnershipClassification.Franchise]: "Franchise",
  [OwnershipClassification.CorporateOwned]: "Corporate owned",
  [OwnershipClassification.Unknown]: "Unknown",
};
