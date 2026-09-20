/**
 * Single typed entry point for all backend access. Components MUST NOT call
 * `fetch` against the API directly; they go through these functions.
 */

import { config } from "@/lib/config";
import type { Business, BusinessDetail, SearchParams } from "@/types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function buildSearchQuery(params: SearchParams): string {
  const query = new URLSearchParams();
  if (params.name) {
    query.set("name", params.name);
  }
  if (params.lat !== undefined && params.lon !== undefined) {
    query.set("lat", String(params.lat));
    query.set("lon", String(params.lon));
  }
  if (params.radiusM !== undefined) {
    query.set("radius_m", String(params.radiusM));
  }
  return query.toString();
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    headers: { Accept: "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new ApiError(`Request to ${path} failed`, response.status);
  }
  return (await response.json()) as T;
}

export function searchBusinesses(params: SearchParams): Promise<Business[]> {
  const query = buildSearchQuery(params);
  const suffix = query ? `?${query}` : "";
  return requestJson<Business[]>(`/businesses/search${suffix}`);
}

export function getBusiness(id: string): Promise<BusinessDetail> {
  return requestJson<BusinessDetail>(`/businesses/${encodeURIComponent(id)}`);
}
