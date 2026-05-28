from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.agent import WorkflowRun
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])

@router.get("")
async def list_runs(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return (await db.execute(select(WorkflowRun).order_by(WorkflowRun.created_at.desc()).limit(50))).scalars().all()

@router.get("/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    run = (await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))).scalar_one_or_none()
    if not run:
        raise HTTPException(404, "Run not found")
    return run

@router.get("/{run_id}/cost")
async def get_cost(run_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    run = (await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))).scalar_one_or_none()
    if not run:
        raise HTTPException(404, "Run not found")
    return {"run_id": run_id, "total_tokens": run.total_tokens, "total_cost_usd": run.total_cost_usd, "status": run.status}
