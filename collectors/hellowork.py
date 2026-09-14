from urllib.parse import quote
from playwright.sync_api import sync_playwright
from collectors.base import JobOffer
from processing.filters import passes_hard_filters
from processing.recency import is_recent_indeed_text

SEARCH_URL = "https://www.hellowork.com/fr-fr/emploi/recherche.html"

def fetch_offers(keyword: str, max_hours: int = 48) -> list[JobOffer]:
    offers = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # st=date : tri par date décroissante
        # d=d : filtre "depuis 3 jours" (plus petit palier dispo au-dessus de 48h)
        # quote() encode correctement les accents/espaces (fix pertinence "Ingénieur IA" etc.)
        url = f"{SEARCH_URL}?k={quote(keyword)}&st=date&d=d"
        page.goto(url, timeout=30000)
        page.wait_for_timeout(3000)

        cards = page.query_selector_all("li[data-id-storage-target='item']")
        print(f"  → {len(cards)} cartes trouvées pour '{keyword}' (≤3j, triées par date)")

        consecutive_old = 0

        for card in cards:
            title_el = card.query_selector('a[data-cy="offerTitle"] h3 p:first-child')
            company_el = card.query_selector('a[data-cy="offerTitle"] h3 p:nth-child(2)')
            link_el = card.query_selector('a[data-cy="offerTitle"]')
            location_el = card.query_selector('[data-cy="localisationCard"]')
            contract_el = card.query_selector('[data-cy="contractCard"]')
            date_el = card.query_selector('.typo-s.text-grey-500.pl-1.pt-1')

            if not title_el or not link_el:
                continue

            title = title_el.inner_text().strip()
            company = company_el.inner_text().strip() if company_el else "N/A"
            location = location_el.inner_text().strip() if location_el else ""
            contract = contract_el.inner_text().strip() if contract_el else "CDI"
            posted_text = date_el.inner_text().strip() if date_el else ""
            href = link_el.get_attribute("href") or ""
            url_job = f"https://www.hellowork.com{href}" if href.startswith("/") else href
            offer_id = href.split("/")[-1].replace(".html", "") if href else ""

            if not is_recent_indeed_text(posted_text, max_hours=max_hours):
                print(f"  ✗ Filtrée (date : '{posted_text}') : {title} — {company}")
                consecutive_old += 1
                if consecutive_old >= 3:
                    print(f"  ⏹ Arrêt anticipé : {consecutive_old} offres trop vieilles d'affilée")
                    break
                continue
            else:
                consecutive_old = 0

            raw = {
                "typeContrat": contract,
                "intitule": title,
                "description": "",
                "secteurActiviteLibelle": "",
                "entreprise": {"nom": company},
            }

            if not passes_hard_filters(raw):
                print(f"  ✗ Filtrée (critères) : {title} — {company}")
                continue

            print(f"  ✓ Retenue : {title} — {company}")

            offers.append(JobOffer(
                id=f"hellowork_{offer_id}",
                title=title,
                company=company,
                description="",
                url=url_job,
                location=location,
                source="hellowork",
                posted_date=posted_text,
                raw_data=raw,
            ))

        browser.close()

    return offers

if __name__ == "__main__":
    offers = fetch_offers("Data Engineer")
    print(f"{len(offers)} offres retenues après filtrage")
    if offers:
        print(offers[0])