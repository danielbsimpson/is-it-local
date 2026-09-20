# Data Sources — License & Terms Compliance

This document records the licensing and terms-of-use obligations for the open data
sources ingested by the seed pipeline (`apps/api/app/providers/`). Review this before
ingesting or redistributing enriched data.

## OpenStreetMap (Overpass API)

- **License:** [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
- **Attribution:** Any product using OSM data must credit "© OpenStreetMap contributors"
  and link to <https://www.openstreetmap.org/copyright>.
- **Share-Alike:** ODbL is a copyleft/share-alike license. If we publicly distribute a
  *derived database* built from OSM data, that derived database must also be offered
  under ODbL. Producing and displaying individual results ("produced works") does not
  trigger share-alike, but redistributing the underlying enriched dataset can.
- **Overpass API usage:** The public Overpass endpoints
  (`https://overpass-api.de/api/interpreter`) are shared community infrastructure with
  a [usage policy](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html).
  Keep queries small (bounded by `--bbox`), avoid parallel bulk requests, and prefer a
  self-hosted Overpass or planet extract for large ingests. `OVERPASS_URL` is
  configurable so we can point at a local instance.

## Overture Maps

- **License:** Overture place data is released under
  [CDLA-Permissive 2.0](https://cdla.dev/permissive-2-0/) (data) with schema/docs under
  other permissive terms. Overture places incorporate data derived from OpenStreetMap;
  records sourced from OSM remain subject to **ODbL** attribution/share-alike, indicated
  by each feature's `sources`/`theme` provenance.
- **Attribution:** Credit "© Overture Maps Foundation" and preserve OSM attribution for
  OSM-derived records.
- **Distribution format:** Official Overture data is published as GeoParquet on cloud
  object storage. For the local-first PoC, `OvertureProvider` reads a **local** GeoJSON
  or newline-delimited JSON export (`OVERTURE_DATA_PATH`), so no cloud egress or account
  is required.

## Practical guidance for this project

- Always display attribution for OpenStreetMap and Overture in any UI that surfaces
  seeded business data (web app, future mobile app).
- Treat the seeded catalog as ODbL-encumbered: if we ever publish the raw/enriched
  database, publish it under ODbL and document provenance per record via the `provider`
  and `provider_place_id` columns.
- Enrichment outputs (LLM classifications, cited web sources) are stored separately from
  the seed catalog so their licensing can be reasoned about independently.
- Re-verify these terms before any public deployment; provider terms change over time.
