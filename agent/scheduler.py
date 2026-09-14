import schedule
import time
from main import run
from matching.matcher import score_all_offers

def job():
    print(f"\n{'='*50}\nLancement du cycle de scraping\n{'='*50}")
    run()
    score_all_offers()

schedule.every().day.at("07:00").do(job)
schedule.every().day.at("12:00").do(job)
schedule.every().day.at("17:00").do(job)
schedule.every().day.at("21:00").do(job)

if __name__ == "__main__":
    print("Scheduler démarré. Ctrl+C pour arrêter.")
    job()
    while True:
        schedule.run_pending()
        time.sleep(60)