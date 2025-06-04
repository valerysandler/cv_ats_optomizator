import streamlit as st
import openai
import re

# ✅ Инициализация клиента
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Resume Matcher", layout="centered")
st.title("🤖 AI Resume vs Job Description Matcher")

resume_file = st.file_uploader("📄 Upload your resume (.txt, .docx or .pdf)", type=["txt", "docx", "pdf"])
job_description = st.text_area("💼 Paste job description")

def extract_text(file):
    import docx2txt
    import pdfplumber
    if file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

resume_text = extract_text(resume_file) if resume_file else ""

if st.button("🔍 Analyze Resume") and resume_text and job_description:
    with st.spinner("Analyzing..."):
        prompt = f"""
You are a technical recruiter. Compare the resume with the job description below.

Job description:
{job_description}

Resume:
{resume_text}

Provide a short report:
1. Match score (0–100)
2. Matching skills
3. Missing skills
4. Suggestions to improve the resume.
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        st.subheader("📋 Analysis")
        st.markdown(response.choices[0].message.content)

if st.button("✍️ Generate Optimized Resume") and resume_text and job_description:
    with st.spinner("Generating improved resume..."):
        prompt = f"""
You are an expert in writing ATS-optimized resumes.

Job description:
{job_description}

Original resume:
{resume_text}

Rewrite the resume to:
- Match the job more closely
- Add missing but truthful keywords
- Keep it ATS friendly
- Don't invent experience
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        st.subheader("🧾 Optimized Resume")
        st.code(response.choices[0].message.content)
