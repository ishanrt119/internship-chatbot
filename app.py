import streamlit as st
import os
import re
import json
import uuid
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

CHATS_FILE = "chats.json"

def load_chats():
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_chats():
    if "chats" in st.session_state:
        with open(CHATS_FILE, "w") as f:
            json.dump(st.session_state.chats, f)

def sync_current_chat():
    if "current_chat_id" in st.session_state and "chats" in st.session_state:
        curr_id = st.session_state.current_chat_id
        if curr_id in st.session_state.chats:
            curr = st.session_state.chats[curr_id]
            curr["messages"] = list(st.session_state.get("messages", []))
            curr["resume_data"] = st.session_state.get("resume_data", None)
            curr["top_jobs"] = list(st.session_state.get("top_jobs", []))
            
            if curr.get("title", "New Chat") == "New Chat" and len(curr["messages"]) > 0:
                for m in curr["messages"]:
                    if m.get("role") == "user" and not m.get("content", "").startswith("Uploaded resume:"):
                        content = m.get("content", "")
                        curr["title"] = content[:30] + ("..." if len(content) > 30 else "")
                        break
            save_chats()

def initialize_session():
    if "chats" not in st.session_state:
        st.session_state.chats = load_chats()
        
    if "current_chat_id" not in st.session_state:
        if st.session_state.chats:
            st.session_state.current_chat_id = list(st.session_state.chats.keys())[-1]
        else:
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = {
                "id": new_id,
                "title": "New Chat",
                "messages": [],
                "resume_data": None,
                "top_jobs": []
            }
            st.session_state.current_chat_id = new_id
            save_chats()

    curr_id = st.session_state.current_chat_id
    if curr_id not in st.session_state.chats:
        st.session_state.chats[curr_id] = {
            "id": curr_id,
            "title": "New Chat",
            "messages": [],
            "resume_data": None,
            "top_jobs": []
        }
        
    curr = st.session_state.chats[curr_id]
    
    if "messages" not in st.session_state or getattr(st.session_state, "_last_chat_id", None) != curr_id:
        st.session_state.messages = list(curr.get("messages", []))
        st.session_state.resume_data = curr.get("resume_data", None)
        st.session_state.top_jobs = list(curr.get("top_jobs", []))
        st.session_state._last_chat_id = curr_id

initialize_session()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💬 Chat History")
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "id": new_id,
            "title": "New Chat",
            "messages": [],
            "resume_data": None,
            "top_jobs": []
        }
        sync_current_chat()
        st.session_state.current_chat_id = new_id
        save_chats()
        st.rerun()
        
    st.divider()
    
    for chat_id, chat_data in reversed(list(st.session_state.chats.items())):
        title = chat_data.get("title", "New Chat")
        if chat_id == st.session_state.current_chat_id:
            st.button(f"👉 {title}", key=f"btn_{chat_id}", use_container_width=True, disabled=True)
        else:
            if st.button(title, key=f"btn_{chat_id}", use_container_width=True):
                sync_current_chat()
                st.session_state.current_chat_id = chat_id
                st.rerun()

    st.divider()
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
                            
                            st.session_state.messages.append({"role": "assistant", "content": "I am searching for internships based on your request..."})
                            message_placeholder.markdown("I am searching for internships based on your request...")
                            
                            with st.spinner(f"Scraping jobs for {role}..."):
                                jobs = get_jobs(role, location=location if not remote_only else "", remote=remote_only)
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
                                sync_current_chat()
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
        sync_current_chat()
        st.rerun()

sync_current_chat()
