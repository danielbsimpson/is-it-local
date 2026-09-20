"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import { config } from "@/lib/config";

interface BusinessMapProps {
  lat: number;
  lon: number;
  name: string;
}

// A CSS-only marker avoids bundling Leaflet's default image assets.
const markerIcon = L.divIcon({
  className: "map-marker",
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

export default function BusinessMap({ lat, lon, name }: BusinessMapProps) {
  return (
    <MapContainer
      center={[lat, lon]}
      zoom={15}
      scrollWheelZoom={false}
      className="business-map"
      aria-label={`Map showing the location of ${name}`}
    >
      <TileLayer
        url={config.mapTileUrl}
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={[lat, lon]} icon={markerIcon}>
        <Popup>{name}</Popup>
      </Marker>
    </MapContainer>
  );
}
