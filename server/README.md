# Server

FastAPI backend for Viztronics Chargepoint Copilot (Demo).

## Running

The repo root has a start script that builds the client, installs these requirements, seeds the database and starts the API.

## Seeding

```
python -m server.seed --reset
```

This creates a deterministic SQLite database with dummy data for sites, chargers, sessions and incidents. The seed uses the constant `RANDOM_SEED = 424242`.

## Data Model (simplified)

```
Site 1---* Charger 1---* Session
Site 1---* Incident
Action audit log records suggestions and executions from the copilot rules.
```
