from typing import Any


class MemoryService:
    """Memory abstraction. Persistence and vector retrieval will be implemented next."""

    async def build_context(self, query: str, *, user_id: str) -> dict[str, Any]:
        return {"query": query, "user_id": user_id, "facts": [], "events": [], "entities": []}

    async def record(self, item: dict[str, Any]) -> None:
        # Persistence is intentionally deferred to the database layer.
        return None
