from sqlalchemy import Column, String, Text, Enum as SAEnum, DateTime, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid, enum
from datetime import datetime
from app.database import Base

class AgentRole(str, enum.Enum):
    ORCHESTRATOR = "ORCHESTRATOR"
    RESEARCHER = "RESEARCHER"
    ANALYST = "ANALYST"
    WRITER = "WRITER"
    REVIEWER = "REVIEWER"
    CODER = "CODER"

class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentDefinition(Base):
    __tablename__ = "agent_definitions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    role = Column(SAEnum(AgentRole), nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text)
    model = Column(String, default="claude-3-5-sonnet-20241022")
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    agent_ids = Column(JSON, default=list)
    process_type = Column(String, default="sequential")
    hitl_enabled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SAEnum(RunStatus), default=RunStatus.PENDING, nullable=False)
    input_task = Column(Text, nullable=False)
    output_result = Column(Text)
    total_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    execution_log = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
