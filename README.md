# 🎓 Internship Copilot

Internship Copilot is an AI-powered internship recommendation and career chatbot. It utilizes advanced Natural Language Processing (NLP) to parse your resume, scrape real-time job listings, and match your skillset with top opportunities. All while letting you converse with a personalized career advisor directly within a clean, ChatGPT-like interface!

## 🌟 Features

- **Resume Parsing Engine**: Upload your PDF resume directly into the chat. The app extracts text and maps your skillset instantly using PyMuPDF and SpaCy models.
- **Dynamic Job Scraping**: Automatically fetches live internship data across domains directly from real portals (e.g. Internshala).
- **Match Scoring**: Analyzes your resume against job descriptions using TF-IDF matching algorithms (via Scikit-Learn) to show exactly how aligned you are for specific roles.
- **AI Career Expert**: Ask any interview, skill, or resume-related queries! Integrated with the Groq API for lightning fast conversational intelligence.
- **Sleek UI**: Focus solely on the conversation with a clean, centralized chat layout featuring inline file attachments—replicating the premium feel of modern tools like ChatGPT.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Web Scraping**: BeautifulSoup4, Requests
- **NLP / AI**: Groq API, SpaCy, Scikit-Learn
- **PDF Processing**: PyMuPDF (`fitz`)
- **Python**: 3.10+ recommended

## 🚀 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ishanrt119/internship-chatbot.git
   cd internship-chatbot
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install streamlit python-dotenv pymupdf spacy scikit-learn groq beautifulsoup4 requests
   ```

4. **Install the SpaCy language model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure your API Key:**
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```
   *Alternatively, you can provide your API key via the "⚙️ Settings" popover within the app after running it.*

## 🎮 Usage

Run the Streamlit app locally:
```bash
streamlit run app.py
```

- **Uploading Resumes:** Click the internal attachment clip button inside the chat text box to upload your PDF resume.
- **Settings:** Adjust your target job roles, minimum stipend, and API settings by clicking the "⚙️ Settings" button near the top right of the application.
- **Chat:** Just ask! "What skills am I missing for Machine Learning roles?" or "Can you explain why the top match is good for me?"

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
