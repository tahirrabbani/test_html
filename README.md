# Viztronics Chargepoint Copilot (Demo)

This repository contains a self-contained demo web application showing reporting dashboards and a rule-based operations copilot for an EV charging network. The backend is FastAPI with SQLite and a deterministic seeding script. The frontend uses React, Vite and Tailwind.

## Running

```
npm start
```

The start script builds the React client, installs Python requirements, seeds the SQLite database and launches the API on `$PORT` (default `8000`). Open the resulting URL to explore.

To reset and reseed the demo data at any time run:

```
python -m server.seed --reset
```

## Tests

```
pip install -r server/requirements.txt
pytest server/tests -q
```
