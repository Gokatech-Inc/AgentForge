import time
from typing import TypedDict, List, Optional
import anthropic
from app.core.config import settings

class AgentState(TypedDict):
    task: str
    agent_outputs: List[dict]
    current_step: int
    status: str
    final_output: Optional[str]
    total_tokens: int
    total_cost: float


def _call_claude(role: str, goal: str, task: str, context: str = "") -> dict:
    if not settings.ANTHROPIC_API_KEY:
        return {"output": f"[{role}] Simulated response for: {task}", "tokens": 0, "cost": 0.0}

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = (
        f"You are a {role} agent. Your goal: {goal}\n\n"
        f"Task: {task}\n"
        + (f"\nContext from previous agents:\n{context}" if context else "")
        + "\n\nComplete your assigned task thoroughly."
    )
    start = time.time()
    msg = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    input_tokens = msg.usage.input_tokens
    output_tokens = msg.usage.output_tokens
    cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000

    return {
        "output": msg.content[0].text,
        "tokens": input_tokens + output_tokens,
        "cost": cost,
        "duration_ms": round((time.time() - start) * 1000),
    }


def run_sequential_workflow(agents: list, task: str) -> dict:
    state: AgentState = {
        "task": task,
        "agent_outputs": [],
        "current_step": 0,
        "status": "RUNNING",
        "final_output": None,
        "total_tokens": 0,
        "total_cost": 0.0,
    }

    context = ""
    for agent in agents:
        for attempt in range(settings.MAX_AGENT_RETRIES):
            try:
                result = _call_claude(agent["role"], agent["goal"], task, context)
                state["agent_outputs"].append({
                    "agent_name": agent["name"],
                    "role": agent["role"],
                    "output": result["output"],
                    "tokens": result["tokens"],
                    "cost": result["cost"],
                    "duration_ms": result.get("duration_ms", 0),
                    "attempt": attempt + 1,
                })
                state["total_tokens"] += result["tokens"]
                state["total_cost"] += result["cost"]
                context = result["output"]
                state["current_step"] += 1
                break
            except Exception as e:
                if attempt == settings.MAX_AGENT_RETRIES - 1:
                    state["agent_outputs"].append({"agent_name": agent["name"], "error": str(e), "attempt": attempt + 1})
                    state["status"] = "FAILED"
                    return state

    state["final_output"] = context
    state["status"] = "COMPLETED"
    return state
