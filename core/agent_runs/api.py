from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.agent_runs.models import AgentRun
from core.agent_runs.service import AgentRunService
from core.orchestrator.protocol import AgentContext
from core.orchestrator.service import Orchestrator
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
    try:
        context = AgentContext(
            objective=request.objective,
            input=request.input,
            memory=request.context.get("memory", {}),
            constraints=request.context.get("constraints", {}),
        )
        result = await Orchestrator().run(request.agent_name, context)
        payload = {
            "status": result.status,
            "summary": result.summary,
            "findings": result.findings,
            "actions": result.actions,
            "recommendations": result.recommendations,
            "memory_updates": result.memory_updates,
            "requires_approval": result.requires_approval,
        }
        await service.complete(run.id, payload)
    except ValueError as exc:
        await service.fail(run.id, str(exc))
        await session.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        await service.fail(run.id, str(exc))
        await session.commit()
        raise HTTPException(status_code=500, detail="Agent execution failed") from exc

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
