"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { SearchForm } from "@/components/SearchForm";
import { SearchResults, type SearchStatus } from "@/components/SearchResults";
import { searchBusinesses } from "@/lib/api-client";
import { logError } from "@/lib/logger";
import type { Business, Center, SearchParams } from "@/types";

function parseParams(params: URLSearchParams): { search: SearchParams; center: Center | null } {
  const name = params.get("name") ?? undefined;
  const latRaw = params.get("lat");
  const lonRaw = params.get("lon");
  const radiusRaw = params.get("radius_m");

  const lat = latRaw != null ? Number(latRaw) : undefined;
  const lon = lonRaw != null ? Number(lonRaw) : undefined;
  const radiusM = radiusRaw != null ? Number(radiusRaw) : undefined;

  const center = lat != null && lon != null ? { lat, lon } : null;
  return { search: { name, lat, lon, radiusM }, center };
}

function SearchView() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<SearchStatus>("loading");
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [center, setCenter] = useState<Center | null>(null);

  const key = searchParams.toString();

  useEffect(() => {
    let active = true;
    const { search, center: parsedCenter } = parseParams(new URLSearchParams(key));
    setCenter(parsedCenter);
    setStatus("loading");

    searchBusinesses(search)
      .then((results) => {
        if (active) {
          setBusinesses(results);
          setStatus("success");
        }
      })
      .catch((error) => {
        if (active) {
          logError(error, { context: "search" });
          setStatus("error");
        }
      });

    return () => {
      active = false;
    };
  }, [key]);

  return (
    <div>
      <SearchForm />
      <section className="results">
        <h2 className="results__header">Results</h2>
        <SearchResults status={status} businesses={businesses} center={center} />
      </section>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<p className="results__state">Loading…</p>}>
      <SearchView />
    </Suspense>
  );
}
