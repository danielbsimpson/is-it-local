import { BusinessCard } from "@/components/BusinessCard";
import { distanceToBusiness } from "@/lib/distance";
import type { Business, Center } from "@/types";

export type SearchStatus = "loading" | "error" | "success";

interface SearchResultsProps {
  status: SearchStatus;
  businesses: Business[];
  center?: Center | null;
}

export function SearchResults({ status, businesses, center = null }: SearchResultsProps) {
  if (status === "loading") {
    return (
      <p className="results__state" role="status">
        Searching businesses…
      </p>
    );
  }

  if (status === "error") {
    return (
      <p className="results__state results__state--error" role="alert">
        Something went wrong loading results. Please try again.
      </p>
    );
  }

  if (!businesses.length) {
    return (
      <p className="results__state" role="status">
        No businesses matched your search.
      </p>
    );
  }

  return (
    <ul className="results__list">
      {businesses.map((business) => (
        <BusinessCard
          key={business.id}
          business={business}
          distanceMeters={distanceToBusiness(business, center)}
        />
      ))}
    </ul>
  );
}
