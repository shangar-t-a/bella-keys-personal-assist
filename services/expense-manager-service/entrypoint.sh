#!/bin/sh
set -e

echo "Starting Expense Manager Service..."

echo "Waiting for PostgreSQL to be ready at $PG_DB_HOST:5432..."
timeout=60
elapsed=0
until pg_isready -h "$PG_DB_HOST" -p 5432; do
  if [ $elapsed -ge $timeout ]; then
    echo "Timeout: PostgreSQL did not become ready within ${timeout}s"
    exit 1
  fi
  echo "PostgreSQL not ready yet, waiting... (${elapsed}/s)"
  sleep 2
  elapsed=$((elapsed + 2))
done
echo "PostgreSQL is ready!"

# Show current migration version
echo "Current database migration version:"
alembic -c app/infrastructures/postgres_db/alembic.ini current

# Show latest migration version
echo "Latest available migration version:"
alembic -c app/infrastructures/postgres_db/alembic.ini heads

# Run database migrations
echo "Running database migrations..."
alembic -c app/infrastructures/postgres_db/alembic.ini upgrade head

# Seed/update data to database
echo "Seeding/updating data to the database..."
python scripts/db/data/manager.py

# Show final migration version after upgrade
echo "Database migration version after upgrade:"
alembic -c app/infrastructures/postgres_db/alembic.ini current

# Start the application
echo "Starting FastAPI application..."
exec python app/main.py