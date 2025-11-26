# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from dataclasses import dataclass
from typing import Dict, Any
from utils.pdf_utils import generate_pdf

@dataclass
class PDFTool:
    name: str = "pdf_generate"

    def run(self, prompt: str, response: str, prefs: Dict[str, Any] = None) -> Dict[str, Any]:
        pdf_result = generate_pdf(prompt, response, prefs)

        return {
            "type": "pdf",
            "bytes": pdf_result["bytes"],
            "meta": pdf_result["meta"]
        }