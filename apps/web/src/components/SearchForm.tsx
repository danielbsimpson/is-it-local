"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { currentPosition, geocode } from "@/lib/geocode";
import { logEvent } from "@/lib/logger";

const RADIUS_OPTIONS = [
  { label: "1 km", value: 1000 },
  { label: "5 km", value: 5000 },
  { label: "10 km", value: 10000 },
  { label: "25 km", value: 25000 },
];

export function SearchForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [radiusM, setRadiusM] = useState(5000);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  async function resolveCenter(): Promise<{ lat: number; lon: number } | null> {
    if (!location.trim()) {
      return null;
    }
    return geocode(location);
  }

  function navigate(params: URLSearchParams) {
    router.push(`/search?${params.toString()}`);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      const params = new URLSearchParams();
      if (name.trim()) {
        params.set("name", name.trim());
      }
      const center = await resolveCenter();
      if (center) {
        params.set("lat", String(center.lat));
        params.set("lon", String(center.lon));
        params.set("radius_m", String(radiusM));
      } else if (location.trim()) {
        setNotice("Could not find that location; showing name matches instead.");
      }
      if (![...params.keys()].length) {
        setNotice("Enter a business name or a location to search.");
        return;
      }
      logEvent("search_submitted", { hasName: params.has("name"), hasLocation: params.has("lat") });
      navigate(params);
    } finally {
      setBusy(false);
    }
  }

  async function handleUseMyLocation() {
    setBusy(true);
    setNotice(null);
    try {
      const center = await currentPosition();
      if (!center) {
        setNotice("Location access is unavailable. Try typing a place name.");
        return;
      }
      const params = new URLSearchParams();
      if (name.trim()) {
        params.set("name", name.trim());
      }
      params.set("lat", String(center.lat));
      params.set("lon", String(center.lon));
      params.set("radius_m", String(radiusM));
      logEvent("search_geolocation", {});
      navigate(params);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="search-form__row">
        <label className="field">
          <span>Business name</span>
          <input
            type="text"
            name="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="e.g. Corner Bakery"
            autoComplete="off"
          />
        </label>
        <label className="field">
          <span>Location</span>
          <input
            type="text"
            name="location"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="City, address, or ZIP"
            autoComplete="off"
          />
        </label>
        <label className="field field--narrow">
          <span>Radius</span>
          <select
            name="radius"
            value={radiusM}
            onChange={(event) => setRadiusM(Number(event.target.value))}
          >
            {RADIUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="search-form__actions">
        <button type="submit" className="button button--primary" disabled={busy}>
          {busy ? "Searching…" : "Search"}
        </button>
        <button
          type="button"
          className="button"
          onClick={handleUseMyLocation}
          disabled={busy}
        >
          Use my location
        </button>
      </div>
      {notice ? (
        <p className="search-form__notice" role="status">
          {notice}
        </p>
      ) : null}
    </form>
  );
}
