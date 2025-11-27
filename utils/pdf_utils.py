# generate_pdf() + regex + font logic
from fpdf import FPDF
import os, re
# --- PDF Generation ---
def generate_pdf(prompt:str, response:str)->bytes:
    pdf = FPDF()
    pdf.add_page()

    # Fonts (TTF supported in fpdf2)
    fonts = {
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

    text = f"Prompt:\n{prompt}\n\nResponse:\n{response}"
    
    current_font = None
    for ch in text:
        font_choice = choose_font(ch)
        if font_choice != current_font:
            pdf.set_font(font_choice, size=12)
            current_font = font_choice

        try:
            pdf.write(8, ch)
        except Exception:
            pdf.write(8, "?")
    
    # Output as bytes
    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin1")
    elif isinstance(pdf_bytes, bytearray):
        pdf_bytes=bytes(pdf_bytes)
        
    return pdf_bytes


