import re
import unicodedata
from config import PROFILE

SENIOR_FLAGS = [
    "confirme", "confirmee", "experimente", "experimentee",
    "senior", "expert", "freelance",
    "tech lead", "staff engineer", "staff ", "engineering manager",
    "manager", "principal ", "lead ",
]

JUNIOR_FRIENDLY_FLAGS = [
    "debutant accepte", "debutant bienvenu", "profil junior",
    "junior accepte", "sans experience", "premier emploi", "jeune diplome",
    "0-2 ans", "0 a 2 ans",
]

MAX_EXPERIENCE_YEARS = 1


def _normalize(text: str) -> str:
    """Retire les accents pour une comparaison robuste (senior/sénior, experience/expérience, etc.)."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def _has_senior_flag(text: str) -> bool:
    text_norm = _normalize(text)
    text_norm = f" {text_norm.strip()} "
    return any(f" {flag}" in text_norm or text_norm.startswith(f" {flag}") or flag in text_norm for flag in SENIOR_FLAGS)


def is_junior_friendly(titre: str, description: str) -> bool:
    combined = _normalize(f"{titre} {description}")
    return any(flag in combined for flag in JUNIOR_FRIENDLY_FLAGS)


def _extract_min_experience_years(text: str) -> int | None:
    """
    Cherche des mentions d'expérience dans plusieurs formats courants (texte normalisé, sans accents) :
    - "5 a 10 ans d'experience"
    - "minimum 3 ans"
    - "5 ans d'experience"
    - "Exp. 5 ans min." (badge HelloWork)
    - "Exp. 1 - 3 ans" (badge HelloWork avec fourchette)
    Retourne le nombre d'années minimum demandé, ou None si rien trouvé.
    """
    text = _normalize(text)

    match = re.search(r"exp\.?\s*(\d+)\s*ans?\s*min", text)
    if match:
        return int(match.group(1))

    match = re.search(r"exp\.?\s*(\d+)\s*-\s*(\d+)\s*ans", text)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*(?:a|-|\bet\b)\s*(\d+)\s*ans", text)
    if match:
        return int(match.group(1))

    match = re.search(r"minimum\s*(?:de\s*)?(\d+)\s*ans", text)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)\s*ans\s*minimum", text)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\+?\s*ans?\s*d['’]?exp", text)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*ans", text)
    if match and "experience" in text:
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

    titre = raw_offer.get("intitule", "")
    description = raw_offer.get("description", "")

    if _has_senior_flag(titre):
        return False

    # Vérifie aussi les mots senior dans la description (pas juste le titre)
    if _has_senior_flag(description):
        return False

    if not is_junior_friendly(titre, description):
        if has_excessive_experience_requirement(titre, description):
            return False

    titre_norm = _normalize(titre)
    description_norm = _normalize(description)
    for excluded in PROFILE["excluded_keywords"]:
        excluded_norm = _normalize(excluded)
        if excluded_norm in titre_norm or excluded_norm in description_norm:
            return False

    secteur = _normalize(raw_offer.get("secteurActiviteLibelle", ""))
    entreprise = _normalize(raw_offer.get("entreprise", {}).get("nom", ""))
    for excluded in PROFILE["excluded_sectors"]:
        excluded_norm = _normalize(excluded)
        if excluded_norm in secteur or excluded_norm in entreprise or excluded_norm in titre_norm:
            return False

    return True