import { CLASSIFICATION_COLORS, CLASSIFICATION_LABELS } from "@/lib/classification";
import type { OwnershipClassification } from "@/types";

interface ClassificationBadgeProps {
  classification: OwnershipClassification;
}

export function ClassificationBadge({ classification }: ClassificationBadgeProps) {
  const color = CLASSIFICATION_COLORS[classification];
  const label = CLASSIFICATION_LABELS[classification];
  return (
    <span
      className="badge"
      style={{ backgroundColor: color }}
      data-classification={classification}
      data-testid="classification-badge"
    >
      {label}
    </span>
  );
}
