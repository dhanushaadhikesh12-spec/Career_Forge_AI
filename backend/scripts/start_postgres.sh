#!/usr/bin/env bash
# Start CareerForge PostgreSQL cluster on port 5433
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PG_DATA="$DIR/postgres_data"
PG_LOG="$DIR/postgres.log"

if /Library/PostgreSQL/18/bin/pg_isready -p 5433 >/dev/null 2>&1; then
  echo "✅ PostgreSQL is already running and accepting connections on port 5433."
else
  echo "🚀 Starting CareerForge PostgreSQL cluster on port 5433..."
  /Library/PostgreSQL/18/bin/pg_ctl -D "$PG_DATA" -l "$PG_LOG" start
  /Library/PostgreSQL/18/bin/pg_isready -p 5433
fi
