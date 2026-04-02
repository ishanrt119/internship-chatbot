from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_scores(resume_data, jobs):
    if not jobs:
        return []
        
    # Build text representation of the resume
    skills = " ".join(resume_data.get("skills", []))
    edu = " ".join(resume_data.get("education", []))
    exp = " ".join(resume_data.get("experience", []))
    
    resume_text = f"{skills} {edu} {exp}".strip()
    
    # If resume lacks substantial data, give it a generic placeholder to prevent Tfidf fitting issues
    if not resume_text:
        resume_text = "motivated candidate looking for internship opportunities"
        
    job_docs = []
    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")
        req_skills = " ".join(job.get("skills_required", []))
        
        doc = f"{title} {desc} {req_skills}"
        job_docs.append(doc)
        
    corpus = [resume_text] + job_docs
    
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Row 0: Resume, Row 1+: Jobs
        resume_vector = tfidf_matrix[0:1]
        job_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()
    except ValueError:
        # Happens if vocab is empty (e.g., all stop words)
        similarities = [0.5] * len(jobs)
        
    for i, job in enumerate(jobs):
        # Convert similarity score (0-1) to percentage string
        score_pct = round(float(similarities[i]) * 100, 2)
        job["match_score"] = score_pct
        
    # Rank jobs (Top highest score first)
    ranked_jobs = sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)
    return ranked_jobs
