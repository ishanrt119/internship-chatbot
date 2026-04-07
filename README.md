# 🎓 Internship Copilot

Internship Copilot is an AI-powered internship recommendation and career chatbot. It utilizes advanced Natural Language Processing (NLP) to parse your resume, scrape real-time job listings, and match your skillset with top opportunities. All while letting you converse with a personalized career advisor directly within a clean, wide-layout ChatGPT-like interface!

## 🌟 Features

- **Resume Parsing Engine**: Upload your PDF resume directly into the chat. The app extracts text and pins your skillset and technical profile instantly to a dedicated side panel using PyMuPDF and SpaCy models.
- **Autonomous Job Scraping**: No manual forms required! Just ask the chatbot to find jobs for you (e.g., "Find remote backend internships"). It autonomously generates search parameters, fetches live internship data, and returns the matches directly into your conversation.
- **Match Scoring**: Analyzes your parsed resume against active job descriptions using TF-IDF matching algorithms (via Scikit-Learn) to intuitively rank opportunities based on how aligned you are.
- **AI Career Expert**: Ask any interview, skill, or resume-related queries! Integrated with the Groq API for lightning fast conversational intelligence.
- **Sleek UI**: Experience a dynamic layout featuring custom styling, badge components, context-aware avatars, and a dedicated profile sidebar.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Web Scraping**: BeautifulSoup4, Requests
- **NLP / AI**: Groq API, SpaCy, Scikit-Learn
- **PDF Processing**: PyMuPDF (`pymupdf`)
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
   pip install -r requirements.txt
   ```

4. **Install the SpaCy language model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure your API Key:**
   Create a `.env` file in the root directory and securely add your Groq API Key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```
   *(Note: The API key is securely loaded from this file and is never exposed in the UI.)*

## 🎮 Usage

Run the Streamlit app locally:
```bash
streamlit run app.py
```

- **Uploading Resumes:** Click the `📎` attachment clip button inside the chat text box to upload your PDF resume. Your extracted profile will appear in the left sidebar!
- **Autonomous Search:** Simply ask the chatbot what you're looking for (e.g., "Find me a Machine Learning internship"). It will automatically figure out the parameters, scrape portals, and match you!
- **Career Advice:** Ask the copilot anything! For example: "What skills am I missing for these roles?" or "Can you explain why the top match is good for me?"

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
