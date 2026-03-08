"""
AI-Powered Resume Analyzer
Author: Senior Software Engineer (15+ years experience)
Tech Stack: Python, Streamlit, Hugging Face Transformers, PyPDF2
Purpose: Analyze resumes against job descriptions, extract keywords, and provide recruiter-style feedback.
"""

# ==============================
# 1. Import Dependencies
# ==============================
import streamlit as st
import PyPDF2
from transformers import pipeline
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
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

STOPWORDS = {"and","the","with","for","are","this","that","have","has","will","role","looking"}

def extract_keywords(text, num_keywords=15):
    """Improved keyword extraction with stopword removal and tech term preservation."""
    text = re.sub(r'[^a-zA-Z0-9#+\s]', '', text)  # keep C++, SQL, REST
    words = text.split()
    freq = {}
    for w in words:
        w = w.lower()
        if len(w) > 2 and w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:num_keywords]]

def match_keywords(resume_keywords, jd_keywords):
    resume_set = set([w.lower() for w in resume_keywords])
    jd_set = set([w.lower() for w in jd_keywords])
    matched = resume_set.intersection(jd_set)
    score = (len(matched) / len(jd_set)) * 100 if jd_set else 0
    return score, matched

SYNONYMS = {
    "sql": ["mysql","postgresql"],
    "rest": ["api","web services"],
    "c++": ["cpp"]
}

def normalize_keywords(keywords):
    normalized = set()
    for k in keywords:
        k = k.lower()
        normalized.add(k)
        for base, variants in SYNONYMS.items():
            if k in variants:
                normalized.add(base)
    return normalized

def generate_feedback(score, matched, jd_keywords):
    """Generate recruiter-style feedback based on keyword match."""
    missing = set(jd_keywords) - matched
    feedback = f"Match Score: {score:.2f}%\n\n"
    feedback += f"✅ Matched Skills: {', '.join(matched) if matched else 'None'}\n"
    feedback += f"❌ Missing Skills: {', '.join(missing) if missing else 'None'}\n\n"
    if score >= 70:
        feedback += "Strong resume alignment with job description. Ready for recruiter review!"
    elif score >= 40:
        feedback += "Moderate alignment. Consider adding missing skills to improve ATS score."
    else:
        feedback += "Low alignment. Resume needs significant improvement to match job requirements."
    return feedback

def generate_suggestions(score, matched, jd_keywords):
    """Provide actionable suggestions to improve ATS score."""
    missing = set(jd_keywords) - matched
    suggestions = []

    if score < 40:
        suggestions.append("Revise your resume to include more job-specific keywords.")
        suggestions.append("Highlight technical skills explicitly (e.g., Python, SQL, Java).")
        suggestions.append("Add project details that demonstrate required skills.")
    elif score < 70:
        suggestions.append("Incorporate missing skills into your resume where relevant.")
        suggestions.append("Tailor your resume summary to match the job description.")
        suggestions.append("Use consistent terminology (e.g., 'REST API' instead of 'web services').")
    else:
        suggestions.append("Your resume aligns well. Focus on formatting and clarity.")
        suggestions.append("Add measurable achievements (e.g., 'Improved query speed by 30%').")

    if missing:
        suggestions.append(f"Consider gaining or showcasing experience in: {', '.join(missing)}")

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

        # Extract keywords
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(jd_text)

        # Match & score
        score, matched = match_keywords(resume_keywords, jd_keywords)

        # Feedback
        feedback = generate_feedback(score, matched, jd_keywords)

        # Display results
        st.subheader("📊 Analysis Results")
        st.write(feedback)

        # Optional: Visualize score
        st.progress(int(score))
        st.write(f"ATS Compatibility Score: {score:.2f}%")

if __name__ == "__main__":
    main()
