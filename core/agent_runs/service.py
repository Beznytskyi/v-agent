from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .models import AgentRun


class AgentRunService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start(self, agent_name: str, objective: str, input_: dict | None = None, context: dict | None = None) -> AgentRun:
        run = AgentRun(
            agent_name=agent_name,
            objective=objective,
            input=input_ or {},
            context=context or {},
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def complete(self, run_id: UUID, result: dict) -> AgentRun:
        run = await self.session.get(AgentRun, run_id)
        if run is None:
            raise ValueError(f"Agent run {run_id} not found")
        run.status = "completed"
        run.result = result
        run.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return run

    async def fail(self, run_id: UUID, error: str) -> AgentRun:
        run = await self.session.get(AgentRun, run_id)
        if run is None:
            raise ValueError(f"Agent run {run_id} not found")
        run.status = "failed"
        run.error = error
        run.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return run
