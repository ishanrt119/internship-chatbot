import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_jobs(role, location="", remote=False):
    api_key = os.getenv("SERP_API_KEY")
    
    # Construct a search query based on the parameters
    query_parts = [role, "internship"]
    if location:
        query_parts.append(location)
    if remote:
        query_parts.append("remote")
        
    query = " ".join(query_parts)
    
    jobs = []
    
    # If no API key is provided, gracefully inform the UI
    if not api_key:
        print("SERP_API_KEY not found in environment. Please add it to your .env file.")
        return [
            {
                "title": f"Action Required: Add SERP_API_KEY",
                "company": "System",
                "location": location if location else "Unknown",
                "apply_link": "https://serpapi.com/",
                "description": "Please add your SERP_API_KEY to the .env file to fetch real Google Jobs results.",
                "skills_required": [role]
            }
        ]

    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": api_key,
        "hl": "en",
        "gl": "us", # default geolocation
    }
    
    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs_results = data.get("jobs_results", [])
            
            for result in jobs_results[:10]: # Limit to top 10 results
                title = result.get("title", f"{role} Internship")
                snippet = result.get("description", "No description provided.")
                # Truncate overly long descriptions
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                
                # Fetch exact company
                company_name = result.get("company_name", "Unknown Company")
                job_location = result.get("location", location or "Various")
                
                # Get direct apply link if available
                apply_link = "#"
                if result.get("apply_options"):
                    apply_link = result["apply_options"][0].get("link", "#")
                elif result.get("share_link"):
                    apply_link = result.get("share_link")
                
                jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": job_location,
                    "apply_link": apply_link,
                    "description": snippet,
                    "skills_required": [role]
                })
        else:
            print(f"SerpAPI Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception while connecting to SerpAPI: {e}")
        
    if not jobs:
        jobs.append({
            "title": "No Internships Found",
            "company": "N/A",
            "location": location if location else "N/A",
            "apply_link": "#",
            "description": "We couldn't find any recent postings matching your exact criteria using the Google Jobs API.",
            "skills_required": []
        })

    return jobs
