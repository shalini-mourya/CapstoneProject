# Agent, Planner, Memory classes -import and register the tool
from tools.pdf_tool import PDFTool
from tools.storage_tool import StorageTool
from dataclasses import dataclass

class InMemoryStore:
    def __init__(self):
        self.profiles = {}
        self.artifacts = {}

    def get_user_profile(self, user_id: str):
        return self.profiles.get(user_id, {})

    def update_user_profile(self, user_id: str, updates: dict):
        base = self.get_user_profile(user_id)
        base.update(updates)
        self.profiles[user_id] = base

    def add_artifact(self, user_id: str, meta: dict):
        self.artifacts.setdefault(user_id, []).append(meta)

    def list_artifacts(self, user_id: str, limit: int = 50):
        return self.artifacts.get(user_id, [])[-limit:]
@dataclass
class PlanStep:
    tool: str
    args: dict

@dataclass
class Plan:
    steps: list

class Planner:
    def __init__(self, tools):
        self.tools = tools

    def make_plan(self, goal, context):
        return Plan(steps=[
            PlanStep(tool="pdf_generate", args={
                "prompt": context["prompt"],
                "response": context["response"],
                "prefs": context.get("prefs")
            })
        ])

class Agent:
    def __init__(self, memory, tools):
        self.memory = memory
        self.registry = {t.name: t for t in tools}
        self.planner = Planner(self.registry)

    def handle(self, user_id: str, goal: str, context: dict) -> dict:
        ctx = {"user_id": user_id, "memory": self.memory, **context}
        plan = self.planner.make_plan(goal, ctx)
        for steps in plan.steps:
            tool = self.registry[step.tool]
            result = tool.run(**step.args)


        last_result = None
        for step in plan.steps:
            tool = self.registry[step.tool]
            args = step.args.copy()
            if last_result and "bytes" in last_result and "pdf_bytes" in tool.run.__code__.co_varnames:
                args["pdf_bytes"] = last_result["bytes"]

            result = tool.run(**args)
            last_result = result

            # Save artifact metadata
            if result.get("type") in ("pdf", "file"):
                self.memory.add_artifact(user_id, {"goal": goal, **result.get("meta", {})})

        return last_result or {"status": "ok"}