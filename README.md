# Back-End-Development-Songs

IBM Back-End Development Capstone Songs microservice, created from the official
ibm-developer-skills-network/hvlga-Back-End-Development-Songs template.
Flask serves a REST API and PyMongo persists songs in a real MongoDB database.

## Run

Use Python 3.9 or later. Provision the lab database with Skills Network Toolbox >
Databases > MongoDB > Create, then copy the connection settings to environment variables.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export MONGODB_SERVICE='<database host>'
export MONGODB_USERNAME='<lab username>'
export MONGODB_PASSWORD='<lab password>'
export MONGODB_PORT=27017
flask --app app run --host 0.0.0.0 --port 5000
```

MONGODB_URI can instead supply a complete URI. MONGODB_DATABASE defaults to songs.
Credentials are never printed or committed. The 20 template songs seed an empty
collection only; server restarts preserve changes. A unique index prevents duplicate IDs.

## API

| Method | Path | Response |
| --- | --- | --- |
| GET | /health | 200, status OK after MongoDB ping |
| GET | /count | 200, count of songs |
| GET | /song | 200, songs array |
| GET | /song/id | 200, song; 404 if absent |
| POST | /song | 201 inserted ID; 302 duplicate per lab |
| PUT | /song/id | 201 changed song per lab example; 200 unchanged; 404 absent |
| DELETE | /song/id | 204 empty body; 404 absent |

POST requires integer id and string title and lyrics. PUT accepts song fields,
uses MongoDB $set, and rejects a changed ID. Invalid input returns 400.
ObjectIds are encoded as MongoDB Extended JSON.

```sh
curl -i http://localhost:5000/health
curl -i http://localhost:5000/song
curl -i -X PUT http://localhost:5000/song/1 -H 'Content-Type: application/json' --data '{"lyrics":"yay hey yay yay","title":"yay song"}'
curl -i -X DELETE http://localhost:5000/song/14
pytest -v
```

## Attribution

The starting template and seed data are IBM Apache-2.0 licensed material.
Implementation and documentation were developed with AI assistance (OpenAI Codex).
Runtime evidence comes from actual requests against MongoDB, not mocked responses.
This is an educational project, not a production deployment.
