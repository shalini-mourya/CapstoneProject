# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from dataclasses import dataclass
from typing import Dict, Any
from utils.pdf_utils import generate_pdf
from fpdf import FPDF 

@dataclass
class PDFTool:
    name: str = "generate_pdf"

    def run(self, prompt: str, response: str, prefs=None, pdf_bytes=None):
        pdf_bytes = pdf.output(dest="S")
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode("latin1")
        elif isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        return {
            "type": "pdf",
            "bytes": pdf_bytes,   # raw binary data
            "meta": {
                "filename": "output.pdf",
                "pages": 1,
                "prefs": prefs
            }
        }
