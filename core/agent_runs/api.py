from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.agent_runs.service import AgentRunService
from database.session import get_session

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRunRequest(BaseModel):
    agent_name: str = Field(min_length=1, max_length=128)
    objective: str = Field(min_length=1)
    input: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    id: UUID
    agent_name: str
    objective: str
    status: str
    result: dict


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest, session: AsyncSession = Depends(get_session)):
    service = AgentRunService(session)
    run = await service.start(
        agent_name=request.agent_name,
        objective=request.objective,
        input_=request.input,
        context=request.context,
    )
    result = {
        "status": "accepted",
        "agent": request.agent_name,
        "objective": request.objective,
        "message": "Agent run created. Execution will be wired to the orchestrator in the next milestone.",
    }
    await service.complete(run.id, result)
    await session.commit()
    return AgentRunResponse(
        id=run.id,
        agent_name=run.agent_name,
        objective=run.objective,
        status=run.status,
        result=run.result,
    )


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(run_id: UUID, session: AsyncSession = Depends(get_session)):
    from core.agent_runs.models import AgentRun

    run = await session.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return AgentRunResponse(
        id=run.id,
        agent_name=run.agent_name,
        objective=run.objective,
        status=run.status,
        result=run.result,
    )
