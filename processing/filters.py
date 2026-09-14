from config import PROFILE

SENIOR_FLAGS = [
    "confirmé", "confirmée", "expérimenté", "expérimentée",
    "senior", "expert", "freelance",
    "tech lead", "staff engineer", "staff ", "engineering manager",
    "manager", "principal ",
]

def _has_senior_flag(titre: str) -> bool:
    titre = f" {titre.strip()} "  # ajoute des espaces virtuels au début/fin
    return any(f" {flag}" in titre or titre.startswith(f" {flag}") or flag in titre for flag in SENIOR_FLAGS)

def passes_hard_filters(raw_offer: dict) -> bool:
    type_contrat = raw_offer.get("typeContrat", "")
    if type_contrat not in PROFILE["contract_types"]:
        return False

    titre = raw_offer.get("intitule", "").lower()
    description = raw_offer.get("description", "").lower()

    if _has_senior_flag(titre):
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