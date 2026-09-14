import os
from dotenv import load_dotenv

load_dotenv()

PROFILE = {
    "job_titles": [
        "Data Engineer",
        "Ingénieur Data",
        "Data Analyst",
        "Analyste Data",
        "Data Scientist",
        "Développeur BI",
        "Ingénieur BI",
        "Consultant Data",
        "ETL Developer",
        "Développeur ETL",
        "AI Engineer",
        "Ingénieur IA",
    ],
    "keywords": ["Python", "SQL", "Machine Learning", "ETL"],
    "location": "France",
    "remote": True,
    "seniority": "junior",
    "excluded_keywords": ["stage", "stagiaire", "apprenti", "apprentie", "apprentissage", "alternance", "alternant"],
    "contract_types": ["CDI", "CDD"],
    "require_no_experience": True,
    "excluded_sectors": ["banque", "assurance", "bancaire", "assurances", "services financiers"],
}

CV_TEXT = """
Data Engineer Junior. Master 2 Ingénierie, Mathématiques et Biostatistique
(Université Paris Cité). Stage Data Analyst/Data Engineer chez Danone :
conception et déploiement de pipelines multi-régions sur Databricks
(Europe, Amériques, Asie), modélisation de tables analytics, dashboards
de monitoring, application Streamlit end-to-end avec CI/CD, assistant IA
(Genie Space) intégré à Databricks. Compétences : PySpark, SQL, Python
(pandas, scikit-learn, PyTorch), R, Databricks, Delta Lake, Unity Catalog,
Power BI. Formation en analyse de survie, deep learning, machine learning,
statistique, séries temporelles, SQL et Big Data. Certifications Databricks
(Fundamentals, Generative AI Fundamentals, AI Agent Fundamentals).
"""

FRANCE_TRAVAIL_CLIENT_ID = os.getenv("FT_CLIENT_ID")
FRANCE_TRAVAIL_CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")