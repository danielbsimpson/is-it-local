import { ClassificationBadge } from "@/components/ClassificationBadge";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import type { BusinessDetail } from "@/types";

interface BusinessDetailViewProps {
  detail: BusinessDetail;
}

function formatAddress(detail: BusinessDetail): string | null {
  const address = detail.business.address;
  if (!address) {
    return null;
  }
  const parts = [
    address.street,
    address.city,
    address.region,
    address.postal_code,
    address.country,
  ].filter(Boolean);
  return parts.length ? parts.join(", ") : null;
}

export function BusinessDetailView({ detail }: BusinessDetailViewProps) {
  const { business, classification, sources } = detail;
  const address = formatAddress(detail);

  return (
    <article className="detail">
      <header className="detail__header">
        <h1 className="detail__name">{business.name}</h1>
        {classification ? (
          <ClassificationBadge classification={classification.classification} />
        ) : (
          <span className="badge badge--muted">Not yet classified</span>
        )}
      </header>

      {address ? <p className="detail__address">{address}</p> : null}
      {business.categories?.length ? (
        <p className="detail__categories">{business.categories.join(" · ")}</p>
      ) : null}

      {classification ? (
        <section className="detail__section" aria-label="Classification confidence">
          <ConfidenceMeter value={classification.confidence} />
        </section>
      ) : null}

      <section className="detail__section" aria-label="Sources">
        <h2 className="detail__subtitle">Sources</h2>
        {sources.length ? (
          <ul className="detail__sources">
            {sources.map((source) => (
              <li key={source.id}>
                <a href={source.url} target="_blank" rel="noopener noreferrer">
                  {source.snippet ? source.snippet : source.url}
                </a>
                <span className="detail__source-provider"> — {source.provider}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="detail__empty">No sources cited yet.</p>
        )}
      </section>
    </article>
  );
}
