/**
 * Free-text location resolution via a Nominatim (OpenStreetMap) endpoint.
 * Falls back gracefully (returns null) when geocoding fails or finds nothing.
 */

import { config } from "@/lib/config";
import type { Center } from "@/types";

interface NominatimResult {
  lat: string;
  lon: string;
}

export async function geocode(query: string): Promise<Center | null> {
  const trimmed = query.trim();
  if (!trimmed) {
    return null;
  }

  const url = new URL(config.geocodeUrl);
  url.searchParams.set("q", trimmed);
  url.searchParams.set("format", "json");
  url.searchParams.set("limit", "1");

  try {
    const response = await fetch(url.toString(), {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return null;
    }
    const results = (await response.json()) as NominatimResult[];
    if (!results.length) {
      return null;
    }
    const { lat, lon } = results[0];
    return { lat: Number(lat), lon: Number(lon) };
  } catch {
    return null;
  }
}

/** Resolve the browser's current position, or null when unavailable/denied. */
export function currentPosition(): Promise<Center | null> {
  if (typeof navigator === "undefined" || !navigator.geolocation) {
    return Promise.resolve(null);
  }
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => resolve({ lat: position.coords.latitude, lon: position.coords.longitude }),
      () => resolve(null),
      { timeout: 10_000 },
    );
  });
}
