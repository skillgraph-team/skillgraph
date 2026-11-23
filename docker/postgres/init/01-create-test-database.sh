#!/bin/sh
# Creates the test database next to the development one, so `uv run pytest` never
# touches your development data. PostgreSQL runs this only when its volume is new;
# if your volume predates this file, run `docker compose down -v` once (wipes local data).
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -c "CREATE DATABASE ${POSTGRES_DB}_test OWNER ${POSTGRES_USER};"
