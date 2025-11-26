# tools/pdf_tool.py # PDFTool wrapper around generate_pdf()
from dataclasses import dataclass
from utils.pdf_utils import generate_pdf
from fpdf import FPDF

@dataclass
class PDFTool:
    name: str = "generate_pdf"

    def run(self, prompt: str, response: str, prefs=None, pdf_bytes=None):
        
        
        pdf = FPDF()
        pdf.add_page()
        
        # Fonts (TTF supported in fpdf2)
        fonts = prefs.get("fonts")if prefs and "fonts" in prefs else{
            "hindi": {"alias": "Mangal", "path": "assets/fonts/Karma-Regular.ttf"},
            "emoji": {"alias": "Emoji", "path": "assets/fonts/NotoEmoji-Regular.ttf"},
            "default": {"alias": "DejaVu", "path": "assets/fonts/DejaVuSans.ttf"}
        }
        
        # Register fonts safely
        for f in fonts.values():
            if os.path.exists(f["path"]):
                pdf.add_font(f["alias"], "", f["path"], uni=True)

        # Regex patterns
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        emoji_pattern = re.compile(r'[\U0001F300-\U0001FAFF]')

        def choose_font(ch):
            if hindi_pattern.match(ch):
                return fonts["hindi"]["alias"]
            elif emoji_pattern.match(ch):
                return fonts["emoji"]["alias"]
            else:
                return fonts["default"]["alias"]

        
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
