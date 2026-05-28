import pytest
from app.services.crewai_service import run_crew_workflow, _decompose_task

def test_crew_workflow_empty_agents():
    result = run_crew_workflow([], "Task")
    assert result["status"] == "FAILED"

def test_crew_workflow_single_agent():
    agents = [{"name": "Orchestrator", "role": "ORCHESTRATOR", "goal": "Manage the team"}]
    result = run_crew_workflow(agents, "Write a market report")
    assert result["status"] == "COMPLETED"
    assert "final_output" in result

def test_crew_workflow_multi_agent():
    agents = [
        {"name": "Orchestrator", "role": "ORCHESTRATOR", "goal": "Coordinate"},
        {"name": "Researcher", "role": "RESEARCHER", "goal": "Research"},
        {"name": "Writer", "role": "WRITER", "goal": "Write"},
    ]
    result = run_crew_workflow(agents, "Produce a competitive analysis")
    assert result["status"] == "COMPLETED"
    assert result["total_tokens"] == 0
