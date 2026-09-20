"""Evaluation harness measuring classification accuracy against labeled fixtures.

Run against the local llama.cpp server configured in the environment::

    python -m eval.run_eval

Each line in ``fixtures.jsonl`` provides a business, its evidence sources, and the
expected classification. The harness reports overall accuracy plus per-class precision
and recall so classifier changes can be compared over time.
"""

from __future__ import annotations

import argparse
import json
import uuid
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from enrichment.config import settings
from enrichment.llm_classifier import build_llm_client, classify
from enrichment.models import (
    CLASSIFICATIONS,
    BusinessRef,
    ClassificationResult,
    SourceCandidate,
)

FIXTURES_PATH = Path(__file__).with_name("fixtures.jsonl")

Classifier = Callable[[BusinessRef, list[SourceCandidate]], ClassificationResult]


def load_fixtures(path: Path = FIXTURES_PATH) -> list[dict]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _to_inputs(fixture: dict) -> tuple[BusinessRef, list[SourceCandidate]]:
    business = BusinessRef(
        id=uuid.uuid4(),
        name=fixture["name"],
        categories=fixture.get("categories"),
        brand=fixture.get("brand"),
        parent_company=fixture.get("parent_company"),
        address=fixture.get("address"),
    )
    sources = [
        SourceCandidate(url=source["url"], snippet=source.get("snippet"))
        for source in fixture.get("sources", [])
    ]
    return business, sources


def evaluate(classifier: Classifier, fixtures: list[dict]) -> dict:
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)
    correct = 0

    for fixture in fixtures:
        business, sources = _to_inputs(fixture)
        expected = fixture["expected"]
        predicted = classifier(business, sources).classification
        if predicted == expected:
            correct += 1
            tp[expected] += 1
        else:
            fp[predicted] += 1
            fn[expected] += 1

    per_class = {}
    for label in CLASSIFICATIONS:
        precision_denom = tp[label] + fp[label]
        recall_denom = tp[label] + fn[label]
        per_class[label] = {
            "precision": tp[label] / precision_denom if precision_denom else None,
            "recall": tp[label] / recall_denom if recall_denom else None,
            "support": tp[label] + fn[label],
        }

    return {
        "accuracy": correct / len(fixtures) if fixtures else 0.0,
        "count": len(fixtures),
        "per_class": per_class,
    }


def _print_report(report: dict) -> None:
    print(f"Accuracy: {report['accuracy']:.3f} over {report['count']} fixture(s)")
    print(f"{'class':<16} {'precision':>10} {'recall':>10} {'support':>8}")
    for label, metrics in report["per_class"].items():
        if metrics["support"] == 0:
            continue
        precision = "n/a" if metrics["precision"] is None else f"{metrics['precision']:.3f}"
        recall = "n/a" if metrics["recall"] is None else f"{metrics['recall']:.3f}"
        print(f"{label:<16} {precision:>10} {recall:>10} {metrics['support']:>8}")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description="Evaluate ownership classification accuracy.").parse_args(
        argv
    )
    fixtures = load_fixtures()
    llm_client = build_llm_client(settings.llm_base_url)

    def classifier(business: BusinessRef, sources: list[SourceCandidate]) -> ClassificationResult:
        return classify(business, sources, client=llm_client, model=settings.llm_model)

    _print_report(evaluate(classifier, fixtures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
