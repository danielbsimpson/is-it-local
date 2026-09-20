import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConfidenceMeter } from "@/components/ConfidenceMeter";

describe("ConfidenceMeter", () => {
  it("renders confidence as a rounded percentage", () => {
    render(<ConfidenceMeter value={0.826} />);
    expect(screen.getByText("83% confidence")).toBeInTheDocument();
    expect(screen.getByRole("meter")).toHaveAttribute("aria-valuenow", "83");
  });

  it("clamps out-of-range values", () => {
    render(<ConfidenceMeter value={1.9} />);
    expect(screen.getByRole("meter")).toHaveAttribute("aria-valuenow", "100");
  });
});
