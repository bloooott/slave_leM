import time
import requests
from collectors.base import JobOffer
from processing.filters import passes_hard_filters
from processing.recency import is_recent_france_travail
from config import FRANCE_TRAVAIL_CLIENT_ID, FRANCE_TRAVAIL_CLIENT_SECRET, PROFILE

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
API_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

_cached_token = None

def get_token():
    global _cached_token
    if _cached_token:
        return _cached_token
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": FRANCE_TRAVAIL_CLIENT_ID,
        "client_secret": FRANCE_TRAVAIL_CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre",
    }, timeout=15)

    if resp.status_code != 200:
        print(f"⚠️ Erreur token — status {resp.status_code}")
        print(f"Réponse : {resp.text}")
        print(f"Client ID utilisé (masqué) : {FRANCE_TRAVAIL_CLIENT_ID[:10]}...{FRANCE_TRAVAIL_CLIENT_ID[-4:] if FRANCE_TRAVAIL_CLIENT_ID else 'VIDE'}")

    resp.raise_for_status()
    _cached_token = resp.json()["access_token"]
    return _cached_token
def fetch_offers(keyword: str) -> list[JobOffer]:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "motsCles": keyword,
        "range": "0-49",
        "experience": "1",
        "sort": "1",           # tri par date décroissante
        "publieeDepuis": "1",  # offres publiées depuis 24h (seules valeurs acceptées : 1, 3, 7, 14, 31)
    }

    resp = requests.get(API_URL, headers=headers, params=params, timeout=15)

    if resp.status_code == 204:
        print(f"  ℹ️ Aucune offre trouvée pour '{keyword}' (204)")
        return []

    if resp.status_code not in (200, 206):
        print(f"  ⚠️ Erreur API pour '{keyword}' : status {resp.status_code} — {resp.text[:200]}")
        return []

    data = resp.json().get("resultats", [])
    print(f"  → {len(data)} offres brutes pour '{keyword}' (≤24h, triées par date)")

    filtered_data = [o for o in data if passes_hard_filters(o)]
    print(f"  → {len(filtered_data)} après filtres durs (contrat/senior/mots exclus/secteur)")

    # Garde-fou (l'API filtre déjà à 24h via publieeDepuis, mais on garde une double sécurité)
    filtered_data = [
        o for o in filtered_data
        if is_recent_france_travail(o.get("dateCreation", ""))
    ]
    print(f"  → {len(filtered_data)} après filtre de récence")

    return [
        JobOffer(
            id=o["id"],
            title=o["intitule"],
            company=o.get("entreprise", {}).get("nom", "N/A"),
            description=o.get("description", ""),
            url=o.get("origineOffre", {}).get("urlOrigine", ""),
            location=o.get("lieuTravail", {}).get("libelle", ""),
            source="france_travail",
            posted_date=o.get("dateCreation", ""),
            raw_data=o,
        )
        for o in filtered_data
    ]

if __name__ == "__main__":
    for title in PROFILE["job_titles"]:
        offers = fetch_offers(title)
        print(f"{title}: {len(offers)} offres trouvées")
        if offers:
            print(offers[0])
        time.sleep(1)