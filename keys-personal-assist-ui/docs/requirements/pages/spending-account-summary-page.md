# Spending Account Summary Requirements

## Overview

The Spending Account Summary page provides users with a comprehensive view of their account status, spending patterns, and credit history. The page consists of two main sections: a dashboard with key metrics and a detailed transaction table.

## Detailed Requirements

### 1. Page Layout and Navigation

1. Retrieve API endpoint details from `openai.json`. Use these endpoints to fetch data for the page and ensure proper integration with the backend. Make sure to handle API errors gracefully and display user-friendly messages.
2. Implement responsive design for desktop and mobile views
3. Show loading states while data is being fetched

### 2. Dashboard Section (Top)

#### Key Metrics Display

1. Current Balance (Last Month)
   1. Display the current balance from the last or latest month
   2. Show balance in Indian Rupees (₹)
   3. Show trend indicator (up/down) comparing with previous month available
      1. The trend indication calculation is done by frontend
      2. Use green up arrow for positive trend (increase in value) and red down arrow for negative trend
      3. Show percentage change from last month (e.g., "10.5% from last month" or "5.2% from last month"). The percentage should also follow same color convention as the trend indicator
      4. The trend indicator should be updated dynamically when the current balance changes
      5. If there is no previous month data available, do not show the trend indicator

2. Current Credit (Last Month)
   1. Display total credit amount from the last or latest month
   2. Show credit in Indian Rupees (₹)
   3. Show trend indicator (up/down) comparing with previous month available
      1. The trend indication calculation is done by frontend
      2. Use red up arrow for positive trend (increase in value) and green down arrow for negative trend. This is because a decrease in credit is a positive trend (less credit used)
      3. Show percentage change from last month (e.g., "10.5% from last month" or "5.2% from last month"). The percentage should also follow same color convention as the trend indicator
      4. The trend indicator should be updated dynamically when the current credit changes
      5. If there is no previous month data available, do not show the trend indicator

3. Total Spending (Filtered Period)
   1. Calculate sum of all spending from filtered table data
   2. Update dynamically when table filters change

4. Total Credit (Filtered Period)
   1. Sum of all credit transactions from filtered data
   2. Update dynamically with filter changes

### 3. Account Summary Table (Bottom)

#### Table Configuration

1. Columns (in order):
   1. Month (sortable)
   2. Year (sortable)
   3. Starting Balance (sortable)
   4. Current Balance (sortable)
   5. Current Credit (sortable)
   6. Balance After Credit (sortable)
   7. Total Spent (sortable)

2. Filtering Capabilities:
   1. Implement 3 filters: Account, Month, and Year
   2. Account filter
      1. Control type: Dropdown
      2. Show all available accounts from the API
      3. Select first account by default
      4. No `All Accounts` option. Table is designed to display one account at a time
      5. When account is changed, reset Month and Year filters to default state
      6. Default: First account in the list
   3. Month filter
      1. Control type: Dropdown
      2. Show all months for the selected account. Months should be in chronological order (January to December)
      3. Select All Months by default: `All Months`
      4. Default: `All months`
   4. Year filter
      1. Control type: Dropdown
      2. Show all years for the selected account
      3. Select All Years by default: `All Years`
      4. When Year is changed, reset Month filter to default state
      5. Default: `All years`
   5. Apply filters to table data dynamically
   6. Provide `Reset Filters` button to clear all filters
   7. Persist filter state across page reloads
   8. Default filter state should be:
      1. Account: First account in the list
      2. Month: All months
      3. Year: All years

3. Sorting Features:
   1. Enable multi-column sorting
   2. Set default sort to latest month and latest year
   3. Display visual indicators for sort direction

4. Pagination:
   1. Provide page size options: 10, 25, 50, 100 rows
   2. Display total number of records
   3. Enable quick navigation to first/last pages
   4. Pagination is handled by the frontend, not the backend

5. Add Entry:
   1. Provide a `Add Entry` button to add a new entry to the account
   2. Open a modal form for entry creation. The form should include:
      1. Account selection (dropdown) - List of available accounts
      2. Month selection (dropdown) - List of all months (January to December)
      3. Year selection (year input)
      4. Starting Balance (input field)
      5. Current Balance (input field)
      6. Current Credit (input field)
   3. Provide a button to save the new entry. Do error handling when calling create entry API. When there is an error, display a user-friendly message and keep the modal open for corrections
   4. Refresh the table data after successful entry creation
   5. Close the modal after successful entry creation

6. Update Entry:
   1. Display pencil icon next to each row for editing. Use a modern, intuitive icon
   2. On click, open a modal with pre-filled data for the selected entry
   3. Allow users to update the entry details
   4. Provide a button to save changes. Do error handling when calling update entry API. When there is an error, display a user-friendly message and keep the modal open for corrections
   5. Refresh the table data after successful update
   6. Close the modal after successful update

7. Delete Entry:
   1. Display trash icon next to each row for deletion. Use a modern, intuitive icon
   2. On click, show a confirmation dialog
   3. If confirmed, call the delete entry API
   4. Refresh the table data after successful deletion

### 4. Data Formatting

1. Use Indian Rupees (₹) for all monetary values
2. Implement proper Indian number formatting (e.g., 1,00,000)
3. Format negative values:
   1. Display in red color
   2. Prefix with minus (-)
4. Display positive values in green color
5. Use date format: MMM YYYY (e.g., Jul 2025)

### 5. Performance Requirements

1. Ensure initial page load under 2 seconds
2. Complete table updates within 500ms of filter changes
3. Implement data caching for better performance
4. Enable lazy loading for table data

### 6. Error Handling

1. Display appropriate error messages for failed API calls
2. Implement retry mechanism for failed requests
3. Preserve filter state during error recovery
