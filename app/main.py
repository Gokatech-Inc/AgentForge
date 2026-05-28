from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import auth, agents, workflows, runs

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="AgentForge", description="Enterprise Multi-Agent AI Automation Platform", version="1.0.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(runs.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AgentForge"}
