import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import io
import os

# --- Configure Gemini API ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Error loading API key: {e}")
    st.stop()

# --- Initialize Gemini Model ---
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Streamlit UI ---
st.title("💬 Gemini Chat & PDF Export")
st.markdown("Ask Gemini anything and download the response as a PDF.")

# --- Prompt Input ---
user_prompt = st.text_area("Enter your prompt for Gemini:")

# --- Generate Response ---
if st.button("Get Response"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Gemini is thinking..."):
            try:
                response = model.generate_content(user_prompt)
                reply_text = response.text
                st.session_state["response_text"] = reply_text
                st.success("Response received!")
                st.markdown(reply_text)
            except Exception as e:
                st.error(f"Gemini API error: {e}")

# --- PDF Generation ---
from fpdf import FPDF
import os

def generate_pdf(prompt, response):
    pdf = FPDF()
    pdf.add_page()

    # Use Unicode font if available
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    try:
        if os.path.exists(font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.set_font("Arial", size=12)
    except Exception as e:
        print(f"Font error: {e}")
        pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Prompt:\n{prompt}\n\nResponse:\n{response}")

    try:
        pdf_bytes = pdf.output(dest='S')
        return bytes(pdf_bytes) if isinstance(pdf_bytes, bytearray) else pdf_bytes.encode('latin-1')
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None  # Explicitly return None on failure

# --- Download Button ---
if st.button("📄 Download Response as PDF"):
    if "response_text" in st.session_state and user_prompt:
        pdf_bytes = generate_pdf(user_prompt, st.session_state["response_text"])
        if pdf_bytes:
            st.download_button(
                label="Click to Download PDF",
                data=pdf_bytes,
                file_name="Gemini_Response.pdf",
                mime="application/pdf"
            )
        else:
            st.error("PDF generation failed.")
    else:
        st.warning("No response available to download.")