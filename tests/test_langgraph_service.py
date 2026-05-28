import pytest
from app.services.langgraph_service import run_sequential_workflow

def test_sequential_workflow_no_agents():
    result = run_sequential_workflow([], "Do something")
    assert result["status"] == "COMPLETED"
    assert result["total_tokens"] == 0

def test_sequential_workflow_simulated():
    agents = [
        {"name": "Researcher", "role": "RESEARCHER", "goal": "Research the topic"},
        {"name": "Writer", "role": "WRITER", "goal": "Write a summary"},
    ]
    result = run_sequential_workflow(agents, "Summarize AI trends")
    assert result["status"] == "COMPLETED"
    assert len(result["agent_outputs"]) == 2
    assert result["current_step"] == 2

def test_state_tracks_steps():
    agents = [{"name": "A1", "role": "ANALYST", "goal": "Analyze data"}]
    result = run_sequential_workflow(agents, "Analyze sales data")
    assert result["current_step"] == 1
    assert result["agent_outputs"][0]["agent_name"] == "A1"
