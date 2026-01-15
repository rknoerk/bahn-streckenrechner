# Bahn-Streckenrechner

Ein kostenloses Online-Tool zur Berechnung von Bahnstrecken, Ticketpreisen und CO2-Einsparungen.

**Live nutzen:** [bahn-streckenrechner.streamlit.app](https://bahn-streckenrechner.streamlit.app)

---

## Was macht dieses Tool?

Der Bahn-Streckenrechner hilft dir, Bahnreisen zu planen und zu dokumentieren:

1. **Streckenkilometer berechnen** - Wie weit ist es wirklich mit dem Zug? (nicht Luftlinie, sondern die tatsächliche Schienenstrecke)
2. **Ticketpreise anzeigen** - Was kostet die Fahrt ungefähr?
3. **CO2-Ersparnis berechnen** - Wie viel CO2 spare ich im Vergleich zum Auto?

## Für wen ist das Tool?

- **Green Consultants** in der Film- und Medienbranche
- Alle, die ihre CO2-Ersparnis durch Bahnfahren dokumentieren möchten
- Unternehmen, die nachhaltige Dienstreisen nachweisen wollen

## So funktioniert's

1. **Startbahnhof eingeben** - Tippe mindestens 2 Buchstaben und wähle aus den Vorschlägen
2. **Zielbahnhof eingeben** - Gleiches Prinzip
3. **Anzahl Personen** - Für Gruppenreisen
4. **Hin- und Rückfahrt** - Checkbox aktivieren für Rundreise
5. **Berechnen klicken** - Fertig!

## Was bedeuten die Ergebnisse?

| Ergebnis | Erklärung |
|----------|-----------|
| **Strecke (km)** | Die tatsächliche Länge der Bahnstrecke in Kilometern |
| **Fahrzeit** | Ungefähre Fahrzeit basierend auf der Strecke |
| **Ticketpreis** | Aktueller Durchschnittspreis laut Deutsche Bahn |
| **CO2 Bahn** | CO2-Ausstoß für diese Zugfahrt in Kilogramm |
| **CO2 Auto** | CO2-Ausstoß, wenn du die gleiche Strecke mit dem Auto fahren würdest |
| **Ersparnis** | So viel CO2 sparst du durch die Zugfahrt |

## Welche Bahnhöfe werden unterstützt?

Das Tool unterstützt alle deutschen Bahnhöfe mit Zugverkehr. Bei kleineren Bahnhöfen auf nicht-elektrifizierten Nebenstrecken kann die Streckenberechnung eingeschränkt sein.

## Woher kommen die Daten?

| Daten | Quelle |
|-------|--------|
| Streckenkilometer | DB InfraGO (Trassenfinder) |
| Ticketpreise | Deutsche Bahn |
| CO2-Werte | Umweltbundesamt 2023 |

### CO2-Werte im Detail

| Verkehrsmittel | Gramm CO2 pro Kilometer |
|----------------|-------------------------|
| ICE | 29 g |
| IC/EC | 32 g |
| Regionalbahn | 55 g |
| Auto (Durchschnitt) | 154 g |
| Flugzeug (Kurzstrecke) | 230 g |

---

## Für Entwickler

<details>
<summary>Technische Details (klicken zum Aufklappen)</summary>

### Lokale Installation

```bash
git clone https://github.com/rknoerk/bahn-streckenrechner.git
cd bahn-streckenrechner
pip install -r requirements.txt
streamlit run app.py
```

### Technologie

- Python + Streamlit
- DB REST API (Ticketpreise, Bahnhofssuche)
- Trassenfinder OpenAPI (Streckenkilometer)

### Deployment

Die App läuft auf Streamlit Cloud. Einfach Repository forken und auf [share.streamlit.io](https://share.streamlit.io) deployen.

</details>

---

**Lizenz:** MIT - Frei nutzbar

Entwickelt für den **BVGCD** - Bundesverband Green Consultants Deutschland
