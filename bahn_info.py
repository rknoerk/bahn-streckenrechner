#!/usr/bin/env python3
"""
Bahn-Info API - Kombiniert Streckenkilometer + Ticketpreise
- Strecken-km: Trassenfinder API (DB InfraGO)
- Ticketpreise: DB REST API (v6.db.transport.rest)
"""

import requests
from datetime import datetime, timedelta

# === TRASSENFINDER API (Streckenkilometer) ===

TRASSENFINDER_URL = "https://openapi.trassenfinder.de/api/v9"

# DS100 Codes für wichtige Bahnhöfe
DS100_CODES = {
    "berlin": "BL",
    "münchen": "MH",
    "hamburg": "AH",
    "köln": "KK",
    "frankfurt": "FF",
    "stuttgart": "TS",
    "düsseldorf": "KD",
    "hannover": "HH",
    "nürnberg": "NN",
    "leipzig": "LL",
}

# EVA-Nummern für DB REST API
EVA_CODES = {
    "berlin": "8011160",
    "münchen": "8000261",
    "hamburg": "8002549",
    "köln": "8000207",
    "frankfurt": "8000105",
    "stuttgart": "8000096",
    "düsseldorf": "8000085",
    "hannover": "8000152",
    "nürnberg": "8000284",
    "leipzig": "8010205",
}


def get_strecke_km(von: str, nach: str) -> dict:
    """Holt Streckenkilometer von der Trassenfinder API."""

    von_ds100 = DS100_CODES.get(von.lower())
    nach_ds100 = DS100_CODES.get(nach.lower())

    if not von_ds100 or not nach_ds100:
        return {"error": f"Unbekannte Stadt: {von} oder {nach}"}

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

    try:
        response = requests.post(
            f"{TRASSENFINDER_URL}/routen/suche",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            route = data['result']['gewichtete_route']
            routenpunkte = route['routenpunkte']
            letzter = routenpunkte[-1]

            return {
                "strecke_km": letzter['laufende_hm'] / 10,
                "fahrzeit_min": letzter['technische_fahrzeit_info']['ankunft_min'],
                "anzahl_stationen": len(routenpunkte)
            }
    except Exception as e:
        return {"error": str(e)}

    return {"error": "API-Fehler"}


def get_ticket_preis(von: str, nach: str) -> dict:
    """Holt Ticketpreis von der DB REST API."""

    von_eva = EVA_CODES.get(von.lower())
    nach_eva = EVA_CODES.get(nach.lower())

    if not von_eva or not nach_eva:
        return {"error": f"Unbekannte Stadt: {von} oder {nach}"}

    # Datum: morgen
    morgen = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        response = requests.get(
            f"https://v6.db.transport.rest/journeys",
            params={
                "from": von_eva,
                "to": nach_eva,
                "departure": f"{morgen}T10:00",
                "results": 1,
                "tickets": "true"
            },
            headers={"Accept": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('journeys'):
                journey = data['journeys'][0]
                price = journey.get('price', {})

                # Zugtyp ermitteln
                zugtyp = ""
                for leg in journey.get('legs', []):
                    line = leg.get('line', {}).get('name', '')
                    if line:
                        zugtyp = line.split()[0] if line else ""
                        break

                return {
                    "preis_euro": price.get('amount'),
                    "zugtyp": zugtyp,
                    "hinweis": "Flexpreis, kann variieren"
                }
    except Exception as e:
        return {"error": str(e)}

    return {"error": "Kein Preis gefunden"}


def get_bahn_info(von: str, nach: str) -> dict:
    """Kombinierte Abfrage: Strecke + Preis."""

    strecke = get_strecke_km(von, nach)
    preis = get_ticket_preis(von, nach)

    result = {
        "von": von,
        "nach": nach,
    }

    if "error" not in strecke:
        result["strecke_km"] = strecke["strecke_km"]
        result["fahrzeit_min"] = strecke["fahrzeit_min"]
        result["fahrzeit_h"] = round(strecke["fahrzeit_min"] / 60, 1)

    if "error" not in preis:
        result["preis_euro"] = preis["preis_euro"]
        result["zugtyp"] = preis["zugtyp"]

    # CO2-Schätzung (42g/Pkm für Fernverkehr, Quelle: UBA)
    if "strecke_km" in result:
        result["co2_kg"] = round(result["strecke_km"] * 0.029, 2)  # 29g/Pkm ICE

    return result


def main():
    print("=" * 65)
    print("BAHN-INFO: Strecke, Preis & CO2")
    print("=" * 65)

    strecken = [
        ("Berlin", "München"),
        ("Hamburg", "Berlin"),
        ("Köln", "Frankfurt"),
        ("Frankfurt", "München"),
        ("Stuttgart", "Hamburg"),
    ]

    print(f"\n{'Route':<25} {'km':>8} {'Zeit':>8} {'Preis':>10} {'CO2':>8}")
    print("-" * 65)

    for von, nach in strecken:
        info = get_bahn_info(von, nach)

        km = f"{info.get('strecke_km', 0):.0f} km" if 'strecke_km' in info else "?"
        zeit = f"{info.get('fahrzeit_h', 0):.1f} h" if 'fahrzeit_h' in info else "?"
        preis = f"{info.get('preis_euro', 0):.0f} €" if 'preis_euro' in info else "?"
        co2 = f"{info.get('co2_kg', 0):.1f} kg" if 'co2_kg' in info else "?"

        print(f"{von} → {nach:<15} {km:>8} {zeit:>8} {preis:>10} {co2:>8}")

    print("-" * 65)
    print("\nQuellen:")
    print("  Strecke: Trassenfinder API (DB InfraGO)")
    print("  Preis: DB REST API (Flexpreis, kann variieren)")
    print("  CO2: 29g/Pkm (UBA, ICE Fernverkehr)")


if __name__ == '__main__':
    main()
