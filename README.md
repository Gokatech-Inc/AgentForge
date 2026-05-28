# AgentForge — Enterprise Multi-Agent AI Automation Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=flat-square" />
  <img src="https://img.shields.io/badge/CrewAI-Multi--Agent-F97316?style=flat-square" />
  <img src="https://img.shields.io/badge/Claude_AI-Anthropic-8B5CF6?style=flat-square" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" />
</p>

> **Enterprise Multi-Agent AI Automation Platform** — define, deploy, and monitor autonomous AI agent teams using LangGraph state machines and CrewAI crew orchestration. Build workflows where specialized agents collaborate, delegate, and self-correct to solve complex business tasks end-to-end.

---

## Overview

AgentForge is the infrastructure layer for enterprise agentic AI. Instead of one-shot LLM calls, AgentForge lets you compose networks of specialized AI agents — each with a defined role, tools, and memory — that work together across multi-step tasks. Developers define workflows via REST API; operators monitor execution, cost, and accuracy in real-time. Human-in-the-loop checkpoints enable approval gates before irreversible actions.

Designed for **enterprise automation teams, AI platform engineers, and organizations** that need reliable, observable, multi-agent AI systems in production.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      AgentForge Platform                         │
│                                                                  │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Agents  │  │ Workflows  │  │   Runs   │  │    Auth      │  │
│  │   API    │  │    API     │  │   API    │  │    API       │  │
│  └────┬─────┘  └──────┬─────┘  └────┬─────┘  └──────────────┘  │
│       │               │             │                            │
│  ┌────▼───────────────▼─────────────▼──────────────────────┐    │
│  │               Orchestration Layer                        │    │
│  │                                                          │    │
│  │  ┌────────────────────┐    ┌────────────────────────┐   │    │
│  │  │  LangGraph Engine  │    │   CrewAI Crew Runner   │   │    │
│  │  │  State Machine     │    │   Role-Based Agents    │   │    │
│  │  │  Conditional Edges │    │   Delegation + Memory  │   │    │
│  │  └────────┬───────────┘    └───────────┬────────────┘   │    │
│  └───────────┼────────────────────────────┼────────────────┘    │
│              └──────────────┬─────────────┘                     │
│                             ▼                                    │
│                 ┌────────────────────┐                          │
│                 │   Claude AI        │                          │
│                 │   (Anthropic)      │                          │
│                 └────────────────────┘                          │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │        PostgreSQL 15  ·  Redis 7 (State Cache)          │    │
│  │    agents · workflows · runs · tasks · checkpoints      │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Agent Types

| Agent Role | Capabilities | Primary Use Cases |
|---|---|---|
| **ORCHESTRATOR** | Decomposes goals, delegates to sub-agents, synthesizes results | Complex multi-step task routing |
| **RESEARCHER** | Web search, document retrieval, knowledge synthesis | Market research, due diligence, fact-checking |
| **ANALYST** | Data analysis, pattern recognition, trend identification | Financial analysis, risk assessment |
| **WRITER** | Content generation, summarization, report drafting | Reports, emails, proposals |
| **REVIEWER** | Quality checking, fact verification, feedback | Output validation, compliance checking |
| **CODER** | Code generation, debugging, documentation | Software engineering, automation scripts |

---

## Features

### 1. LangGraph State Machine Orchestration
Define complex agent workflows as directed state graphs. Nodes represent agent actions; edges define conditional transitions based on agent output. Supports cycles, parallel branches, and conditional routing — enabling sophisticated reasoning loops and error recovery.

### 2. CrewAI Multi-Agent Crew Execution
Deploy crews of agents with defined roles, backstories, and goals. Agents share a collective memory and can delegate sub-tasks to each other. CrewAI's sequential and hierarchical process modes handle both linear pipelines and dynamic task assignment.

### 3. Human-in-the-Loop Checkpoints
Insert approval gates at any workflow node. Execution pauses, the current state is persisted in Redis, and an operator receives a notification. Resume with approval or rejection via the `/runs/{id}/resume` endpoint.

### 4. Cost & Token Tracking
Every agent run tracks input/output tokens, cost (at current Claude pricing), and wall-clock latency per agent step. Real-time cost dashboard per workflow and per run.

### 5. Fault Tolerance & Retry
Configurable retry policies with exponential backoff per workflow step. Failed agent calls are retried up to N times; persistent failures trigger the fallback branch or escalate to the REVIEWER agent.

### 6. Full Execution Audit Trail
Every workflow run generates a complete execution log: agent called, input prompt, output, token count, cost, duration, and pass/fail status. Queryable via the Runs API for debugging and compliance.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register user |
| POST | `/api/v1/auth/login` | Public | Login, receive JWT |
| POST | `/api/v1/agents` | Developer/Admin | Define a new agent |
| GET | `/api/v1/agents` | Required | List agent definitions |
| POST | `/api/v1/workflows` | Developer/Admin | Create workflow definition |
| GET | `/api/v1/workflows` | Required | List workflows |
| POST | `/api/v1/workflows/{id}/trigger` | Required | Trigger workflow execution |
| GET | `/api/v1/runs` | Required | List execution runs |
| GET | `/api/v1/runs/{id}` | Required | Get run detail + logs |
| POST | `/api/v1/runs/{id}/resume` | Operator/Admin | Resume paused run (HITL) |
| GET | `/api/v1/runs/{id}/cost` | Required | Get token + cost breakdown |
| GET | `/health` | Public | Health check |

---

## Getting Started

```bash
git clone https://github.com/Gokatech-Inc/AgentForge.git
cd AgentForge

cp .env.example .env
# Set ANTHROPIC_API_KEY

docker-compose up -d

# API:  http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Local Development
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d db redis
uvicorn app.main:app --reload
```

### Running Tests
```bash
pytest tests/ -v
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `SECRET_KEY` | (required) | JWT signing secret |
| `ANTHROPIC_API_KEY` | (required) | Claude AI API key |
| `REDIS_URL` | `redis://localhost:6379` | State cache |
| `MAX_AGENT_RETRIES` | `3` | Max retries per agent step |
| `AGENT_TIMEOUT_SECONDS` | `120` | Per-step timeout |

---

## License

MIT License — **Gokatech Inc** · Enterprise AI Automation
