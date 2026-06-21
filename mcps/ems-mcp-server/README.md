# EMS MCP Server

This Model Context Protocol (MCP) server exposes Expense Manager Service (EMS) read operations as tools over streamable-HTTP.

## Core Tools

* `list_accounts` / `get_account`
* `list_periods` / `get_period`
* `list_spending_entries` / `list_spending_entries_for_account`

## Configuration

Configure the server via environment variables or a `.env` file:

* `HOST`: The host to bind the server to (default: `0.0.0.0`).
* `PORT`: The port to run the server on (default: `8001`).
* `EMS_BASE_URL`: The URL of the running Expense Manager Service (default: `http://localhost:8000`).
* `AUTH_SERVICE_URL`: The URL of the running Authentication Service (default: `http://localhost:8002`).

## Authentication

When running over HTTP-based transports (like `streamable-http` or `sse`), the server secures its endpoints using token validation middleware:
1. It intercepts incoming requests and extracts the `Authorization: Bearer <token>` header.
2. It queries `AUTH_SERVICE_URL/me` to authenticate the user and verify token validity.
3. Once validated, the request is processed, and the token is forwarded dynamically to the EMS backend.

For local execution and debugging using the `stdio` transport, the authentication middleware is bypassed automatically.

## Running the Server

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Start the server:
   ```bash
   uv run app/main.py
   ```

## Testing and Debugging

Use the MCP Inspector to verify tool behaviors:

```bash
npx @modelcontextprotocol/inspector
```

Access the inspector in your browser at `http://localhost:6274` to execute and debug tools.
