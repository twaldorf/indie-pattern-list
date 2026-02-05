# Pattern Marketplace Backend (Deprecated)

This repository contains the deprecated (no longer in use) backend for the Pattern Marketplace module of Flatland Pattern Studio. It was developed primarily between August and December 2024.

## Stack

- Python + Flask
- MongoDB (via `pymongo`)
- Auth with `flask-login`
- CORS via `flask-cors`
- Rate limiting via `flask-limiter`
- Gunicorn for production

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Start MongoDB locally (default assumes `mongodb://127.0.0.1:27017`).
4. Run the server.

```bash
python server/app.py
```

## Environment Variables

- `FLASK_SECRET_KEY` (required for sessions)
- `ENVIRONMENT` (`PRODUCTION` to enable stricter cookie settings)
- `CORS_ORIGINS` (comma-separated list used in production)
- `MONGODB_URI` (optional; overrides local MongoDB)
- `DB_NAME` (optional; used with `MONGODB_URI`)

## Database Collections

The server uses multiple MongoDB collections:

- `patterns` (main, curated patterns)
- `pen` (user-submitted patterns and updates)
- `garbage` (unused/holding)
- `users`

## API Overview (Selected)

Patterns

- `GET /patterns` (list, supports `category`, `page`, `page_length`, `SortBy=price`)
- `GET /patterns/search?query=...`
- `GET /patterns/summary?limit=...`
- `GET /pattern/<id>`
- `POST /pattern/new` (auth required; inserts into `pen`)
- `POST /pattern/update?_id=<id>` (auth required; inserts/updates in `pen`)

Pen/Moderation

- `GET /pen` (auth required)
- `GET /pen/pattern/<id>`
- `DELETE /pen/<id>`
- `POST /approve/<id>` (moves from `pen` into main collection)

Auth

- `POST /auth/login`
- `POST /auth/create_user`
- `POST /logout`

## Notes

- This repo is deprecated and not in active use.
- The production entrypoint uses Gunicorn as defined in `Procfile`.
