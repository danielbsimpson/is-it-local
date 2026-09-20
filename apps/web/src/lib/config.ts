/**
 * Client-safe runtime configuration read from `NEXT_PUBLIC_*` environment variables.
 * Only values safe to expose in the browser belong here.
 */

export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  mapTileUrl:
    process.env.NEXT_PUBLIC_MAP_TILE_URL ?? "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  geocodeUrl:
    process.env.NEXT_PUBLIC_GEOCODE_URL ?? "https://nominatim.openstreetmap.org/search",
} as const;
