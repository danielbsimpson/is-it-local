import Link from "next/link";

import { ClassificationBadge } from "@/components/ClassificationBadge";
import { formatDistance } from "@/lib/distance";
import type { Business, OwnershipClassification } from "@/types";

interface BusinessCardProps {
  business: Business;
  distanceMeters?: number | null;
  classification?: OwnershipClassification | null;
}

function formatAddress(business: Business): string | null {
  const address = business.address;
  if (!address) {
    return null;
  }
  const parts = [address.street, address.city, address.region, address.postal_code].filter(
    Boolean,
  );
  return parts.length ? parts.join(", ") : null;
}

export function BusinessCard({ business, distanceMeters, classification }: BusinessCardProps) {
  const address = formatAddress(business);
  return (
    <li className="business-card">
      <Link href={`/business/${business.id}`} className="business-card__link">
        <div className="business-card__header">
          <h3 className="business-card__name">{business.name}</h3>
          {classification ? <ClassificationBadge classification={classification} /> : null}
        </div>
        {address ? <p className="business-card__address">{address}</p> : null}
        {business.categories?.length ? (
          <p className="business-card__categories">{business.categories.join(" · ")}</p>
        ) : null}
        {distanceMeters != null ? (
          <p className="business-card__distance">{formatDistance(distanceMeters)} away</p>
        ) : null}
      </Link>
    </li>
  );
}
