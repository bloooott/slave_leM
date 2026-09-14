import re
from config import PROFILE

SENIOR_FLAGS = [
    "confirmé", "confirmée", "expérimenté", "expérimentée",
    "senior", "expert", "freelance",
    "tech lead", "staff engineer", "staff ", "engineering manager",
    "manager", "principal ",
]

JUNIOR_FRIENDLY_FLAGS = [
    "débutant accepté", "débutant accepte", "débutant bienvenu", "profil junior",
    "junior accepté", "sans expérience", "premier emploi", "jeune diplômé",
    "jeune diplômée", "0-2 ans", "0 à 2 ans",
]

# Seuil d'expérience maximum accepté (en années). Une offre demandant plus est filtrée.
MAX_EXPERIENCE_YEARS = 1


def _has_senior_flag(titre: str) -> bool:
    titre = f" {titre.strip()} "
    return any(f" {flag}" in titre or titre.startswith(f" {flag}") or flag in titre for flag in SENIOR_FLAGS)


def is_junior_friendly(titre: str, description: str) -> bool:
    combined = f"{titre} {description}".lower()
    return any(flag in combined for flag in JUNIOR_FRIENDLY_FLAGS)


def _extract_min_experience_years(text: str) -> int | None:
    """
    Cherche des mentions d'expérience du type :
    - "5 à 10 ans d'expérience"
    - "3-5 ans d'expérience"
    - "minimum 3 ans"
    - "3 ans minimum"
    - "5 ans d'expérience"
    Retourne le nombre d'années minimum demandé, ou None si rien trouvé.
    """
    text = text.lower()

    match = re.search(r"(\d+)\s*(?:à|-|\bet\b)\s*(\d+)\s*ans", text)
    if match:
        return int(match.group(1))

    match = re.search(r"minimum\s*(?:de\s*)?(\d+)\s*ans", text)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)\s*ans\s*minimum", text)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\+?\s*ans?\s*d[’']?exp", text)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*ans", text)
    if match and "expérience" in text:
        return int(match.group(1))

    return None


def has_excessive_experience_requirement(titre: str, description: str, max_years: int = MAX_EXPERIENCE_YEARS) -> bool:
    combined = f"{titre} {description}"
    min_years = _extract_min_experience_years(combined)
    if min_years is None:
        return False
    return min_years > max_years


def passes_hard_filters(raw_offer: dict) -> bool:
    type_contrat = raw_offer.get("typeContrat", "")
    if type_contrat not in PROFILE["contract_types"]:
        return False

    titre = raw_offer.get("intitule", "").lower()
    description = raw_offer.get("description", "").lower()

    if _has_senior_flag(titre):
        return False

    # Si l'offre se déclare explicitement ouverte aux débutants, on ignore le filtre d'années
    if not is_junior_friendly(titre, description):
        if has_excessive_experience_requirement(titre, description):
            return False

    for excluded in PROFILE["excluded_keywords"]:
        if excluded.lower() in titre or excluded.lower() in description:
            return False

    secteur = raw_offer.get("secteurActiviteLibelle", "").lower()
    entreprise = raw_offer.get("entreprise", {}).get("nom", "").lower()
    for excluded in PROFILE["excluded_sectors"]:
        if excluded in secteur or excluded in entreprise or excluded in titre:
            return False

    return True