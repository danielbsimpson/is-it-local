import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SearchForm } from "@/components/SearchForm";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/geocode", () => ({
  geocode: vi.fn(async (query: string) =>
    query.includes("nowhere") ? null : { lat: 40.5, lon: -74.2 },
  ),
  currentPosition: vi.fn(async () => ({ lat: 12.34, lon: 56.78 })),
}));

describe("SearchForm", () => {
  beforeEach(() => {
    push.mockClear();
  });

  it("navigates with an encoded name-only query", async () => {
    const user = userEvent.setup();
    render(<SearchForm />);
    await user.type(screen.getByPlaceholderText("e.g. Corner Bakery"), "Joe & Sons");
    await user.click(screen.getByRole("button", { name: "Search" }));

    expect(push).toHaveBeenCalledTimes(1);
    const target = push.mock.calls[0][0] as string;
    expect(target.startsWith("/search?")).toBe(true);
    const params = new URLSearchParams(target.split("?")[1]);
    expect(params.get("name")).toBe("Joe & Sons");
  });

  it("geocodes a location into lat/lon/radius params", async () => {
    const user = userEvent.setup();
    render(<SearchForm />);
    await user.type(screen.getByPlaceholderText("City, address, or ZIP"), "Somewhere");
    await user.click(screen.getByRole("button", { name: "Search" }));

    const params = new URLSearchParams((push.mock.calls[0][0] as string).split("?")[1]);
    expect(params.get("lat")).toBe("40.5");
    expect(params.get("lon")).toBe("-74.2");
    expect(params.get("radius_m")).toBe("5000");
  });

  it("uses the browser geolocation when requested", async () => {
    const user = userEvent.setup();
    render(<SearchForm />);
    await user.click(screen.getByRole("button", { name: "Use my location" }));

    const params = new URLSearchParams((push.mock.calls[0][0] as string).split("?")[1]);
    expect(params.get("lat")).toBe("12.34");
    expect(params.get("lon")).toBe("56.78");
  });
});
