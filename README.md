# AI Resume Screening System 📄🚀

An automated talent matching and resume screening web application built with **Python**, **Streamlit**, **Scikit-learn**, and **Plotly**. The system parses resumes in **PDF** and **DOCX** formats, extracts technical skills and contact details, estimates years of experience and education, and computes a multi-factor composite match score against any Job Description (JD).

---

## 🌟 Key Features

- **Multi-Format Resume Parsing**:
  - Supports both `.pdf` (using `pypdf`) and `.docx` (using `python-docx`).
  - Extracts text from body paragraphs, tables, and skill grids.
  - Automatically identifies candidate **Email** and **Phone Numbers** using regex.
  - Detects unreadable or scanned documents and handles them gracefully without crashing.

- **Taxonomy-Based Skill Matching**:
  - Over 170+ standardized skills across 5 domains: *Programming & Data*, *Data Science & ML*, *Web & Frameworks*, *Databases & Cloud*, and *Tools & Soft Skills*.
  - Boundary-aware regex token matching prevents false-positive substring matches (e.g., `C` inside `C++`, `Go` inside `Google`, or `Java` inside `JavaScript`).

- **Interactive Skill Highlighting**:
  - Inside each candidate's expandable breakdown, the extracted resume text is displayed in a dedicated inspection box with all matched skills **highlighted in green (`<mark>`)**.
  - Reviewers can instantly verify context and see why each skill was identified.

- **Hybrid Similarity Engine**:
  - **TF-IDF Cosine Similarity**: Fast, lightweight keyword and content analysis running instantly on any CPU.
  - **Semantic AI Embeddings (Optional)**: Deep sentence-level semantic understanding via `sentence-transformers` (`all-MiniLM-L6-v2`) with automatic fallback to TF-IDF if offline or uninstalled.
  - **Weighted Final Scoring**: 
    $$\text{Final Score} = (0.60 \times \text{Skill Match \%}) + (0.40 \times \text{Similarity \%})$$

- **Candidate Profiling & Seniority Filtering**:
  - **Experience Extraction**: Estimates total years of experience from explicit statements and job date ranges.
  - **Education Detection**: Recognizes degrees (Ph.D., M.Tech, M.S., MCA, MBA, B.Tech, B.S., BCA, etc.).
  - **Experience Filtering**: Filter or flag candidates who do not meet minimum seniority requirements.

- **Executive Insights & Tailored Interview Prompts**:
  - Rule-based **Screening Verdict** (`Strong Fit`, `Moderate / Partial Fit`, `Low Fit`) summarizing alignment and skill gaps.
  - Generates **3 customized interview questions** tailored to the candidate's matched strengths and missing requirements.

- **Interactive Visualizations & Multi-Format Reports**:
  - Top KPI cards: Total Resumes Evaluated, Shortlisted Candidates count, and Highest Match Score.
  - Dynamic Plotly horizontal bar chart with color-coded rankings and an interactive threshold line.
  - Filterable and searchable candidate table.
  - Multi-format exports:
    - **Download All (CSV)**
    - **Download Shortlisted Only (CSV)**
    - **Download Full Screening Report (.md)** (includes JD summary, rankings, candidate verdicts, and tailored interview questions)

---

## 📁 Project Structure

```
AI Resume Screening System/
├── app.py                         # Main Streamlit web application
├── requirements.txt               # Project dependencies
├── generate_sample_resumes.py     # Helper script to create 5 sample PDF resumes
├── sample_resumes/                # Pre-generated sample resumes for instant testing
│   ├── 1_Aarav_Sharma_Data_Scientist.pdf
│   ├── 2_Liam_Smith_Frontend_Developer.pdf
│   ├── 3_Priya_Patel_Data_Analyst.pdf
│   ├── 4_Marcus_Johnson_Cloud_Backend.pdf
│   └── 5_Chloe_Taylor_Junior_IT.pdf
├── src/
│   ├── __init__.py                # Package initializer
│   ├── skills_db.py               # 170+ categorized technical & soft skills
│   ├── parser.py                  # Text extraction (PDF/DOCX), email, phone, exp & edu
│   └── matcher.py                 # Skill extraction, TF-IDF / Semantic scoring & interview Qs
└── README.md                      # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Install Dependencies
In your terminal, navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

*(Optional)* To enable deep neural embeddings using Sentence-Transformers:
```bash
pip install sentence-transformers
```
*(If omitted, the app automatically runs in standard TF-IDF mode with zero setup.)*

---

## 🚀 Running the Application

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

---

## 🧪 Testing with Sample Resumes

To generate or refresh the 5 realistic sample resumes:

```bash
python generate_sample_resumes.py
```

### Quick Live Demo Steps:
1. In the app sidebar, click **"📋 Load Sample JD (Python & ML)"** to populate the job description.
2. In the right pane (**Upload Candidate Resumes**), drag and drop the `.pdf` files from the `sample_resumes/` folder.
3. Click **"🚀 Screen Resumes"**.
4. Adjust the **"Minimum Match Score (%)"** and **"Min Experience (Years)"** sliders in the sidebar to observe real-time recalculations in metrics, chart colors, and shortlisting status.
5. Expand any candidate card to inspect:
   - Contact information & detected education.
   - Matched vs. Missing skill badges.
   - Tailored technical and behavioral interview questions.
   - **✨ Highlighted Skills Preview** showing matched skills highlighted in green directly inside the resume text.
6. Click **"📄 Download Full Screening Report (.md)"** or **"⭐ Download Shortlisted (CSV)"** to save the executive screening report.
7. Click **"🔄 Reset / Clear Results"** to reset state and screen a fresh batch of candidates.

---

## ⚖️ Scoring Formula

The system computes an objective, weighted match score:

- **Skill Match %**:
  $$\text{Skill Match} = \left(\frac{\text{Skills in both JD and Resume}}{\text{Total Skills identified in JD}}\right) \times 100$$
- **Similarity %**: Cosine similarity between the JD and Resume text (using TF-IDF or Sentence-Transformer embeddings), scaled from 0 to 100.
- **Final Weighted Score**:
  $$\text{Final Score} = \text{round}(0.60 \times \text{Skill Match} + 0.40 \times \text{Similarity}, 2)$$

---

## 📄 License
This project is open-source and available under the MIT License.
