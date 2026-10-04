#!/usr/bin/env bash
# Stop CareerForge PostgreSQL cluster on port 5433
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PG_DATA="$DIR/postgres_data"

echo "🛑 Stopping CareerForge PostgreSQL cluster on port 5433..."
/Library/PostgreSQL/18/bin/pg_ctl -D "$PG_DATA" stop
