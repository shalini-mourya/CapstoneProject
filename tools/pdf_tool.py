# tools/pdf_tool.py 
from utils.pdf_utils import generate_pdf
import re

class PDFTool:
    def __init__(self):
        # Define trigger keywords/phrases
        self.triggers = [
            "save as pdf",
            "save response as pdf",  
            "save the response as pdf",  
            "save this response as pdf",        
            "save pdf",
            "save this as pdf",
            "save it as pdf",
            "create pdf",
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
        last_query = memory_manager.get("last_query")
        if not last_response:
            return {
                "reply_text": "",
                "message": "**PDF Save Error:** Please give your query to Gemini first. The 'save as pdf' command must be used *after* a response is shown"
            }

        try:
            pdf_bytes = generate_pdf(last_query, last_response)
        except Exception as e:
            return {
                "reply_text": last_response,
                "message": f"Error generating PDF: {e}"
            }
        
              # Return structured data for UI
        return {
            "reply_text": last_response,       # show the last Gemini response
            "message": "",
            "pdf_bytes": pdf_bytes             # for download/preview
        }

    
   
