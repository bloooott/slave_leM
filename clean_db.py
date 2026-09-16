from storage.db import get_connection
from processing.filters import passes_hard_filters

def clean_existing_offers():
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, title, company, description, source FROM offers")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        offers = [dict(zip(columns, row)) for row in rows]

    removed = 0
    with get_connection() as conn:
        for offer in offers:
            # Reconstruit un dict compatible avec passes_hard_filters
            raw = {
                "typeContrat": "CDI",  # on suppose CDI/CDD déjà filtré à l'insertion
                "intitule": offer["title"],
                "description": offer["description"] or "",
                "secteurActiviteLibelle": "",
                "entreprise": {"nom": offer["company"]},
            }
            if not passes_hard_filters(raw):
                conn.execute("DELETE FROM offers WHERE id = ?", (offer["id"],))
                removed += 1
                print(f"  ✗ Supprimée (nouveaux critères) : {offer['title']} — {offer['company']}")

    print(f"\n{removed} offre(s) supprimée(s) sur {len(offers)} au total.")

if __name__ == "__main__":
    clean_existing_offers()