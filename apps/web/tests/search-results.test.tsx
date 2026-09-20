import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SearchResults } from "@/components/SearchResults";
import type { Business } from "@/types";

const business: Business = {
  id: "11111111-1111-1111-1111-111111111111",
  name: "Corner Bakery",
  location: { type: "Point", coordinates: [-74.2, 40.5] },
  address: { street: "1 Main St", city: "Springfield" },
  categories: ["bakery"],
};

describe("SearchResults", () => {
  it("shows a loading state", () => {
    render(<SearchResults status="loading" businesses={[]} />);
    expect(screen.getByText("Searching businesses…")).toBeInTheDocument();
  });

  it("shows an error state", () => {
    render(<SearchResults status="error" businesses={[]} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("shows an empty state", () => {
    render(<SearchResults status="success" businesses={[]} />);
    expect(screen.getByText("No businesses matched your search.")).toBeInTheDocument();
  });

  it("renders businesses with a computed distance", () => {
    render(
      <SearchResults
        status="success"
        businesses={[business]}
        center={{ lat: 40.5, lon: -74.21 }}
      />,
    );
    expect(screen.getByText("Corner Bakery")).toBeInTheDocument();
    expect(screen.getByText(/away$/)).toBeInTheDocument();
  });
});
