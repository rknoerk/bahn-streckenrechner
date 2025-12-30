#!/usr/bin/env python3
"""
Trassenfinder API - Zeigt die vollständige Fahrstrecke
"""

import requests
import json

BASE_URL = "https://openapi.trassenfinder.de/api/v9"

def get_route_details(von_ds100: str, nach_ds100: str):
    """Holt die vollständige Route mit allen Zwischenstationen."""

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
        return response.json()
    return None


def main():
    print("=" * 70)
    print("TRASSENFINDER - Vollständige Fahrstrecke Berlin → München")
    print("=" * 70)

    data = get_route_details("BL", "MH")

    if not data:
        print("Fehler beim Abrufen der Route")
        return

    route = data['result']['gewichtete_route']
    routenpunkte = route['routenpunkte']

    print(f"\nAnzahl Betriebsstellen: {len(routenpunkte)}")
    print()
    print(f"{'Nr':<4} {'DS100':<8} {'km':>8} {'Fahrzeit':>10} {'Strecke':>8} {'Halt':<12}")
    print("-" * 70)

    prev_km = 0
    for i, punkt in enumerate(routenpunkte):
        ds100 = punkt.get('ds100', '')
        km = punkt.get('laufende_hm', 0) / 10
        segment_km = km - prev_km
        prev_km = km

        fahrzeit = punkt.get('technische_fahrzeit_info', {}).get('ankunft_min', 0)
        strecke = punkt.get('naechstes_streckensegment', {}).get('streckennummer', '')
        halt = punkt.get('haltart', '')

        print(f"{i+1:<4} {ds100:<8} {km:>8.1f} {fahrzeit:>8} min {strecke:>8} {halt:<12}")

    print("-" * 70)

    # Zusammenfassung
    letzter = routenpunkte[-1]
    gesamt_km = letzter.get('laufende_hm', 0) / 10
    gesamt_min = letzter.get('technische_fahrzeit_info', {}).get('ankunft_min', 0)

    print(f"\nGESAMT: {gesamt_km:.1f} km in {gesamt_min} Minuten ({gesamt_min/60:.1f} Stunden)")

    # Streckenabschnitte
    print("\n" + "=" * 70)
    print("STRECKENABSCHNITTE (VzG-Nummern)")
    print("=" * 70)

    strecken = {}
    for punkt in routenpunkte:
        seg = punkt.get('naechstes_streckensegment', {})
        if seg:
            nr = seg.get('streckennummer')
            von = seg.get('von')
            bis = seg.get('bis')
            if nr:
                if nr not in strecken:
                    strecken[nr] = {'von': von, 'bis': bis}
                else:
                    strecken[nr]['bis'] = bis

    for nr, info in strecken.items():
        print(f"  VzG {nr}: {info['von']} → {info['bis']}")


if __name__ == '__main__':
    main()
