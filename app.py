import streamlit as st
import os
import re
import json
from dotenv import load_dotenv

from resume_parser import extract_text_from_pdf, parse_resume
from scraper import get_jobs
from matcher import calculate_match_scores
from groq_llm import generate_job_explanation, generate_chat_response

load_dotenv()

st.set_page_config(page_title="Internship Copilot", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .skill-badge {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        background-color: rgba(120, 120, 150, 0.2);
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    if "top_jobs" not in st.session_state:
        st.session_state.top_jobs = []

initialize_session()

# --- SIDEBAR (Current Profile) ---
with st.sidebar:
    st.title("👤 Your Profile")
    st.divider()
    if st.session_state.resume_data:
        st.success("Resume Active", icon="📄")
        st.markdown("### Extracted Skills")
        skills = st.session_state.resume_data.get('skills', [])
        if skills:
            html_skills = "".join([f"<span class='skill-badge'>{s}</span>" for s in skills])
            st.markdown(html_skills, unsafe_allow_html=True)
        else:
            st.info("No technical skills detected.")
            
        edu = st.session_state.resume_data.get('education', [])
        if edu:
            st.markdown("### Education")
            for e in edu:
                st.markdown(f"- {e}")
                
        exp = st.session_state.resume_data.get('experience', [])
        if exp:
            st.markdown("### Experience")
            for e in exp:
                st.markdown(f"- {e}")
                
        if st.session_state.top_jobs:
            st.divider()
            st.metric("Top Matches Found", len(st.session_state.top_jobs))
    else:
        st.info("Upload your resume (PDF) in the chat attachment icon to automatically build your profile and match with jobs!")

# --- CHAT UI ---
st.title("💬 Career Copilot")

chat_container = st.container(height=600)

with chat_container:
    # Show enhanced empty state
    if len(st.session_state.messages) == 0:
        st.info("👋 **Welcome to Career Copilot!**\n\nI can help you find your dream internship. Try asking me:\n- *\"Find me remote backend developer internships.\"*\n- *\"What skills do I need for Machine Learning?\"*\n\nOr click the 📎 attachment icon below to upload your resume (PDF) and get personalized job matches!")

    for message in st.session_state.messages:
        avatar = "🎓" if message["role"] == "assistant" else "👤" if message["role"] == "user" else None
        with st.chat_message(message["role"], avatar=avatar):
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
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_text)
                
            with st.chat_message("assistant", avatar="🎓"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    response = generate_chat_response(
                        st.session_state.messages,
                        st.session_state.resume_data,
                        st.session_state.top_jobs
                    )
                    
                    search_match = re.search(r'<SEARCH>(.*?)</SEARCH>', response, re.DOTALL | re.IGNORECASE)
                    if search_match:
                        try:
                            search_params = json.loads(search_match.group(1).strip())
                            role = search_params.get("role", "Software Engineer")
                            location = search_params.get("location", "")
                            remote_only = search_params.get("remote", True)
                            min_stipend = search_params.get("min_stipend", "")
                            
                            st.session_state.messages.append({"role": "assistant", "content": "I am searching for internships based on your request..."})
                            message_placeholder.markdown("I am searching for internships based on your request...")
                            
                            with st.spinner(f"Scraping jobs for {role}..."):
                                jobs = get_jobs(role, location=location if not remote_only else "", remote=remote_only, min_stipend=min_stipend)
                                if jobs:
                                    if st.session_state.resume_data:
                                        ranked_jobs = calculate_match_scores(st.session_state.resume_data, jobs)
                                        st.session_state.top_jobs = ranked_jobs[:10]
                                    else:
                                        st.session_state.top_jobs = jobs[:10]
                                    
                                    success_msg = f"I just found {len(st.session_state.top_jobs)} internship matches for {role}! You can ask me to list them or explain why they fit you."
                                    st.session_state.messages.append({"role": "assistant", "content": success_msg})
                                else:
                                    error_msg = f"Sorry, I couldn't find any jobs matching your criteria."
                                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                st.rerun()
                        except json.JSONDecodeError:
                            clean_response = response.replace(search_match.group(0), "").strip()
                            if clean_response:
                                message_placeholder.markdown(clean_response)
                                st.session_state.messages.append({"role": "assistant", "content": clean_response})
                    else:
                        message_placeholder.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
    elif files_processed:
        # If files were processed but no text was submitted, we should still refresh the UI to show the new assistant message
        st.rerun()
