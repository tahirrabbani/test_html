# Viztronics Chargepoint Copilot (Demo)

This repository contains a small demo web application showing reporting dashboards and a rule-based operations copilot for an EV charging network. The backend is FastAPI with SQLite and a deterministic seeding script. The frontend uses React, Vite and Tailwind.

## Running

```
npm start
```

The start script will build the React client, install Python requirements, seed the SQLite database and launch the API on port 8000. Open the resulting URL to explore.

To reset and reseed the demo data at any time run:

```
python -m server.seed --reset
```

## Tests

```
pip install -r server/requirements.txt
pytest server/tests -q
```
