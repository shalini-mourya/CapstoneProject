# tools/pdf_tool.py 
from utils.pdf_utils import generate_pdf

class PDFTool:
    
    def can_handle(self, prompt: str) -> bool:
        triggers = [
            "generate pdf", "save as pdf", "save pdf",
            "save response as pdf", "save this as pdf",
            "make pdf", "make response as pdf",
            "print pdf", "print this", "pdf please", "export pdf"
        ]
        return any(trigger in prompt for trigger in triggers)

    def handle(self, prompt: str, memory) -> str:
        # Get last response from memory
        last_response = memory.get("response_text")
        last_query = memory.get("last_query")

        if not last_response:
            return "No response available yet to save as PDF."

        pdf_bytes = generate_pdf(last_query, last_response)
        # Return structured data instead of calling UI directly
        return {
            "message": "PDF generated from the last response.",
            "pdf_bytes": pdf_bytes
        }
    
   
