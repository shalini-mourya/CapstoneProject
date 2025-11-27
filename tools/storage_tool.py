# tools/storage_tool.py
import os
from typing import Dict, Any

class StorageTool:
    def __init__(self):
        self.storage = []

    def can_handle(self, prompt: str) -> bool:
        triggers = ["store this", "save chat", "remember this"]
        return any(trigger in prompt for trigger in triggers)

    def handle(self, prompt: str, memory) -> str:
        last_response = memory.get("response_text")
        if last_response:
            self.storage.append(last_response)
            return "Response stored successfully."
        else:
            return "Nothing to store yet."
