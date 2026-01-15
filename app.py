"""
Bahn-Streckenrechner für Green Consultants
Berechnet Streckenkilometer, CO2-Emissionen und Ticketpreise

Prototyp für BVGCD - Bundesverband Green Consultants Deutschland
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
from streamlit_searchbox import st_searchbox

# === Konfiguration ===

st.set_page_config(
    page_title="Bahn-Streckenrechner",
    page_icon="🚄",
    layout="centered"
)

# API URLs
TRASSENFINDER_URL = "https://openapi.trassenfinder.de/api/v9"
DB_REST_URL = "https://v6.db.transport.rest"

# Bahnhöfe mit DS100 und EVA-Codes
BAHNHOEFE = {
    "Berlin Hbf": {"ds100": "BL", "eva": "8011160"},
    "München Hbf": {"ds100": "MH", "eva": "8000261"},
    "Hamburg Hbf": {"ds100": "AH", "eva": "8002549"},
    "Köln Hbf": {"ds100": "KK", "eva": "8000207"},
    "Frankfurt (Main) Hbf": {"ds100": "FF", "eva": "8000105"},
    "Stuttgart Hbf": {"ds100": "TS", "eva": "8000096"},
    "Düsseldorf Hbf": {"ds100": "KD", "eva": "8000085"},
    "Hannover Hbf": {"ds100": "HH", "eva": "8000152"},
    "Nürnberg Hbf": {"ds100": "NN", "eva": "8000284"},
    "Leipzig Hbf": {"ds100": "LL", "eva": "8010205"},
    "Dresden Hbf": {"ds100": "DD", "eva": "8010085"},
    "Bremen Hbf": {"ds100": "HB", "eva": "8000050"},
    "Dortmund Hbf": {"ds100": "EDO", "eva": "8000080"},
    "Essen Hbf": {"ds100": "EE", "eva": "8000098"},
    "Mannheim Hbf": {"ds100": "RM", "eva": "8000244"},
    "Karlsruhe Hbf": {"ds100": "RK", "eva": "8000191"},
    "Freiburg (Breisg) Hbf": {"ds100": "RF", "eva": "8000107"},
    "Augsburg Hbf": {"ds100": "MA", "eva": "8000013"},
}

# DS100 → Bahnhofsname Mapping (wichtige ICE-Halte)
DS100_NAMEN = {
    # Hauptbahnhöfe
    "BL": "Berlin Hbf", "BLS": "Berlin Südkreuz", "BSPD": "Berlin-Spandau",
    "MH": "München Hbf", "MOP": "München Ost", "MPA": "München-Pasing",
    "AH": "Hamburg Hbf", "AHAR": "Hamburg-Harburg", "ADAT": "Hamburg Dammtor",
    "KK": "Köln Hbf", "KKDZ": "Köln Messe/Deutz",
    "FF": "Frankfurt (Main) Hbf", "FFLU": "Frankfurt Flughafen",
    "TS": "Stuttgart Hbf",
    "KD": "Düsseldorf Hbf",
    "HH": "Hannover Hbf",
    "NN": "Nürnberg Hbf",
    "LL": "Leipzig Hbf",
    "DD": "Dresden Hbf",
    "HB": "Bremen Hbf",
    "EDO": "Dortmund Hbf",
    "EE": "Essen Hbf",
    "RM": "Mannheim Hbf",
    "RK": "Karlsruhe Hbf",
    "RF": "Freiburg (Breisg) Hbf",
    "MA": "Augsburg Hbf",
    # Wichtige ICE-Halte
    "UE": "Erfurt Hbf", "UE  L": "Erfurt Hbf", "UE  F": "Erfurt Hbf",
    "UE  O": "Erfurt Hbf", "UE  G": "Erfurt Hbf", "UE  P": "Erfurt Hbf",
    "LH": "Halle (Saale) Hbf",
    "LW": "Lutherstadt Wittenberg",
    "NBG": "Bamberg",
    "NBG S": "Bamberg",
    "MIN": "Ingolstadt Hbf",
    "NUL": "Erlangen",
    "UTHE": "Gotha",
    "UWE": "Weimar",
    "UJ": "Jena Paradies",
    "UJEW": "Jena West",
    "USA": "Saalfeld",
    "NLI": "Lichtenfels",
    "NCO": "Coburg",
    "RH": "Heidelberg Hbf",
    "RWI": "Wiesloch-Walldorf",
    "RBH": "Bruchsal",
    "TBH": "Bietigheim-Bissingen",
    "TLB": "Ludwigsburg",
    "TU": "Ulm Hbf",
    "TG": "Göppingen",
    "TPU": "Plochingen",
    "MDAG": "Dachau",
    "MRO": "Rosenheim",
    "MGS": "Garmisch-Partenkirchen",
    "WR": "Schwerin Hbf",
    "WGW": "Güstrow",
    "WRSK": "Rostock Hbf",
    "AAL": "Hamburg-Altona",
    "AWE": "Wedel",
    "EBHF": "Bochum Hbf",
    "EDG": "Duisburg Hbf",
    "EEST": "Essen Süd",
    "EG": "Gelsenkirchen Hbf",
    "EHM": "Hamm (Westf)",
    "EMST": "Münster (Westf) Hbf",
    "KO": "Koblenz Hbf",
    "KBO": "Bonn Hbf",
    "KBON": "Bonn-Beuel",
    "SSB": "Saarbrücken Hbf",
    "FKW": "Kassel-Wilhelmshöhe",
    "FFU": "Fulda",
    "FGI": "Gießen",
    "FMZ": "Mainz Hbf",
    "FWI": "Wiesbaden Hbf",
    "FLG": "Limburg Süd",
    "FMF": "Montabaur",
    "NWÜ": "Würzburg Hbf",
    "NAH": "Aschaffenburg Hbf",
}

# CO2-Emissionsfaktoren (g/Pkm) - Quelle: UBA 2023
CO2_FAKTOREN = {
    "ice": 29,      # ICE Fernverkehr
    "ic": 32,       # IC/EC
    "regional": 55, # Regionalverkehr
    "auto": 154,    # PKW (Durchschnitt)
    "flug_kurz": 230,  # Kurzstrecke <1000km
    "flug_lang": 195,  # Langstrecke >1000km
}

# Preisschätzung pro km (Fallback wenn API keine Preise liefert)
PREIS_PRO_KM = 0.18  # ca. 18 Cent/km für Flexpreis


# === API-Funktionen ===

@st.cache_data(ttl=3600)
def get_strecke_details(von_ds100: str, nach_ds100: str) -> dict:
    """Holt Streckenkilometer und Routenverlauf von der Trassenfinder API."""
    # Versuche verschiedene Kombinationen:
    # 1. Mit mutter=true (für große Knotenpunkte)
    # 2. Ohne mutter (für kleinere Stationen)
    wegpunkt_varianten = [
        [
            {"betriebsstelle": {"ds100": von_ds100, "mutter": True}},
            {"betriebsstelle": {"ds100": nach_ds100, "mutter": True}}
        ],
        [
            {"betriebsstelle": {"ds100": von_ds100}},
            {"betriebsstelle": {"ds100": nach_ds100}}
        ],
    ]

    verkehrsarten = ["spfv_tw", "spnv_tw"]  # Fernverkehr elektrisch, Nahverkehr elektrisch

    for wegpunkte in wegpunkt_varianten:
        for verkehrsart in verkehrsarten:
            payload = {
                "infrastruktur_id": 19,
                "sucheinstellungen": {
                    "an_abzeit": "2026-01-15T10:00:00+01:00",
                    "verkehrsart": verkehrsart,
                    "zeitvorgabe_typ": "abzeit"
                },
                "wegpunkte": wegpunkte
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

                    # Prüfe ob Route gefunden wurde
                    if "failure" in data or "result" not in data:
                        continue

                    route = data['result']['gewichtete_route']
                    routenpunkte = route['routenpunkte']
                    letzter = routenpunkte[-1]

                    # Wichtige Bahnhöfe auf der Route finden (die in DS100_NAMEN sind)
                    wichtige_halte = []
                    gesehene_namen = set()
                    for punkt in routenpunkte:
                        ds100 = punkt.get('ds100', '')
                        if ds100 in DS100_NAMEN:
                            name = DS100_NAMEN[ds100]
                            km = punkt.get('laufende_hm', 0) / 10
                            if name not in gesehene_namen:
                                gesehene_namen.add(name)
                                wichtige_halte.append({
                                    'ds100': ds100,
                                    'name': name,
                                    'km': km,
                                })

                    # VzG-Strecken sammeln
                    vzg_strecken = []
                    for punkt in routenpunkte:
                        seg = punkt.get('naechstes_streckensegment', {})
                        if seg and seg.get('streckennummer'):
                            nr = seg['streckennummer']
                            if not vzg_strecken or vzg_strecken[-1]['nr'] != nr:
                                vzg_strecken.append({
                                    'nr': nr,
                                    'von': seg.get('von', ''),
                                    'bis': seg.get('bis', '')
                                })
                            else:
                                vzg_strecken[-1]['bis'] = seg.get('bis', '')

                    return {
                        "strecke_km": round(letzter['laufende_hm'] / 10, 1),
                        "fahrzeit_min": letzter['technische_fahrzeit_info']['ankunft_min'],
                        "anzahl_betriebsstellen": len(routenpunkte),
                        "halte": wichtige_halte,
                        "vzg_strecken": vzg_strecken,
                        "erfolg": True
                    }
            except Exception:
                continue

    return {"erfolg": False, "fehler": "Streckenberechnung nicht möglich. Die Station liegt möglicherweise auf einer nicht-elektrifizierten Nebenstrecke."}


@st.cache_data(ttl=1800)
def get_ticket_preis(von_eva: str, nach_eva: str) -> dict:
    """Holt Ticketpreis von der DB REST API."""
    # Versuche mehrere Tage
    for tage_voraus in [7, 14, 21]:
        datum = (datetime.now() + timedelta(days=tage_voraus)).strftime("%Y-%m-%d")

        try:
            response = requests.get(
                f"{DB_REST_URL}/journeys",
                params={
                    "from": von_eva,
                    "to": nach_eva,
                    "departure": f"{datum}T10:00",
                    "results": 5,
                    "tickets": "true"
                },
                headers={"Accept": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('journeys'):
                    preise = []
                    for journey in data['journeys']:
                        price = journey.get('price', {})
                        if price and price.get('amount'):
                            preise.append(price['amount'])

                    if preise:
                        return {
                            "preis_min": min(preise),
                            "preis_max": max(preise),
                            "preis_avg": round(sum(preise) / len(preise), 2),
                            "quelle": "DB API",
                            "erfolg": True
                        }
        except:
            continue

    return {"erfolg": False}


# === Bahnhofssuche ===

@st.cache_data(ttl=86400)
def get_station_ds100(eva_id: str) -> dict:
    """Holt DS100/RIL100 Code für einen Bahnhof anhand der EVA-Nummer."""
    try:
        response = requests.get(
            f"{DB_REST_URL}/stations/{eva_id}",
            headers={"Accept": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            ril100 = data.get("ril100")
            if ril100:
                return {
                    "ds100": ril100,
                    "name": data.get("name", ""),
                    "erfolg": True
                }
    except Exception:
        pass
    return {"erfolg": False}


def search_stations(searchterm: str) -> list:
    """Sucht Bahnhöfe und gibt Liste von (Anzeigename, Daten) Tupeln zurück."""
    if not searchterm or len(searchterm) < 2:
        return []

    # Lokale Suche in vordefinierten Bahnhöfen (immer verfügbar)
    local_results = [
        (name, {"name": name, "eva": data["eva"], "ds100_hint": data["ds100"]})
        for name, data in BAHNHOEFE.items()
        if searchterm.lower() in name.lower()
    ]

    # API-Suche versuchen
    api_results = []
    try:
        response = requests.get(
            f"{DB_REST_URL}/locations",
            params={
                "query": searchterm,
                "results": 10,
                "addresses": "false",
                "poi": "false"
            },
            headers={"Accept": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            for station in data:
                products = station.get("products", {})
                is_train_station = (
                    products.get("national") or
                    products.get("nationalExpress") or
                    products.get("regional") or
                    products.get("regionalExpress")
                )

                if station.get("type") in ("stop", "station") and is_train_station:
                    eva_id = station.get("id")
                    name = station.get("name", "")
                    ril100 = None
                    ril100_ids = station.get("ril100Ids", [])
                    if ril100_ids:
                        ril100 = ril100_ids[0]

                    api_results.append((
                        name,
                        {
                            "name": name,
                            "eva": eva_id,
                            "ds100_hint": ril100
                        }
                    ))
    except Exception as e:
        print(f"Bahnhofssuche API-Fehler: {e}")

    # API-Ergebnisse haben Priorität, sonst lokale Ergebnisse
    if api_results:
        return api_results[:10]
    return local_results[:10]


def resolve_station_ds100(station_data: dict) -> dict:
    """Löst den DS100-Code für einen Bahnhof auf."""
    if not station_data:
        return {"erfolg": False, "fehler": "Kein Bahnhof ausgewählt"}

    # Prüfe ob DS100 bereits bekannt
    if station_data.get("ds100_hint"):
        return {
            "name": station_data["name"],
            "eva": station_data["eva"],
            "ds100": station_data["ds100_hint"],
            "erfolg": True
        }

    # Nachschlagen via /stations/:eva
    eva = station_data.get("eva")
    if eva:
        lookup = get_station_ds100(eva)
        if lookup.get("erfolg"):
            return {
                "name": station_data["name"],
                "eva": eva,
                "ds100": lookup["ds100"],
                "erfolg": True
            }

    return {
        "name": station_data.get("name", ""),
        "eva": station_data.get("eva"),
        "ds100": None,
        "erfolg": False,
        "fehler": "DS100-Code nicht verfügbar"
    }


# === UI ===

st.title("🚄 Bahn-Streckenrechner")
st.markdown("**Für Green Consultants** - Berechnet Streckenkilometer, CO2-Emissionen und Ticketpreise")

st.divider()

# Eingabe
st.markdown("**Start- und Zielbahnhof** (mind. 2 Buchstaben eingeben)")

col1, col2 = st.columns(2)

with col1:
    von_selection = st_searchbox(
        search_stations,
        placeholder="Startbahnhof suchen...",
        key="von_search",
        clear_on_submit=False,
    )

with col2:
    nach_selection = st_searchbox(
        search_stations,
        placeholder="Zielbahnhof suchen...",
        key="nach_search",
        clear_on_submit=False,
    )

# Optionen
col3, col4 = st.columns(2)

with col3:
    anzahl_personen = st.number_input("Anzahl Personen", min_value=1, max_value=100, value=1)

with col4:
    hin_rueck = st.checkbox("Hin- und Rückfahrt", value=False)

# Berechnen Button
if st.button("🔍 Berechnen", type="primary", use_container_width=True):

    # Validierung
    if not von_selection or not nach_selection:
        st.error("Bitte Start- und Zielbahnhof auswählen!")
    elif von_selection.get("eva") == nach_selection.get("eva"):
        st.error("Start und Ziel müssen unterschiedlich sein!")
    else:
        with st.spinner("Berechne Route..."):
            # DS100-Codes auflösen
            von_resolved = resolve_station_ds100(von_selection)
            nach_resolved = resolve_station_ds100(nach_selection)

            # Namen für Anzeige
            von = von_resolved.get("name", "Start")
            nach = nach_resolved.get("name", "Ziel")

            if not von_resolved.get("erfolg"):
                st.error(f"Streckenberechnung für '{von}' nicht möglich: DS100-Code fehlt")
                strecke = {"erfolg": False}
                preis = {"erfolg": False}
            elif not nach_resolved.get("erfolg"):
                st.error(f"Streckenberechnung für '{nach}' nicht möglich: DS100-Code fehlt")
                strecke = {"erfolg": False}
                preis = {"erfolg": False}
            else:
                # Daten abrufen
                strecke = get_strecke_details(von_resolved["ds100"], nach_resolved["ds100"])
                preis = get_ticket_preis(von_resolved["eva"], nach_resolved["eva"])

        st.divider()

        # Ergebnisse
        if strecke.get("erfolg"):
            km = strecke["strecke_km"]
            fahrzeit = strecke["fahrzeit_min"]

            # Multiplikatoren
            faktor = 2 if hin_rueck else 1
            km_gesamt = km * faktor * anzahl_personen
            pkm = km * faktor  # Personenkilometer pro Person

            # CO2 Berechnung
            co2_bahn = round(pkm * CO2_FAKTOREN["ice"] / 1000, 2)  # kg
            co2_auto = round(pkm * CO2_FAKTOREN["auto"] / 1000, 2)
            co2_ersparnis = round(co2_auto - co2_bahn, 2)

            # Preis (API oder Schätzung)
            if preis.get("erfolg"):
                preis_anzeige = f"~{preis['preis_avg']:.0f} €"
                preis_detail = f"{preis['preis_min']:.0f}-{preis['preis_max']:.0f} €"
                preis_quelle = "DB API"
            else:
                preis_geschaetzt = round(km * PREIS_PRO_KM)
                preis_anzeige = f"~{preis_geschaetzt} €"
                preis_detail = "geschätzt"
                preis_quelle = "Schätzung (18 ct/km)"

            # Anzeige
            st.subheader("📊 Ergebnis")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Strecke", f"{km} km", delta=f"{'x2 (H+R)' if hin_rueck else 'einfach'}")
            with col_b:
                st.metric("Fahrzeit", f"{fahrzeit} min", delta=f"{round(fahrzeit/60, 1)} h")
            with col_c:
                st.metric("Ticketpreis", preis_anzeige, delta=preis_detail)

            st.divider()

            # CO2 Vergleich
            st.subheader("🌱 CO2-Bilanz")

            if anzahl_personen > 1:
                st.info(f"Berechnung für **{anzahl_personen} Personen** × {km} km {'(Hin+Rück)' if hin_rueck else ''} = **{km_gesamt:.0f} Personen-km**")

            col_x, col_y, col_z = st.columns(3)

            with col_x:
                st.metric("🚄 Bahn (ICE)", f"{co2_bahn * anzahl_personen:.1f} kg CO₂")
            with col_y:
                st.metric("🚗 Auto (Vergleich)", f"{co2_auto * anzahl_personen:.1f} kg CO₂")
            with col_z:
                st.metric("💚 Ersparnis", f"{co2_ersparnis * anzahl_personen:.1f} kg CO₂", delta=f"{round((1 - co2_bahn/co2_auto) * 100)}% weniger")

            st.divider()

            # Fahrstrecke
            st.subheader("🗺️ Fahrstrecke")

            # Wichtige Halte anzeigen
            halte = strecke.get("halte", [])
            if halte:
                st.markdown(f"**{len(halte)} Halte auf dieser Strecke:**")

                # Halte als übersichtliche Liste
                halte_text = ""
                for i, h in enumerate(halte):
                    name = h.get('name', h['ds100'])
                    km_wert = h['km']

                    if i == 0:
                        halte_text += f"🚉 **{name}** (Start)\n\n"
                    elif i == len(halte) - 1:
                        halte_text += f"🏁 **{name}** ({km_wert:.0f} km)\n"
                    else:
                        halte_text += f"→ {name} ({km_wert:.0f} km)\n\n"

                st.markdown(halte_text)

                # VzG-Strecken
                vzg = strecke.get("vzg_strecken", [])
                if vzg:
                    with st.expander("🛤️ VzG-Strecken (technische Details)"):
                        for s in vzg:
                            st.markdown(f"- VzG **{s['nr']}**: {s['von']} → {s['bis']}")

            # Details
            with st.expander("📋 Details für Dokumentation"):
                vzg = strecke.get("vzg_strecken", [])
                halte_namen = [h.get('name', h['ds100']) for h in halte]

                st.markdown(f"""
**Route:** {von} → {nach}
**Strecke:** {km} km {'(Hin- und Rückfahrt: ' + str(km*2) + ' km)' if hin_rueck else ''}
**Fahrzeit:** {fahrzeit} Minuten ({round(fahrzeit/60, 1)} Stunden)
**Halte:** {' → '.join(halte_namen)}

**Anzahl Personen:** {anzahl_personen}
**Personenkilometer:** {km_gesamt:.0f} Pkm

**Ticketpreis:** {preis_anzeige} ({preis_quelle})

**CO₂-Emissionen (Bahn):** {co2_bahn * anzahl_personen:.2f} kg
**CO₂-Emissionen (Auto-Vergleich):** {co2_auto * anzahl_personen:.2f} kg
**CO₂-Ersparnis:** {co2_ersparnis * anzahl_personen:.2f} kg ({round((1 - co2_bahn/co2_auto) * 100)}%)

**VzG-Strecken:** {', '.join([str(s['nr']) for s in vzg])}

---
*Emissionsfaktoren: ICE 29 g/Pkm, PKW 154 g/Pkm (Quelle: UBA 2023)*
*Streckendaten: DB InfraGO Trassenfinder API*
                """)

        else:
            st.error(f"Fehler bei der Streckenberechnung: {strecke.get('fehler', 'Unbekannt')}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    <p>Prototyp für <b>BVGCD</b> - Bundesverband Green Consultants Deutschland</p>
    <p>Datenquellen: DB InfraGO (Trassenfinder), DB REST API, UBA (Emissionsfaktoren)</p>
</div>
""", unsafe_allow_html=True)
