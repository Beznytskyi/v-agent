from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import MemoryRepository


class MemoryService:
    """Application service for structured long-term memory."""

    def __init__(self, session: AsyncSession):
        self.repo = MemoryRepository(session)

    async def remember_entity(
        self,
        type_: str,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        return await self.repo.create_entity(type_, name, description, metadata)

    async def remember_fact(
        self,
        entity_id,
        attribute: str,
        value: str,
        confidence: float = 1.0,
    ):
        return await self.repo.add_fact(entity_id, attribute, value, confidence)

    async def remember_event(
        self,
        event_type: str,
        description: str,
        entity_id=None,
        occurred_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        return await self.repo.add_event(
            event_type,
            description,
            occurred_at or datetime.now(timezone.utc),
            entity_id,
            metadata=metadata,
        )

    async def recall_entities(self, query: str, limit: int = 20):
        return await self.repo.find_entities(query, limit)

    async def build_context(self, query: str, *, user_id: str) -> dict[str, Any]:
        entities = await self.recall_entities(query)
        return {
            "query": query,
            "user_id": user_id,
            "entities": [
                {"id": str(entity.id), "type": entity.type, "name": entity.name}
                for entity in entities
            ],
            "facts": [],
            "events": [],
        }

    async def record(self, item: dict[str, Any]) -> None:
        # Structured record dispatch will be expanded as additional memory types are added.
        return None
