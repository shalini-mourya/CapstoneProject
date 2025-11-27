# tools/pdf_tool.py 
from utils.pdf_utils import generate_pdf
import re

class PDFTool:
    
    def can_handle(self, prompt: str) -> bool:
        pattern = r"(save|generate|make|print|export).*pdf"
        return re.search(pattern, prompt) is not None

    def handle(self, prompt: str, memory) -> dict:
        # Get last response from memory
        last_response = memory.get("response_text")
        last_query = memory.get("last_query")

        if not last_response:
            return {"message": "No response available yet to save as PDF."}

        pdf_bytes = generate_pdf(last_query, last_response)
        # Return structured data instead of calling UI directly
        return {
            "message": "PDF generated from the last response.",
            "pdf_bytes": pdf_bytes
        }
    
   
