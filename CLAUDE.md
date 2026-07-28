# CLAUDE.md

## Project Overview

Bahn-Streckenrechner: A Streamlit web app for calculating German rail distances, CO2 emissions, and ticket prices. Prototype for BVGCD (Bundesverband Green Consultants Deutschland).

**Live:** https://bahn-streckenrechner.streamlit.app

## Tech Stack

- **Python + Streamlit** (UI framework)
- **streamlit-searchbox** for autocomplete station search
- **requests** for API calls
- Dependencies in `requirements.txt`

## Project Structure

```
app.py                    # Main Streamlit app (UI + API logic)
bahn_info.py              # Standalone CLI tool for route/price queries
show_route.py             # CLI tool to display full route details
test_api.py               # CLI test script for Trassenfinder API
trassenfinder_api_test.py # Playwright-based API explorer (one-off script)
requirements.txt          # Python dependencies
.devcontainer/            # Dev container config
```

## External APIs

- **Trassenfinder API** (`https://openapi.trassenfinder.de/api/v9`) - Rail distance (km) and route details via DS100 station codes
- **DB REST API** (`https://v6.db.transport.rest`) - Ticket prices, station search, and EVA station codes

## Key Concepts

- **DS100/RIL100**: German railway station codes (e.g., "BL" = Berlin Hbf)
- **EVA codes**: Numeric station IDs used by DB APIs (e.g., "8011160" = Berlin Hbf)
- **VzG-Strecken**: Official German rail line numbers
- **CO2 factors** from UBA 2023 (ICE: 29 g/Pkm, Auto: 154 g/Pkm)

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed on Streamlit Cloud. Push to `main` triggers automatic deployment.

## Code Conventions

- Language: German variable names, comments, and UI text
- No test framework configured; test scripts are standalone CLI tools
- API calls use `requests` with timeouts and `@st.cache_data` for caching
