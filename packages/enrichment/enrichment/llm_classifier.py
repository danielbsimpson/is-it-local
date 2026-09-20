"""Ownership classification using a local llama.cpp OpenAI-compatible server."""

from __future__ import annotations

import json
import uuid
from typing import Any, Protocol

from enrichment.models import (
    CLASSIFICATIONS,
    BusinessRef,
    ClassificationResult,
    SourceCandidate,
)

_SYSTEM_PROMPT = (
    "You classify the ownership structure of a business using only the provided "
    "evidence. Respond with a single JSON object and nothing else, using the keys "
    '"classification", "confidence", and "cited_source_ids". '
    f'"classification" must be exactly one of: {", ".join(CLASSIFICATIONS)}. '
    '"confidence" is a number from 0.0 to 1.0. '
    '"cited_source_ids" is a list of the source id strings that support your answer. '
    'If the evidence is insufficient or conflicting, use "unknown" with low confidence.'
)


class ChatClient(Protocol):
    """The subset of the OpenAI client interface the classifier depends on."""

    @property
    def chat(self) -> Any: ...


def build_prompt(business: BusinessRef, sources: list[SourceCandidate]) -> str:
    lines = [f"Business name: {business.name}"]
    if business.categories:
        lines.append(f"Categories: {', '.join(business.categories)}")
    if business.brand:
        lines.append(f"Brand: {business.brand}")
    if business.parent_company:
        lines.append(f"Parent company: {business.parent_company}")
    if business.address:
        lines.append(f"Address: {json.dumps(business.address)}")

    lines.append("\nEvidence sources:")
    if sources:
        for source in sources:
            snippet = (source.snippet or "").strip()
            lines.append(f"- id={source.id} url={source.url}\n  {snippet}")
    else:
        lines.append("- (no sources found)")

    lines.append("\nReturn the JSON classification object based only on the evidence above.")
    return "\n".join(lines)


def _parse_response(content: str, sources: list[SourceCandidate]) -> ClassificationResult:
    known_ids = {str(source.id) for source in sources}
    data = _extract_json(content)

    classification = str(data.get("classification", "unknown")).strip().lower()
    if classification not in CLASSIFICATIONS:
        classification = "unknown"

    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = min(1.0, max(0.0, confidence))

    cited: list[uuid.UUID] = []
    for raw_id in data.get("cited_source_ids", []) or []:
        candidate = str(raw_id)
        if candidate in known_ids:
            cited.append(uuid.UUID(candidate))

    if classification == "unknown":
        confidence = min(confidence, 0.5)

    return ClassificationResult(
        classification=classification, confidence=confidence, cited_source_ids=cited
    )


def _extract_json(content: str) -> dict:
    content = content.strip()
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {}
    try:
        return json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return {}


def classify(
    business: BusinessRef,
    sources: list[SourceCandidate],
    *,
    client: ChatClient,
    model: str,
) -> ClassificationResult:
    """Classify ``business`` ownership from ``sources`` using the local LLM."""
    prompt = build_prompt(business, sources)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    content = completion.choices[0].message.content or ""
    return _parse_response(content, sources)


def build_llm_client(base_url: str, *, api_key: str = "not-needed") -> ChatClient:
    """Construct an OpenAI-compatible client pointed at the local llama.cpp server."""
    from openai import OpenAI

    return OpenAI(base_url=base_url, api_key=api_key)
