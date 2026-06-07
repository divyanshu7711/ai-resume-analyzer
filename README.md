# AI Resume Analyzer

A **Generative AI-based Resume Analyzer** that evaluates resumes against job descriptions and provides structured, actionable feedback. Built with Streamlit and powered by OpenAI GPT or HuggingFace Mistral.

## 🚀 Features

- **Resume Evaluation**: Upload PDF or DOCX resumes for instant AI analysis
- **Match Score**: Keyword-based scoring of resume vs job description
- **Missing Keywords**: Identifies skills and keywords absent from your resume
- **Prompt Engineering**: Structured prompts for consistent, actionable feedback
- **Dual AI Support**: OpenAI GPT-4 (paid) or HuggingFace Mistral (free)
- **PDF Report**: Download the full analysis as a PDF report
- **Multi-language**: English and Spanish support

## 🛠️ Tech Stack

- **Frontend/UI**: Streamlit
- **LLM**: OpenAI GPT-4o-mini / HuggingFace Mistral-7B
- **NLP**: NLTK (tokenization, stopword removal)
- **PDF Parsing**: PyPDF2
- **DOCX Parsing**: docx2txt
- **Report Generation**: ReportLab

## ⚙️ Setup & Installation

```bash
# Clone the repository
git clone https://github.com/divyanshu7711/ai-resume-analyzer
cd ai-resume-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLTK resources
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Configure environment
cp .env.example .env
# Add your HF_TOKEN or OPENAI_API_KEY to .env

# Run the app
streamlit run resume_analyzer_app.py
```

## 📖 Usage

1. Upload your resume (PDF or DOCX)
2. Paste the job description in the text area
3. Choose AI model: **Free (HuggingFace)** or **OpenAI API**
4. Click **Analyze Resume**
5. Review feedback, match score, and missing keywords
6. Download the PDF report

## 🏗️ Architecture

```
Resume Upload → Text Extraction (PyPDF2/docx2txt)
       ↓
Keyword Analysis → Match Score + Missing Keywords (NLTK)
       ↓
Prompt Engineering → LLM (OpenAI / HuggingFace)
       ↓
Structured Feedback → Streamlit UI + PDF Report
```
