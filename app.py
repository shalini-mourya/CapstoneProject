#pip install streamlit google-generativeai fpdf2
import streamlit as st
import google.generativeai as genai
from google import genai
from google.genai import types
from fpdf import FPDF # fpdf2 is imported as fpdf
import io # To handle binary data for PDF
import os # For environment variables

# --- 1. Configure Gemini API (Using Streamlit Secrets for secure deployment) ---
# It's best practice to store API keys securely.
# On Streamlit Cloud, use "Secrets". For local, set an environment variable.
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except AttributeError:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Please add it.")
    st.stop()
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# --- 2. Initialize Gemini Model and Chat History ---
# Use session state to persist chat history across reruns
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Initialize the model and start a chat session
    st.session_state.model = genai.GenerativeModel("gemini-2.5-flash")
    st.session_state.chat = st.session_state.model.start_chat(history=st.session_state.chat_history)

# --- 3. Function to Generate PDF ---
def generate_chat_pdf(history_list):
    pdf = FPDF()
    pdf.add_page()

    # Add DejaVuSans font (assuming it's available or bundled)
    # For Streamlit deployment, you might need to ensure this TTF file is accessible.
    # A common approach is to place it in the same directory as app.py
    # or install it in the deployment environment.
    # As a fallback, you could use a standard font like 'Arial' if DejaVu causes issues.
    try:
        # Assuming DejaVuSans.ttf is in the same directory or accessible via path
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        if not os.path.exists(font_path):
            st.warning("DejaVuSans.ttf not found. Using Arial. Unicode characters may not display correctly.")
            pdf.set_font("Arial", size=12)
        else:
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
    except Exception as e:
        st.error(f"Error adding DejaVu font: {e}. Falling back to Arial.")
        pdf.set_font("Arial", size=12)


    pdf.multi_cell(0, 10, "Gemini Chat Transcript\n\n", align='C')

    for message in history_list:
        role = "You" if message.role == "user" else "Gemini"
        content = message.parts[0].text if message.parts else "*(No content)*"
        pdf.multi_cell(0, 10, f"{role}: {content}\n")
        pdf.ln(2) # Add a small line break

    pdf_output = io.BytesIO()
    pdf.output(pdf_output, 'S') # 'S' means return as a string (bytes)
    return pdf_output.getvalue()

# --- 4. Streamlit UI Layout ---
st.set_page_config(page_title="ChatToPrint: Gemini AI Chat & PDF", layout="wide")

st.title("💬 ChatToPrint: Gemini AI Conversation")
st.markdown("Automate conversations with Gemini AI and generate a downloadable, Unicode-compliant PDF summary of the full chat dialogue.")

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    avatar = "🧑‍💻" if message.role == "user" else "🤖"
    with st.chat_message(message.role, avatar=avatar):
        st.markdown(message.parts[0].text)

# Chat input
if user_prompt := st.chat_input("Ask Gemini..."):
    # Add user message to chat history and display
   # st.session_state.chat_history.append(genai.types.contents.glm_content.to_glm_content({"role": "user", "parts": [{"text": user_prompt}]}))
    st.session_state.chat_history.append(
    types.Content(
        role="user", 
        parts=[types.Part.from_text(user_prompt)]
    )
)
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    # Get Gemini's response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Gemini is thinking..."):
            try:
                response = st.session_state.chat.send_message(user_prompt)
                gemini_reply = response.text
                st.markdown(gemini_reply)
                # Add Gemini's response to chat history
                st.session_state.chat_history.append(genai.types.contents.glm_content.to_glm_content({"role": "model", "parts": [{"text": gemini_reply}]}))
            except Exception as e:
                st.error(f"Gemini API Error: {e}")
                st.markdown("*(Failed to get response)*")
                # Remove the last user prompt if the response failed
                st.session_state.chat_history.pop()


st.sidebar.title("Options")
st.sidebar.markdown("---")

# Download PDF button
if st.sidebar.button("💾 Download Chat as PDF"):
    if st.session_state.chat_history:
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_chat_pdf(st.session_state.chat_history)
            st.sidebar.download_button(
                label="Click to Download PDF",
                data=pdf_bytes,
                file_name="ChatToPrint_Transcript.pdf",
                mime="application/pdf"
            )
            st.sidebar.success("PDF generated!")
    else:
        st.sidebar.warning("No chat history to download.")

# Clear Chat button
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.model = genai.GenerativeModel("gemini-2.5-flash") # Re-initialize model
    st.session_state.chat = st.session_state.model.start_chat(history=st.session_state.chat_history)
    st.rerun() # Rerun the app to clear the display

st.sidebar.markdown("---")
st.sidebar.info("Built with Gemini AI and Streamlit by [Shalini Mourya]")