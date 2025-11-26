import streamlit as st
import google.generativeai as genai
import base64
import streamlit.components.v1 as components
from utils.pdf_utils import generate_pdf
from agent_core import Agent, InMemoryStore
from tools.pdf_tool import PDFTool
from tools.storage_tool import StorageTool

# Create memory + tools
memory = InMemoryStore()
pdf_tool = PDFTool()
storage_tool = StorageTool()

# Create the agent object
agent = Agent(memory=memory, tools=[pdf_tool, storage_tool])


# --- Background Image ---
with open("assets/images/background.jpg", "rb") as f:
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
            
# --- Show PDF ---
def show_pdf(pdf_bytes, default_width=800, default_height=600):
   
    # Sidebar controls
    preview_option = st.sidebar.checkbox("Show inline PDF preview", value=False)
    fit_to_container = st.sidebar.checkbox("Fit preview to container width", value=False)     
    result = agent.handle(user_id="shalini", goal="generate", context=context)
    pdf_bytes = result["bytes"]
    if isinstance(pdf_bytes,bytearray):
        pdf_bytes=bytes(pdf_bytes)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name="conversation.pdf",
            mime="application/pdf"
        )
    else:
        st.write("👉 Type 'generate pdf' in your prompt if you want a PDF download.")



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
    # Define trigger phrases
    triggers = ["generate pdf", "save as pdf", "make pdf", "print this"]
    # Check if any trigger phrase is present in the prompt
    if any(trigger in user_prompt.lower() for trigger in triggers):
        pdf_bytes = generate_pdf(user_prompt, st.session_state["response_text"])
    

    if pdf_bytes:
        st.markdown("### Response PDF")
        show_pdf(pdf_bytes)

# --- Sidebar Signature ---
st.sidebar.image("assets/images/chattoprint_logo.png", width=160)
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 Developed by **Shalini Mourya**")