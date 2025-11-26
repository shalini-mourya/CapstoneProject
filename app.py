import streamlit as st
import google.generativeai as genai
import base64, re
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

# --- Sidebar  ---        
st.sidebar.image("assets/images/chattoprint_logo.png", width=100)


# --- Show PDF ---
def show_pdf(pdf_bytes, default_width=800, default_height=600):   

    # Sidebar controls
    preview_option = st.sidebar.checkbox("Show inline PDF preview", value=False)
    fit_to_container = st.sidebar.checkbox("Fit preview to container width", value=False)     
    
    if isinstance(pdf_bytes,bytearray):
        pdf_bytes=bytes(pdf_bytes)
        
    st.download_button(
        label="📄 Download PDF",
        data=pdf_bytes,
        file_name="conversation.pdf",
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
            <p> Inline preview not supported in this browser. 
            Please use the download button above to view the PDF.</p>
        </iframe>
        """
        components.html(pdf_display, height=default_height)  
        


# --- Prompt Input ---
user_prompt = st.text_input("Enter your query for Gemini:", key="prompt")

if user_prompt.strip():
    # Define trigger phrases (lowercase for consistency)
    triggers = [
        "generate pdf",
        "save as pdf",
        "save pdf",
        "save response as pdf",
        "save this as pdf",      
        "make pdf",
        "make response as pdf"
        "print pdf",
        "print this",
        "pdf please",
        "export pdf"
    ]
    # Normalize prompt to lowercase
    prompt_lower = user_prompt.lower()
    if any(trigger in prompt_lower for trigger in triggers):
        # Skip Gemini, just generate PDF from last response
        if st.session_state["response_text"]:
            # --- Sidebar Save as PDF option ---
            savepdf_option = st.sidebar.checkbox("Save as PDF", value=False)
            if savepdf_option:             
            show_pdf(pdf_bytes)
            pdf_bytes = generate_pdf(st.session_state.get("last_query", ""),st.session_state["response_text"])            
            st.sidebar.success("PDF ready — check the main panel below for the download button.")
        else:
            st.warning("No response available yet to save as PDF.")
    else:
        # Normal flow → ask Gemini    
        with st.spinner("Gemini is thinking..."):
            try:
                response = model.generate_content(user_prompt)
                reply_text = response.text
                st.session_state["response_text"] = reply_text
                st.session_state["last_query"] = user_prompt  # store the actual query
                st.success("Response received!")
                st.write(reply_text)
                # Show guidance only if a response exists                
                if st.session_state["response_text"]:                   
                    st.info("Tip: You can save this response as a PDF. Either type 'save as pdf' in the prompt box or use the sidebar button.")
            except Exception as e:
                st.error(f"Gemini API error: {e}")
            

# --- Sidebar Signature ---   
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 Developed by **Shalini Mourya**")
