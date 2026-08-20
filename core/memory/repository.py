from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Decision, Entity, Event, Fact


class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_entity(self, type_: str, name: str, description: str | None = None, metadata: dict | None = None) -> Entity:
        entity = Entity(type=type_, name=name, description=description, metadata_=metadata or {})
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def add_fact(self, entity_id: UUID, attribute: str, value: str, confidence: float = 1.0, source_id: UUID | None = None) -> Fact:
        fact = Fact(entity_id=entity_id, attribute=attribute, value=value, confidence=confidence, source_id=source_id)
        self.session.add(fact)
        await self.session.flush()
        return fact

    async def add_event(self, event_type: str, description: str, occurred_at: datetime, entity_id: UUID | None = None, source_id: UUID | None = None, metadata: dict | None = None) -> Event:
        event = Event(event_type=event_type, description=description, occurred_at=occurred_at, entity_id=entity_id, source_id=source_id, metadata_=metadata or {})
        self.session.add(event)
        await self.session.flush()
        return event

    async def add_decision(self, decision: str, decided_at: datetime, reason: str | None = None, decision_maker: str | None = None) -> Decision:
        item = Decision(decision=decision, decided_at=decided_at, reason=reason, decision_maker=decision_maker)
        self.session.add(item)
        await self.session.flush()
        return item

    async def find_entities(self, query: str, limit: int = 20) -> list[Entity]:
        result = await self.session.execute(select(Entity).where(Entity.name.ilike(f"%{query}%")).limit(limit))
        return list(result.scalars())
