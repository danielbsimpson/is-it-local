interface ConfidenceMeterProps {
  /** Confidence in the range 0.0–1.0. */
  value: number;
}

export function ConfidenceMeter({ value }: ConfidenceMeterProps) {
  const clamped = Math.min(1, Math.max(0, value));
  const percent = Math.round(clamped * 100);
  return (
    <div className="confidence" data-testid="confidence-meter">
      <div
        className="confidence__track"
        role="meter"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Classification confidence: ${percent}%`}
      >
        <div className="confidence__fill" style={{ width: `${percent}%` }} />
      </div>
      <span className="confidence__value">{percent}% confidence</span>
    </div>
  );
}
