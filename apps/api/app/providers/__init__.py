"""Place data providers.

Each provider implements the :class:`PlaceProvider` interface so ingestion can add
new sources without changing orchestration logic.
"""

from app.providers.base import BoundingBox, NormalizedPlace, PlaceProvider

__all__ = ["BoundingBox", "NormalizedPlace", "PlaceProvider"]
