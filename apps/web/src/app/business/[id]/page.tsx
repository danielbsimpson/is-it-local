import Link from "next/link";
import { notFound } from "next/navigation";

import { BusinessDetailView } from "@/components/BusinessDetailView";
import { MapSection } from "@/components/MapSection";
import { ApiError, getBusiness } from "@/lib/api-client";
import type { BusinessDetail } from "@/types";

interface BusinessPageProps {
  params: { id: string };
}

export default async function BusinessPage({ params }: BusinessPageProps) {
  let detail: BusinessDetail;
  try {
    detail = await getBusiness(params.id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const [lon, lat] = detail.business.location.coordinates;

  return (
    <div>
      <Link href="/search" className="detail__back">
        &larr; Back to results
      </Link>
      <BusinessDetailView detail={detail} />
      <section className="detail__section" aria-label="Location map">
        <MapSection lat={lat} lon={lon} name={detail.business.name} />
      </section>
    </div>
  );
}
