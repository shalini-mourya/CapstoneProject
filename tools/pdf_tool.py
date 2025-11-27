# tools/pdf_tool.py 
from utils.pdf_utils import generate_pdf
import re

class PDFTool:
    def __init__(self):
        # Define trigger keywords/phrases
        self.triggers = [
            "save as pdf",
            "export pdf",
            "generate pdf",
            "make pdf",
            "print pdf",
            "download pdf",
            "convert to pdf"
        ]


    def can_handle(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        print(f"[DEBUG] prompt_lower = {prompt_lower}")
        # Check if any trigger keyword is present
        return any(trigger in prompt_lower for trigger in self.triggers)


    def handle(self, prompt: str, memory) -> dict:
        
        
        if memory is None:
            return {"message": "⚠️ Memory object is None. Cannot access last response."}


        # Get last response from memory
        last_response = memory.get("response_text")
        last_query = memory.get("last_query")
       
        if not last_response or last_response.strip() == "":
            return {"message": "No response available yet to save as PDF."}

        pdf_bytes = generate_pdf(last_query or "User Query", last_response)
        
              # Return structured data instead of calling UI directly
        return {
            "message": "PDF generated from the last response.",
            "pdf_bytes": pdf_bytes
        }
    
   
