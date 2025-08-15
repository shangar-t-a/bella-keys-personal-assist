import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  getAllAccounts,
  getAllSpendingAccountEntriesForAccount,
  getAllMonthYears,
  deleteSpendingAccountEntry,
} from '../api/client';
import { AccountNameResponse, SpendingAccountEntryWithCalculatedFieldsResponse, MonthYearResponse } from '../types/api';
import { formatCurrency, formatMonthYear, getMonthIndex } from '../utils/formatters';
import AddEntryModal from '../components/AddEntryModal';
import EditEntryModal from '../components/EditEntryModal';
import DeleteConfirmationModal from '../components/DeleteConfirmationModal';
import './SpendingAccountSummary.css';

// Define month order for sorting
const MONTH_ORDER = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const SpendingAccountSummary: React.FC = () => {
  const [accounts, setAccounts] = useState<AccountNameResponse[]>([]);
  const [monthYears, setMonthYears] = useState<MonthYearResponse[]>([]); // Not directly used for filters, but kept for potential future use or context
  const [selectedAccount, setSelectedAccount] = useState<string | null>(() => localStorage.getItem('selectedAccount') || null);
  const [selectedMonth, setSelectedMonth] = useState<string | null>(() => localStorage.getItem('selectedMonth') || 'All Months');
  const [selectedYear, setSelectedYear] = useState<string | null>(() => localStorage.getItem('selectedYear') || 'All Years');
  const [entries, setEntries] = useState<SpendingAccountEntryWithCalculatedFieldsResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [sortColumn, setSortColumn] = useState<keyof SpendingAccountEntryWithCalculatedFieldsResponse | null>('year');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // Modals state
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [editingEntry, setEditingEntry] = useState<SpendingAccountEntryWithCalculatedFieldsResponse | null>(null);
  const [deletingEntryId, setDeletingEntryId] = useState<string | null>(null);

  // Function to fetch entries for the currently selected account
  const fetchEntriesForSelectedAccount = useCallback(async (accountId: string) => {
    setLoading(true);
    setError(null);
    try {
      const fetchedEntries = await getAllSpendingAccountEntriesForAccount(accountId);
      setEntries(fetchedEntries);
    } catch (err) {
      setError('Failed to fetch spending account entries.');
      console.error('Error fetching entries:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch accounts and initial selected account
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const fetchedAccounts = await getAllAccounts();
        setAccounts(fetchedAccounts);
        if (fetchedAccounts.length > 0) {
          const storedAccount = localStorage.getItem('selectedAccount');
          if (storedAccount && fetchedAccounts.some(acc => acc.id === storedAccount)) {
            setSelectedAccount(storedAccount);
            fetchEntriesForSelectedAccount(storedAccount);
          } else {
            setSelectedAccount(fetchedAccounts[0].id);
            localStorage.setItem('selectedAccount', fetchedAccounts[0].id);
            fetchEntriesForSelectedAccount(fetchedAccounts[0].id);
          }
        } else {
          setSelectedAccount(null);
          localStorage.removeItem('selectedAccount');
          setLoading(false);
        }
      } catch (err) {
        setError('Failed to fetch accounts.');
        console.error('Error fetching accounts:', err);
        setSelectedAccount(null);
        localStorage.removeItem('selectedAccount');
        setLoading(false);
      }
    };
    fetchAccounts();
  }, [fetchEntriesForSelectedAccount]);

  // Fetch month/year combinations (kept for completeness, though not directly used for filters as entries provide this)
  useEffect(() => {
    const fetchMonthYears = async () => {
      try {
        const fetchedMonthYears = await getAllMonthYears();
        setMonthYears(fetchedMonthYears);
      } catch (err) {
        setError('Failed to fetch month and year data.');
        console.error('Error fetching month years:', err);
      }
    };
    fetchMonthYears();
  }, []);

  // Re-fetch entries when selectedAccount changes
  useEffect(() => {
    if (selectedAccount) {
      fetchEntriesForSelectedAccount(selectedAccount);
    } else {
      setEntries([]);
      setLoading(false);
    }
  }, [selectedAccount, fetchEntriesForSelectedAccount]);

  // Persist selected filters to localStorage
  useEffect(() => {
    if (selectedAccount) localStorage.setItem('selectedAccount', selectedAccount);
    if (selectedMonth) localStorage.setItem('selectedMonth', selectedMonth);
    if (selectedYear) localStorage.setItem('selectedYear', selectedYear);
  }, [selectedAccount, selectedMonth, selectedYear]);

  const handleAccountChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newAccountId = event.target.value;
    setSelectedAccount(newAccountId);
    setSelectedMonth('All Months');
    setSelectedYear('All Years');
    setCurrentPage(1);
  };

  const handleMonthChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedMonth(event.target.value);
    // Removed: setSelectedYear('All Years'); as per updated requirements
    setCurrentPage(1);
  };

  const handleYearChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedYear(event.target.value);
    setSelectedMonth('All Months');
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    if (accounts.length > 0) {
      setSelectedAccount(accounts[0].id);
      localStorage.setItem('selectedAccount', accounts[0].id);
    } else {
      setSelectedAccount(null);
      localStorage.removeItem('selectedAccount');
    }
    setSelectedMonth('All Months');
    setSelectedYear('All Years');
    localStorage.setItem('selectedMonth', 'All Months');
    localStorage.setItem('selectedYear', 'All Years');
    setCurrentPage(1);
    setSortColumn('year');
    setSortDirection('desc');
  };

  // Filtered and Sorted Entries
  const filteredEntries = useMemo(() => {
    let currentFilteredEntries = entries;

    if (selectedMonth && selectedMonth !== 'All Months') {
      currentFilteredEntries = currentFilteredEntries.filter(entry => entry.month === selectedMonth);
    }

    if (selectedYear && selectedYear !== 'All Years') {
      currentFilteredEntries = currentFilteredEntries.filter(entry => entry.year.toString() === selectedYear);
    }

    // Apply sorting
    if (sortColumn) {
      currentFilteredEntries = [...currentFilteredEntries].sort((a, b) => {
        let valA: any = a[sortColumn];
        let valB: any = b[sortColumn];

        if (sortColumn === 'month') {
          valA = getMonthIndex(valA);
          valB = getMonthIndex(valB);
        }

        if (typeof valA === 'string' && typeof valB === 'string') {
          return sortDirection === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
        } else {
          return sortDirection === 'asc' ? (valA - valB) : (valB - valA);
        }
      });
    } else {
      // Default sort: latest month and latest year
      currentFilteredEntries.sort((a, b) => {
        if (a.year !== b.year) {
          return b.year - a.year;
        }
        return getMonthIndex(b.month) - getMonthIndex(a.month);
      });
    }

    return currentFilteredEntries;
  }, [entries, selectedMonth, selectedYear, sortColumn, sortDirection]);

  // Get unique months and years for the selected account from the fetched entries
  const availableMonths = useMemo(() => {
    const months = new Set<string>();
    entries.forEach(entry => months.add(entry.month));
    return ['All Months', ...MONTH_ORDER.filter(month => months.has(month))];
  }, [entries]);

  const availableYears = useMemo(() => {
    const years = new Set<number>();
    entries.forEach(entry => years.add(entry.year));
    return ['All Years', ...Array.from(years).sort((a, b) => b - a).map(String)];
  }, [entries]);

  // Dashboard Metrics Calculation
  const { currentBalanceLastMonth, currentCreditLastMonth, totalSpendingFiltered, totalCreditFiltered } = useMemo(() => {
    let currentBalanceLastMonth = 0;
    let currentCreditLastMonth = 0;
    let totalSpending = 0;
    let totalCredit = 0;

    // For "Last Month" metrics, we need the latest entry from the *unfiltered* entries
    // This ensures the trend is always based on the actual last month, not the last month in a filtered view
    if (entries.length > 0) {
      const sortedByDateEntries = [...entries].sort((a, b) => {
        if (a.year !== b.year) {
          return b.year - a.year;
        }
        return getMonthIndex(b.month) - getMonthIndex(a.month);
      });
      const latestEntry = sortedByDateEntries[0];
      currentBalanceLastMonth = latestEntry.currentBalance;
      currentCreditLastMonth = latestEntry.currentCredit;
    }

    // For "Filtered Period" metrics, sum up all *filtered* entries
    filteredEntries.forEach(entry => {
      totalSpending += entry.totalSpent;
      totalCredit += entry.currentCredit;
    });

    return {
      currentBalanceLastMonth,
      currentCreditLastMonth,
      totalSpendingFiltered: totalSpending,
      totalCreditFiltered: totalCredit,
    };
  }, [entries, filteredEntries]);

  // Trend calculation for Current Balance (Last Month)
  const balanceTrend = useMemo(() => {
    if (entries.length < 2) {
      return null; // Not enough data for trend
    }
    const sortedByDateEntries = [...entries].sort((a, b) => {
      if (a.year !== b.year) {
        return b.year - a.year;
      }
      return getMonthIndex(b.month) - getMonthIndex(a.month);
    });
    const latest = sortedByDateEntries[0].currentBalance;
    const previous = sortedByDateEntries[1].currentBalance;
    const diff = latest - previous;
    const percentageChange = previous !== 0 ? (diff / previous) * 100 : 0;
    const isPositiveTrend = diff > 0; // Increase in balance is positive
    const colorClass = isPositiveTrend ? 'positive-trend' : 'negative-trend';
    const arrow = isPositiveTrend ? '▲' : '▼';

    return (
      <span className={`trend-indicator ${colorClass}`}>
        {arrow} {Math.abs(percentageChange).toFixed(1)}% from last month
      </span>
    );
  }, [entries]);

  // Trend calculation for Current Credit (Last Month)
  const creditTrend = useMemo(() => {
    if (entries.length < 2) {
      return null; // Not enough data for trend
    }
    const sortedByDateEntries = [...entries].sort((a, b) => {
      if (a.year !== b.year) {
        return b.year - a.year;
      }
      return getMonthIndex(b.month) - getMonthIndex(a.month);
    });
    const latest = sortedByDateEntries[0].currentCredit;
    const previous = sortedByDateEntries[1].currentCredit;
    const diff = latest - previous;
    const percentageChange = previous !== 0 ? (diff / previous) * 100 : 0;
    // As per requirements: "decrease in credit is a positive trend (less credit used)"
    const isPositiveTrend = diff < 0;
    const colorClass = isPositiveTrend ? 'positive-trend' : 'negative-trend';
    // As per requirements: "Use red up arrow for positive trend (increase in value) and green down arrow for negative trend."
    // If positive trend (decrease in credit value), use green down arrow.
    // If negative trend (increase in credit value), use red up arrow.
    const arrow = isPositiveTrend ? '▼' : '▲';

    return (
      <span className={`trend-indicator ${colorClass}`}>
        {arrow} {Math.abs(percentageChange).toFixed(1)}% from last month
      </span>
    );
  }, [entries]);

  const handleSort = (column: keyof SpendingAccountEntryWithCalculatedFieldsResponse) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc'); // Default to ascending when changing column
    }
  };

  const getSortIndicator = (column: keyof SpendingAccountEntryWithCalculatedFieldsResponse) => {
    if (sortColumn === column) {
      return sortDirection === 'asc' ? ' ▲' : ' ▼';
    }
    return '';
  };

  // Pagination logic
  const totalPages = Math.ceil(filteredEntries.length / pageSize);
  const paginatedEntries = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return filteredEntries.slice(startIndex, endIndex);
  }, [filteredEntries, currentPage, pageSize]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setCurrentPage(1); // Reset to first page when page size changes
  };

  // CRUD operations handlers
  const handleAddEntryClick = () => {
    setShowAddModal(true);
  };

  const handleEditEntryClick = (entry: SpendingAccountEntryWithCalculatedFieldsResponse) => {
    setEditingEntry(entry);
    setShowEditModal(true);
  };

  const handleDeleteEntryClick = (entryId: string) => {
    setDeletingEntryId(entryId);
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = async () => {
    if (deletingEntryId && selectedAccount) {
      try {
        await deleteSpendingAccountEntry(deletingEntryId);
        setShowDeleteConfirm(false);
        setDeletingEntryId(null);
        fetchEntriesForSelectedAccount(selectedAccount); // Refresh data
      } catch (err) {
        setError('Failed to delete entry. Please try again.');
        console.error('Error deleting entry:', err);
      }
    }
  };

  const handleModalClose = () => {
    setShowAddModal(false);
    setShowEditModal(false);
    setShowDeleteConfirm(false);
    setEditingEntry(null);
    setDeletingEntryId(null);
  };

  const handleDataRefresh = () => {
    if (selectedAccount) {
      fetchEntriesForSelectedAccount(selectedAccount);
    }
  };

  if (loading && accounts.length === 0 && selectedAccount === null) {
    return <div className="loading-state">Loading spending account summary...</div>;
  }

  if (error) {
    return <div className="error-state">{error}</div>;
  }

  // If no accounts are available after loading, display a message
  if (accounts.length === 0 && !loading && !error) {
    return (
      <div className="spending-account-summary-container">
        <h1 className="page-title">Spending Account Summary</h1>
        <div className="no-accounts-message">
          No spending accounts found. Please add an account to view summaries.
        </div>
      </div>
    );
  }

  return (
    <div className="spending-account-summary-container">
      <h1 className="page-title">Spending Account Summary</h1>

      {/* Dashboard Section */}
      <div className="dashboard-metrics-grid">
        <div className="metric-card">
          <h3>Current Balance (Last Month)</h3>
          <p className={`metric-value ${currentBalanceLastMonth < 0 ? 'negative-value' : 'positive-value'}`}>
            {formatCurrency(currentBalanceLastMonth)}
          </p>
          {balanceTrend}
        </div>
        <div className="metric-card">
          <h3>Current Credit (Last Month)</h3>
          <p className={`metric-value ${currentCreditLastMonth < 0 ? 'negative-value' : 'positive-value'}`}>
            {formatCurrency(currentCreditLastMonth)}
          </p>
          {creditTrend}
        </div>
        <div className="metric-card">
          <h3>Total Spending (Filtered Period)</h3>
          <p className={`metric-value ${totalSpendingFiltered < 0 ? 'negative-value' : 'positive-value'}`}>
            {formatCurrency(totalSpendingFiltered)}
          </p>
        </div>
        <div className="metric-card">
          <h3>Total Credit (Filtered Period)</h3>
          <p className={`metric-value ${totalCreditFiltered < 0 ? 'negative-value' : 'positive-value'}`}>
            {formatCurrency(totalCreditFiltered)}
          </p>
        </div>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="account-filter">Account:</label>
          <select id="account-filter" value={selectedAccount || ''} onChange={handleAccountChange}>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.accountName}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="month-filter">Month:</label>
          <select id="month-filter" value={selectedMonth || 'All Months'} onChange={handleMonthChange}>
            {availableMonths.map((month) => (
              <option key={month} value={month}>
                {month}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="year-filter">Year:</label>
          <select id="year-filter" value={selectedYear || 'All Years'} onChange={handleYearChange}>
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
        <button className="reset-filters-button" onClick={handleResetFilters}>Reset Filters</button>
      </div>

      {/* Account Summary Table */}
      <div className="account-summary-table-section">
        <div className="table-header-controls">
          <h2>Account Entries</h2>
          <button className="add-entry-button" onClick={handleAddEntryClick}>Add Entry</button>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th onClick={() => handleSort('month')}>Month{getSortIndicator('month')}</th>
                <th onClick={() => handleSort('year')}>Year{getSortIndicator('year')}</th>
                <th onClick={() => handleSort('startingBalance')}>Starting Balance{getSortIndicator('startingBalance')}</th>
                <th onClick={() => handleSort('currentBalance')}>Current Balance{getSortIndicator('currentBalance')}</th>
                <th onClick={() => handleSort('currentCredit')}>Current Credit{getSortIndicator('currentCredit')}</th>
                <th onClick={() => handleSort('balanceAfterCredit')}>Balance After Credit{getSortIndicator('balanceAfterCredit')}</th>
                <th onClick={() => handleSort('totalSpent')}>Total Spent{getSortIndicator('totalSpent')}</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedEntries.length === 0 ? (
                <tr>
                  <td colSpan={8} className="no-data">No entries found for the selected filters.</td>
                </tr>
              ) : (
                paginatedEntries.map((entry) => (
                  <tr key={entry.id}>
                    <td>{formatMonthYear(entry.month, entry.year).split(' ')[0]}</td>
                    <td>{formatMonthYear(entry.month, entry.year).split(' ')[1]}</td>
                    <td className={entry.startingBalance < 0 ? 'negative-value' : 'positive-value'}>
                      {formatCurrency(entry.startingBalance)}
                    </td>
                    <td className={entry.currentBalance < 0 ? 'negative-value' : 'positive-value'}>
                      {formatCurrency(entry.currentBalance)}
                    </td>
                    <td className={entry.currentCredit < 0 ? 'negative-value' : 'positive-value'}>
                      {formatCurrency(entry.currentCredit)}
                    </td>
                    <td className={entry.balanceAfterCredit < 0 ? 'negative-value' : 'positive-value'}>
                      {formatCurrency(entry.balanceAfterCredit)}
                    </td>
                    <td className={entry.totalSpent < 0 ? 'negative-value' : 'positive-value'}>
                      {formatCurrency(entry.totalSpent)}
                    </td>
                    <td>
                      <button className="action-button" onClick={() => handleEditEntryClick(entry)}>Edit</button>
                      <button className="action-button delete-button" onClick={() => handleDeleteEntryClick(entry.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {/* Pagination Controls */}
        <div className="pagination-controls">
          <p>Total Records: {filteredEntries.length}</p>
          <div className="pagination-buttons">
            <button onClick={() => handlePageChange(1)} disabled={currentPage === 1}>First</button>
            <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>Previous</button>
            <span>Page {currentPage} of {totalPages}</span>
            <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
            <button onClick={() => handlePageChange(totalPages)} disabled={currentPage === totalPages}>Last</button>
          </div>
          <div className="page-size-selector">
            Rows per page:
            <select value={pageSize} onChange={handlePageSizeChange}>
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      {/* Modals */}
      <AddEntryModal
        isOpen={showAddModal}
        onClose={handleModalClose}
        onSave={handleDataRefresh}
        accounts={accounts}
      />
      <EditEntryModal
        isOpen={showEditModal}
        onClose={handleModalClose}
        onSave={handleDataRefresh}
        entry={editingEntry}
        accounts={accounts}
      />
      <DeleteConfirmationModal
        isOpen={showDeleteConfirm}
        onClose={handleModalClose}
        onConfirm={handleConfirmDelete}
        itemName="this entry"
      />
    </div>
  );
};

export default SpendingAccountSummary;
