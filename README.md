# AI Resume Analyzer

This project analyzes a resume against a job description using AI and gives feedback on what is missing or what can be improved. I built this as a side project to learn more about generative AI and prompt engineering.

## What it does

- upload your resume (pdf or docx format)
- paste the job description
- it will give you feedback using AI
- also shows a match score (how much your resume matches the job)
- shows missing keywords
- you can download the feedback as pdf also

## Technologies

- Python
- Streamlit
- OpenAI API
- HuggingFace (free option if you dont have openai key)
- NLTK
- PyPDF2, docx2txt
- ReportLab for pdf generation

## Setup

```
pip install -r requirements.txt
```

you also need to download nltk data, run this once

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

create .env file

```
HF_TOKEN=your_huggingface_token
OPENAI_API_KEY=your_openai_key  (optional)
```

then run

```
streamlit run resume_analyzer_app.py
```

## How to use

1. open the app in browser
2. upload resume file
3. paste job description in the box
4. select which AI model you want to use
5. click Analyze Resume button
6. see the feedback and score

## Notes

- free huggingface model sometimes takes time or may not respond, in that case use openai
- I was trying to learn how prompt engineering works so the prompts might not be perfect
- its a beginner level project, open to suggestions
