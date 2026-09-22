import os
from dotenv import load_dotenv

load_dotenv()

PROFILE = {
    "job_titles": [
        "CFD Engineer",
        "Ingénieur CFD",
        "Fluid mechanics Engineer",
        "Mécanique des fluides",
        "numerical simulation fluid dynamics engineer",
        "simulation numérique mécanique des fluides",
        "computational fluid dynamics engineer",
        "ingénieur simulation numérique mécanique des fluides",
      
    ],
    "keywords": ["Python", "Ansys Fluent", "Mécanique des fluides", "OpenFOAM", "CFD", "Simulation numérique", "Modélisation numérique", "Dynamique des fluides", "Thermique", "Heat transfer", "Multiphysics", "Multiphase flow","magnétohydrodynamique", "MHD", "Turbulence modeling", "Turbulence", "Navier-Stokes equations", "Finite volume method", "Finite element method", "Computational fluid dynamics", "CFD software", "Meshing", "Post-processing", "Data analysis", "Scientific computing"],
    "location": "France",
    "remote": True,
    "seniority": "junior",
    "excluded_keywords": ["stage", "stagiaire", "apprenti", "apprentie", "apprentissage", "alternance", "alternant", "thèse", "doctorat", "doctorant", "doctorante"],
    "contract_types": ["CDI", "CDD","Thèse","Doctorat"],
    "require_no_experience": True,
    "excluded_sectors": ["banque", "assurance", "bancaire", "assurances", " millitaire", "armée", "militaire", "défense", "défense nationale", "police", "gendarmerie", "sécurité", "sécurité intérieure", "sécurité publique"],
}

CV_TEXT = """
Issu d’une formation en physique et mécanique des fluides, 
avec un Master 2 en Dynamique des Fluides et Énergétique (Université Paris-Saclay), 
je possède une solide expérience en modélisation et simulation numérique, écoulements 
multiphasiques, couplages multiphysiques et transferts thermiques. Je présente une forte 
appétence pour la modélisation numérique et le développement de méthodes de simulation,
 et je recherche une thèse associant développement théorique, modélisation physique et
simulation numérique.
"""

