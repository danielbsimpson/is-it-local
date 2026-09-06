# Ownership Classification Schema

Every business is assigned exactly one of six ownership categories, each with a
numeric confidence score (0.0–1.0) and a list of cited sources. This document
defines each category and the boundaries between the ones most easily confused.

## Categories

### `family_owned`

Owned and operated by a family or an individual, where ownership is intended to
stay within a family. Typically single-location or a small number of locations
run by the owners themselves.

- **Signals:** "family owned since," named founders still operating, succession
  within a family, no external/parent ownership.

### `locally_owned`

Owned by residents of the local community, so profits largely stay local. May
have more than one location, but ownership and control remain within the
community it serves.

- **Signals:** owners named as local residents, locally headquartered, no
  national brand or franchise agreement.

### `independent`

Independently owned business not tied to a national brand and not operating
under a franchise agreement. Emphasis is on **brand independence** rather than
the owner's residency.

- **Signals:** unique/standalone brand, no parent company, not part of a chain.

### `franchise`

Locally owned but operating under a national or regional brand via a franchise
agreement. The local owner controls day-to-day operations, but the brand and a
share of revenue flow to the franchisor.

- **Signals:** recognizable national brand at a single location, "independently
  owned and operated" franchise disclosures, franchisor listed as brand/parent.

### `corporate_owned`

Owned and operated directly by a large corporation or national chain. Locations
are company-operated rather than franchised.

- **Signals:** parent company operates the location directly, publicly traded or
  large private parent, company-operated store language.

### `unknown`

Insufficient or conflicting information to classify with confidence. Prefer
`unknown` with a low confidence over guessing.

- **Signals:** no ownership evidence found, contradictory sources, ambiguous
  disclosures.

## Boundary: `locally_owned` vs `independent`

These two overlap most often. Use this rule of thumb:

- **`independent`** is about the **brand**: the business is not part of a
  national chain and has no franchisor or corporate parent. It says nothing
  about where the owners live.
- **`locally_owned`** is about the **owners**: they are residents of the local
  community, so profits stay local. A locally owned business is usually also
  independent, but the distinguishing claim is local residency.

Guidance when both could apply:

| Situation                                                 | Prefer          |
| --------------------------------------------------------- | --------------- |
| Standalone brand, owner residency unknown                 | `independent`   |
| Standalone brand, owners confirmed local residents        | `locally_owned` |
| Owners local but operate under a national brand/franchise | `franchise`     |
| Standalone brand owned by an out-of-area investor group   | `independent`   |

When evidence supports both and residency is confirmed, `locally_owned` is the
more specific (and more useful) classification. When residency cannot be
established, fall back to `independent`.

## Confidence and sources

- `confidence` reflects how strongly the evidence supports the chosen category,
  from 0.0 (no support) to 1.0 (certain).
- `sources` cite the evidence used. A classification without sources should
  carry low confidence.
- Community submissions can raise confidence or change the category once
  reviewed and approved.
