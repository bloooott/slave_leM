from collectors.hellowork import _get_full_description
from processing.filters import _normalize, SENIOR_FLAGS
from playwright.sync_api import sync_playwright

url = "https://www.hellowork.com/fr-fr/emplois/83538054.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    full_text = _get_full_description(page, url)

    text_norm = _normalize(full_text)
    text_norm_padded = f" {text_norm.strip()} "

    print("=== MOTS SENIOR TROUVÉS ===")
    for flag in SENIOR_FLAGS:
        if f" {flag}" in text_norm_padded or text_norm_padded.startswith(f" {flag}") or flag in text_norm_padded:
            # Affiche le contexte autour du mot trouvé
            idx = text_norm.find(flag)
            start = max(0, idx - 50)
            end = min(len(text_norm), idx + 50)
            print(f"\nMot trouvé: '{flag}'")
            print(f"Contexte: ...{text_norm[start:end]}...")

    input("\nEntrée pour fermer...")
    browser.close()