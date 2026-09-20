/** Great-circle distance helpers for showing how far a result is from the search center. */

import type { Business, Center } from "@/types";

const EARTH_RADIUS_M = 6_371_000;

function toRadians(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

/** Haversine distance in meters between two lat/lon points. */
export function haversineMeters(a: Center, b: Center): number {
  const dLat = toRadians(b.lat - a.lat);
  const dLon = toRadians(b.lon - a.lon);
  const lat1 = toRadians(a.lat);
  const lat2 = toRadians(b.lat);

  const h =
    Math.sin(dLat / 2) ** 2 + Math.sin(dLon / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
}

/** Distance in meters from a center to a business, or null when no center is set. */
export function distanceToBusiness(business: Business, center: Center | null): number | null {
  if (!center) {
    return null;
  }
  const [lon, lat] = business.location.coordinates;
  return haversineMeters(center, { lat, lon });
}

/** Human-friendly distance string (e.g. "450 m" or "2.3 km"). */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  return `${(meters / 1000).toFixed(1)} km`;
}
