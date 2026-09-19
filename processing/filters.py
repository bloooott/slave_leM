import re
import unicodedata
from config import PROFILE

SENIOR_FLAGS = [
    "confirme", "confirmee", "experimente", "experimentee",
    "senior", "expert", "freelance",
    "tech lead", "staff engineer", "staff", "engineering manager",
    "manager", "lead",
]

NEGATION_PATTERNS = [
    r"pas\s+besoin\s+d[’']?etre",
    r"pas\s+forcement",
    r"sans\s+etre",
    r"n[’']?avez\s+pas\s+besoin",
    r"nul\s+besoin\s+d[’']?etre",
    r"pas\s+necessairement",
    r"pas\s+deja",
]

JUNIOR_FRIENDLY_FLAGS = [
    "debutant accepte", "debutant bienvenu", "profil junior",
    "junior accepte", "sans experience", "premier emploi", "jeune diplome",
    "0-2 ans", "0 a 2 ans", "entry level", "entry-level",
    "no experience required", "graduate", "junior", "debutant",
]

MAX_EXPERIENCE_YEARS = 2

FRENCH_NUMBER_WORDS = {
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
    "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10,
    "onze": 11, "douze": 12, "quinze": 15, "vingt": 20,
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _replace_spelled_out_numbers(text: str) -> str:
    for word, digit in FRENCH_NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", str(digit), text)
    return text


def _has_senior_flag(text: str) -> bool:
    """Détecte un mot senior avec de vraies limites de mots, en ignorant les cas
    où le mot est précédé d'une négation (ex: 'pas besoin d'être expert')."""
    text_norm = _normalize(text)

    for flag in SENIOR_FLAGS:
        pattern = r"\b" + re.escape(flag.strip()) + r"\b"
        for match in re.finditer(pattern, text_norm):
            context_before = text_norm[max(0, match.start() - 60):match.start()]
            is_negated = any(re.search(neg, context_before) for neg in NEGATION_PATTERNS)
            if not is_negated:
                return True

    return False


def is_junior_friendly(titre: str, description: str) -> bool:
    combined = _normalize(f"{titre} {description}")
    return any(flag in combined for flag in JUNIOR_FRIENDLY_FLAGS)


def is_junior_in_title(titre: str) -> bool:
    titre_norm = _normalize(titre)
    return "junior" in titre_norm or "debutant" in titre_norm


def _extract_min_experience_years(text: str) -> int | None:
    text = _normalize(text)
    text = _replace_spelled_out_numbers(text)

    match = re.search(r"(\d+)\+?\s*(?:-|to)?\s*(\d+)?\s*years?\s*(?:of\s*)?exp", text)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)\+?\s*years?", text)
    if match and "experience" in text:
        return int(match.group(1))

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


def passes_hard_filters(raw_offer: dict, debug: bool = False) -> bool:
    type_contrat = raw_offer.get("typeContrat", "")
    if type_contrat not in PROFILE["contract_types"]:
        if debug:
            print(f"    [debug] Rejet : type de contrat '{type_contrat}' non accepté")
        return False

    titre = raw_offer.get("intitule", "")
    description = raw_offer.get("description", "")

    if _has_senior_flag(titre):
        if debug:
            print(f"    [debug] Rejet : mot senior dans le TITRE")
        return False

    if _has_senior_flag(description):
        if debug:
            print(f"    [debug] Rejet : mot senior dans la DESCRIPTION")
        return False

    if not is_junior_friendly(titre, description):
        if has_excessive_experience_requirement(titre, description):
            if debug:
                years = _extract_min_experience_years(f"{titre} {description}")
                print(f"    [debug] Rejet : expérience excessive ({years} ans, max {MAX_EXPERIENCE_YEARS})")
            return False

    titre_norm = _normalize(titre)
    description_norm = _normalize(description)
    for excluded in PROFILE["excluded_keywords"]:
        excluded_norm = _normalize(excluded)
        if excluded_norm in titre_norm or excluded_norm in description_norm:
            if debug:
                print(f"    [debug] Rejet : mot-clé exclu : '{excluded}'")
            return False

    secteur = _normalize(raw_offer.get("secteurActiviteLibelle", ""))
    entreprise = _normalize(raw_offer.get("entreprise", {}).get("nom", ""))
    for excluded in PROFILE["excluded_sectors"]:
        excluded_norm = _normalize(excluded)
        if excluded_norm in secteur or excluded_norm in entreprise or excluded_norm in titre_norm:
            if debug:
                print(f"    [debug] Rejet : secteur exclu : '{excluded}'")
            return False

    return True