from main import run
from matching.scorer import score_all_offers

if __name__ == "__main__":
    print("=== Scraping ===")
    run()
    print("\n=== Scoring ===")
    score_all_offers()
    print("\nTerminé.")