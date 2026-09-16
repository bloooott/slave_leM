from collectors.hellowork import _get_full_description

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False pour voir la page
        page = browser.new_page()
        desc = _get_full_description(page, "https://www.hellowork.com/fr-fr/emplois/83363562.html")
        print(desc[:1000])
        input("Appuie sur Entrée pour fermer...")
        browser.close()