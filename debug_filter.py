from processing.filters import (
    _extract_min_experience_years,
    has_excessive_experience_requirement,
    is_junior_friendly,
    passes_hard_filters,
    MAX_EXPERIENCE_YEARS,
)
from storage.db import get_connection

print(f"MAX_EXPERIENCE_YEARS actuel = {MAX_EXPERIENCE_YEARS}\n")

# Test direct sur le texte problématique
test_text = "Vous avez environ 5 à 10 ans d'expérience en data engineering, analytics engineering/BI"
years = _extract_min_experience_years(test_text)
print(f"Test texte isolé : '{test_text}'")
print(f"  -> années détectées : {years}")
print(f"  -> is_junior_friendly : {is_junior_friendly('', test_text)}")
print(f"  -> has_excessive_experience_requirement : {has_excessive_experience_requirement('', test_text)}")

print("\n--- Recherche de l'offre exacte en base ---")
with get_connection() as conn:
    cursor = conn.execute(
        "SELECT id, title, company, description FROM offers WHERE description LIKE ?",
        ("%5 à 10 ans%",)
    )
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

print(f"{len(rows)} offre(s) trouvée(s) contenant '5 à 10 ans' dans la description")
for r in rows:
    print(f"\nID: {r['id']}")
    print(f"Titre: {r['title']}")
    print(f"Company: {r['company']}")
    print(f"Description (100 premiers caractères): {r['description'][:200] if r['description'] else 'VIDE'}")

    raw = {
        "typeContrat": "CDI",
        "intitule": r["title"],
        "description": r["description"] or "",
        "secteurActiviteLibelle": "",
        "entreprise": {"nom": r["company"]},
    }
    result = passes_hard_filters(raw)
    print(f"passes_hard_filters -> {result} (False = devrait être filtrée)")