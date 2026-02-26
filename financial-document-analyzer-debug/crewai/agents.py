"""Minimal Agent stub for local debugging."""

class Agent:
    def __init__(self, role=None, goal=None, verbose=False, memory=False, backstory=None, tool=None, llm=None, max_iter=1, max_rpm=1, allow_delegation=False):
        self.role = role
        self.goal = goal
        self.verbose = verbose
        self.memory = memory
        self.backstory = backstory
        self.tool = tool or []
        self.llm = llm
        self.max_iter = max_iter
        self.max_rpm = max_rpm
        self.allow_delegation = allow_delegation

    def __repr__(self):
        return f"Agent(role={self.role})"
