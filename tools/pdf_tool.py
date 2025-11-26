# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from dataclasses import dataclass
from typing import Dict, Any
from utils.pdf_utils import generate_pdf

@dataclass
class PDFTool:
    name: str = "generate_pdf"

    def run(self, prompt: str, response: str, prefs=None, pdf_bytes=None):
        pdf_bytes = bytearray(b"%PDF-...") 
        #pdf_result = generate_pdf(prompt, response, prefs)

        return {
            "type": "pdf",
            "bytes": pdf_bytes,   # raw binary data
            "meta": {
                "filename": "output.pdf",
                "pages": 3,
                "prefs": prefs
            }
        }
