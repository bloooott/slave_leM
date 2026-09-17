from matching.embeddings import embed_text, cosine_similarity
from storage.db import get_unscored_offers, get_connection
from processing.filters import is_junior_friendly, is_junior_in_title
from config import CV_TEXT

def score_all_offers():
    cv_vector = embed_text(CV_TEXT)
    offers = get_unscored_offers()

    print(f"Scoring de {len(offers)} offres...")

    with get_connection() as conn:
        for offer in offers:
            offer_text = f"{offer['title']}. {offer['description']}"
            offer_vector = embed_text(offer_text)
            score = cosine_similarity(cv_vector, offer_vector)

            # Bonus fort si "junior"/"débutant" apparaît dans le TITRE (signal explicite)
            if is_junior_in_title(offer['title']):
                score = min(score + 0.20, 1.0)
            # Bonus plus léger si mentionné seulement dans la description
            elif is_junior_friendly(offer['title'], offer['description']):
                score = min(score + 0.10, 1.0)

            conn.execute(
                "UPDATE offers SET score = ? WHERE id = ?",
                (score, offer["id"])
            )

    print("Scoring terminé.")

def get_top_offers(limit: int = 20):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT title, company, location, score, url FROM offers "
            "WHERE score IS NOT NULL ORDER BY score DESC LIMIT ?",
            (limit,)
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

if __name__ == "__main__":
    score_all_offers()
    print("\n--- TOP 20 OFFRES ---\n")
    for o in get_top_offers(20):
        print(f"[{o['score']:.3f}] {o['title']} — {o['company']} ({o['location']})")
        print(f"  {o['url']}\n")