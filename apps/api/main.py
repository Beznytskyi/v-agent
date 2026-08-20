from fastapi import FastAPI

from core.agent_runs.api import router as agent_router

app = FastAPI(title="V-Agent API", version="0.1.0")
app.include_router(agent_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "v-agent-api"}
