# EMS MCP Server

Exposes Expense Manager Service read operations as MCP tools over streamable-HTTP.

## Tools

- `list_accounts` / `get_account`
- `list_periods` / `get_period`
- `list_spending_entries` / `list_spending_entries_for_account`

## Run

```bash
uv sync
uv run app/main.py
```

## Debugging with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Open `http://localhost:6274` to inspect the MCP tools exposed by the EMS MCP Server. You can also use the inspector to send requests to the tools and see their responses.
