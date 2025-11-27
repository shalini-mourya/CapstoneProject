# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from utils.pdf_utils import generate_pdf
from app_ui import show_pdf   # assuming you have show_pdf in a helper


class PDFTool:
    
    def __init__(self):
        pass

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
        # You can call show_pdf(pdf_bytes) here if you want UI output
        show_pdf(pdf_bytes)
        return "PDF generated from the last response."
    
   
