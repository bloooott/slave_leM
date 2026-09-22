from collectors.hellowork import fetch_offers_batch
from storage.db import init_db, save_offers, delete_old_offers
from config import PROFILE

def run():
    init_db()

    print("=== Nettoyage des offres obsolètes (> 12h) ===")
    deleted = delete_old_offers(max_hours=12)
    print(f"{deleted} offre(s) supprimée(s)\n")

    total_new = 0

    print("=== HelloWork ===")
    all_results = fetch_offers_batch(PROFILE["job_titles"])
    for title, offers in all_results.items():
        new_count = save_offers(offers)
        total_new += new_count
        print(f"{title}: {len(offers)} récupérées, {new_count} nouvelles")

    print(f"\nTotal nouvelles offres stockées : {total_new}")

if __name__ == "_main_":
    run()