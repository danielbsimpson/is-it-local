import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BusinessDetailView } from "@/components/BusinessDetailView";
import { CLASSIFICATION_LABELS } from "@/lib/classification";
import { OwnershipClassification, type BusinessDetail } from "@/types";

const detail: BusinessDetail = {
  business: {
    id: "11111111-1111-1111-1111-111111111111",
    name: "Corner Bakery",
    location: { type: "Point", coordinates: [-74.2, 40.5] },
    address: { street: "1 Main St", city: "Springfield", region: "IL" },
    categories: ["bakery"],
  },
  classification: {
    classification: OwnershipClassification.FamilyOwned,
    confidence: 0.9,
    updated_at: "2026-01-01T00:00:00Z",
    source_ids: ["22222222-2222-2222-2222-222222222222"],
  },
  sources: [
    {
      id: "22222222-2222-2222-2222-222222222222",
      provider: "searxng",
      url: "https://example.com/about",
      retrieved_at: "2026-01-01T00:00:00Z",
      snippet: "Family run since 1950",
    },
  ],
};

describe("BusinessDetailView", () => {
  it("renders the classification badge and confidence", () => {
    render(<BusinessDetailView detail={detail} />);
    expect(
      screen.getByText(CLASSIFICATION_LABELS[OwnershipClassification.FamilyOwned]),
    ).toBeInTheDocument();
    expect(screen.getByText("90% confidence")).toBeInTheDocument();
  });

  it("renders cited sources as safe external links", () => {
    render(<BusinessDetailView detail={detail} />);
    const link = screen.getByRole("link", { name: /Family run since 1950/ });
    expect(link).toHaveAttribute("href", "https://example.com/about");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("shows a muted state when unclassified", () => {
    render(<BusinessDetailView detail={{ ...detail, classification: null, sources: [] }} />);
    expect(screen.getByText("Not yet classified")).toBeInTheDocument();
    expect(screen.getByText("No sources cited yet.")).toBeInTheDocument();
  });
});
