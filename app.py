import streamlit as st
import os
from dotenv import load_dotenv

from resume_parser import extract_text_from_pdf, parse_resume
from scraper import get_jobs
from matcher import calculate_match_scores
from groq_llm import generate_job_explanation, generate_chat_response

load_dotenv()

st.set_page_config(page_title="Internship Copilot", page_icon="🎓", layout="centered")

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    if "top_jobs" not in st.session_state:
        st.session_state.top_jobs = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("GROQ_API_KEY", "")

initialize_session()

# --- TOP NAVIGATION / SETTINGS ---
# We use a popover to hide the settings, simulating a clean ChatGPT-like UI
col1, col2 = st.columns([8, 2])
with col2:
    with st.popover("⚙️ Settings"):
        st.markdown("**Configuration**")
        api_key_input = st.text_input("Groq API Key", value=st.session_state.api_key, type="password")
        if api_key_input:
            st.session_state.api_key = api_key_input
            os.environ["GROQ_API_KEY"] = api_key_input
        
        st.divider()
        st.markdown("**Job Search Preferences**")
        role = st.text_input("Preferred Role (e.g. Machine Learning, Web Dev)", "Python Developer")
        location = st.text_input("Location Preference", "Remote")
        remote_only = st.checkbox("Remote Only", value=True)
        min_stipend = st.text_input("Minimum Stipend Expected", "$1000")
        
        if st.button("Search Internships"):
            if not st.session_state.resume_data:
                st.warning("Please upload a resume in the chat first to get match scores.")
            else:
                with st.spinner("Scraping portals and analyzing matches..."):
                    jobs = get_jobs(role, location=location if not remote_only else "", remote=remote_only, min_stipend=min_stipend)
                    if jobs:
                        ranked_jobs = calculate_match_scores(st.session_state.resume_data, jobs)
                        st.session_state.top_jobs = ranked_jobs[:10]
                        st.success(f"Found and matched {len(st.session_state.top_jobs)} internships!")
                        # Add a system message to chat to notify the user
                        st.session_state.messages.append({"role": "assistant", "content": f"I just found {len(st.session_state.top_jobs)} internship matches based on your preferences! You can ask me to list them or explain why they fit you."})
                    else:
                        st.error("No jobs found for the given criteria.")

# --- CHAT UI ---
st.title("💬 Career Copilot")

chat_container = st.container(height=600)

with chat_container:
    # Display extracted resume info as a system message if it exists
    if len(st.session_state.messages) == 0:
        st.chat_message("assistant").markdown("Hello! I'm your Career Copilot. You can ask me anything, or upload your PDF resume using the attachment icon in the chat input to get started.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input with file upload feature
prompt = st.chat_input("Ask about interviews, skills needed, or attach your resume (PDF)...", accept_file="multiple", file_type=["pdf"])

if prompt:
    # Streamlit returns a dict-like object with .text and .files attributes
    # The files list will contain UploadedFile objects
    uploaded_files = prompt.files if hasattr(prompt, "files") else prompt.get("files", [])
    user_text = prompt.text if hasattr(prompt, "text") else prompt.get("text", "")
    
    files_processed = False
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Extracting text and parsing skills from {uploaded_file.name}..."):
                pdf_bytes = uploaded_file.read()
                text = extract_text_from_pdf(pdf_bytes)
                if text:
                    parsed_data = parse_resume(text)
                    st.session_state.resume_data = parsed_data
                    skills_found = ', '.join(parsed_data.get('skills', []))
                    st.session_state.messages.append({"role": "user", "content": f"Uploaded resume: {uploaded_file.name}"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Resume `{uploaded_file.name}` parsed successfully! I extracted the following skills: **{skills_found}**. What would you like to do next?"})
                    files_processed = True
                else:
                    st.toast(f"Failed to extract text from {uploaded_file.name}.", icon="❌")
    
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_text)
                
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    response = generate_chat_response(
                        st.session_state.messages,
                        st.session_state.resume_data,
                        st.session_state.top_jobs
                    )
                    message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
    elif files_processed:
        # If files were processed but no text was submitted, we should still refresh the UI to show the new assistant message
        st.rerun()
