from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.agent import AgentDefinition, AgentRole
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

class AgentCreate(BaseModel):
    name: str
    role: AgentRole
    goal: str
    backstory: Optional[str] = None
    model: str = "claude-3-5-sonnet-20241022"

@router.post("", status_code=201)
async def create_agent(req: AgentCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    agent = AgentDefinition(**req.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("")
async def list_agents(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return (await db.execute(select(AgentDefinition))).scalars().all()
