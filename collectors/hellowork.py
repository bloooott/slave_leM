from urllib.parse import quote
from playwright.sync_api import sync_playwright
from collectors.base import JobOffer
from processing.filters import passes_hard_filters, has_excessive_experience_requirement, is_junior_friendly
from processing.recency import is_recent_indeed_text

SEARCH_URL = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
MAX_CANDIDATES_TO_CHECK = 8


def _get_full_description(page, url: str) -> str:
    try:
        page.goto(url, timeout=20000)
        page.wait_for_timeout(1500)

        try:
            cookie_button = page.query_selector("text=Continuer sans accepter")
            if cookie_button:
                cookie_button.click()
                page.wait_for_timeout(500)
            else:
                accept_button = page.query_selector("text=Tout accepter")
                if accept_button:
                    accept_button.click()
                    page.wait_for_timeout(500)
        except Exception:
            pass

        result = page.evaluate("""
            () => {
                const summaries = Array.from(document.querySelectorAll('summary'));
                const target = summaries.find(s => (s.textContent || '').toLowerCase().includes('profil recherché'));
                if (!target) return null;

                const details = target.closest('details');
                if (!details) return null;

                return (details.textContent || '').trim();
            }
        """)

        if result and len(result) > 30:
            return result

        return page.inner_text("body")

    except Exception as e:
        print(f"    ⚠️ Impossible de charger la description complète : {e}")
        return ""


def fetch_offers(keyword: str, max_hours: int = 48) -> list[JobOffer]:
    offers = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        url = f"{SEARCH_URL}?k={quote(keyword)}&st=date&d=h"
        page.goto(url, timeout=30000)
        page.wait_for_timeout(3000)

        try:
            cookie_button = page.query_selector("text=Continuer sans accepter")
            if cookie_button:
                cookie_button.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

        cards = page.query_selector_all("li[data-id-storage-target='item']")
        print(f"  → {len(cards)} cartes trouvées pour '{keyword}' (≤24h, triées par date)")

        consecutive_old = 0
        candidates = []

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
                print(f"  ✗ Filtrée (critères titre) : {title} — {company}")
                continue

            candidates.append({
                "id": f"hellowork_{offer_id}",
                "title": title,
                "company": company,
                "location": location,
                "url": url_job,
                "posted_date": posted_text,
            })

        print(f"  → {len(candidates)} candidat(e)s après filtrage rapide")

        # Limite pour garder un temps de scraping raisonnable
        if len(candidates) > MAX_CANDIDATES_TO_CHECK:
            print(f"  → limite à {MAX_CANDIDATES_TO_CHECK} candidat(e)s vérifié(e)s (les plus récent(e)s)")
        candidates = candidates[:MAX_CANDIDATES_TO_CHECK]

        for c in candidates:
            full_text = _get_full_description(page, c["url"])

            if not is_junior_friendly(c["title"], full_text):
                if has_excessive_experience_requirement(c["title"], full_text):
                    print(f"  ✗ Filtrée (expérience excessive) : {c['title']} — {c['company']}")
                    continue

            print(f"  ✓ Retenue : {c['title']} — {c['company']}")

            offers.append(JobOffer(
                id=c["id"],
                title=c["title"],
                company=c["company"],
                description=full_text[:2000],
                url=c["url"],
                location=c["location"],
                source="hellowork",
                posted_date=c["posted_date"],
                raw_data={},
            ))

        browser.close()

    return offers


if __name__ == "__main__":
    offers = fetch_offers("Data Engineer")
    print(f"{len(offers)} offres retenues après filtrage")
    if offers:
        print(offers[0])