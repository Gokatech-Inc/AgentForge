from typing import List
import anthropic
from app.core.config import settings


def run_crew_workflow(agents: list, task: str) -> dict:
    """Execute agents as a CrewAI-style hierarchical crew."""
    if not agents:
        return {"status": "FAILED", "error": "No agents defined"}

    orchestrator = next((a for a in agents if a["role"] == "ORCHESTRATOR"), agents[0])
    workers = [a for a in agents if a != orchestrator]

    execution_log = []
    total_tokens = 0
    total_cost = 0.0

    subtasks = _decompose_task(orchestrator, task)
    execution_log.append({"phase": "decomposition", "subtasks": subtasks, "agent": orchestrator["name"]})

    worker_results = []
    for i, subtask in enumerate(subtasks):
        agent = workers[i % len(workers)] if workers else orchestrator
        result = _invoke_agent(agent, subtask, "")
        total_tokens += result.get("tokens", 0)
        total_cost += result.get("cost", 0.0)
        worker_results.append({"agent": agent["name"], "subtask": subtask, "output": result["output"]})
        execution_log.append({"phase": "execution", **worker_results[-1]})

    synthesis_context = "\n\n".join(f"[{r['agent']}]: {r['output']}" for r in worker_results)
    final = _invoke_agent(orchestrator, f"Synthesize the following worker outputs into a final answer for: {task}", synthesis_context)
    total_tokens += final.get("tokens", 0)
    total_cost += final.get("cost", 0.0)
    execution_log.append({"phase": "synthesis", "agent": orchestrator["name"], "output": final["output"]})

    return {
        "status": "COMPLETED",
        "final_output": final["output"],
        "agent_outputs": worker_results,
        "execution_log": execution_log,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6),
    }


def _decompose_task(orchestrator: dict, task: str) -> List[str]:
    result = _invoke_agent(
        orchestrator,
        f"Decompose this task into 2-4 specific subtasks for team members: {task}. Return only a numbered list.",
        "",
    )
    lines = [l.strip().lstrip("1234. ") for l in result["output"].split("\n") if l.strip() and l.strip()[0].isdigit()]
    return lines[:4] if lines else [task]


def _invoke_agent(agent: dict, task: str, context: str) -> dict:
    if not settings.ANTHROPIC_API_KEY:
        return {"output": f"[{agent['role']}] Simulated: {task[:80]}", "tokens": 0, "cost": 0.0}
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = f"Role: {agent['role']}\nGoal: {agent['goal']}\nTask: {task}"
    if context:
        prompt += f"\nContext:\n{context}"
    msg = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=800, messages=[{"role": "user", "content": prompt}])
    tokens = msg.usage.input_tokens + msg.usage.output_tokens
    return {"output": msg.content[0].text, "tokens": tokens, "cost": (msg.usage.input_tokens * 3 + msg.usage.output_tokens * 15) / 1_000_000}
