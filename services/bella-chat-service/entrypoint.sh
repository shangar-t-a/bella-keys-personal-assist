#!/bin/sh
set -e

echo "Starting Bella Chat Service..."

# Wait for LangGraph PostgreSQL checkpointer to be ready
echo "Waiting for LangGraph PostgreSQL checkpointer at $LANGGRAPH_PG_DB_HOST:5432..."
timeout=60
elapsed=0
until pg_isready -h "$LANGGRAPH_PG_DB_HOST" -p 5432; do
  if [ $elapsed -ge $timeout ]; then
    echo "Timeout: PostgreSQL did not become ready within ${timeout}s"
    exit 1
  fi
  echo "PostgreSQL not ready yet, waiting... (${elapsed}/${timeout}s)"
  sleep 2
  elapsed=$((elapsed + 2))
done
echo "LangGraph PostgreSQL checkpointer is ready!"

# Start the application
echo "Starting FastAPI application..."
exec python app/main.py