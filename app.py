import streamlit as st
import re
import openai

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Resume Matcher", layout="centered")

lang = st.radio("🌐 Language / שפה", ["English", "עברית"], horizontal=True)

# 🗣️ UI текст на двух языках
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
    st.title("🤖 התאמת קורות חיים לתיאור משרה עם AI")
    upload_label = "📄 העלה קובץ קורות חיים (.txt, .docx או .pdf)"
    job_label = "💼 הדבק תיאור משרה"
    analyze_btn = "🔍 נתח קורות חיים"
    optimize_btn = "✍️ צור גרסה משופרת"
    analysis_title = "📋 ניתוח התאמה (Recruiter Pro):"
    optimized_title = "🧾 קורות חיים מותאמים:"
    spinner_analyze = "🧠 מבצע ניתוח..."
    spinner_optimize = "📄 יוצר קורות חיים חדשים..."

# 📄 Загрузка резюме и описание вакансии
resume_file = st.file_uploader(upload_label, type=["txt", "docx", "pdf"])
job_description = st.text_area(job_label)

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

# 📊 Подсчёт совпадений
def get_match_score(resume, job):
    keywords_resume = set(re.findall(r'\b\w+\b', resume.lower()))
    keywords_job = set(re.findall(r'\b\w+\b', job.lower()))
    matched = keywords_resume & keywords_job
    percent = int(len(matched) / len(keywords_job) * 100) if keywords_job else 0
    return percent, matched, keywords_job - keywords_resume

# 🔍 Анализ соответствия
if st.button(analyze_btn) and resume_text and job_description:
    with st.spinner(spinner_analyze):
        score_before, matched_before, missing_before = get_match_score(resume_text, job_description)
        st.subheader(analysis_title)
        st.markdown(f"**Match Score:** {score_before}%")
        st.markdown(f"**Missing Keywords:** {', '.join(sorted(missing_before)) if missing_before else 'None'}")

# ✍️ Оптимизация резюме
if st.button(optimize_btn) and resume_text and job_description:
    with st.spinner(spinner_optimize):
        prompt = f"""
You are a professional resume writer. Rewrite the resume below so that it:
- Matches the job description better
- Emphasizes relevant experience
- Adds truthful, relevant keywords only
- Keeps formatting clean (no tables)
- Does NOT invent or falsify any job, date, or skill

Job Description:
{job_description}

Original Resume:
{resume_text}
"""
        messages = [
            {"role": "system", "content": "You are a technical recruiter and resume optimizer."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
        )
        optimized_resume = response.choices[0].message.content
        st.subheader(optimized_title)
        st.code(optimized_resume, language="markdown")

        # 📊 Повторный анализ после оптимизации
        score_after, _, _ = get_match_score(optimized_resume, job_description)
        st.markdown(f"**New Match Score:** {score_after}%")
