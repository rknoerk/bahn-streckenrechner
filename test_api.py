#!/usr/bin/env python3
"""
Trassenfinder API Test - Routensuche mit Streckenkilometern
"""

import requests
import json

BASE_URL = "https://openapi.trassenfinder.de/api/v9"

def search_route(von_ds100: str, nach_ds100: str, von_name: str = "", nach_name: str = ""):
    """Sucht eine Route zwischen zwei Betriebsstellen und gibt km zurück."""

    payload = {
        "infrastruktur_id": 19,
        "sucheinstellungen": {
            "an_abzeit": "2026-01-15T10:00:00+01:00",
            "verkehrsart": "spfv_tw",
            "zeitvorgabe_typ": "abzeit"
        },
        "wegpunkte": [
            {"betriebsstelle": {"ds100": von_ds100, "mutter": True}},
            {"betriebsstelle": {"ds100": nach_ds100, "mutter": True}}
        ]
    }

    response = requests.post(
        f"{BASE_URL}/routen/suche",
        json=payload,
        headers={"Accept": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        result = data.get('result', {})
        route = result.get('gewichtete_route', {})

        # Letzer Routenpunkt hat die Gesamtstrecke
        routenpunkte = route.get('routenpunkte', [])
        if routenpunkte:
            letzter = routenpunkte[-1]
            hm = letzter.get('laufende_hm', 0)
            km = hm / 10  # Hektometer → km

            # Fahrzeit
            fahrzeit = letzter.get('technische_fahrzeit_info', {}).get('ankunft_min', 0)

            return {
                'von': von_name or von_ds100,
                'nach': nach_name or nach_ds100,
                'strecke_km': km,
                'fahrzeit_min': fahrzeit,
                'status': 'ok'
            }

    return {'status': 'error', 'message': response.text}


def main():
    print("=" * 60)
    print("TRASSENFINDER API - Streckenkilometer Berechnung")
    print("=" * 60)

    # Test-Strecken
    strecken = [
        ("BL", "MH", "Berlin Hbf", "München Hbf"),
        ("AH", "BL", "Hamburg Hbf", "Berlin Hbf"),
        ("KK", "FF", "Köln Hbf", "Frankfurt Hbf"),
        ("MH", "TS", "München Hbf", "Stuttgart Hbf"),
        ("FF", "MH", "Frankfurt Hbf", "München Hbf"),
    ]

    print(f"\n{'Route':<35} {'Strecke':>10} {'Fahrzeit':>10}")
    print("-" * 60)

    for von, nach, von_name, nach_name in strecken:
        result = search_route(von, nach, von_name, nach_name)
        if result['status'] == 'ok':
            print(f"{result['von']} → {result['nach']:<20} {result['strecke_km']:>8.1f} km {result['fahrzeit_min']:>7} min")
        else:
            print(f"{von_name} → {nach_name}: FEHLER")

    print("-" * 60)
    print("\nAPI: https://openapi.trassenfinder.de/api/v9/routen/suche")
    print("Datenquelle: DB InfraGO AG (Trassenfinder)")


if __name__ == '__main__':
    main()
