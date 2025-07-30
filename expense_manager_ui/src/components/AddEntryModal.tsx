import React, { useState, useEffect } from 'react';
import {
  AccountNameResponse,
  MonthYearResponse,
  SpendingAccountEntryRequest,
} from '../types/api';
import { addSpendingAccountEntry } from '../api/client';
import './Modal.css';

interface AddEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void; // Callback to refresh data after save
  accounts: AccountNameResponse[];
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const AddEntryModal: React.FC<AddEntryModalProps> = ({ isOpen, onClose, onSave, accounts }) => {
  const [formData, setFormData] = useState<SpendingAccountEntryRequest>({
    accountName: accounts.length > 0 ? accounts[0].accountName : '',
    month: MONTH_NAMES[new Date().getMonth()],
    year: new Date().getFullYear(),
    startingBalance: 0,
    currentBalance: 0,
    currentCredit: 0,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && accounts.length > 0) {
      setFormData(prev => ({
        ...prev,
        accountName: accounts[0].accountName,
        month: MONTH_NAMES[new Date().getMonth()],
        year: new Date().getFullYear(),
      }));
      setError(null); // Clear error when modal opens
    }
  }, [isOpen, accounts]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'year' || name.includes('Balance') || name.includes('Credit') ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Basic validation
    if (!formData.accountName || !formData.month || !formData.year) {
      setError('Please fill in all required fields.');
      setLoading(false);
      return;
    }
    if (formData.year < 2000 || formData.year > 2100) {
      setError('Year must be between 2000 and 2100.');
      setLoading(false);
      return;
    }

    try {
      await addSpendingAccountEntry(formData);
      onSave(); // Refresh data in parent component
      onClose(); // Close modal on success
    } catch (err: any) {
      console.error('Failed to add entry:', err);
      setError(err.response?.data?.detail || 'Failed to add entry. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add New Entry</h2>
        </div>
        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="accountName">Account</label>
            <select
              id="accountName"
              name="accountName"
              value={formData.accountName}
              onChange={handleChange}
              required
              disabled={accounts.length === 0}
            >
              {accounts.length === 0 && <option value="">No accounts available</option>}
              {accounts.map(account => (
                <option key={account.id} value={account.accountName}>
                  {account.accountName}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="month">Month</label>
            <select id="month" name="month" value={formData.month} onChange={handleChange} required>
              {MONTH_NAMES.map(month => (
                <option key={month} value={month}>
                  {month}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="year">Year</label>
            <input
              type="number"
              id="year"
              name="year"
              value={formData.year}
              onChange={handleChange}
              min="2000"
              max="2100"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="startingBalance">Starting Balance</label>
            <input
              type="number"
              id="startingBalance"
              name="startingBalance"
              value={formData.startingBalance}
              onChange={handleChange}
              step="0.01"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="currentBalance">Current Balance</label>
            <input
              type="number"
              id="currentBalance"
              name="currentBalance"
              value={formData.currentBalance}
              onChange={handleChange}
              step="0.01"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="currentCredit">Current Credit</label>
            <input
              type="number"
              id="currentCredit"
              name="currentCredit"
              value={formData.currentCredit}
              onChange={handleChange}
              step="0.01"
              required
            />
          </div>
          {error && <p className="modal-error-message">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="modal-button secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="modal-button primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Entry'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddEntryModal;
