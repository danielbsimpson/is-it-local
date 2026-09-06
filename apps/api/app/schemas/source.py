"""Source (evidence) response schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    url: str
    retrieved_at: datetime
    snippet: str | None = None
