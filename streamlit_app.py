"""
AI-Powered Resume Analyzer
Author: Senior Software Engineer (15+ years experience)
Tech Stack: Python, Streamlit, PyPDF2
Purpose: Analyze resumes against job descriptions, extract keywords, and provide recruiter-style feedback.
"""

# ==============================
# 1. Import Dependencies
# ==============================
import streamlit as st
import PyPDF2
import re

# ==============================
# 2. Utility Functions
# ==============================

def extract_text_from_pdf(uploaded_file):
    """Extract raw text from uploaded PDF resume."""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_text(text):
    """Basic text cleaning for NLP processing."""
    return text.lower()

# Curated skill dictionary for fresher software developer roles
SKILL_DICTIONARY = {
    "languages": ["java","python","c++","cpp","php","javascript","html","css"],
    "databases": ["sql","mysql","postgresql","mongodb","sqlite"],
    "frameworks": ["spring boot","django","node.js","rest","api"],
    "tools": ["git","github","vs code","eclipse"],
    "concepts": ["oop","problem solving","debugging","testing","maintenance","designing","coding"]
}

SYNONYMS = {
    "sql": ["mysql","postgresql","sqlite"],
    "rest": ["api","restful","web services"],
    "c++": ["cpp"],
    "javascript": ["js","node","node.js"],
    "html": ["html5"],
    "css": ["css3"],
    "django": ["python web framework"],
    "php": ["php7","php8"]
}

def extract_skills(text):
    """Extract skills from resume/job description using curated dictionary."""
    text = re.sub(r'[^a-zA-Z0-9#+\s]', ' ', text)
    words = text.lower().split()
    found = set()
    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            if skill in text:
                found.add(skill)
    return list(found)

def normalize_keywords(keywords):
    """Normalize keywords with synonym mapping."""
    normalized = set()
    for k in keywords:
        k = k.lower()
        normalized.add(k)
        for base, variants in SYNONYMS.items():
            if k in variants:
                normalized.add(base)
    return normalized

def match_keywords(resume_keywords, jd_keywords):
    """Compare resume keywords with job description keywords using synonym mapping."""
    resume_set = normalize_keywords(resume_keywords)
    jd_set = normalize_keywords(jd_keywords)
    matched = resume_set.intersection(jd_set)
    score = (len(matched) / len(jd_set)) * 100 if jd_set else 0
    return score, matched, jd_set - matched

def generate_feedback(score, matched, missing):
    """Generate recruiter-style feedback based on keyword match."""
    feedback = f"Match Score: {score:.2f}%\n\n"
    feedback += f"✅ Matched Skills: {', '.join(sorted(matched)) if matched else 'None'}\n"
    feedback += f"❌ Missing Skills: {', '.join(sorted(missing)) if missing else 'None'}\n\n"
    if score >= 70:
        feedback += "Strong alignment with the job description."
    elif score >= 40:
        feedback += "Moderate alignment. Add missing skills to improve ATS score."
    else:
        feedback += "Low alignment. Resume needs significant improvement."
    return feedback


def generate_suggestions(score, matched, missing):
    """Provide clear, concise suggestions to improve ATS score."""
    suggestions = []

    # General advice based on score
    if score < 40:
        suggestions.append("Add more job-specific keywords.")
        suggestions.append("List technical skills clearly (Python, SQL, Java).")
        suggestions.append("Show projects that use required skills.")
    elif score < 70:
        suggestions.append("Include missing skills where relevant.")
        suggestions.append("Match resume summary to job description.")
        suggestions.append("Use consistent terms (e.g., REST API).")
    else:
        suggestions.append("Resume aligns well. Focus on formatting.")
        suggestions.append("Add measurable results (e.g., improved speed by 30%).")

    # Category-specific advice
    if missing:
        web_missing = [m for m in missing if m in ["html","css","javascript"]]
        if web_missing:
            suggestions.append(f"Add web tech: {', '.join(web_missing)}")
        backend_missing = [m for m in missing if m in ["php","django","spring boot","rest"]]
        if backend_missing:
            suggestions.append(f"Learn backend frameworks: {', '.join(backend_missing)}")
        testing_missing = [m for m in missing if m in ["testing","maintenance","designing","coding"]]
        if testing_missing:
            suggestions.append(f"Highlight testing/maintenance: {', '.join(testing_missing)}")

    return suggestions


# ==============================
# 3. Streamlit UI
# ==============================
def main():
    st.title("📄 AI-Powered Resume Analyzer")
    st.write("Upload your resume and paste a job description to get instant AI feedback.")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jd_text = st.text_area("Paste Job Description Here")

    if uploaded_file and jd_text:
        # Extract resume text
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_text = clean_text(resume_text)
        jd_text = clean_text(jd_text)

        # Extract skills
        resume_keywords = extract_skills(resume_text)
        jd_keywords = extract_skills(jd_text)

        # Match & score
        score, matched, missing = match_keywords(resume_keywords, jd_keywords)

        # Feedback
        feedback = generate_feedback(score, matched, missing)

        # Display results
        st.subheader("📊 Analysis Results")
        st.write(feedback)

        # Visualize score
        st.progress(int(score))
        st.write(f"ATS Compatibility Score: {score:.2f}%")

        # Suggestions
        st.subheader("💡 Suggestions to Improve ATS Score")
        suggestions = generate_suggestions(score, matched, missing)
        for s in suggestions:
            st.write(f"- {s}")

if __name__ == "__main__":
    main()
