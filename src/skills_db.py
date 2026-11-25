"""
skills_db.py
Defines the skills database categorized by domain and provides helper
utilities to access and query recognized skills.
"""

from typing import Dict, List

SKILLS_DB: Dict[str, List[str]] = {
    "Programming & Data": [
        "Python", "Java", "C", "C++", "C#", "R", "Go", "Rust", "Ruby", "PHP",
        "Swift", "Kotlin", "TypeScript", "JavaScript", "SQL", "PL/SQL", "Scala",
        "Shell Scripting", "Bash", "PowerShell", "Perl", "Dart", "Julia", "MATLAB",
        "SAS", "VBA", "Lua", "Groovy"
    ],
    "Data Science & ML": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
        "Computer Vision", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Pandas",
        "NumPy", "SciPy", "Matplotlib", "Seaborn", "Hugging Face", "Transformers",
        "LLMs", "Large Language Models", "LangChain", "LlamaIndex", "Generative AI",
        "GenAI", "OpenAI", "Prompt Engineering", "XGBoost", "LightGBM", "CatBoost",
        "Data Analysis", "Data Mining", "Feature Engineering", "Statistics",
        "Statistical Modeling", "A/B Testing", "Time Series Analysis", "Big Data",
        "Apache Spark", "PySpark", "Hadoop", "Databricks", "Apache Kafka", "MLOps",
        "MLflow", "DVC", "Kubeflow", "Data Visualization", "Data Engineering",
        "Neural Networks", "CNN", "RNN", "LSTM", "BERT", "GPT", "Reinforcement Learning"
    ],
    "Web & Frameworks": [
        "React", "Angular", "Vue.js", "Node.js", "Express.js", "Next.js", "Nuxt.js",
        "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "ASP.NET Core",
        "Ruby on Rails", "Laravel", "HTML", "HTML5", "CSS", "CSS3", "Tailwind CSS",
        "Bootstrap", "Sass", "GraphQL", "REST API", "RESTful APIs", "Redux", "Svelte",
        "jQuery", "WebSockets", "Webpack", "Vite", "Streamlit", "Gradio", "NestJS"
    ],
    "Databases & Cloud": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle",
        "Microsoft SQL Server", "Cassandra", "DynamoDB", "Elasticsearch", "Firebase",
        "Supabase", "Snowflake", "BigQuery", "AWS", "Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "Terraform", "Ansible", "CI/CD", "Jenkins",
        "GitHub Actions", "GitLab CI", "Linux", "Unix", "Nginx", "Apache",
        "Neo4j", "MariaDB"
    ],
    "Tools & Soft Skills": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello",
        "Postman", "Swagger", "Power BI", "Tableau", "Excel", "Advanced Excel",
        "Agile", "Scrum", "Kanban", "Problem Solving", "Communication",
        "Leadership", "Teamwork", "Critical Thinking", "Project Management",
        "Time Management", "Adaptability", "Collaboration", "Analytical Thinking",
        "Presentation Skills", "Mentoring", "Negotiation", "Cross-functional Collaboration"
    ]
}


def get_all_skills() -> List[str]:
    """
    Returns a clean, deduplicated list of all skills across all categories in SKILLS_DB,
    sorted alphabetically for consistent querying.
    """
    all_skills = set()
    for _, skills in SKILLS_DB.items():
        for skill in skills:
            clean_skill = skill.strip()
            if clean_skill:
                all_skills.add(clean_skill)
    return sorted(list(all_skills), key=lambda x: x.lower())
