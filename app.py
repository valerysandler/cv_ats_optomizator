import streamlit as st
import re
import openai

# Инициализация клиента GPT
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Resume Matcher", layout="centered")

# Переключатель языка
lang = st.radio("🌐 Language / שפה", ["English", "עברית"], horizontal=True)

# Переводы текста UI
if lang == "English":
    st.title("🤖 AI Resume vs Job Description Matcher")
    upload_label = "📄 Upload your resume (.txt, .docx or .pdf)"
    job_label = "💼 Paste job description"
    analyze_btn = "🔍 Analyze Resume"
    optimize_btn = "✍️ Generate Optimized Resume"
    analysis_title = "📋 Match Analysis (Recruiter Pro):"
    optimized_title = "🧾 Optimized Resume:"
    spinner_analyze = "🧠 Evaluating resume..."
    spinner_optimize = "📄 Generating optimized resume..."
else:
    st.title("🤖 התאמת קורות חיים למשרה בעזרת AI")
    upload_label = "📄 העלה קובץ קורות חיים (.txt, .docx או .pdf)"
    job_label = "💼 הדבק תיאור משרה"
    analyze_btn = "🔍 נתח קורות חיים"
    optimize_btn = "✍️ צור גרסה משופרת"
    analysis_title = "📋 ניתוח התאמה (Recruiter Pro):"
    optimized_title = "🧾 קורות חיים מותאמים:"
    spinner_analyze = "🧠 מבצע ניתוח..."
    spinner_optimize = "📄 יוצר קורות חיים חדשים..."

# UI Elements
resume_file = st.file_uploader(upload_label, type=["txt", "docx", "pdf"])
job_description = st.text_area(job_label)

# Извлечение текста
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

# Анализ
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

if st.button(analyze_btn) and resume_text and job_description:
    with st.spinner(spinner_analyze):
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
        st.subheader(analysis_title)
        st.markdown(result)

# Генерация нового резюме
if st.button(optimize_btn) and resume_text and job_description:
    with st.spinner(spinner_optimize):
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
        st.subheader(optimized_title)
        st.code(optimized, language="markdown")
