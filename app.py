"""
app.py
Streamlit web application for the AI Resume Screening System.
Integrates text parsing (PDF/DOCX), contact extraction, experience & education parsing,
skill matching, hybrid similarity scoring (TF-IDF & Semantic AI with automatic fallback),
candidate filtering, smart screening verdicts, tailored interview questions,
interactive skill highlighting in resume previews, and full Markdown report export.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of execution environment
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import html
import io
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.parser import parse_resume
from src.matcher import (
    score_resume,
    extract_skills,
    is_sentence_transformers_available,
    generate_candidate_insights
)


# ---------------------------------------------------------
# Page Configuration & Custom Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Light Beige + Olive" Aesthetic
st.markdown("""
<style>
    /* 1. Main Application Background & Global Typography */
    .stApp {
        background-color: #F5F0E6 !important;
        color: #1B1F16 !important;
    }
    
    /* Global text colors */
    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1B1F16;
    }
    .stApp .stCaption, .stApp small {
        color: #3F4238 !important;
    }
    
    /* 2. Headings - Olive & Deep Charcoal Olive */
    h1, h2, h3, h4, h5, h6 {
        color: #283618 !important;
        font-weight: 700 !important;
    }
    
    /* 3. Sidebar - Soft Sand Beige */
    section[data-testid="stSidebar"] {
        background-color: #E6DEC8 !important;
        border-right: 1px solid #D4CBB3 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1B1F16 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #283618 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #D4CBB3 !important;
    }
    
    /* 4. Metric Containers & Cards - Soft Sand Beige */
    div[data-testid="metric-container"] {
        background-color: #E6DEC8 !important;
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid #B7B7A4 !important;
        box-shadow: 0 1px 3px rgba(40, 54, 24, 0.08);
    }
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #3F4238 !important;
        font-weight: 600;
        font-size: 13.5px;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #1B1F16 !important;
        font-weight: 800;
    }
    
    /* 5. Buttons - Olive Green */
    .stButton > button[kind="primary"] {
        background-color: #6B705C !important;
        color: #F5F0E6 !important;
        border: 1px solid #6B705C !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #585C4B !important;
        border-color: #585C4B !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #E6DEC8 !important;
        color: #1B1F16 !important;
        border: 1px solid #6B705C !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #DDD3BB !important;
        color: #1B1F16 !important;
    }
    
    /* Download Buttons */
    .stDownloadButton > button {
        background-color: #E6DEC8 !important;
        color: #1B1F16 !important;
        border: 1px solid #6B705C !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        background-color: #6B705C !important;
        color: #F5F0E6 !important;
    }
    
    /* 6. Form Inputs & Text Areas */
    .stTextArea textarea, .stTextInput input {
        background-color: #FAF7F0 !important;
        color: #1B1F16 !important;
        border: 1px solid #B7B7A4 !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #6B705C !important;
        box-shadow: 0 0 0 1px #6B705C !important;
    }
    
    /* File Uploader Container & Dropzone */
    div[data-testid="stFileUploader"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        background-color: #E6DEC8 !important;
        border: 2px dashed #6B705C !important;
        border-radius: 10px !important;
        padding: 24px 16px !important;
        color: #1B1F16 !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #283618 !important;
        background-color: #E0D7C0 !important;
    }
    
    /* Dropzone text: "Drag and drop file here", instructions, limits */
    [data-testid="stFileUploaderDropzone"] * {
        color: #1B1F16 !important;
    }
    [data-testid="stFileUploaderDropzone"] span {
        color: #1B1F16 !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #3F4238 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    
    /* "Browse files" button inside dropzone */
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #6B705C !important;
        color: #F5F0E6 !important;
        border: 1px solid #6B705C !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #585C4B !important;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploaderDropzone"] button * {
        color: #F5F0E6 !important;
    }
    
    /* Uploaded File List Rows */
    [data-testid="stFileUploaderFile"] {
        background-color: #E6DEC8 !important;
        border: 1px solid #B7B7A4 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        margin-top: 6px !important;
    }
    [data-testid="stFileUploaderFile"] * {
        color: #1B1F16 !important;
    }
    [data-testid="stFileUploaderFileName"] {
        color: #1B1F16 !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploaderFile"] small,
    [data-testid="stFileUploaderFileData"] {
        color: #3F4238 !important;
        font-weight: 500 !important;
    }
    
    /* 7. Expanders & Containers */
    div[data-testid="stExpander"] {
        background-color: #E6DEC8 !important;
        border: 1px solid #B7B7A4 !important;
        border-radius: 8px !important;
        margin-bottom: 8px;
    }
    div[data-testid="stExpander"] details {
        background-color: #E6DEC8 !important;
    }
    div[data-testid="stExpander"] summary {
        color: #1B1F16 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #6B705C !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid #B7B7A4 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #3F4238 !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #283618 !important;
        font-weight: 700 !important;
        border-bottom-color: #6B705C !important;
    }
    
    /* 8. Skill Badges - Sage Olive & Warm Terracotta */
    .skill-badge-matched {
        display: inline-block;
        background-color: #A5A58D;
        color: #283618;
        border: 1px solid #6B705C;
        padding: 3px 10px;
        margin: 2px 4px 2px 0;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }
    .skill-badge-missing {
        display: inline-block;
        background-color: #CB997E;
        color: #3F2212;
        border: 1px solid #A86D4F;
        padding: 3px 10px;
        margin: 2px 4px 2px 0;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }
    
    /* 9. Screening Verdict Box */
    .verdict-box {
        background-color: #E6DEC8;
        color: #1B1F16;
        border: 1px solid #B7B7A4;
        border-left: 4px solid #6B705C;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 1px 3px rgba(40, 54, 24, 0.05);
    }
    .verdict-box b, .verdict-box strong {
        color: #283618;
    }
    
    /* 10. Interview Question Cards */
    .question-box {
        background-color: #E6DEC8;
        color: #1B1F16;
        border: 1px solid #B7B7A4;
        border-left: 4px solid #6B705C;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 1px 3px rgba(40, 54, 24, 0.05);
    }
    .question-box b, .question-box strong {
        color: #283618;
    }
    
    /* 11. Resume Preview Inspection Box */
    .resume-preview-box {
        max-height: 280px;
        overflow-y: auto;
        background-color: #FAF7F0;
        border: 1px solid #B7B7A4;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #1B1F16;
        white-space: pre-wrap;
        word-break: break-word;
    }
    
    /* Matched Skill Highlight Badge inside Resume Text */
    mark.skill-highlight {
        background-color: #A5A58D;
        color: #283618;
        border: 1px solid #6B705C;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
SAMPLE_JD = """Role: Senior Python & Machine Learning Engineer

Job Overview:
We are seeking an experienced Senior Python & Machine Learning Engineer to design, build, and deploy production-grade AI solutions and scalable backend services.

Key Responsibilities & Requirements:
- 3+ years of professional development experience using Python.
- Strong hands-on expertise in Machine Learning, Deep Learning, and Scikit-learn.
- Experience with PyTorch or TensorFlow, Pandas, NumPy, and Data Analysis.
- Production experience with SQL databases (PostgreSQL, MySQL) and Redis caching.
- Practical experience with Docker, Kubernetes, and Cloud platforms (AWS or GCP).
- Experience developing and deploying REST APIs using FastAPI or Flask.
- Familiarity with CI/CD pipelines, Git, and Agile development methodologies.
- Excellent Problem Solving, Teamwork, and Communication skills.
"""

if "jd_input" not in st.session_state:
    st.session_state["jd_input"] = ""

def load_sample_jd() -> None:
    """Populates the JD text area with sample data."""
    st.session_state["jd_input"] = SAMPLE_JD

def clear_results() -> None:
    """Resets screening results and uploaded file references from session state."""
    if "screening_results" in st.session_state:
        del st.session_state["screening_results"]
    if "evaluated_jd" in st.session_state:
        del st.session_state["evaluated_jd"]


def highlight_skills_in_text(raw_text: str, matched_skills: List[str]) -> str:
    """
    Escapes raw resume text for HTML safety and highlights all detected matched skills
    using boundary-aware regex to prevent incorrect partial matches.
    """
    if not raw_text:
        return "<i>No readable text extracted.</i>"

    escaped_text = html.escape(raw_text)
    
    # Sort skills by length descending to match composite skills first (e.g. "Machine Learning" before "Learning")
    sorted_skills = sorted(matched_skills, key=len, reverse=True)
    for skill in sorted_skills:
        escaped_skill = re.escape(html.escape(skill))
        pattern = rf"(?<![a-zA-Z0-9_+#]){escaped_skill}(?![a-zA-Z0-9_+#])"
        escaped_text = re.sub(
            pattern,
            r'<mark class="skill-highlight">\g<0></mark>',
            escaped_text,
            flags=re.IGNORECASE
        )

    return escaped_text


def generate_markdown_report(
    jd_text: str,
    results: List[Dict[str, Any]],
    min_score: int,
    min_exp: int,
    sim_mode: str,
    total_screened: int,
    shortlisted_count: int,
    top_score: float
) -> str:
    """Generates an executive-level Markdown screening report."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    jd_skills = extract_skills(jd_text)

    lines = [
        "# AI Resume Screening System - Candidate Evaluation Report",
        f"**Generated On:** {now_str}  ",
        f"**Matching Engine:** {sim_mode}  ",
        f"**Score Threshold:** ≥ {min_score}%  ",
        f"**Minimum Experience Filter:** {min_exp} years  ",
        "",
        "---",
        "",
        "## 1. Job Description Summary",
        f"**Target Role:** {jd_text.splitlines()[0] if jd_text else 'N/A'}",
        f"**Identified JD Skills ({len(jd_skills)}):** {', '.join(jd_skills) if jd_skills else 'None'}",
        "",
        "---",
        "",
        "## 2. Screening Metrics & Overview",
        f"- **Total Candidates Evaluated:** {total_screened}",
        f"- **Shortlisted Candidates:** {shortlisted_count} ({(shortlisted_count/total_screened*100):.1f}%)" if total_screened else "- **Shortlisted:** 0",
        f"- **Top Match Score:** {top_score}%",
        "",
        "---",
        "",
        "## 3. Candidate Rankings",
        "",
        "| Rank | Status | Filename | Final Score | Skill Match | Similarity | Experience | Education |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |"
    ]

    for cand in results:
        lines.append(
            f"| {cand['Rank']} | {cand['Status']} | {cand['filename']} | "
            f"{cand['final_score']}% | {cand['skill_match_pct']}% | "
            f"{cand['similarity_pct']}% | {cand.get('experience_display', 'N/A')} | "
            f"{cand.get('education', 'N/A')} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Detailed Candidate Insights & Tailored Interview Questions",
        ""
    ])

    for cand in results:
        insights = cand.get("insights", {})
        verdict = insights.get("verdict_text", "").replace("**", "")
        questions = insights.get("interview_questions", [])
        matched_str = ", ".join(cand["matched_skills"]) if cand["matched_skills"] else "None"
        missing_str = ", ".join(cand["missing_skills"]) if cand["missing_skills"] else "None"

        lines.extend([
            f"### #{cand['Rank']} - {cand['filename']} ({cand['Status']})",
            f"- **Contact:** Email: `{cand['email']}` | Phone: `{cand['phone']}`",
            f"- **Experience:** {cand.get('experience_display', 'N/A')} | **Education:** {cand.get('education', 'N/A')}",
            f"- **Scores:** Final: **{cand['final_score']}%** (Skill Coverage: {cand['skill_match_pct']}%, Similarity: {cand['similarity_pct']}%)",
            f"- **Screening Verdict:** {verdict}",
            f"- **Matched Skills ({len(cand['matched_skills'])}):** {matched_str}",
            f"- **Missing Required Skills ({len(cand['missing_skills'])}):** {missing_str}",
            "",
            "**Tailored Interview Questions:**"
        ])
        for q_idx, q in enumerate(questions, start=1):
            clean_q = q.replace("**", "")
            lines.append(f"{q_idx}. {clean_q}")
        lines.append("")

    lines.extend([
        "---",
        "*Report automatically generated by AI Resume Screening System.*"
    ])

    return "\n".join(lines)


# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    st.title("📄 AI Resume Screener")
    st.markdown("Automated talent matching powered by **Semantic Similarity** and **Taxonomy Skill Extraction**.")
    st.markdown("---")
    
    st.subheader("⚙️ Screening Settings")

    # Similarity Engine Selection
    has_sentence_transformers = is_sentence_transformers_available()
    engine_choice = st.radio(
        "Similarity Engine",
        options=["TF-IDF (Fast Keyword + Text)", "Semantic AI (Neural Embeddings)"],
        index=0,
        help="TF-IDF runs instantly on any CPU. Semantic AI uses sentence-transformers (all-MiniLM-L6-v2) for deep semantic comprehension, with automatic fallback if offline."
    )
    sim_mode = "semantic" if "Semantic AI" in engine_choice else "tfidf"

    if sim_mode == "semantic":
        if has_sentence_transformers:
            st.caption("🟢 Neural embeddings active (`all-MiniLM-L6-v2`).")
        else:
            st.caption("🟡 `sentence-transformers` not detected; will safely fall back to TF-IDF.")

    min_score_threshold = st.slider(
        "Minimum Match Score (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="Candidates scoring at or above this threshold are classified as Shortlisted."
    )

    min_experience_req = st.slider(
        "Min Experience (Years)",
        min_value=0,
        max_value=10,
        value=0,
        step=1,
        help="Filter or flag candidates who do not meet the minimum required years of experience."
    )
    
    hide_under_exp = st.checkbox("Hide candidates below Min Experience", value=False)

    st.markdown("---")
    st.subheader("⚡ Quick Testing")
    st.caption("Load a pre-configured Job Description for instant testing:")
    st.button("📋 Load Sample JD (Python & ML)", on_click=load_sample_jd, use_container_width=True)

    st.markdown("---")
    st.subheader("📌 How it Works")
    st.markdown("""
    1. **Paste Job Description**: Provide the role requirements and qualifications.
    2. **Upload Resumes**: Upload multiple `.pdf` or `.docx` candidate resumes.
    3. **Screen & Analyze**: Candidates are ranked by overall weighted fit:
       - **60%** Skill Coverage
       - **40%** Text/Semantic Similarity
    4. **Inspect Insights**: View screening verdicts, experience/education extraction, and custom interview prompts.
    5. **Export**: Download shortlisted or complete results in CSV or Markdown report.
    """)
    st.caption("AI Resume Screening System v1.3")


# ---------------------------------------------------------
# Main Header & Inputs
# ---------------------------------------------------------
st.header("🎯 Candidate Screening & Matching Dashboard")
st.write("Match candidates against your job description with instant skill gap analysis, experience verification, and semantic ranking.")

col_jd, col_upload = st.columns([1, 1], gap="large")

with col_jd:
    st.subheader("1. Job Description")
    jd_text = st.text_area(
        label="Paste or edit the Job Description:",
        key="jd_input",
        height=260,
        placeholder="Paste role requirements, technical skills, and responsibilities here..."
    )
    if jd_text.strip():
        extracted_jd_skills = extract_skills(jd_text)
        st.caption(f"💡 Detected **{len(extracted_jd_skills)}** key skills in JD: " + 
                   (", ".join(extracted_jd_skills[:8]) + ("..." if len(extracted_jd_skills) > 8 else "") if extracted_jd_skills else "None"))

with col_upload:
    st.subheader("2. Upload Candidate Resumes")
    uploaded_files = st.file_uploader(
        label="Upload resumes in PDF or DOCX format:",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="You can drag and drop multiple PDF or DOCX files here."
    )
    if uploaded_files:
        st.success(f"📂 **{len(uploaded_files)}** file(s) selected for screening.")

st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    screen_button = st.button("🚀 Screen Resumes", type="primary", use_container_width=True)
with btn_col2:
    st.button("🔄 Reset / Clear Results", on_click=clear_results, use_container_width=True)


# ---------------------------------------------------------
# Screening Execution Logic
# ---------------------------------------------------------
if screen_button:
    if not jd_text.strip():
        st.error("⚠️ Please paste or load a Job Description before proceeding.")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one resume (.pdf or .docx) to screen.")
    else:
        results: List[Dict[str, Any]] = []
        progress_bar = st.progress(0, text="Starting resume parsing...")
        total_files = len(uploaded_files)

        for idx, file in enumerate(uploaded_files):
            progress_bar.progress(
                (idx + 1) / total_files,
                text=f"Analyzing resume {idx + 1}/{total_files}: {file.name}"
            )
            parsed = parse_resume(file)
            scored = score_resume(jd_text, parsed["text"], similarity_mode=sim_mode)

            candidate_dict = {
                "filename": parsed["filename"],
                "email": parsed["email"],
                "phone": parsed["phone"],
                "experience_years": parsed.get("experience_years", 0.0),
                "experience_display": parsed.get("experience_display", "Not Specified"),
                "education": parsed.get("education", "Not Specified"),
                "text": parsed["text"],
                "is_empty": parsed.get("is_empty", False),
                "word_count": parsed.get("word_count", 0),
                "status_note": parsed.get("status_note", ""),
                "final_score": scored["final_score"],
                "skill_match_pct": scored["skill_match_pct"],
                "similarity_pct": scored["similarity_pct"],
                "similarity_engine": scored.get("similarity_engine", "TF-IDF"),
                "matched_skills": scored["matched_skills"],
                "missing_skills": scored["missing_skills"],
                "jd_skills": scored["jd_skills"],
                "resume_skills": scored["resume_skills"]
            }

            # Generate smart insights & interview questions
            insights = generate_candidate_insights(candidate_dict)
            candidate_dict["insights"] = insights

            results.append(candidate_dict)

        progress_bar.empty()
        st.session_state["screening_results"] = results
        st.session_state["evaluated_jd"] = jd_text


# ---------------------------------------------------------
# Display Results, Analytics & Export
# ---------------------------------------------------------
if "screening_results" in st.session_state and st.session_state["screening_results"]:
    all_results = st.session_state["screening_results"]

    # Filter by experience if selected
    if min_experience_req > 0 and hide_under_exp:
        results = [r for r in all_results if r["experience_years"] >= min_experience_req or r.get("is_empty")]
    else:
        results = all_results

    # Sort candidates by final score descending
    sorted_results = sorted(results, key=lambda r: r["final_score"], reverse=True)
    for rank, item in enumerate(sorted_results, start=1):
        item["Rank"] = rank
        under_exp = (min_experience_req > 0 and item["experience_years"] < min_experience_req and not item.get("is_empty"))
        
        if item.get("is_empty"):
            item["Status"] = "⚠️ Unreadable"
        elif item["final_score"] >= min_score_threshold:
            item["Status"] = "Shortlisted" if not under_exp else "Shortlisted (Low Exp)"
        else:
            item["Status"] = "Under Review"

    st.markdown("---")

    # Unreadable file warning banner
    unreadable_files = [r["filename"] for r in sorted_results if r.get("is_empty")]
    if unreadable_files:
        st.warning(
            f"⚠️ **{len(unreadable_files)} document(s)** contained no extractable text "
            f"(e.g., scanned images or empty files): `{', '.join(unreadable_files)}`. "
            "These received a 0% match score and may require OCR preprocessing."
        )

    st.subheader("📊 Screening Summary & Key Metrics")

    # Metrics
    total_screened = len(sorted_results)
    shortlisted_candidates = [
        r for r in sorted_results 
        if r["final_score"] >= min_score_threshold and not r.get("is_empty")
        and (min_experience_req == 0 or r["experience_years"] >= min_experience_req)
    ]
    shortlisted_count = len(shortlisted_candidates)
    top_score = sorted_results[0]["final_score"] if sorted_results else 0.0
    top_candidate_name = sorted_results[0]["filename"] if sorted_results else "N/A"

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="Total Resumes Evaluated", value=total_screened)
    with m_col2:
        st.metric(
            label="Shortlisted Candidates",
            value=f"{shortlisted_count} / {total_screened}",
            delta=f"Threshold ≥ {min_score_threshold}% | Exp ≥ {min_experience_req}y"
        )
    with m_col3:
        st.metric(
            label="Highest Match Score",
            value=f"{top_score}%",
            delta=f"Top: {top_candidate_name}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Plotly Bar Chart
    # ---------------------------------------------------------
    st.subheader("📈 Candidate Score Comparison")
    
    chart_candidates = [r["filename"] for r in reversed(sorted_results)]
    chart_scores = [r["final_score"] for r in reversed(sorted_results)]
    chart_skill_pct = [r["skill_match_pct"] for r in reversed(sorted_results)]
    chart_sim_pct = [r["similarity_pct"] for r in reversed(sorted_results)]
    chart_exp = [r.get("experience_display", "N/A") for r in reversed(sorted_results)]
    chart_engine = [r.get("similarity_engine", "TF-IDF") for r in reversed(sorted_results)]

    chart_colors = [
        "#B7B7A4" if r.get("is_empty") else ("#6B705C" if r["final_score"] >= min_score_threshold else "#CB997E")
        for r in reversed(sorted_results)
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=chart_candidates,
        x=chart_scores,
        orientation='h',
        marker=dict(color=chart_colors, line=dict(color="#3F4238", width=1)),
        text=[f"{s}%" for s in chart_scores],
        textposition='outside',
        textfont=dict(color="#1B1F16", size=12),
        customdata=list(zip(chart_skill_pct, chart_sim_pct, chart_exp, chart_engine)),
        hovertemplate=(
            "<b>Candidate:</b> %{y}<br>" +
            "<b>Final Score:</b> %{x}%<br>" +
            "<b>Skill Match:</b> %{customdata[0]}%<br>" +
            "<b>Similarity:</b> %{customdata[1]}% (%{customdata[3]})<br>" +
            "<b>Experience:</b> %{customdata[2]}<extra></extra>"
        )
    ))

    # Add minimum score threshold line
    fig.add_vline(
        x=min_score_threshold,
        line_width=2,
        line_dash="dash",
        line_color="#A5382B",
        annotation_text=f"Threshold ({min_score_threshold}%)",
        annotation_position="top right",
        annotation_font_color="#A5382B",
        annotation_font_size=12
    )

    fig.update_layout(
        title=dict(
            text="Candidate Match Ranking vs Minimum Score Threshold",
            font=dict(color="#1B1F16", size=16, family="sans-serif")
        ),
        xaxis=dict(
            title=dict(text="Final Match Score (%)", font=dict(color="#1B1F16", size=13)),
            range=[0, 105],
            gridcolor="#D4CBB3",
            linecolor="#3F4238",
            linewidth=1.5,
            tickfont=dict(color="#1B1F16", size=12)
        ),
        yaxis=dict(
            title=dict(text="Candidate Resume", font=dict(color="#1B1F16", size=13)),
            automargin=True,
            linecolor="#3F4238",
            linewidth=1.5,
            tickfont=dict(color="#1B1F16", size=12)
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        height=max(320, len(sorted_results) * 45),
        plot_bgcolor="#F5F0E6",
        paper_bgcolor="#F5F0E6",
        font=dict(color="#1B1F16", size=13, family="sans-serif")
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # Ranked Table & Multi-Format Reports Export
    # ---------------------------------------------------------
    st.subheader("📋 Ranked Candidates Overview & Export Reports")

    table_data = []
    for r in sorted_results:
        table_data.append({
            "Rank": r["Rank"],
            "Status": r["Status"],
            "Filename": r["filename"],
            "Email": r["email"],
            "Phone": r["phone"],
            "Experience": r.get("experience_display", "Not Specified"),
            "Education": r.get("education", "Not Specified"),
            "Final Score (%)": r["final_score"],
            "Skill Match (%)": r["skill_match_pct"],
            "Similarity (%)": r["similarity_pct"],
            "Engine": r.get("similarity_engine", "TF-IDF"),
            "Matched Skills": ", ".join(r["matched_skills"]) if r["matched_skills"] else "None",
            "Missing Skills": ", ".join(r["missing_skills"]) if r["missing_skills"] else "None"
        })

    df_results = pd.DataFrame(table_data)

    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Final Score (%)": st.column_config.ProgressColumn(
                "Final Score (%)",
                help="Weighted composite score: 60% skills + 40% similarity",
                format="%.2f%%",
                min_value=0,
                max_value=100
            ),
            "Skill Match (%)": st.column_config.NumberColumn(
                "Skill Match (%)",
                format="%.2f%%"
            ),
            "Similarity (%)": st.column_config.NumberColumn(
                "Similarity (%)",
                format="%.2f%%"
            ),
        }
    )

    # Export Buttons (CSV & Markdown Report)
    col_dl_all, col_dl_short, col_dl_md = st.columns([1, 1, 1.2])
    with col_dl_all:
        csv_all = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All (CSV)",
            data=csv_all,
            file_name="all_resume_screening_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_dl_short:
        df_short = df_results[
            (df_results["Final Score (%)"] >= min_score_threshold) & 
            (~df_results["Status"].str.contains("Unreadable"))
        ]
        csv_short = df_short.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⭐ Download Shortlisted (CSV)",
            data=csv_short,
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_dl_md:
        evaluated_jd_str = st.session_state.get("evaluated_jd", jd_text)
        md_report_data = generate_markdown_report(
            jd_text=evaluated_jd_str,
            results=sorted_results,
            min_score=min_score_threshold,
            min_exp=min_experience_req,
            sim_mode=engine_choice,
            total_screened=total_screened,
            shortlisted_count=shortlisted_count,
            top_score=top_score
        )
        st.download_button(
            label="📄 Download Full Screening Report (.md)",
            data=md_report_data.encode('utf-8'),
            file_name="candidate_screening_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Detailed Candidate Breakdowns, Insights & Skill Highlights
    # ---------------------------------------------------------
    st.subheader("🔍 Smart Candidate Insights & Skill Highlighting")

    for cand in sorted_results:
        is_shortlisted = cand["final_score"] >= min_score_threshold and not cand.get("is_empty")
        status_label = "✅ Shortlisted" if is_shortlisted else "⚠️ Under Review"
        if cand.get("is_empty"):
            status_label = "⚠️ Unreadable"

        expander_title = (
            f"#{cand['Rank']} - {cand['filename']} | Score: {cand['final_score']}% | "
            f"Exp: {cand.get('experience_display', 'N/A')} ({status_label})"
        )

        with st.expander(expander_title, expanded=(cand['Rank'] == 1)):
            insights = cand.get("insights", {})

            # Screening Verdict Card
            verdict_text = insights.get("verdict_text", "")
            verdict_badge = insights.get("verdict_badge", "General")
            verdict_color = "#6B705C" if cand["final_score"] >= min_score_threshold else "#CB997E"
            formatted_verdict = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #283618;">\1</strong>', verdict_text)

            st.markdown(
                f'<div class="verdict-box" style="border-left-color: {verdict_color};">'
                f'<b style="color: #283618;">Screening Verdict:</b> {formatted_verdict}'
                f'</div>',
                unsafe_allow_html=True
            )

            detail_col1, detail_col2 = st.columns([1, 1])

            with detail_col1:
                st.markdown(f"**Email:** `{cand['email']}`")
                st.markdown(f"**Phone:** `{cand['phone']}`")
                st.markdown(f"**Experience:** `{cand.get('experience_display', 'Not Specified')}`")
                st.markdown(f"**Education:** `{cand.get('education', 'Not Specified')}`")
                st.markdown(f"**Skill Match:** `{cand['skill_match_pct']}%` ({len(cand['matched_skills'])} of {len(cand['jd_skills'])} JD skills)")
                st.markdown(f"**Content Similarity:** `{cand['similarity_pct']}%` *(Engine: {cand.get('similarity_engine', 'TF-IDF')})*")

            with detail_col2:
                st.markdown("**Matched Skills (Found in Resume):**")
                if cand["matched_skills"]:
                    matched_html = "".join([f'<span class="skill-badge-matched">{s}</span>' for s in cand["matched_skills"]])
                    st.markdown(matched_html, unsafe_allow_html=True)
                else:
                    st.caption("No matching JD skills identified.")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Missing Skills (Required by JD):**")
                if cand["missing_skills"]:
                    missing_html = "".join([f'<span class="skill-badge-missing">{s}</span>' for s in cand["missing_skills"]])
                    st.markdown(missing_html, unsafe_allow_html=True)
                else:
                    st.success("None! Candidate possesses all identified JD skills.")

            # Tailored Interview Questions
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 💡 Tailored Interview Questions")
            questions = insights.get("interview_questions", [])
            for q_idx, q_text in enumerate(questions, start=1):
                formatted_q = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #283618;">\1</strong>', q_text)
                st.markdown(
                    f'<div class="question-box"><b style="color: #6B705C; margin-right: 6px;">Q{q_idx}:</b>{formatted_q}</div>',
                    unsafe_allow_html=True
                )

            # Resume Text Preview with Skill Match Highlighting
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📄 Resume Text Inspection & Skill Highlighting")
            st.caption("Review extracted resume text with matched technical skills highlighted in green:")

            tab_highlight, tab_raw = st.tabs(["✨ Highlighted Skills Preview", "📝 Raw Extracted Text"])
            
            with tab_highlight:
                highlighted_html = highlight_skills_in_text(cand["text"], cand["matched_skills"])
                st.markdown(
                    f'<div class="resume-preview-box">{highlighted_html}</div>',
                    unsafe_allow_html=True
                )

            with tab_raw:
                st.text_area(
                    label=f"Raw text extracted from {cand['filename']}:",
                    value=cand["text"] if cand["text"] else "No text extracted.",
                    height=240,
                    disabled=True,
                    key=f"text_area_{cand['Rank']}"
                )
