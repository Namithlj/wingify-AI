"""Local debug stub for `crewai` used to run the project without external deps.

Provide minimal `Crew`, `Process`, and `Task` required by the codebase.
This is a lightweight fallback for debugging only.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Process(Enum):
    sequential = "sequential"


@dataclass
class Task:
    description: str
    expected_output: str = ""
    agent: Any = None
    tools: list = None
    async_execution: bool = False


class Crew:
    def __init__(self, agents=None, tasks=None, process=Process.sequential):
        self.agents = agents or []
        self.tasks = tasks or []
        self.process = process

    def kickoff(self, inputs: dict):
        # Minimal deterministic behavior for debugging: return a summary dict
        return {
            "query": inputs.get("query"),
            "agents": [getattr(a, "role", str(a)) for a in self.agents],
            "tasks": [getattr(t, "description", str(t)) for t in self.tasks],
            "message": "Stub crew executed (local debug stub).",
        }


__all__ = ["Crew", "Process", "Task"]
