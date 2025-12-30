# 🚄 Bahn-Streckenrechner

**Für Green Consultants** - Berechnet Streckenkilometer, CO2-Emissionen und Ticketpreise für Bahnreisen.

## Features

- ✅ Exakte Streckenkilometer (Daten: DB InfraGO Trassenfinder)
- ✅ Aktuelle Ticketpreise (Daten: DB REST API)
- ✅ CO2-Berechnung mit Vergleich Bahn vs. Auto
- ✅ Unterstützung für Gruppenreisen und Hin-/Rückfahrt
- ✅ Export-Daten für Green-Motion-Dokumentation

## Live Demo

🔗 [https://bahn-streckenrechner.streamlit.app](https://bahn-streckenrechner.streamlit.app)

## Lokale Installation

```bash
# Repository klonen
git clone https://github.com/DEIN-USERNAME/bahn-streckenrechner.git
cd bahn-streckenrechner

# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
streamlit run app.py
```

## Deployment auf Streamlit Cloud

1. Repository auf GitHub pushen
2. Auf [share.streamlit.io](https://share.streamlit.io) einloggen
3. "New app" → Repository auswählen → Deploy

## Datenquellen

| Daten | Quelle | API |
|-------|--------|-----|
| Streckenkilometer | DB InfraGO | [Trassenfinder OpenAPI](https://openapi.trassenfinder.de) |
| Ticketpreise | Deutsche Bahn | [v6.db.transport.rest](https://v6.db.transport.rest) |
| CO2-Faktoren | Umweltbundesamt | [UBA 2023](https://www.umweltbundesamt.de) |

## CO2-Emissionsfaktoren

| Verkehrsmittel | g CO₂/Pkm |
|----------------|-----------|
| ICE Fernverkehr | 29 |
| IC/EC | 32 |
| Regionalverkehr | 55 |
| PKW (Durchschnitt) | 154 |
| Flug (Kurzstrecke) | 230 |

*Quelle: Umweltbundesamt 2023*

## Lizenz

MIT - Frei verwendbar für Green Consultants und nachhaltige Filmproduktion.

---

Entwickelt für **BVGCD** - Bundesverband Green Consultants Deutschland
