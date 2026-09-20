"""CLI to enrich businesses that lack an ownership classification.

Example::

    python -m enrichment.cli --limit 25
"""

from __future__ import annotations

import argparse
import functools
import sys

from sqlalchemy import create_engine

from enrichment.config import settings
from enrichment.guardrails import RateLimiter
from enrichment.llm_classifier import build_llm_client, classify
from enrichment.pipeline import EnrichmentPipeline
from enrichment.repository import SqlAlchemyEnrichmentRepository
from enrichment.search_client import SearxngSearchClient


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enrich businesses lacking an ownership classification."
    )
    parser.add_argument(
        "--limit", type=int, default=25, help="Maximum number of businesses to enrich."
    )
    parser.add_argument(
        "--max-results", type=int, default=5, help="Maximum search sources per business."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    repository = SqlAlchemyEnrichmentRepository(engine)
    search_client = SearxngSearchClient(settings.searxng_base_url)
    llm_client = build_llm_client(settings.llm_base_url)
    classifier = functools.partial(classify, client=llm_client, model=settings.llm_model)
    rate_limiter = RateLimiter(settings.provider_rate_limit_per_min)

    pipeline = EnrichmentPipeline(
        repository=repository,
        search_client=search_client,
        classifier=classifier,
        rate_limiter=rate_limiter,
        max_results=args.max_results,
    )

    results = pipeline.run(args.limit)
    print(f"Enriched {len(results)} business(es).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
