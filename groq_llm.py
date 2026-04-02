import os
from groq import Groq

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        return Groq(api_key=api_key)
    except:
        return None

def generate_job_explanation(resume_data, job):
    client = get_groq_client()
    if not client:
        return "Groq API key not configured. Explanation cannot be generated."
        
    skills = ', '.join(resume_data.get('skills', [])) if resume_data.get('skills') else 'Not specified'
    edu = ', '.join(resume_data.get('education', [])) if resume_data.get('education') else 'Not specified'
    exp = ', '.join(resume_data.get('experience', [])) if resume_data.get('experience') else 'Not specified'
    
    prompt = f"""
    You are an AI career advisor. Briefly evaluate why the following job is a good fit for this candidate.
    
    Candidate Profile:
    - Skills: {skills}
    - Education: {edu}
    - Experience: {exp}
    
    Job Details:
    - Title: {job.get('title')}
    - Company: {job.get('company')}
    - Description: {job.get('description')}
    
    Keep the explanation under 3 sentences. Be encouraging and highlight how their skills map to the job requirements.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            reasoning_effort="medium"
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with LLM: {e}"

def generate_chat_response(messages, resume_data, top_jobs):
    client = get_groq_client()
    if not client:
        return "Please set your Groq API key in the sidebar or .env file to chat."
        
    system_prompt = "You are an expert internship matching AI assistant. "
    
    if resume_data:
        skills = ', '.join(resume_data.get('skills', []))
        if skills:
            system_prompt += f"The user has the following skills: {skills}. "
            
    if top_jobs:
        jobs_str = ", ".join([f"{j['title']} at {j['company']} ({j.get('match_score', 0)}% match)" for j in top_jobs[:3]])
        system_prompt += f"You have found the following top roles for them: {jobs_str}. "
        
    system_prompt += "Answer user queries concisely and helpfully. Do not make up fake job links."
        
    api_messages = [{"role": "system", "content": system_prompt}]
    
    # Take the last 6 messages to keep context window manageable
    for msg in messages[-6:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    try:
        chat_completion = client.chat.completions.create(
            messages=api_messages,
            model="openai/gpt-oss-120b",
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            reasoning_effort="medium"
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with LLM: {e}"
