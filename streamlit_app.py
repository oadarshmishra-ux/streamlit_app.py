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

def extract_keywords(text, num_keywords=10):
    """Simple frequency-based keyword extraction (stable on Streamlit Cloud)."""
    words = text.split()
    freq = {}
    for w in words:
        if len(w) > 3:  # ignore very short words
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:num_keywords]]

def match_keywords(resume_keywords, jd_keywords):
    """Compare resume keywords with job description keywords."""
    matched = set(resume_keywords).intersection(set(jd_keywords))
    score = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
    return score, matched

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
