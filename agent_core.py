import google.generativeai as genai

class InMemoryStore:
    """Simple key-value memory store for agent context."""

    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)

class Agent:
    """Agent that routes prompts to tools or Gemini by default."""

    def __init__(self, memory, tools):
        self.memory = memory
        self.tools = tools or []        
    
    def run(self, prompt: str) -> dict:
        # Simple routing example
        prompt_lower = prompt.lower()       
        reply_text = "" 
        # Route to tools
        for tool in self.tools:
           if hasattr(tool, "can_handle") and tool.can_handle(prompt_lower):
                result = tool.handle(prompt_lower, self.memory)
                # Ensure tool returns structured dict
                if isinstance(result, dict):
                    return {
                        "reply_text": self.memory.get("response_text", ""),
                        **result
                    }
                else:
                    return {
                        "reply_text": self.memory.get("response_text", ""),
                        "message": str(result)
                    }
  
        # otherwise call → Gemini       
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        reply_text = response.text

        # Save to memory
        self.memory.set("response_text", reply_text)
        self.memory.set("last_query", prompt)

        return {"reply_text": reply_text}    