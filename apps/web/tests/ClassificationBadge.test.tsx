import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ClassificationBadge } from "@/components/ClassificationBadge";
import { CLASSIFICATION_COLORS, CLASSIFICATION_LABELS } from "@/lib/classification";
import { OwnershipClassification } from "@/types";

describe("ClassificationBadge", () => {
  it("renders the label for a classification", () => {
    render(<ClassificationBadge classification={OwnershipClassification.FamilyOwned} />);
    expect(
      screen.getByText(CLASSIFICATION_LABELS[OwnershipClassification.FamilyOwned]),
    ).toBeInTheDocument();
  });

  it("applies the mapped color", () => {
    render(<ClassificationBadge classification={OwnershipClassification.Franchise} />);
    const badge = screen.getByTestId("classification-badge");
    expect(badge).toHaveAttribute("data-classification", OwnershipClassification.Franchise);
    expect(badge).toHaveStyle({
      backgroundColor: CLASSIFICATION_COLORS[OwnershipClassification.Franchise],
    });
  });
});
