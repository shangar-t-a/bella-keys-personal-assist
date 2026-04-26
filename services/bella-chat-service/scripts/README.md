# Utility Scripts

## `setup-postgres-checkpoints.py`

Verifies LangGraph Postgres checkpointer connection and initializes checkpoint tables.

**Usage:**

```bash
cd services/bella-chat-service
python scripts/setup-postgres-checkpoints.py
```

**Prerequisites:**

- Database and user must already exist on your Postgres server
- `.env` file must have `LANGGRAPH_PG_DB_*` credentials set

**Note:** When running from host, ensure `.env` password matches the database user password.
