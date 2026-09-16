from collectors.france_travail import fetch_offers as fetch_france_travail
from collectors.hellowork import fetch_offers as fetch_hellowork
from storage.db import init_db, save_offers, delete_old_offers
from config import PROFILE

def run():
    init_db()

    print("=== Nettoyage des offres obsolètes (> 48h) ===")
    deleted = delete_old_offers(max_hours=48)
    print(f"{deleted} offre(s) supprimée(s)\n")

    total_new = 0

    print("=== France Travail ===")
    for title in PROFILE["job_titles"]:
        offers = fetch_france_travail(title)
        new_count = save_offers(offers)
        total_new += new_count  
        print(f"{title}: {len(offers)} récupérées, {new_count} nouvelles")

    print("\n=== HelloWork ===")
    for title in PROFILE["job_titles"]:
        offers = fetch_hellowork(title)
        new_count = save_offers(offers)
        total_new += new_count
        print(f"{title}: {len(offers)} récupérées, {new_count} nouvelles")

    print(f"\nTotal nouvelles offres stockées : {total_new}")

if __name__ == "__main__":
    run()