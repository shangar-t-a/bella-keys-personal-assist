# EMS MCP Server

This Model Context Protocol (MCP) server exposes Expense Manager Service (EMS) operations as tools over streamable-HTTP and stdio transports.

## Core Tools

The server exposes tools for interacting with the following domains of the Expense Manager Service:

* **Accounts** (`list_accounts`, `get_account`, `get_or_create_account`, `update_account_name`, `delete_account`)
* **Periods** (`list_periods`, `get_period`, `get_or_create_period`, `update_period`, `delete_period`)
* **Spending Entries** (`list_spending_entries`, `list_spending_entries_for_account`, `add_spending_entry`, `edit_spending_entry`, `delete_spending_entry`)
* **Assets** (`list_asset_categories`, `list_assets`, `get_asset_by_id`, `create_asset`, `update_asset`, `delete_asset`, `get_asset_summary`, `get_transactions_for_asset`, `add_asset_transaction`, `delete_asset_transaction`)
* **Liabilities** (`list_liability_categories`, `list_liabilities`, `get_liability_by_id`, `create_liability`, `update_liability`, `delete_liability`, `get_liability_summary`, `get_transactions_for_liability`, `add_liability_transaction`, `delete_liability_transaction`, `get_liability_projections`)
* **Monthly Planner** (`list_monthly_categories`, `add_monthly_category`, `delete_monthly_category`, `get_monthly_summary`, `update_monthly_salary`, `list_monthly_expenses`, `add_monthly_expense`, `update_monthly_expense`, `delete_monthly_expense`, `reset_monthly_expense_statuses`, `sync_monthly_expenses_from_previous_month`)
* **Savings Buckets** (`list_savings_buckets`, `create_savings_bucket`, `update_savings_bucket`, `delete_savings_bucket`, `create_savings_bucket_transaction`, `list_savings_bucket_transactions`, `cancel_savings_bucket_transaction`)
* **Wealth** (`get_wealth_summary`, `get_historical_net_worth`, `get_wealth_allocation`)

## Configuration

Configure the server via environment variables or a `.env` file:

* `HOST`: The host to bind the server to (default: `0.0.0.0`).
* `PORT`: The port to run the server on (default: `8001`).
* `EMS_BASE_URL`: The URL of the running Expense Manager Service (default: `http://localhost:8000`).
* `AUTH_SERVICE_URL`: The URL of the running Authentication Service (default: `http://localhost:8002`).

## Authentication

When running over HTTP-based transports (like `streamable-http` or `sse`), the server secures its endpoints using token validation middleware:

1. It intercepts incoming requests and extracts the `Authorization: Bearer <token>` header.
2. It locally validates the JWT signature using the shared `JWT_SECRET`.
3. It checks that the target audience (`aud`) matches the server's configured `BASE_URL` to protect against token reuse/replay.
4. The validated request is processed, and the Bearer token is forwarded dynamically in downstream HTTP calls to the EMS backend.

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

## Running Tests

To run the unit tests:

```bash
uv run pytest
```

## Testing and Debugging

Use the MCP Inspector to verify tool behaviors via HTTP/SSE. Since the downstream EMS service requires JWT authentication, follow these steps to connect and authorize:

1. **Start the MCP Server on a custom port:**
   To avoid conflicts with containerized services running on port `8001`, start the local server on a different port (e.g. `8009`):

   * **PowerShell:**

     ```powershell
     $env:PORT=8009
     uv run app/main.py
     ```

   * **Git Bash / Linux / macOS:**

     ```bash
     PORT=8009 uv run app/main.py
     ```

2. **Obtain a JWT token:**
   Register or log in to the Auth Service (running on port `8002`) via the main application UI authentication flow.

3. **Start the MCP Inspector:**
   Run the inspector in proxy-only mode (without any server command arguments):

   ```bash
   npx @modelcontextprotocol/inspector
   ```

4. **Connect in the Inspector UI:**
   * Open `http://localhost:6274` in your browser.
   * Set **Transport Type** to `SSE`.
   * Set the **URL** to `http://localhost:8009/sse`.
   * Under **Headers**, add a header with name `Authorization` and value `Bearer <your_token>`.
   * Click **Connect** to interactively test the tools.
