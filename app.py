import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os, base64, re

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
# Display logo at the top

st.title("ChatToPrint- converse and capture")
st.markdown("Type your query and Gemini will respond instantly.")

# --- Prompt Input (auto trigger) ---
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

    # Load fonts
    fonts = {
        "hindi": {"alias": "mangalb", "path": os.path.join(os.getcwd(), "mangalb.ttf")},
        "emoji": {"alias": "NotoEmoji-Regular", "path": os.path.join(os.getcwd(), "NotoEmoji-Regular.ttf")},
        "default": {"alias": "DejaVuSans", "path": os.path.join(os.getcwd(), "DejaVuSans.ttf")}
    }

    # Register fonts safely
    for f in fonts.values():
        if os.path.exists(f["path"]):
            pdf.add_font(f["alias"], "", f["path"], uni=True)

    # Regex patterns
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]')

    def choose_font(char):
        if hindi_pattern.match(char):
            return fonts["hindi"]["alias"]
        elif emoji_pattern.match(char):
            return fonts["emoji"]["alias"]
        else:
            return fonts["default"]["alias"]

    text = f"Prompt:\n{prompt}\n\nResponse:\n{response}"

    # Write character by character with font switching
    current_font = None
    for ch in text:
    	if hindi_pattern.match(ch):
        	font_choice = "mangalb"
    	elif emoji_pattern.match(ch):
        	font_choice = "NotoEmoji-Regular"
    	else:
        	font_choice = "DejaVuSans"

    	if font_choice not in pdf.fonts:
        	font_choice = "DejaVuSans"

    	if font_choice != current_font:
        	pdf.set_font(font_choice, size=14)
        	current_font = font_choice

    	pdf.write(8, ch)


    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin-1")  # convert string to bytes
    return pdf_bytes

 

# --- Show PDF ---
import streamlit.components.v1 as components

def show_pdf(pdf_bytes, width=800, height=600):
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f"""
    <object data="data:application/pdf;base64,{base64_pdf}" 
            type="application/pdf" 
            width="{width}" 
            height="{height}">
        <p style="text-align:center; font-size:16px; color:#555;">
            📄 Preview not supported in this browser. 
            Please use the download button above to view the PDF.
        </p>
    </object>
    """
    components.html(pdf_display, height=height)

    


# --- Download & Preview ---
if st.session_state["response_text"] and user_prompt.strip():
    pdf_bytes = generate_pdf(user_prompt, st.session_state["response_text"])
    if pdf_bytes:
        st.download_button("📄 Download Response as PDF",
                           data=pdf_bytes,
                           file_name="Gemini_Response.pdf",
                           mime="application/pdf")
        st.markdown("### Preview PDF")
        show_pdf(pdf_bytes)

# --- Sidebar Signature ---
# Show logo in sidebar
st.sidebar.image("chattoprint_logo.png", width=160)
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 Developed by **Shalini Mourya**")