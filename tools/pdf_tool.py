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
        # Check if any trigger keyword is present
        return any(trigger in prompt_lower for trigger in self.triggers)

    def handle(self, prompt: str, memory_manager) -> dict:       
        
        # Get the last response text from memory
        last_response = memory_manager.get("response_text")
       
        if not last_response:
            return {
                "reply_text": "I can't save a PDF yet.",
                "message": "No response available yet to save as PDF."
            }

        pdf_bytes = generate_pdf(last_response)
        
              # Return structured data instead of calling UI directly
        return {
            "reply_text": last_response,       # show the last Gemini response
            "message": "PDF generated from the last response.",
            "pdf_bytes": pdf_bytes             # for download/preview
        }

    
   
