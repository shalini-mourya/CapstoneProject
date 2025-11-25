import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os, base64, re
import streamlit.components.v1 as components

# --- Background Image ---
with open("background.jpg", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{encoded}");
    background-size: cover;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Configure Gemini API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Error loading API key: {e}")
    st.stop()

# --- Initialize Gemini Model ---
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Session State ---
if "response_text" not in st.session_state:
    st.session_state["response_text"] = ""

# --- Streamlit UI ---
st.title("ChatToPrint - converse and capture")
st.markdown("Type your query and Gemini will respond instantly.")

# --- Prompt Input ---
user_prompt = st.text_input("Enter your query for Gemini:", key="prompt")

if user_prompt.strip():
    with st.spinner("Gemini is thinking..."):
        try:
            response = model.generate_content(user_prompt)
            reply_text = response.text
            st.session_state["response_text"] = reply_text
            st.success("Response received!")
            st.write(reply_text)
        except Exception as e:
            st.error(f"Gemini API error: {e}")

# --- PDF Generation ---
def generate_pdf(prompt, response):
    pdf = FPDF()
    pdf.add_page()

    # Fonts (TTF supported in fpdf2)
    fonts = {
        "hindi": {"alias": "Mangal", "path": os.path.join(os.getcwd(), "Mangal Regular.ttf")},
        "emoji": {"alias": "Emoji", "path": os.path.join(os.getcwd(), "NotoEmoji-Regular.ttf")},
        "default": {"alias": "DejaVu", "path": os.path.join(os.getcwd(), "DejaVuSans.ttf")}
    }

    # Register fonts safely
    for f in fonts.values():
        if os.path.exists(f["path"]):
            pdf.add_font(f["alias"], "", f["path"],uni=True)

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
        if font_choice not in pdf.fonts:
            font_choice = "DejaVu"

        if font_choice != current_font:
            pdf.set_font(font_choice, size=12)
            current_font = font_choice

        try:
            pdf.write(8, ch)
        except Exception:
            pdf.write(8, "?")

    # Output as bytes
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)
    return pdf_bytes



# --- Show PDF ---
def show_pdf(pdf_bytes, default_width=800, default_height=600):
    if isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)

    # Sidebar controls
    preview_option = st.sidebar.checkbox("Show inline PDF preview", value=True)
    fit_to_container = st.sidebar.checkbox("Fit preview to container width", value=False)

    # Download button
    st.download_button(
        "📄 Download PDF",
        data=pdf_bytes,
        file_name="Gemini_Response.pdf",
        mime="application/pdf"
    )

    # Inline preview
    if preview_option:
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        width_attr = "100%" if fit_to_container else f"{default_width}px"
        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                width="{width_attr}" 
                height="{default_height}" 
                style="border:none; background-color:white;">
            <p>📄 Inline preview not supported in this browser. 
            Please use the download button above to view the PDF.</p>
        </iframe>
        """
        components.html(pdf_display, height=default_height)

# --- Download & Preview ---
if st.session_state["response_text"] and user_prompt.strip():
    pdf_bytes = generate_pdf(user_prompt, st.session_state["response_text"])
    if pdf_bytes:
        st.markdown("### Response PDF")
        show_pdf(pdf_bytes)

# --- Sidebar Signature ---
st.sidebar.image("chattoprint_logo.png", width=160)
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 Developed by **Shalini Mourya**")