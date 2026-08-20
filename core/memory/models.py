from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Entity(Base, TimestampMixin):
    __tablename__ = "entities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text())
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class Fact(Base, TimestampMixin):
    __tablename__ = "facts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_id: Mapped[UUID] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    attribute: Mapped[str] = mapped_column(String(128), index=True)
    value: Mapped[str] = mapped_column(Text())
    source_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(128), index=True)
    entity_id: Mapped[UUID | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"), index=True)
    description: Mapped[str] = mapped_column(Text())
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class Decision(Base, TimestampMixin):
    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision: Mapped[str] = mapped_column(Text())
    reason: Mapped[str | None] = mapped_column(Text())
    alternatives: Mapped[list] = mapped_column(JSONB, default=list)
    decision_maker: Mapped[str | None] = mapped_column(String(255))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    outcome: Mapped[str | None] = mapped_column(Text())
