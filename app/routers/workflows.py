from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.agent import WorkflowDefinition, WorkflowRun, AgentDefinition, RunStatus
from app.services.langgraph_service import run_sequential_workflow
from app.services.crewai_service import run_crew_workflow
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_ids: List[str]
    process_type: str = "sequential"
    hitl_enabled: bool = False

class TriggerRequest(BaseModel):
    task: str

@router.post("", status_code=201)
async def create_workflow(req: WorkflowCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    wf = WorkflowDefinition(**{**req.model_dump(), "hitl_enabled": int(req.hitl_enabled)})
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return wf

@router.get("")
async def list_workflows(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return (await db.execute(select(WorkflowDefinition))).scalars().all()

@router.post("/{workflow_id}/trigger", status_code=201)
async def trigger_workflow(workflow_id: str, req: TriggerRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    wf = (await db.execute(select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id))).scalar_one_or_none()
    if not wf:
        raise HTTPException(404, "Workflow not found")

    agents_data = []
    for aid in (wf.agent_ids or []):
        a = (await db.execute(select(AgentDefinition).where(AgentDefinition.id == aid))).scalar_one_or_none()
        if a:
            agents_data.append({"name": a.name, "role": a.role.value, "goal": a.goal})

    run = WorkflowRun(workflow_id=workflow_id, input_task=req.task, status=RunStatus.RUNNING)
    db.add(run)
    await db.commit()

    try:
        if wf.process_type == "crew":
            result = run_crew_workflow(agents_data, req.task)
        else:
            result = run_sequential_workflow(agents_data, req.task)

        run.status = RunStatus.COMPLETED if result["status"] == "COMPLETED" else RunStatus.FAILED
        run.output_result = result.get("final_output", "")
        run.total_tokens = result.get("total_tokens", 0)
        run.total_cost_usd = result.get("total_cost", 0.0)
        run.execution_log = result.get("agent_outputs", [])
        run.completed_at = datetime.utcnow()
    except Exception as e:
        run.status = RunStatus.FAILED
        run.execution_log = [{"error": str(e)}]

    await db.commit()
    await db.refresh(run)
    return run
