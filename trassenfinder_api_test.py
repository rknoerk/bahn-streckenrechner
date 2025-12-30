#!/usr/bin/env python3
"""
Trassenfinder OpenAPI Explorer - V2
Extrahiert API-Dokumentation Version 9
"""

from playwright.sync_api import sync_playwright
import json
import time
import re

def explore_trassenfinder_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Netzwerk-Requests mitschneiden
        api_calls = []

        def handle_response(response):
            url = response.url
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type or 'openapi' in url.lower():
                api_calls.append({
                    'url': url,
                    'status': response.status,
                    'content_type': content_type
                })

        page.on('response', handle_response)

        print("=== Lade OpenAPI-Dokumentation ===")
        page.goto('https://openapi.trassenfinder.de/', wait_until='networkidle')
        time.sleep(2)

        # Disclaimer akzeptieren
        print("=== Akzeptiere Disclaimer ===")
        try:
            accept_btn = page.get_by_text('Akzeptieren')
            accept_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')
        except:
            pass

        # Klicke auf Dokumentation für Version 9
        print("\n=== Öffne API Version 9 Dokumentation ===")
        try:
            # Finde den Link zur Dokumentation V9
            doc_links = page.query_selector_all('a')
            for link in doc_links:
                text = link.inner_text()
                href = link.get_attribute('href')
                if 'Dokumentation' in text and href:
                    print(f"Gefunden: {text} -> {href}")
                    # Klicke auf den ersten Dokumentation-Link (V9)
                    link.click()
                    time.sleep(3)
                    page.wait_for_load_state('networkidle')
                    break
        except Exception as e:
            print(f"Fehler: {e}")

        # Seiten-Inhalt der Dokumentation
        print("\n=== API-Dokumentation Inhalt ===")
        text = page.inner_text('body')
        print(text[:5000])

        # Suche nach HTTP-Methoden und Pfaden
        print("\n=== Gefundene Endpoints ===")
        # Regex für API-Pfade
        paths = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[a-zA-Z0-9/_\-{}]+)', text)
        for method, path in paths[:30]:
            print(f"  {method} {path}")

        # Abgefangene Requests
        print("\n=== Abgefangene JSON/API Requests ===")
        for call in api_calls:
            print(f"  {call['url']}")

        # Screenshot
        page.screenshot(path='/Users/rknoerk/Code/slack-export/trassenfinder_docs.png', full_page=True)
        print("\n=== Screenshot: trassenfinder_docs.png ===")

        # HTML speichern
        html = page.content()
        with open('/Users/rknoerk/Code/slack-export/trassenfinder_docs.html', 'w') as f:
            f.write(html)

        browser.close()

if __name__ == '__main__':
    explore_trassenfinder_api()
