"""EMS MCP Server entry point.

Exposes Expense Manager Service read operations as MCP tools over streamable-HTTP.
"""

from fastmcp import FastMCP

from app.settings import get_settings
from app.tools.accounts import get_account, list_accounts
from app.tools.periods import get_period, list_periods
from app.tools.spending_entries import list_spending_entries, list_spending_entries_for_account

mcp = FastMCP(
    name="ems-mcp-server",
    instructions=(
        "Tools for reading data from the Expense Manager Service (EMS). "
        "Use list_accounts / list_periods to discover available data. "
        "Use list_spending_entries or list_spending_entries_for_account to fetch "
        "balance and spending data, optionally filtered by month, year, or account name."
    ),
)

# Register all tools
for _fn in [
    list_accounts,
    get_account,
    list_periods,
    get_period,
    list_spending_entries,
    list_spending_entries_for_account,
]:
    mcp.add_tool(_fn)


def run() -> None:
    """Entry point for the EMS MCP Server."""
    settings = get_settings()
    mcp.run(
        transport="streamable-http",
        host=settings.HOST,
        port=settings.PORT,
    )


if __name__ == "__main__":
    run()
