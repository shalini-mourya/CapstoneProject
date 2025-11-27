import streamlit as st
import google.generativeai as genai
import base64, re
import streamlit.components.v1 as components
from utils.pdf_utils import generate_pdf
from agent_core import Agent, MemoryManager
from tools.pdf_tool import PDFTool

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
    
# --- Memory + Tools + Agent ---
memory = MemoryManager()
pdf_tool = PDFTool()
agent = Agent(model=model, memory_manager=MemoryManager())

# --- Session State ---
for key in ["response_text","last_query"]:
    if key not in st.session_state:
        st.session_state["response_text"] = ""

# --- Streamlit UI ---
st.title("ChatToPrint - converse and capture")
st.markdown("Type your query and Gemini will respond instantly.")

# --- Sidebar  ---        
st.sidebar.image("assets/images/chattoprint_logo.png", width=100)

# --- Show PDF ---
def show_pdf(pdf_bytes, default_width=800, default_height=600):   
           
    if isinstance(pdf_bytes,bytearray):
        pdf_bytes=bytes(pdf_bytes)    
    
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="Gemini_Response.pdf",
        mime="application/pdf"
    )  

    # Inline preview
                   
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    width_attr = "100%"
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
            width="{width_attr}" 
            height="{default_height}" 
            style="border:none; background-color:white;">
            <p> Inline preview not supported in this browser. 
            Please use the download button above to download the PDF.</p>
        </iframe>
    """
    components.html(pdf_display, height=default_height)          


# --- Prompt Input ---
user_prompt = st.text_input("Enter your query for Gemini:", key="prompt")

if user_prompt.strip():
    with st.spinner("Agent is processing ..."):
        try:
            # Pass the prompt into the agent                
            #result = agent.run(user_prompt)
            result = agent.process("Explain modular agent orchestration")
            print(result["message"])   # Gemini’s response
            result = agent.process("save as pdf")
            print(result["message"])   # "PDF generated from the last response."

            # Store response in session  
            st.session_state["response_text"] = result.get("reply_text", "")
            st.session_state["last_query"] = user_prompt  
            # Show response
            if result.get("reply_text"):
                st.success("Response received!")
                st.write(result["reply_text"])
                
            if "message" in result:
                st.info(result["message"])
                
            if "pdf_bytes" in result:
                st.success("PDF has been saved! Click below to download:")
                show_pdf(result["pdf_bytes"])  
                              
            if st.session_state["response_text"]:
                st.info("Tip: You can save this response as a PDF. Type 'save as pdf' in the prompt box.")
        except Exception as e:
            st.error(f"Agent error: {e}")           

# --- Sidebar Signature ---   
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 Developed by **Shalini Mourya**")
