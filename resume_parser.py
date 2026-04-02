import fitz # PyMuPDF
import spacy
import re

# Load English NLP model safely
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None 

def extract_text_from_pdf(pdf_path_or_bytes):
    try:
        # if bytes
        if isinstance(pdf_path_or_bytes, bytes):
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            doc = fitz.open(pdf_path_or_bytes)
            
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def parse_resume(text):
    data = {
        "skills": [],
        "education": [],
        "experience": [],
        "projects": []
    }
    if not nlp:
        # basic fallback if spacy model is missing
        data["skills"] = ["Python", "SQL"] if "python" in text.lower() else []
        return data
        
    doc = nlp(text)
    
    # Simple keyword extraction for skills
    common_skills = ["python", "java", "c++", "javascript", "react", "node.js", "sql", "machine learning", "data analysis", "aws", "docker", "kubernetes", "html", "css", "streamlit", "nlp", "django", "flask", "pytorch", "tensorflow", "git", "linux"]
    text_lower = text.lower()
    found_skills = set()
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.add(skill.capitalize())
            
    data["skills"] = list(found_skills)
    
    # Entity extraction for education & experience
    for ent in doc.ents:
        if ent.label_ == "ORG":
            if any(word in ent.text.lower() for word in ["university", "college", "institute", "school"]):
                data["education"].append(ent.text)
            else:
                data["experience"].append(ent.text)
                
    data["education"] = list(set(data["education"]))
    data["experience"] = list(set(data["experience"]))
    
    return data
