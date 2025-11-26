# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from dataclasses import dataclass
from utils.pdf_utils import generate_pdf
from fpdf import FPDF

@dataclass
class PDFTool:
    name: str = "generate_pdf"

    def run(self, prompt: str, response: str, prefs=None, pdf_bytes=None):
        
        """
        Agent-friendly wrapper around generate_pdf.
        Returns structured dict with PDF bytes + metadata.
        """
        pdf_bytes = generate_pdf(prompt, response, prefs)
            
        return {
            "type": "pdf",
            "bytes": pdf_bytes,   # raw binary data
            "meta": {
                "filename": "output.pdf",
                "pages": 1,
                "prefs": prefs
            }
        }
