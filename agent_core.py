import google.generativeai as genai
from tools.pdf_tool import PDFTool

class MemoryManager:
    def __init__(self):
        self._memory = {"response_text": "", "last_query": ""}

    def update(self, query: str, response: str):
        self._memory["last_query"] = query or ""
        self._memory["response_text"] = response or ""

    def get(self, key: str):
        return self._memory.get(key, "")

    def snapshot(self):
        return dict(self._memory)

class Agent:
    """Agent that routes prompts to tools or Gemini by default."""

    def __init__(self, model, memory_manager):
        self.model = model 
        self.memory = memory_manager
        self.tools = {
            "pdf": PDFTool()          
        }
    
    def process(self, user_prompt: str) -> dict:
        """
        Main orchestration: generate response, update memory, route tools.
        """
        # 1. Get response from Gemini
        response = self.model.generate_content(user_prompt)
        response_text = response.text


        # 2. Update memory immediately
        self.memory.update(user_prompt, response_text)

        # 3. Route prompt to tools if needed
        for tool in self.tools.values():
            if tool.can_handle(user_prompt):
                return tool.handle(user_prompt, self.memory)

        # 4. Default return if no tool triggered
        return {
            "message": response_text
        }
  
    
    def run(self, prompt: str) -> dict:
        # Simple routing example
        prompt_lower = prompt.lower()       
        #reply_text = "" 
        # Route to tools
        for tool in self.tools.values():
           if tool.can_handle(prompt_lower):
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
        #model = genai.GenerativeModel("gemini-2.5-flash")
        response = self.model.generate_content(prompt)
        reply_text = response.text

        # Save to memory
        self.memory.update(prompt, reply_text)


        return {"reply_text": reply_text}    