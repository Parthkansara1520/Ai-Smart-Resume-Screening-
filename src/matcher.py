"""
matcher.py
Provides text cleaning, boundary-aware skill extraction from SKILLS_DB,
multi-factor resume scoring against job descriptions, hybrid similarity engines
(TF-IDF and Sentence-Transformers Semantic AI with automatic fallback), and
AI-driven candidate screening insights & tailored interview questions.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.skills_db import get_all_skills

# Global cache for sentence-transformers model instance
_EMBEDDING_MODEL_CACHE: Dict[str, Any] = {}


def clean_text(text: str) -> str:
    """
    Cleans raw text by converting to lowercase and stripping non-alphanumeric
    characters, while preserving characters useful for technical skills (+, #, ., -).
    """
    if not text:
        return ""
    cleaned = text.lower()
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    cleaned = re.sub(r'[^a-z0-9\s+#.-]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def extract_skills(text: str, skills_list: Optional[List[str]] = None) -> List[str]:
    """
    Matches skills from SKILLS_DB in the input text using case-insensitive
    boundary regex checks to avoid substring false matches (e.g., 'C' in 'C++',
    'Go' in 'Google', or 'Java' in 'JavaScript').

    Returns a clean, sorted list of recognized skills.
    """
    if not text or not text.strip():
        return []

    if skills_list is None:
        skills_list = get_all_skills()

    matched_skills = []
    for skill in skills_list:
        escaped_skill = re.escape(skill)
        pattern = rf"(?<![a-zA-Z0-9_+#]){escaped_skill}(?![a-zA-Z0-9_+#])"
        if re.search(pattern, text, re.IGNORECASE):
            matched_skills.append(skill)

    return sorted(matched_skills, key=lambda s: s.lower())


def is_sentence_transformers_available() -> bool:
    """Checks whether the sentence_transformers package is available in the environment."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def get_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> Any:
    """
    Loads and caches the SentenceTransformer embedding model.
    Returns None if sentence-transformers is not installed or model loading fails.
    """
    global _EMBEDDING_MODEL_CACHE
    if model_name in _EMBEDDING_MODEL_CACHE:
        return _EMBEDDING_MODEL_CACHE[model_name]

    if not is_sentence_transformers_available():
        _EMBEDDING_MODEL_CACHE[model_name] = None
        return None

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        _EMBEDDING_MODEL_CACHE[model_name] = model
        return model
    except Exception:
        _EMBEDDING_MODEL_CACHE[model_name] = None
        return None


def compute_tfidf_similarity(jd_text: str, resume_text: str) -> float:
    """
    Computes cosine similarity (0 to 100) between JD and Resume using TF-IDF.
    """
    cleaned_jd = clean_text(jd_text)
    cleaned_resume = clean_text(resume_text)

    if not cleaned_jd or not cleaned_resume:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([cleaned_jd, cleaned_resume])
        cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(cos_sim) * 100.0, 2)
    except Exception:
        return 0.0


def compute_semantic_similarity(
    jd_text: str,
    resume_text: str,
    model: Optional[Any] = None
) -> Tuple[float, bool]:
    """
    Computes cosine similarity between JD and Resume embeddings using sentence-transformers.
    Returns (similarity_pct, success_bool). If model is unavailable, success_bool is False.
    """
    if model is None:
        model = get_embedding_model("all-MiniLM-L6-v2")

    if model is None:
        return 0.0, False

    try:
        from sentence_transformers import util
        # Encode JD and resume text into neural embeddings
        embeddings = model.encode([jd_text, resume_text], convert_to_tensor=True)
        cos_sim = util.cos_sim(embeddings[0], embeddings[1]).item()
        sim_pct = round(max(0.0, float(cos_sim) * 100.0), 2)
        return sim_pct, True
    except Exception:
        return 0.0, False


def score_resume(
    jd_text: str,
    resume_text: str,
    similarity_mode: str = "tfidf",
    embedding_model: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Calculates candidate resume fit against a job description:
      - skill_match_pct: percentage of skills found in jd_text also present in resume_text
      - similarity_pct: similarity percentage using either TF-IDF or Semantic AI Embeddings
      - final_score: weighted score round((0.60 * skill_match_pct) + (0.40 * similarity_pct), 2)

    Supports similarity_mode: 'tfidf' or 'semantic'.
    Gracefully falls back to TF-IDF if 'semantic' is chosen but unavailable.
    """
    jd_skills = extract_skills(jd_text)

    # Edge Case: Empty or unreadable resume text
    if not resume_text or not resume_text.strip():
        return {
            "final_score": 0.0,
            "skill_match_pct": 0.0,
            "similarity_pct": 0.0,
            "similarity_engine": "None (Empty Text)",
            "matched_skills": [],
            "missing_skills": jd_skills,
            "jd_skills": jd_skills,
            "resume_skills": []
        }

    resume_skills = extract_skills(resume_text)

    # Calculate skill overlaps
    matched_skills = sorted(list(set(jd_skills) & set(resume_skills)), key=lambda s: s.lower())
    missing_skills = sorted(list(set(jd_skills) - set(resume_skills)), key=lambda s: s.lower())

    if jd_skills:
        skill_match_pct = round((len(matched_skills) / len(jd_skills)) * 100.0, 2)
    else:
        skill_match_pct = 0.0

    # Calculate Similarity based on selected mode
    similarity_pct = 0.0
    engine_used = "TF-IDF"

    if similarity_mode == "semantic":
        sem_score, success = compute_semantic_similarity(jd_text, resume_text, embedding_model)
        if success:
            similarity_pct = sem_score
            engine_used = "Semantic AI (all-MiniLM-L6-v2)"
        else:
            # Fallback cleanly to TF-IDF
            similarity_pct = compute_tfidf_similarity(jd_text, resume_text)
            engine_used = "TF-IDF (Neural Fallback)"
    else:
        similarity_pct = compute_tfidf_similarity(jd_text, resume_text)
        engine_used = "TF-IDF"

    # Weighted final score: 60% skill match, 40% overall semantic/content similarity
    final_score = round((0.60 * skill_match_pct) + (0.40 * similarity_pct), 2)

    return {
        "final_score": final_score,
        "skill_match_pct": skill_match_pct,
        "similarity_pct": similarity_pct,
        "similarity_engine": engine_used,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "jd_skills": jd_skills,
        "resume_skills": resume_skills
    }


def generate_candidate_insights(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a concise rule-based screening verdict and 3 tailored technical/behavioral
    interview questions based on the candidate's matched skills and identified skill gaps.
    """
    final_score = candidate.get("final_score", 0.0)
    matched = candidate.get("matched_skills", [])
    missing = candidate.get("missing_skills", [])
    exp_display = candidate.get("experience_display", "Not Specified")
    edu = candidate.get("education", "Not Specified")

    # 1. Screening Verdict
    if final_score >= 65.0:
        verdict_badge = "Strong Fit"
        verdict_color = "#6B705C"  # Olive Green
        top_skills = ", ".join(matched[:4]) if matched else "General technical skills"
        verdict_text = (
            f"**Strong Fit ({final_score}%)**: High technical alignment across {len(matched)} matched competencies "
            f"({top_skills}). Experience level ({exp_display}) and background ({edu}) align well with core role demands."
        )
        if missing:
            verdict_text += f" Gaps to verify during interview: {', '.join(missing[:3])}."
    elif final_score >= 40.0:
        verdict_badge = "Moderate / Partial Fit"
        verdict_color = "#CB997E"  # Warm Terracotta
        top_skills = ", ".join(matched[:3]) if matched else "Foundational overlap"
        gaps = ", ".join(missing[:3]) if missing else "None"
        verdict_text = (
            f"**Moderate Fit ({final_score}%)**: Shows relevant competencies in {top_skills}, but lacks direct evidence "
            f"for key requirements ({gaps}). Recommend assessing hands-on depth and learning ramp-up potential."
        )
    else:
        verdict_badge = "Low Fit"
        verdict_color = "#A5382B"  # Terracotta Red
        gaps = ", ".join(missing[:4]) if missing else "role requirements"
        verdict_text = (
            f"**Low Alignment ({final_score}%)**: Limited keyword and semantic overlap with the job description. "
            f"Lacks key core competencies: {gaps}."
        )

    # 2. Tailored Interview Questions
    questions: List[str] = []

    # Question 1: Deep dive into top matched skill
    if matched:
        primary = matched[0]
        secondary = matched[1] if len(matched) > 1 else None
        if secondary:
            q1 = f"Can you describe an end-to-end production project where you combined **{primary}** and **{secondary}**? What architectural trade-offs did you make?"
        else:
            q1 = f"Can you detail your production experience with **{primary}**? How do you ensure maintainability, performance, and testing standards?"
    else:
        q1 = "What software systems or technical architectures have you spent the majority of your time building over the past 2 years?"
    questions.append(q1)

    # Question 2: Probe requirement gap or missing skills
    if missing:
        primary_gap = missing[0]
        q2 = f"This position requires working with **{primary_gap}**. What is your current level of familiarity with this or adjacent technologies, and what is your strategy for mastering it quickly?"
    else:
        q2 = "How do you design scalable error-handling, logging, and automated CI/CD deployment pipelines for enterprise applications?"
    questions.append(q2)

    # Question 3: Problem solving / system resilience
    if len(matched) >= 3:
        anchor_skill = matched[-1]
        q3 = f"Describe a scenario where a system using **{anchor_skill}** encountered severe performance bottlenecks, data anomalies, or unexpected downtime. How did you isolate and resolve the issue?"
    else:
        q3 = "Can you describe a challenging technical roadblock you encountered in a recent project and walk us through your step-by-step diagnostic process?"
    questions.append(q3)

    return {
        "verdict_badge": verdict_badge,
        "verdict_color": verdict_color,
        "verdict_text": verdict_text,
        "interview_questions": questions
    }
