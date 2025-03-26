import streamlit as st
import os
import tempfile
from main import MediTrustAI, State
from graph_bot import MediGuide
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="MediTrust AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'flow_state' not in st.session_state:
    st.session_state.flow_state = 'upload'
if 'meditrust' not in st.session_state:
    st.session_state.meditrust = MediTrustAI(State())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_folders():
    """Create necessary folders for output files"""
    Path("temp").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)

def process_uploaded_file(uploaded_file):
    """Process the uploaded PDF file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='temp') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        st.error("Error processing the uploaded file. Please try again.")
        return None

def run_medic_bot(file_path):
    """Run the medical report analysis"""
    try:
        st.session_state.meditrust.state.report = file_path
        st.session_state.meditrust.medic_bot()
        return True
    except Exception as e:
        logger.error(f"Error in medical analysis: {e}")
        st.error("Error analyzing the medical report. Please try again.")
        return False

def display_chat_interface():
    """Display the chat interface for MediGuide"""
    st.markdown("### 💬 Chat with MediGuide")
    st.write("Ask any questions about your medical report, abnormalities, or recommended doctors.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Your question"):
        with st.chat_message("user"):
            st.write(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            try:
                response = MediGuide(prompt)
                st.write(response["output"])
                st.session_state.chat_history.append({"role": "assistant", "content": response["output"]})
            except Exception as e:
                st.error(f"Error: {str(e)}")

def main():
    initialize_folders()
    
    # Sidebar
    with st.sidebar:
        st.title("🏥 MediTrust AI")
        st.markdown("---")
        st.markdown("### Progress")
        if st.session_state.flow_state == 'upload':
            st.info("📁 Upload Report")
        elif st.session_state.flow_state == 'analysis':
            st.success("📁 Upload Report")
            st.info("🔍 Analysis")
        elif st.session_state.flow_state == 'doctor':
            st.success("📁 Upload Report")
            st.success("🔍 Analysis")
            st.info("👨‍⚕️ Doctor Recommendations")
        elif st.session_state.flow_state == 'chat':
            st.success("📁 Upload Report")
            st.success("🔍 Analysis")
            st.success("👨‍⚕️ Doctor Recommendations")
            st.info("💬 Chat Interface")

    # Main content
    st.title("Medical Report Analysis System")

    if st.session_state.flow_state == 'upload':
        uploaded_file = st.file_uploader("Upload your medical report (PDF)", type=['pdf'])
        if uploaded_file and st.button("Process Report"):
            with st.spinner("Processing your report..."):
                file_path = process_uploaded_file(uploaded_file)
                if file_path and run_medic_bot(file_path):
                    st.session_state.flow_state = 'analysis'
                    st.experimental_rerun()

    elif st.session_state.flow_state == 'analysis':
        st.success("Report processed successfully!")
        st.markdown("### Would you like to get doctor recommendations?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes"):
                st.session_state.flow_state = 'doctor'
                st.experimental_rerun()
        with col2:
            if st.button("No"):
                st.session_state.flow_state = 'chat'
                st.experimental_rerun()

    elif st.session_state.flow_state == 'doctor':
        city = st.text_input("Enter your city:")
        if city and st.button("Find Doctors"):
            with st.spinner("Finding doctors in your area..."):
                try:
                    st.session_state.meditrust.state.decision = "yes"
                    st.session_state.meditrust.doctor_bot()
                    st.success("Doctors found successfully!")
                    st.session_state.flow_state = 'chat'
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error finding doctors: {str(e)}")

    elif st.session_state.flow_state == 'chat':
        display_chat_interface()

    # Reset button
    if st.sidebar.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

if __name__ == "__main__":
    main()
