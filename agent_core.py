# Agent, Planner, Memory classes -import and register the tool
class Agent:
    def __init__(self, memory, tools):
        self.memory = memory
        self.registry = {t.name: t for t in tools}
        self.planner = Planner(self.registry)

    def handle(self, user_id: str, goal: str, context: dict) -> dict:
        ctx = {"user_id": user_id, "memory": self.memory, **context}
        plan = self.planner.make_plan(goal, ctx)

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