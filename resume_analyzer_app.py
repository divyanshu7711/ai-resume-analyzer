import random
import streamlit as st
import docx2txt
import openai
import PyPDF2
import os
import io
import requests
import re
from openai import OpenAI

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from typing import Optional

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
MAX_NEW_TOKENS = 1024

nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

def ensure_nltk_resources():
    resources = ["punkt", "stopwords"]
    for resource in resources:
        try:
            nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, download_dir=nltk_data_path)

ensure_nltk_resources()

def strip_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def language_change():
    st.session_state.lang = st.session_state.language_selection

def get_hf_token():
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if not HF_TOKEN:
        try:
            HF_TOKEN = st.secrets["HF_TOKEN"]
        except KeyError:
            st.error("HF_TOKEN secret not found. Set environment variable locally or Streamlit secret in the cloud.")
            st.stop()
            return None
    return HF_TOKEN

def read_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text

def read_docx(file) -> str:
    return docx2txt.process(file)

def extract_text(uploaded_file) -> Optional[str]:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "pdf":
        return read_pdf(uploaded_file)
    elif file_extension == "docx":
        return read_docx(uploaded_file)
    else:
        return None

def calculate_match_score(resume_text: str, job_description: str):
    try:
        resume_tokens = set(word_tokenize(resume_text.lower()))
        job_tokens = set(word_tokenize(job_description.lower()))
        stop_words = set(stopwords.words('english'))
        resume_tokens = {w for w in resume_tokens if w.isalpha() and w not in stop_words}
        job_tokens = {w for w in job_tokens if w.isalpha() and w not in stop_words}
        if not job_tokens:
            return 0, []
        matched = resume_tokens & job_tokens
        missing = job_tokens - resume_tokens
        score = round((len(matched) / len(job_tokens)) * 100)
        return score, list(missing)
    except Exception:
        return 0, []

def analyze_resume_openai(resume_text: str, job_description: str, api_key: str, language: str = "English") -> str:
    client = OpenAI(api_key=api_key)
    lang_instruction = "Respond in Spanish." if language == "Espanol" else "Respond in English."
    prompt = f"""
    You are an expert resume reviewer. Analyze the following resume against the job description.
    Provide structured feedback with improvements, focusing only on analysis.
    Format your response as a bullet list with no more than 12 points.
    {lang_instruction}

    Resume:
    {resume_text[:3000]}

    Job Description:
    {job_description[:2000]}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return response.choices[0].message.content

def analyze_resume_hf(resume_text: str, job_description: str, language: str = "English") -> str:
    HF_TOKEN = get_hf_token()
    lang_instruction = "Respond in Spanish." if language == "Espanol" else "Respond in English."
    prompt = f"""<s>[INST] You are an expert resume reviewer. Analyze the resume against the job description.
    Provide structured feedback as bullet points (max 12). {lang_instruction}

    Resume: {resume_text[:2000]}
    Job Description: {job_description[:1500]} [/INST]"""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": MAX_NEW_TOKENS, "return_full_text": False}}
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and result:
            return result[0].get("generated_text", "No response generated.")
    return "Free AI model is currently unavailable. Please try again later or use OpenAI API."

def generate_pdf_report(feedback: str, match_score: int, missing_keywords: list, improvement_text: str = "") -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 60
    y = height - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "AI-Powered Resume Analysis Report")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Resume Match Score: {match_score}%")
    y -= 25

    if missing_keywords:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Missing Keywords:")
        y -= 20
        c.setFont("Helvetica", 10)
        keywords_text = ", ".join(missing_keywords[:20])
        for line in simpleSplit(keywords_text, "Helvetica", 10, width - 2 * margin):
            c.drawString(margin, y, line)
            y -= 15
        y -= 10

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "AI Resume Feedback:")
    y -= 20
    c.setFont("Helvetica", 10)
    clean_feedback = strip_markdown(feedback)
    for line in clean_feedback.split("\n"):
        wrapped = simpleSplit(line, "Helvetica", 10, width - 2 * margin)
        for wline in wrapped:
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, wline)
            y -= 15

    c.save()
    buffer.seek(0)
    return buffer.read()

def main():
    st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
    st.title("📄 AI-Powered Resume Analyzer")
    st.markdown("Upload your resume and provide a job description to get AI-generated feedback.")

    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "match_score" not in st.session_state:
        st.session_state.match_score = 0
    if "missing_keywords" not in st.session_state:
        st.session_state.missing_keywords = []
    if "improvement_text" not in st.session_state:
        st.session_state.improvement_text = ""

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        job_description = st.text_area("Paste Job Description Here", height=200)
        model_choice = st.radio("Choose an AI Model:", ["Free Public AI (HuggingFace)", "OpenAI API (GPT-4)"])
        api_key = ""
        if model_choice == "OpenAI API (GPT-4)":
            api_key = st.text_input("Enter OpenAI API Key", type="password")

    with col2:
        if st.button("🔍 Analyze Resume", type="primary"):
            if not uploaded_file or not job_description.strip():
                st.warning("Please upload a resume and enter a job description.")
            else:
                resume_text = extract_text(uploaded_file)
                if not resume_text:
                    st.error("Unsupported file format. Please upload a PDF or DOCX.")
                else:
                    with st.spinner("Analyzing resume..."):
                        score, missing = calculate_match_score(resume_text, job_description)
                        st.session_state.match_score = score
                        st.session_state.missing_keywords = missing
                        try:
                            if model_choice == "OpenAI API (GPT-4)" and api_key:
                                feedback = analyze_resume_openai(resume_text, job_description, api_key)
                            else:
                                feedback = analyze_resume_hf(resume_text, job_description)
                            st.session_state.feedback = feedback
                        except Exception as e:
                            st.session_state.feedback = f"Error during analysis: {str(e)}"

        if st.session_state.feedback:
            st.subheader("📝 Resume Feedback")
            st.write(st.session_state.feedback)

            st.subheader("📊 Resume Match Score")
            score = st.session_state.match_score
            st.progress(score / 100)
            st.write(f"Your resume matches **{score}%** of the job description.")
            if score >= 75:
                st.success("✅ Excellent match! Your resume aligns very well with this job.")
            elif score >= 50:
                st.info("👍 Good match! Consider emphasizing missing keywords.")
            else:
                st.warning("⚠️ Low match. Try tailoring your resume to the job requirements.")

            if st.session_state.missing_keywords:
                st.subheader("🔍 Missing Keywords & Skills")
                st.write(", ".join(st.session_state.missing_keywords[:30]))
            else:
                st.success("✅ Your resume includes all important keywords!")

            pdf_bytes = generate_pdf_report(
                st.session_state.feedback,
                st.session_state.match_score,
                st.session_state.missing_keywords
            )
            st.download_button(
                label="📥 Download Report (PDF)",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
