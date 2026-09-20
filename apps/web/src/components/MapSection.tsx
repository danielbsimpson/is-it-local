"use client";

import dynamic from "next/dynamic";

// Leaflet touches `window`, so the map is loaded client-side only.
const BusinessMap = dynamic(() => import("@/components/BusinessMap"), {
  ssr: false,
  loading: () => <div className="business-map" aria-hidden="true" />,
});

interface MapSectionProps {
  lat: number;
  lon: number;
  name: string;
}

export function MapSection({ lat, lon, name }: MapSectionProps) {
  return <BusinessMap lat={lat} lon={lon} name={name} />;
}
