# Projektplan Videoflix

## Aktueller Ausgangspunkt

Das GitHub-Repository ist erstellt und lokal geklont. Die Backend-Implementierung soll noch sauber gestartet werden. Das Frontend bleibt ein separates Nachbarprojekt und wird nicht in dieses Repository kopiert.

## Externe Vorgaben

- Docker-Dateien: `claude`
- Frontend: `git@github.com:Developer-Akademie-Backendkurs/project.Videoflix.git`
- Endpoint-Dokumentation: `https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=videoflix`
- Original-Checkliste: `docs/Videoflix Checkliste.md`

## Erster Umsetzungsschritt

Issue `#1` muss die Projektgrundlage herstellen:

1. vorgegebene Docker-Dateien aus dem Docker-Repository unverändert übernehmen
2. `.env.template` aus der Vorlage übernehmen
3. `.env` in `.gitignore` eintragen
4. Projekt mit `uv` und Python 3.12 initialisieren
5. Django-Projekt mit dem Namen `core` erstellen
6. `pyproject.toml`, `uv.lock` und `requirements.txt` konsistent halten
7. Docker-Start testen

## Technische Festlegungen

- Backend: Django REST Framework
- Python: 3.12, passend zum Dockerfile
- Django: 5.2 LTS
- Paketverwaltung lokal: uv
- Docker-Installation: `pip install -r requirements.txt`
- Datenbank: PostgreSQL
- Cache und Queue: Redis, getrennte Datenbanken für Cache und Django-RQ
- Hintergrundjobs: Django-RQ
- Codequalität: Ruff mit Importsortierung, PEP-8-Regeln, snake_case, ungenutzten Imports/Variablen und D101

## Wichtige Architekturregeln

- Das Django-Projekt muss `core` heißen, weil Docker `gunicorn core.wsgi:application` startet.
- Die Docker-Dateien aus der Akademie-Vorlage werden nicht verändert.
- Das Backend-Repository enthält nur das Backend, nicht das Frontend.
- Das Custom-User-Modell muss vor der ersten Migration angelegt werden.
- Das User-Modell behält `username`, damit der Docker-Superuser funktioniert.
- Nutzer melden sich fachlich per E-Mail an.

## Definition of Done

Das Projekt ist erst fertig, wenn alle Punkte aus `docs/Videoflix Checkliste.md` und alle GitHub-Issues der Milestone `Videoflix Backend Abschlussprojekt` abgearbeitet sind.
