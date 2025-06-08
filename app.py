import streamlit as st
import re
import openai

# ✅ Инициализация клиента GPT
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Resume Matcher", layout="centered")
st.title("🤖 AI Resume vs Job Description Matcher")
st.markdown("Upload your resume and a job description. Get match analysis and an optimized version for ATS.")

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

# 🧠 System Prompt в стиле Recruiter Pro
system_prompt = """
You are an expert technical recruiter and ATS algorithm analyst.
Evaluate how well a resume fits a job description.

Provide:
1. Match Score (0–100)
2. Matching Skills/Experience
3. Missing or Weak Points
4. ATS compatibility notes
5. Clear suggestions to improve resume for both ATS and recruiters
"""

# 🔍 Анализ соответствия
if st.button("🔍 Analyze Resume") and resume_text and job_description:
    with st.spinner("🧠 Evaluating resume..."):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Job description:\n{job_description}\n\nResume:\n{resume_text}"}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
        )
        result = response.choices[0].message.content
        st.subheader("📋 Match Analysis (Recruiter Pro):")
        st.markdown(result)

# ✍️ Генерация резюме
if st.button("✍️ Generate Optimized Resume") and resume_text and job_description:
    with st.spinner("📄 Generating optimized resume..."):
        rewrite_prompt = f"""
You are an expert in writing professional ATS-compatible resumes.

Here is the job description:
{job_description}

Here is the current resume:
{resume_text}

Please rewrite the resume using these guidelines:
- Structure it clearly (Summary, Experience, Skills, etc.)
- Use bullet points
- Be specific: include tools, technologies, and results
- Incorporate missing but truthful keywords from the job
- Keep formatting simple for ATS
"""
        messages = [
            {"role": "system", "content": "You are a resume writing expert and ATS optimization specialist."},
            {"role": "user", "content": rewrite_prompt}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        optimized = response.choices[0].message.content
        st.subheader("🧾 Optimized Resume:")
        st.code(optimized, language="markdown")
