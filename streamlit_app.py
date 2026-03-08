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
    return text.lower()  # keep symbols like C++, SQL intact

STOPWORDS = {
    "and","the","with","for","are","this","that","have","has","will",
    "role","looking","strong","foundation","graduate","fresher"
}

def weighted_extract_keywords(text, num_keywords=25):
    """Keyword extraction with stopword removal and weighted scoring."""
    text = re.sub(r'[^a-zA-Z0-9#+\s]', '', text)  # keep C++, SQL, REST
    words = text.split()
    freq = {}
    for w in words:
        w = w.lower()
        if len(w) > 2 and w not in STOPWORDS:
            # Weight technical skills higher if 'skills' section is present
            weight = 2 if "skills" in text.lower() else 1
            freq[w] = freq.get(w, 0) + weight
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:num_keywords]]

SYNONYMS = {
    "sql": ["mysql","postgresql","sqlite"],
    "rest": ["api","restful","web services"],
    "c++": ["cpp"],
    "javascript": ["js","node","node.js"],
    "html": ["html5"],
    "css": ["css3"]
}

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
        # Group missing skills into categories
        web_missing = [m for m in missing if m in ["html","css","javascript"]]
        if web_missing:
            suggestions.append(f"Consider adding web technologies: {', '.join(web_missing)}")
        backend_missing = [m for m in missing if m in ["php","django","spring","rest"]]
        if backend_missing:
            suggestions.append(f"Consider gaining backend framework experience: {', '.join(backend_missing)}")
        suggestions.append(f"Overall missing skills: {', '.join(missing)}")

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
        resume_keywords = weighted_extract_keywords(resume_text)
        jd_keywords = weighted_extract_keywords(jd_text)

        # Match & score
        score, matched = match_keywords(resume_keywords, jd_keywords)

        # Feedback
        feedback = generate_feedback(score, matched, jd_keywords)

        # Display results
        st.subheader("📊 Analysis Results")
        st.write(feedback)

        # Visualize score
        st.progress(int(score))
        st.write(f"ATS Compatibility Score: {score:.2f}%")

        # Suggestions
        st.subheader("💡 Suggestions to Improve ATS Score")
        suggestions = generate_suggestions(score, matched, jd_keywords)
        for s in suggestions:
            st.write(f"- {s}")

if __name__ == "__main__":
    main()
