import requests
from bs4 import BeautifulSoup

def scrape_internshala(role, location=""):
    jobs = []
    keyword = role.replace(" ", "-").lower()
    url = f"https://internshala.com/internships/keywords-{keyword}/"
    if location:
        loc = location.replace(" ", "-").lower()
        url = f"https://internshala.com/internships/{loc}-internship/keywords-{keyword}/"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for internship containers
            postings = soup.find_all("div", class_="container-fluid individual_internship")
            
            for post in postings[:10]: # take top 10
                title_elem = post.find("h3", class_="heading_4_5 profile")
                company_elem = post.find("div", class_="heading_6 company_name")
                loc_elem = post.find("a", class_="location_link")
                stipend_elem = post.find("span", class_="stipend")
                apply_link_elem = title_elem.find("a") if title_elem else None
                
                title = title_elem.text.strip() if title_elem else "Unknown Role"
                company = company_elem.text.strip() if company_elem else "Unknown Company"
                loc = loc_elem.text.strip() if loc_elem else "Unknown Location"
                stipend = stipend_elem.text.strip() if stipend_elem else "Unpaid/Unknown"
                apply_link = "https://internshala.com" + apply_link_elem["href"] if apply_link_elem else url
                
                description = f"Internship opportunity for {title} at {company}. Based in {loc}. Offering: {stipend}."
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": loc,
                    "stipend": stipend,
                    "apply_link": apply_link,
                    "description": description,
                    "skills_required": [role]
                })
    except Exception as e:
        print(f"Error scraping Internshala: {e}")
        
    return jobs

def get_jobs(role, location="", remote=False, min_stipend=""):
    jobs = scrape_internshala(role, location)
    
    # Fallback to dummy data if scrape fails / captcha blocks us
    if not jobs:
        jobs = [
            {
                "title": f"{role} Intern",
                "company": "TechNova Solutions",
                "location": "Remote" if remote else (location or "New York, NY"),
                "stipend": min_stipend if min_stipend else "$1000/month",
                "apply_link": "https://example.com/apply1",
                "description": f"Join our forward-thinking team as a {role} Intern. You will work alongside senior developers to build scalable features and improve system architecture.",
                "skills_required": ["Python", "SQL"] if "data" in role.lower() else ["Javascript", "React"]
            },
            {
                "title": f"Junior {role} ",
                "company": "Apex Innovations",
                "location": "Remote" if remote else (location or "San Francisco, CA"),
                "stipend": min_stipend if min_stipend else "$1500/month",
                "apply_link": "https://example.com/apply2",
                "description": f"Exciting opportunity for a {role} enthusiast to assist in our core product development. Ideal candidate must be a fast learner.",
                "skills_required": [role, "Teamwork"]
            },
            {
                "title": f"{role} Development Intern",
                "company": "Global Systems Inc",
                "location": "On-site" if not remote else "Remote",
                "stipend": "Unpaid",
                "apply_link": "https://example.com/apply3",
                "description": f"Learn the ropes of {role} in a fast-paced environment. Mentorship provided by industry veterans.",
                "skills_required": ["Communication", "Problem Solving"]
            }
        ]
    return jobs
