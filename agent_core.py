import google.generativeai as genai

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

class Agent:
    """Agent that routes prompts to tools or Gemini by default."""

    def __init__(self, memory, tools):
        self.memory = memory
        self.tools = tools or []        
    
    def run(self, prompt: str) -> str:
        # Simple routing example
        prompt_lower = prompt.lower()
        
        # Route to tools
        for tool in self.tools:
            # Check tools
            if tool.can_handle(prompt_lower):
                return tool.handle(prompt_lower, self.memory)

        # Default → Gemini        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        reply_text = response.text

        # Save to memory
        self.memory.set("response_text", reply_text)
        self.memory.set("last_query", prompt)

        return reply_text


    