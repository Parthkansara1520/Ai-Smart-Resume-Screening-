"""
generate_sample_resumes.py
Generates 5 realistic sample candidate resumes in PDF format inside the
sample_resumes/ directory for immediate testing and verification of the
AI Resume Screening System.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def create_candidate_pdf(filepath: str, data: dict):
    """Generates a professionally styled PDF resume using ReportLab."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CandidateName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'CandidateRole',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'ContactInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyContent',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    skills_style = ParagraphStyle(
        'SkillLine',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Header
    story.append(Paragraph(data["name"], title_style))
    story.append(Paragraph(data["title"], subtitle_style))
    story.append(Paragraph(data["contact"], contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_header_style))
    story.append(Paragraph(data["summary"], body_style))

    # Technical Skills
    story.append(Paragraph("TECHNICAL & PROFESSIONAL SKILLS", section_header_style))
    skill_rows = []
    for cat, sk_list in data["skills_categorized"].items():
        cat_p = Paragraph(f"<b>{cat}:</b>", skills_style)
        sk_p = Paragraph(", ".join(sk_list), skills_style)
        skill_rows.append([cat_p, sk_p])

    skill_table = Table(skill_rows, colWidths=[120, 400])
    skill_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(skill_table)
    story.append(Spacer(1, 6))

    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_header_style))
    for exp in data["experience"]:
        role_comp = f"<b>{exp['role']}</b> | {exp['company']} ({exp['period']})"
        story.append(Paragraph(role_comp, body_style))
        for bullet in exp["bullets"]:
            story.append(Paragraph(f"• {bullet}", body_style))
        story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_header_style))
    for edu in data["education"]:
        story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['institution']} ({edu['year']})", body_style))

    doc.build(story)


def main():
    output_dir = Path("sample_resumes")
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        # Candidate 1: Strong Data Science & Machine Learning fit
        {
            "filename": "1_Aarav_Sharma_Data_Scientist.pdf",
            "name": "Aarav Sharma",
            "title": "Senior Data Scientist & Machine Learning Engineer",
            "contact": "Email: aarav.sharma@example.com | Phone: +1 (555) 432-8765 | San Jose, CA",
            "summary": "Results-driven Machine Learning Engineer with 5+ years building and deploying deep learning pipelines, predictive models, and scalable analytical algorithms in Python. Passionate about natural language processing and production AI.",
            "skills_categorized": {
                "Programming & Data": ["Python", "SQL", "R", "Bash"],
                "Data Science & ML": ["Machine Learning", "Deep Learning", "Scikit-learn", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Natural Language Processing", "Statistics", "Data Analysis", "Feature Engineering"],
                "Databases & Cloud": ["PostgreSQL", "MySQL", "AWS", "Docker", "Git"]
            },
            "experience": [
                {
                    "role": "Lead Data Scientist",
                    "company": "NeuralMetrics Corp",
                    "period": "2022 - Present",
                    "bullets": [
                        "Architected end-to-end Machine Learning pipelines using Scikit-learn and PyTorch, increasing prediction accuracy by 22%.",
                        "Leveraged Pandas, NumPy, and SQL for extensive data cleaning, feature engineering, and statistical modeling across 50M+ records.",
                        "Deployed deep learning containerized services using Docker onto AWS cloud infrastructure."
                    ]
                },
                {
                    "role": "Machine Learning Engineer",
                    "company": "Apex Analytics",
                    "period": "2019 - 2022",
                    "bullets": [
                        "Built Natural Language Processing classification models using Python and TensorFlow.",
                        "Automated data extraction pipelines using SQL queries and PostgreSQL database optimization."
                    ]
                }
            ],
            "education": [
                {"degree": "M.S. in Computer Science (Machine Learning)", "institution": "Stanford University", "year": "2019"},
                {"degree": "B.S. in Statistics", "institution": "University of California, Berkeley", "year": "2017"}
            ]
        },

        # Candidate 2: Web & Frontend Developer
        {
            "filename": "2_Liam_Smith_Frontend_Developer.pdf",
            "name": "Liam Smith",
            "title": "Senior Frontend & Web Applications Engineer",
            "contact": "Email: liam.smith@example.com | Phone: +1 (555) 890-1234 | New York, NY",
            "summary": "Creative and user-focused Frontend Engineer with 4+ years architecting dynamic, accessible web applications using React, TypeScript, and modern CSS frameworks. Experienced in RESTful API integration and client-side optimization.",
            "skills_categorized": {
                "Programming & Web": ["JavaScript", "TypeScript", "HTML5", "CSS3", "Python (basic)"],
                "Web & Frameworks": ["React", "Next.js", "Node.js", "Express.js", "Redux", "Tailwind CSS", "Bootstrap", "REST API"],
                "Databases & Tools": ["MongoDB", "Git", "GitHub", "Webpack", "Vite", "Agile", "Jira"]
            },
            "experience": [
                {
                    "role": "Senior Frontend Engineer",
                    "company": "PixelCraft Studios",
                    "period": "2021 - Present",
                    "bullets": [
                        "Spearheaded redesign of enterprise SaaS dashboard using React, Next.js, and Tailwind CSS, reducing load time by 35%.",
                        "Implemented global application state management with Redux and connected backend services via REST APIs.",
                        "Collaborated closely with UX designers and backend teams using Agile and Jira."
                    ]
                },
                {
                    "role": "Web Developer",
                    "company": "BrightWave Interactive",
                    "period": "2019 - 2021",
                    "bullets": [
                        "Engineered responsive components in HTML5, CSS3, and JavaScript.",
                        "Developed lightweight backend mock microservices using Node.js and Express.js."
                    ]
                }
            ],
            "education": [
                {"degree": "B.S. in Software Engineering", "institution": "New York University", "year": "2019"}
            ]
        },

        # Candidate 3: Data Analyst
        {
            "filename": "3_Priya_Patel_Data_Analyst.pdf",
            "name": "Priya Patel",
            "title": "Senior Data & Business Intelligence Analyst",
            "contact": "Email: priya.patel@example.com | Phone: +1 (555) 321-9876 | Chicago, IL",
            "summary": "Detail-oriented Business Intelligence Analyst with 4 years extracting actionable insights from large enterprise datasets. Expert in SQL, Power BI, Excel modeling, and exploratory data analysis using Python.",
            "skills_categorized": {
                "Analytics & BI": ["SQL", "Power BI", "Tableau", "Excel", "Advanced Excel", "Data Analysis", "Data Visualization", "Statistics"],
                "Programming & Data": ["Python", "Pandas", "NumPy", "MySQL", "PostgreSQL"],
                "Tools & Soft Skills": ["Problem Solving", "Communication", "Presentation Skills", "Git", "Agile"]
            },
            "experience": [
                {
                    "role": "Senior Data Analyst",
                    "company": "InsightMatrix Partners",
                    "period": "2021 - Present",
                    "bullets": [
                        "Designed and published over 30 interactive dashboards in Power BI and Tableau for senior stakeholders.",
                        "Authored complex SQL queries, stored procedures, and ETL views across PostgreSQL databases.",
                        "Analyzed seasonal revenue trends and churn probability using Python, Pandas, and statistical modeling."
                    ]
                },
                {
                    "role": "Data Analyst",
                    "company": "Horizon Market Research",
                    "period": "2019 - 2021",
                    "bullets": [
                        "Created automated Excel models with advanced formulas and pivot tables for executive reporting.",
                        "Presented monthly business performance summaries to department directors."
                    ]
                }
            ],
            "education": [
                {"degree": "B.S. in Data Analytics & Economics", "institution": "University of Illinois Urbana-Champaign", "year": "2019"}
            ]
        },

        # Candidate 4: Backend & Cloud Engineer
        {
            "filename": "4_Marcus_Johnson_Cloud_Backend.pdf",
            "name": "Marcus Johnson",
            "title": "Senior Backend & Cloud Infrastructure Engineer",
            "contact": "Email: marcus.johnson@example.com | Phone: +1 (555) 654-7890 | Seattle, WA",
            "summary": "Backend specialist with 6+ years designing high-throughput REST APIs, asynchronous microservices, and automated cloud deployments. Extensive expertise in Python, FastAPI, Docker, Kubernetes, and AWS architecture.",
            "skills_categorized": {
                "Languages & Backend": ["Python", "FastAPI", "Flask", "Django", "SQL", "Bash", "REST API", "RESTful APIs"],
                "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "CI/CD", "GitHub Actions", "Terraform", "Linux"],
                "Databases & Tools": ["PostgreSQL", "Redis", "MySQL", "Git", "Problem Solving", "Teamwork"]
            },
            "experience": [
                {
                    "role": "Principal Backend Developer",
                    "company": "CloudWave Systems",
                    "period": "2020 - Present",
                    "bullets": [
                        "Architected scalable microservices handling 25M requests/day using Python, FastAPI, and PostgreSQL.",
                        "Implemented caching strategies using Redis, lowering database query latency by 45%.",
                        "Maintained CI/CD deployment pipelines using GitHub Actions, Docker, and Kubernetes on AWS."
                    ]
                },
                {
                    "role": "Software Engineer",
                    "company": "Vanguard Softworks",
                    "period": "2018 - 2020",
                    "bullets": [
                        "Built secure authentication and REST APIs using Python and Flask.",
                        "Managed PostgreSQL database schemas and query indexing on Linux servers."
                    ]
                }
            ],
            "education": [
                {"degree": "B.S. in Computer Science", "institution": "University of Washington", "year": "2018"}
            ]
        },

        # Candidate 5: Fresher / Junior IT Profile
        {
            "filename": "5_Chloe_Taylor_Junior_IT.pdf",
            "name": "Chloe Taylor",
            "title": "Junior Software Developer & IT Associate",
            "contact": "Email: chloe.taylor@example.com | Phone: +1 (555) 789-4561 | Atlanta, GA",
            "summary": "Motivated Computer Science graduate with strong foundational programming skills in Python, C, and Java. Eager to apply analytical problem solving, quick learning capability, and team collaboration in a growth-oriented tech role.",
            "skills_categorized": {
                "Foundational Languages": ["Python", "C", "Java", "HTML", "CSS"],
                "Tools & Systems": ["Git", "GitHub", "Linux", "Excel", "VS Code"],
                "Soft Skills": ["Problem Solving", "Communication", "Teamwork", "Adaptability", "Time Management", "Critical Thinking"]
            },
            "experience": [
                {
                    "role": "IT & Programming Intern",
                    "company": "Campus Tech Helpdesk",
                    "period": "2023 - 2024",
                    "bullets": [
                        "Assisted campus faculty with software configurations, hardware diagnostics, and Linux workstation setups.",
                        "Wrote basic Python automation scripts to parse attendance records from Excel spreadsheets.",
                        "Collaborated in a team of 6 student developers on academic projects using Git version control."
                    ]
                }
            ],
            "education": [
                {"degree": "B.S. in Information Technology", "institution": "Georgia State University", "year": "2024"}
            ]
        }
    ]

    print("Generating 5 realistic candidate resumes in sample_resumes/...")
    for c in candidates:
        filepath = output_dir / c["filename"]
        create_candidate_pdf(str(filepath), c)
        print(f"  [+] Generated: {filepath.name}")

    print("\nAll 5 sample PDF resumes successfully generated!")


if __name__ == "__main__":
    main()
